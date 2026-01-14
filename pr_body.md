Summary
This PR transforms the codebase from a SaaS-oriented application into a streamlined, open-source core. The primary focus was removing proprietary integrations (Auth, Payments, Credits) and enhancing local-first/self-hosted capabilities.

Key Changes
1. Removal of SaaS Infrastructure
- Authentication: Removed Clerk integration. Middleware and hooks refactored for local-friendly auth.
- Payments & Credits: Deleted Stripe/Paddle services, webhooks, and product sync scripts.
- UI Components: Removed pricing pages and subscription managers.

2. Enhanced Pipeline & Local LLM/TTS Support
- Local TTS: Added support for OpenAI-compatible local endpoints (e.g., Kokoro-FastAPI).
- Pipeline: Introduced "Full + Explanation" mode and enhanced LLM cost tracking.

3. Documentation & Developer Experience
- Added comprehensive guides in /docs (Backend, Frontend, System Walkthrough).
- Updated utility scripts for DB management and E2E testing.

4. Backend & Worker Refinement
- Updated docker-compose.yml for easier local deployment.
- Refactored PDFToAudioPipeline for better robustness.

NOTE: This change converts the project into a "Bring Your Own Key" (BYOK) tool.
