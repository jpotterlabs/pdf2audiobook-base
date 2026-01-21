#!/bin/bash

# start-local.sh
# Starts the PDF2AudioBook application locally.

set -e

# --- Colors ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== PDF2AudioBook Local Startup ===${NC}"

# --- Checks ---
# Check for .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env created.${NC}"
else
    echo -e "${GREEN}Found .env${NC}"
fi

# Ensure .env has local settings
# (Optional: specialized checks)

# Start Redis
echo -e "${BLUE}--- Checking Redis ---${NC}"
if ! (redis-cli ping > /dev/null 2>&1); then
    echo -e "${YELLOW}Redis is not running.${NC}"
    if command -v docker >/dev/null 2>&1; then
        echo -e "${YELLOW}Starting Redis via Docker...${NC}"
        docker run -d -p 6379:6379 --name pdf2audiobook-redis redis:7-alpine || docker start pdf2audiobook-redis
        echo -e "${GREEN}Redis started via Docker.${NC}"
    else
        echo -e "${RED}Redis is required but not running, and Docker is not available.${NC}"
        echo "Please install and start Redis locally."
        exit 1
    fi
else
    echo -e "${GREEN}Redis is running.${NC}"
fi

# Python Setup
echo -e "${BLUE}--- Checking Backend Environment ---${NC}"

RUN_CMD="python"
PIP_CMD="pip"

if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}Found 'uv'. Using uv for dependency management.${NC}"
    # uv might not need venv activation if using 'uv run' but for simplicity let's stick to venv or install
    # uv sync creates/updates .venv
    uv sync
    RUN_CMD="uv run python"
    # Or just use source .venv/bin/activate if generated
else
    echo -e "${YELLOW}'uv' not found. Using standard python venv.${NC}"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo -e "${GREEN}Created .venv${NC}"
    fi
    source .venv/bin/activate
    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -e .
    RUN_CMD="python"
fi

# Migrations
echo -e "${BLUE}--- Running Database Migrations ---${NC}"
# Use run-migrations.sh or direct command
# We need to set DATABASE_URL if not set, but .env should have it.
# source .env to be sure? python-dotenv handles it in app, but alembic?
# alembic.ini uses sqlalchemy.url from .env mostly if configured to do so or env vars.
# Let's try running the migration using the python env
# export vars from .env for shell
set -a
source .env
set +a
$RUN_CMD -m alembic upgrade head

# --- Start Processes ---
echo -e "${BLUE}--- Starting Services ---${NC}"

pids=()
cleanup() {
    echo -e "${RED}Stopping all processes...${NC}"
    for pid in "${pids[@]}"; do
        kill "$pid" 2>/dev/null
    done
    wait
    echo -e "${GREEN}Shutdown complete.${NC}"
}
trap cleanup EXIT INT TERM

# 1. Backend
echo -e "${GREEN}Starting Backend (Port 8000)...${NC}"
# Run from backend directory to match structure
# We use $RUN_CMD which is either "python" (with venv activated) or "uv run python"
(cd backend && export PYTHONPATH=$PYTHONPATH:$(pwd) && $RUN_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000) > backend.log 2>&1 &
pids+=($!)

# 2. Worker
echo -e "${GREEN}Starting Worker...${NC}"
# Run from worker directory
(cd worker && $RUN_CMD -m celery -A celery_app worker --loglevel=info) > worker.log 2>&1 &
pids+=($!)


# 3. Frontend
echo -e "${GREEN}Starting Frontend (Port 3000)...${NC}"
(
    cd apps/reference-ui
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing Frontend Dependencies...${NC}"
        npm install
    fi
    npm run dev
) &
pids+=($!)

# Wait for background processes
wait
