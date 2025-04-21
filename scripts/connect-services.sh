#!/bin/bash
# This script creates a common network and connects all your microservices to it

# Create the common network
echo "Creating microservices-network..."
docker network create microservices-network || echo "Network already exists"

# Connect Auth Service containers
echo "Connecting Auth Service containers..."
docker network connect microservices-network auth_api || echo "Could not connect auth_api"
docker network connect microservices-network auth_db || echo "Could not connect auth_db"
docker network connect microservices-network auth_redis || echo "Could not connect auth_redis"

# Connect User Profile Service containers
echo "Connecting User Profile Service containers..."
docker network connect microservices-network profile_api || echo "Could not connect profile_api"
docker network connect microservices-network profile_db || echo "Could not connect profile_db"

# Connect Model Service container
echo "Connecting Model Service container..."
docker network connect microservices-network model-manager || echo "Could not connect model-manager"

echo "Network setup complete!"

echo "Now you can generate a service token and register the interaction service:"
echo "python scripts/register_service.py --generate-token"
echo ""
echo "Or start the interaction service with:"
echo "docker-compose up -d"