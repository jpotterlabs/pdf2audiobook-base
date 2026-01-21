import os
import redis
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env from project root
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

def check_redis():
    print(f"Connecting to Redis at: {redis_url}")
    try:
        r = redis.from_url(redis_url)
        # Check connection
        r.ping()
        print("✅ Connected to Redis successfully.")
        
        # Check queue length
        q_len = r.llen("celery")
        print(f"Queue 'celery' length: {q_len}")
        
        # Peek at first item if exists
        if q_len > 0:
            item = r.lindex("celery", 0)
            print(f"First item: {item}")
            
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")

if __name__ == "__main__":
    check_redis()
