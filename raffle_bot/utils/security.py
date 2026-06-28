"""
utils/security.py — input sanitization & safe-parsing helpers.

These guard against:
  - Telegram HTML parse errors / markup injection from free-text input
    (admin broadcast messages, rejection reasons) since the bot runs with
    parse_mode=HTML globally.
  - Malformed/forged callback_data crashing handlers.

Note: SQL injection itself is prevented in database.py by using
parameterized queries (? placeholders) everywhere — never string-format
or concatenate user input into SQL. Nothing here changes that; these are
additional, separate layers of defense.
"""

import html
from typing import Optional


def escape_html(text: str) -> str:
    """
    Escape text that will be embedded in an HTML-parse-mode Telegram message.
    Use this for ANY free-text user/admin input that gets sent back to users
    (broadcast text, rejection reasons, etc.) — but NOT for text you already
    fully control and that intentionally contains your own <b>/<i> tags.
    """
    if text is None:
        return ""
    return html.escape(str(text), quote=False)


def safe_int(value, default: Optional[int] = None) -> Optional[int]:
    """Parse an int from arbitrary input, returning `default` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_id_from_callback(data: str, prefix: str) -> Optional[int]:
    """
    Safely extract a trailing numeric id from callback_data like
    'adm_approve_42' -> 42. Returns None if data doesn't match the
    expected prefix or the suffix isn't a valid integer.
    """
    if not data or not data.startswith(prefix):
        return None
    return safe_int(data[len(prefix):])
