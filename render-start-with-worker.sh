#!/bin/bash
set -e

echo "🚀 Starting PDF2AudioBook backend with integrated worker..."
echo "Working directory: $(pwd)"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src:/opt/render/project/src/backend"

# Add local ffmpeg to PATH
export PATH="$(pwd):$PATH"
echo "🎥 Checking ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg found: $(which ffmpeg)"
    ffmpeg -version | head -n 1
else
    echo "⚠️ ffmpeg not found in PATH"
fi

# Verify required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "❌ ERROR: REDIS_URL is not set"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY is not set"
    exit 1
fi

echo "✅ Environment variables verified"

# Check database connection and create tables if needed
echo "🔍 Checking database connection..."

MAX_RETRIES=5
RETRY_DELAY=5
DATABASE_STATUS="ERROR"

for i in $(seq 1 $MAX_RETRIES); do
    RAW_STATUS=$(python3 << 'EOF'
import sys
import os
import warnings
from sqlalchemy import create_engine, inspect, text

# Suppress warnings to keep stdout clean for status detection
warnings.filterwarnings("ignore")

# Add backend to path
sys.path.insert(0, '/opt/render/project/src/backend')
sys.path.insert(0, '/opt/render/project/src')

try:
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("STATUS:MISSING")
        sys.exit(0)
    
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url, connect_args={'connect_timeout': 5})
    
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'users' in tables:
        print("STATUS:READY")
    else:
        print("STATUS:MIGRATE")
except Exception as e:
    # Print error but include the error prefix for bash to catch
    print(f"STATUS:ERROR: {e}")
    sys.exit(1)
EOF
)
    # Extract status using grep/sed to be safe from extra library output
    DATABASE_STATUS=$(echo "$RAW_STATUS" | grep "STATUS:" | tail -n 1 | cut -d':' -f2-)
    
    if [[ "$DATABASE_STATUS" == "READY" || "$DATABASE_STATUS" == "MIGRATE" || "$DATABASE_STATUS" == "MISSING" ]]; then
        break
    fi
    
    echo "⚠️ Connection attempt $i failed ($DATABASE_STATUS). Retrying in ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
done

if [[ "$DATABASE_STATUS" == "MIGRATE" ]]; then
    echo "📦 First-time setup: Running database migrations..."
    export PYTHONPATH=$PYTHONPATH:/opt/render/project/src/backend:/opt/render/project/src
    alembic upgrade head
elif [[ "$DATABASE_STATUS" == "READY" ]]; then
    echo "✅ Database tables already exist"
elif [[ "$DATABASE_STATUS" == "MISSING" ]]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
elif [[ "$DATABASE_STATUS" == ERROR* ]]; then
    echo "❌ $DATABASE_STATUS"
    exit 1
fi

echo "✅ Database ready"

# Install supervisor if not present
if ! command -v supervisord &> /dev/null; then
    echo "📦 Installing supervisor..."
    pip install supervisor
fi

# Determine command prefix based on .venv existence
CMD_PREFIX=""
if [ -d "/opt/render/project/src/.venv" ]; then
    CMD_PREFIX="/opt/render/project/src/.venv/bin/"
    echo "✅ Found .venv, using prefix: $CMD_PREFIX"
else
    echo "⚠️ .venv not found, assuming binaries are in PATH"
fi

# Create supervisor configuration
echo "📝 Creating supervisor configuration..."

# Export PYTHONPATH so child processes inherit it
export PYTHONPATH="/opt/render/project/src:/opt/render/project/src/backend"

cat > /tmp/supervisord.conf << SUPERVISOR_EOF
[supervisord]
nodaemon=true
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid
loglevel=info

[program:backend]
command=${CMD_PREFIX}uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1
directory=/opt/render/project/src
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:worker]
command=${CMD_PREFIX}celery -A worker.celery_app worker --loglevel=info --concurrency=1
directory=/opt/render/project/src
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

SUPERVISOR_EOF

echo "✅ Supervisor configuration created"
echo ""
echo "🚀 Starting services with Supervisor..."
echo "   - Backend API (Uvicorn on port ${PORT:-10000})"
echo "   - Celery Worker (2 concurrent tasks)"
echo ""

# Start supervisor
exec supervisord -c /tmp/supervisord.conf
