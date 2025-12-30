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
            result = db.execute(text(
                "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid WHERE t.typname = :name"
            ), {"name": type_name})
            return [row[0] for row in result]

        # 1. Normalize conversionmode
        logger.info("Checking conversionmode enum...")
        labels = get_enum_labels('conversionmode')
        if 'FULL' in labels and 'full' not in labels:
            logger.info("Renaming FULL to full in conversionmode")
            db.execute(text("ALTER TYPE conversionmode RENAME VALUE 'FULL' TO 'full'"))
        if 'SUMMARY_EXPLANATION' in labels and 'summary_explanation' not in labels:
            logger.info("Renaming SUMMARY_EXPLANATION to summary_explanation in conversionmode")
            db.execute(text("ALTER TYPE conversionmode RENAME VALUE 'SUMMARY_EXPLANATION' TO 'summary_explanation'"))

        # 2. Normalize subscriptiontier
        logger.info("Checking subscriptiontier enum...")
        labels = get_enum_labels('subscriptiontier')
        for old, new in [('FREE', 'free'), ('PRO', 'pro'), ('ENTERPRISE', 'enterprise')]:
            if old in labels and new not in labels:
                logger.info(f"Renaming {old} to {new} in subscriptiontier")
                db.execute(text(f"ALTER TYPE subscriptiontier RENAME VALUE '{old}' TO '{new}'"))

        # 3. Normalize producttype
        logger.info("Checking producttype enum...")
        labels = get_enum_labels('producttype')
        for old, new in [('SUBSCRIPTION', 'subscription'), ('ONE_TIME', 'one_time')]:
            if old in labels and new not in labels:
                logger.info(f"Renaming {old} to {new} in producttype")
                db.execute(text(f"ALTER TYPE producttype RENAME VALUE '{old}' TO '{new}'"))

        # 4. Normalize jobstatus
        logger.info("Checking jobstatus enum...")
        labels = get_enum_labels('jobstatus')
        for old, new in [('PENDING', 'pending'), ('PROCESSING', 'processing'), ('COMPLETED', 'completed'), ('FAILED', 'failed')]:
            if old in labels and new not in labels:
                logger.info(f"Renaming {old} to {new} in jobstatus")
                db.execute(text(f"ALTER TYPE jobstatus RENAME VALUE '{old}' TO '{new}'"))

        # 5. Normalize voiceprovider
        logger.info("Checking voiceprovider enum...")
        labels = get_enum_labels('voiceprovider')
        for old, new in [('OPENAI', 'openai'), ('GOOGLE', 'google'), ('AWS_POLLY', 'aws_polly'), ('AZURE', 'azure'), ('ELEVEN_LABS', 'eleven_labs')]:
            if old in labels and new not in labels:
                logger.info(f"Renaming {old} to {new} in voiceprovider")
                db.execute(text(f"ALTER TYPE voiceprovider RENAME VALUE '{old}' TO '{new}'"))

        # 6. Seed products
        logger.info("Seeding products...")
        products = [
            ('pro_01k5c6wwxw8fgxx6ad61s0vd78', 'The Discover', 'Pay as you go. Estimate cost based on characters and voices.', 0.00, 'USD', 0, 'free', 'one_time'),
            ('pro_01k5c7648e8ss1bak485ajctfp', 'The Research', '$9.99/mo. 3 audiobooks, 300k std / 100k premium chars, 1 summary/explanation per book.', 9.99, 'USD', 3, 'pro', 'subscription'),
            ('pro_01k5c7dgx4ayf68pfrxv6q586h', 'The Inteligence', '$19.99/mo. 7 audiobooks, 500k std / 250k premium chars, 5 summaries/explanations total.', 19.99, 'USD', 7, 'enterprise', 'subscription')
        ]
        for pid, name, desc, price, curr, credits, tier, ptype in products:
            logger.info(f"Upserting product: {name}")
            db.execute(text("""
                INSERT INTO products (paddle_product_id, name, description, price, currency, credits_included, subscription_tier, type, is_active, created_at)
                VALUES (:pid, :name, :desc, :price, :curr, :credits, :tier, :ptype, true, NOW())
                ON CONFLICT (paddle_product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    credits_included = EXCLUDED.credits_included,
                    subscription_tier = EXCLUDED.subscription_tier,
                    type = EXCLUDED.type,
                    is_active = true
            """), {"pid": pid, "name": name, "desc": desc, "price": price, "curr": curr, "credits": credits, "tier": tier, "ptype": ptype})
        
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
