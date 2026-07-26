import yaml
import sys
from pathlib import Path


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        print(f"Ошибка: {path} не найден. Скопируйте config.yaml.example в config.yaml и заполните.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required = ["api_id", "api_hash", "chat_id", "photos_dir"]
    missing = [k for k in required if k not in config or config[k] is None]
    if missing:
        print(f"Ошибка: отсутствуют обязательные поля: {', '.join(missing)}")
        sys.exit(1)

    schedule = config.get("schedule", {})
    config["schedule"] = {
        "start_hour": schedule.get("start_hour", 7),
        "start_minute": schedule.get("start_minute", 0),
        "end_hour": schedule.get("end_hour", 8),
        "end_minute": schedule.get("end_minute", 0),
    }
    config["photos_per_day"] = config.get("photos_per_day", 3)
    config["sent_log"] = config.get("sent_log", "./sent_photos.json")

    return config
