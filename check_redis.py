import os
import redis

redis_url = "redis://192.168.0.225:6379/0"
try:
    r = redis.from_url(redis_url)
    # Check connection
    r.ping()
    print("Connected to Redis successfully.")
    
    # Check queue length
    q_len = r.llen("celery")
    print(f"Queue 'celery' length: {q_len}")
    
    # Peek at first item if exists
    if q_len > 0:
        item = r.lindex("celery", 0)
        print(f"First item: {item}")
        
except Exception as e:
    print(f"Error connecting to Redis: {e}")
