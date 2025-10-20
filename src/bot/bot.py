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
                # Check if it's a location share or photo
                if self._is_location_message(media_url):
                    return self._handle_location_message(from_number, media_url)
                else:
                    return self._handle_photo_message(from_number, media_url, media_id)
            elif message_body in ['START', 'NEW', 'HI', 'HELLO', 'HEY', 'HOLA']:
                if message_body in ['START', 'NEW']:
                    return self._handle_start_command(from_number)
                else:
                    return self._handle_greeting_command(from_number)
            elif message_body == 'STATUS':
                return self._handle_status_command(from_number)
            elif message_body == 'HELP':
                return self._handle_help_command(from_number)
            elif message_body == 'RESET':
                return self._handle_reset_command(from_number)
            elif message_body in ['SKIP', 'SKIP LOCATION', 'SKIP STEP']:
                return self._handle_skip_command(from_number, message_body)
            elif message_body == 'LIST':
                return self._handle_list_command(from_number)
            elif message_body.startswith('STRICTNESS'):
                return self._handle_strictness_command(from_number, message_body)
            else:
                # Check if it's a DR number or other text input
                return self._handle_text_input(from_number, message_body)

        except Exception as e:
            logger.error(f"Error processing message from {from_number}: {e}")
            return self._generate_error_response()

    def _handle_photo_message(self, from_number: str, media_url: str, media_id: str) -> str:
        """Handle incoming photo submission"""
        session = self.session_manager.get_session(from_number)
        
        if not session:
            return "❌ No active installation found. Type 'START' to begin."
            
        if session.current_step <= 0:
            if session.current_step == 0:
                return "📄 Please provide your DR number first before uploading photos."
            elif session.current_step == -1:
                return "📍 Please share your location first before uploading photos."
            else:
                return "❌ Please follow the installation steps in order."

        if session.current_step > 12:
            return self._generate_completion_message(session)

        try:
            # Download photo
            photo_path = self.message_handler.download_photo(media_url, session.current_job_id)
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

    def _handle_greeting_command(self, from_number: str) -> str:
        """Handle greeting commands with friendly welcome"""
        greeting_msg = (
            "👋 *Hello! Welcome to Fiber Installation Bot*\n\n"
            "I'm here to help you verify fiber installation photos step by step.\n\n"
            "*What would you like to do?*\n"
            "• Send `START` to begin a new installation\n"
            "• Send `STATUS` to check your progress\n"
            "• Send `HELP` for more information\n\n"
            "Ready when you are! 🚀"
        )
        return greeting_msg

    def _handle_reset_command(self, from_number: str) -> str:
        """Handle RESET command to start new installation"""
        # Reset any existing session to start fresh
        existing_session = self.session_manager.get_session(from_number)
        if existing_session:
            self.session_manager.reset_session(from_number)
        else:
            # Create new session
            self.session_manager.get_or_create_session(from_number)
        
        session = self.session_manager.get_session(from_number)
        return self._handle_start_command(from_number)
    
    def _handle_skip_command(self, from_number: str, skip_type: str) -> str:
        """Handle SKIP commands for admin/testing purposes"""
        session = self.session_manager.get_session(from_number)
        
        if not session:
            return "❌ No active installation found. Type 'START' to begin."
        
        logger.info(f"Admin SKIP command used by {from_number}: {skip_type}")
        
        if session.current_step == -1:  # Awaiting location
            # Skip location verification, move to Step 1
            self.session_manager.update_session(
                from_number,
                location_verified=True,
                location_data={"skipped": True, "timestamp": datetime.now().isoformat()},
                current_step=1
            )
            
            step1_name = STEP_NAMES.get(1, "Step 1")
            return (
                f"⚠️ *Location Verification SKIPPED* (Admin)\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"📄 DR Number: {session.dr_number}\n"
                f"📍 Location: ⚠️ Skipped for testing\n\n"
                f"📷 *Step 1: {step1_name}*\n"
                f"{STEP_REQUIREMENTS[1]}"
            )
        
        elif 1 <= session.current_step <= 12:  # Photo steps
            # Store current step info BEFORE completing
            current_step_number = session.current_step
            step_name = STEP_NAMES.get(current_step_number, f"Step {current_step_number}")
            
            # Mark step as completed with skip indicator
            self.session_manager.complete_step(from_number, current_step_number, "SKIPPED_FOR_TESTING")
            
            # Get updated session after completion
            updated_session = self.session_manager.get_session(from_number)
            
            next_step = updated_session.current_step
            if next_step <= 12:
                next_name = STEP_NAMES.get(next_step, f"Step {next_step}")
                return (
                    f"⚠️ *Step {current_step_number}: {step_name} - SKIPPED* (Admin)\n\n"
                    f"📊 Progress: {len(updated_session.completed_steps)}/12 steps\n\n"
                    f"📷 *Next Step: {next_name}*\n"
                    f"{STEP_REQUIREMENTS.get(next_step, 'Please send photo for this step.')}\n\n"
                    f"⚠️ Note: Step was skipped for testing purposes"
                )
            else:
                return (
                    f"⚠️ *Step {current_step_number}: {step_name} - SKIPPED* (Admin)\n\n"
                    f"🎉 *All steps completed!*\n"
                    f"📊 Final Progress: 12/12 steps (with skips)\n"
                    f"⚠️ Installation completed with admin skips for testing"
                )
        
        elif session.current_step == 0:  # Awaiting DR
            return (
                f"❌ Cannot skip DR number collection.\n\n"
                f"Please provide a valid DR number first."
            )
        
        else:
            return (
                f"❌ Nothing to skip at current stage.\n\n"
                f"Current step: {session.current_step}"
            )
    
    def _handle_start_command(self, from_number: str) -> str:
        """Handle START command to begin new installation"""
        session = self.session_manager.get_or_create_session(from_number)
        
        welcome_msg = (
            f"🔧 *New Fiber Installation Started*\n\n"
            f"📋 Job ID: {session.current_job_id}\n"
            f"👷 Agent: {session.agent_id}\n"
            f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"📄 *Please provide the DR Number*\n"
            f"Send the DR number for this installation (e.g., DR0123456)\n\n"
            f"💡 *Format*: DR followed by numbers (e.g., DR0123456)"
        )

        logger.info(f"Started new installation for {from_number}: {session.current_job_id}")
        return welcome_msg
    
    def _handle_list_command(self, from_number: str) -> str:
        """Handle LIST command to show all active installations"""
        try:
            session = self.session_manager.get_session(from_number)
            installations = self.session_manager.get_installation_list(from_number)
            
            if not installations:
                return "📋 No active installations found.\n\nType 'START' to begin a new installation."
            
            response_lines = ["📋 **Active Installations:**"]
            
            for install in installations:
                dr_number = install['dr_number']
                current_step = install['current_step']
                
                # Mark current active installation
                active_marker = " ← *Current*" if install.get('is_current', False) else ""
                
                # Determine status
                if current_step == 0:
                    status = "Waiting for DR number"
                elif current_step == -1:
                    status = "Waiting for location"
                elif install.get('status') == 'completed' or current_step > 12:
                    status = "✅ Complete"
                elif 1 <= current_step <= 12:
                    step_name = self._get_step_name(current_step)
                    progress = install.get('progress_percent', 0)
                    status = f"Step {current_step}/12 - {step_name} ({progress:.0f}%)"
                else:
                    status = "Unknown status"
                
                response_lines.append(f"• **DR {dr_number}**: {status}{active_marker}")
            
            response_lines.append(f"\nTotal: {len(installations)}/10 installations")
            response_lines.append("\nType a DR number to switch installations.")
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Error in list command: {str(e)}")
            return "Error retrieving installation list."
    
    def _handle_strictness_command(self, from_number: str, message: str) -> str:
        """Handle admin strictness adjustment commands"""
        from ..config import Config
        
        logger.info(f"Admin STRICTNESS command used by {from_number}: {message}")
        
        parts = message.split()
        
        if len(parts) == 1:  # Just 'STRICTNESS' - show current settings
            return (
                f"🔧 *AI Strictness Settings*\n\n"
                f"📊 **Current Settings:**\n"
                f"• Score Threshold: {Config.PASSING_SCORE_THRESHOLD}/10\n"
                f"• Completion Rate: {Config.PASSING_COMPLETION_RATE*100:.0f}%\n\n"
                f"🎯 **Preset Modes:**\n"
                f"• `STRICTNESS STRICT` - Threshold 9 (very strict)\n"
                f"• `STRICTNESS STANDARD` - Threshold 8 (standard)\n"
                f"• `STRICTNESS LENIENT` - Threshold 7 (more lenient)\n"
                f"• `STRICTNESS TESTING` - Threshold 5 (testing mode)\n\n"
                f"📝 **Custom:** `STRICTNESS SET 7.5`\n\n"
                f"💡 *Higher threshold = stricter evaluation*"
            )
        
        elif len(parts) >= 2:
            command = parts[1].upper()
            
            if command == 'STRICT':
                Config.PASSING_SCORE_THRESHOLD = 9
                return f"✅ Strictness set to **STRICT** (threshold: 9/10)\nOnly excellent photos will pass."
                
            elif command == 'STANDARD':
                Config.PASSING_SCORE_THRESHOLD = 8
                return f"✅ Strictness set to **STANDARD** (threshold: 8/10)\nGood quality photos will pass."
                
            elif command == 'LENIENT':
                Config.PASSING_SCORE_THRESHOLD = 7
                return f"✅ Strictness set to **LENIENT** (threshold: 7/10)\nAcceptable photos will pass."
                
            elif command == 'TESTING':
                Config.PASSING_SCORE_THRESHOLD = 5
                return f"⚠️ Strictness set to **TESTING** (threshold: 5/10)\nMost photos will pass - for testing only!"
                
            elif command == 'SET' and len(parts) >= 3:
                try:
                    new_threshold = float(parts[2])
                    if 0 <= new_threshold <= 10:
                        Config.PASSING_SCORE_THRESHOLD = new_threshold
                        return f"✅ Custom strictness set to **{new_threshold}/10**"
                    else:
                        return "❌ Threshold must be between 0 and 10"
                except ValueError:
                    return "❌ Invalid number. Use format: STRICTNESS SET 7.5"
        
        return (
            "❓ Invalid strictness command\n\n"
            "Use: STRICTNESS, STRICTNESS STRICT, STRICTNESS LENIENT, or STRICTNESS SET 7.5"
        )
    
    def _get_step_name(self, step_number: int) -> str:
        """Get the name for a step number"""
        return STEP_NAMES.get(step_number, f"Step {step_number}")

    def _handle_status_command(self, from_number: str) -> str:
        """Handle STATUS command to show current progress"""
        session = self.session_manager.get_session(from_number)

        if not session:
            return "❌ No active installation found. Type 'START' to begin."

        completed_count = len(session.completed_steps)
        progress_percent = (completed_count / 12) * 100
        
        # Build status based on current step
        if session.current_step == 0:
            return (
                f"📊 *Installation Status*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"⏳ Status: Awaiting DR Number\n\n"
                f"📄 *Next Step*: Please provide the DR number\n"
                f"Format: DR followed by 7 digits (e.g., DR0123456)"
            )
        elif session.current_step == -1:
            return (
                f"📊 *Installation Status*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"📄 DR Number: {session.dr_number}\n"
                f"⏳ Status: Awaiting Location Verification\n\n"
                f"📍 *Next Step*: Please share your current location\n"
                f"Use WhatsApp's location sharing feature"
            )

        if session.status == "completed":
            status_msg = (
                f"✅ *Installation Completed*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"✅ All 12 steps approved\n"
                f"🎉 Ready for activation!\n\n"
                f"Type 'NEW' to start another installation."
            )
        else:
            status_msg = (
                f"📊 *Installation Status*\n\n"
                f"📋 Job ID: {session.current_job_id}\n"
                f"📄 DR Number: {session.dr_number or 'Not provided'}\n"
                f"📍 Location: {'✅ Verified' if session.location_verified else '❌ Not verified'}\n"
                f"📈 Progress: {completed_count}/12 steps ({progress_percent:.0f}%)\n"
                f"🎯 Current Step: {session.current_step if session.current_step <= 12 else 'Completed'}\n\n"
            )

            if session.completed_steps:
                status_msg += "✅ *Completed Steps:*\n"
                for step_num in sorted(session.completed_steps.keys()):
                    step_name = STEP_NAMES.get(step_num, f"Step {step_num}")
                    status_msg += f"• {step_name}\n"

            if session.current_step <= 12:
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
            "• `LIST` - Show all active installations\n"
            "• `HELP` - Show this help message\n"
            "• `RESET` - Start over with new installation\n\n"
            "*Admin Commands:*\n"
            "• `SKIP` - Skip current step (testing)\n"
            "• `STRICTNESS` - View/adjust AI evaluation strictness\n\n"
            "*How to Use:*\n"
            "1. Send 'START' to begin installation\n"
            "2. Follow step-by-step photo instructions\n"
            "3. Send one photo at a time\n"
            "4. Wait for AI feedback before continuing\n"
            "5. Complete all 12 steps\n\n"
            "*Tips:*\n"
            "📸 Take clear, well-lit photos\n"
            "🎯 Follow specific requirements for each step\n"
            "⏱️ Wait 30 seconds for AI analysis\n"
            "🔄 Retake photos if feedback suggests improvements\n\n"
            "❓ Need help? Contact your supervisor"
        )
        return help_msg


    def _handle_unknown_command(self, from_number: str, message: str) -> str:
        """Handle unknown commands"""
        return (
            f"❓ Unknown command: '{message}'\n\n"
            "Type 'HELP' for available commands or send a photo for your current step.\n\n"
            "Available commands: START, STATUS, LIST, HELP, RESET"
        )

    def _format_verification_response(self, result: VerificationResult, session) -> str:
        """Format verification result into user-friendly WhatsApp message"""

        # Import Config for threshold info
        from ..config import Config
        
        if result.passed:
            # Success message
            emoji = "✅"
            status = "PASSED"
            response = f"{emoji} *Step {result.step}: {result.step_name} - {status}*\n\n"
            
            # Add score information
            response += f"📊 *Score: {result.score:.1f}/10* (Threshold: {Config.PASSING_SCORE_THRESHOLD}/10)\n\n"

            # Add positive feedback
            if result.score >= 9:
                response += "🌟 *Excellent work!* Photo quality is outstanding.\n"
            elif result.score >= 7:
                response += "✨ *Good job!* Photo meets quality standards.\n"

            # Progress update
            completed_count = len(session.completed_steps) + 1  # Include current step
            progress_percent = (completed_count / 12) * 100
            response += f"\n📊 *Progress: {completed_count}/12 steps completed ({progress_percent:.0f}%)*"

            # Next step guidance
            next_step = result.step + 1
            if next_step <= 12:
                next_name = STEP_NAMES.get(next_step, f"Step {next_step}")
                response += f"\n\n📷 *Next Step: {next_name}*\n"
                response += STEP_REQUIREMENTS.get(next_step, "Please send photo for this step.")
            else:
                response += "\n\n🎉 *All steps completed! Installation verified and ready for activation.*"

        else:
            # Failure message - SIMPLE & CLEAR for field agents
            emoji = "❌"
            status = "NEEDS RETAKE"
            response = f"{emoji} *Step {result.step}: {result.step_name} - {status}*\n\n"
            
            # Add score information to show why it failed
            response += f"📊 *Score: {result.score:.1f}/10* (Need: {Config.PASSING_SCORE_THRESHOLD}/10)\n\n"

            # Simplified issues - keep only the most important ones
            main_issues = result.issues[:3]  # Only top 3 issues
            if main_issues:
                response += "*What to fix:*\n"
                for issue in main_issues:
                    # Simplify technical language
                    simple_issue = self._simplify_issue_text(issue)
                    response += f"• {simple_issue}\n"
            
            # Simple, actionable recommendation
            simple_recommendation = self._simplify_recommendation(result.recommendation)
            response += f"\n💡 *Try this:*\n{simple_recommendation}\n\n"

            response += "📸 *Take the photo again and send it.*\n"
            response += f"📊 *Progress: {len(session.completed_steps)}/12 steps completed*"

        return response
    
    def _simplify_issue_text(self, issue: str) -> str:
        """Convert technical language to simple terms for field agents"""
        # Common replacements for technical terms
        replacements = {
            'ONT': 'white box',
            'fiber cable': 'cable',
            'pigtail screw': 'cable entry point',
            'duct entry': 'cable hole',
            'weather-proofing': 'weather protection',
            'penetration': 'hole',
            'installation area': 'work area',
            'equipment': 'devices',
            'visible and stable': 'clear and steady',
            'identifiable': 'clear',
            'insufficient': 'not enough',
            'not adequately documented': 'not clear enough',
            'strain relief': 'cable support'
        }
        
        simple_issue = issue.lower()
        for tech_term, simple_term in replacements.items():
            simple_issue = simple_issue.replace(tech_term.lower(), simple_term)
        
        # Capitalize first letter
        return simple_issue.capitalize()
    
    def _simplify_recommendation(self, recommendation: str) -> str:
        """Convert technical recommendations to simple actions"""
        # Common action simplifications
        simple_rec = recommendation.lower()
        
        # Key action words to make it more actionable
        if 'wider' in simple_rec or 'step back' in simple_rec:
            return "Step further back to fit more in the photo"
        elif 'closer' in simple_rec or 'close-up' in simple_rec:
            return "Get closer to show more detail"
        elif 'angle' in simple_rec:
            return "Try a different angle - move to the side or front"
        elif 'lighting' in simple_rec or 'light' in simple_rec:
            return "Take the photo in better light or use your phone's flash"
        elif 'clear' in simple_rec:
            return "Make sure the camera is focused and the image is sharp"
        elif 'visible' in simple_rec:
            return "Make sure you can clearly see what's needed in the photo"
        else:
            # Generic advice
            return "Take a clearer photo showing what's needed for this step"

    def _generate_completion_message(self, session) -> str:
        """Generate message for completed installation"""
        return (
            f"🎉 *Installation Already Completed!*\n\n"
            f"📋 Job ID: {session.current_job_id}\n"
            f"✅ All 12 steps successfully verified\n"
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

    def _handle_text_input(self, from_number: str, message_body: str) -> str:
        """Handle text input based on current session state"""
        session = self.session_manager.get_session(from_number)
        
        logger.info(f"Text input handler: from={from_number}, message={message_body}, session_exists={session is not None}")
        if session:
            logger.info(f"Session current_step: {session.current_step}, dr_number: {session.dr_number}")
        
        if not session:
            logger.info("No session found for text input")
            return self._handle_unknown_command(from_number, message_body)
            
        # Check if it's a DR number (for switching/creating installations)
        if self._is_valid_dr_number(message_body):
            logger.info("Routing DR number to DR input handler")
            return self._handle_dr_input(from_number, message_body)
        elif session.current_step == 0:  # Awaiting initial DR number
            logger.info("Routing to DR input handler for initial setup")
            return self._handle_dr_input(from_number, message_body)
        else:
            logger.info(f"Unknown text input for step {session.current_step}")
            return self._handle_unknown_command(from_number, message_body)
    
    def _handle_dr_input(self, from_number: str, dr_input: str) -> str:
        """Handle DR number input with multi-installation support"""
        dr_input = dr_input.strip().upper()
        
        # Validate DR number format
        if not self._is_valid_dr_number(dr_input):
            return (
                f"❌ *Invalid DR Number Format*\n\n"
                f"You entered: {dr_input}\n\n"
                f"Please use the correct format:\n"
                f"• DR followed by 4-10 digits\n"
                f"• Example: DR0123456\n\n"
                f"Please try again:"
            )
        
        # Use multi-installation switching
        session = self.session_manager.get_session(from_number)
        if not session:
            return "❌ No active session found. Please type START first."
            
        # Check if switching to existing installation
        is_existing = dr_input in session.installations or dr_input == session.current_dr
        
        # Switch to or create installation
        success = self.session_manager.switch_to_dr(from_number, dr_input)
        
        if not success:
            return (
                f"❌ *Installation Limit Reached*\n\n"
                f"You can only manage 10 installations at once.\n"
                f"Please complete or cancel existing installations first.\n\n"
                f"Type 'LIST' to see your active installations."
            )
            
        # Get updated session
        session = self.session_manager.get_session(from_number)
        
        if is_existing:
            # Switching to existing installation
            if session.current_step == -1:
                return (
                    f"🔄 *Switched to DR {dr_input}*\n\n"
                    f"📋 Job ID: {session.current_job_id}\n"
                    f"📍 *Location Verification Required*\n"
                    f"Please share your current location using WhatsApp's location sharing feature."
                )
            elif 1 <= session.current_step <= 12:
                from ..prompts import STEP_NAMES, STEP_REQUIREMENTS
                step_name = STEP_NAMES.get(session.current_step, f"Step {session.current_step}")
                progress = (len(session.completed_steps) / 12) * 100
                return (
                    f"🔄 *Switched to DR {dr_input}*\n\n"
                    f"📋 Job ID: {session.current_job_id}\n"
                    f"📈 Progress: {len(session.completed_steps)}/12 steps ({progress:.0f}%)\n\n"
                    f"📷 *Current Step: {step_name}*\n"
                    f"{STEP_REQUIREMENTS.get(session.current_step, 'Please send photo for this step.')}\n\n"
                    f"📍 Location: {'✅ Verified' if session.location_verified else '❌ Not verified'}"
                )
            else:
                return f"🎉 *Installation DR {dr_input} is completed!*"
        else:
            # New installation created
            return (
                f"✅ *New Installation Created*\n\n"
                f"📄 DR Number: {dr_input}\n"
                f"📋 Job ID: {session.current_job_id}\n\n"
                f"📍 *Location Verification Required*\n"
                f"Please share your current location using WhatsApp's location sharing feature:\n\n"
                f"1. Tap the attachment (📎) icon\n"
                f"2. Select 'Location'\n"
                f"3. Choose 'Share Live Location' or 'Send Your Current Location'\n\n"
                f"🎯 This ensures you're at the correct installation site."
            )
    
    def _handle_location_message(self, from_number: str, media_url: str) -> str:
        """Handle location sharing message"""
        session = self.session_manager.get_session(from_number)
        
        if not session or session.current_step != -1:
            return "❌ Location sharing not expected at this time. Please follow the installation steps."
        
        # Store location data and move to Step 1
        location_data = {"media_url": media_url, "timestamp": datetime.now().isoformat()}
        self.session_manager.update_session(
            from_number, 
            location_verified=True, 
            location_data=location_data, 
            current_step=1
        )
        
        response_msg = (
            f"✅ *Location Verified*\n\n"
            f"📍 Location recorded successfully\n"
            f"📄 DR Number: {session.dr_number}\n\n"
            f"📷 *Step 1: Property Frontage*\n"
            f"{STEP_REQUIREMENTS[1]}\n\n"
            f"Please send a clear photo showing the house/building with street number visible."
        )
        
        logger.info(f"Location verified for {from_number}, moving to Step 1")
        return response_msg
    
    def _is_location_message(self, media_url: str) -> bool:
        """Check if the media URL indicates a location share"""
        # WhatsApp location shares typically have specific URL patterns
        if not media_url:
            return False
        
        # More specific location detection - only consider it a location if URL explicitly contains location keywords
        location_indicators = ['location', 'maps', 'coordinates', 'lat=', 'lng=', 'geo:']
        
        # Check for explicit location indicators in the URL
        url_lower = media_url.lower()
        return any(indicator in url_lower for indicator in location_indicators)
    
    def _is_valid_dr_number(self, dr_input: str) -> bool:
        """Validate DR number format"""
        import re
        # DR followed by 4-10 digits (flexible for different formats)
        pattern = r'^DR\d{4,10}$'
        return bool(re.match(pattern, dr_input))

    def get_bot_stats(self) -> Dict:
        """Get bot statistics"""
        session_stats = self.session_manager.get_session_stats()

        return {
            "bot_status": "active",
            "total_sessions": session_stats["total_sessions"],
            "active_installations": session_stats["active_sessions"],
            "completed_installations": session_stats["completed_sessions"],
            "average_steps_per_session": session_stats["average_steps_completed"],
            "uptime": "active since start"
        }
