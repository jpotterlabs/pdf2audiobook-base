import os
import sys
# Add current directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Product
from loguru import logger
from paddle_billing import Client, Environment, Options
from paddle_billing.Resources.Products.Operations import ListProducts

def sync_products():
    """
    Fetches active products from Paddle and syncs them to the local database.
    """
    db = SessionLocal()
    
    # Initialize Paddle Client
    env = Environment.SANDBOX if settings.PADDLE_ENVIRONMENT == "sandbox" else Environment.PRODUCTION
    if not settings.PADDLE_API_KEY:
        logger.error("PADDLE_API_KEY is missing! Cannot sync.")
        return

    client = Client(settings.PADDLE_API_KEY, options=Options(env))
    logger.info(f"Syncing products from Paddle ({settings.PADDLE_ENVIRONMENT})...")

    try:
        # Fetch all products (filtering locally if needed, or using correct SDK params)
        paddle_products = list(client.products.list(ListProducts()))
        
        if not paddle_products:
            logger.warning("No active products found in Paddle!")
            return

        for pp in paddle_products:
            logger.info(f"Found Paddle Product: {pp.name} (ID: {pp.id})")
            
            # Determine tier and type based on name or custom data
            # This is a heuristic matching our known plan names
            tier = "free"
            ptype = "one_time"
            price = 0.0
            credits = 0
            
            name_lower = pp.name.lower()
            if "discover" in name_lower:
                tier = "free"
                ptype = "one_time" # Although free isn't really a product usually
            elif "research" in name_lower:
                tier = "pro"
                ptype = "subscription"
                price = 9.99
                credits = 3
            elif "intelligence" in name_lower:
                tier = "enterprise"
                ptype = "subscription"
                price = 19.99
                credits = 7
            else:
                 logger.warning(f"Skipping unknown product: {pp.name}")
                 continue

            # Upsert into DB
            product = db.query(Product).filter(Product.subscription_tier == tier).first()
            if not product:
                logger.info(f"Creating new local product records for tier: {tier}")
                product = Product(
                    paddle_product_id=pp.id,
                    name=pp.name,
                    description=pp.description or "",
                    price=price,
                    currency="USD", # Simplified
                    credits_included=credits,
                    subscription_tier=tier,
                    type=ptype,
                    is_active=True
                )
                db.add(product)
            else:
                logger.info(f"Updating ID for local product tier: {tier} -> {pp.id}")
                product.paddle_product_id = pp.id
                product.name = pp.name
                product.description = pp.description or product.description
                # We trust our local config for price/credits unless we want to fetch Prices too
            
        db.commit()
        logger.info("Product sync completed successfully!")

    except Exception as e:
        logger.error(f"Failed to sync products: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_products()
