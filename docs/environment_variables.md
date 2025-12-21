# Environment Configuration Guide

This document outlines the core environment variables that drive the PDF2Audiobook platform. These variables control everything from billing logic to storage backends.

---

## 🌎 Core Environment Control

### 1. ENVIRONMENT (The "Where")
Tells the application which operational context it is running in.
- **Possible Values**: `development`, `staging`, `production`
- **What it Controls**: 
    - **Payments**: Toggles between Paddle Sandbox and Production environments.
    - **Debug UI**: Enables the "Debug Metrics & Metadata" section on the Job View page when set to `development`.
    - **Security**: Relaxes certain origin checks in development for easier local testing.

### 2. DEBUG (The "How much detail")
A switch to enable or disable deep internal visibility.
- **Possible Values**: `true`, `false`
- **What it Controls**: 
    - **Error Detail**: When `true`, the API returns full Python tracebacks (file names and line numbers) to the client on failure.
    - **Logging**: Enables `DEBUG` level logs for tracing complex PDF processing steps.
    - **Security**: Adds HSTS (Strict-Transport-Security) headers only when `DEBUG` is `false`.

---

## 🔑 Authentication & Security

### 3. CLERK_PEM_PUBLIC_KEY (The "Bouncer's ID")
The RSA Public Key used to verify the authenticity of user login tokens.
- **Possible Values**: A full `-----BEGIN PUBLIC KEY-----` string from the Clerk Dashboard.
- **What it Controls**: All secure API access. If this is wrong, all users will receive `401 Unauthorized` errors.

### 4. SECRET_KEY (The "Vault Key")
Used for internal cryptographic signing of temporary tokens and sessions.
- **Possible Values**: Any long, random alphanumeric string.
- **What it Controls**: Security integrity of the backend. **Must be unique in production.**

---

## 🤖 AI & Processing

### 5. OPENROUTER_API_KEY (The "Brain Fuel")
Your API key for the OpenRouter gateway.
- **Possible Values**: `sk-or-v1-...`
- **What it Controls**: Powers the LLM features like Concept Explanations and Summaries.

### 6. LLM_MODEL (The "Brain Type")
Specifies which AI model to use via OpenRouter.
- **Possible Values**: `google/gemini-2.0-flash-001`, `anthropic/claude-3-haiku`, etc.
- **What it Controls**: The quality and speed of document summarization.

---

## 📦 Storage & Infrastructure

### 7. AWS_ENDPOINT_URL (The "Post Office Address")
The custom URL for your S3-compatible storage provider.
- **Possible Values**: `https://<account_id>.r2.cloudflarestorage.com` (for Cloudflare R2).
- **What it Controls**: Redirects storage requests away from standard Amazon S3 to more cost-effective providers like R2.

### 8. S3_BUCKET_NAME (The "Warehouse Name")
The specific bucket where PDFs and Audio files are stored.
- **Possible Values**: e.g., `pdf2audiobook-assets`
- **What it Controls**: Organization of file assets.

---

## 💳 Billing & Payments

### 9. PADDLE_ENVIRONMENT (The "Bank Branch")
Tells the Paddle integration whether to process real money or test transactions.
- **Possible Values**: `sandbox`, `production`
- **What it Controls**: Whether users are charged real money.

---

## 📊 Deployment Scenarios

| Scenario | ENVIRONMENT | DEBUG | PADDLE_ENVIRONMENT | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Local Development** | `development` | `true` | `sandbox` | Working on code locally; full error detail; test payments. |
| **Cloud Debugging** | `development` | `true` | `sandbox` | Testing Render deployments; seeing debug metrics in the UI. |
| **Production Launch** | `production` | `false` | `production` | Scaling to real users; secure logs; real money transactions. |
| **Security Audit** | `production` | `false` | `sandbox` | Testing production security headers while using test credits. |

---

## 🛠 Complete Reference Table

| Variable | Required | Mnemonic | Default |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | The "Work Bench" | `sqlite:///./dev.db` |
| `REDIS_URL` | Yes | The "Messaging Hub" | `redis://localhost:6379/0` |
| `CORS_ALLOW_ORIGINS` | No | The "Allowed Guests" | `*` (Dev) |
| `LOG_LEVEL` | No | The "Filter Noise" | `INFO` |
| `MAX_FILE_SIZE_MB` | No | The "Scale Limit" | `50` |
| `LLM_MODEL` | No | The "AI Model" | `google/gemini-2.0-flash-001` |
