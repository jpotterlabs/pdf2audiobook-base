# Environment Variables Reference Guide

This document provides a comprehensive list of all environment variables used across the PDF2Audiobook platform (Backend, Production UI, and Reference UI).

---

## 🌎 Global Mode Control

### `ENVIRONMENT` / `NEXT_PUBLIC_ENVIRONMENT`
- **Description**: The master switch for the application's operating mode.
- **Values**: `development` (or `sandbox`), `staging`, `production`.
- **Impact**: 
    - Auto-selects between `PROD_` and `SANDBOX_` prefixed variables.
    - Toggles between Paddle Sandbox and Live environments.
    - Controls frontend API endpoints and Clerk keys.

---

## 🔑 Authentication (Clerk)

The system supports dual-identity configurations to prevent accidental cross-talk between sandbox and production users.

| Backend Variable | Description |
| :--- | :--- |
| `PROD_CLERK_PEM_PUBLIC_KEY` | Public key for production JWT verification. |
| `PROD_CLERK_JWT_ISSUER` | JWT issuer for production (e.g., `https://clerk.pdf2audiobook.com`). |
| `PROD_CLERK_JWT_AUDIENCE` | JWT audience for production. |
| `SANDBOX_CLERK_PEM_PUBLIC_KEY` | Public key for sandbox/dev JWT verification. |
| `SANDBOX_CLERK_JWT_ISSUER` | JWT issuer for sandbox. |
| `SANDBOX_CLERK_JWT_AUDIENCE` | JWT audience for sandbox. |

| Frontend Variable | Description |
| :--- | :--- |
| `NEXT_PUBLIC_PROD_CLERK_PUBLISHABLE_KEY` | Public key for production frontend. |
| `NEXT_PUBLIC_SANDBOX_CLERK_PUBLISHABLE_KEY` | Public key for local/sandbox development. |

---

## 💳 Payments & Billing (Paddle)

| Backend Variable | Description |
| :--- | :--- |
| `PROD_PADDLE_API_KEY` | Live API key from Paddle dashboard. |
| `PROD_PADDLE_VENDOR_ID` | Live Vendor ID. |
| `PROD_PADDLE_WEBHOOK_SECRET_KEY` | Live Webhook secret for signature verification. |
| `SANDBOX_PADDLE_API_KEY` | Sandbox API key from Paddle. |
| `SANDBOX_PADDLE_VENDOR_ID` | Sandbox Vendor ID. |
| `SANDBOX_PADDLE_WEBHOOK_SECRET_KEY` | Sandbox Webhook secret. |
| `PADDLE_ENVIRONMENT` | Overridden by `ENVIRONMENT`. Explicitly `sandbox` or `production`. |

---

## 🤖 AI & Processing (OpenRouter / OpenAI)

| Variable | Description |
| :--- | :--- |
| `OPENROUTER_API_KEY` | Required. Powers LLM features (summaries, explanations). |
| `LLM_MODEL` | Default: `google/gemini-2.0-flash-001:free`. Specify model string. |
| `OPENAI_API_KEY` | Optional. Used if direct OpenAI access is preferred over OpenRouter. |

---

## 🗣️ Voice & TTS (Google Cloud)

| Variable | Description |
| :--- | :--- |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your Google Cloud Service Account JSON file. |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | **Preferred for Render/Cloud.** Paste the entire JSON blob here to auto-initialize. |
| `GOOGLE_VOICE_US_FEMALE_STD` | Default: `en-US-Wavenet-C`. |
| `GOOGLE_VOICE_US_MALE_STD` | Default: `en-US-Wavenet-I`. |
| `GOOGLE_VOICE_GB_FEMALE_STD` | Default: `en-GB-Wavenet-F`. |
| `GOOGLE_VOICE_GB_MALE_STD` | Default: `en-GB-Wavenet-O`. |

---

## 📦 Infrastructure & Storage

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string (e.g., `postgresql://user:pass@host:port/db`). |
| `REDIS_URL` | Redis connection for Celery and caching. |
| `AWS_ACCESS_KEY_ID` | S3-compatible access key. |
| `AWS_SECRET_ACCESS_KEY` | S3-compatible secret key. |
| `AWS_ENDPOINT_URL` | e.g., `https://<account_id>.r2.cloudflarestorage.com`. |
| `S3_BUCKET_NAME` | The bucket name for assets. |
| `AWS_REGION` | Default: `us-east-1`. |

---

## 🌐 Frontend Routing & CORS

| Backend Variable | Description |
| :--- | :--- |
| `PROD_FRONTEND_URL` | Used for CORS allowance in production. |
| `SANDBOX_FRONTEND_URL` | Used for CORS allowance in development. |
| `ALLOWED_HOSTS` | Comma-separated list of extra allowed origins. |

| Frontend Variable | Description |
| :--- | :--- |
| `NEXT_PUBLIC_PROD_API_URL` | Production Backend URL. |
| `NEXT_PUBLIC_SANDBOX_API_URL` | Local/Sandbox Backend URL. |

---

## 🛠️ Debug & Utility

| Variable | Description |
| :--- | :--- |
| `DEBUG` | If `true`, enables verbose tracebacks and debug logging. |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `MAX_FILE_SIZE_MB` | Default: `50`. |
| `SECRET_KEY` | Cryptographic secret for session signing. |
| `NEXT_PUBLIC_DEV_BYPASS_PAYMENTS` | Frontend ONLY. Set to `true` to skip payment UI checks (Dev only). |
