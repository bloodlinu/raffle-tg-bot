import os
from dotenv import load_dotenv

load_dotenv()

# ─── Bot ───────────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ─── Admin ─────────────────────────────────────────────────────────────────────
# Add all admin Telegram user IDs here (comma-separated in .env)
ADMIN_IDS: list[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip()
]

# ─── Google Sheets (optional) ──────────────────────────────────────────────────
GOOGLE_SHEETS_ENABLED: bool = os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"
GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")

# ─── Raffle settings ──────────────────────────────────────────────────────────
MIN_DEPOSIT: int = 10             # minimum deposit amount
MAX_DEPOSIT: int = 10_000         # sanity cap to reject absurd input
TICKETS_PER_DEPOSIT: int = 10     # deposit units per 1 ticket
RAFFLE_DAY: int = 6               # Sunday (0=Mon … 6=Sun)

# Prize pool
PRIZE_POOL = {
    1: 500,
    2: 300,
    3: 200,
}
TOTAL_PRIZE_POOL: int = 1_000

# ─── Timezone ──────────────────────────────────────────────────────────────────
TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

# ─── Storage ───────────────────────────────────────────────────────────────────
DB_PATH: str = os.getenv("DB_PATH", "data/raffle.db")
