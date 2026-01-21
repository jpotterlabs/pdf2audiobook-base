import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent

# Ensure backend matches where dev.db is expected to be
db_path = BACKEND_DIR / "dev.db"
db_url = f"sqlite:///{db_path}"

print(f"Connecting to: {db_url}")

# Verify file exists first (optional depending on use case, but WAL is usually for existing DB)
# But sqlalchemy creates it if not exists.

engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        print("Checking current journal_mode...")
        result = conn.execute(text("PRAGMA journal_mode"))
        current_mode = result.fetchone()[0]
        print(f"Current mode: {current_mode}")

        if current_mode.upper() != "WAL":
            print("Enabling WAL mode...")
            result = conn.execute(text("PRAGMA journal_mode=WAL"))
            new_mode = result.fetchone()[0]
            print(f"New mode: {new_mode}")
        else:
            print("WAL mode already enabled.")

except Exception as e:
    print(f"Error: {e}")

