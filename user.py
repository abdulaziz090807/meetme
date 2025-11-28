"""
User handlers - registration, profile, filters.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

import database as db
from config import COURSES, MIN_AGE, MAX_AGE
from states import RegistrationStates, DeleteAccountStates
from keyboards import (
    get_gender_keyboard, get_course_keyboard, get_skip_keyboard,
    get_confirm_keyboard, get_preferred_gender_keyboard, get_main_menu_keyboard,
    get_cancel_keyboard
)
from texts import (
    WELCOME_NEW, WELCOME_BACK, USERNAME_REQUIRED, BANNED_MESSAGE,
    REG_FIRST_NAME, REG_AGE, REG_GENDER, REG_COURSE, REG_INTERESTS,
    REG_MEDIA, REG_ABOUT, REG_PREF_GENDER, REG_PREF_AGE, REG_PREVIEW,
    REG_SUCCESS, REG_CANCELLED, PROFILE_VIEW, FILTERS_VIEW, ERROR_CANT_EDIT,
    DELETE_ACCOUNT_CONFIRM, DELETE_ACCOUNT_SUCCESS, DELETE_ACCOUNT_CANCELLED,
    DELETE_ACCOUNT_PARTNER_NOTIF,
    BTN_SKIP_SIMPLE, BTN_SUBMIT, BTN_CANCEL, BTN_MALE, BTN_FEMALE, BTN_ANY,
    BTN_MY_PROFILE, BTN_EDIT_PROFILE, BTN_MY_FILTERS, BTN_DELETE_ACCOUNT,
    get_gender_emoji, get_gender_text, format_approval_status,
    format_pairing_status, build_optional_line
)

user_router = Router()


def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown."""
    if not text:
        return ""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    
    if not message.from_user.username:
        await message.answer(USERNAME_REQUIRED, parse_mode="Markdown")
        return
    
    user = db.get_user(message.from_user.id)
    
    if user:
        if user["is_banned"]:
            await message.answer(
                BANNED_MESSAGE.format(reason=user["ban_reason"] or "Not specified"),
                parse_mode="Markdown"
            )
            return
        
        # Allow rejected users to re-register
        if user["approval_status"] == "rejected":
            await message.answer(
                "💫 *Your previous profile was not approved.*\n\nLet's create a new profile! Please enter your *first name*:",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(RegistrationStates.waiting_for_first_name)
            return
        
        await message.answer(
            WELCOME_BACK.format(
                name=user["first_name"],
                approval_status=format_approval_status(user["approval_status"]),
                pairing_status=format_pairing_status(user["pairing_status"])
            ),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(user["pairing_status"])
        )
    else:
        await message.answer(WELCOME_NEW, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.waiting_for_first_name)


@user_router.message(Command("profile"))
@user_router.message(F.text == BTN_MY_PROFILE)
async def cmd_profile(message: Message, bot: Bot) -> None:
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("👋 Use /start to create your profile!")
        return
    
    u = dict(user)
    
    # Escape special characters in user data
    first_name = escape_markdown(u["first_name"])
    last_name = escape_markdown(u["last_name"])
    username = escape_markdown(u["username"])
    course = escape_markdown(u.get("course", ""))
    interests = escape_markdown(u.get("interests", ""))
    about_me = escape_markdown(u.get("about_me", ""))
    
    text = PROFILE_VIEW.format(
        first_name=first_name,
        last_name=last_name,
        user_id=u["user_id"],
        username=username,
        age=u["age"],
        gender_emoji=get_gender_emoji(u["gender"]),
        gender=get_gender_text(u["gender"]),
        course_line=f"🎓 Course: {course}\n" if course else "",
        interests_line=f"💝 Interests: {interests}\n" if interests else "",
        about_line=f"💭 About: {about_me}\n" if about_me else "",
        approval_status=format_approval_status(u["approval_status"]),
        pairing_status=format_pairing_status(u["pairing_status"]),
        pref_gender=u["preferred_gender"].title(),
        pref_age_min=u["preferred_age_min"],
        pref_age_max=u["preferred_age_max"]
    )
    
    if u.get("media_file_id") and u.get("media_type"):
        if u["media_type"] == "photo":
            await bot.send_photo(message.chat.id, u["media_file_id"], caption=text, parse_mode="Markdown")
        elif u["media_type"] == "video":
            await bot.send_video(message.chat.id, u["media_file_id"], caption=text, parse_mode="Markdown")
        elif u["media_type"] == "video_note":
            await bot.send_video_note(message.chat.id, u["media_file_id"])
            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(text + "\n\n📷 [No media]", parse_mode="Markdown")


@user_router.message(F.text == BTN_MY_FILTERS)
async def show_filters(message: Message) -> None:
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("👋 Use /start to create your profile!")
        return
    
    await message.answer(
        FILTERS_VIEW.format(
            gender_emoji=get_gender_emoji(user["preferred_gender"]) if user["preferred_gender"] != "any" else "💫",
            pref_gender=user["preferred_gender"].title(),
            pref_age_min=user["preferred_age_min"],
            pref_age_max=user["preferred_age_max"]
        ),
        parse_mode="Markdown"
    )


# ==================== REGISTRATION ====================

@user_router.message(RegistrationStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name.replace(" ", "").replace("-", "").isalpha() or len(name) < 2 or len(name) > 50:
        await message.answer("💫 Please enter a valid first name (2-50 letters):")
        return
    
    await state.update_data(first_name=name.title())
    await state.set_state(RegistrationStates.waiting_for_last_name)
    await message.answer(REG_FIRST_NAME.format(name=name.title()), parse_mode="Markdown")


@user_router.message(RegistrationStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name.replace(" ", "").replace("-", "").isalpha() or len(name) < 2 or len(name) > 50:
        await message.answer("💫 Please enter a valid last name (2-50 letters):")
        return
    
    await state.update_data(last_name=name.title())
    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer(REG_AGE.format(min_age=MIN_AGE, max_age=MAX_AGE), parse_mode="Markdown")


@user_router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext) -> None:
    try:
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE:
            await message.answer(f"💫 Age must be {MIN_AGE}-{MAX_AGE}:")
            return
    except ValueError:
        await message.answer("💫 Please enter a valid number:")
        return
    
    await state.update_data(age=age)
    await state.set_state(RegistrationStates.waiting_for_gender)
    await message.answer(REG_GENDER, parse_mode="Markdown", reply_markup=get_gender_keyboard())


@user_router.message(RegistrationStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lower()
    if BTN_FEMALE.lower() in text or "female" in text:
        gender = "female"
    elif BTN_MALE.lower() in text or "male" in text:
        gender = "male"
    else:
        await message.answer("💫 Please use the buttons:", reply_markup=get_gender_keyboard())
        return
    
    await state.update_data(gender=gender)
    await state.set_state(RegistrationStates.waiting_for_course)
    await message.answer(REG_COURSE, parse_mode="Markdown", reply_markup=get_course_keyboard())


@user_router.message(RegistrationStates.waiting_for_course)
async def process_course(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if BTN_SKIP_SIMPLE in text or text.lower() == "skip":
        course = ""
    elif text in COURSES:
        course = text
    else:
        await message.answer("💫 Please select from options:", reply_markup=get_course_keyboard())
        return
    
    await state.update_data(course=course)
    await state.set_state(RegistrationStates.waiting_for_interests)
    await message.answer(REG_INTERESTS, parse_mode="Markdown", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if BTN_SKIP_SIMPLE in text or text.lower() == "skip":
        interests = ""
    elif len(text) > 200:
        await message.answer("💫 Too long (max 200 chars):", reply_markup=get_skip_keyboard())
        return
    else:
        interests = text
    
    await state.update_data(interests=interests)
    await state.set_state(RegistrationStates.waiting_for_media)
    await message.answer(REG_MEDIA, parse_mode="Markdown", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_media, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(media_file_id=message.photo[-1].file_id, media_type="photo")
    await state.set_state(RegistrationStates.waiting_for_about_me)
    await message.answer(REG_ABOUT, parse_mode="Markdown", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_media, F.video)
async def process_video(message: Message, state: FSMContext) -> None:
    if message.video.duration and message.video.duration > 60:
        await message.answer("💫 Video too long (max 1 min):", reply_markup=get_skip_keyboard())
        return
    await state.update_data(media_file_id=message.video.file_id, media_type="video")
    await state.set_state(RegistrationStates.waiting_for_about_me)
    await message.answer(REG_ABOUT, parse_mode="Markdown", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_media, F.video_note)
async def process_video_note(message: Message, state: FSMContext) -> None:
    await state.update_data(media_file_id=message.video_note.file_id, media_type="video_note")
    await state.set_state(RegistrationStates.waiting_for_about_me)
    await message.answer(REG_ABOUT, parse_mode="Markdown", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_media, F.text)
async def process_media_skip(message: Message, state: FSMContext) -> None:
    if BTN_SKIP_SIMPLE in message.text or message.text.strip().lower() == "skip":
        await state.update_data(media_file_id=None, media_type=None)
        await state.set_state(RegistrationStates.waiting_for_about_me)
        await message.answer(REG_ABOUT, parse_mode="Markdown", reply_markup=get_skip_keyboard())
    else:
        await message.answer("💫 Send photo/video or Skip:", reply_markup=get_skip_keyboard())


@user_router.message(RegistrationStates.waiting_for_about_me)
async def process_about_me(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if BTN_SKIP_SIMPLE in text or text.lower() == "skip":
        about = ""
    elif len(text) > 500:
        await message.answer("💫 Too long (max 500 chars):", reply_markup=get_skip_keyboard())
        return
    else:
        about = text
    
    await state.update_data(about_me=about)
    await state.set_state(RegistrationStates.waiting_for_preferred_gender)
    await message.answer(REG_PREF_GENDER, parse_mode="Markdown", reply_markup=get_preferred_gender_keyboard())


@user_router.message(RegistrationStates.waiting_for_preferred_gender)
async def process_pref_gender(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lower()
    if BTN_ANY.lower() in text or "any" in text:
        pref = "any"
    elif BTN_FEMALE.lower() in text or "female" in text:
        pref = "female"
    elif BTN_MALE.lower() in text or "male" in text:
        pref = "male"
    else:
        await message.answer("💫 Use the buttons:", reply_markup=get_preferred_gender_keyboard())
        return
    
    await state.update_data(preferred_gender=pref)
    await state.set_state(RegistrationStates.waiting_for_preferred_age)
    await message.answer(
        REG_PREF_AGE.format(min_age=MIN_AGE, max_age=MAX_AGE),
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard()
    )


@user_router.message(RegistrationStates.waiting_for_preferred_age)
async def process_pref_age(message: Message, state: FSMContext, bot: Bot) -> None:
    text = message.text.strip()
    
    if BTN_SKIP_SIMPLE in text or text.lower() == "skip":
        pmin, pmax = MIN_AGE, MAX_AGE
    else:
        try:
            parts = text.replace(" ", "").split("-")
            pmin = int(parts[0])
            pmax = int(parts[1]) if len(parts) > 1 else pmin
            if pmin < MIN_AGE or pmax > MAX_AGE or pmin > pmax:
                await message.answer(f"💫 Valid range: {MIN_AGE}-{MAX_AGE}:", reply_markup=get_skip_keyboard())
                return
        except (ValueError, IndexError):
            await message.answer("💫 Format: 18-22 or Skip:", reply_markup=get_skip_keyboard())
            return
    
    await state.update_data(preferred_age_min=pmin, preferred_age_max=pmax)
    await state.set_state(RegistrationStates.confirm_profile)
    
    data = await state.get_data()
    
    # Escape special characters in user data
    first_name = escape_markdown(data["first_name"])
    last_name = escape_markdown(data["last_name"])
    course = escape_markdown(data.get("course", ""))
    interests = escape_markdown(data.get("interests", ""))
    about_me = escape_markdown(data.get("about_me", ""))
    
    text = REG_PREVIEW.format(
        first_name=first_name,
        last_name=last_name,
        user_id=message.from_user.id,
        age=data["age"],
        gender_emoji=get_gender_emoji(data["gender"]),
        gender=get_gender_text(data["gender"]),
        course_line=f"🎓 Course: {course}\n" if course else "",
        interests_line=f"💝 Interests: {interests}\n" if interests else "",
        about_line=f"💭 About: {about_me}\n" if about_me else "",
        pref_gender=data["preferred_gender"].title(),
        pref_age_min=pmin,
        pref_age_max=pmax
    )
    
    if data.get("media_file_id") and data.get("media_type"):
        if data["media_type"] == "photo":
            await bot.send_photo(message.chat.id, data["media_file_id"], caption=text,
                               parse_mode="Markdown", reply_markup=get_confirm_keyboard())
        elif data["media_type"] == "video":
            await bot.send_video(message.chat.id, data["media_file_id"], caption=text,
                               parse_mode="Markdown", reply_markup=get_confirm_keyboard())
        elif data["media_type"] == "video_note":
            await bot.send_video_note(message.chat.id, data["media_file_id"])
            await message.answer(text, parse_mode="Markdown", reply_markup=get_confirm_keyboard())
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=get_confirm_keyboard())


@user_router.message(RegistrationStates.confirm_profile)
async def process_confirm(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lower()
    
    if BTN_SUBMIT.lower() in text or "submit" in text:
        data = await state.get_data()
        success = db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            gender=data["gender"],
            course=data.get("course", ""),
            interests=data.get("interests", ""),
            about_me=data.get("about_me", ""),
            media_file_id=data.get("media_file_id"),
            media_type=data.get("media_type"),
            preferred_gender=data.get("preferred_gender", "any"),
            preferred_age_min=data.get("preferred_age_min", MIN_AGE),
            preferred_age_max=data.get("preferred_age_max", MAX_AGE)
        )
        await state.clear()
        
        if success:
            await message.answer(REG_SUCCESS, parse_mode="Markdown",
                               reply_markup=get_main_menu_keyboard("inactive"))
        else:
            await message.answer("😔 Error or banned. Contact admin.", reply_markup=ReplyKeyboardRemove())
    
    elif BTN_CANCEL.lower() in text or "cancel" in text:
        await state.clear()
        await message.answer(REG_CANCELLED, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("💫 Use Submit or Cancel:", reply_markup=get_confirm_keyboard())


@user_router.message(F.text == BTN_EDIT_PROFILE)
async def edit_profile(message: Message, state: FSMContext) -> None:
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("👋 Use /start first!")
        return
    
    if user["pairing_status"] in ["pending_pair", "have_pair", "rejection_pending"]:
        await message.answer(ERROR_CANT_EDIT, parse_mode="Markdown",
                           reply_markup=get_main_menu_keyboard(user["pairing_status"]))
        return
    
    await message.answer(
        "✏️ *Edit Profile*\n\nEnter your *first name*:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_first_name)



# ==================== DELETE ACCOUNT ====================

@user_router.message(F.text == BTN_DELETE_ACCOUNT)
@user_router.message(Command("delete_account"))
async def cmd_delete_account(message: Message, state: FSMContext) -> None:
    """Start delete account flow."""
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("👋 You don't have an account to delete!")
        return
    
    await state.set_state(DeleteAccountStates.confirm_deletion)
    await message.answer(
        DELETE_ACCOUNT_CONFIRM,
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )


@user_router.message(DeleteAccountStates.confirm_deletion)
async def process_delete_confirmation(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process delete account confirmation."""
    text = message.text.strip()
    
    if text == BTN_CANCEL or text.lower() == "cancel":
        await state.clear()
        user = db.get_user(message.from_user.id)
        pairing_status = user["pairing_status"] if user else "inactive"
        await message.answer(
            DELETE_ACCOUNT_CANCELLED,
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(pairing_status)
        )
        return
    
    if text.upper() != "DELETE":
        await message.answer(
            "💫 Please type *DELETE* to confirm or tap Cancel.",
            parse_mode="Markdown",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Delete the account
    success, partner_id = db.delete_user_account(message.from_user.id)
    await state.clear()
    
    if success:
        # Notify partner if they had one
        if partner_id:
            try:
                await bot.send_message(
                    partner_id,
                    DELETE_ACCOUNT_PARTNER_NOTIF,
                    parse_mode="Markdown",
                    reply_markup=get_main_menu_keyboard("active_finding")
                )
            except:
                pass
        
        await message.answer(
            DELETE_ACCOUNT_SUCCESS,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "😔 Error deleting account. Please try again or contact admin.",
            reply_markup=ReplyKeyboardRemove()
        )
