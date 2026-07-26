import pytest
from datetime import datetime, time
from sender import generate_random_times, filter_image_files
from pathlib import Path


def test_generate_random_times_returns_correct_count():
    times = generate_random_times(7, 0, 8, 0, 3)
    assert len(times) == 3


def test_generate_random_times_within_window():
    times = generate_random_times(7, 0, 8, 0, 10)
    start = time(7, 0)
    end = time(8, 0)
    for t in times:
        assert start <= t <= end


def test_generate_random_times_unique():
    times = generate_random_times(7, 0, 8, 0, 100)
    assert len(times) == len(set(times))


def test_generate_random_times_sorted():
    times = generate_random_times(7, 0, 8, 0, 10)
    assert times == sorted(times)


def test_filter_image_files_excludes_non_images(tmp_path):
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "photo.png").touch()
    (tmp_path / "document.pdf").touch()
    (tmp_path / "video.mp4").touch()
    
    result = filter_image_files(str(tmp_path))
    assert len(result) == 2
    assert all(p.suffix.lower() in {".jpg", ".jpeg", ".png"} for p in result)


def test_filter_image_files_sorts_by_mtime(tmp_path):
    import time
    
    old = tmp_path / "old.jpg"
    new = tmp_path / "new.jpg"
    old.touch()
    time.sleep(0.1)
    new.touch()
    
    result = filter_image_files(str(tmp_path))
    assert result[0].name == "old.jpg"
    assert result[1].name == "new.jpg"


def test_filter_image_files_empty_dir(tmp_path):
    result = filter_image_files(str(tmp_path))
    assert result == []


def test_filter_image_files_nonexistent_dir():
    result = filter_image_files("/nonexistent/path")
    assert result == []
