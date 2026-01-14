import os
import sys
from sqlalchemy import create_engine, text

# Force SQLite connection string
db_url = "sqlite:///./backend/dev.db"
engine = create_engine(db_url)

print(f"Connecting to: {db_url}")

try:
    with engine.connect() as conn:
        print("\n--- jobs Table Info ---")
        # SQLite specific pragma to list columns
        result = conn.execute(text("PRAGMA table_info(jobs)"))
        columns = [row[1] for row in result]
        print(f"Columns: {columns}")
        
        missing = []
        expected = ["estimated_cost", "chars_processed", "tokens_used", "voice_provider", "conversion_mode"]
        for col in expected:
            if col not in columns:
                missing.append(col)
        
        if missing:
             print(f"\n❌ MISSING COLUMNS: {missing}")
        else:
             print("\n✅ All expected columns present.")

except Exception as e:
    print(f"Error querying database: {e}")
