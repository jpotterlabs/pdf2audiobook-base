import requests
import time
import os
from io import BytesIO

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = "mock-token-for-base-pipeline" # Any string works for the base pipeline

def create_mock_pdf():
    """Returns a simple PDF byte stream for testing."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Hello PDF2Audiobook World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"

def run_test_journey():
    print("🚀 Starting PDF-to-Audiobook Test Journey")
    
    # 1. Setup Headers
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    # 2. Upload PDF
    print("📤 Step 1: Uploading PDF...")
    pdf_content = create_mock_pdf()
    files = {"file": ("demo_test.pdf", BytesIO(pdf_content), "application/pdf")}
    data = {
        "voice_provider": "openai",
        "voice_type": "alloy",
        "reading_speed": 1.0,
        "include_summary": False,
        "conversion_mode": "full"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/jobs", 
            headers=headers, 
            files=files, 
            data=data,
            timeout=(10, 300)
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"❌ Upload failed (HTTP Error): {e}")
        print(f"Response: {getattr(e.response, 'text', 'No response body')}")
        return
    except requests.RequestException as e:
        print(f"❌ Upload failed (Request Error): {e}")
        return

    job_data = response.json()
    job_id = job_data["id"]
    print(f"✅ Job created! ID: {job_id}")

    # 3. Poll for Status
    print(f"⏳ Step 2: Polling status for Job {job_id}...")
    max_retries = 30
    delay = 2
    
    for i in range(max_retries):
        try:
            status_resp = requests.get(
                f"{API_BASE_URL}/jobs/{job_id}", 
                headers=headers,
                timeout=(10, 60)
            )
            status_resp.raise_for_status()
            current_job = status_resp.json()
            status = current_job["status"]
            progress = current_job.get("progress_percentage", 0)
            
            print(f"   [{i+1}/{max_retries}] Status: {status} | Progress: {progress}%")
            
            if status == "completed":
                print("\n🎉 JOURNEY COMPLETE!")
                print(f"📁 Original File: {current_job['original_filename']}")
                print(f"🔊 Audio URL: {current_job['audio_s3_url']}")
                print(f"💰 Estimated Cost: ${current_job['estimated_cost']}")
                return
            elif status == "failed":
                print(f"❌ Job failed: {current_job.get('error_message')}")
                return
            
            time.sleep(delay)
        except requests.HTTPError as e:
            print(f"⚠️ Polling error (HTTP Error): {e}")
            print(f"Response: {getattr(e.response, 'text', 'No response body')}")
            break
        except requests.RequestException as e:
            print(f"⚠️ Polling error (Request Error): {e}")
            break
            
    print("🕒 Polling timed out.")

if __name__ == "__main__":
    run_test_journey()
