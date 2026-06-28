"""
handlers/rules.py — правила кампании и кнопка Free Spins.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import back_to_menu_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()

FREE_SPINS_URL = "https://betineclub.com/"


@router.message(F.text == t("btn_rules"))
async def btn_rules(message: Message):
    await message.answer(t("rules"), reply_markup=back_to_menu_kb())


@router.message(F.text == t("btn_free_spins"))
async def btn_free_spins(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("btn_free_spins"), url=FREE_SPINS_URL)
    ]])
    await message.answer(
        "🎰 <b>100 Free Spins</b> kazanmak için aşağıdaki butona tıklayın!",
        reply_markup=kb,
    )
