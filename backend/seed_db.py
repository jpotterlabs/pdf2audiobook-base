import os
import sys
from sqlalchemy import text
# Add current directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from loguru import logger

def run_db_fixes():
    db = SessionLocal()
    if not db:
        logger.error("Could not connect to database")
        return

    try:
        # Helper to check enum labels
        def get_enum_labels(type_name):
            try:
                result = db.execute(text(
                    "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid WHERE t.typname = :name"
                ), {"name": type_name})
                return [row[0] for row in result]
            except Exception:
                return []

        # 1. Normalize conversionmode
        logger.info("Checking conversionmode enum...")
        labels = get_enum_labels('conversionmode')
        if labels:
            if 'FULL' in labels and 'full' not in labels:
                logger.info("Renaming FULL to full in conversionmode")
                db.execute(text("ALTER TYPE conversionmode RENAME VALUE 'FULL' TO 'full'"))
            if 'SUMMARY_EXPLANATION' in labels and 'summary_explanation' not in labels:
                logger.info("Renaming SUMMARY_EXPLANATION to summary_explanation in conversionmode")
                db.execute(text("ALTER TYPE conversionmode RENAME VALUE 'SUMMARY_EXPLANATION' TO 'summary_explanation'"))

        # 2. Normalize jobstatus
        logger.info("Checking jobstatus enum...")
        labels = get_enum_labels('jobstatus')
        if labels:
            for old, new in [('PENDING', 'pending'), ('PROCESSING', 'processing'), ('COMPLETED', 'completed'), ('FAILED', 'failed')]:
                if old in labels and new not in labels:
                    logger.info(f"Renaming {old} to {new} in jobstatus")
                    db.execute(text(f"ALTER TYPE jobstatus RENAME VALUE '{old}' TO '{new}'"))

        # 3. Normalize voiceprovider
        logger.info("Checking voiceprovider enum...")
        labels = get_enum_labels('voiceprovider')
        if labels:
            for old, new in [('OPENAI', 'openai'), ('GOOGLE', 'google'), ('AWS_POLLY', 'aws_polly'), ('AZURE', 'azure'), ('ELEVEN_LABS', 'eleven_labs')]:
                if old in labels and new not in labels:
                    logger.info(f"Renaming {old} to {new} in voiceprovider")
                    db.execute(text(f"ALTER TYPE voiceprovider RENAME VALUE '{old}' TO '{new}'"))

        db.commit()
        logger.info("DB fixes completed successfully!")
    except Exception as e:
        db.rollback()
        logger.error(f"DB fixes failed: {e}")
        # Re-raise so the build fails if this is critical
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_db_fixes()
