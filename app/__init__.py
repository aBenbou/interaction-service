import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Ensure the identity is always a string (UUID is converted to string)"""
        return str(user) if user is not None else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """We don't need to load user from database since Auth Service handles validation"""
        identity = jwt_data["sub"]
        return identity
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables if they don't exist
    try:
        with app.app_context():
            db.create_all()
            app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")
        app.logger.error("Application will continue startup, but database operations may fail")
    
    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.api.interactions import interactions_bp
    from app.api.prompts import prompts_bp
    from app.api.bookmarks import bookmarks_bp
    
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')
    app.register_blueprint(prompts_bp, url_prefix='/api')  # Routes include /interactions prefix
    app.register_blueprint(bookmarks_bp, url_prefix='/api')  # Routes include /interactions prefix

def configure_logging(app):
    """Configure logging for the application"""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure Flask logger
    app.logger.setLevel(log_level)
    
    # Create log directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Add rotating file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'interaction_service.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    
    # Set log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    app.logger.addHandler(file_handler)