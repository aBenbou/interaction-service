#!/bin/bash
# This script uses Unix-style line endings (LF only, not CRLF)
# This script must be run in a Unix-compatible environment
set -e

# Debug environment variables
echo "DEBUGGING ENVIRONMENT VARIABLES:"
echo "DATABASE_URL: $DATABASE_URL"
echo "SQLALCHEMY_DATABASE_URI: $SQLALCHEMY_DATABASE_URI"
echo "AUTH_SERVICE_URL: $AUTH_SERVICE_URL"
echo "USER_SERVICE_URL: $USER_SERVICE_URL"
echo "MODEL_SERVICE_URL: $MODEL_SERVICE_URL"
env | grep -E "DATABASE|SQL"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL is ready!"

# Service checks (optional)
echo "Checking for services..."
for service in "auth_api:5000" "profile_api:5001" "model-manager:8000"; do
  host=$(echo $service | cut -d: -f1)
  port=$(echo $service | cut -d: -f2)
  if nc -z $host $port 2>/dev/null; then
    echo "$host is available"
  else
    echo "Warning: $host not detected. Proceeding anyway."
  fi
done

# IMPROVED DATABASE SETUP SECTION
echo "Setting up database..."

# Create a simple Python script for database operations
cat > /tmp/db_setup.py << 'EOF'
import psycopg2
import os
import sys
from uuid import uuid4
from datetime import datetime

# Connect to database with autocommit mode from the start
try:
    conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
    conn = psycopg2.connect(conn_string, autocommit=True)
    cursor = conn.cursor()
    print("Connected to database successfully")
except Exception as e:
    print(f"Database connection error: {e}")
    sys.exit(1)

try:
    # Check if tables already exist
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'interactions')")
    has_tables = cursor.fetchone()[0]

    if has_tables:
        print("Tables already exist, skipping database setup")
        sys.exit(0)

    # Check and drop alembic_version if it exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
    has_alembic = cursor.fetchone()[0]
    if has_alembic:
        cursor.execute('DROP TABLE alembic_version')
        print('Dropped alembic_version table')

    # Check if types already exist
    cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_status_enum')")
    has_status_enum = cursor.fetchone()[0]

    if not has_status_enum:
        cursor.execute("CREATE TYPE interaction_status_enum AS ENUM ('ACTIVE', 'COMPLETED', 'ABANDONED')")
        print("Created interaction_status_enum type")

    cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'feedback_status_enum')")
    has_feedback_enum = cursor.fetchone()[0]

    if not has_feedback_enum:
        cursor.execute("CREATE TYPE feedback_status_enum AS ENUM ('PENDING', 'VALIDATED', 'REJECTED')")
        print("Created feedback_status_enum type")

    # Create core tables
    print("Creating tables...")

    cursor.execute("""
    CREATE TABLE interactions (
        id UUID PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        model_id VARCHAR(100) NOT NULL,
        model_version VARCHAR(50) NOT NULL,
        endpoint_name VARCHAR(100) NOT NULL,
        session_id UUID NOT NULL,
        started_at TIMESTAMP NOT NULL,
        ended_at TIMESTAMP,
        status interaction_status_enum NOT NULL,
        interaction_metadata JSONB NOT NULL DEFAULT '{}'
    )
    """)
    print("Created interactions table")

    cursor.execute("""
    CREATE TABLE prompts (
        id UUID PRIMARY KEY,
        interaction_id UUID NOT NULL REFERENCES interactions(id),
        content TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        submitted_at TIMESTAMP NOT NULL,
        context JSONB NOT NULL DEFAULT '{}',
        UNIQUE(interaction_id, sequence_number)
    )
    """)
    print("Created prompts table")

    cursor.execute("""
    CREATE TABLE responses (
        id UUID PRIMARY KEY,
        prompt_id UUID NOT NULL UNIQUE REFERENCES prompts(id),
        content TEXT NOT NULL,
        generated_at TIMESTAMP NOT NULL,
        processing_time_ms INTEGER,
        tokens_used INTEGER,
        model_endpoint VARCHAR(100) NOT NULL
    )
    """)
    print("Created responses table")

    cursor.execute("""
    CREATE TABLE evaluation_dimensions (
        id UUID PRIMARY KEY,
        model_id VARCHAR(100) NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        created_by UUID NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(model_id, name)
    )
    """)
    print("Created evaluation_dimensions table")

    cursor.execute("""
    CREATE TABLE feedback (
        id UUID PRIMARY KEY,
        response_id UUID NOT NULL REFERENCES responses(id),
        user_id VARCHAR(36) NOT NULL,
        overall_comment TEXT,
        submitted_at TIMESTAMP NOT NULL,
        status feedback_status_enum NOT NULL DEFAULT 'PENDING'
    )
    """)
    print("Created feedback table")

    cursor.execute("""
    CREATE TABLE dimension_ratings (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL REFERENCES feedback(id),
        dimension_id UUID NOT NULL REFERENCES evaluation_dimensions(id),
        score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
        justification TEXT,
        correct_response TEXT,
        UNIQUE(feedback_id, dimension_id)
    )
    """)
    print("Created dimension_ratings table")

    cursor.execute("""
    CREATE TABLE validation_records (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL UNIQUE REFERENCES feedback(id),
        validator_id VARCHAR(36) NOT NULL,
        is_valid BOOLEAN NOT NULL,
        notes TEXT,
        validated_at TIMESTAMP NOT NULL
    )
    """)
    print("Created validation_records table")

    cursor.execute("""
    CREATE TABLE dataset_entries (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL UNIQUE REFERENCES feedback(id),
        model_id VARCHAR(100) NOT NULL,
        prompt_text TEXT NOT NULL,
        response_text TEXT NOT NULL,
        correct_response TEXT,
        dataset_metadata JSONB NOT NULL DEFAULT '{}',
        created_at TIMESTAMP NOT NULL
    )
    """)
    print("Created dataset_entries table")

    # Create a dummy alembic_version record so migrations don't try to run again
    cursor.execute("""
    CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL
    )
    """)
    print("Created alembic_version table")

    # Insert a placeholder version
    cursor.execute("""
    INSERT INTO alembic_version (version_num) VALUES ('manual_migration')
    """)
    print("Inserted manual migration record")

    # Create indices
    cursor.execute("CREATE INDEX idx_interactions_user_id ON interactions(user_id)")
    cursor.execute("CREATE INDEX idx_interactions_model_id ON interactions(model_id)")
    cursor.execute("CREATE INDEX idx_prompts_interaction_id ON prompts(interaction_id)")
    cursor.execute("CREATE INDEX idx_responses_prompt_id ON responses(prompt_id)")
    cursor.execute("CREATE INDEX idx_feedback_response_id ON feedback(response_id)")
    cursor.execute("CREATE INDEX idx_feedback_user_id ON feedback(user_id)")
    cursor.execute("CREATE INDEX idx_dimension_ratings_feedback_id ON dimension_ratings(feedback_id)")
    cursor.execute("CREATE INDEX idx_dimension_ratings_dimension_id ON dimension_ratings(dimension_id)")
    cursor.execute("CREATE INDEX idx_dataset_entries_model_id ON dataset_entries(model_id)")
    print("Created indices")

    print('Manual database setup completed successfully')

