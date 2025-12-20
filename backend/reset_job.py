from app.core.database import SessionLocal
from app.models import Job, JobStatus

db = SessionLocal()
job = db.query(Job).filter(Job.id == 1, Job.status == JobStatus.FAILED).first()
if job:
    print(f"Resetting FAILED Job {job.id} to PENDING")
    job.status = JobStatus.PENDING
    job.retry_count = 0
    job.error_message = None
    db.commit()
    
    # Re-queue the task
    from app.worker.tasks import process_pdf_task
    print(f"Re-queuing Job {job.id} to Celery...")
    process_pdf_task.delay(job.id)
    print("Success")
else:
    print("Job 1 not found or not in FAILED state. Skipping reset.")
db.close()
