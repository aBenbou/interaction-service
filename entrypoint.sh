#!/bin/bash
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

# Service checks
echo "Checking for Auth Service..."
if nc -z auth_api 5000 2>/dev/null; then
  echo "Auth Service is available!"
else
  echo "Warning: Auth Service not detected. Proceeding anyway."
fi

echo "Checking for User Profile Service..."
if nc -z profile_api 5001 2>/dev/null; then
  echo "User Profile Service is available!"
else
  echo "Warning: User Profile Service not detected. Proceeding anyway."
fi

echo "Checking for Model Service..."
if nc -z model-manager 8000 2>/dev/null; then
  echo "Model Service is available!"
else
  echo "Warning: Model Service not detected. Proceeding anyway."
fi

# Run migrations with better error handling
echo "Running database migrations..."
if [ ! -d "/app/migrations" ]; then
  echo "Initializing migrations directory..."
  flask db init || { echo "Migration initialization failed"; exit 1; }
fi

# Create migrations with better error handling
echo "Creating migrations..."
flask db migrate -m "Initial migration" || echo "Migration creation skipped"

# Apply migrations with better error handling
echo "Applying migrations..."
flask db upgrade || { echo "Migration application failed"; exit 1; }

# This is where we'll add debug code to check Flask initialization
echo "Testing Flask app initialization..."
python -c "from app import create_app; app = create_app(); print('Flask app created successfully!')" || { echo "Flask app initialization failed"; exit 1; }

# Set up initial data with error handling
echo "Setting up initial data..."
if flask setup-initial-data &>/dev/null; then
  echo "Initial data setup complete"
else
  echo "Initial data setup skipped"
fi

# Check if gunicorn is available
echo "Checking for gunicorn..."
if ! command -v gunicorn &> /dev/null; then
  echo "gunicorn not found. Installing..."
  pip install gunicorn
fi

# Try to register service with error handling
echo "Attempting to register service with Auth Service..."
python scripts/register_service.py || echo "Could not register with Auth Service. Will need to be done manually."

# Start the application with explicit error logging
echo "Starting the application..."
echo "Command: $@"
# Run the command with error trapping
"$@" || { echo "Application failed to start with exit code $?"; exit 1; }