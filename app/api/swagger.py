from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "AI Model Feedback Platform API"
    }
)

def get_swagger_spec():
    """Generate OpenAPI specification."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "AI Model Feedback Platform API",
            "description": "API for collecting and managing feedback on AI model responses",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "servers": [
            {
                "url": "/api/v1",
                "description": "API v1"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "example": False
                        },
                        "message": {
                            "type": "string",
                            "example": "Error message"
                        }
                    }
                },
                "Feedback": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "interaction_id": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "prompt_id": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "user_id": {
                            "type": "string"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["accuracy", "relevance", "helpfulness"]
                        },
                        "rating": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "binary_evaluation": {
                            "type": "boolean"
                        },
                        "ranking": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "justification": {
                            "type": "string"
                        },
                        "validation_status": {
                            "type": "string",
                            "enum": ["PENDING", "ACCEPTED", "REJECTED"]
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time"
                        }
                    }
                },
                "Analytics": {
                    "type": "object",
                    "properties": {
                        "total_interactions": {
                            "type": "integer"
                        },
                        "completed_interactions": {
                            "type": "integer"
                        },
                        "total_feedback": {
                            "type": "integer"
                        },
                        "accepted_feedback": {
                            "type": "integer"
                        },
                        "average_response_time": {
                            "type": "number"
                        }
                    }
                },
                "Leaderboard": {
                    "type": "object",
                    "properties": {
                        "rank": {
                            "type": "integer"
                        },
                        "user_id": {
                            "type": "string"
                        },
                        "username": {
                            "type": "string"
                        },
                        "total_points": {
                            "type": "integer"
                        },
                        "metrics": {
                            "type": "object",
                            "properties": {
                                "feedback_count": {
                                    "type": "integer"
                                },
                                "accepted_feedback": {
                                    "type": "integer"
                                },
                                "interaction_count": {
                                    "type": "integer"
                                }
                            }
                        }
                    }
                }
            }
        },
        "paths": {
            "/feedback": {
                "post": {
                    "summary": "Submit feedback",
                    "description": "Submit feedback for a model response",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["interaction_id", "prompt_id", "category"],
                                    "properties": {
                                        "interaction_id": {
                                            "type": "string",
                                            "format": "uuid"
                                        },
                                        "prompt_id": {
                                            "type": "string",
                                            "format": "uuid"
                                        },
                                        "category": {
                                            "type": "string",
                                            "enum": ["accuracy", "relevance", "helpfulness"]
                                        },
                                        "rating": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 5
                                        },
                                        "binary_evaluation": {
                                            "type": "boolean"
                                        },
                                        "ranking": {
                                            "type": "integer",
                                            "minimum": 1
                                        },
                                        "justification": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Feedback submitted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "example": True
                                            },
                                            "feedback": {
                                                "$ref": "#/components/schemas/Feedback"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/analytics/user": {
                "get": {
                    "summary": "Get user engagement metrics",
                    "description": "Get engagement metrics for the current user",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "start_date",
                            "in": "query",
                            "description": "Start date (ISO format)",
                            "schema": {
                                "type": "string",
                                "format": "date-time"
                            }
                        },
                        {
                            "name": "end_date",
                            "in": "query",
                            "description": "End date (ISO format)",
                            "schema": {
                                "type": "string",
                                "format": "date-time"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User metrics retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "example": True
                                            },
                                            "metrics": {
                                                "$ref": "#/components/schemas/Analytics"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/leaderboard/rankings": {
                "get": {
                    "summary": "Get user rankings",
                    "description": "Get user rankings based on various metrics",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "time_period",
                            "in": "query",
                            "description": "Time period for rankings",
                            "schema": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "all_time"],
                                "default": "all_time"
                            }
                        },
                        {
                            "name": "category",
                            "in": "query",
                            "description": "Category filter",
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Number of users to return",
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1000,
                                "default": 100
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Rankings retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "example": True
                                            },
                                            "time_period": {
                                                "type": "string"
                                            },
                                            "category": {
                                                "type": "string"
                                            },
                                            "rankings": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Leaderboard"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    } 