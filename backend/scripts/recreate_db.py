import sys
import os
from pathlib import Path

# Resolve the project root and backend directory
# This script is at backend/scripts/recreate_db.py
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Add backend directory to sys.path to allow 'from app...' imports
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import engine
from app.models import Job, User, Base

def recreate_db():
    safe_url = engine.url.render_as_string(hide_password=True)
    print(f"Creating database tables using engine: {safe_url}...")
    
    # Handle SQLite file removal specifically
    if 'sqlite' in engine.url.drivername:
        # Check if using a relative path that usually points to backend/dev.db
        # The engine url might be "sqlite:///./backend/dev.db" or "sqlite:///./dev.db" depending on env
        
        # We try to locate the DB file to delete it
        # Assuming dev.db is in backend/ directory usually
        db_path = BACKEND_DIR / "dev.db"
        
        if db_path.exists():
             print(f"Removing existing {db_path} to start fresh...")
             db_path.unlink()
        elif os.path.exists("dev.db"): # Fallback check in CWD
             print("Removing existing dev.db from CWD...")
             os.remove("dev.db")
            
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    recreate_db()
