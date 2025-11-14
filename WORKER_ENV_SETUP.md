# Worker Environment Variables Setup

## Problem

The Celery worker is failing with the error:
```
ModuleNotFoundError: No module named '${REDIS_URL}'
```

This indicates that the worker service doesn't have the required environment variables set, or they're not being expanded properly.

## Required Environment Variables

The worker service needs the following environment variables to function:

### Critical (Required for Basic Operation)

1. **CELERY_BROKER_URL** or **REDIS_URL**
   - Format: `redis://hostname:port/db`
   - Example: `redis://red-abc123.oregon.render.com:6379/0`
   - This is the Redis connection URL that Celery uses as a message broker

2. **CELERY_RESULT_BACKEND** (optional, defaults to broker URL)
   - Format: Same as CELERY_BROKER_URL
   - This is where Celery stores task results

3. **DATABASE_URL**
   - Format: `postgresql://user:password@host:port/database`
   - Required for tasks that access the database

### AWS S3 (Required for File Storage)

4. **AWS_ACCESS_KEY_ID**
5. **AWS_SECRET_ACCESS_KEY**
6. **AWS_REGION**
   - Example: `us-west-2`
7. **AWS_S3_BUCKET**
   - Example: `pdf2audiobook-files`

### OpenAI (Required for TTS Processing)

8. **OPENAI_API_KEY**
   - Format: `sk-...`

### Optional Service Providers

9. **ELEVENLABS_API_KEY** (if using ElevenLabs TTS)
10. **GOOGLE_APPLICATION_CREDENTIALS** (if using Google Cloud TTS)
11. **AZURE_SPEECH_KEY** (if using Azure TTS)
12. **AZURE_SPEECH_REGION** (if using Azure TTS)

## How to Set Environment Variables on Render

### Option 1: Via Render Dashboard (Recommended)

1. Go to https://dashboard.render.com/worker/srv-d4ba08juibrs739obsfg
2. Click on "Environment" in the left sidebar
3. Add each environment variable:
   - Click "Add Environment Variable"
   - Enter the key (e.g., `REDIS_URL`)
   - Enter the value (the actual Redis URL)
   - Click "Save Changes"

### Option 2: Link from Another Service

If you've already set these variables on your backend service, you can link them:

1. Go to the worker service dashboard
2. Click "Environment"
3. For each variable, click "Add Environment Variable"
4. Select "Link from existing service"
5. Choose the backend service
6. Select the variable to link
7. Save changes

### Option 3: Using Environment Groups

For variables shared across multiple services:

1. Go to your Render dashboard
2. Click on "Environment Groups" 
3. Create a new group or use existing
4. Add all shared variables to the group
5. Connect both backend and worker services to this group

## Minimal Configuration to Start

To get the worker running immediately, you need at minimum:

```bash
CELERY_BROKER_URL=redis://your-redis-host:6379/0
DATABASE_URL=postgresql://user:pass@host:5432/dbname
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-west-2
AWS_S3_BUCKET=your-bucket-name
OPENAI_API_KEY=sk-your-key
```

## Verification

After setting the environment variables:

1. The worker will automatically redeploy
2. Check the logs for:
   ```
   [2025-XX-XX HH:MM:SS,XXX: INFO/MainProcess] Connected to redis://...
   [2025-XX-XX HH:MM:SS,XXX: INFO/MainProcess] celery@hostname ready.
   ```

3. The worker should NOT show:
   - `ModuleNotFoundError: No module named '${REDIS_URL}'`
   - Connection errors to Redis or PostgreSQL

## Common Issues

### Issue: Variables not expanding

**Symptom**: `No module named '${REDIS_URL}'`

**Solution**: Make sure you're setting the actual value, not the placeholder string `${REDIS_URL}`. The value should look like:
```
redis://red-xyz123.render.com:6379/0
```

### Issue: Redis connection refused

**Symptom**: `Error 111 connecting to localhost:6379. Connection refused.`

**Solution**: 
- Verify CELERY_BROKER_URL or REDIS_URL is set
- Check that the Redis instance is running
- Verify the Redis instance is in the same environment/region

### Issue: Database connection errors

**Symptom**: `could not connect to server: Connection refused`

**Solution**:
- Verify DATABASE_URL is set correctly
- Ensure the database and worker are in the same private network
- Check database credentials

## Testing After Setup

Once environment variables are configured:

1. Watch the worker logs for successful startup:
   ```bash
   # Should see these messages
   Connected to redis://...
   celery@srv-xxxxx ready.
   ```

2. From the backend, trigger a test task:
   ```python
   from worker.tasks import process_pdf_to_audio
   
   job_id = "test-123"
   result = process_pdf_to_audio.delay(job_id)
   ```

3. Check worker logs for task execution:
   ```
   [INFO/MainProcess] Task worker.tasks.process_pdf_to_audio[...] received
   [INFO/ForkPoolWorker-1] Task worker.tasks.process_pdf_to_audio[...] succeeded
   ```

## Next Steps

After the worker is running:

1. ✅ Verify all environment variables are set
2. ✅ Test PDF upload from frontend
3. ✅ Monitor worker logs during processing
4. ✅ Verify audio files appear in S3
5. ✅ Check job status updates in database

## Related Files

- `worker/celery_app.py` - Celery configuration
- `worker/tasks.py` - Task definitions
- `backend/app/core/config.py` - Environment variable definitions