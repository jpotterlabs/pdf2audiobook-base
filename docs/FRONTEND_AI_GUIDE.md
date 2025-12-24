# Frontend AI Development Guide

This guide is for AI Agents (like Cursor/Windsurf/Gemini) to understand how to build and extend the PDF2Audiobook frontend.

## 1. Stack Overview

-   **Framework**: Next.js 14+ (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS (v3 or v4)
-   **State Management**: React Context (`CreditsContext`) + SWR (optional but good for polling)
-   **Auth**: Clerk (`@clerk/nextjs`)
-   **Icons**: Lucide React

## 2. Design System & Aesthetics

### Core Principles
-   **Modern & Clean**: Use ample whitespace, rounded corners (`rounded-xl`), and subtle shadows.
-   **Visual Hierarchy**: distinct primary/secondary actions.
-   **Feedback**: Loading spinners for async actions, toast notifications for errors/success.

### Key Components
-   **Glassmorphism**: Use `bg-white/80 backdrop-blur-md` for overlays/headers.
-   **Gradients**: Use subtle gradients for primary buttons (e.g., `bg-gradient-to-r from-blue-600 to-indigo-600`).

## 3. Core Architecture

### Authentication & Credits
We use a **hybrid context** approach.

-   **`CreditsContext`**: Wraps the entire app. It *internally* uses `useAuth` to get tokens.
-   **Usage**:
    ```tsx
    const { credits, loading, refreshCredits } = useCredits()
    ```
-   **Safe Fallback**: If Clerk is missing (dev mode), it returns null credits but does NOT crash.

### API Layer (`src/lib/api.ts`)
All backend calls must go through the centralized API client.

-   **Pattern**: Pass the `token` explicitly to these functions.
-   **Function Signature**: `async function createJob(token: string, data: FormData)`
-   **Error Handling**: The API client should normalize errors (catch 402, 401, etc.).

## 4. Feature Implementation Guides

### A. Creating a New Page
1.  **Layout**: Use the standard `AppShell` (which includes `Header`).
2.  **Auth Protection**: Wrap with `withAuth` or check `userId` from Clerk.
3.  **Data Fetching**: Use `useEffect` or SWR to fetch data, passing the token from `getToken()`.

### B. Accessing User Balance
**Do NOT** fetch user balance manually in components.
-   ✅ **Correct**: `const { credits } = useCredits()`
-   ❌ **Incorrect**: `fetch('/api/v1/auth/me')` inside a component.

### C. Job Creation
1.  Check `credits > 0` before allowing submission.
2.  Call `api.createJob()`.
3.  On success, call `refreshCredits()` to update the header balance immediately.

## 5. Directory Structure

```
frontend/
├── src/
│   ├── app/                 # Pages (Next.js App Router)
│   ├── components/
│   │   ├── ui/             # Reusable UI (Button, Input, Card)
│   │   ├── Header.tsx      # Main Nav
│   │   └── ...
│   ├── contexts/           # Global State (CreditsContext)
│   ├── lib/
│   │   ├── api.ts          # Backend Client
│   │   └── utils.ts        # CN helper etc.
│   └── types/              # TS Interfaces
```

## 6. Common Prompts

**Prompt for generating a new UI component:**
> "Create a [Component Name] using Tailwind CSS and Lucide icons. It should look modern, with rounded corners and smooth transitions. Use the `Button` component from `@/components/ui/button` if available."


**Prompt for connecting to API:**
> "Wire up the [Action Name] button to call `api.endpointName`. Ensure you get the auth token using `useAuth` first, and handle loading/error states. After success, trigger `refreshCredits` from `useCredits`."

**Prompt for implementing the Credit & Usage System:**
> "Refactor the application to fully integrate the hybrid Credit & Usage system.
> 1.  **Context**: Use the existing `CreditsContext` for global state.
> 2.  **Header**: Display the user's `credits` balance (e.g., '$10.50') and a 'Refresh' button. Show a loading spinner while fetching.
> 3.  **Job Creation**: In the Upload form, check `credits` from the context. If balance is <= 0 and user is not on a plan, disable the submit button and show a 'Low Credits' warning linking to `/pricing`.
> 4.  **Job History**: Update the Job List item component to display `estimated_cost` (as currency), `tokens_used`, and `chars_processed` if available in the job object.

**Prompt for Backend Hardening & Usage Logic:**
> "Implement robust usage tracking and security measures in the backend:
> 1.  **Paddle Hardening**: Create a `WebhookEvent` table to log all incoming payloads (`received` -> `processed`). Ensure `UserService` handles `payment.succeeded` by explicitly adding to `credit_balance`.
> 2.  **Usage Tracking**: Modify the `PDFToAudioPipeline` to return exact token (LLM) and character (TTS) counts. Save these to the `Job` record (`tokens_used`, `chars_processed`).
> 3.  **Cost Deduction**: IN the Celery task, calculate `final_cost` based on usage and deduct it from `user.credit_balance`.
> 4.  **Endpoint Gating**: Update `POST /jobs/` to enforce strictly: if `credit_balance <= 0`, return 402 (Payment Required)."

## 7. Backend Features Reference (Usage & Gating)
*This section helps the Frontend Agent understand what the Backend provides.*

-   **Endpoint Gating**: The backend explicitly returns **402 Payment Required** if the user tries to create a job with insufficient funds. The Frontend **MUST** handle this error and redirect to `/pricing`.
-   **Structure Usage Stats**: The `Job` object returned by the API now includes:
    -   `chars_processed`: Number of characters sent to TTS.
    -   `tokens_used`: Number of LLM tokens used.
    -   `estimated_cost`: The final cost deducted from the user.
-   **Webhook Logging**: If a user claims they paid but credits didn't appear, check the `webhook_events` table in the DB. The frontend can implement a "Check Payment Status" button that polls for user profile updates.
