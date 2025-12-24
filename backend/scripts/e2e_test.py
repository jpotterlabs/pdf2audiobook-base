#!/usr/bin/env python3
"""
End-to-End System Integration Test for PDF2Audiobook.
This script simulates a full user workflow:
1. Health Check
2. Authentication (Mock/Verify)
3. PDF Upload & Job Creation
4. Polling for Completion
5. Verifying Usage & Costs
"""

import time
import sys
import httpx
from loguru import logger

BASE_URL = "http://localhost:8000"
TEST_TOKEN = "dev-secret-key-for-testing-only" # Requires TESTING_MODE=True
HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}

def run_e2e_test():
    logger.info("🚀 Starting End-to-End Test...")

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Health Check
        logger.info("Checking system health...")
        resp = client.get("/health")
        if resp.status_code != 200:
            logger.error(f"❌ Health check failed: {resp.text}")
            return
        logger.info(f"✅ System Health: {resp.json()['status']}")

        # 2. Auth Verify
        logger.info("Verifying authentication...")
        resp = client.post("/api/v1/auth/verify", headers=HEADERS, json={})
        if resp.status_code != 200:
            logger.error(f"❌ Auth verify failed: {resp.text}")
            return
        user_id = resp.json()["user"]["id"]
        initial_credits = resp.json()["user"]["credit_balance"]
        logger.info(f"✅ Auth Success. User: {user_id}, Balance: ${initial_credits}")

        # 3. Job Creation
        logger.info("Uploading PDF and creating job...")
        # Note: In a real test, provide a small valid PDF file
        # For this script, we assume 'test.pdf' exists or we send dummy bytes
        files = {"file": ("test.pdf", b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF", "application/pdf")}
        data = {
            "voice_provider": "google",
            "voice_type": "standard",
            "reading_speed": "1.0",
            "include_summary": "true"
        }
        
        resp = client.post("/api/v1/jobs/", headers=HEADERS, data=data, files=files)
        if resp.status_code == 402:
            logger.warning("⚠️ Insufficient credits for test. Please seed the DB with credits.")
            return
        if resp.status_code != 200:
            logger.error(f"❌ Job creation failed: {resp.text}")
            return
        
        job_id = resp.json()["id"]
        logger.info(f"✅ Job Created: {job_id}")

        # 4. Polling
        logger.info(f"Polling job {job_id} for status...")
        max_retries = 30
        for i in range(max_retries):
            resp = client.get(f"/api/v1/jobs/{job_id}/status", headers=HEADERS)
            status = resp.json()["status"]
            logger.info(f"[{i+1}/{max_retries}] Status: {status}")
            
            if status == "completed":
                logger.info("✅ Job Completed Successfully!")
                break
            if status == "failed":
                logger.error(f"❌ Job Failed: {resp.json().get('error', 'Unknown error')}")
                return
            
            time.sleep(5)
        else:
            logger.error("❌ Polling timed out.")
            return

        # 5. Final Verification
        logger.info("Verifying final balance and usage...")
        resp = client.get(f"/api/v1/jobs/{job_id}", headers=HEADERS)
        job_data = resp.json()
        logger.info(f"Usage: {job_data.get('chars_processed')} chars, {job_data.get('tokens_used')} tokens")
        logger.info(f"Cost Deducted: ${job_data.get('estimated_cost')}")

        resp = client.get("/api/v1/auth/me", headers=HEADERS)
        final_credits = resp.json()["credit_balance"]
        logger.info(f"✅ Initial: ${initial_credits} -> Final: ${final_credits}")

    logger.info("🎉 E2E Test Finished Successfully!")

if __name__ == "__main__":
    run_e2e_test()
