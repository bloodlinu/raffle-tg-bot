"""
handlers/leaderboard.py — weekly leaderboard.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import back_to_menu_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def _mask_name(name: str) -> str:
    if len(name) <= 4:
        return name[:2] + "***"
    return name[:3] + "***" + name[-2:]


@router.message(F.text == t("btn_leaderboard"))
async def btn_leaderboard(message: Message):
    await _show_leaderboard(message.from_user.id, message)


@router.callback_query(F.data == "leaderboard")
async def cb_leaderboard(call: CallbackQuery):
    await _show_leaderboard(call.from_user.id, call.message)
    await call.answer()


async def _show_leaderboard(user_id: int, target):
    rows = db.get_weekly_leaderboard(limit=10)
    week_label = db.get_week_label()

    lines = [t("leaderboard_header", week=week_label)]

    if not rows:
        lines.append(t("leaderboard_empty"))
    else:
        for i, row in enumerate(rows, start=1):
            medal = MEDALS.get(i, "⭐")
            masked = _mask_name(row["betine_name"])
            if row["user_id"] == user_id:
                masked = row["betine_name"] + " 👈"
            lines.append(t("leaderboard_row", medal=medal, name=masked, tickets=row["total_tickets"]))

    await target.answer("\n".join(lines), reply_markup=back_to_menu_kb())


cat > /tmp/raffle_bot/handlers/rules.py << 'EOF'
"""
handlers/rules.py — campaign rules and website button.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import back_to_menu_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()

WEBSITE_URL = "https://example.com/"


@router.message(F.text == t("btn_rules"))
async def btn_rules(message: Message):
    await message.answer(t("rules"), reply_markup=back_to_menu_kb())


@router.message(F.text == t("btn_website"))
async def btn_website(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_website"), url=WEBSITE_URL)
    ]])
    await message.answer(
        "🌐 Visit our website:",
        reply_markup=kb,
    )