except Exception as e:
    print(f"Error setting up database: {e}")
    sys.exit(1)
finally:
    cursor.close()
    conn.close()
EOF

# Run the Python script for database setup
echo "Running database setup script..."
python3 /tmp/db_setup.py || {
    echo "Manual database setup failed, attempting standard migrations..."

    # Try standard migration process
    if [ ! -d "/app/migrations" ]; then
        echo "Initializing migrations directory..."
        flask db init || echo "Migration initialization failed"
    fi

    # Create migrations
    flask db migrate -m "Initial migration" && flask db upgrade
}

# Testing Flask app initialization
echo "Testing Flask app initialization..."
python3 -c "from app import create_app; app = create_app(); print('Flask app created successfully!')" || { echo "Flask app initialization failed"; exit 1; }

# Patch SQLAlchemy mappers before setting up initial data
echo "Patching SQLAlchemy relationship issues..."
cat > /tmp/patch_mappers.py << 'EOF'
from app import create_app, db
from app.models import Feedback, DimensionRating

# Create app context
app = create_app()
with app.app_context():
    # Force mapper configuration
    db.configure_mappers()
    print("SQLAlchemy mappers configured successfully")
EOF

python3 /tmp/patch_mappers.py || echo "SQLAlchemy mapper configuration skipped (non-critical)"

# Set up initial data
echo "Setting up initial data..."
flask setup-initial-data || echo "Initial data setup skipped (non-critical)"

# Attempt to register service (not critical for startup)
echo "Attempting to register service with Auth Service..."
python3 scripts/register_service.py || echo "Could not register with Auth Service. Will need to be done manually."

# Start the application
echo "Starting the application..."
echo "Command: $@"
exec "$@"