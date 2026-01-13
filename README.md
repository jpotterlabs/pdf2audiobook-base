# PDF2AudioBook Core

An open-source, self-hosted platform for converting PDF documents to high-quality audiobooks. "Core" is the base version of PDF2AudioBook, designed for individual use and community extensibility.

## 🚀 Key Features

- **Local & Private**: Data stays under your control. Supports local TTS engines (like Kokoro) for offline privacy.
- **Advanced PDF Processing**: Robust text extraction with OCR Fallback.
- **Smart Summarization**: Use any LLM (via OpenRouter) to generate executive summaries and concept explanations before listening.
- **Multiple TTS Engines**:
  - **Local**: Run [Kokoro-FastAPI](https://github.com/remsky/kokoro-fastapi) or any OpenAI-compatible TTS locally.
  - **remote**: Google Cloud TTS, OpenAI, AWS Polly, Azure, ElevenLabs.
- **Cost Tracking**: Estimate LLM and Cloud TTS costs (or $0.00 for local engines).

## 🏗️ Architecture

- **Frontend**: Next.js 14 (React) - Modern, responsive UI.
- **Backend**: FastAPI (Python) - High-performance API.
- **Processing**: Celery + Redis - Robust asynchronous job queue.
- **Storage**: S3-Compatible (MinIO, R2, AWS S3).

## 🛠️ Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- An S3-compatible storage bucket (or Localstack/MinIO)
- (Optional) An OpenRouter API Key for summaries
- (Optional) A local running TTS instance (e.g., Kokoro)

### 2. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` to configure your storage and desired TTS providers.

### 3. Run with Docker
```bash
docker-compose up --build
```

Access the application:
- **UI**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🐳 Local TTS Setup (Recommended)
To use high-quality neural TTS for free/offline:

1. Run a local Kokoro instance (or similar OpenAI-compatible server) on port 8880.
2. In your `.env`:
   ```bash
   OPENAI_BASE_URL=http://localhost:8880/v1
   OPENAI_TTS_MODEL=kokoro
   OPENAI_API_KEY=not-needed
   ```
3. Use the **OpenAI** provider in the UI. The "Voices" (Alloy, Echo, etc.) will map to your local model voices.

## 🤝 Contributing
Contributions are welcome! This is the "Core" edition, serving as the foundation for the community.

1. Fork the repo.
2. Create a feature branch.
3. Submit a Pull Request.

## 📄 License
MIT License.