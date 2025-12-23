
import pytest
from app.services.job import JobService
from app.models import User, Job, JobStatus, Product, ConversionMode
from decimal import Decimal

def test_deduct_credits_balance_priority(db_session):
    # Setup user with both balance and legacy credits
    user = User(
        email="test@example.com",
        auth_provider_id="test_123",
        credit_balance=10.0,
        one_time_credits=5
    )
    db_session.add(user)
    db_session.commit()
    
    service = JobService(db_session)
    
    # 1. Deduct small amount (should come from balance)
    success = service.deduct_credits(user.id, 2.0)
    db_session.refresh(user)
    
    assert success is True
    assert user.credit_balance == 8.0 # 10 - 2
    assert user.one_time_credits == 5 # Unchanged

def test_deduct_credits_legacy_fallback(db_session):
    # Setup user with NO balance but legacy credits
    user = User(
        email="legacy@example.com",
        auth_provider_id="legacy_123",
        credit_balance=0.0,
        one_time_credits=5
    )
    db_session.add(user)
    db_session.commit()
    
    service = JobService(db_session)
    
    # 2. Deduct amount (balance 0 -> fallback to legacy token)
    # The new logic: if balance < amount, check legacy > 0
    # Note: Using fallback consumes 1 legacy credit regardless of cost in the old system?
    # Let's verify the implementation. 
    # Logic in service: failure if balance < amount, then check legacy. 
    # If legacy > 0, decrement 1 and return True.
    
    success = service.deduct_credits(user.id, 5.0) # Cost 5.0
    db_session.refresh(user)
    
    assert success is True
    assert user.credit_balance == 0.0
    assert user.one_time_credits == 4 # Decremented

def test_deduct_credits_insufficient(db_session):
    user = User(
        email="poor@example.com",
        auth_provider_id="poor_123",
        credit_balance=1.0, 
        one_time_credits=0
    )
    db_session.add(user)
    db_session.commit()
    
    service = JobService(db_session)
    success = service.deduct_credits(user.id, 5.0)
    
    assert success is False
    assert user.credit_balance == 1.0 # Unchanged

def test_update_job_status_usage_stats(db_session):
    user = User(email="jobtest@example.com", auth_provider_id="job_123")
    db_session.add(user)
    db_session.commit()
    
    job = Job(
        user_id=user.id,
        # filename="test.pdf", # Invalid field
        original_filename="test.pdf",
        status=JobStatus.pending,
        pdf_s3_key="test_key"
    )
    db_session.add(job)
    db_session.commit()
    
    service = JobService(db_session)
    
    # Update with usage stats
    service.update_job_status(
        job.id, 
        JobStatus.completed, 
        100, 
        chars_processed=5000,
        tokens_used=150
    )
    
    db_session.refresh(job)
    assert job.status == JobStatus.completed
    assert job.chars_processed == 5000
    assert job.tokens_used == 150
