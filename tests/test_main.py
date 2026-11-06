import asyncio
from datetime import date, datetime, time
from pathlib import Path

import pytest

from main import (
    WINDOW_AFTER,
    WINDOW_BEFORE,
    WINDOW_INSIDE,
    schedule_today,
    window_state,
)
from tracker import PhotoTracker

SCHEDULE = {"start_hour": 8, "start_minute": 5, "end_hour": 8, "end_minute": 10}


class FakeClient:
    def __init__(self):
        self.sent = []

    async def send_file(self, chat_id, path):
        self.sent.append(Path(path).name)


def make_config(tmp_path, photos_per_day=2):
    incoming = tmp_path / "incoming"
    sent = tmp_path / "sent"
    incoming.mkdir()
    sent.mkdir()
    return {
        "photos_dir": str(incoming),
        "sent_dir": str(sent),
        "sent_log": str(tmp_path / "sent.json"),
        "chat_id": 1,
        "photos_per_day": photos_per_day,
        "schedule": SCHEDULE,
    }


def make_photos(directory, count):
    for index in range(count):
        (directory / f"photo{index}.jpg").touch()


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        (time(7, 59), WINDOW_BEFORE),
        (time(8, 5), WINDOW_INSIDE),
        (time(8, 7), WINDOW_INSIDE),
        (time(8, 10), WINDOW_INSIDE),
        (time(8, 11), WINDOW_AFTER),
        (time(11, 27), WINDOW_AFTER),
        (time(23, 59), WINDOW_AFTER),
    ],
)
def test_window_state(current, expected):
    now = datetime.combine(date(2026, 1, 1), current)
    assert window_state(now, SCHEDULE) == expected


def test_catch_up_sends_all_photos_when_none_sent(tmp_path):
    config = make_config(tmp_path, photos_per_day=2)
    make_photos(Path(config["photos_dir"]), 3)
    tracker = PhotoTracker(config["sent_log"])
    client = FakeClient()

    result = asyncio.run(
        schedule_today(
            client,
            config,
            tracker,
            catch_up=True,
            now=datetime(2026, 1, 1, 11, 27),
        )
    )

    assert result is True
    assert len(client.sent) == 2
    assert tracker.get_today_count() == 2


def test_catch_up_sends_only_remaining_quota(tmp_path):
    config = make_config(tmp_path, photos_per_day=2)
    make_photos(Path(config["photos_dir"]), 3)
    tracker = PhotoTracker(config["sent_log"])
    tracker.mark_sent("already_sent.jpg")
    client = FakeClient()

    result = asyncio.run(
        schedule_today(
            client,
            config,
            tracker,
            catch_up=True,
            now=datetime(2026, 1, 1, 11, 27),
        )
    )

    assert result is True
    assert len(client.sent) == 1
    assert tracker.get_today_count() == 2


def test_catch_up_does_nothing_when_quota_already_met(tmp_path):
    config = make_config(tmp_path, photos_per_day=1)
    make_photos(Path(config["photos_dir"]), 3)
    tracker = PhotoTracker(config["sent_log"])
    tracker.mark_sent("already_sent.jpg")
    client = FakeClient()

    result = asyncio.run(
        schedule_today(
            client,
            config,
            tracker,
            catch_up=True,
            now=datetime(2026, 1, 1, 11, 27),
        )
    )

    assert result is True
    assert client.sent == []
    assert tracker.get_today_count() == 1
