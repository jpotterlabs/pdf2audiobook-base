#!/bin/bash
set -e

export PYTHONPATH="${PYTHONPATH}:backend"

echo "Starting PDF2AudioBook deployment..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "DATABASE_URL is set, proceeding with migrations..."
echo "Working directory: $(pwd)"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..."

# Check if we need to run migrations
echo "Checking if database tables already exist..."
table_exists=$(PGPASSWORD=$DB_PASSWORD psql "$DATABASE_URL" -t -c "SELECT to_regclass('users');" 2>/dev/null | xargs)

if [ "$table_exists" = "users" ]; then
    echo "Database tables already exist, skipping migrations..."
    echo "This is normal for subsequent deployments."
else
    echo "Running database migrations for first-time setup..."

    # Clean up any existing ENUM types that might have been created from failed migrations
    echo "Cleaning up any existing ENUM types from previous failed migrations..."
    psql "$DATABASE_URL" << 'EOF' 2>/dev/null || true
DROP TYPE IF EXISTS jobstatus CASCADE;
DROP TYPE IF EXISTS subscriptiontier CASCADE;
DROP TYPE IF EXISTS voiceprovider CASCADE;
DROP TYPE IF EXISTS conversionmode CASCADE;
DROP TYPE IF EXISTS producttype CASCADE;
DROP TYPE IF EXISTS subscriptionstatus CASCADE;
DROP TYPE IF EXISTS transactiontype CASCADE;
EOF
    echo "Cleanup completed"



    # Run migrations from the parent directory
    echo "Running: alembic upgrade head"
    alembic upgrade head

    if [ $? -eq 0 ]; then
        echo "Database migrations completed successfully"
    else
        echo "ERROR: Database migration failed"
        echo "This is a critical error - the application cannot start without database tables"
        exit 1
    fi


fi

# Start the application
echo "Starting FastAPI application..."
# Use 1 worker to fit within Render's 512MB memory limit
exec uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1
