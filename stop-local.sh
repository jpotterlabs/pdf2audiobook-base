#!/bin/bash

echo "=== PDF2AudioBook Local Cleanup ==="

# Function to kill process by port
kill_port() {
    local port=$1
    local description=$2
    local pid=$(lsof -t -i:$port)

    if [ -n "$pid" ]; then
        echo "Killing $description on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    else
        echo "$description on port $port is not running."
    fi
}

# Function to kill process by name/pattern
kill_pattern() {
    local pattern=$1
    local description=$2
    # Find PIDs matching pattern, excluding grep itself and this script
    local pids=$(pgrep -f "$pattern")

    if [ -n "$pids" ]; then
        echo "Killing $description processes..."
        echo "$pids" | xargs kill -9 2>/dev/null
    else
        echo "No $description processes found."
    fi
}

# 1. Kill Backend (Port 8000)
kill_port 8000 "Backend (Uvicorn)"

# 2. Kill Frontend (Port 3000)
kill_port 3000 "Frontend (Next.js)"
# Also try finding next-server explicitly if port kill didn't catch everything
kill_pattern "next-server" "Next.js Server"
kill_port 3001 "Frontend (Next.js Alternate)"

# 3. Kill Celery Worker
kill_pattern "celery -A worker.celery_app" "Celery Worker"

# 4. Kill lingering Python processes started by uv related to this project
# Be careful not to kill other unrelated python processes
echo "Checking for lingering python processes in .venv..."
# Assuming we are in the project root or can find processes using this venv
pids=$(pgrep -f "pdf2audiobook-base/.venv/bin/python")
if [ -n "$pids" ]; then
   echo "Killing lingering venv python processes..."
   echo "$pids" | xargs kill -9 2>/dev/null
fi

echo "=== Cleanup Complete ==="
echo "You can check running processes with: ps aux | grep python"
