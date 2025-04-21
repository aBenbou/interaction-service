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

# Check if tables already exist (to avoid migration issues)
echo "Checking if database tables exist..."
python -c "
import psycopg2
import os
conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'interactions')\")
has_tables = cursor.fetchone()[0]
exit(0 if has_tables else 1)
" && TABLES_EXIST=true || TABLES_EXIST=false

if $TABLES_EXIST; then
  echo "Tables already exist, skipping migrations"
else
  echo "Tables don't exist, setting up database..."
  
  # Try resetting migrations if alembic_version exists but is causing problems
  python -c "
  import psycopg2
  import os
  conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
  conn = psycopg2.connect(conn_string)
  conn.autocommit = True
  cursor = conn.cursor()
  cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')\")
  has_alembic = cursor.fetchone()[0]
  if has_alembic:
    cursor.execute('DROP TABLE alembic_version')
    print('Dropped alembic_version table')
  " || echo "No alembic_version table to reset"
  
  # Try multiple approaches in sequence
  
  # 1. Try standard migration process
  echo "Attempting standard migrations..."
  if [ ! -d "/app/migrations" ]; then
    echo "Initializing migrations directory..."
    flask db init || echo "Migration initialization failed, will try alternatives"
  fi
  
  # Create migrations
  (flask db migrate -m "Initial migration" && flask db upgrade) || {
    echo "Standard migration failed, trying manual setup..."
    
    # 2. Try manual migration as backup
    echo "Running manual database setup..."
    python -c "
    import psycopg2
    import os
    from uuid import uuid4
    import enum
    from datetime import datetime
    
    # Connect to database
    conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create enums
    cursor.execute(\"\"\"
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_status_enum') THEN
            CREATE TYPE interaction_status_enum AS ENUM ('ACTIVE', 'COMPLETED', 'ABANDONED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'feedback_status_enum') THEN
            CREATE TYPE feedback_status_enum AS ENUM ('PENDING', 'VALIDATED', 'REJECTED');
        END IF;
    END$$;
    \"\"\")
    
    # Create core tables
    cursor.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS interactions (
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
    );
    
    CREATE TABLE IF NOT EXISTS prompts (
        id UUID PRIMARY KEY,
        interaction_id UUID NOT NULL REFERENCES interactions(id),
        content TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        submitted_at TIMESTAMP NOT NULL,
        context JSONB NOT NULL DEFAULT '{}',
        UNIQUE(interaction_id, sequence_number)
    );
    
    CREATE TABLE IF NOT EXISTS responses (
        id UUID PRIMARY KEY,
        prompt_id UUID NOT NULL UNIQUE REFERENCES prompts(id),
        content TEXT NOT NULL,
        generated_at TIMESTAMP NOT NULL,
        processing_time_ms INTEGER,
        tokens_used INTEGER,
        model_endpoint VARCHAR(100) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS evaluation_dimensions (
        id UUID PRIMARY KEY,
        model_id VARCHAR(100) NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        created_by UUID NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(model_id, name)
    );
    
    CREATE TABLE IF NOT EXISTS feedback (
        id UUID PRIMARY KEY,
        response_id UUID NOT NULL REFERENCES responses(id),
        user_id VARCHAR(36) NOT NULL,
        overall_comment TEXT,
        submitted_at TIMESTAMP NOT NULL,
        status feedback_status_enum NOT NULL DEFAULT 'PENDING'
    );
    
    CREATE TABLE IF NOT EXISTS dimension_ratings (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL REFERENCES feedback(id),
        dimension_id UUID NOT NULL REFERENCES evaluation_dimensions(id),
        score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
        justification TEXT,
        correct_response TEXT,
        UNIQUE(feedback_id, dimension_id)
    );
    
    CREATE TABLE IF NOT EXISTS validation_records (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL UNIQUE REFERENCES feedback(id),
        validator_id VARCHAR(36) NOT NULL,
        is_valid BOOLEAN NOT NULL,
        notes TEXT,
        validated_at TIMESTAMP NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS dataset_entries (
        id UUID PRIMARY KEY,
        feedback_id UUID NOT NULL UNIQUE REFERENCES feedback(id),
        model_id VARCHAR(100) NOT NULL,
        prompt_text TEXT NOT NULL,
        response_text TEXT NOT NULL,
        correct_response TEXT,
        dataset_metadata JSONB NOT NULL DEFAULT '{}',
        created_at TIMESTAMP NOT NULL
    );
    
    -- Create a dummy alembic_version record so migrations don't try to run again
    CREATE TABLE IF NOT EXISTS alembic_version (
        version_num VARCHAR(32) NOT NULL
    );
    
    -- Insert a placeholder version
    INSERT INTO alembic_version (version_num) VALUES ('manual_migration')
    ON CONFLICT DO NOTHING;
    
    -- Create indices
    CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);
    CREATE INDEX IF NOT EXISTS idx_interactions_model_id ON interactions(model_id);
    CREATE INDEX IF NOT EXISTS idx_prompts_interaction_id ON prompts(interaction_id);
    CREATE INDEX IF NOT EXISTS idx_responses_prompt_id ON responses(prompt_id);
    CREATE INDEX IF NOT EXISTS idx_feedback_response_id ON feedback(response_id);
    CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
    CREATE INDEX IF NOT EXISTS idx_dimension_ratings_feedback_id ON dimension_ratings(feedback_id);
    CREATE INDEX IF NOT EXISTS idx_dimension_ratings_dimension_id ON dimension_ratings(dimension_id);
    CREATE INDEX IF NOT EXISTS idx_dataset_entries_model_id ON dataset_entries(model_id);
    \"\"\"
    )
    
    print('Manual database setup completed successfully')
    "
  }
fi

# Testing Flask app initialization
echo "Testing Flask app initialization..."
python -c "from app import create_app; app = create_app(); print('Flask app created successfully!')" || { echo "Flask app initialization failed"; exit 1; }

# Set up initial data
echo "Setting up initial data..."
flask setup-initial-data || echo "Initial data setup skipped (non-critical)"

# Attempt to register service (not critical for startup)
echo "Attempting to register service with Auth Service..."
python scripts/register_service.py || echo "Could not register with Auth Service. Will need to be done manually."

# Start the application
echo "Starting the application..."
echo "Command: $@"
exec "$@"