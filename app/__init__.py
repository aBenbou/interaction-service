# app/__init__.py
import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config=None):
    """
    Application factory function.
    
    Args:
        config: Configuration object or string
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Override with environment-specific configuration
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif env == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Override with custom config if provided
    if config:
        if isinstance(config, str):
            app.config.from_object(config)
        else:
            app.config.from_mapping(config)
    
    # Set DATABASE_URL if only SQLALCHEMY_DATABASE_URI is available
    if not app.config.get('DATABASE_URL') and app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['DATABASE_URL'] = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api.interactions import interactions_bp
    from app.api.feedback import feedback_bp
    from app.api.dimensions import dimensions_bp
    from app.api.validation import validation_bp
    from app.api.dataset import dataset_bp
    
    app.register_blueprint(interactions_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(dimensions_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(dataset_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {str(error)}")
        return {"error": "Internal server error"}, 500
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "healthy"}, 200
    
    logger.info(f"Application initialized in {env} mode")
    return app