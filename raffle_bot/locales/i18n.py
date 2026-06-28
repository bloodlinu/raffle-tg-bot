"""
i18n.py — all bot strings in English.
Usage: t("key", var=value)
"""

from typing import Any

STRINGS: dict[str, str] = {

    # ── Registration ──────────────────────────────────────────────────────────
    "ask_username": (
        "👤 Enter your platform username:\n\n<i>Example: john_doe</i>"
    ),
    "username_saved": (
        "✅ Username saved: <b>{name}</b>\n\n"
        "Redirecting to the main menu..."
    ),
    "username_invalid": (
        "❌ Invalid username. Only letters, numbers and underscores are allowed."
    ),
    "text_required": "❌ Please send a text message.",

    # ── Main menu ─────────────────────────────────────────────────────────────
    "main_menu": (
        "🎉 <b>Weekly Raffle</b>\n\n"
        "🏆 Weekly prize pool: <b>$1,000</b>\n"
        "🎟 Every <b>$10</b> deposit = <b>1 ticket</b>\n"
        "⚡️ Draw happens every Sunday!\n\n"
        "🥇 1st prize: <b>$500</b>\n"
        "🥈 2nd prize: <b>$300</b>\n"
        "🥉 3rd prize: <b>$200</b>\n\n"
        "Choose an option:"
    ),

    # ── Ticket flow ───────────────────────────────────────────────────────────
    "ask_amount": "💰 Enter your deposit amount ($):\n\n<i>Example: 50</i>",
    "amount_invalid": (
        "❌ Invalid amount. Please enter a number.\n\n<i>Example: 50</i>"
    ),
    "amount_too_low": "❌ Minimum deposit is <b>$10</b>.",
    "amount_too_high": (
        "❌ Maximum deposit is <b>$10,000</b>. "
        "Please contact support for larger amounts."
    ),
    "ask_time": (
        "🕐 Enter the time of your deposit:\n\n"
        "Format: <b>HH:MM</b>\n"
        "Example: <b>14:35</b>\n\n"
        "📅 Date assigned automatically: <b>{date}</b>"
    ),
    "time_invalid": (
        "❌ Invalid time format. Please use <b>HH:MM</b>.\n\n"
        "<i>Example: 14:35</i>"
    ),
    "time_future": (
        "⚠️ <b>You cannot enter a future time!</b>\n\n"
        "🕐 Current time: <b>{now}</b>\n"
        "📝 You entered: <b>{entered}</b>\n\n"
        "Please enter a valid time (e.g. {now}):"
    ),
    "confirm_ticket": (
        "📋 <b>Ticket Summary</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 Username: <b>{username}</b>\n"
        "💰 Deposit: <b>${amount}</b>\n"
        "🎟 Tickets: <b>{tickets}</b>\n"
        "📅 Date: <b>{date}</b>\n"
        "🕐 Time: <b>{time}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Confirm submission?"
    ),
    "ticket_submitted": (
        "✅ <b>Your ticket request has been submitted.</b>\n\n"
        "You will receive a notification once it is reviewed.\n\n"
        "⚠️ Please do not block or mute the bot — "
        "all notifications are sent through it."
    ),
    "ticket_cancelled": "❌ Action cancelled.",
    "ticket_duplicate": (
        "⚠️ This request looks like a duplicate (same amount and time). Please wait."
    ),

    # ── Approve / reject (user notification) ─────────────────────────────────
    "ticket_approved_user": (
        "✅ <b>Your ticket request has been approved!</b>\n\n"
        "🎟 <b>{tickets} ticket(s)</b> added to your account.\n"
        "📅 Draw: this Sunday\n\n"
        "Good luck! 🍀"
    ),
    "ticket_rejected_user": (
        "❌ <b>Your ticket request was rejected.</b>\n\n"
        "{note}\n\n"
        "If you have questions, please contact support."
    ),

    # ── Profile ───────────────────────────────────────────────────────────────
    "profile": (
        "👤 <b>My Profile</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 Username: <b>{username}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📅 <b>THIS WEEK</b>\n"
        "🎟 My tickets: <b>{week_tickets}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 <b>ALL TIME</b>\n"
        "🎫 Total tickets: <b>{total_tickets}</b>\n"
        "💰 Total winnings: <b>${total_prize}</b>"
    ),
    "change_username": "✏️ Enter your new platform username:",

    # ── Leaderboard ───────────────────────────────────────────────────────────
    "leaderboard_header": (
        "🏆 <b>Leaderboard</b>\n📅 Week of {week}\n━━━━━━━━━━━━━━━━━━━━"
    ),
    "leaderboard_row": "{medal} <b>{name}</b> — {tickets} tickets",
    "leaderboard_empty": "No approved tickets this week yet.",

    # ── Rules ─────────────────────────────────────────────────────────────────
    "rules": (
        "📋 <b>Campaign Rules</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎟 Every <b>$10</b> deposit earns <b>1 ticket</b>.\n\n"
        "📅 Requests must be submitted on the day of the deposit.\n\n"
        "⏰ Deposits made between <b>00:00–01:00</b> are counted as "
        "the <b>previous day</b>.\n\n"
        "🚫 Requests for past days are not accepted.\n\n"
        "🚫 Future deposit times cannot be entered.\n\n"
        "💰 Min/max withdrawal equals the deposit amount."
    ),

    # ── Prize distribution ────────────────────────────────────────────────────
    "prize_dist": (
        "💰 <b>Prize Distribution</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🥇 1st prize: <b>$500</b>\n"
        "🥈 2nd prize: <b>$300</b>\n"
        "🥉 3rd prize: <b>$200</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 Total prize pool: <b>$1,000</b>"
    ),

    # ── Buttons ───────────────────────────────────────────────────────────────
    "btn_request_ticket": "🎟 Request Ticket",
    "btn_leaderboard":    "🏆 Leaderboard",
    "btn_rules":          "📋 Rules",
    "btn_profile":        "👤 My Profile",
    "btn_website":        "🌐 Visit Website",
    "btn_main_menu":      "🏠 Main Menu",
    "btn_cancel":         "❌ Cancel",
    "btn_confirm":        "✅ Submit",
    "btn_change_username":"✏️ Change Username",
    "btn_prize_dist":     "💰 Prize Distribution",
    "btn_win_history":    "🏅 Win History",

    # ── Admin ─────────────────────────────────────────────────────────────────
    "admin_new_ticket": (
        "🔔 <b>New Ticket Request</b> #{ticket_id}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 User: @{username} (<code>{user_id}</code>)\n"
        "🎮 Username: <b>{platform_username}</b>\n"
        "💰 Deposit: <b>${amount}</b>\n"
        "🎟 Tickets: <b>{tickets}</b>\n"
        "📅 Date: <b>{date}</b>\n"
        "🕐 Time: <b>{time}</b>"
    ),
    "admin_approved": "✅ Request #{ticket_id} approved.",
    "admin_rejected": "❌ Request #{ticket_id} rejected.",
    "admin_ask_reject_reason": "❓ Enter rejection reason (send - to skip):",
    "not_admin": "⛔ You don't have permission to use this command.",

    # ── Errors ────────────────────────────────────────────────────────────────
    "error_generic": "⚠️ Something went wrong. Please try again.",
    "win_history_empty": "You haven't won any prizes yet. Good luck! 🍀",
}


def t(key: str, **kwargs: Any) -> str:
    text = STRINGS.get(key, f"[{key}]")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def get_user_lang(user_id: int) -> str:
    return "en"
