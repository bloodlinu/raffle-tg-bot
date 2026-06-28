"""
keyboards.py — all keyboards for the Raffle Bot.
"""

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from locales.i18n import t

WEBSITE_URL = "https://example.com/"


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t("btn_request_ticket")),
        KeyboardButton(text=t("btn_leaderboard")),
    )
    builder.row(
        KeyboardButton(text=t("btn_rules")),
        KeyboardButton(text=t("btn_profile")),
    )
    builder.row(
        KeyboardButton(text=t("btn_website")),
    )
    return builder.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=t("btn_cancel")))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_confirm"), callback_data="ticket_confirm"),
        InlineKeyboardButton(text=t("btn_cancel"),  callback_data="ticket_cancel"),
    )
    return builder.as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_win_history"),    callback_data="win_history"),
        InlineKeyboardButton(text=t("btn_prize_dist"),     callback_data="prize_dist"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_change_username"), callback_data="change_username"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_main_menu"), callback_data="main_menu"),
    )
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=t("btn_main_menu"), callback_data="main_menu")
    )
    return builder.as_markup()


def admin_ticket_kb(ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Approve", callback_data=f"adm_approve_{ticket_id}"
        ),
        InlineKeyboardButton(
            text="❌ Reject", callback_data=f"adm_reject_{ticket_id}"
        ),
    )
    return builder.as_markup()
