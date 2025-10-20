from flask import Flask, request, Response, jsonify
import logging
import os
from .routes import register_routes
from ..config import Config

def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # Setup logging
    setup_logging(app)

    # Register routes
    register_routes(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "fiber-photo-verification",
            "version": "1.0.0"
        })

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "service": "Fiber Installation Photo Verification",
            "version": "1.0.0",
            "endpoints": {
                "webhook": "/webhook",
                "health": "/health",
                "stats": "/stats"
            }
        })

    return app

def setup_logging(app):
    """Configure logging for the application"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper())
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logs directory if it doesn't exist
    log_file = Config.LOG_FILE
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
            logging.StreamHandler()  # Always log to console
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {Config.LOG_LEVEL}")

# Create app instance for deployment
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_ENV == 'development'
    )