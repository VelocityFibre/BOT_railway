import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Storage Configuration
    PHOTO_STORAGE_PATH = os.getenv('PHOTO_STORAGE_PATH', './data/photos')
    SESSION_FILE_PATH = os.getenv('SESSION_FILE_PATH', './data/sessions.json')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/verification.log')

    # Rate Limiting
    MAX_PHOTOS_PER_HOUR = int(os.getenv('MAX_PHOTOS_PER_HOUR', '10'))
    MAX_SESSION_DURATION_HOURS = int(os.getenv('MAX_SESSION_DURATION_HOURS', '24'))

    # Photo Verification Configuration
    MAX_PHOTO_SIZE_MB = 10
    COMPRESSION_QUALITY = 85
    MAX_PHOTO_DIMENSION = 1024

    # Installation Steps Configuration
    TOTAL_INSTALLATION_STEPS = 14
    PASSING_SCORE_THRESHOLD = 8
    PASSING_COMPLETION_RATE = 0.85

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}