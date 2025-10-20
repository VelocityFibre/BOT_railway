#!/usr/bin/env python3
"""
Main entry point for Fiber Installation Photo Verification System

Usage:
    python app.py

Environment Variables:
    FLASK_ENV=development|production
    OPENAI_API_KEY=your-openai-key
    TWILIO_ACCOUNT_SID=your-twilio-sid
    TWILIO_AUTH_TOKEN=your-twilio-token
    WHATSAPP_NUMBER=your-whatsapp-number
"""

import os
import logging
from src.api.app import create_app

def main():
    """Main application entry point"""
    # Set environment
    env = os.getenv('FLASK_ENV', 'development')

    # Create Flask app
    app = create_app()

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Fiber Photo Verification Bot in {env} mode")

    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))

    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=env == 'development'
    )

if __name__ == '__main__':
    main()