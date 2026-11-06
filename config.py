import yaml
from pathlib import Path


class ConfigError(Exception):
    """Raised when the configuration is missing or invalid."""


def load_config(path: str | Path = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"{path} not found. Copy config.yaml.example to config.yaml and fill it in."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    required = ["api_id", "api_hash", "phone", "chat_id", "photos_dir"]
    missing = [k for k in required if k not in config or config[k] is None]
    if missing:
        raise ConfigError(f"Missing required config fields: {', '.join(missing)}")

    if not isinstance(config["chat_id"], int):
        raise ConfigError("chat_id must be an integer")

    schedule = config.get("schedule", {})
    config["schedule"] = {
        "start_hour": schedule.get("start_hour", 7),
        "start_minute": schedule.get("start_minute", 0),
        "end_hour": schedule.get("end_hour", 8),
        "end_minute": schedule.get("end_minute", 0),
    }
    config["photos_per_day"] = config.get("photos_per_day", 3)
    config["catch_up_missed"] = bool(config.get("catch_up_missed", True))
    config["sent_log"] = config.get("sent_log", "./data/sent_photos.json")
    config["sent_dir"] = config.get("sent_dir", "./photos/sent")

    return config
