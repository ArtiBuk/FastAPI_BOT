import asyncio
import logging
import sys
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.handlers import dp, clear_auth_users
from src.settings import settings


async def main() -> None:
    bot = Bot(token=settings.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    await dp.start_polling(bot, storage=storage, on_startup=clear_auth_users)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
