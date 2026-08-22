import asyncio
import logging
import os
from datetime import datetime, time
from pathlib import Path

from telethon import TelegramClient

from config import load_config
from sender import generate_random_times, send_photo
from tracker import PhotoTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def schedule_today(client: TelegramClient, config: dict, tracker: PhotoTracker) -> bool:
    photos_dir = config["photos_dir"]
    sent_dir = config["sent_dir"]
    chat_id = config["chat_id"]
    photos_per_day = config["photos_per_day"]
    schedule = config["schedule"]

    if tracker.get_today_count() >= photos_per_day:
        logger.info("Today's photo quota already sent")
        return True

    pending = tracker.get_pending_photos(photos_dir, photos_per_day)
    if len(pending) < photos_per_day:
        logger.warning(f"Not enough photos. Available: {len(pending)}, needed: {photos_per_day}")
        if not pending:
            logger.info("All photos have been sent. Stopping.")
            return False

    times = generate_random_times(
        schedule["start_hour"],
        schedule["start_minute"],
        schedule["end_hour"],
        schedule["end_minute"],
        len(pending),
    )

    now = datetime.now()
    for photo_path, send_time in zip(pending, times):
        target = datetime.combine(now.date(), send_time)
        if target < now:
            logger.warning(f"Scheduled time {send_time} has passed, sending immediately")
            target = now

        delay = (target - now).total_seconds()
        if delay > 0:
            logger.info(f"Scheduled: {Path(photo_path).name} at {send_time}")
            await asyncio.sleep(delay)

        success = await send_photo(client, chat_id, photo_path, sent_dir)
        if success:
            tracker.mark_sent(photo_path)
        now = datetime.now()

    return True


async def main_loop() -> None:
    config = load_config()
    tracker = PhotoTracker(config["sent_log"])

    client = TelegramClient(
        "data/telegram_session",
        config["api_id"],
        config["api_hash"],
    )

    telegram_code = os.environ.get("TELEGRAM_CODE")
    if telegram_code:
        await client.start(phone=config["phone"], code_callback=lambda: telegram_code)
    else:
        await client.start(phone=config["phone"])
    logger.info("Scheduler started")

    try:
        while True:
            now = datetime.now()
            schedule = config["schedule"]
            start_time = time(schedule["start_hour"], schedule["start_minute"])
            end_time = time(schedule["end_hour"], schedule["end_minute"])

            current_time = now.time()
            today_count = tracker.get_today_count()
            in_window = start_time <= current_time <= end_time

            if today_count < config["photos_per_day"]:
                if in_window or today_count == 0:
                    if in_window:
                        logger.info("Inside sending window")
                    else:
                        logger.warning("Outside sending window but no photos sent today — sending now")
                    result = await schedule_today(client, config, tracker)
                    if result is False:
                        break

            await asyncio.sleep(300)

    except KeyboardInterrupt:
        logger.info("Stopping on user request")
    finally:
        await client.disconnect()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main_loop())
