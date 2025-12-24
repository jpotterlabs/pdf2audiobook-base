# PDF2Audiobook - Turn Your PDFs into Lifelike Audiobooks

A premium SaaS platform for converting PDF documents into high-quality audiobooks using AI-powered text-to-speech technology.

## Features

- **Multiple TTS Providers**: Choose from OpenAI, Google Cloud, AWS Polly, Azure, and ElevenLabs
- **AI Summaries**: Generate intelligent summaries or full word-for-word conversion
- **Custom Voices**: Select from dozens of natural-sounding voices
- **Flexible Speed Control**: Adjust reading speed from 0.5x to 2.0x
- **Real-time Progress**: Track conversion progress with live updates
- **Secure Authentication**: Powered by Clerk for seamless auth experience
- **Beautiful UI**: Premium dark mode design with glassmorphism effects

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4 with custom glassmorphism utilities
- **UI Components**: Shadcn/UI (Radix-based)
- **Authentication**: Clerk
- **State Management**: React Query (TanStack Query)
- **Icons**: Lucide React
- **Form Validation**: React Hook Form + Zod

## Getting Started

1. Clone the repository
2. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`

3. Set up environment variables:
   Copy `.env.local.example` to `.env.local` and fill in your credentials:
   - Clerk API keys from [clerk.com](https://clerk.com)
   - Backend API URL

4. Run the development server:
   \`\`\`bash
   npm run dev
   \`\`\`

5. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

\`\`\`
├── app/                    # Next.js app router pages
│   ├── jobs/              # Jobs dashboard
│   ├── upload/            # Upload page
│   ├── sign-in/           # Clerk sign in
│   └── sign-up/           # Clerk sign up
├── components/
│   ├── landing/           # Landing page components
│   ├── jobs/              # Job management components
│   ├── upload/            # File upload components
│   ├── audio/             # Audio player
│   └── ui/                # Shadcn UI components
├── lib/
│   ├── api/               # API client and types
│   ├── constants/         # Voice options and constants
│   └── hooks/             # Custom React hooks
└── middleware.ts          # Clerk auth middleware
\`\`\`

## API Integration

The app connects to a FastAPI backend. Ensure the backend is running or update `NEXT_PUBLIC_API_URL` to point to your production API.

## Deployment

Deploy to Vercel with one click:

1. Push your code to GitHub
2. Import the repository in Vercel
3. Add environment variables
4. Deploy

## License

MIT License - feel free to use this project for your own purposes.
