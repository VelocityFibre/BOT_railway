import os
import base64
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from PIL import Image
import io
from openai import OpenAI
from .config import Config
from .prompts import INSTALLATION_STEP_PROMPTS

logger = logging.getLogger(__name__)

@dataclass
class VerificationResult:
    """Result of photo verification for a specific step"""
    step: int
    step_name: str
    passed: bool
    score: float
    issues: List[str]
    confidence: float
    recommendation: str

class FiberInstallationVerifier:
    """AI-powered photo verification engine for fiber installations"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize verifier with OpenAI API"""
        self.client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self.prompts = INSTALLATION_STEP_PROMPTS

        if not self.client.api_key:
            raise ValueError("OpenAI API key is required")

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI Vision API"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if too large (OpenAI limit: 1024x1024)
                max_size = (Config.MAX_PHOTO_DIMENSION, Config.MAX_PHOTO_DIMENSION)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save to buffer with compression
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=Config.COMPRESSION_QUALITY)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            raise ValueError(f"Image processing failed: {str(e)}")

    def verify_step(self, image_path: str, step_number: int) -> VerificationResult:
        """
        Verify a single installation step photo

        Args:
            image_path: Path to photo file
            step_number: Installation step number (1-14)

        Returns:
            VerificationResult with detailed analysis
        """
        step_keys = {
            1: "step1_frontage",
            2: "step2_wall_before",
            3: "step3_cable_span",
            4: "step4_entry_outside",
            5: "step5_entry_inside",
            6: "step6_ont_connection",
            7: "step7_patched_labelled",
            8: "step8_work_area_complete",
            9: "step9_ont_barcode",
            10: "step10_mini_ups",
            11: "step11_powermeter_reading",
            12: "step12_powermeter_ont",
            13: "step13_active_light",
            14: "step14_customer_signature"
        }
        step_key = step_keys.get(step_number)

        if step_key not in self.prompts:
            return VerificationResult(
                step=step_number,
                step_name=f"Step {step_number}",
                passed=False,
                score=0,
                issues=[f"Invalid step number: {step_number}"],
                confidence=1.0,
                recommendation="Please use a valid step number (1-14)"
            )

        try:
            # Encode image for API
            base64_image = self._encode_image(image_path)

            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.prompts[step_key]
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent results
            )

            # Parse response
            result_text = response.choices[0].message.content
            logger.info(f"OpenAI response for step {step_number}: {result_text[:100]}...")

            try:
                # Try to parse JSON response (remove markdown if present)
                if result_text.startswith('```json'):
                    result_text = result_text.replace('```json', '').replace('```', '').strip()
                result_json = json.loads(result_text)

                return VerificationResult(
                    step=step_number,
                    step_name=self._get_step_name(step_number),
                    passed=result_json.get('passed', False),
                    score=min(max(result_json.get('score', 0), 0), 10),  # Clamp 0-10
                    issues=result_json.get('issues', []),
                    confidence=min(max(result_json.get('confidence', 0), 0), 1),  # Clamp 0-1
                    recommendation=result_json.get('recommendation', '')
                )

            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response for step {step_number}: {result_text}")

                # Fallback parsing if JSON fails
                return self._parse_text_response(result_text, step_number)

        except Exception as e:
            logger.error(f"Verification failed for step {step_number}: {e}")

            return VerificationResult(
                step=step_number,
                step_name=self._get_step_name(step_number),
                passed=False,
                score=0,
                issues=[f"Verification error: {str(e)}"],
                confidence=0,
                recommendation="Please try again or contact support if problem persists"
            )

    def _parse_text_response(self, response_text: str, step_number: int) -> VerificationResult:
        """Fallback parsing for non-JSON responses"""
        # Simple text analysis for fallback
        text_lower = response_text.lower()

        passed_keywords = ['pass', 'good', 'excellent', 'proper', 'correct']
        failed_keywords = ['fail', 'issue', 'problem', 'error', 'missing', 'blurry']

        passed = any(keyword in text_lower for keyword in passed_keywords)
        failed = any(keyword in text_lower for keyword in failed_keywords)

        # Default to failed if uncertain
        passed = passed and not failed

        return VerificationResult(
            step=step_number,
            step_name=self._get_step_name(step_number),
            passed=passed,
            score=8 if passed else 4,
            issues=[response_text] if not passed else [],
            confidence=0.5,  # Lower confidence for text parsing
            recommendation=response_text if not passed else "Photo looks good!"
        )

    def _get_step_name(self, step_number: int) -> str:
        """Get human-readable step name"""
        step_names = {
            1: "Property Frontage",
            2: "Location on Wall (Before Install)",
            3: "Outside Cable Span",
            4: "Home Entry Point - Outside",
            5: "Home Entry Point - Inside",
            6: "Fibre Entry to ONT",
            7: "Patched & Labelled Drop",
            8: "Overall Work Area After Completion",
            9: "ONT Barcode",
            10: "Mini-UPS Serial Number",
            11: "Powermeter Reading (Drop/Feeder)",
            12: "Powermeter at ONT (Before Activation)",
            13: "Active Broadband Light",
            14: "Customer Signature"
        }
        return step_names.get(step_number, f"Step {step_number}")

    def verify_installation_batch(self, photos: Dict[int, str]) -> Dict:
        """
        Verify multiple photos for a complete installation

        Args:
            photos: Dictionary mapping step numbers to photo paths

        Returns:
            Comprehensive verification report
        """
        results = {}
        total_score = 0
        verified_count = 0

        for step_num, photo_path in photos.items():
            if os.path.exists(photo_path):
                result = self.verify_step(photo_path, step_num)
                results[step_num] = result

                if result.confidence > 0.3:  # Only count confident results
                    total_score += result.score
                    verified_count += 1
            else:
                results[step_num] = VerificationResult(
                    step=step_num,
                    step_name=self._get_step_name(step_num),
                    passed=False,
                    score=0,
                    issues=["Photo not provided"],
                    confidence=1.0,
                    recommendation="Please upload photo for this step"
                )

        # Calculate overall metrics
        average_score = total_score / max(verified_count, 1) if verified_count > 0 else 0
        completion_rate = len(photos) / 14 * 100
        passed_steps = sum(1 for r in results.values() if r.passed)

        # Determine overall status
        status = "PASS" if (
            average_score >= Config.PASSING_SCORE_THRESHOLD and
            completion_rate >= Config.PASSING_COMPLETION_RATE * 100 and
            passed_steps >= 12  # At least 12 steps must pass
        ) else "FAIL"

        return {
            "overall_score": round(average_score, 1),
            "completion_rate": round(completion_rate, 1),
            "total_steps": 14,
            "submitted_steps": len(photos),
            "passed_steps": passed_steps,
            "verified_steps": verified_count,
            "status": status,
            "results": results,
            "summary": self._generate_summary(results, status)
        }

    def _generate_summary(self, results: Dict[int, VerificationResult], status: str) -> str:
        """Generate human-readable summary of verification results"""
        if status == "PASS":
            return (
                "🎉 Installation verification PASSED!\n\n"
                f"✅ {sum(1 for r in results.values() if r.passed)} steps approved\n"
                "📊 Quality standards met\n"
                "🚀 Ready for activation"
            )
        else:
            failed_steps = [step for step, result in results.items() if not result.passed]
            return (
                "❌ Installation verification needs attention\n\n"
                f"❌ {len(failed_steps)} steps need retake\n"
                f"✅ {sum(1 for r in results.values() if r.passed)} steps approved\n\n"
                "Please retake photos for failed steps and resubmit."
            )