import asyncio
import logging
import threading
from flask import Flask, jsonify

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import config
import database as db
from handlers import user_router, matching_router, admin_router
from scheduler import scheduler_loop

# --- Flask для Keep-Alive ---
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), use_reloader=False)

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- aiogram бот ---
async def main() -> None:
    logger.info("Initializing database...")
    db.init_database()
    
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(admin_router)
    dp.include_router(matching_router)
    dp.include_router(user_router)
    
    logger.info("Starting Meet Me Waltz Partner bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    scheduler_task = asyncio.create_task(scheduler_loop(bot, interval_minutes=60))
    
    try:
        await dp.start_polling(bot)
    finally:
        scheduler_task.cancel()
        await bot.session.close()
        logger.info("Bot stopped!")

# --- запуск ---
if __name__ == "__main__":
    # старт Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # старт aiogram
    asyncio.run(main())
