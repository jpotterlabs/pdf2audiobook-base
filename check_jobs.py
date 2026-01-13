import os
import sys

# Add backend directory to path if needed for imports, 
# though we are using sqlalchemy directly which doesn't need app code
sys.path.append(os.path.join(os.getcwd(), "backend"))

from sqlalchemy import create_engine, text

# Force SQLite connection string
db_url = "sqlite:///./backend/dev.db"
engine = create_engine(db_url)

print(f"Connecting to: {db_url}")

try:
    with engine.connect() as conn:
        print("\n--- Recent Jobs ---")
        # Use CORRECT column names: voice_provider (not provider)
        query = text('SELECT id, status, voice_provider, voice_type, created_at, progress_percentage FROM jobs ORDER BY id DESC LIMIT 5')
        result = conn.execute(query)
        rows = list(result)
        if not rows:
            print("No jobs found in database.")
        for row in rows:
            print(f"ID: {row[0]}, Status: {row[1]}, Provider: {row[2]}, Voice: {row[3]}, Created: {row[4]}, Progress: {row[5]}%")
except Exception as e:
    print(f"Error querying database: {e}")
