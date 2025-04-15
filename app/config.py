import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:postgres@interaction_db:5432/interaction_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_TOKEN_LOCATION = ['headers']
    
    # Services
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_api:5000')
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://profile_api:5001')
    MODEL_SERVICE_URL = os.getenv('MODEL_SERVICE_URL', 'http://model_api:8000')
    
    # Event Bus
    EVENT_BUS_ENABLED = os.getenv('EVENT_BUS_ENABLED', 'False').lower() in ('true', '1', 't')
    EVENT_BUS_TYPE = os.getenv('EVENT_BUS_TYPE', 'http')
    EVENT_BUS_URL = os.getenv('EVENT_BUS_URL', 'http://event_bus:8080/events')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    AUTH_SERVICE_URL = 'http://localhost:5000'
    USER_SERVICE_URL = 'http://localhost:5001'
    MODEL_SERVICE_URL = 'http://localhost:8000'
    EVENT_BUS_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Override these with environment variables in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

# Config dictionary to map environment names to config classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}