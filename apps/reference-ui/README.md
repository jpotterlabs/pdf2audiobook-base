# PDF2AudioBook Frontend (Reference UI)

This is the reference frontend for the PDF2AudioBook Open Source Core. It provides a simple, functional interface for uploading PDFs and managing conversion jobs.

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment Variables

Create a `.env.local` file in the root of the `apps/reference-ui` directory and add the following environment variables:

```
# Point to your backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The frontend will automatically route requests to the versioned API (`/api/v1`) under `NEXT_PUBLIC_API_URL`.
