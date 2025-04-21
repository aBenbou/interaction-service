AI Model Interaction and Feedback Service
This service provides a robust system for tracking user interactions with AI models, collecting structured feedback, managing the validation process, and preparing data for model retraining. It integrates seamlessly with the Model Service for deploying and querying AI models on AWS SageMaker.
Features

Interaction Management: Track user conversations with AI models
Prompt and Response Tracking: Record all prompts and generated responses
Structured Feedback Collection: Collect user feedback across multiple evaluation dimensions
Validation Workflow: Review and validate feedback submissions
Training Data Generation: Create dataset entries from validated feedback
Model Integration: Seamless connection to the Model Service for AI model queries
User Progression: Track user feedback contributions and quality

Architecture
The Interaction Service operates within a microservices architecture:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │  User Profile   │    │  Model Service  │
│                 │    │    Service      │    │                 │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────┬───────────┴──────────┬───────────┘
                    │                      │
                    ▼                      ▼
          ┌───────────────────────────────────────┐
          │     Interaction & Feedback Service     │
          └────────────────────┬──────────────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                ┌────▼─────┐        ┌────▼─────┐
                │PostgreSQL │        │  Redis   │
                └──────────┘        └──────────┘
Prerequisites

Docker and Docker Compose
PostgreSQL
Python 3.9+
Access to the Model Service

Installation and Setup
Step 1: Clone the Repository
bashgit clone https://github.com/yourusername/interaction-service.git
cd interaction-service
Step 2: Set Up Environment Variables
bashcp .env.example .env
Edit the .env file to set appropriate values:

Set valid JWT and API keys
Configure database connection
Set URLs for Auth, User, and Model services

Step 3: Run with Docker Compose
bashdocker-compose up -d
The API will be available at: http://localhost:8000
Step 4: Run Migrations and Initial Setup
bashdocker-compose exec interaction-service flask db upgrade
docker-compose exec interaction-service flask setup-initial-data
Integration with Model Service
The Interaction Service is designed to work seamlessly with the Model Service. It communicates with the Model Service API to:

Query model endpoints
Submit prompts for inference
Use the chat completion API for conversation-based models

Setting Up Connection
Ensure that the MODEL_SERVICE_URL environment variable points to the correct instance of the Model Service:
MODEL_SERVICE_URL=http://model-service:8000
In the docker-compose.yml file, the service connects to the Model Service network:
yamlnetworks:
  interaction-network:
    driver: bridge
  model-manager-network:
    external: true  # Use the existing network from model-service
Flow of Interaction

The user starts an interaction session with a specific model
The service looks up available endpoints for the model in the Model Service
Prompts are submitted to the Model Service's query API
Responses are recorded along with metadata
Users can provide structured feedback on responses
Feedback is validated and used to create training data

Usage
Starting an Interaction
bashcurl -X POST http://localhost:8000/interactions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "google-bert/bert-base-uncased",
    "model_version": "1.0"
  }'
This returns an interaction ID that you use for subsequent prompts.
Submitting a Prompt
bashcurl -X POST http://localhost:8000/interactions/{interaction_id}/prompts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is machine learning?"
  }'
Providing Feedback
bashcurl -X POST http://localhost:8000/feedback \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": "RESPONSE_ID",
    "dimension_ratings": [
      {
        "dimension_id": "accuracy",
        "score": 4,
        "justification": "The response was accurate but missing some context."
      },
      {
        "dimension_id": "helpfulness",
        "score": 5,
        "justification": "Very helpful explanation for beginners."
      }
    ],
    "overall_comment": "Good response overall, just needed more depth."
  }'
Validating Feedback (for validators)
bashcurl -X POST http://localhost:8000/validation/feedback/{feedback_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_valid": true,
    "notes": "Valid feedback with good justification."
  }'
Exporting Dataset
bashcurl -X GET http://localhost:8000/dataset/model/{model_id}/export?format=json \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
API Documentation
Interactions

POST /interactions - Create a new interaction
GET /interactions - List user interactions
GET /interactions/{interaction_id} - Get interaction details
PUT /interactions/{interaction_id} - Update interaction status
POST /interactions/{interaction_id}/prompts - Submit a prompt
POST /interactions/{interaction_id}/chat - Submit a chat message
GET /interactions/{interaction_id}/history - Get conversation history

Feedback

POST /feedback - Submit feedback
GET /feedback/{feedback_id} - Get feedback details
GET /feedback/user - Get user's feedback
GET /feedback/pending - Get pending feedback (validators only)
GET /feedback/response/{response_id} - Get feedback for a response

Dimensions

POST /dimensions - Create a dimension (admin only)
GET /dimensions/model/{model_id} - Get dimensions for a model
PUT /dimensions/{dimension_id} - Update a dimension (admin only)

Validation

POST /validation/feedback/{feedback_id} - Validate feedback
GET /validation/stats - Get validation statistics

Dataset

GET /dataset/model/{model_id} - Get dataset entries
GET /dataset/model/{model_id}/export - Export dataset
GET /dataset/entry/{entry_id} - Get specific dataset entry
GET /dataset/stats - Get dataset statistics

Development
Project Structure
interaction-service/
├── app/
│   ├── api/                # API endpoints
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   ├── __init__.py         # Flask application factory
│   └── config.py           # Configuration
├── migrations/             # Database migrations
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── entrypoint.sh           # Docker entrypoint
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md               # Documentation
Local Development
For development without Docker:
bash# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export FLASK_APP=run.py
export FLASK_ENV=development

# Run migrations
flask db upgrade

# Set up initial data
flask setup-initial-data

# Run the development server
flask run --host=0.0.0.0 --port=8000
Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.