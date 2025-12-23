
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
        # 1. Create Webhook Events table
        logger.info("Creating webhook_events table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id SERIAL PRIMARY KEY,
                paddle_event_id VARCHAR(255),
                event_type VARCHAR(255) NOT NULL,
                payload TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'received',
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_webhook_events_id ON webhook_events (id);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_webhook_events_paddle_event_id ON webhook_events (paddle_event_id);"))

        # 2. Update Users table
        logger.info("Updating users table...")
        # Check if credit_balance exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='credit_balance'"))
        if not result.fetchone():
            logger.info("Adding credit_balance column to users")
            db.execute(text("ALTER TABLE users ADD COLUMN credit_balance NUMERIC(10, 2) DEFAULT 0.00"))
        
        # 3. Update Jobs table
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
