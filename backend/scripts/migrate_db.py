
import os
import sys
from sqlalchemy import text
from loguru import logger

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import SessionLocal

def migrate():
    try:
        db = SessionLocal()
        
        # 1. Update Jobs table
        logger.info("Updating jobs table...")
        # Check chars_processed
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='jobs' AND column_name='chars_processed'"))
        if not result.fetchone():
            logger.info("Adding chars_processed column to jobs")
            db.execute(text("ALTER TABLE jobs ADD COLUMN chars_processed INTEGER DEFAULT 0"))
        
        # Check tokens_used
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='jobs' AND column_name='tokens_used'"))
        if not result.fetchone():
            logger.info("Adding tokens_used column to jobs")
            db.execute(text("ALTER TABLE jobs ADD COLUMN tokens_used INTEGER DEFAULT 0"))

        db.commit()
        logger.info("Migration completed successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
