import asyncio

from telethon import TelegramClient

from config import load_config
from sender import filter_image_files, send_photo
from tracker import PhotoTracker

SESSION_PATH = "data/telegram_session"


async def test_send() -> None:
    config = load_config()
    tracker = PhotoTracker(config["sent_log"])

    client = TelegramClient(
        SESSION_PATH,
        config["api_id"],
        config["api_hash"],
    )

    await client.start(phone=config["phone"])

    photos = filter_image_files(config["photos_dir"])
    if not photos:
        print("No photos found in the incoming folder.")
        await client.disconnect()
        return

    photo = photos[0]
    print(f"Sending test photo: {photo}")

    try:
        success = await send_photo(client, config["chat_id"], str(photo), config["sent_dir"])
        if success:
            print("Photo sent. Check the chat.")
            tracker.mark_sent(str(photo))
            print("Photo marked as sent.")
        else:
            print("Failed to send photo.")
    except Exception as exc:
        print(f"Error: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_send())
