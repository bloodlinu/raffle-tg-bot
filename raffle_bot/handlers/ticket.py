"""
handlers/ticket.py — ticket submission flow.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import MIN_DEPOSIT, MAX_DEPOSIT, TICKETS_PER_DEPOSIT, ADMIN_IDS
from keyboards import cancel_kb, confirm_kb, main_menu_kb, admin_ticket_kb
from locales.i18n import t
from utils.time_utils import (
    parse_time, is_future_time, deposit_date_for_time,
    format_date_display, now_local, today_local,
)

logger = logging.getLogger(__name__)
router = Router()


class TicketStates(StatesGroup):
    waiting_amount = State()
    waiting_time   = State()
    confirming     = State()


@router.message(F.text == t("btn_request_ticket"))
async def btn_request_ticket(message: Message, state: FSMContext):
    await state.clear()
    if not db.get_user(message.from_user.id):
        from handlers.start import RegStates
        await message.answer(t("ask_username"), reply_markup=cancel_kb())
        await state.set_state(RegStates.waiting_username)
        return

    await message.answer(t("ask_amount"), reply_markup=cancel_kb())
    await state.set_state(TicketStates.waiting_amount)


@router.message(TicketStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(t("text_required"), reply_markup=cancel_kb())
        return

    if message.text.strip() == t("btn_cancel"):
        await _cancel(message, state)
        return

    raw = message.text.strip().replace(".", "").replace(",", "").replace(" ", "")
    if not raw.isdigit() or len(raw) > 9:
        await message.answer(t("amount_invalid"), reply_markup=cancel_kb())
        return

    amount = int(raw)
    if amount < MIN_DEPOSIT:
        await message.answer(t("amount_too_low"), reply_markup=cancel_kb())
        return
    if amount > MAX_DEPOSIT:
        await message.answer(t("amount_too_high"), reply_markup=cancel_kb())
        return

    await state.update_data(amount=amount)
    today_display = format_date_display(today_local())
    await message.answer(t("ask_time", date=today_display), reply_markup=cancel_kb())
    await state.set_state(TicketStates.waiting_time)


@router.message(TicketStates.waiting_time)
async def process_time(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(t("text_required"), reply_markup=cancel_kb())
        return

    if message.text.strip() == t("btn_cancel"):
        await _cancel(message, state)
        return

    parsed = parse_time(message.text.strip())
    if parsed is None:
        await message.answer(t("time_invalid"), reply_markup=cancel_kb())
        return

    if is_future_time(parsed):
        now = now_local()
        await message.answer(
            t("time_future", now=now.strftime("%H:%M"), entered=parsed.strftime("%H:%M")),
            reply_markup=cancel_kb(),
        )
        return

    data = await state.get_data()
    amount = data["amount"]
    deposit_date = deposit_date_for_time(parsed)
    tickets = amount // TICKETS_PER_DEPOSIT
    user = db.get_user(message.from_user.id)

    await state.update_data(
        deposit_time=parsed.strftime("%H:%M"),
        deposit_date=deposit_date.isoformat(),
        tickets=tickets,
    )

    await message.answer(
        t("confirm_ticket",
          username=user["platform_username"],
          amount=f"{amount:,}",
          tickets=tickets,
          date=format_date_display(deposit_date),
          time=parsed.strftime("%H:%M")),
        reply_markup=confirm_kb(),
    )
    await state.set_state(TicketStates.confirming)


@router.callback_query(F.data == "ticket_confirm", TicketStates.confirming)
async def confirm_ticket(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = db.get_user(call.from_user.id)

    from datetime import date
    ticket_id = db.create_ticket(
        user_id=call.from_user.id,
        platform_username=user["platform_username"],
        amount=data["amount"],
        deposit_date=date.fromisoformat(data["deposit_date"]),
        deposit_time=data["deposit_time"],
    )

    await state.clear()
    await call.message.edit_reply_markup()

    if ticket_id is None:
        await call.message.answer(t("ticket_duplicate"), reply_markup=main_menu_kb())
        await call.answer()
        return

    await call.message.answer(t("ticket_submitted"), reply_markup=main_menu_kb())

    from utils.security import escape_html
    admin_text = t(
        "admin_new_ticket",
        ticket_id=ticket_id,
        username=escape_html(user["username"] or "—"),
        user_id=call.from_user.id,
        platform_username=escape_html(user["platform_username"]),
        amount=f"{data['amount']:,}",
        tickets=data["tickets"],
        date=data["deposit_date"],
        time=data["deposit_time"],
    )
    for admin_id in ADMIN_IDS:
        try:
            await call.bot.send_message(
                admin_id, admin_text,
                reply_markup=admin_ticket_kb(ticket_id),
            )
        except Exception as e:
            logger.warning("Admin %s notify error: %s", admin_id, e)

    await call.answer()


@router.callback_query(F.data == "ticket_cancel", TicketStates.confirming)
async def cancel_ticket(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_reply_markup()
    await call.message.answer(t("ticket_cancelled"), reply_markup=main_menu_kb())
    await call.answer()


async def _cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(t("ticket_cancelled"), reply_markup=main_menu_kb())
