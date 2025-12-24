# Credits & Usage Tracking System

This document outlines the architecture and implementation of the usage tracking, credit deduction, and endpoint gating systems in the PDF2Audiobook platform.

## Overview

The platform operates on a **hybrid model**:
1.  **Subscriptions**: Provide a base allowance (e.g., "Pro" tier).
2.  **Credits**: A granular currency (`user.credit_balance`) used to pay for processing costs beyond the base allowance or for pay-as-you-go users.

**Key Feature**: Usage is tracked precisely based on **Characters** (for Text-to-Speech) and **Tokens** (for LLM Summaries/Explanations).

---

## 1. Usage Tracking Architecture

### Data Models
-   **`User.credit_balance`** (`Numeric(10, 2)`): The user's current available funds/credits.
-   **`Job.chars_processed`** (`Integer`): Total characters sent to the TTS provider.
-   **`Job.tokens_used`** (`Integer`): Total LLM tokens (prompt + completion) used for summaries/explanations.
-   **`Job.estimated_cost`** (`Float`): The final calculated cost of the job, deducted from the user.

### processing Pipeline (`worker/pdf_pipeline.py`)

The pipeline now returns detailed usage statistics along with the audio file:
1.  **Text Extraction**: PDF text is extracted and cleaned.
2.  **LLM Processing**: 
    -   `_call_llm_with_retry` captures token usage from the LLM provider response.
    -   Summaries and Explanations aggregate these token counts.
3.  **TTS Processing**:
    -   Text is chunked for TTS.
    -   The pipeline counts the exact number of characters in each chunk sent to the TTS API.
4.  **Result**: Returns `usage_stats = {'chars': 15000, 'tokens': 450}`.

### Cost Calculation (`worker/tasks.py`)

The Celery worker calculates the final cost at the end of the job:

```python
# Pseudo-code logic
tts_cost = calculate_tts_cost(voice_provider, chars_processed)
llm_cost = (tokens_used / 1_000_000) * 2.00  # $2.00 per 1M tokens (configurable)

final_cost = tts_cost + llm_cost
```

---

## 2. Credit Deduction & Gating

### Deduction
Credits are deducted *automatically* by the worker upon job completion:
1.  Worker calculates `final_cost`.
2.  Updates `User.credit_balance -= final_cost`.
3.  Updates `Job` record with `chars_processed`, `tokens_used`, and `estimated_cost`.

### Endpoint Gating (`JobService.can_user_create_job`)
Before a job is even created, the API checks if the user has sufficient standing:
1.  **Credit Check**: If `user.credit_balance > 0`, the job is allowed.
2.  **Legacy Fallback**: If using a subscription tier (Free/Pro), checks monthly job limits.

This ensures users cannot abuse the system with zero balance.

---

## 3. Webhook Hardening & Paddle Integration

We use **Paddle** for payments. To ensure reliability:

### Webhook Logging (`WebhookEvent`)
Every incoming webhook from Paddle is logged to a `webhook_events` table *before* processing.
-   **Status**: `received` -> `processed` (or `failed`).
-   **Payload**: Full JSON payload stored for auditing/debugging.
-   **Replayability**: Events can be re-processed manually if needed.

### Credit Top-up
When a `payment_succeeded` webhook is received:
1.  The payment amount/product value is looked up.
2.  Credits are added to `user.credit_balance`.

---

## 4. Frontend Architecture (`CreditsContext`)

To manage credit state efficiently in the UI:

-   **`CreditsContext`**: A React Context that creates a global "store" for credit data.
    -   Wraps the entire application in `layout.tsx`.
    -   Uses `useRef` to handle Clerk's unstable `getToken` reference safely.
-   **`useCredits()`**: Custom hook for components to access:
    -   `credits`: Current balance.
    -   `loading`: Fetch status.
    -   `refreshCredits()`: Function to force a re-fetch (e.g., after a new job starts).
-   **No-Auth Safety**: The hook gracefully returns default values if the Auth provider is missing (e.g., in local dev without keys), preventing crashes.

### Visuals
The Header uses this context to display a **Live Credit Balance** with a loading spinner during initial fetch.
