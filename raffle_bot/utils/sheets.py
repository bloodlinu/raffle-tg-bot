"""
utils/sheets.py — optional Google Sheets sync for approved tickets.
"""
import traceback
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_client = None
_sheet = None


def _init():
    global _client, _sheet
    if _client is not None:
        return True
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), GOOGLE_CREDENTIALS_FILE)
        creds = Credentials.from_service_account_file(
        creds_path, scopes=scopes
        )
        _client = gspread.authorize(creds)
        _sheet = _client.open_by_key(GOOGLE_SHEET_ID).sheet1
        logger.info("Google Sheets connected successfully")
        return True
    except Exception as e:
        logger.error("Google Sheets init failed: %s\n%s", e, traceback.format_exc())
        return False


def append_ticket(ticket_id: int, betine: str, user_id: int, username: str,
                  amount: int, tickets: int, deposit_date: str,
                  deposit_time: str, status: str = "Onaylandı") -> bool:
    from config import GOOGLE_SHEETS_ENABLED
    if not GOOGLE_SHEETS_ENABLED:
        return False
    if not _init():
        return False
    try:
        _sheet.append_row([
            ticket_id, betine, user_id, f"@{username}" if username else "—",
            amount, tickets, str(deposit_date), str(deposit_time),
            status, datetime.now().strftime("%d.%m.%Y %H:%M"),
        ])
        logger.info("Ticket #%s appended to Google Sheets", ticket_id)
        return True
    except Exception as e:
        logger.error("Google Sheets append failed: %s", e)
        return False
