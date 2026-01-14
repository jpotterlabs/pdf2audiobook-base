from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from loguru import logger
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_dir)

# Load environment variables from .env if it exists
try:
    from dotenv import load_dotenv
    # Look for .env in both root and backend
    load_dotenv(os.path.join(backend_dir, ".env"))
    load_dotenv(os.path.join(backend_dir, "..", ".env"))
    # Also support the temporary file the user created for testing
    load_dotenv(os.path.join(backend_dir, "copy.env.antigravity"))
except ImportError:
    pass

# Create Celery app
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker_url = os.getenv("CELERY_BROKER_URL", redis_url)
result_backend = os.getenv("CELERY_RESULT_BACKEND", redis_url)

def _redact_url(url: str) -> str:
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if parsed.password:
            # Reconstruct URL without password
            netloc = parsed.hostname
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            if parsed.username:
                netloc = f"{parsed.username}:***@{netloc}"
            else:
                netloc = f"***@{netloc}"
            return parsed._replace(netloc=netloc).geturl()
        return url
    except Exception:
        return "<redacted>"

logger.info(f"Connecting to Celery Broker: {_redact_url(broker_url)}")
logger.info(f"Using Result Backend: {_redact_url(result_backend)}")

celery_app = Celery(
    "pdf2audiobook_worker",
    broker=broker_url,
    backend=result_backend,
    include=["worker.tasks"],
)

from celery.schedules import crontab

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic Task Schedule (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-old-files": {
        "task": "worker.tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM UTC
    },
}


# Optional: Set up logging
@task_prerun.connect
def task_prerun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds
):
    logger.info(f"Task {task_id} ({task.name}) started")


@task_postrun.connect
def task_postrun_handler(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    state=None,
    **kwds,
):
    logger.info(f"Task {task_id} ({task.name}) finished with state: {state}")


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
):
    logger.error(f"Task {task_id} failed: {exception}")


if __name__ == "__main__":
    celery_app.start()
