import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from src.verifier import FiberInstallationVerifier, VerificationResult

class TestFiberInstallationVerifier:
    """Test suite for FiberInstallationVerifier"""

    @pytest.fixture
    def verifier(self):
        """Create verifier instance for testing"""
        with patch('src.verifier.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            verifier = FiberInstallationVerifier(api_key="test-key")
            verifier.client = mock_client
            return verifier

    @pytest.fixture
    def sample_image(self):
        """Create a temporary image file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Create a simple test image (1x1 pixel JPEG)
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(temp_file.name, 'JPEG')
            yield temp_file.name
        os.unlink(temp_file.name)

    def test_init_with_api_key(self):
        """Test verifier initialization with API key"""
        with patch('src.verifier.OpenAI'):
            verifier = FiberInstallationVerifier(api_key="test-key")
            assert verifier.client is not None

    def test_init_without_api_key(self):
        """Test verifier initialization fails without API key"""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            FiberInstallationVerifier(api_key=None)

    def test_encode_image_success(self, verifier, sample_image):
        """Test successful image encoding"""
        result = verifier._encode_image(sample_image)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_encode_image_invalid_file(self, verifier):
        """Test image encoding with invalid file"""
        with pytest.raises(ValueError, match="Image processing failed"):
            verifier._encode_image("nonexistent.jpg")

    def test_verify_step_success(self, verifier, sample_image):
        """Test successful step verification"""
        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"passed": true, "score": 9, "issues": [], "confidence": 0.95, "recommendation": "Great photo!"}'
        verifier.client.chat.completions.create.return_value = mock_response

        result = verifier.verify_step(sample_image, 1)

        assert isinstance(result, VerificationResult)
        assert result.step == 1
        assert result.passed is True
        assert result.score == 9
        assert result.confidence == 0.95
        assert result.step_name == "Property Frontage"

    def test_verify_step_failure(self, verifier, sample_image):
        """Test step verification with failure"""
        # Mock OpenAI API response for failure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"passed": false, "score": 3, "issues": ["Photo too blurry"], "confidence": 0.85, "recommendation": "Please retake with steady hands"}'
        verifier.client.chat.completions.create.return_value = mock_response

        result = verifier.verify_step(sample_image, 1)

        assert result.passed is False
        assert result.score == 3
        assert "Photo too blurry" in result.issues
        assert "steady hands" in result.recommendation

    def test_verify_step_invalid_step(self, verifier, sample_image):
        """Test verification with invalid step number"""
        result = verifier.verify_step(sample_image, 99)

        assert result.passed is False
        assert "Invalid step number" in result.issues[0]

    def test_verify_step_api_error(self, verifier, sample_image):
        """Test verification when OpenAI API fails"""
        verifier.client.chat.completions.create.side_effect = Exception("API Error")

        result = verifier.verify_step(sample_image, 1)

        assert result.passed is False
        assert "Verification error" in result.issues[0]
        assert result.confidence == 0

    def test_parse_text_response(self, verifier):
        """Test fallback text response parsing"""
        response_text = "The photo looks good and passes all requirements"
        result = verifier._parse_text_response(response_text, 1)

        assert result.passed is True
        assert result.score == 8
        assert result.confidence == 0.5

    def test_parse_text_response_failure(self, verifier):
        """Test fallback text parsing for failure"""
        response_text = "The photo has issues with blurry content and poor lighting"
        result = verifier._parse_text_response(response_text, 1)

        assert result.passed is False
        assert result.score == 4

    def test_get_step_name(self, verifier):
        """Test step name retrieval"""
        assert verifier._get_step_name(1) == "Property Frontage"
        assert verifier._get_step_name(14) == "Customer Signature"
        assert verifier._get_step_name(99) == "Step 99"

    def test_verify_installation_batch(self, verifier, sample_image):
        """Test batch verification of multiple steps"""
        # Mock successful API responses
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"passed": true, "score": 8, "issues": [], "confidence": 0.9, "recommendation": "Good"}'
        verifier.client.chat.completions.create.return_value = mock_response

        # Create temporary copies of sample image
        photos = {}
        for step in [1, 2, 3]:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                from PIL import Image
                img = Image.new('RGB', (100, 100), color='blue')
                img.save(temp_file.name, 'JPEG')
                photos[step] = temp_file.name

        try:
            result = verifier.verify_installation_batch(photos)

            assert "overall_score" in result
            assert "completion_rate" in result
            assert "status" in result
            assert "results" in result
            assert len(result["results"]) == 3

        finally:
            # Clean up temporary files
            for photo_path in photos.values():
                os.unlink(photo_path)

    def test_verify_installation_batch_missing_file(self, verifier):
        """Test batch verification with missing photo files"""
        photos = {1: "nonexistent.jpg"}

        result = verifier.verify_installation_batch(photos)

        assert result["status"] == "FAIL"
        assert "Photo not provided" in result["results"][1].issues

    def test_generate_summary_pass(self, verifier):
        """Test summary generation for passing installation"""
        results = {
            1: VerificationResult(1, "Step 1", True, 9, [], 0.9, ""),
            2: VerificationResult(2, "Step 2", True, 8, [], 0.8, "")
        }

        summary = verifier._generate_summary(results, "PASS")
        assert "PASSED" in summary
        assert "🎉" in summary

    def test_generate_summary_fail(self, verifier):
        """Test summary generation for failing installation"""
        results = {
            1: VerificationResult(1, "Step 1", False, 3, ["Blurry"], 0.7, "Retake"),
            2: VerificationResult(2, "Step 2", True, 9, [], 0.9, "")
        }

        summary = verifier._generate_summary(results, "FAIL")
        assert "needs attention" in summary
        assert "❌" in summary

if __name__ == '__main__':
    pytest.main([__file__])