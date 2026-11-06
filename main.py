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

WINDOW_BEFORE = "before"
WINDOW_INSIDE = "inside"
WINDOW_AFTER = "after"


def window_state(now: datetime, schedule: dict) -> str:
    """Return where `now` is relative to today's sending window."""
    start = time(schedule["start_hour"], schedule["start_minute"])
    end = time(schedule["end_hour"], schedule["end_minute"])
    current = now.time()

    if current < start:
        return WINDOW_BEFORE
    if current > end:
        return WINDOW_AFTER
    return WINDOW_INSIDE


async def schedule_today(
    client: TelegramClient,
    config: dict,
    tracker: PhotoTracker,
    catch_up: bool = False,
    now: datetime | None = None,
) -> bool:
    photos_dir = config["photos_dir"]
    sent_dir = config["sent_dir"]
    chat_id = config["chat_id"]
    photos_per_day = config["photos_per_day"]
    schedule = config["schedule"]

    if now is None:
        now = datetime.now()

    today_count = tracker.get_today_count()
    if today_count >= photos_per_day:
        logger.info("Today's photo quota already sent")
        return True

    remaining = photos_per_day - today_count
    pending = tracker.get_pending_photos(photos_dir, remaining)
    if len(pending) < remaining:
        logger.warning(f"Not enough photos. Available: {len(pending)}, needed: {remaining}")
        if not pending:
            logger.info("All photos have been sent. Stopping.")
            return False

    if catch_up:
        logger.info(f"Catching up {len(pending)} missed photo(s) for today")
        times = None
    else:
        times = generate_random_times(
            schedule["start_hour"],
            schedule["start_minute"],
            schedule["end_hour"],
            schedule["end_minute"],
            len(pending),
        )

    for index, photo_path in enumerate(pending):
        if times is None:
            logger.info(f"Sending missed photo: {Path(photo_path).name}")
        else:
            send_time = times[index]
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
    await client.connect()
    if not await client.is_user_authorized():
        if not telegram_code:
            logger.error(
                "Telegram session is not authorized and TELEGRAM_CODE is not set. "
                "Authenticate first with: docker compose run --rm telepost python auth.py"
            )
            await client.disconnect()
            return
        await client.start(phone=config["phone"], code_callback=lambda: telegram_code)
    logger.info("Scheduler started")

    try:
        while True:
            now = datetime.now()
            today_count = tracker.get_today_count()
            state = window_state(now, config["schedule"])

            if today_count < config["photos_per_day"]:
                if state == WINDOW_INSIDE:
                    logger.info("Inside sending window")
                    result = await schedule_today(client, config, tracker, now=now)
                    if result is False:
                        break
                elif state == WINDOW_AFTER and config["catch_up_missed"]:
                    logger.info(
                        "Sending window has already ended; "
                        "catching up today's missed photos"
                    )
                    result = await schedule_today(
                        client, config, tracker, catch_up=True, now=now
                    )
                    if result is False:
                        break
                elif state == WINDOW_AFTER:
                    logger.info(
                        "Sending window has ended for today, waiting until tomorrow"
                    )
                else:
                    logger.info("Outside sending window, waiting")

            await asyncio.sleep(300)

    except KeyboardInterrupt:
        logger.info("Stopping on user request")
    finally:
        await client.disconnect()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main_loop())
