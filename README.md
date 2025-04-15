# README.md
# AI Interaction Service

A microservice for managing and tracking user interactions with AI models, maintaining conversation history, and providing a foundation for the feedback collection process.

## Architecture

This service integrates with the Authentication Service and User Profile Service, tracking all user interactions with AI models.

## Features

- Interaction management (create, retrieve, end)
- Prompt submission and response tracking
- Conversation history management
- Interaction bookmarking
- Search and filtering capabilities
- Comprehensive API for client integration

## API Endpoints

### Interaction Management
- `POST /api/interactions`: Create a new interaction
- `GET /api/interactions/{id}`: Get interaction details
- `PUT /api/interactions/{id}/end`: End an active interaction
- `GET /api/interactions/user/{user_id}`: Get user's interactions
- `GET /api/interactions/{id}/history`: Get interaction history
- `GET /api/interactions/search`: Search interactions

### Prompt & Response Management
- `POST /api/interactions/{id}/prompts`: Submit a prompt and get a response
- `GET /api/interactions/{id}/prompts/{prompt_id}`: Get a specific prompt and response

### Bookmark Management
- `POST /api/interactions/{id}/bookmark`: Bookmark an interaction
- `GET /api/bookmarks`: Get user's bookmarks
- `DELETE /api/bookmarks/{id}`: Remove a bookmark
- `PUT /api/bookmarks/{id}`: Update a bookmark

## Setup & Installation

### Environment Variables

Copy the sample environment file:
```bash
cp .env.example .env