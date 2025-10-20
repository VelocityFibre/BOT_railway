#!/usr/bin/env python3
"""Quick test of the verification engine with OpenAI API"""

import os
import sys
sys.path.append('.')

from src.verifier import FiberInstallationVerifier
from src.config import Config

def test_verifier():
    """Test the OpenAI Vision verifier with a simple test"""
    print("🔧 Testing Fiber Installation Verifier...")

    try:
        # Initialize verifier
        verifier = FiberInstallationVerifier()
        print("✅ Verifier initialized successfully")

        # Test with a sample image path (this will fail since we don't have a real image)
        # but it will test if the API connection works
        print("📸 Testing API connection...")

        # Create a simple test image
        from PIL import Image, ImageDraw
        import io

        # Create a test image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 350, 250], outline='black', width=2)
        draw.text((100, 150), "Test Property Frontage", fill='black')

        # Save test image
        test_image_path = './test_property.jpg'
        img.save(test_image_path)
        print(f"✅ Test image created: {test_image_path}")

        # Test step 1 verification (Property Frontage)
        print("🔍 Testing Step 1 verification (Property Frontage)...")
        result = verifier.verify_step(test_image_path, 1)

        print(f"Result:")
        print(f"  Step: {result.step} - {result.step_name}")
        print(f"  Passed: {result.passed}")
        print(f"  Score: {result.score}/10")
        print(f"  Confidence: {result.confidence}")
        print(f"  Issues: {result.issues}")
        print(f"  Recommendation: {result.recommendation}")

        # Clean up
        os.remove(test_image_path)
        print("🧹 Test image cleaned up")

        print("✅ Verification engine test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing verifier: {e}")
        return False

if __name__ == "__main__":
    success = test_verifier()
    sys.exit(0 if success else 1)