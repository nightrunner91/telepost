# Spec: Telegram Photo Scheduler

## Objective

Автоматизировать отправку фотографий другу в Telegram от вашего имени (userbot), чтобы это выглядело как ручная отправка. Скрипт берёт 3 фото в день из папки (по дате модификации, от старых к новым) и отправляет в случайное время в окне 8:10-8:20.

**Пользователь:** Вы сами (автоматизация личного процесса)
**Получатель:** Один друг (не должен догадываться об автоматизации)
**Успех:** Запустить один раз — работает ежедневно без ручного вмешательства

## Tech Stack

- **Язык:** Python 3.10+
- **MTProto клиент:** Telethon (или Pyrogram) — для авторизации от вашего аккаунта
- **Конфигурация:** YAML или JSON (chat_id, путь к папке, временное окно)
- **Трекинг:** SQLite или JSON-файл (список отправленных фото, чтобы не дублировать)
- **Планировщик:** asyncio + встроенный scheduler (или APScheduler)

## Commands

```bash
# Установка зависимостей
pip install -r requirements.txt

# Первая авторизация (запросит код из Telegram)
python auth.py

# Запуск бота (фоновый процесс)
python main.py

# Проверка статуса (опционально)
python status.py
```

## Project Structure

```
telegram-photo-scheduler/
├── main.py              # Точка входа, планировщик
├── auth.py              # Авторизация userbot (первый запуск)
├── config.yaml          # Конфигурация (chat_id, папка, время)
├── sender.py            # Логика отправки фото
├── tracker.py           # Трекинг отправленных фото
├── requirements.txt     # Зависимости (telethon, pyyaml, etc.)
├── photos/              # Папка с фотографиями (по умолчанию)
├── sent_photos.json     # История отправленных (или SQLite)
└── logs/                # Логи (опционально)
```

## Code Style

```python
import asyncio
import random
from datetime import datetime, timedelta
from telethon import TelegramClient

async def send_photo(client: TelegramClient, chat_id: int, photo_path: str):
    """Отправляет одно фото в указанный чат."""
    await client.send_file(chat_id, photo_path)
    print(f"[{datetime.now()}] Отправлено: {photo_path}")

async def schedule_daily_photos(config: dict):
    """Планирует отправку 3 фото в случайное время в окне 8:10-8:20."""
    client = TelegramClient('session', config['api_id'], config['api_hash'])
    await client.start()
    
    while True:
        now = datetime.now()
        if now.hour == 8 and 10 <= now.minute <= 20:
            photos = get_next_photos(config['photos_dir'], count=3)
            for photo in photos:
                delay = random.randint(0, 600)  # 0-10 минут
                await asyncio.sleep(delay)
                await send_photo(client, config['chat_id'], photo)
                mark_as_sent(photo)
        
        await asyncio.sleep(300)  # Проверять каждые 5 минут
```

**Конвенции:**
- async/await для всех I/O операций
- Имена функций: `snake_case`
- Конфиг через `config.yaml`, не хардкод
- Логи через `print` или `logging` (не `sys.stdout`)

## Testing Strategy

**Фреймворк:** pytest + mock для Telethon

**Что тестировать:**
1. **Трекинг:** фото не отправляются дважды
2. **Выбор фото:** сортировка по дате модификации работает
3. **Временное окно:** отправка происходит только в 8:10-8:20
4. **Пустая папка:** корректная обработка (лог, не краш)

**Пример теста:**
```python
def test_tracker_prevents_duplicates(tmp_path):
    tracker = PhotoTracker(tmp_path / "sent.json")
    tracker.mark_sent("photo1.jpg")
    assert tracker.is_sent("photo1.jpg")
    assert not tracker.is_sent("photo2.jpg")
```

**Покрытие:** 80%+ для core logic (tracker, scheduler)

## Boundaries

**Always:**
- Проверять что фото не отправлялось ранее перед отправкой
- Логировать каждую отправку (время, имя файла)
- Валидировать `chat_id` при старте

**Ask first:**
- Изменение временного окна (7:00-8:00)
- Добавление поддержки нескольких получателей
- Изменение формата конфигурации

**Never:**
- Коммитить `config.yaml` с реальными credentials (api_id, api_hash, session)
- Отправлять фото без проверки трекера
- Использовать Bot API (только MTProto userbot)
- Хардкодить `chat_id` или пути в коде

## Success Criteria

1. **Функциональность:** 3 фото отправляются ежедневно в 7:00-8:00 от вашего аккаунта
2. **Надёжность:** Скрипт работает непрерывно (не падает, перезапускается при ошибке)
3. **Незаметность:** Друг не видит "bot" в имени отправителя, время отправки варьируется
4. **Трекинг:** Фото не отправляются повторно после перезапуска скрипта
5. **Простота:** Один запуск `python main.py` — работает без дополнительного вмешательства

**Тестовые сценарии:**
- [ ] Запустить скрипт → 3 фото отправлены в течение часа (тестовое окно)
- [ ] Перезапустить скрипт → те же фото не отправлены повторно
- [ ] Проверить у друга → сообщение от вас (не от бота)
- [ ] Оставить на 24 часа → 3 фото отправлены на следующий день
- [ ] Docker контейнер запускается автоматически при старте системы

## Decisions

1. **Перезапуск после окна:** Если скрипт не работал во время окна отправки — пропустить день, залогировать ошибку
2. **Закончились фото:** Лог + остановка скрипта (не цикл)
3. **Формат:** Только изображения (JPEG, PNG)
4. **Ошибки отправки:** Лог + пропуск (не повтор)
5. **Временное окно:** Настраиваемое в `config.yaml` (по умолчанию 7:00-8:00), пользователь корректирует под свой график
