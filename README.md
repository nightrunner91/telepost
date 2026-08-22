# <p align="center">Telepost</p>

<p align="center">
  <strong>Lightweight Telegram userbot for scheduling photo posts to a chat.</strong>
</p>

<p align="center">
  <strong><img src="https://flagcdn.com/w20/us.png" width="20"> English</strong> | <a href="README.ru.md"><img src="https://flagcdn.com/w20/ru.png" width="20"> Russian</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests">
</p>

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Usage](#usage)
  - [Running locally](#running-locally)
  - [Running with Docker](#running-with-docker)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Project Structure](#project-structure)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Footer](#footer)

## Project Overview

Telepost is a minimal, reliable scheduler that sends photos from a local folder to a Telegram chat on your behalf. It is designed for creators, administrators, and developers who need a hands-off way to publish visual content at predictable daily intervals.

The scheduler wakes up periodically, checks whether today's quota has already been sent, and if the current time is inside the configured window, it picks the oldest unsent images, randomizes their delivery times, and posts them one by one. Each successfully sent photo is logged and moved to a separate `sent/` folder so the same file is never posted twice.

## Features

- **Userbot-style posting** from your personal Telegram account.
- **Configurable daily window** and number of photos per day.
- **Randomized send times** within the window for natural-looking activity.
- **Deduplication** through a persistent JSON log of sent photos.
- **Automatic file management** that moves sent images to a `sent/` directory.
- **Docker-ready** deployment with persistent session storage.
- **Test coverage** with `pytest` for core scheduling and tracking logic.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core runtime |
| [Telethon](https://docs.telethon.dev/) | Telegram MTProto client |
| [PyYAML](https://pyyaml.org/) | Configuration parsing |
| [Pillow](https://python-pillow.org/) | Image handling support |
| [cryptg](https://github.com/cher-nov/cryptg) | Faster Telegram encryption |
| Docker & Docker Compose | Containerized deployment |
| pytest | Unit testing |

## Getting Started

### Prerequisites

- Python 3.11 or newer installed locally, or Docker and Docker Compose.
- A Telegram account.
- `api_id` and `api_hash` obtained from [my.telegram.org/apps](https://my.telegram.org/apps).
- The `chat_id` of the target chat or user. Forward a message from the target chat to [@userinfobot](https://t.me/userinfobot) to obtain it.

### Installation

```bash
git clone https://github.com/nightrunner91/telepost.git
cd telepost
```

For local development:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Quick Start

```bash
# Copy the example configuration and fill in your credentials
cp config.yaml.example config.yaml
# Edit config.yaml with your api_id, api_hash, phone, and chat_id

# Authenticate once
python auth.py

# Run the scheduler
python main.py
```

## Usage

### Running locally

After authentication, start the scheduler with:

```bash
python main.py
```

The scheduler checks every 5 minutes whether it is inside the configured posting window and whether today's quota has been met. If both conditions are true, it begins sending photos.

### Running with Docker

```bash
# Copy and edit the configuration
cp config.yaml.example config.yaml

# Optional: prepare an .env file for non-interactive auth code
cp .env.example .env

# Authenticate interactively (one-time)
docker compose run --rm telepost python auth.py

# Start the scheduler in detached mode
docker compose up -d
```

> [!NOTE]
> The Telegram session and sent-photo log are persisted in the `telepost_data` Docker volume, so authentication is only required once. Photos are still managed from the `photos/` folder on your host.

## Configuration

Create `config.yaml` by copying `config.yaml.example` and adjust the values:

```yaml
api_id: 12345678
api_hash: "your_api_hash_here"
phone: "+1234567890"
chat_id: 987654321              # target chat or user id (integer)
photos_dir: "./photos/incoming" # source folder
sent_dir: "./photos/sent"       # folder for already-sent photos
sent_log: "./data/sent_photos.json"
schedule:
  start_hour: 8
  start_minute: 10
  end_hour: 8
  end_minute: 20
photos_per_day: 3
```

| Field | Description | Default |
|-------|-------------|---------|
| `api_id` | Telegram app ID from my.telegram.org | required |
| `api_hash` | Telegram app hash from my.telegram.org | required |
| `phone` | Phone number linked to the Telegram account | required |
| `chat_id` | Target chat or user ID | required |
| `photos_dir` | Folder containing images to send | `"./photos/incoming"` |
| `sent_dir` | Folder where sent images are moved | `"./photos/sent"` |
| `sent_log` | JSON log of sent photos | `"./data/sent_photos.json"` |
| `schedule.start_hour` | Window start hour | `7` |
| `schedule.start_minute` | Window start minute | `0` |
| `schedule.end_hour` | Window end hour | `8` |
| `schedule.end_minute` | Window end minute | `0` |
| `photos_per_day` | Maximum photos to send per day | `3` |

> [!IMPORTANT]
> Keep `config.yaml`, `.env`, and the `data/` directory out of version control. They are already ignored in `.gitignore`.

## API Reference

Telepost is organized into small, focused modules. The key public interfaces are described below.

### `config.load_config(path: str | Path = "config.yaml") -> dict`

Loads and validates `config.yaml`. Raises `ConfigError` if required fields are missing or `chat_id` is not an integer.

### `sender.generate_random_times(start_hour, start_minute, end_hour, end_minute, count) -> list[time]`

Returns `count` unique, sorted `datetime.time` values inside the configured window.

### `sender.send_photo(client, chat_id, photo_path, sent_dir) -> bool`

Sends a single image via the Telethon client and moves it to `sent_dir` on success.

### `tracker.PhotoTracker`

Persistent helper for managing the sent-photo log.

| Method | Description |
|--------|-------------|
| `mark_sent(path)` | Records a photo as sent today. |
| `is_sent(path) -> bool` | Checks whether a photo has already been sent. |
| `get_today_count() -> int` | Returns the number of photos sent today. |
| `get_pending_photos(photos_dir, count) -> list[str]` | Returns the oldest unsent photos up to `count`. |

### `auth.authenticate(code: str | None = None)`

Starts a Telethon session and authenticates with Telegram. If `code` is not provided, it prompts interactively. The session file is stored in `data/telegram_session.session`.

### `main.main_loop()`

Entry point for the scheduler. Connects to Telegram, checks authorization, and runs the infinite scheduling loop.

## Development

### Running tests

```bash
pytest tests/ -v
```

### Project structure

```
telepost/
├── main.py              # scheduler entry point
├── auth.py              # one-time Telegram authentication
├── sender.py            # photo selection, filtering, and sending
├── tracker.py           # persistent sent-photo tracking
├── config.py            # configuration loader and validation
├── config.yaml.example  # configuration template
├── .env.example         # optional auth-code environment template
├── docker-compose.yml   # Docker Compose service definition
├── Dockerfile           # container image definition
├── requirements.txt     # Python dependencies
├── photos/              # photo folders
│   ├── incoming/        # drop images here
│   └── sent/            # sent images are moved here
├── data/                # runtime data (session, log)
└── tests/               # pytest test suite
    ├── test_sender.py
    └── test_tracker.py
```

## Disclaimer

Automating a personal Telegram account may violate Telegram's Terms of Service. Use this tool at your own risk and only for legitimate automation of channels or chats you manage. Do not use it for spam, harassment, or unsolicited messaging.

## License

This project is licensed under the [MIT License](LICENSE).

<hr>

<p align="center">
  Built with ❤ by <a href="https://t.me/nightrunner91">nightrunner91</a>
</p>
