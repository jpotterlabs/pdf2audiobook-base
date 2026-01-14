# End-to-End System Walkthrough

This guide provides a step-by-step walkthrough of the PDF2AudioBook system, from initial setup to downloading your first AI-generated audiobook.

## 📍 Where do I point my browser?
- **Frontend (Reference UI)**: [http://localhost:3000](http://localhost:3000)
- **Backend API (Swagger Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🚀 Step 1: Start the Engine
To use the system, you must have three components running simultaneously:

1. **The Backend (FastAPI)**:
   ```bash
   cd backend && python -m uvicorn main:app --port 8000
   ```
2. **The Worker (Celery)**:
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```
3. **The Frontend (Next.js)**:
   ```bash
   cd apps/reference-ui && npm run dev -- --port 3000
   ```

## 📂 Step 2: Upload Your PDF
1. Navigate to [http://localhost:3000/upload](http://localhost:3000/upload).
2. Drag and drop a PDF file (e.g., a research paper or a novel) into the drop zone.
3. Configure your preferences:
    - **Voice**: Choose between available OpenAI or Google voices.
    - **Mode**: Choose the conversion strategy:
        - `full`: Complete narration of the document.
        - `summary`: Concise executive summary.
        - `explanation`: Educational breakdown of core concepts.
        - `summary_explanation`: Both a summary and a concept explanation.
        - `full_explanation`: The complete text preceded by a concept explanation.
4. Click **Start Conversion**.

## 🔄 Step 3: Monitor Progress
After clicking convert, you will be redirected to the **Job Details** page.
- You will see a progress bar indicating the pipeline stage (Extraction -> Processing -> Generation).
- You can safely leave this page; the job will continue in the background. Navigate back via the "My Jobs" link in the header anytime.

## 🎧 Step 4: Download & Listen
Once the status changes to **"Completed"**:
1. An audio player will appear on the Job Details page.
2. Click the **Download Audio** button to save the MP3 file to your device.
3. Check the **Job Metadata** at the bottom to see processing metrics like tokens used and estimated cost.

---

## 🛠 Advanced: Testing via Script
If you prefer the command line, you can run the integrated journey script to verify the entire backend/worker pipeline without the UI:
```bash
python backend/test_journey.py
```
This script will mock a file upload, track the job status to completion, and print the results to your terminal.
