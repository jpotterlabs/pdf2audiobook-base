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

        # 4. Seed products
        logger.info("Seeding products...")
        products = [
            ('free_tier', 'Free Plan', 'Ideal for individuals starting their audiobook journey. 50 jobs per month included.', 0.00, 'USD', 50, 'free', 'subscription'),
            ('pro_monthly', 'Pro Plan', 'Power users who need more conversions and premium features. 50 jobs per month with priority processing.', 19.99, 'USD', 50, 'pro', 'subscription'),
            ('enterprise_monthly', 'Enterprise', 'Unlimited conversions and dedicated support for organizations.', 99.99, 'USD', 9999, 'enterprise', 'subscription')
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
