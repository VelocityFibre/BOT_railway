from flask import Flask, request, Response, jsonify
import logging
import os
from typing import Dict, Any
from ..bot.bot import FiberInstallationBot
from ..config import Config
from ..db.database import save_installation, mark_resubmitted, test_connection

logger = logging.getLogger(__name__)

# Global bot instance
bot_instance = None

def get_bot() -> FiberInstallationBot:
    """Get or create bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = FiberInstallationBot()
    return bot_instance

def register_routes(app: Flask):
    """Register all API routes"""

    @app.route('/webhook', methods=['POST'])
    def whatsapp_webhook():
        """Handle incoming WhatsApp messages from Twilio"""
        try:
            # Extract message data from Twilio request
            from_number = request.values.get('From', '')
            message_body = request.values.get('Body', '')
            media_url = request.values.get('MediaUrl0', '')
            media_id = request.values.get('MediaId0', '')

            logger.info(f"WhatsApp webhook: from={from_number}, body={message_body[:50]}..., media={bool(media_url)}")

            # Process message through bot
            bot = get_bot()
            response_message = bot.process_message(
                from_number=from_number,
                message_body=message_body,
                media_url=media_url,
                media_id=media_id
            )

            # Format response for Twilio
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_message}</Message>
</Response>"""

            return Response(twiml_response, mimetype='text/xml')

        except Exception as e:
            logger.error(f"Error in WhatsApp webhook: {e}")
            # Return error message to user
            error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>❌ System error occurred. Please try again.</Message>
