# Telegram Photo Scheduler - Docker

## Сборка

```bash
docker-compose build
```

## Первый запуск (авторизация)

```bash
docker-compose run --rm telegram-bot python auth.py
```

Введите код из Telegram. Session сохранится в `telegram_session.session`.

## Запуск бота

```bash
docker-compose up -d
```

## Логи

```bash
docker-compose logs -f
```

## Остановка

```bash
docker-compose down
```

## Автозапуск

Docker Desktop для Windows автоматически запускает контейнеры при старте системы, если включена опция "Start Docker Desktop when you log in".

Контейнер имеет `restart: unless-stopped`, поэтому будет перезапускаться после перезагрузки компьютера.
