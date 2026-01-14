import os
import sys

# Setup path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "backend"))

# Load env variables explicitly because we are running disjointed
from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

from worker.celery_app import celery_app
from worker.tasks import process_pdf_task

print("Sending test task...")
try:
    # Send a task for the existing job #7
    result = process_pdf_task.delay(7)
    print(f"Task sent! ID: {result.id}")
except Exception as e:
    print(f"Failed to send task: {e}")
