# Save as manual_migration.py
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def run_manual_migration():
    try:
        # Create a minimal Flask app with the same database config
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        
        # Define basic tables - we'll manually create the core tables needed
        print("Setting up core tables...")
        with app.app_context():
            # Execute raw SQL to create basic tables
            db.engine.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id UUID PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                model_id VARCHAR(100) NOT NULL,
                model_version VARCHAR(50) NOT NULL,
                endpoint_name VARCHAR(100) NOT NULL,
                session_id UUID NOT NULL,
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                status VARCHAR(20) NOT NULL,
                interaction_metadata JSONB NOT NULL DEFAULT '{}'
            );
            
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL
            );
            
            INSERT INTO alembic_version (version_num) VALUES ('initial_setup');
            """)
            
            print("Core tables created successfully")
        return True
    except Exception as e:
        print(f"Manual migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if run_manual_migration():
        sys.exit(0)
    else:
        sys.exit(1)