import sys
import os
import time

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.models import ConversionMode, JobStatus

def test_full_explanation_mode():
    """Verifies that the new enum value exists and is accessible."""
    print("Testing ConversionMode Enum...")
    try:
        mode = ConversionMode.full_explanation
        print(f"✅ Success: ConversionMode.full_explanation = {mode}")
    except AttributeError:
        print("❌ Failed: ConversionMode.full_explanation does not exist!")
        sys.exit(1)

if __name__ == "__main__":
    test_full_explanation_mode()
