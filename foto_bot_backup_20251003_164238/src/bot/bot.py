import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from ..config import Config
from ..storage.sessions import SessionManager
from ..verifier import FiberInstallationVerifier, VerificationResult
from ..prompts import STEP_NAMES, STEP_REQUIREMENTS
from .handlers import MessageHandler

logger = logging.getLogger(__name__)

class FiberInstallationBot:
    """WhatsApp bot for fiber installation photo verification"""

    def __init__(self):
        """Initialize bot with dependencies"""
        self.session_manager = SessionManager()
        self.verifier = FiberInstallationVerifier()
        self.message_handler = MessageHandler()

    def process_message(self, from_number: str, message_body: str,
                       media_url: Optional[str] = None,
                       media_id: Optional[str] = None) -> str:
        """
        Process incoming WhatsApp message

        Args:
            from_number: Sender's phone number
            message_body: Message text content
            media_url: URL of media (photo) if provided
            media_id: Media ID for downloading

        Returns:
            Response message to send back
        """
        try:
            # Normalize phone number
            from_number = self._normalize_phone_number(from_number)
            message_body = message_body.strip().upper()

            logger.info(f"Processing message from {from_number}: {message_body[:50]}...")

            # Handle different message types
            if media_url:
                return self._handle_photo_message(from_number, media_url, media_id)
            elif message_body in ['START', 'NEW']:
                return self._handle_start_command(from_number)
            elif message_body == 'STATUS':
                return self._handle_status_command(from_number)
            elif message_body == 'HELP':
                return self._handle_help_command(from_number)
            elif message_body == 'RESET':
                return self._handle_reset_command(from_number)
            else:
                return self._handle_unknown_command(from_number, message_body)

        except Exception as e:
            logger.error(f"Error processing message from {from_number}: {e}")
            return self._generate_error_response()

    def _handle_photo_message(self, from_number: str, media_url: str, media_id: str) -> str:
        """Handle incoming photo submission"""
        session = self.session_manager.get_or_create_session(from_number)

        if session.current_step > 14:
            return self._generate_completion_message(session)

        try:
            # Download photo
            photo_path = self.message_handler.download_photo(media_id, session.current_job_id)
            if not photo_path:
                return "❌ Error downloading your photo. Please try sending it again."

            # Verify photo
            result = self.verifier.verify_step(photo_path, session.current_step)

            # Generate response
            response = self._format_verification_response(result, session)

            # Update session if passed
            if result.passed:
                self.session_manager.complete_step(from_number, session.current_step, photo_path)
                logger.info(f"Step {session.current_step} passed for {from_number}")
            else:
                logger.info(f"Step {session.current_step} failed for {from_number}: {result.issues}")

            return response

        except Exception as e:
            logger.error(f"Error handling photo for {from_number}: {e}")
            return "❌ Error processing your photo. Please try again."

    def _handle_start_command(self, from_number: str) -> str:
        """Handle START command to begin new installation"""
        session = self.session_manager.get_or_create_session(from_number)

        welcome_msg = (
            f"🔧 *New Fiber Installation Started*\n\n"
            f"📋 Job ID: {session.current_job_id}\n"
            f"👷 Agent: {session.agent_id}\n"
            f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"📷 *Step 1: Property Frontage*\n"
            f"{STEP_REQUIREMENTS[1]}\n\n"
            f"Please send a clear photo showing the house/building with street number visible."
        )

        logger.info(f"Started new installation for {from_number}: {session.current_job_id}")
        return welcome_msg

    def _handle_status_command(self, from_number: str) -> str:
        """Handle STATUS command to show current progress"""
        session = self.session_manager.get_session(from_number)

        if not session:
            return "❌ No active installation found. Type 'START' to begin."

        completed_count = len(session.completed_steps)
        progress_percent = (completed_count / 14) * 100

        if session.status == "completed":
            status_msg = (
                f"✅ *Installation Completed*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"✅ All 14 steps approved\n"
                f"🎉 Ready for activation!\n\n"
                f"Type 'NEW' to start another installation."
            )
        else:
            status_msg = (
                f"📊 *Installation Status*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"📍 Progress: {completed_count}/14 steps ({progress_percent:.0f}%)\n"
                f"🎯 Current Step: {session.current_step if session.current_step <= 14 else 'Completed'}\n\n"
            )

            if session.completed_steps:
                status_msg += "✅ *Completed Steps:*\n"
                for step_num in sorted(session.completed_steps.keys()):
                    step_name = STEP_NAMES.get(step_num, f"Step {step_num}")
                    status_msg += f"• {step_name}\n"

            if session.current_step <= 14:
                next_step_name = STEP_NAMES.get(session.current_step, f"Step {session.current_step}")
                status_msg += f"\n📷 *Next: {next_step_name}*\n"
                status_msg += STEP_REQUIREMENTS.get(session.current_step, "Please send photo for this step.")

        return status_msg

    def _handle_help_command(self, from_number: str) -> str:
        """Handle HELP command"""
        help_msg = (
            "🔧 *Fiber Installation Bot Help*\n\n"
            "*Available Commands:*\n"
            "• `START` or `NEW` - Begin new installation\n"
            "• `STATUS` - Check current progress\n"
            "• `HELP` - Show this help message\n"
            "• `RESET` - Start over with new installation\n\n"
            "*How to Use:*\n"
            "1. Send 'START' to begin installation\n"
            "2. Follow step-by-step photo instructions\n"
            "3. Send one photo at a time\n"
            "4. Wait for AI feedback before continuing\n"
            "5. Complete all 14 steps\n\n"
            "*Tips:*\n"
            "📸 Take clear, well-lit photos\n"
            "🎯 Follow specific requirements for each step\n"
            "⏱️ Wait 30 seconds for AI analysis\n"
            "🔄 Retake photos if feedback suggests improvements\n\n"
            "❓ Need help? Contact your supervisor"
        )
        return help_msg

    def _handle_reset_command(self, from_number: str) -> str:
        """Handle RESET command to start new installation"""
        self.session_manager.reset_session(from_number)
        return self._handle_start_command(from_number)

    def _handle_unknown_command(self, from_number: str, message: str) -> str:
        """Handle unknown commands"""
        return (
            f"❓ Unknown command: '{message}'\n\n"
            "Type 'HELP' for available commands or send a photo for your current step.\n\n"
            "Available commands: START, STATUS, HELP, RESET"
        )

    def _format_verification_response(self, result: VerificationResult, session) -> str:
        """Format verification result into user-friendly WhatsApp message"""

        if result.passed:
            # Success message
            emoji = "✅"
            status = "PASSED"
            response = f"{emoji} *Step {result.step}: {result.step_name} - {status}*\n\n"

            # Add positive feedback
            if result.score >= 9:
                response += "🌟 *Excellent work!* Photo quality is outstanding.\n"
            elif result.score >= 7:
                response += "✨ *Good job!* Photo meets quality standards.\n"

            # Progress update
            completed_count = len(session.completed_steps) + 1  # Include current step
            progress_percent = (completed_count / 14) * 100
            response += f"\n📊 *Progress: {completed_count}/14 steps completed ({progress_percent:.0f}%)*"

            # Next step guidance
            next_step = result.step + 1
            if next_step <= 14:
                next_name = STEP_NAMES.get(next_step, f"Step {next_step}")
                response += f"\n\n📷 *Next Step: {next_name}*\n"
                response += STEP_REQUIREMENTS.get(next_step, "Please send photo for this step.")
            else:
                response += "\n\n🎉 *All steps completed! Installation verified and ready for activation.*"

        else:
            # Failure message
            emoji = "❌"
            status = "NEEDS RETAKE"
            response = f"{emoji} *Step {result.step}: {result.step_name} - {status}*\n\n"

            response += "*Issues Found:*\n"
            for issue in result.issues[:5]:  # Limit to 5 issues
                response += f"• {issue}\n"

            if len(result.issues) > 5:
                response += f"• ... and {len(result.issues) - 5} more issues\n"

            response += f"\n📸 *Recommendation:*\n{result.recommendation}\n\n"

            response += "🔄 *Please retake this photo and send it again.*\n"
            response += f"📊 *Progress: {len(session.completed_steps)}/14 steps completed*"

        return response

    def _generate_completion_message(self, session) -> str:
        """Generate message for completed installation"""
        return (
            f"🎉 *Installation Already Completed!*\n\n"
            f"📋 Job ID: {session.current_job_id}\n"
            f"✅ All 14 steps successfully verified\n"
            f"🚀 Ready for service activation\n\n"
            f"Type 'NEW' to start another installation."
        )

    def _generate_error_response(self) -> str:
        """Generate error response message"""
        return (
            "❌ *System Error*\n\n"
            "We encountered an error processing your request. "
            "Please try again in a moment.\n\n"
            "If problems persist, contact your supervisor."
        )

    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number format"""
        # Remove WhatsApp prefix and standardize format
        normalized = phone_number.replace('whatsapp:', '').replace('+', '')
        return f"+{normalized}" if not normalized.startswith('+') else normalized

    def get_bot_stats(self) -> Dict:
        """Get bot statistics"""
        session_stats = self.session_manager.get_session_stats()

        return {
            "bot_status": "active",
            "total_sessions": session_stats["total_sessions"],
            "active_installations": session_stats["active_sessions"],
            "completed_installations": session_stats["completed_installations"],
            "average_steps_per_session": session_stats["average_steps_completed"],
            "uptime": "active since start"
        }