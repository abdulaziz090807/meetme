"""
Matching handlers - partner search, pairing, unpair.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import database as db
from states import RejectionStates
from keyboards import (
    get_main_menu_keyboard, get_matching_keyboard,
    get_pair_confirmation_keyboard, get_unpair_confirm_keyboard
)
from texts import (
    FINDING_PARTNER, PARTNER_CARD, NO_PARTNERS, NO_MORE_PARTNERS, ALL_SEEN,
    MATCH_FOUND, MATCH_VIEW, MATCH_CONFIRMED_WAIT, MATCH_BOTH_CONFIRMED,
    MATCH_REJECTED, MATCH_REJECTED_PARTNER, PARTNER_VIEW,
    UNPAIR_CONFIRM, UNPAIR_REASON, UNPAIR_SUBMITTED, UNPAIR_CANCELLED,
    UNPAIR_STATUS_PENDING, BTN_FIND_PARTNER, BTN_VIEW_MATCH, BTN_MY_PARTNER,
    BTN_REQUEST_UNPAIR, BTN_YES_UNPAIR, BTN_NO_CANCEL, BTN_CHECK_STATUS, BTN_CANCEL_REQUEST,
    get_gender_emoji, get_gender_text, build_optional_line
)

matching_router = Router()


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown."""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


async def send_partner_card(bot: Bot, chat_id: int, user: dict, keyboard=None, show_username: bool = False) -> None:
    """Send partner profile card."""
    # Escape special characters in user data
    first_name = escape_markdown(user["first_name"])
    username = escape_markdown(user.get("username", ""))
    course = escape_markdown(user.get("course", ""))
    interests = escape_markdown(user.get("interests", ""))
    about_me = escape_markdown(user.get("about_me", ""))
    
    text = PARTNER_CARD.format(
        first_name=first_name,
        age=user["age"],
        gender_emoji=get_gender_emoji(user["gender"]),
        gender=get_gender_text(user["gender"]),
        username_line=f"📱 @{username}\n" if show_username and username else "",
        course_line=f"🎓 {course}\n" if course else "",
        interests_line=f"💝 {interests}\n" if interests else "",
        about_line=f"💭 {about_me}" if about_me else ""
    )
    
    if user.get("media_file_id") and user.get("media_type"):
        if user["media_type"] == "photo":
            await bot.send_photo(chat_id, user["media_file_id"], caption=text,
                               parse_mode="Markdown", reply_markup=keyboard)
        elif user["media_type"] == "video":
            await bot.send_video(chat_id, user["media_file_id"], caption=text,
                               parse_mode="Markdown", reply_markup=keyboard)
        elif user["media_type"] == "video_note":
            await bot.send_video_note(chat_id, user["media_file_id"])
            await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, text + "\n\n📷 [No photo]", parse_mode="Markdown", reply_markup=keyboard)


async def show_next_partner(bot: Bot, chat_id: int, user_id: int) -> None:
    """Show next partner or expand search."""
    user = db.get_user(user_id)
    expanded = user["search_expanded"] if user else False
    
    partners = db.get_potential_partners(user_id, expanded)
    
    if partners:
        partner = dict(partners[0])
        await bot.send_message(chat_id, FINDING_PARTNER, parse_mode="Markdown")
        await send_partner_card(bot, chat_id, partner, get_matching_keyboard(partner["user_id"]))
    elif not expanded:
        # Expand search
        db.set_search_expanded(user_id, True)
        partners = db.get_potential_partners(user_id, True)
        
        if partners:
            await bot.send_message(chat_id, NO_MORE_PARTNERS, parse_mode="Markdown")
            partner = dict(partners[0])
            await send_partner_card(bot, chat_id, partner, get_matching_keyboard(partner["user_id"]))
        else:
            await bot.send_message(chat_id, ALL_SEEN, parse_mode="Markdown",
                                 reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))
    else:
        await bot.send_message(chat_id, ALL_SEEN, parse_mode="Markdown",
                             reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))


