from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json
import logging

from app.core.database import get_db
from app.core.config import settings
from app.services.payment import PaymentService
from app.services.user import UserService

router = APIRouter()
logger = logging.getLogger(__name__)


from app.models import WebhookEvent

@router.post(
    "/paddle",
    summary="Handle Paddle Webhooks",
    description="This single endpoint receives all webhook notifications from Paddle for events like successful payments, new subscriptions, cancellations, etc. It verifies the webhook signature and processes the event to update user data accordingly.",
)
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles all incoming webhooks from Paddle.
    """
    event_log = None
    try:
        # Get the raw body and signature
        raw_body = await request.body()
        signature = request.headers.get("Paddle-Signature") or request.headers.get("x-paddle-signature")
        
        # Parse webhook data first to get event type for logging
        try:
            body_str = raw_body.decode()
            webhook_data = json.loads(body_str)

            event_type = webhook_data.get("alert_name") or webhook_data.get("event_type") or "unknown"
            event_id = webhook_data.get("alert_id") or webhook_data.get("event_id") or "unknown"
        except Exception:
            webhook_data = {}
            event_type = "parse_error"
            event_id = "unknown"
            body_str = str(raw_body)

        # Log event received
        event_log = WebhookEvent(
            paddle_event_id=str(event_id),
            event_type=str(event_type),
            payload=body_str,
            status="received"
        )
        db.add(event_log)
        db.commit()
        db.refresh(event_log)

        # Verify webhook signature
        payment_service = PaymentService()
        if not payment_service.verify_webhook_signature(raw_body, signature):
            event_log.status = "failed"
            event_log.error_message = "Invalid webhook signature"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        # Process event
        user_service = UserService(db)

        if event_type in ["subscription_created", "subscription.created"]:
            user_service.handle_subscription_created(webhook_data)
        elif event_type in ["subscription_payment_succeeded", "subscription.activated", "subscription.updated"]:
            # Note: subscription.updated might need more logic to check if it was a payment
            user_service.handle_subscription_payment(webhook_data)
        elif event_type in ["subscription_cancelled", "subscription.canceled"]:
            user_service.handle_subscription_cancelled(webhook_data)
        elif event_type in ["payment_succeeded", "transaction.completed"]:
            # Handle one-time payment (credit packs)
            user_service.handle_payment_succeeded(webhook_data)
        
        # Update log status
        event_log.status = "processed"
        db.commit()

        return {"status": "success"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}", exc_info=True)
        if event_log:
            event_log.status = "failed"
            event_log.error_message = str(e)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}",
        )
