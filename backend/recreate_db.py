import sys
import os

# Ensure backend root is in sys.path. 
# Since we are running from backend/, the current directory is the root for app imports.
sys.path.append(os.getcwd())

from app.core.database import engine
from app.models import Job, User, Base

def recreate_db():
    print(f"Creating database tables using engine: {engine.url}...")
    # Explicitly verify we are writing to dev.db in CWD
    if 'sqlite' in str(engine.url) and 'dev.db' in str(engine.url):
        print(f"Working directory: {os.getcwd()}")
        if os.path.exists("dev.db"):
            print("Removing existing dev.db to start fresh...")
            os.remove("dev.db")
            
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    recreate_db()
