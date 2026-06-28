"""
database.py — SQLite persistence layer for Raffle Bot.

Tables:
  users    — registered users
  tickets  — ticket requests (pending / approved / rejected)
  winners  — historical raffle winners
"""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Optional

from config import DB_PATH

logger = logging.getLogger(__name__)

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id          INTEGER PRIMARY KEY,
            username         TEXT,
            platform_username TEXT NOT NULL,
            lang             TEXT NOT NULL DEFAULT 'en',
            registered_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(user_id),
            platform_username TEXT NOT NULL,
            amount           INTEGER NOT NULL,
            ticket_count     INTEGER NOT NULL,
            deposit_date     DATE NOT NULL,
            deposit_time     TEXT NOT NULL,
            status           TEXT NOT NULL DEFAULT 'pending',
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at      TIMESTAMP,
            rejected_at      TIMESTAMP,
            admin_note       TEXT
        );

        CREATE TABLE IF NOT EXISTS winners (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start       DATE NOT NULL,
            week_end         DATE NOT NULL,
            prize_rank       INTEGER NOT NULL,
            prize_amount     INTEGER NOT NULL,
            platform_username TEXT NOT NULL,
            user_id          INTEGER,
            announced_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_tickets_user   ON tickets(user_id);
        CREATE INDEX IF NOT EXISTS idx_tickets_date   ON tickets(deposit_date);
        CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_dedupe
            ON tickets(user_id, amount, deposit_date, deposit_time);
        """)
    logger.info("Database initialized at %s", DB_PATH)


# ─── Users ─────────────────────────────────────────────────────────────────────

def upsert_user(user_id: int, username: str, platform_username: str, lang: str = "en") -> None:
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO users (user_id, username, platform_username, lang)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username          = excluded.username,
                platform_username = excluded.platform_username,
                lang              = excluded.lang
        """, (user_id, username or "", platform_username, lang))


def get_user(user_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()


def set_user_lang(user_id: int, lang: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))


def set_platform_username(user_id: int, name: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET platform_username = ? WHERE user_id = ?", (name, user_id)
        )


# ─── Tickets ───────────────────────────────────────────────────────────────────

def create_ticket(
    user_id: int,
    platform_username: str,
    amount: int,
    deposit_date: date,
    deposit_time: str,
) -> Optional[int]:
    """Returns the new ticket id, or None if a duplicate (same user, amount, date, time)."""
    from config import TICKETS_PER_DEPOSIT
    ticket_count = amount // TICKETS_PER_DEPOSIT
    with get_conn() as conn:
        try:
            cur = conn.execute("""
                INSERT INTO tickets
                    (user_id, platform_username, amount, ticket_count, deposit_date, deposit_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, platform_username, amount, ticket_count, deposit_date, deposit_time))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            logger.info("Duplicate ticket submission ignored for user %s", user_id)
            return None


def get_ticket(ticket_id: int) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()


def approve_ticket(ticket_id: int) -> None:
    with get_conn() as conn:
        conn.execute("""
            UPDATE tickets
            SET status = 'approved', approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (ticket_id,))


def reject_ticket(ticket_id: int, note: str = "") -> None:
    with get_conn() as conn:
        conn.execute("""
            UPDATE tickets
            SET status = 'rejected', rejected_at = CURRENT_TIMESTAMP, admin_note = ?
            WHERE id = ?
        """, (note, ticket_id))


def get_user_tickets_this_week(user_id: int) -> list:
    from utils.time_utils import get_week_range
    start, end = get_week_range()
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM tickets
            WHERE user_id = ? AND deposit_date BETWEEN ? AND ?
            AND status = 'approved'
            ORDER BY created_at DESC
        """, (user_id, start, end)).fetchall()


def get_user_total_tickets(user_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COALESCE(SUM(ticket_count), 0) as total
            FROM tickets WHERE user_id = ? AND status = 'approved'
        """, (user_id,)).fetchone()
        return row["total"] if row else 0


def get_user_total_prize(user_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute("""
            SELECT COALESCE(SUM(prize_amount), 0) as total
            FROM winners WHERE user_id = ?
        """, (user_id,)).fetchone()
        return row["total"] if row else 0


def get_pending_tickets() -> list:
    with get_conn() as conn:
        return conn.execute("""
            SELECT t.*, u.username FROM tickets t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.status = 'pending'
            ORDER BY t.created_at ASC
        """).fetchall()


# ─── Leaderboard ───────────────────────────────────────────────────────────────

def get_weekly_leaderboard(limit: int = 10) -> list:
    from utils.time_utils import get_week_range
    start, end = get_week_range()
    with get_conn() as conn:
        return conn.execute("""
            SELECT
                u.platform_username,
                SUM(t.ticket_count) as total_tickets,
                t.user_id
            FROM tickets t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.deposit_date BETWEEN ? AND ?
            AND t.status = 'approved'
            GROUP BY t.user_id
            ORDER BY total_tickets DESC
            LIMIT ?
        """, (start, end, limit)).fetchall()


def get_week_label() -> str:
    from utils.time_utils import get_week_range
    start, end = get_week_range()
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d')}"
