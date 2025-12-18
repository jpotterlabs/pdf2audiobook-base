#!/bin/bash
set -e

echo "🚀 Starting PDF2AudioBook backend with integrated worker..."
echo "Working directory: $(pwd)"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src:/opt/render/project/src/backend"

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
python3 << 'EOF'
import sys
import os

# Add backend to path
sys.path.insert(0, '/opt/render/project/src/backend')
sys.path.insert(0, '/opt/render/project/src')

from app.core.database import engine
from app.models import Base
from sqlalchemy import inspect, text

try:
    # Test connection
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database connection successful')

    # Check if tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'users' in tables:
        print(f"✅ Database tables already exist ({len(tables)} tables)")
    else:
        print("📦 Creating database tables...")
        Base.metadata.create_all(bind=engine)

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Created {len(tables)} tables successfully")

except Exception as e:
    print(f"❌ Error setting up database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed"
    exit 1
fi

echo "✅ Database ready"

# Install supervisor if not present
if ! command -v supervisord &> /dev/null; then
    echo "📦 Installing supervisor..."
    pip install supervisor
fi

# Create supervisor configuration
echo "📝 Creating supervisor configuration..."
cat > /tmp/supervisord.conf << 'SUPERVISOR_EOF'
[supervisord]
nodaemon=true
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid
loglevel=info

[program:backend]
command=uvicorn backend.main:app --host 0.0.0.0 --port %(ENV_PORT)s --workers 1
directory=/opt/render/project/src
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PYTHONPATH="/opt/render/project/src:/opt/render/project/src/backend"

[program:worker]
command=celery -A worker.celery_app worker --loglevel=info --concurrency=1
directory=/opt/render/project/src
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PYTHONPATH="/opt/render/project/src:/opt/render/project/src/backend"

SUPERVISOR_EOF

echo "✅ Supervisor configuration created"
echo ""
echo "🚀 Starting services with Supervisor..."
echo "   - Backend API (Uvicorn on port ${PORT:-10000})"
echo "   - Celery Worker (2 concurrent tasks)"
echo ""

# Start supervisor
exec supervisord -c /tmp/supervisord.conf
