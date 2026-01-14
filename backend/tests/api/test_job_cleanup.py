from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Job, User, JobStatus
from datetime import datetime

# Helper to get the test user created by conftest override
def get_test_user(db: Session):
    user = db.query(User).first()
    if not user:
        user = User(id=1, email="dev@example.com")
        db.add(user)
        db.commit()
    return user

def test_delete_job(client: TestClient, db_session: Session):
    user = get_test_user(db_session)
    
    # Create a job
    job = Job(
        user_id=user.id,
        original_filename="test_delete.pdf",
        pdf_s3_key="pdfs/test_delete.pdf",
        status=JobStatus.completed,
        created_at=datetime.now()
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Delete it
    response = client.delete(f"/api/v1/jobs/{job.id}")
    assert response.status_code == 204

    # Verify deleted
    deleted_job = db_session.query(Job).filter(Job.id == job.id).first()
    assert deleted_job is None

def test_cleanup_failed_jobs(client: TestClient, db_session: Session):
    user = get_test_user(db_session)
    
    # Create failed jobs
    job1 = Job(
        user_id=user.id,
        original_filename="failed1.pdf",
        pdf_s3_key="pdf/failed1.pdf",
        status=JobStatus.failed,
        created_at=datetime.now()
    )
    job2 = Job(
        user_id=user.id,
        original_filename="failed2.pdf",
        pdf_s3_key="pdf/failed2.pdf",
        status=JobStatus.cancelled,
        created_at=datetime.now()
    )
    job3 = Job(
        user_id=user.id,
        original_filename="success.pdf",
        pdf_s3_key="pdf/success.pdf",
        status=JobStatus.completed,
        created_at=datetime.now()
    )
    db_session.add_all([job1, job2, job3])
    db_session.commit()

    # Cleanup
    response = client.delete("/api/v1/jobs/cleanup")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 2

    # Verify
    assert db_session.query(Job).filter(Job.id == job1.id).first() is None
    assert db_session.query(Job).filter(Job.id == job2.id).first() is None
    assert db_session.query(Job).filter(Job.id == job3.id).first() is not None
