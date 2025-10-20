import os
import requests
import logging
from typing import Optional
from datetime import datetime
from PIL import Image
import io
from ..config import Config

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handles WhatsApp message operations and media downloads"""

    def __init__(self):
        self.twilio_account_sid = Config.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = Config.TWILIO_AUTH_TOKEN

    def download_photo(self, media_id: str, job_id: str) -> Optional[str]:
        """
        Download photo from Twilio media URL

        Args:
            media_id: Twilio media ID
            job_id: Installation job ID for file naming

        Returns:
            Path to downloaded photo file or None if failed
        """
        try:
            # Get media URL from Twilio
            media_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages/{media_id}/Media.json"

            response = requests.get(
                media_url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Failed to get media URL: {response.status_code}")
                return None

            media_data = response.json()
            if not media_data.get('media_list'):
                logger.error("No media in response")
                return None

            # Download the actual media content
            media_content_url = media_data['media_list'][0]['uri']
            media_response = requests.get(
                media_content_url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                timeout=30
            )

            if media_response.status_code != 200:
                logger.error(f"Failed to download media: {media_response.status_code}")
                return None

            # Save photo to appropriate directory
            return self._save_photo(media_response.content, job_id, media_id)

        except Exception as e:
            logger.error(f"Error downloading photo {media_id}: {e}")
            return None

    def _save_photo(self, photo_content: bytes, job_id: str, media_id: str) -> Optional[str]:
        """
        Save photo content to file system

        Args:
            photo_content: Raw photo data
            job_id: Installation job ID
            media_id: Twilio media ID

        Returns:
            Path to saved photo file
        """
        try:
            # Create directories if they don't exist
            base_dir = os.path.join(Config.PHOTO_STORAGE_PATH, "pending")
            os.makedirs(base_dir, exist_ok=True)

            # Generate filename
            timestamp = int(datetime.now().timestamp())
            filename = f"{job_id}_{media_id}_{timestamp}.jpg"
            filepath = os.path.join(base_dir, filename)

            # Process and optimize image
            processed_image = self._process_image(photo_content)

            # Save processed image
            with open(filepath, 'wb') as f:
                f.write(processed_image)

            logger.info(f"Saved photo to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving photo: {e}")
            return None

    def _process_image(self, image_data: bytes) -> bytes:
        """
        Process and optimize image for API usage

        Args:
            image_data: Raw image data

        Returns:
            Processed image data
        """
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Check file size
                original_size = len(image_data)
                max_size_mb = Config.MAX_PHOTO_SIZE_MB
                max_size_bytes = max_size_mb * 1024 * 1024

                # Resize if too large
                width, height = img.size
                max_dimension = Config.MAX_PHOTO_DIMENSION

                if width > max_dimension or height > max_dimension:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(max_dimension / width, max_dimension / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")

                # Compress image if needed
                quality = Config.COMPRESSION_QUALITY
                while True:
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    processed_data = buffer.getvalue()

                    if len(processed_data) <= max_size_bytes or quality <= 50:
                        break

                    # Reduce quality and try again
                    quality -= 10
                    logger.warning(f"Reducing JPEG quality to {quality}% to meet size limits")

                final_size = len(processed_data)
                if final_size != original_size:
                    reduction = ((original_size - final_size) / original_size) * 100
                    logger.info(f"Image size reduced by {reduction:.1f}% (from {original_size:,} to {final_size:,} bytes)")

                return processed_data

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            # Return original data if processing fails
            return image_data

    def move_photo_to_storage(self, photo_path: str, step: int, passed: bool, job_id: str) -> Optional[str]:
        """
        Move photo to appropriate storage directory based on verification result

        Args:
            photo_path: Current path to photo
            step: Installation step number
            passed: Whether verification passed
            job_id: Installation job ID

        Returns:
            New path to photo file
        """
        try:
            if not os.path.exists(photo_path):
                logger.error(f"Photo file not found: {photo_path}")
                return None

            # Determine target directory
            if passed:
                target_dir = os.path.join(Config.PHOTO_STORAGE_PATH, "approved")
            else:
                target_dir = os.path.join(Config.PHOTO_STORAGE_PATH, "rejected")

            os.makedirs(target_dir, exist_ok=True)

            # Generate new filename
            original_filename = os.path.basename(photo_path)
            status_prefix = "PASS" if passed else "FAIL"
            new_filename = f"{job_id}_step{step}_{status_prefix}_{original_filename}"
            new_path = os.path.join(target_dir, new_filename)

            # Move file
            os.rename(photo_path, new_path)
            logger.info(f"Moved photo to {new_path}")

            return new_path

        except Exception as e:
            logger.error(f"Error moving photo {photo_path}: {e}")
            return photo_path  # Return original path if move fails