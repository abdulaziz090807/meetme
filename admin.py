"""
Admin handlers - panel, broadcast, DM, bot control.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import database as db
from config import config
from states import AdminStates
from keyboards import (
    get_admin_menu_keyboard, get_admin_approval_keyboard,
    get_admin_rejection_keyboard, get_admin_bot_control_keyboard,
    get_broadcast_confirm_keyboard, get_cancel_keyboard, get_main_menu_keyboard
)
from texts import (
    ADMIN_PANEL, ADMIN_STATS, ADMIN_PROFILE_REVIEW, ADMIN_APPROVED, ADMIN_REJECTED,
    ADMIN_BANNED_NOTIF, ADMIN_UNPAIR_REQUEST, ADMIN_BROADCAST_ASK, ADMIN_BROADCAST_CONFIRM,
    ADMIN_BROADCAST_SENT, ADMIN_DM_ASK, ADMIN_DM_MESSAGE, ADMIN_DM_SENT,
    ADMIN_BOT_STOPPING, ADMIN_BOT_RESTARTING, ADMIN_FROM_ADMIN, ADMIN_ALL_REVIEWED,
    UNPAIR_APPROVED, UNPAIR_DENIED, get_gender_emoji, get_gender_text, BTN_CANCEL
)

admin_router = Router()

# Global flag for bot control
bot_running = True


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown."""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


async def send_next_pending_profile(chat_id: int, bot: Bot) -> bool:
    """
    Send next pending profile to admin.
    Returns True if a profile was sent, False if no more profiles.
    """
    users = db.get_pending_users()
    
    if not users:
        return False
    
    u = dict(users[0])
    
    # Escape special characters in user data
    first_name = escape_markdown(u["first_name"])
    last_name = escape_markdown(u["last_name"])
    username = escape_markdown(u["username"])
    course = escape_markdown(u.get("course", ""))
    interests = escape_markdown(u.get("interests", ""))
    about_me = escape_markdown(u.get("about_me", ""))
    
    text = ADMIN_PROFILE_REVIEW.format(
        user_id=u["user_id"],
        first_name=first_name,
        last_name=last_name,
        username=username,
        age=u["age"],
        gender_emoji=get_gender_emoji(u["gender"]),
        gender=get_gender_text(u["gender"]),
        course_line=f"🎓 {course}\n" if course else "",
        interests_line=f"💝 {interests}\n" if interests else "",
        about_line=f"💭 {about_me}" if about_me else ""
    )
    kb = get_admin_approval_keyboard(u["user_id"])
    
    try:
        if u.get("media_file_id") and u.get("media_type"):
            if u["media_type"] == "photo":
                await bot.send_photo(chat_id, u["media_file_id"],
                                   caption=text, parse_mode="Markdown", reply_markup=kb)
            elif u["media_type"] == "video":
                await bot.send_video(chat_id, u["media_file_id"],
                                   caption=text, parse_mode="Markdown", reply_markup=kb)
            elif u["media_type"] == "video_note":
                await bot.send_video_note(chat_id, u["media_file_id"])
                await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)
        else:
            await bot.send_message(chat_id, text + "\n\n📷 [No media]",
                                 parse_mode="Markdown", reply_markup=kb)
        return True
    except Exception as e:
        # Fallback to text-only if media fails
        try:
            await bot.send_message(chat_id, text + "\n\n📷 [Media failed to load]",
                                 parse_mode="Markdown", reply_markup=kb)
            return True
        except:
            return False


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not config.is_admin(message.from_user.id):
        return
    
    stats = db.get_statistics()
    await message.answer(
        ADMIN_PANEL.format(**stats),
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard()
    )


@admin_router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not config.is_admin(message.from_user.id):
        return
    
    stats = db.get_statistics()
    await message.answer(ADMIN_STATS.format(**stats), parse_mode="Markdown")


@admin_router.message(Command("force_unpair"))
async def cmd_force_unpair(message: Message, bot: Bot) -> None:
    if not config.is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /force_unpair <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid ID")
        return
    
    success, partner_id = db.force_unpair(user_id)
    
    if success:
        await message.answer(f"✅ Unpaired {user_id} from {partner_id}")
        for uid in [user_id, partner_id]:
            try:
                await bot.send_message(uid, "🔔 Admin has unpaired you. You can search again!",
                                      reply_markup=get_main_menu_keyboard("active_finding"))
            except:
                pass
    else:
        await message.answer("❌ User not paired")


