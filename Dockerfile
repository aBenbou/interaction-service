# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client tools and curl for healthcheck
RUN apt-get update && apt-get install -y postgresql-client curl && apt-get clean

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Expose the port
EXPOSE 5002

# Start the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "run:app"]