</Response>"""
            return Response(error_twiml, mimetype='text/xml')

    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get bot and system statistics"""
        try:
            bot = get_bot()
            stats = bot.get_bot_stats()

            # Add system stats
            stats.update({
                "api_status": "active",
                "environment": Config.FLASK_ENV,
                "openai_configured": bool(Config.OPENAI_API_KEY),
                "twilio_configured": bool(Config.TWILIO_ACCOUNT_SID),
                "photo_storage": Config.PHOTO_STORAGE_PATH,
                "max_session_duration": f"{Config.MAX_SESSION_DURATION_HOURS} hours"
            })

            return jsonify(stats)

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return jsonify({"error": "Failed to get statistics"}), 500

    @app.route('/test', methods=['POST'])
    def test_verification():
        """Test photo verification (for development)"""
        if Config.FLASK_ENV != 'development':
            return jsonify({"error": "Test endpoint only available in development"}), 403

        try:
            # Check if file was uploaded
            if 'photo' not in request.files:
                return jsonify({"error": "No photo file provided"}), 400

            photo = request.files['photo']
            step = int(request.form.get('step', 1))

            if photo.filename == '':
                return jsonify({"error": "No photo file selected"}), 400

            # Save photo temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                photo.save(temp_file.name)
                temp_path = temp_file.name

            # Verify photo
            bot = get_bot()
            result = bot.verifier.verify_step(temp_path, step)

            # Clean up
            os.unlink(temp_path)

            return jsonify({
                "step": result.step,
                "step_name": result.step_name,
                "passed": result.passed,
                "score": result.score,
                "issues": result.issues,
                "confidence": result.confidence,
                "recommendation": result.recommendation
            })

        except Exception as e:
            logger.error(f"Error in test verification: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/sessions', methods=['GET'])
    def get_sessions():
        """Get active sessions (admin endpoint)"""
        if Config.FLASK_ENV != 'development':
            return jsonify({"error": "Sessions endpoint only available in development"}), 403

        try:
            bot = get_bot()
            sessions = bot.session_manager.get_active_sessions()

            session_data = []
            for session in sessions:
                session_data.append({
                    "agent_id": session.agent_id,
                    "phone_number": session.phone_number,
                    "job_id": session.current_job_id,
                    "current_step": session.current_step,
                    "completed_steps": len(session.completed_steps),
                    "session_start": session.session_start.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "status": session.status
                })

            return jsonify({
                "active_sessions": len(session_data),
                "sessions": session_data
            })

        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/config', methods=['GET'])
    def get_config():
        """Get configuration info (sanitized)"""
        if Config.FLASK_ENV != 'development':
            return jsonify({"error": "Config endpoint only available in development"}), 403

        try:
            config_info = {
                "environment": Config.FLASK_ENV,
                "photo_storage": Config.PHOTO_STORAGE_PATH,
                "max_photo_size_mb": Config.MAX_PHOTO_SIZE_MB,
                "compression_quality": Config.COMPRESSION_QUALITY,
                "max_photo_dimension": Config.MAX_PHOTO_DIMENSION,
                "max_photos_per_hour": Config.MAX_PHOTOS_PER_HOUR,
                "max_session_duration_hours": Config.MAX_SESSION_DURATION_HOURS,
                "total_installation_steps": Config.TOTAL_INSTALLATION_STEPS,
                "passing_score_threshold": Config.PASSING_SCORE_THRESHOLD,
                "passing_completion_rate": Config.PASSING_COMPLETION_RATE,
                "openai_configured": bool(Config.OPENAI_API_KEY),
                "twilio_configured": all([
                    Config.TWILIO_ACCOUNT_SID,
                    Config.TWILIO_AUTH_TOKEN,
                    Config.WHATSAPP_NUMBER
                ])
            }

            return jsonify(config_info)

        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/admin/strictness', methods=['GET', 'POST'])
    def admin_strictness():
        """Admin endpoint to view/adjust AI strictness settings"""
        if Config.FLASK_ENV != 'development':
            return jsonify({"error": "Admin endpoint only available in development"}), 403
        
        if request.method == 'GET':
            # Return current strictness settings
            return jsonify({
                "current_settings": {
                    "passing_score_threshold": Config.PASSING_SCORE_THRESHOLD,
                    "passing_completion_rate": Config.PASSING_COMPLETION_RATE,
                    "minimum_passed_steps": 10,  # Currently hardcoded
                    "total_steps": 12
                },
                "description": {
                    "passing_score_threshold": "Minimum score (0-10) for individual photos to pass",
                    "passing_completion_rate": "Minimum percentage (0-1) of steps that must be completed",
                    "minimum_passed_steps": "Minimum number of steps that must pass for overall approval"
                },
                "recommendations": {
                    "strict": {"passing_score_threshold": 9, "description": "Very strict - only excellent photos pass"},
                    "standard": {"passing_score_threshold": 8, "description": "Standard quality - good photos pass"},
                    "lenient": {"passing_score_threshold": 7, "description": "More lenient - acceptable photos pass"},
                    "testing": {"passing_score_threshold": 5, "description": "Testing mode - most photos pass"}
                }
            })
        
        elif request.method == 'POST':
            try:
                # Update strictness settings
                data = request.get_json()
                
                if 'passing_score_threshold' in data:
                    new_threshold = float(data['passing_score_threshold'])
                    if 0 <= new_threshold <= 10:
                        Config.PASSING_SCORE_THRESHOLD = new_threshold
                        logger.info(f"Updated passing score threshold to {new_threshold}")
                    else:
                        return jsonify({"error": "passing_score_threshold must be between 0 and 10"}), 400
                
                if 'passing_completion_rate' in data:
                    new_rate = float(data['passing_completion_rate'])
                    if 0 <= new_rate <= 1:
                        Config.PASSING_COMPLETION_RATE = new_rate
                        logger.info(f"Updated passing completion rate to {new_rate}")
                    else:
                        return jsonify({"error": "passing_completion_rate must be between 0 and 1"}), 400
                
                return jsonify({
                    "success": True,
                    "updated_settings": {
                        "passing_score_threshold": Config.PASSING_SCORE_THRESHOLD,
                        "passing_completion_rate": Config.PASSING_COMPLETION_RATE
                    },
                    "message": "Strictness settings updated successfully"
                })
                
            except Exception as e:
                logger.error(f"Error updating strictness settings: {e}")
                return jsonify({"error": str(e)}), 500

    # ==================== NEW ENDPOINTS FOR NEON INTEGRATION ====================

    @app.route('/api/submit-installation', methods=['POST'])
    def submit_installation():
        """
        Submit a completed installation to the database
        Called when agent completes all 12 photos via WhatsApp

        Request body:
        {
            "drop_number": "DR12345678",
            "contractor_number": "+27640412391",
            "project_name": "Velo Test"
        }
        """
        try:
            data = request.get_json()

            if not data or 'drop_number' not in data:
                return jsonify({"error": "drop_number is required"}), 400

            drop_number = data['drop_number']
            contractor_number = data.get('contractor_number', 'Unknown')
            project_name = data.get('project_name', 'Velo Test')

            logger.info(f"📥 Received installation submission: {drop_number} from {contractor_number}")

            # Save to database
            result = save_installation(drop_number, contractor_number, project_name)

            if result['success']:
                logger.info(f"✅ Installation {drop_number} saved successfully")
                return jsonify(result), 200
            else:
                logger.error(f"❌ Failed to save installation {drop_number}: {result.get('error')}")
                return jsonify(result), 500

        except Exception as e:
            logger.error(f"❌ Error in submit_installation: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/send', methods=['POST'])
    def send_whatsapp():
        """
        Send WhatsApp message to a contractor
        Called by Next.js dashboard when marking drop as incomplete

        Request body:
        {
            "to": "+27640412391" or "whatsapp:+27640412391",
            "message": "Your drop DR12345678 is incomplete..."
        }
        """
        try:
            # Verify API key
            api_key = request.headers.get('X-API-Key')
            expected_key = os.getenv('BRIDGE_API_KEY')

            if expected_key and api_key != expected_key:
                logger.warning(f"⚠️ Invalid API key attempt from {request.remote_addr}")
                return jsonify({"error": "Unauthorized"}), 401

            data = request.get_json()

            if not data or 'to' not in data or 'message' not in data:
                return jsonify({"error": "Both 'to' and 'message' are required"}), 400

            to_number = data['to']
            message = data['message']

            # Ensure number has whatsapp: prefix for Twilio
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"

            logger.info(f"📤 Sending WhatsApp message to {to_number}")

            # Send via Twilio
            from twilio.rest import Client

            client = Client(
                Config.TWILIO_ACCOUNT_SID,
                Config.TWILIO_AUTH_TOKEN
            )

            twilio_message = client.messages.create(
                from_=f"whatsapp:{Config.WHATSAPP_NUMBER}",
                to=to_number,
                body=message
            )

            logger.info(f"✅ WhatsApp message sent successfully: SID={twilio_message.sid}")

            return jsonify({
                "success": True,
                "message_sid": twilio_message.sid,
                "to": to_number,
                "status": twilio_message.status
            }), 200

        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/resubmit', methods=['POST'])
    def handle_resubmit():
        """
        Mark a drop as resubmitted
        Called when agent sends "DR12345678 DONE" via WhatsApp

        Request body:
        {
            "drop_number": "DR12345678"
        }
        """
        try:
            data = request.get_json()

            if not data or 'drop_number' not in data:
                return jsonify({"error": "drop_number is required"}), 400

            drop_number = data['drop_number']

            logger.info(f"🔄 Received resubmission for: {drop_number}")

            # Update database
            result = mark_resubmitted(drop_number)

            if result['success']:
                logger.info(f"✅ Drop {drop_number} marked as resubmitted")
                return jsonify(result), 200
            else:
                logger.error(f"❌ Failed to mark {drop_number} as resubmitted: {result.get('error')}")
                return jsonify(result), 500

        except Exception as e:
            logger.error(f"❌ Error in handle_resubmit: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/db/test', methods=['GET'])
    def test_database():
        """Test database connection"""
        success, message = test_connection()

        if success:
            return jsonify({
                "success": True,
                "message": message,
                "database": "Neon PostgreSQL"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 500
