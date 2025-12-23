from celery import Celery
from .celery_app import celery_app
import os
import sys
import tempfile
from typing import Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import SessionLocal, engine
from app.models import Job, JobStatus
from app.services.storage import StorageService
from app.services.job import JobService
from app.core.config import settings

# Import PDF processing pipeline

from .pdf_pipeline import PDFToAudioPipeline

pipeline = PDFToAudioPipeline()


from loguru import logger

# Diagnostic: Print voice env vars at startup
logger.info("⚙️ Loading Google TTS Voice Configuration from Environment:")
voice_vars = [
    "GOOGLE_VOICE_US_FEMALE_STD", "GOOGLE_VOICE_US_MALE_STD",
    "GOOGLE_VOICE_GB_FEMALE_STD", "GOOGLE_VOICE_GB_MALE_STD",
    "GOOGLE_VOICE_US_FEMALE_PREMIUM", "GOOGLE_VOICE_US_MALE_PREMIUM",
    "GOOGLE_VOICE_GB_FEMALE_PREMIUM", "GOOGLE_VOICE_GB_MALE_PREMIUM"
]
for var in voice_vars:
    val = getattr(settings, var, "NOT SET")
    logger.info(f"  {var} = '{val}'")


@celery_app.task(bind=True)
def process_pdf_task(self, job_id: int):
    """
    Process a PDF file and convert it to audio
    """
    db = SessionLocal()
    storage_service = StorageService()
    job_service = JobService(db)
    pdf_path = None
    temp_dir = None

    try:
        logger.info(f"Starting PDF processing for job {job_id}")
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job_service.update_job_status(job_id, JobStatus.processing, 0)

        # Create a temporary directory for this specific job
        temp_dir = tempfile.TemporaryDirectory()
        work_dir = temp_dir.name

        pdf_data = storage_service.download_file(job.pdf_s3_key)
        
        pdf_path = os.path.join(work_dir, "input.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_data)

        # process_pdf now returns (file_path, cost, usage_stats) and uses work_dir
        audio_file_path, tts_cost, usage_stats = pipeline.process_pdf(
            pdf_path=pdf_path,
            voice_provider=job.voice_provider,
            voice_type=job.voice_type,
            reading_speed=float(job.reading_speed),
            include_summary=job.include_summary,
            conversion_mode=job.conversion_mode,
            progress_callback=lambda progress: job_service.update_job_status(
                job_id, JobStatus.processing, progress
            ),
            work_dir=work_dir
        )

        # Calculate final cost (TTS + LLM)
        # TTS cost is already in tts_cost
        # LLM cost: estimate $2.00 per 1M tokens (avg for GPT-3.5/Flash-like models)
        token_cost = (usage_stats["tokens"] / 1_000_000) * 2.0
        final_cost = float(tts_cost) + token_cost
        
        job.audio_s3_key = audio_key
        job.audio_s3_url = audio_url
        
        # Deduct credits using service logic (AFTER successful upload)
        job_service.deduct_credits(job.user_id, final_cost)
        
        job_service.update_job_status(
            job_id, 
            JobStatus.completed, 
            100, 
            estimated_cost=final_cost,
            chars_processed=usage_stats.get("chars", 0),
            tokens_used=usage_stats.get("tokens", 0)
        )

        logger.info(f"Successfully processed job {job_id}")
        return {"status": "completed", "job_id": job_id, "audio_url": audio_url}

    except ValueError as e:
        logger.warning(f"User error processing job {job_id}: {e}")
        job_service.update_job_status(job_id, JobStatus.failed, error_message=str(e))
        # Do not retry for user errors

    except Exception as e:
        logger.error(f"System error processing job {job_id}: {e}", exc_info=True)
        job_service.update_job_status(
            job_id, JobStatus.failed, error_message=f"An unexpected error occurred: {str(e)}"
        )
        # Retry for system errors
        raise self.retry(exc=e, countdown=60, max_retries=3)

    finally:
        # cleanup happens automatically when temp_dir object is garbage collected or explicitly cleaned
        # but explicit cleanup is good practice
        if temp_dir:
            try:
                temp_dir.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")
        
        db.close()


from loguru import logger

# ... (imports)


@celery_app.task
def cleanup_old_files():
    """
    Clean up old temporary files and completed jobs older than 30 days
    """
    db = SessionLocal()
    logger.info("Starting cleanup of old files and jobs.")

    try:
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=30)

        old_jobs = (
            db.query(Job)
            .filter(Job.status == JobStatus.completed, Job.completed_at < cutoff_date)
            .all()
        )

        if not old_jobs:
            logger.info("No old jobs to clean up.")
            return "No old jobs to clean up."

        storage_service = StorageService()

        for job in old_jobs:
            logger.info(f"Deleting files for job {job.id}")
            if job.pdf_s3_key:
                storage_service.delete_file(job.pdf_s3_key)
            if job.audio_s3_key:
                storage_service.delete_file(job.audio_s3_key)

            db.delete(job)

        db.commit()
        logger.info(f"Cleaned up {len(old_jobs)} old jobs.")
        return f"Cleaned up {len(old_jobs)} old jobs"

    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup of old files: {e}", exc_info=True)
        raise e

    finally:
        db.close()
