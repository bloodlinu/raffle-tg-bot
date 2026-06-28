import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import start, ticket, profile, leaderboard, rules, admin
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    init_db()
    if ADMIN_IDS == [123456789]:
        logger.warning(
            "ADMIN_IDS still has the default placeholder value — "
            "set real Telegram user IDs in .env or /admin will be unusable."
        )
    if BOT_TOKEN in ("YOUR_BOT_TOKEN_HERE", "", None):
        logger.warning("BOT_TOKEN is not set in .env — the bot cannot start without it.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(ticket.router)
    dp.include_router(profile.router)
    dp.include_router(leaderboard.router)
    dp.include_router(rules.router)

    logger.info("Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
