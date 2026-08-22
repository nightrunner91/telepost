import json
from datetime import date, datetime
from pathlib import Path

from sender import choose_photos


class PhotoTracker:
    def __init__(self, log_file: str | Path):
        self.log_file = Path(log_file)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.log_file.exists():
            return {"sent": []}
        with open(self.log_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_sent_photos(self) -> list[str]:
        return [Path(entry["path"]).as_posix() for entry in self.data["sent"]]

    def get_sent_set(self) -> set[str]:
        return set(self.get_sent_photos())

    def mark_sent(self, path: str | Path, date_str: str | None = None) -> None:
        if date_str is None:
            date_str = date.today().isoformat()
        self.data["sent"].append({
            "path": Path(path).as_posix(),
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def is_sent(self, path: str | Path) -> bool:
        return Path(path).as_posix() in self.get_sent_set()

    def get_today_count(self) -> int:
        today = date.today().isoformat()
        return sum(1 for entry in self.data["sent"] if entry["date"] == today)

    def get_pending_photos(self, photos_dir: str | Path, count: int) -> list[str]:
        return [p.as_posix() for p in choose_photos(photos_dir, self.get_sent_set(), count)]
