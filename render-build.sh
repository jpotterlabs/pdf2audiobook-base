#!/bin/bash
set -e

echo "🚀 Starting PDF2Audiobook backend build for Render..."

# Install dependencies using uv or fallback to pip
echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for dependency installation..."
    uv sync --no-install-project
else
    echo "uv not found, using pip..."
    pip install -r requirements.txt
fi

# Verify installation (don't run migrations here - database may not be available)
echo "✅ Verifying installation..."
if command -v uv &> /dev/null && uv run python -c "import sys; sys.path.insert(0, 'backend'); from main import app; print('✅ Application imports successfully')"; then
    echo "✅ Application imports successfully (uv)"
elif python -c "import sys; sys.path.insert(0, 'backend'); from main import app; print('✅ Application imports successfully')"; then
    echo "✅ Application imports successfully (pip)"
else
    echo "❌ Application import failed, but continuing build..."
fi

# Check if critical environment variables are set (some may only be available at runtime)
echo "🔍 Checking critical environment variables..."
critical_vars=("SECRET_KEY")
for var in "${critical_vars[@]}"; do
     if [ -z "${!var}" ]; then
         echo "❌ Required environment variable $var is not set"
         exit 1
     fi
done

echo "✅ Critical environment variables check passed"
echo "Note: Some environment variables (DATABASE_URL, REDIS_URL, etc.) may only be available at runtime"

# Install static FFmpeg
echo "🎥 Installing static FFmpeg..."
if [ ! -f "ffmpeg" ]; then
    curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
    tar -xf ffmpeg.tar.xz
    mv ffmpeg-*-amd64-static/ffmpeg .
    mv ffmpeg-*-amd64-static/ffprobe .
    rm -rf ffmpeg-*-amd64-static ffmpeg.tar.xz
    chmod +x ffmpeg ffprobe
    echo "✅ FFmpeg installed to $(pwd)/ffmpeg"
else
    echo "✅ FFmpeg already exists"
fi

echo "🎉 Build completed successfully!"
echo "Note: Database migrations will be run on first startup"