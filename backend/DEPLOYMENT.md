# Backend Deployment Guide

This guide covers deploying the PDF2Audiobook Core backend. As an open-source core, the primary deployment target is Docker (local or self-hosted).

## 🐳 Docker Deployment (Recommended)

The easiest way to run the application is using Docker Compose.

### 1. Prerequisites
- Docker & Docker Compose
- An S3-compatible storage bucket (MinIO, AWS S3, Cloudflare R2, etc.)

### 2. Configuration
1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` to configure your storage and desired TTS providers.

### 3. Run with Docker Compose
```bash
docker-compose up --build -d
```
This starts:
- **Backend**: http://localhost:8000
- **Worker**: Background processing
- **Frontend**: http://localhost:3000
- **Redis**: Local queue

### 4. Verify
Check the logs to ensure everything is running:
```bash
docker-compose logs -f
```

## 🛠️ Manual / Local Deployment

For development without Docker (except for Redis):

1.  **Start Redis**:
    ```bash
    docker run -d -p 6379:6379 redis:7-alpine
    ```

2.  **Start Services**:
    Use the provided script:
    ```bash
    ./start-local.sh
    ```

## ☁️ Cloud Deployment (Self-Hosted)

To deploy on a VPS or cloud provider (e.g. AWS EC2, DigitalOcean Droplet, Hetzner):

1.  Provision a server with Docker installed.
2.  Clone the repository.
3.  Configure `.env` with your production secrets (S3 keys, TTS API keys).
4.  Run `docker-compose -f docker-compose.yml up -d`.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Database connection string (defaults to local SQLite) | No |
| `REDIS_URL` | Redis connection string | No (if local) |
| `AWS_ACCESS_KEY_ID` | S3 Access Key | Yes |
| `AWS_SECRET_ACCESS_KEY` | S3 Secret Key | Yes |
| `S3_BUCKET_NAME` | S3 Bucket Name | Yes |
| `AWS_REGION` | S3 Region | Yes |
| `AWS_ENDPOINT_URL` | S3 Endpoint (for MinIO/R2) | Optional |
| `OPENAI_API_KEY` | For OpenAI TTS/LLM | Optional |
| `SECRET_KEY` | JWT signing key (change in prod) | Yes (in prod) |

## 🔒 Security Notes
- Change `SECRET_KEY` in production.
- Ensure your S3 bucket permissions are correct.
- If using `start-local.sh` in production, ensure you use a process manager like `supervisor` or `systemd`, though Docker is preferred.