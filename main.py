import asyncio
import logging
from datetime import datetime, time, timedelta
from pathlib import Path
from telethon import TelegramClient
from config import load_config
from tracker import PhotoTracker
from sender import generate_random_times, filter_image_files

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def send_photo(client: TelegramClient, chat_id: int, photo_path: str):
    try:
        await client.send_file(chat_id, photo_path)
        logger.info(f"Отправлено: {photo_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки {photo_path}: {e}")
        return False


async def schedule_today(client: TelegramClient, config: dict, tracker: PhotoTracker):
    photos_dir = config['photos_dir']
    chat_id = config['chat_id']
    photos_per_day = config['photos_per_day']
    schedule = config['schedule']
    
    if tracker.get_today_count() >= photos_per_day:
        logger.info("Сегодня уже отправлено достаточно фото")
        return
    
    pending = tracker.get_pending_photos(photos_dir, photos_per_day)
    if len(pending) < photos_per_day:
        logger.warning(f"Недостаточно фото. Доступно: {len(pending)}, нужно: {photos_per_day}")
        if len(pending) == 0:
            logger.info("Все фото отправлены. Остановка.")
            return False
    
    times = generate_random_times(
        schedule['start_hour'],
        schedule['start_minute'],
        schedule['end_hour'],
        schedule['end_minute'],
        len(pending)
    )
    
    now = datetime.now()
    for photo_path, send_time in zip(pending, times):
        target = datetime.combine(now.date(), send_time)
        if target < now:
            logger.warning(f"Время {send_time} уже прошло, пропускаю")
            continue
        
        delay = (target - now).total_seconds()
        logger.info(f"Запланировано: {Path(photo_path).name} в {send_time}")
        await asyncio.sleep(delay)
        
        success = await send_photo(client, chat_id, photo_path)
        if success:
            tracker.mark_sent(photo_path)
    
    return True


async def main_loop():
    config = load_config()
    tracker = PhotoTracker(config['sent_log'])
    
    client = TelegramClient(
        'telegram_session',
        config['api_id'],
        config['api_hash']
    )
    
    await client.start(phone=config['phone'])
    logger.info("Бот запущен")
    
    try:
        while True:
            now = datetime.now()
            schedule = config['schedule']
            start_time = time(schedule['start_hour'], schedule['start_minute'])
            end_time = time(schedule['end_hour'], schedule['end_minute'])
            
            current_time = now.time()
            
            if start_time <= current_time <= end_time:
                if tracker.get_today_count() == 0:
                    logger.info("Начало окна отправки")
                    result = await schedule_today(client, config, tracker)
                    if result is False:
                        break
            
            await asyncio.sleep(300)
    
    except KeyboardInterrupt:
        logger.info("Остановка по запросу пользователя")
    finally:
        await client.disconnect()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main_loop())
