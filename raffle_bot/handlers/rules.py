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
