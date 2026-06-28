"""
handlers/start.py — /start command and user registration.
"""

import re
import logging
import os
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import main_menu_kb, cancel_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")

WELCOME_IMAGE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "welcome.jpg"
)


class RegStates(StatesGroup):
    waiting_username = State()
    waiting_new_username = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = db.get_user(message.from_user.id)

    if user:
        await message.answer(t("main_menu"), reply_markup=main_menu_kb())
    else:
        ask_text = t("ask_username")
        if os.path.exists(WELCOME_IMAGE):
            await message.answer_photo(
                photo=FSInputFile(WELCOME_IMAGE),
                caption=ask_text,
                reply_markup=cancel_kb(),
            )
        else:
            await message.answer(ask_text, reply_markup=cancel_kb())
        await state.set_state(RegStates.waiting_username)


@router.message(RegStates.waiting_username)
async def reg_username(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(t("text_required"), reply_markup=cancel_kb())
        return

    name = message.text.strip()

    if t("btn_cancel") in name:
        await state.clear()
        await message.answer(t("ask_username"), reply_markup=cancel_kb())
        return

    if not USERNAME_RE.match(name):
        await message.answer(t("username_invalid"), reply_markup=cancel_kb())
        return

    username = message.from_user.username or ""
    db.upsert_user(message.from_user.id, username, name, "en")
    await state.clear()
    await message.answer(t("username_saved", name=name), reply_markup=main_menu_kb())


@router.callback_query(F.data == "change_username")
async def cb_change_username(call: CallbackQuery, state: FSMContext):
    await call.message.answer(t("change_username"), reply_markup=cancel_kb())
    await state.set_state(RegStates.waiting_new_username)
    await call.answer()


@router.message(RegStates.waiting_new_username)
async def reg_new_username(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(t("text_required"), reply_markup=cancel_kb())
        return

    name = message.text.strip()

    if t("btn_cancel") in name:
        await state.clear()
        await message.answer(t("main_menu"), reply_markup=main_menu_kb())
        return

    if not USERNAME_RE.match(name):
        await message.answer(t("username_invalid"), reply_markup=cancel_kb())
        return

    db.set_platform_username(message.from_user.id, name)
    await state.clear()
    await message.answer(t("username_saved", name=name), reply_markup=main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(t("main_menu"), reply_markup=main_menu_kb())
    await call.answer()


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer(t("ask_username"), reply_markup=cancel_kb())
        await state.set_state(RegStates.waiting_username)
        return
    await message.answer(t("main_menu"), reply_markup=main_menu_kb())
