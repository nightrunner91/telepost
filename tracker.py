import json
from datetime import datetime, date
from pathlib import Path


class PhotoTracker:
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.log_file.exists():
            return {"sent": []}
        with open(self.log_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_sent_photos(self) -> list:
        return [entry["path"] for entry in self.data["sent"]]

    def mark_sent(self, path: str, date_str: str = None):
        if date_str is None:
            date_str = date.today().isoformat()
        self.data["sent"].append({
            "path": path,
            "date": date_str,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def is_sent(self, path: str) -> bool:
        return path in self.get_sent_photos()

    def get_today_count(self) -> int:
        today = date.today().isoformat()
        return sum(1 for entry in self.data["sent"] if entry["date"] == today)

    def get_pending_photos(self, photos_dir: str, count: int) -> list:
        dir_path = Path(photos_dir)
        if not dir_path.exists():
            return []

        sent_set = set(self.get_sent_photos())
        all_photos = []

        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                if str(file_path) not in sent_set:
                    mtime = file_path.stat().st_mtime
                    all_photos.append((str(file_path), mtime))

        all_photos.sort(key=lambda x: x[1])
        return [p[0] for p in all_photos[:count]]
