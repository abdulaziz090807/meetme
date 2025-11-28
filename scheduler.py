"""
Scheduler for timeout handling.
"""

import asyncio
import logging
from aiogram import Bot

import database as db
from config import config
from keyboards import get_main_menu_keyboard
from texts import MATCH_EXPIRED, UNPAIR_AUTO_APPROVED

logger = logging.getLogger(__name__)


async def check_timeouts(bot: Bot) -> None:
    """Check and handle timeouts."""
    
    # Pending pair timeouts
    timed_out = db.get_timed_out_pending_pairs(config.pending_timeout)
    for user in timed_out:
        success, partner_id = db.auto_expire_pending_match(user["user_id"])
        if success:
            logger.info(f"Auto-expired match for {user['user_id']}")
            for uid in [user["user_id"], partner_id]:
                if uid:
                    try:
                        await bot.send_message(
                            uid,
                            MATCH_EXPIRED.format(hours=config.pending_timeout),
                            parse_mode="Markdown",
                            reply_markup=get_main_menu_keyboard("active_finding")
                        )
                    except:
                        pass
    
    # Rejection timeouts
    timed_out_reqs = db.get_timed_out_rejections(config.rejection_timeout)
    for req in timed_out_reqs:
        success, user_id, partner_id = db.auto_approve_rejection(req["id"])
        if success:
            logger.info(f"Auto-approved rejection {req['id']}")
            for uid in [user_id, partner_id]:
                if uid:
                    try:
                        await bot.send_message(
                            uid,
                            UNPAIR_AUTO_APPROVED.format(hours=config.rejection_timeout),
                            parse_mode="Markdown",
                            reply_markup=get_main_menu_keyboard("active_finding")
                        )
                    except:
                        pass


async def scheduler_loop(bot: Bot, interval_minutes: int = 60) -> None:
    """Run timeout checks periodically."""
    logger.info(f"Scheduler started (interval: {interval_minutes} min)")
    
    while True:
        try:
            await check_timeouts(bot)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        
        await asyncio.sleep(interval_minutes * 60)