"""
handlers/profile.py — user profile, win history, prize distribution.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import profile_kb, back_to_menu_kb
from locales.i18n import t

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == t("btn_profile"))
async def btn_profile(message: Message):
    await _show_profile(message.from_user.id, message)


@router.callback_query(F.data == "profile")
async def cb_profile(call: CallbackQuery):
    await _show_profile(call.from_user.id, call.message)
    await call.answer()


async def _show_profile(user_id: int, target):
    user = db.get_user(user_id)
    if not user:
        from keyboards import cancel_kb
        await target.answer(t("ask_username"), reply_markup=cancel_kb())
        return

    week_tickets_rows = db.get_user_tickets_this_week(user_id)
    week_tickets = sum(r["ticket_count"] for r in week_tickets_rows)
    total_tickets = db.get_user_total_tickets(user_id)
    total_prize = db.get_user_total_prize(user_id)

    await target.answer(
        t("profile",
          username=user["betine_name"],
          week_tickets=week_tickets,
          total_tickets=total_tickets,
          total_prize=f"{total_prize:,}"),
        reply_markup=profile_kb(),
    )


@router.callback_query(F.data == "win_history")
async def cb_win_history(call: CallbackQuery):
    user = db.get_user(call.from_user.id)
    if not user:
        await call.answer()
        return

    with db.get_conn() as conn:
        rows = conn.execute("""
            SELECT prize_rank, prize_amount, week_start, week_end
            FROM winners WHERE user_id = ?
            ORDER BY announced_at DESC LIMIT 20
        """, (call.from_user.id,)).fetchall()

    if not rows:
        await call.message.answer(t("win_history_empty"), reply_markup=back_to_menu_kb())
        await call.answer()
        return

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = ["🏅 <b>Win History</b>\n━━━━━━━━━━━━━━━━━━━━"]
    for r in rows:
        medal = medals.get(r["prize_rank"], "🏆")
        lines.append(
            f"{medal} {r['week_start']} – {r['week_end']} → "
            f"<b>${r['prize_amount']:,}</b>"
        )

    await call.message.answer("\n".join(lines), reply_markup=back_to_menu_kb())
    await call.answer()


@router.callback_query(F.data == "prize_dist")
async def cb_prize_dist(call: CallbackQuery):
    await call.message.answer(t("prize_dist"), reply_markup=back_to_menu_kb())
    await call.answer()
