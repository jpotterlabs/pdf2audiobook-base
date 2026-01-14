import os
from sqlalchemy import create_engine, text

# Force SQLite connection string
db_url = "sqlite:///./backend/dev.db"
engine = create_engine(db_url)

print(f"Connecting to: {db_url}")

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
