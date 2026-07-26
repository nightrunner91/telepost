import asyncio
from telethon import TelegramClient
from config import load_config


async def authenticate():
    config = load_config()
    
    client = TelegramClient(
        'telegram_session',
        config['api_id'],
        config['api_hash']
    )
    
    await client.start(phone=config['phone'])
    
    print("Авторизация успешна!")
    print(f"Аккаунт: {(await client.get_me()).first_name}")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(authenticate())
