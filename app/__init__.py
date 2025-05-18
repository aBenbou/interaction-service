# app/__init__.py
import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config
from app.log_config import configure_logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    configure_logging(app)
    app.config.from_object(config_class)
    
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif env == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    if not app.config.get('DATABASE_URL') and app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['DATABASE_URL'] = app.config.get('SQLALCHEMY_DATABASE_URI')
  
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    from app.api.interactions import interactions_bp
    from app.api.feedback import feedback_bp
    from app.api.analytics import analytics_bp
    from app.api.leaderboard import leaderboard_bp
    from app.api.swagger import swagger_bp
    from app.api.dimensions import dimensions_bp
    from app.api.validation import validation_bp
    from app.api.dataset import dataset_bp
    
    app.register_blueprint(interactions_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(swagger_bp)
    app.register_blueprint(dimensions_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(dataset_bp)
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "healthy"}, 200
    
    logger.info(f"Application initialized in {env} mode")
    return app