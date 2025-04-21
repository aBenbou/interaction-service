# app/config.py
import os
from datetime import timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("Environment variables:")
logger.info(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
logger.info(f"SQLALCHEMY_DATABASE_URI: {os.environ.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
logger.info(f"AUTH_SERVICE_URL: {os.environ.get('AUTH_SERVICE_URL', 'Not set')}")
logger.info(f"USER_SERVICE_URL: {os.environ.get('USER_SERVICE_URL', 'Not set')}")
logger.info(f"MODEL_SERVICE_URL: {os.environ.get('MODEL_SERVICE_URL', 'Not set')}")

class Config:
    """Base configuration."""
    
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database - prioritize SQLALCHEMY_DATABASE_URI over DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@db:5432/interaction_service'
    )
    
    # Handle potential "postgres://" format in DATABASE_URL (convert to "postgresql://")
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Print the actual value that will be used
    logger.info(f"Final SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Microservice URLs
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth_api:5000')
    AUTH_SERVICE_TOKEN = os.environ.get('AUTH_SERVICE_TOKEN', 'placeholder-token')
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://profile_api:5001')
    MODEL_SERVICE_URL = os.environ.get('MODEL_SERVICE_URL', 'http://model-manager:8000')
    
    # Service API key for internal service-to-service communication
    SERVICE_API_KEY = os.environ.get('SERVICE_API_KEY', 'dev-service-key-change-in-production')
    
    # Auth Service settings
    AUTH_SERVICE_ROLE_NAME = os.environ.get('AUTH_SERVICE_ROLE_NAME', 'interaction_admin')
    
    # Map roles to permissions for local checking
    ROLE_PERMISSIONS = {
        'admin': ['interaction:read', 'interaction:write', 'feedback:read', 'feedback:write', 'validation:read', 'validation:write', 'dataset:read', 'dataset:write'],
        'validator': ['interaction:read', 'feedback:read', 'feedback:write', 'validation:read', 'validation:write'],
        'user': ['interaction:read', 'interaction:write', 'feedback:read', 'feedback:write']
    }
    
    # Message broker
    MESSAGE_BROKER_URL = os.environ.get('MESSAGE_BROKER_URL', None)
    
    # Timeouts
    SERVICE_TIMEOUT = 10  # seconds
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # Longer expiration for development

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 
        'postgresql://postgres:postgres@db:5432/interaction_service_test'
    )
    
    # Handle potential "postgres://" format in TEST_DATABASE_URL
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Mock service URLs or use test doubles
    AUTH_SERVICE_URL = None
    USER_SERVICE_URL = None
    MODEL_SERVICE_URL = None
    
    # Set environment variable for mocks
    os.environ['TESTING'] = 'true'
    
    # Test user IDs
    ADMIN_USERS = os.environ.get('ADMIN_USERS', '11111111-1111-1111-1111-111111111111')
    VALIDATOR_USERS = os.environ.get('VALIDATOR_USERS', '22222222-2222-2222-2222-222222222222')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # In production, these must be set from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SERVICE_API_KEY = os.environ.get('SERVICE_API_KEY')
    
    # Ensure SSL for database in production - handle potential "postgres://" format
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Stricter security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Error reporting
    PROPAGATE_EXCEPTIONS = True