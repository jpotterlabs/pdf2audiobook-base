import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from paddle_billing import Client, Environment, Options
from paddle_billing.Resources.Products.Operations import ListProducts
from paddle_billing.Resources.Prices.Operations import ListPrices
from loguru import logger

def test_paddle():
    print(f"Testing Paddle API Key: {settings.PADDLE_API_KEY[:5]}***")
    print(f"Environment: {settings.PADDLE_ENVIRONMENT}")
    
    env = Environment.SANDBOX if settings.PADDLE_ENVIRONMENT == "sandbox" else Environment.PRODUCTION
    client = Client(settings.PADDLE_API_KEY, options=Options(env))

    print("\n--- Attempting ListProducts ---")
    try:
        products = list(client.products.list(ListProducts()))
        print(f"SUCCESS: Found {len(products)} products.")
        for p in products:
            print(f" - {p.name} ({p.id})")
    except Exception as e:
        print(f"FAILURE: ListProducts failed: {e}")

    print("\n--- Attempting ListPrices ---")
    try:
        prices = list(client.prices.list(ListPrices()))
        print(f"SUCCESS: Found {len(prices)} prices.")
        for p in prices:
            print(f" - Price {p.id} for Product {p.product_id}")
    except Exception as e:
        print(f"FAILURE: ListPrices failed: {e}")

if __name__ == "__main__":
    test_paddle()
