import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import engine, Base
from app.models import job, user  # Import models so they are registered in Base

def recreate_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    recreate_db()
