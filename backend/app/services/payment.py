import requests
from pydantic import BaseModel
from typing import List, Dict, Any
from hashlib import sha1
import hmac
import base64

from app.core.config import settings

class PaddleCheckoutRequest(BaseModel):
    product_id: int
    customer_email: str
    custom_message: str = "PDF2Audiobook Conversion Credits"

class PaymentService:
    def __init__(self):
        self.vendor_id = settings.PADDLE_VENDOR_ID
        self.vendor_auth_code = settings.PADDLE_VENDOR_AUTH_CODE
        self.public_key = settings.PADDLE_PUBLIC_KEY
        self.api_endpoint = "https://vendors.paddle.com/api/2.0"
        self.sandbox_api_endpoint = "https://sandbox-vendors.paddle.com/api/2.0"

    def _get_api_url(self) -> str:
        return self.sandbox_api_endpoint if settings.PADDLE_ENVIRONMENT == "sandbox" else self.api_endpoint

    def generate_checkout_url(self, checkout_request: PaddleCheckoutRequest) -> str:
        """
        Generates a Paddle checkout URL for a given product.
        """
        if settings.TESTING_MODE:
            print("--- MOCK PAYMENT: Generating dummy checkout URL ---")
            return f"http://localhost:3000/mock-checkout?product_id={checkout_request.product_id}&email={checkout_request.customer_email}"

        url = f"{self._get_api_url()}/product/generate_pay_link"
        payload = {
            "vendor_id": self.vendor_id,
            "vendor_auth_code": self.vendor_auth_code,
            "product_id": checkout_request.product_id,
            "customer_email": checkout_request.customer_email,
            "custom_message": checkout_request.custom_message,
            "passthrough": f'{{"user_email": "{checkout_request.customer_email}"}}' # Example passthrough
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success"):
            return data["response"]["url"]
        else:
            raise Exception(f"Paddle API error: {data.get('error', {}).get('message', 'Unknown error')}")

    def verify_webhook_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Verifies the signature of an incoming Paddle webhook using the official SDK.
        """
        if settings.TESTING_MODE:
            print("--- MOCK PAYMENT: Skipping webhook verification ---")
            return True

        if not signature:
            return False

        secret_key = settings.PADDLE_WEBHOOK_SECRET_KEY
        if not secret_key:
            # If no secret key is configured, we cannot verify. 
            # (Unless falling back to old method, but user asked for modern)
            print("--- WARNING: PADDLE_WEBHOOK_SECRET_KEY not set. Verification failing. ---")
            return False

        try:
            # Modern Paddle Billing Verification
            from paddle_billing.Notifications import Secret, Verifier
            
            # The SDK expects a Request object with 'headers' and 'body' attributes.
            # We create a simple class todduck-type expectation. 
            class SDKRequest:
                def __init__(self, body_bytes, headers_dict):
                    self.body = body_bytes
                    self.headers = headers_dict
            
            # SDK's Verifier internal logic:
            # raw_body = request.body.decode("utf-8")
            # So we pass the bytes directly in .body
            req = SDKRequest(request_body, {"Paddle-Signature": signature})
            
            verifier = Verifier()
            # verify(request, secrets)
            return verifier.verify(req, Secret(secret_key))
            
        except ImportError:
            print("--- ERROR: paddle-python-sdk not installed. cannot verify. ---")
            return False
        except Exception as e:
            print(f"--- Webhook verification failed: {e} ---")
            return False