from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger
from paddle_billing import Client, Environment, Options
from paddle_billing.Notifications import Secret, Verifier
from paddle_billing.Resources.Transactions.Operations import CreateTransaction
from paddle_billing.Resources.Transactions.Operations.CreateTransaction import TransactionItem

from app.core.config import settings

class PaddleCheckoutRequest(BaseModel):
    product_id: str  # In Billing, this is usually the Price ID
    customer_email: Optional[str] = None
    custom_message: str = "PDF2Audiobook Conversion Credits"

class PaymentService:
    def __init__(self):
        env = Environment.SANDBOX if settings.PADDLE_ENVIRONMENT == "sandbox" else Environment.PRODUCTION
        self.client = Client(settings.PADDLE_API_KEY, options=Options(env)) if settings.PADDLE_API_KEY else None
        self.webhook_secret = settings.PADDLE_WEBHOOK_SECRET_KEY

    def generate_checkout_url(self, checkout_request: PaddleCheckoutRequest) -> str:
        """
        Generates a Paddle Billing checkout URL for a given price (product).
        """
        if settings.TESTING_MODE:
            logger.info("--- MOCK PAYMENT: Generating dummy checkout URL ---")
            return f"http://localhost:3000/mock-checkout?price_id={checkout_request.product_id}&email={checkout_request.customer_email}"

        if not self.client:
            raise Exception("Paddle API key not configured")

        # Create a transaction for the checkout
        # Note: In a real production app, you might want to associate this with a Customer ID if known
        transaction = self.client.transactions.create(CreateTransaction(
            items=[
                TransactionItem(price_id=checkout_request.product_id, quantity=1)
            ],
            # Pass email in custom data or use it to find/create customer
            custom_data={"user_email": checkout_request.customer_email} if checkout_request.customer_email else None
        ))
        
        # Construct the checkout URL using the transaction ID
        base_url = "https://sandbox-checkout.paddle.com" if settings.PADDLE_ENVIRONMENT == "sandbox" else "https://checkout.paddle.com"
        return f"{base_url}/checkout/transaction/{transaction.id}"

    def verify_webhook_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Verifies the signature of an incoming Paddle webhook using the official SDK.
        """
        if settings.TESTING_MODE:
            logger.info("--- MOCK PAYMENT: Skipping webhook verification ---")
            return True

        if not signature or not self.webhook_secret:
            logger.warning("--- WARNING: Signature or Webhook Secret missing. ---")
            return False

        try:
            # The SDK expects a Request-like object. 
            # We create a simple class to satisfy the interface.
            class SDKRequest:
                def __init__(self, body_bytes, headers_dict):
                    self.body = body_bytes
                    self.headers = headers_dict
            
            req = SDKRequest(request_body, {"Paddle-Signature": signature})
            return Verifier().verify(req, Secret(self.webhook_secret))
            
        except Exception as e:
            logger.error(f"--- Webhook verification failed: {e} ---")
            return False