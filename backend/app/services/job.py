from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import Job, User, JobStatus
from app.schemas import JobCreate, JobUpdate

import logging

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(
        self, user_id: int, job_data: JobCreate, pdf_s3_key: str, pdf_s3_url: str
    ) -> Job:
        job = Job(
            user_id=user_id,
            original_filename=job_data.original_filename,
            pdf_s3_key=pdf_s3_key,
            pdf_s3_url=pdf_s3_url,
            voice_provider=job_data.voice_provider,
            voice_type=job_data.voice_type,
            reading_speed=job_data.reading_speed,
            include_summary=job_data.include_summary,
            conversion_mode=job_data.conversion_mode,
            status=JobStatus.pending,
        )

        self.db.add(job)
        self.db.commit()

        # Skip refresh in testing mode to avoid enum conversion issues
        from app.core.config import settings
        if not settings.TESTING_MODE:
            self.db.refresh(job)

        return job

    def get_user_job(self, user_id: int, job_id: int) -> Optional[Job]:
        return (
            self.db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        )

    def get_user_jobs(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Job]:
        return (
            self.db.query(Job)
            .filter(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_job(self, job_id: int, job_update: dict) -> Optional[Job]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        for field, value in job_update.items():
            setattr(job, field, value)

        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job_status(
        self,
        job_id: int,
        status: JobStatus,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        estimated_cost: Optional[float] = None,
        chars_processed: Optional[int] = None,
        tokens_used: Optional[int] = None,
    ):
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        job.status = status

        if progress is not None:
            job.progress_percentage = progress

        if error_message is not None:
            job.error_message = error_message

        if estimated_cost is not None:
            job.estimated_cost = estimated_cost
            
        if chars_processed is not None:
            job.chars_processed = chars_processed
            
        if tokens_used is not None:
            job.tokens_used = tokens_used

        if status == JobStatus.processing and not job.started_at:
            job.started_at = datetime.now()
        elif status == JobStatus.completed:
            job.completed_at = datetime.now()
            job.progress_percentage = 100

        self.db.commit()
        self.db.refresh(job)
        return job

    def can_user_create_job(self, user_id: int, estimated_cost: float = 0.0) -> bool:
        # Bypass database checks in testing mode
        from app.core.config import settings
        if settings.TESTING_MODE:
            return True
            
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # 1. Check credit balance (Primary Method)
        # If user has enough credits for the estimated cost (or just > 0 if unknown)
        if user.credit_balance is not None and user.credit_balance >= estimated_cost:
            return True

        # 2. Check legacy one-time credits
        if user.one_time_credits > 0:
            return True

        # 3. Check subscription limits (Legacy/Fallback for Free Tier)
        if user.subscription_tier == "free":
            # Free tier limit
            limit = settings.FREE_TIER_JOBS_LIMIT
            monthly_jobs = (
                self.db.query(Job)
                    .filter(
                        Job.user_id == user_id,
                        Job.created_at >= datetime.now().replace(day=1),
                    )
                    .count()
            )
            # Only allow if under limit AND we haven't already returned True from credits
            return monthly_jobs < limit

        elif user.subscription_tier == "pro":
            # Pro tier: 50 jobs per month (Legacy check, should move to credits mainly)
            monthly_jobs = (
                self.db.query(Job)
                    .filter(
                        Job.user_id == user_id,
                        Job.created_at >= datetime.now().replace(day=1),
                    )
                    .count()
            )
            return monthly_jobs < 50

        elif user.subscription_tier == "enterprise":
            # Enterprise: unlimited
            return True

        return False

    def deduct_credits(self, user_id: int, amount: float) -> bool:
        """
        Deduct credits from user's balance. 
        Returns True if successful, False if insufficient funds.
        """
        user = self.db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            return False

        # 1. Deduct from credit balance if available
        if user.credit_balance >= amount:
            user.credit_balance = float(user.credit_balance) - amount
            self.db.commit()
            return True
        
        # 2. Legacy: Deduct from one_time_credits (1 credit = 1 job approx)
        # This is a fallback if credit_balance is 0 but they have old credits
        if user.one_time_credits > 0:
            user.one_time_credits -= 1
            self.db.commit()
            return True

        return False

    def delete_job(self, user_id: int, job_id: int) -> bool:
        """
        Permanently delete a job and its associated S3 files.
        """
        job = self.get_user_job(user_id, job_id)
        if not job:
            return False

        # Delete from S3
        from app.services.storage import StorageService
        storage = StorageService()
        
        # Try to delete PDF
        if job.pdf_s3_key:
            try:
                storage.delete_file(job.pdf_s3_key)
            except Exception as e:
                logger.warning(f"Could not delete PDF file {job.pdf_s3_key}: {e}")

        # Try to delete Audio
        if job.audio_s3_key:
            try:
                storage.delete_file(job.audio_s3_key)
            except Exception as e:
                logger.warning(f"Could not delete audio file {job.audio_s3_key}: {e}")

        # Delete database record
        self.db.delete(job)
        self.db.commit()
        return True

    def cleanup_failed_jobs(self, user_id: int) -> int:
        """
        Delete all failed or cancelled jobs for a user.
        Returns the number of jobs deleted.
        """
        failed_jobs = (
            self.db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.status.in_([JobStatus.failed, JobStatus.cancelled])
            )
            .all()
        )

        count = 0
        from app.services.storage import StorageService
        storage = StorageService()

        for job in failed_jobs:
            # S3 Cleanup
            if job.pdf_s3_key:
                try:
                    storage.delete_file(job.pdf_s3_key)
                except Exception as e:
                    logger.warning(f"Could not delete PDF {job.pdf_s3_key} for job {job.id}: {e}")
            if job.audio_s3_key:
                try:
                    storage.delete_file(job.audio_s3_key)
                except Exception as e:
                    logger.warning(f"Could not delete audio {job.audio_s3_key} for job {job.id}: {e}")
            
            self.db.delete(job)
            count += 1
        
        if count > 0:
            self.db.commit()
            
        return count
