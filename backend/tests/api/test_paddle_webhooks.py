
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.models import WebhookEvent, User
import json

# Mock the PaymentService verification
@pytest.fixture
def mock_payment_verify():
    with patch("app.services.payment.PaymentService.verify_webhook_signature") as mock:
        yield mock

def test_paddle_webhook_success(client, db_session, mock_payment_verify):
    # Setup
    mock_payment_verify.return_value = True
    
    payload = {
        "event_type": "payment_succeeded",
        "event_id": "evt_123",
        "email": "test@example.com",
        "checkout_id": "ch_12345",
        "sale_gross": "12.99",
        "product_id": "prod_123",
        "data": {"user_id": 1, "amount": 100} 
    }
    # Note: Payload structure depends on actual Paddle event. 
    # For now, simplistic test to verify flow, not specific handling logic which is covered elsewhere.
    
    response = client.post(
        "/api/v1/webhooks/paddle",
        json=payload,
        headers={"Paddle-Signature": "valid_sig"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # Verify DB Log
    all_logs = db_session.query(WebhookEvent).all()
    print(f"DEBUG LOGS: {[(log.paddle_event_id, log.status, log.error_message) for log in all_logs]}")
    
    log = db_session.query(WebhookEvent).filter_by(paddle_event_id="evt_123").first()
    assert log is not None
    assert log.status == "processed"
    assert log.event_type == "payment_succeeded"

def test_paddle_webhook_invalid_signature(client, db_session, mock_payment_verify):
    mock_payment_verify.return_value = False
    
    payload = {"event_id": "evt_bad_sig", "event_type": "test"}
    
    response = client.post(
        "/api/v1/webhooks/paddle",
        json=payload,
        headers={"Paddle-Signature": "invalid"}
    )
    
    assert response.status_code == 401
    
    # Verify DB Log - should be failed
    log = db_session.query(WebhookEvent).filter_by(paddle_event_id="evt_bad_sig").first()
    assert log is not None
    assert log.status == "failed"
    assert "Invalid webhook signature" in log.error_message

def test_paddle_webhook_processing_error(client, db_session, mock_payment_verify):
    mock_payment_verify.return_value = True
    
    # Force an error in processing by sending malformed data that handler crashes on?
    # Or patch the user service.
    with patch("app.services.user.UserService.handle_payment_succeeded") as mock_handle:
        mock_handle.side_effect = Exception(" processing boom ")
        
        payload = {
            "event_type": "payment_succeeded", # Triggers handle_payment_succeeded
            "event_id": "evt_crash",
        }
        
        response = client.post(
            "/api/v1/webhooks/paddle",
            json=payload,
            headers={"Paddle-Signature": "valid"}
        )
        
        assert response.status_code == 400
        
        log = db_session.query(WebhookEvent).filter_by(paddle_event_id="evt_crash").first()
        assert log is not None
        assert log.status == "failed"
        assert "processing boom" in log.error_message
