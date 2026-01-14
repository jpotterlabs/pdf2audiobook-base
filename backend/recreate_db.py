import sys
import os

# Ensure backend root is in sys.path. 
# Since we are running from backend/, the current directory is the root for app imports.
sys.path.append(os.getcwd())

from app.core.database import engine
from app.models import Job, User, Base

def recreate_db():
    safe_url = engine.url.render_as_string(hide_password=True)
    print(f"Creating database tables using engine: {safe_url}...")
    # Explicitly verify we are writing to dev.db in CWD
    if 'sqlite' in engine.url.drivername and 'dev.db' in safe_url:
        print(f"Working directory: {os.getcwd()}")
        if os.path.exists("dev.db"):
            print("Removing existing dev.db to start fresh...")
            os.remove("dev.db")
            
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    recreate_db()
