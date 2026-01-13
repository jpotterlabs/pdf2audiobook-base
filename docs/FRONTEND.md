# Frontend Documentation: Reference UI

The Reference UI is a high-performance Next.js 16 application built to showcase the core capabilities of the PDF-to-audiobook pipeline. It has been simplified to provide a seamless, no-friction experience for developers and researchers.

## 🎨 Theme & User Experience
- **Aesthetic**: Premium, minimalist design using Tailwind CSS.
- **Color Palette**: 
    - **Primary**: Blue-600 (`#2563eb`) for high-intent actions.
    - **Neutral**: Slate-50 to Slate-900 for a sophisticated, technical feel.
- **Interactivity**: Smooth CSS transitions, glassmorphism backgrounds (`bg-white/80 backdrop-blur`), and real-time status polling.

## 🧱 Component Architecture

### Core Pages (`src/app`)
| Page | Route | Description |
| :--- | :--- | :--- |
| **Home** | `/` | Landing page highlighting "Start Converting" and "My Jobs." |
| **Upload** | `/upload` | Interactive drag-and-drop zone with AI configuration options. |
| **My Jobs** | `/jobs` | Dashboard with filtering, progress bars, and cleanup tools. |
| **Job Details** | `/jobs/view` | Deep-dive into a single job with audio playback and metadata. |

### Shared Components (`src/components`)
- **Header**: Responsive navigation with a "Base User" indicator.
- **AppShell**: Root wrapper providing global layout and styling.
- **Icons**: Powered by `lucide-react`.

## 🔐 Mock Authentication ("Base User")
The base pipeline uses a mock-tenant model.
- **Logic**: Located in `src/lib/api.ts`.
- **Implementation**: Every API request is automatically signed with a hardcoded `mock_admin_token_123`.
- **Result**: Users don't need to sign up or log in. All jobs created on a local instance are automatically linked to the same "Base User" profile, ensuring immediate usability.

## 📡 API Integration (`src/lib/api.ts`)
The frontend uses `axios` to communicate with the FastAPI backend.
- **Base URL**: Defaults to `http://localhost:8000/api/v1`.
- **Normalization**: The client automatically ensures all requests target the versioned API paths.
- **Polling**: The `JobDetailContent` component uses `setInterval` (5s) to poll `/api/v1/jobs/status/{id}` for live updates without requiring WebSockets.

## 🛠 Troubleshooting the Frontend
- **"Failed to Fetch Jobs"**: Usually means the backend at `localhost:8000` is not running.
- **Hydration Errors**: Can occur if `localStorage` or `searchParams` are accessed before the component is mounted.
- **Audio Not Playing**: Check the `audio_s3_url` in the metadata. If using local storage, ensure the file exists in the backend's `storage/` directory.

## 💻 Development Commands
```bash
# Enter the directory
cd apps/reference-ui

# Install dependencies
npm install

# Start development server
npm run dev -- --port 3000
```
Application will be accessible at [http://localhost:3000](http://localhost:3000).
