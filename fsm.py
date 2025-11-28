"""
FSM states for all bot flows.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """User registration flow."""
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_course = State()
    waiting_for_interests = State()
    waiting_for_media = State()
    waiting_for_about_me = State()
    waiting_for_preferred_gender = State()
    waiting_for_preferred_age = State()
    confirm_profile = State()


class RejectionStates(StatesGroup):
    """Unpair request flow."""
    waiting_for_reason = State()


class AdminStates(StatesGroup):
    """Admin operations."""
    waiting_for_broadcast = State()
    confirm_broadcast = State()
    waiting_for_dm_user_id = State()
    waiting_for_dm_message = State()


class DeleteAccountStates(StatesGroup):
    """Delete account flow."""
    confirm_deletion = State()