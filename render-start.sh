#!/bin/bash
set -e

export PYTHONPATH="${PYTHONPATH}:backend"

echo "Starting PDF2AudioBook deployment..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

# Ensure we are in the project root (where alembic.ini is)
if [ -f "../alembic.ini" ]; then
    echo "Changing to project root directory..."
    cd ..
fi

echo "Current working directory: $(pwd)"
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Verify Alembic configuration exists
if [ ! -f "alembic.ini" ]; then
    echo "ERROR: alembic.ini not found in $(pwd)"
    exit 1
fi

echo "DATABASE_URL is set, proceeding with migrations..."
echo "DATABASE_URL: ${DATABASE_URL:0:20}..."

# Check if we need to run migrations
    # Rescue: Check if 'users' table exists but 'alembic_version' is empty/missing
    # This implies an un-tracked existing DB. We stamp it to the revision *before* the new one.
    # Revision 1e025f228445 was the stable state before 'estimated_cost'.
    
    users_exists=$(PGPASSWORD=$DB_PASSWORD psql "$DATABASE_URL" -t -c "SELECT to_regclass('users');" 2>/dev/null | xargs)
    version_count=$(PGPASSWORD=$DB_PASSWORD psql "$DATABASE_URL" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_name = 'alembic_version';" 2>/dev/null | xargs)
    
    if [ "$users_exists" = "users" ] && [ "$version_count" = "0" ]; then
        echo "⚠️  Database has tables but no migration history. Remedying..."
        echo "Stamping database to revision 1e025f228445 (Update models to match current schema)..."
        alembic stamp 1e025f228445
    fi

    # Run migrations
    echo "Running: alembic upgrade head"
    alembic upgrade head
    
    # Verify the created column specifically to be sure
    echo "Verifying schema update..."
    column_exists=$(PGPASSWORD=$DB_PASSWORD psql "$DATABASE_URL" -t -c "SELECT count(*) FROM information_schema.columns WHERE table_name='jobs' AND column_name='estimated_cost';" 2>/dev/null | xargs)
    if [ "$column_exists" = "0" ]; then
        echo "⚠️  WARNING: 'estimated_cost' column still missing after migration!"
    else
        echo "✅ 'estimated_cost' column confirmed present."
    fi

    if [ $? -eq 0 ]; then
        echo "Database migrations completed successfully"
    else
        echo "ERROR: Database migration failed"
        echo "This is a critical error - the application cannot start without database tables"
        exit 1
    fi

# Start the application
echo "Starting FastAPI application..."
# Use 1 worker to fit within Render's 512MB memory limit
exec uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1
