import random
from datetime import datetime, time, timedelta
from pathlib import Path


def generate_random_times(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
    count: int
) -> list:
    start = time(start_hour, start_minute)
    end = time(end_hour, end_minute)
    
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute
    
    available = list(range(start_minutes, end_minutes + 1))
    if len(available) < count:
        count = len(available)
    
    selected = sorted(random.sample(available, count))
    return [time(m // 60, m % 60) for m in selected]


def filter_image_files(photos_dir: str) -> list:
    dir_path = Path(photos_dir)
    if not dir_path.exists():
        return []
    
    images = []
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            mtime = file_path.stat().st_mtime
            images.append((file_path, mtime))
    
    images.sort(key=lambda x: x[1])
    return [img[0] for img in images]
