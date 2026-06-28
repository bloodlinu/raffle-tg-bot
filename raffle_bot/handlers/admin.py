"""
handlers/admin.py — admin panel: approve/reject tickets, stats, broadcast.
"""

import logging
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from utils import sheets
from utils.security import escape_html, extract_id_from_callback
from config import ADMIN_IDS
from keyboards import admin_ticket_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminStates(StatesGroup):
    waiting_reject_reason = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin"))
        return

    pending = db.get_pending_tickets()
    if not pending:
        await message.answer("✅ No pending requests.")
        return

    await message.answer(f"📋 <b>{len(pending)} pending request(s):</b>")
    for ticket in pending[:20]:
        text = t(
            "admin_new_ticket",
            ticket_id=ticket["id"],
            username=ticket["username"] or "—",
            user_id=ticket["user_id"],
            platform_username=ticket["betine_name"],
            amount=f"{ticket['amount']:,}",
            tickets=ticket["ticket_count"],
            date=ticket["deposit_date"],
            time=ticket["deposit_time"],
        )
        await message.answer(text, reply_markup=admin_ticket_kb(ticket["id"]))


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin"))
        return

    with db.get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_tickets_week = conn.execute("""
            SELECT COALESCE(SUM(ticket_count), 0) FROM tickets
            WHERE status='approved'
            AND deposit_date BETWEEN date('now', 'weekday 0', '-6 days') AND date('now')
        """).fetchone()[0]
        pending_count = conn.execute(
            "SELECT COUNT(*) FROM tickets WHERE status='pending'"
        ).fetchone()[0]
        total_tickets_all = conn.execute(
            "SELECT COALESCE(SUM(ticket_count),0) FROM tickets WHERE status='approved'"
        ).fetchone()[0]

    await message.answer(
        f"📊 <b>Stats</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total users: <b>{total_users}</b>\n"
        f"🎟 Approved tickets this week: <b>{total_tickets_week}</b>\n"
        f"⏳ Pending requests: <b>{pending_count}</b>\n"
        f"🏆 Total approved tickets: <b>{total_tickets_all}</b>"
    )


@router.callback_query(F.data.startswith("adm_approve_"))
async def cb_approve(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Unauthorized!", show_alert=True)
        return

    ticket_id = extract_id_from_callback(call.data, "adm_approve_")
    if ticket_id is None:
        await call.answer("❌ Invalid request.", show_alert=True)
        return
    ticket = db.get_ticket(ticket_id)

    if not ticket:
        await call.answer("❌ Ticket not found.", show_alert=True)
        return
    if ticket["status"] != "pending":
        await call.answer(f"ℹ️ Status: {ticket['status']}", show_alert=True)
        return

    db.approve_ticket(ticket_id)

    try:
        user = db.get_user(ticket["user_id"])
        await asyncio.to_thread(
            sheets.append_ticket,
            ticket_id=ticket_id,
            betine=ticket["betine_name"],
            user_id=ticket["user_id"],
            username=user["username"] if user else "",
            amount=ticket["amount"],
            tickets=ticket["ticket_count"],
            deposit_date=ticket["deposit_date"],
            deposit_time=ticket["deposit_time"],
        )
    except Exception as e:
        logger.warning("Sheets sync failed for ticket #%s: %s", ticket_id, e)

    await call.message.edit_text(
        call.message.text + f"\n\n✅ <b>Approved</b> (@{call.from_user.username})"
    )

    try:
        await call.bot.send_message(
            ticket["user_id"],
            t("ticket_approved_user", tickets=ticket["ticket_count"]),
        )
    except Exception as e:
        logger.warning("Could not notify user %s: %s", ticket["user_id"], e)

    await call.answer(t("admin_approved", ticket_id=ticket_id))


@router.callback_query(F.data.startswith("adm_reject_"))
async def cb_reject_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Unauthorized!", show_alert=True)
        return

    ticket_id = extract_id_from_callback(call.data, "adm_reject_")
    if ticket_id is None:
        await call.answer("❌ Invalid request.", show_alert=True)
        return
    ticket = db.get_ticket(ticket_id)

    if not ticket or ticket["status"] != "pending":
        await call.answer("ℹ️ Cannot process.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_reject_reason)
    await state.update_data(ticket_id=ticket_id, msg_id=call.message.message_id)
    await call.message.answer(t("admin_ask_reject_reason"))
    await call.answer()


@router.message(AdminStates.waiting_reject_reason)
async def process_reject_reason(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    ticket_id = data["ticket_id"]

    if not message.text:
        await message.answer(t("text_required"))
        return

    raw_reason = "" if message.text.strip() == "-" else message.text.strip()
    reason = escape_html(raw_reason)

    db.reject_ticket(ticket_id, raw_reason)
    await state.clear()

    ticket = db.get_ticket(ticket_id)
    note_text = reason or "No reason provided."
    try:
        await message.bot.send_message(
            ticket["user_id"],
            t("ticket_rejected_user", note=note_text),
        )
    except Exception as e:
        logger.warning("Could not notify user: %s", e)

    await message.answer(t("admin_rejected", ticket_id=ticket_id))


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin"))
        return

    raw_text = message.text.removeprefix("/broadcast").strip()
    if not raw_text:
        await message.answer("Usage: /broadcast <message>")
        return
    text = escape_html(raw_text)

    with db.get_conn() as conn:
        users = conn.execute("SELECT user_id FROM users").fetchall()

    sent = failed = 0
    for row in users:
        try:
            await message.bot.send_message(row["user_id"], text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(f"📢 Sent: {sent} | Failed: {failed}")
