import asyncio
import os
import sys

from telethon import TelegramClient

from config import load_config

SESSION_PATH = "data/telegram_session"


async def authenticate(code: str | None = None) -> None:
    config = load_config()

    client = TelegramClient(
        SESSION_PATH,
        config["api_id"],
        config["api_hash"],
    )

    await client.start(
        phone=config["phone"],
        code_callback=lambda: code if code else input("Telegram code: "),
    )

    me = await client.get_me()
    print(f"Authenticated as {me.first_name} ({me.id})")

    await client.disconnect()


if __name__ == "__main__":
    code = os.environ.get("TELEGRAM_CODE") or (sys.argv[1] if len(sys.argv) > 1 else None)
    asyncio.run(authenticate(code))
