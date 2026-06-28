"""
time_utils.py — timezone-aware helpers for Raffle Bot.
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from config import TIMEZONE

TZ = ZoneInfo(TIMEZONE)


def now_local() -> datetime:
    """Current datetime in configured timezone."""
    return datetime.now(TZ)


def today_local() -> date:
    return now_local().date()


def parse_time(raw: str) -> time | None:
    """
    Parse HH:MM string. Returns None on bad format.
    Accepts '14:35' and '1435'.
    """
    raw = raw.strip().replace(".", ":").replace("-", ":")
    if len(raw) == 4 and raw.isdigit():
        raw = raw[:2] + ":" + raw[2:]
    try:
        h, m = raw.split(":")
        return time(int(h), int(m))
    except Exception:
        return None


def is_future_time(t: time) -> bool:
    """True if given time (today) is strictly after current local time."""
    now = now_local()
    return t > now.time().replace(second=0, microsecond=0)


def deposit_date_for_time(t: time) -> date:
    """
    Special rule: deposits between 00:00–01:00 count as previous day.
    """
    today = today_local()
    if t < time(1, 0):
        return today - timedelta(days=1)
    return today


def get_week_range() -> tuple[date, date]:
    """Returns (Monday, Sunday) of the current week."""
    today = today_local()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)                  # Sunday
    return start, end


def format_date_display(d: date) -> str:
    """Returns date as DD.MM.YYYY with (Today) or (Yesterday) suffix."""
    today = today_local()
    if d == today:
        suffix = " (Today)"
    elif d == today - timedelta(days=1):
        suffix = " (Yesterday)"
    else:
        suffix = ""
    return f"{d.strftime('%d.%m.%Y')}{suffix}"
