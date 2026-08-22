import json
import pytest
from datetime import datetime, date
from pathlib import Path
from tracker import PhotoTracker


@pytest.fixture
def tracker(tmp_path):
    log_file = tmp_path / "sent.json"
    return PhotoTracker(str(log_file))


def test_new_tracker_has_no_sent_photos(tracker):
    assert tracker.get_sent_photos() == []


def test_mark_sent_adds_photo(tracker):
    tracker.mark_sent("photo1.jpg")
    assert "photo1.jpg" in tracker.get_sent_photos()


def test_is_sent_returns_true_for_sent_photo(tracker):
    tracker.mark_sent("photo1.jpg")
    assert tracker.is_sent("photo1.jpg") is True


def test_is_sent_returns_false_for_unsent_photo(tracker):
    assert tracker.is_sent("photo1.jpg") is False


def test_get_today_count_returns_zero_initially(tracker):
    assert tracker.get_today_count() == 0


def test_get_today_count_increments_after_mark(tracker):
    tracker.mark_sent("photo1.jpg")
    tracker.mark_sent("photo2.jpg")
    assert tracker.get_today_count() == 2


def test_get_today_count_ignores_old_entries(tracker):
    tracker.mark_sent("photo1.jpg", date_str="2024-01-01")
    assert tracker.get_today_count() == 0


def test_tracker_persists_to_file(tracker, tmp_path):
    tracker.mark_sent("photo1.jpg")
    
    # Создаём новый трекер с тем же файлом
    new_tracker = PhotoTracker(str(tmp_path / "sent.json"))
    assert "photo1.jpg" in new_tracker.get_sent_photos()


def test_get_pending_photos_excludes_sent(tracker, tmp_path):
    # Создаём тестовые фото
    photo1 = tmp_path / "photo1.jpg"
    photo2 = tmp_path / "photo2.jpg"
    photo1.touch()
    photo2.touch()
    
    tracker.mark_sent(str(photo1))
    
    pending = tracker.get_pending_photos(str(tmp_path), count=5)
    assert photo1.as_posix() not in pending
    assert photo2.as_posix() in pending
