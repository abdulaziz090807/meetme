"""
All keyboard layouts.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import COURSES
from texts import (
    BTN_FIND_PARTNER, BTN_MY_PROFILE, BTN_EDIT_PROFILE, BTN_MY_FILTERS,
    BTN_DELETE_ACCOUNT, BTN_VIEW_MATCH, BTN_MY_PARTNER, BTN_REQUEST_UNPAIR, BTN_CHECK_STATUS,
    BTN_CANCEL_REQUEST, BTN_LIKE, BTN_SKIP, BTN_WANT_PAIR, BTN_SEARCH_ANOTHER,
    BTN_MALE, BTN_FEMALE, BTN_ANY, BTN_SKIP_SIMPLE, BTN_SUBMIT, BTN_CANCEL,
    BTN_YES_UNPAIR, BTN_NO_CANCEL, BTN_ADMIN_PENDING, BTN_ADMIN_REJECTIONS,
    BTN_ADMIN_PAIRS, BTN_ADMIN_STATS, BTN_ADMIN_BROADCAST, BTN_ADMIN_DM,
    BTN_ADMIN_BOT_CONTROL, BTN_APPROVE, BTN_REJECT, BTN_BAN
)


# ==================== REGISTRATION ====================

def get_gender_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_MALE), KeyboardButton(text=BTN_FEMALE)]],
        resize_keyboard=True, one_time_keyboard=True
    )


def get_course_keyboard() -> ReplyKeyboardMarkup:
    rows = []
    for i in range(0, len(COURSES), 2):
        row = [KeyboardButton(text=COURSES[i])]
        if i + 1 < len(COURSES):
            row.append(KeyboardButton(text=COURSES[i + 1]))
        rows.append(row)
    rows.append([KeyboardButton(text=BTN_SKIP_SIMPLE)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_SKIP_SIMPLE)]],
        resize_keyboard=True, one_time_keyboard=True
    )


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_SUBMIT), KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True, one_time_keyboard=True
    )


def get_preferred_gender_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MALE), KeyboardButton(text=BTN_FEMALE)],
            [KeyboardButton(text=BTN_ANY)]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )


# ==================== MAIN MENU ====================

def get_main_menu_keyboard(pairing_status: str) -> ReplyKeyboardMarkup:
    """Dynamic main menu based on status."""
    
    if pairing_status == "active_finding":
        keyboard = [
            [KeyboardButton(text=BTN_FIND_PARTNER)],
            [KeyboardButton(text=BTN_MY_PROFILE), KeyboardButton(text=BTN_EDIT_PROFILE)],
            [KeyboardButton(text=BTN_MY_FILTERS), KeyboardButton(text=BTN_DELETE_ACCOUNT)]
        ]
    elif pairing_status == "pending_pair":
        keyboard = [
            [KeyboardButton(text=BTN_VIEW_MATCH)],
            [KeyboardButton(text=BTN_MY_PROFILE), KeyboardButton(text=BTN_DELETE_ACCOUNT)]
        ]
    elif pairing_status == "have_pair":
        keyboard = [
            [KeyboardButton(text=BTN_MY_PARTNER)],
            [KeyboardButton(text=BTN_MY_PROFILE), KeyboardButton(text=BTN_REQUEST_UNPAIR)],
            [KeyboardButton(text=BTN_DELETE_ACCOUNT)]
        ]
    elif pairing_status == "rejection_pending":
        keyboard = [
            [KeyboardButton(text=BTN_MY_PROFILE)],
            [KeyboardButton(text=BTN_CHECK_STATUS), KeyboardButton(text=BTN_CANCEL_REQUEST)],
            [KeyboardButton(text=BTN_DELETE_ACCOUNT)]
        ]
    else:
        keyboard = [
            [KeyboardButton(text=BTN_MY_PROFILE)],
            [KeyboardButton(text=BTN_DELETE_ACCOUNT)]
        ]
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ==================== MATCHING ====================

def get_matching_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=BTN_LIKE, callback_data=f"like_{target_user_id}"),
            InlineKeyboardButton(text=BTN_SKIP, callback_data=f"skip_{target_user_id}")
        ]]
    )


def get_pair_confirmation_keyboard(partner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BTN_WANT_PAIR, callback_data=f"confirm_pair_{partner_id}")],
            [InlineKeyboardButton(text=BTN_SEARCH_ANOTHER, callback_data=f"reject_match_{partner_id}")]
        ]
    )


def get_unpair_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_YES_UNPAIR)],
            [KeyboardButton(text=BTN_NO_CANCEL)]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )


# ==================== ADMIN ====================

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BTN_ADMIN_PENDING, callback_data="admin_pending")],
            [InlineKeyboardButton(text=BTN_ADMIN_REJECTIONS, callback_data="admin_rejections")],
            [InlineKeyboardButton(text=BTN_ADMIN_PAIRS, callback_data="admin_pairs")],
            [InlineKeyboardButton(text=BTN_ADMIN_STATS, callback_data="admin_stats")],
            [
                InlineKeyboardButton(text=BTN_ADMIN_BROADCAST, callback_data="admin_broadcast"),
                InlineKeyboardButton(text=BTN_ADMIN_DM, callback_data="admin_dm")
            ],
            [InlineKeyboardButton(text=BTN_ADMIN_BOT_CONTROL, callback_data="admin_bot_control")]
        ]
    )


def get_admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BTN_APPROVE, callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text=BTN_REJECT, callback_data=f"reject_{user_id}")
            ],
            [InlineKeyboardButton(text=BTN_BAN, callback_data=f"ban_{user_id}")]
        ]
    )


def get_admin_rejection_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=BTN_APPROVE, callback_data=f"approve_unpair_{request_id}"),
            InlineKeyboardButton(text=BTN_REJECT, callback_data=f"deny_unpair_{request_id}")
        ]]
    )


def get_admin_bot_control_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Restart Bot", callback_data="admin_restart_bot")],
            [InlineKeyboardButton(text="🛑 Stop Bot", callback_data="admin_stop_bot")],
            [InlineKeyboardButton(text="« Back", callback_data="admin_back")]
        ]
    )


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Send", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="broadcast_cancel")
            ]
        ]
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True, one_time_keyboard=True
    )