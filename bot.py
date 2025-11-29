"""
Main bot entry point.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from meet_me_bot.config.settings import config
import database as db
from handlers import user_router, matching_router, admin_router
from scheduler import scheduler_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and run the bot."""
    logger.info("Initializing database...")
    db.init_database()
    
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers (order matters)
    dp.include_router(admin_router)
    dp.include_router(matching_router)
    dp.include_router(user_router)
    
    logger.info("Starting Meet Me Waltz Partner bot...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start scheduler
    scheduler_task = asyncio.create_task(scheduler_loop(bot, interval_minutes=60))
    
    try:
        await dp.start_polling(bot)
    finally:
        scheduler_task.cancel()
        await bot.session.close()
        logger.info("Bot stopped!")


if __name__ == "__main__":

    asyncio.run(main())

