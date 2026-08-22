import logging
import random
import shutil
from datetime import time
from pathlib import Path

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def generate_random_times(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    count: int,
) -> list[time]:
    """Generate `count` unique sorted random times inside the given window."""
    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute

    if end_minutes < start_minutes:
        raise ValueError("end time must be after start time")

    available = list(range(start_minutes, end_minutes + 1))
    count = min(count, len(available))

    selected = sorted(random.sample(available, count))
    return [time(m // 60, m % 60) for m in selected]


def filter_image_files(photos_dir: str | Path) -> list[Path]:
    """Return all image files in the directory sorted by modification time (oldest first)."""
    dir_path = Path(photos_dir)
    if not dir_path.exists():
        return []

    images = []
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append((file_path, file_path.stat().st_mtime))

    images.sort(key=lambda item: item[1])
    return [img[0] for img in images]


def choose_photos(photos_dir: str | Path, sent_paths: set[str], count: int) -> list[Path]:
    """Pick up to `count` oldest photos from `photos_dir` that are not in `sent_paths`."""
    candidates = [
        path
        for path in filter_image_files(photos_dir)
        if path.as_posix() not in sent_paths
    ]
    return candidates[:count]


async def send_photo(client, chat_id: int, photo_path: str | Path, sent_dir: str | Path) -> bool:
    """Send a single photo and move it to the sent folder on success."""
    photo_file = Path(photo_path)
    sent_path = Path(sent_dir) / photo_file.name

    try:
        await client.send_file(chat_id, str(photo_file))
        logger.info(f"Sent: {photo_file}")

        shutil.move(str(photo_file), str(sent_path))
        logger.info(f"Moved to: {sent_path}")

        return True
    except Exception as exc:
        logger.error(f"Failed to send {photo_file}: {exc}")
        return False
