# Telepost

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Lightweight Telegram userbot for scheduling photo posts to a chat.

Telepost sends photos from a local folder to a Telegram chat on your behalf, at configurable daily times. It tracks already-sent photos, picks the oldest ones first, and randomizes send times within a window so the activity looks natural.

## Features

- 📤 Sends photos from your personal Telegram account (userbot)
- ⏰ Configurable daily sending window and photo count
- 🎲 Randomized send times inside the window
- 🗂️ Tracks sent photos so nothing is duplicated
- 📁 Automatically moves sent photos to a `sent/` folder
- 🐳 Ready-to-use Docker setup
- 🧪 Covered with pytest

## Disclaimer

Automating a personal Telegram account may violate Telegram's Terms of Service. Use at your own risk. Do not use this tool for spam or unsolicited messaging.

## Requirements

- Python 3.11+
- A Telegram account
- `api_id` and `api_hash` from [my.telegram.org/apps](https://my.telegram.org/apps)

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/telepost.git
cd telepost

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill the configuration
cp config.yaml.example config.yaml
# edit config.yaml with your api_id, api_hash, phone and chat_id

# 4. Authenticate (one-time)
python auth.py

# 5. Run the scheduler
python main.py
```

## Configuration

Copy `config.yaml.example` to `config.yaml` and adjust the values:

```yaml
api_id: 12345678
api_hash: "your_api_hash_here"
phone: "+1234567890"
chat_id: 987654321              # target chat/user id
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

**How to get `chat_id`:** forward a message from the target chat to [@userinfobot](https://t.me/userinfobot).

## How it works

1. The scheduler wakes up every few minutes and checks whether today's photos have been sent.
2. If the current time is inside the configured window, it picks the next `photos_per_day` oldest images from `photos_dir` that have not been sent yet.
3. It generates random send times inside the window, waits, and sends the photos.
4. Each successfully sent photo is recorded in `sent_log` and moved to `sent_dir`.
5. When there are no more photos, the scheduler logs a message and stops.

## Docker

```bash
# 1. Copy and fill configuration
cp config.yaml.example config.yaml
# edit config.yaml

# 2. Optional: create .env for an auth code
cp .env.example .env

# 3. Authenticate (interactive)
docker-compose run --rm telepost python auth.py

# 4. Run the scheduler
docker-compose up -d
```

Your Telegram session is persisted in `data/telegram_session.session`, so you only need to authenticate once.

## Testing

```bash
pytest tests/ -v
```

## Project structure

```
telepost/
├── main.py              # scheduler entry point
├── auth.py              # one-time authentication
├── sender.py            # photo selection & time generation
├── tracker.py           # sent-photo tracking
├── config.py            # configuration loader
├── config.yaml.example  # configuration template
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── photos/              # put photos in photos/incoming
│   ├── incoming/
│   └── sent/
└── data/                # created at runtime
    ├── telegram_session.session
    └── sent_photos.json
```

## License

[MIT](LICENSE)