@matching_router.message(F.text == BTN_FIND_PARTNER)
async def find_partner(message: Message, bot: Bot) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["approval_status"] != "approved":
        await message.answer("⏳ Your profile must be approved first!")
        return
    
    if user["pairing_status"] != "active_finding":
        await message.answer("🎭 You're not in search mode!",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"]))
        return
    
    await show_next_partner(bot, message.chat.id, message.from_user.id)


@matching_router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    
    target_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    success, is_match = db.add_like(user_id, target_id)
    
    if not success:
        await callback.message.answer("😅 Error, try again!")
        return
    
    try:
        if callback.message.caption:
            await callback.message.edit_caption(callback.message.caption + "\n\n💖 [Liked]", parse_mode="Markdown")
        else:
            await callback.message.edit_text(callback.message.text + "\n\n💖 [Liked]", parse_mode="Markdown")
    except:
        pass
    
    if is_match:
        user = db.get_user(user_id)
        partner = db.get_user(target_id)
        
        # Escape names for Markdown
        partner_name = escape_markdown(partner["first_name"])
        user_name = escape_markdown(user["first_name"])
        
        await callback.message.answer(
            MATCH_FOUND.format(name=partner_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard("pending_pair")
        )
        
        try:
            await bot.send_message(
                target_id,
                MATCH_FOUND.format(name=user_name),
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard("pending_pair")
            )
        except:
            pass
    else:
        await show_next_partner(bot, callback.message.chat.id, user_id)


@matching_router.callback_query(F.data.startswith("skip_"))
async def process_skip(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    
    target_id = int(callback.data.split("_")[1])
    db.add_skip(callback.from_user.id, target_id)
    
    try:
        if callback.message.caption:
            await callback.message.edit_caption(callback.message.caption + "\n\n👋 [Skipped]", parse_mode="Markdown")
        else:
            await callback.message.edit_text(callback.message.text + "\n\n👋 [Skipped]", parse_mode="Markdown")
    except:
        pass
    
    await show_next_partner(bot, callback.message.chat.id, callback.from_user.id)


@matching_router.message(F.text == BTN_VIEW_MATCH)
async def view_match(message: Message, bot: Bot) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["pairing_status"] != "pending_pair":
        await message.answer("💔 No pending match!",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))
        return
    
    partner = db.get_match_partner(message.from_user.id)
    if not partner:
        await message.answer("😅 Match not found!")
        return
    
    await message.answer(MATCH_VIEW, parse_mode="Markdown")
    await send_partner_card(bot, message.chat.id, dict(partner),
                          get_pair_confirmation_keyboard(partner["user_id"]), show_username=True)


@matching_router.callback_query(F.data.startswith("confirm_pair_"))
async def confirm_pair(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    
    partner_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    success, both = db.confirm_pair(user_id)
    
    if not success:
        await callback.message.answer("😅 Error, try again!")
        return
    
    try:
        if callback.message.caption:
            await callback.message.edit_caption(callback.message.caption + "\n\n✅ [Confirmed]", parse_mode="Markdown")
        else:
            await callback.message.edit_text(callback.message.text + "\n\n✅ [Confirmed]", parse_mode="Markdown")
    except:
        pass
    
    if both:
        user = db.get_user(user_id)
        partner = db.get_user(partner_id)
        
        # Escape names and usernames for Markdown
        partner_name = escape_markdown(partner["first_name"])
        partner_username = escape_markdown(partner["username"])
        user_name = escape_markdown(user["first_name"])
        user_username = escape_markdown(user["username"])
        
        await callback.message.answer(
            MATCH_BOTH_CONFIRMED.format(name=partner_name, username=partner_username),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard("have_pair")
        )
        
        try:
            await bot.send_message(
                partner_id,
                MATCH_BOTH_CONFIRMED.format(name=user_name, username=user_username),
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard("have_pair")
            )
        except:
            pass
    else:
        partner = db.get_user(partner_id)
        partner_name = escape_markdown(partner["first_name"])
        await callback.message.answer(
            MATCH_CONFIRMED_WAIT.format(name=partner_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard("pending_pair")
        )


@matching_router.callback_query(F.data.startswith("reject_match_"))
async def reject_match(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    
    success, partner_id = db.reject_match(callback.from_user.id)
    
    if not success:
        await callback.message.answer("😅 Error!")
        return
    
    try:
        if callback.message.caption:
            await callback.message.edit_caption(callback.message.caption + "\n\n💔 [Declined]", parse_mode="Markdown")
        else:
            await callback.message.edit_text(callback.message.text + "\n\n💔 [Declined]", parse_mode="Markdown")
    except:
        pass
    
    await callback.message.answer(MATCH_REJECTED, parse_mode="Markdown",
                                 reply_markup=get_main_menu_keyboard("active_finding"))
    
    if partner_id:
        try:
            await bot.send_message(partner_id, MATCH_REJECTED_PARTNER, parse_mode="Markdown",
                                 reply_markup=get_main_menu_keyboard("active_finding"))
        except:
            pass


@matching_router.message(F.text == BTN_MY_PARTNER)
async def view_partner(message: Message, bot: Bot) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["pairing_status"] != "have_pair":
        await message.answer("💔 No partner yet!",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))
        return
    
    partner = db.get_user(user["partner_id"])
    if not partner:
        await message.answer("😅 Partner not found!")
        return
    
    await message.answer(PARTNER_VIEW, parse_mode="Markdown")
    await send_partner_card(bot, message.chat.id, dict(partner), show_username=True)


# ==================== UNPAIR ====================

@matching_router.message(F.text == BTN_REQUEST_UNPAIR)
async def request_unpair(message: Message) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["pairing_status"] != "have_pair":
        await message.answer("💔 No partner!")
        return
    
    partner = db.get_user(user["partner_id"])
    partner_name = escape_markdown(partner["first_name"])
    await message.answer(
        UNPAIR_CONFIRM.format(name=partner_name),
        parse_mode="Markdown",
        reply_markup=get_unpair_confirm_keyboard()
    )


@matching_router.message(F.text == BTN_YES_UNPAIR)
async def confirm_unpair(message: Message, state: FSMContext) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["pairing_status"] != "have_pair":
        await message.answer("💔 No partner!")
        return
    
    await state.set_state(RejectionStates.waiting_for_reason)
    await state.update_data(partner_id=user["partner_id"])
    await message.answer(UNPAIR_REASON, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())


@matching_router.message(F.text == BTN_NO_CANCEL)
async def cancel_unpair(message: Message) -> None:
    user = db.get_user(message.from_user.id)
    await message.answer(UNPAIR_CANCELLED, parse_mode="Markdown",
                       reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))


@matching_router.message(RejectionStates.waiting_for_reason)
async def process_reason(message: Message, state: FSMContext) -> None:
    reason = message.text.strip()
    
    if len(reason) < 10:
        await message.answer("💫 More detail needed (min 10 chars):")
        return
    if len(reason) > 500:
        await message.answer("💫 Too long (max 500 chars):")
        return
    
    data = await state.get_data()
    success = db.create_rejection_request(message.from_user.id, data["partner_id"], reason)
    
    await state.clear()
    
    if success:
        await message.answer(UNPAIR_SUBMITTED, parse_mode="Markdown",
                           reply_markup=get_main_menu_keyboard("rejection_pending"))
    else:
        user = db.get_user(message.from_user.id)
        await message.answer("😅 Error!",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))


@matching_router.message(F.text == BTN_CHECK_STATUS)
async def check_status(message: Message) -> None:
    user = db.get_user(message.from_user.id)
    
    if user and user["pairing_status"] == "rejection_pending":
        await message.answer(UNPAIR_STATUS_PENDING, parse_mode="Markdown")
    else:
        await message.answer("📋 No pending requests!",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"] if user else "inactive"))


@matching_router.message(F.text == BTN_CANCEL_REQUEST)
async def cancel_request(message: Message) -> None:
    user = db.get_user(message.from_user.id)
    
    if not user or user["pairing_status"] != "rejection_pending":
        await message.answer("📋 No pending request!")
        return
    
    success = db.cancel_rejection_request(message.from_user.id)
    
    if success:
        await message.answer("✅ Request cancelled! You remain paired 💕",
                           reply_markup=get_main_menu_keyboard("have_pair"))
    else:
        await message.answer("😅 Could not cancel.")