"""Run this once to initialize the database."""
import sys
sys.path.insert(0, ".")
from database import init_db
init_db()
print("✅ Database initialized successfully.")
