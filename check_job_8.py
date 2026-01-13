import os
import sys
from sqlalchemy import create_engine, text

# Force SQLite connection string
db_url = "sqlite:///./backend/dev.db"
engine = create_engine(db_url)

print(f"Connecting to: {db_url}")

try:
    with engine.connect() as conn:
        print("\n--- Job 8 Raw Data ---")
        # Select raw values without ORM to see what's physically in the DB
        result = conn.execute(text("SELECT * FROM jobs WHERE id = 8"))
        row = result.fetchone()
        if not row:
            print("Job 8 NOT FOUND")
        else:
             # keys = result.keys() # keys() might not be available in all sqlalchemy versions on proxy
             print(f"Row: {row}")

except Exception as e:
    print(f"Error querying database: {e}")