@admin_router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot) -> None:
    if not config.is_admin(message.from_user.id):
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("Usage: /ban <user_id> [reason]")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid ID")
        return
    
    reason = args[2] if len(args) > 2 else "Banned by admin"
    success = db.ban_user(user_id, reason)
    
    if success:
        await message.answer(f"🚫 Banned user {user_id}")
        try:
            await bot.send_message(user_id, ADMIN_BANNED_NOTIF.format(reason=reason), parse_mode="Markdown")
        except:
            pass
    else:
        await message.answer("❌ Could not ban")


@admin_router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    if not config.is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid ID")
        return
    
    if db.unban_user(user_id):
        await message.answer(f"✅ Unbanned {user_id}")
    else:
        await message.answer("❌ Could not unban")


# ==================== CALLBACKS ====================

@admin_router.callback_query(F.data == "admin_pending")
async def cb_pending(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    users = db.get_pending_users()
    
    if not users:
        await callback.message.answer("📋 No pending profiles!")
        return
    
    # Show count and first profile only
    await callback.message.answer(f"📋 *Pending Profiles ({len(users)})*\n\nReviewing first profile...", parse_mode="Markdown")
    
    # Send first profile using helper function
    await send_next_pending_profile(callback.message.chat.id, bot)


@admin_router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    stats = db.get_statistics()
    await callback.message.answer(ADMIN_STATS.format(**stats), parse_mode="Markdown")


@admin_router.callback_query(F.data == "admin_pairs")
async def cb_pairs(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    pairs = db.get_all_pairs()
    
    if not pairs:
        await callback.message.answer("💕 No pairs yet!")
        return
    
    await callback.message.answer(f"💕 *All Pairs ({len(pairs)})*", parse_mode="Markdown")
    for p in pairs:
        await callback.message.answer(
            f"💃 {p['first_name']} (@{p['username']})\n🕺 {p['partner_first_name']} (@{p['partner_username']})"
        )


async def send_next_unpair_request(chat_id: int, bot: Bot) -> bool:
    """
    Send next unpair request to admin.
    Returns True if a request was sent, False if no more requests.
    """
    requests = db.get_pending_rejections()
    
    if not requests:
        return False
    
    r = dict(requests[0])
    
    # Escape special characters in user data
    requester_name = escape_markdown(r["requester_name"])
    requester_username = escape_markdown(r["requester_username"])
    partner_name = escape_markdown(r["partner_name"])
    partner_username = escape_markdown(r["partner_username"])
    reason = escape_markdown(r["reason"])
    
    text = ADMIN_UNPAIR_REQUEST.format(
        id=r["id"],
        requester_name=requester_name,
        requester_username=requester_username,
        partner_name=partner_name,
        partner_username=partner_username,
        reason=reason
    )
    
    try:
        await bot.send_message(
            chat_id,
            text,
            parse_mode="Markdown",
            reply_markup=get_admin_rejection_keyboard(r["id"])
        )
        return True
    except:
        return False


@admin_router.callback_query(F.data == "admin_rejections")
async def cb_rejections(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    requests = db.get_pending_rejections()
    
    if not requests:
        await callback.message.answer("📨 No pending requests!")
        return
    
    # Show count and first request only
    await callback.message.answer(f"📨 *Unpair Requests ({len(requests)})*\n\nReviewing first request...", parse_mode="Markdown")
    
    # Send first request using helper function
    await send_next_unpair_request(callback.message.chat.id, bot)


@admin_router.callback_query(F.data.startswith("approve_"))
async def cb_approve(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    
    if db.update_approval_status(user_id, "approved"):
        # Remove inline keyboard and add status
        try:
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n✅ [APPROVED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
            else:
                await callback.message.edit_text(
                    text=callback.message.text + "\n\n✅ [APPROVED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
        except:
            pass
        
        # Get remaining count
        remaining = len(db.get_pending_users())
        
        # Notify approved user
        try:
            await bot.send_message(user_id, ADMIN_APPROVED, parse_mode="Markdown",
                                 reply_markup=get_main_menu_keyboard("active_finding"))
        except:
            pass
        
        # Show next profile or completion message
        if remaining > 0:
            await callback.answer(f"✅ Approved! ({remaining} remaining)")
            await send_next_pending_profile(callback.message.chat.id, bot)
        else:
            await callback.answer("✅ Approved!")
            await callback.message.answer(ADMIN_ALL_REVIEWED, parse_mode="Markdown")
    else:
        await callback.answer("❌ Error")


@admin_router.callback_query(F.data.startswith("reject_"))
async def cb_reject(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    
    if db.update_approval_status(user_id, "rejected"):
        # Remove inline keyboard and add status
        try:
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n❌ [REJECTED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
            else:
                await callback.message.edit_text(
                    text=callback.message.text + "\n\n❌ [REJECTED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
        except:
            pass
        
        # Get remaining count
        remaining = len(db.get_pending_users())
        
        # Notify rejected user
        try:
            await bot.send_message(user_id, ADMIN_REJECTED, parse_mode="Markdown")
        except:
            pass
        
        # Show next profile or completion message
        if remaining > 0:
            await callback.answer(f"❌ Rejected! ({remaining} remaining)")
            await send_next_pending_profile(callback.message.chat.id, bot)
        else:
            await callback.answer("❌ Rejected!")
            await callback.message.answer(ADMIN_ALL_REVIEWED, parse_mode="Markdown")
    else:
        await callback.answer("❌ Error")


@admin_router.callback_query(F.data.startswith("ban_"))
async def cb_ban(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    
    if db.ban_user(user_id, "Banned during review"):
        # Remove inline keyboard and add status
        try:
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n🚫 [BANNED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
            else:
                await callback.message.edit_text(
                    text=callback.message.text + "\n\n🚫 [BANNED]",
                    parse_mode="Markdown",
                    reply_markup=None
                )
        except:
            pass
        
        # Get remaining count
        remaining = len(db.get_pending_users())
        
        # Notify banned user
        try:
            await bot.send_message(user_id, ADMIN_BANNED_NOTIF.format(reason="Banned during review"), parse_mode="Markdown")
        except:
            pass
        
        # Show next profile or completion message
        if remaining > 0:
            await callback.answer(f"🚫 Banned! ({remaining} remaining)")
            await send_next_pending_profile(callback.message.chat.id, bot)
        else:
            await callback.answer("🚫 Banned!")
            await callback.message.answer(ADMIN_ALL_REVIEWED, parse_mode="Markdown")
    else:
        await callback.answer("❌ Error")


@admin_router.callback_query(F.data.startswith("approve_unpair_"))
async def cb_approve_unpair(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    request_id = int(callback.data.split("_")[2])
    success, user_id, partner_id = db.approve_rejection(request_id)
    
    if success:
        # Remove inline keyboard and add status
        try:
            await callback.message.edit_text(
                text=callback.message.text + "\n\n✅ [APPROVED]",
                parse_mode="Markdown",
                reply_markup=None
            )
        except:
            pass
        
        # Get remaining count
        remaining = len(db.get_pending_rejections())
        
        # Notify users
        for uid in [user_id, partner_id]:
            try:
                await bot.send_message(uid, UNPAIR_APPROVED, parse_mode="Markdown",
                                      reply_markup=get_main_menu_keyboard("active_finding"))
            except:
                pass
        
        # Show next request or completion message
        if remaining > 0:
            await callback.answer(f"✅ Approved! ({remaining} remaining)")
            await send_next_unpair_request(callback.message.chat.id, bot)
        else:
            await callback.answer("✅ Approved!")
            await callback.message.answer("✅ *All unpair requests reviewed!*", parse_mode="Markdown")
    else:
        await callback.answer("❌ Error")


@admin_router.callback_query(F.data.startswith("deny_unpair_"))
async def cb_deny_unpair(callback: CallbackQuery, bot: Bot) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    request_id = int(callback.data.split("_")[2])
    success, user_id = db.deny_rejection(request_id)
    
    if success:
        # Remove inline keyboard and add status
        try:
            await callback.message.edit_text(
                text=callback.message.text + "\n\n❌ [DENIED]",
                parse_mode="Markdown",
                reply_markup=None
            )
        except:
            pass
        
        # Get remaining count
        remaining = len(db.get_pending_rejections())
        
        # Notify user
        try:
            await bot.send_message(user_id, UNPAIR_DENIED, parse_mode="Markdown",
                                  reply_markup=get_main_menu_keyboard("have_pair"))
        except:
            pass
        
        # Show next request or completion message
        if remaining > 0:
            await callback.answer(f"❌ Denied! ({remaining} remaining)")
            await send_next_unpair_request(callback.message.chat.id, bot)
        else:
            await callback.answer("❌ Denied!")
            await callback.message.answer("✅ *All unpair requests reviewed!*", parse_mode="Markdown")
    else:
        await callback.answer("❌ Error")


# ==================== BROADCAST ====================

@admin_router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.answer(ADMIN_BROADCAST_ASK, parse_mode="Markdown", reply_markup=get_cancel_keyboard())


@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext) -> None:
    if message.text == BTN_CANCEL:
        await state.clear()
        await message.answer("❌ Cancelled", reply_markup=get_admin_menu_keyboard())
        return
    
    users = db.get_all_users()
    await state.update_data(broadcast_message=message.text, user_count=len(users))
    await state.set_state(AdminStates.confirm_broadcast)
    
    # Escape markdown for preview
    escaped_preview = escape_markdown(message.text)
    
    await message.answer(
        ADMIN_BROADCAST_CONFIRM.format(message=escaped_preview, count=len(users)),
        parse_mode="Markdown",
        reply_markup=get_broadcast_confirm_keyboard()
    )


@admin_router.callback_query(F.data == "broadcast_confirm", AdminStates.confirm_broadcast)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    
    data = await state.get_data()
    msg = data["broadcast_message"]
    users = db.get_all_users()
    
    # Escape markdown in the broadcast message
    escaped_msg = escape_markdown(msg)
    
    success = 0
    for u in users:
        try:
            await bot.send_message(u["user_id"], f"📢 *Announcement*\n\n{escaped_msg}", parse_mode="Markdown")
            success += 1
        except:
            pass
    
    await state.clear()
    await callback.message.answer(
        ADMIN_BROADCAST_SENT.format(success=success, total=len(users)),
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard()
    )


@admin_router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer("❌ Cancelled", reply_markup=get_admin_menu_keyboard())


# ==================== DIRECT MESSAGE ====================

@admin_router.callback_query(F.data == "admin_dm")
async def cb_dm(callback: CallbackQuery, state: FSMContext) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_dm_user_id)
    await callback.message.answer(ADMIN_DM_ASK, parse_mode="Markdown", reply_markup=get_cancel_keyboard())


@admin_router.message(AdminStates.waiting_for_dm_user_id)
async def process_dm_user_id(message: Message, state: FSMContext) -> None:
    if message.text == BTN_CANCEL:
        await state.clear()
        await message.answer("❌ Cancelled", reply_markup=get_admin_menu_keyboard())
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("💫 Enter a valid user ID:")
        return
    
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ User not found!")
        return
    
    await state.update_data(dm_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_dm_message)
    await message.answer(ADMIN_DM_MESSAGE.format(user_id=user_id), parse_mode="Markdown", reply_markup=get_cancel_keyboard())


@admin_router.message(AdminStates.waiting_for_dm_message)
async def process_dm_message(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == BTN_CANCEL:
        await state.clear()
        await message.answer("❌ Cancelled", reply_markup=get_admin_menu_keyboard())
        return
    
    data = await state.get_data()
    user_id = data["dm_user_id"]
    
    try:
        await bot.send_message(user_id, ADMIN_FROM_ADMIN.format(message=message.text), parse_mode="Markdown")
        await message.answer(ADMIN_DM_SENT.format(user_id=user_id), parse_mode="Markdown",
                           reply_markup=get_admin_menu_keyboard())
    except Exception as e:
        await message.answer(f"❌ Could not send: {e}")
    
    await state.clear()


# ==================== BOT CONTROL ====================

@admin_router.callback_query(F.data == "admin_bot_control")
async def cb_bot_control(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.answer("🎛️ *Bot Control*", parse_mode="Markdown",
                                 reply_markup=get_admin_bot_control_keyboard())


@admin_router.callback_query(F.data == "admin_back")
async def cb_back(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        return
    
    await callback.answer()
    stats = db.get_statistics()
    await callback.message.edit_text(
        ADMIN_PANEL.format(**stats),
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard()
    )


@admin_router.callback_query(F.data == "admin_restart_bot")
async def cb_restart_bot(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer("🔄 Restarting...", show_alert=True)
    await callback.message.answer(ADMIN_BOT_RESTARTING, parse_mode="Markdown")
    # In production, use process manager like systemd/supervisor to restart


@admin_router.callback_query(F.data == "admin_stop_bot")
async def cb_stop_bot(callback: CallbackQuery) -> None:
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    await callback.answer("🛑 Stopping...", show_alert=True)
    await callback.message.answer(ADMIN_BOT_STOPPING, parse_mode="Markdown")
    # In production, signal the bot to shut down gracefully