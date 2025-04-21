# app/utils/model_constants.py
"""
Constants and utilities for maintaining consistent model references
between the Interaction Service and Model Service.
"""

# Model source types (should match Model Service's ModelSource enum)
class ModelSource:
    HUGGING_FACE = "huggingface"
    SAGEMAKER = "sagemaker"
    CUSTOM = "custom"

# Task types for models (should align with Model Service's task enums)
class ModelTask:
    # Text generation tasks
    TEXT_GENERATION = "text-generation"
    CHAT = "text-generation"  # For compatibility with chat models
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    
    # Question answering tasks
    QUESTION_ANSWERING = "question-answering"
    TABLE_QUESTION_ANSWERING = "table-question-answering"
    
    # Classification tasks
    TEXT_CLASSIFICATION = "text-classification"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"
    
    # Other tasks
    FILL_MASK = "fill-mask"
    FEATURE_EXTRACTION = "feature-extraction"

# Mapping of model tasks to default evaluation dimensions
DEFAULT_EVALUATION_DIMENSIONS = {
    ModelTask.TEXT_GENERATION: [
        {"id": "coherence", "name": "Coherence", "description": "How logical and well-structured the response is"},
        {"id": "relevance", "name": "Relevance", "description": "How relevant the response is to the prompt"},
        {"id": "creativity", "name": "Creativity", "description": "The originality and inventiveness of the response"},
        {"id": "accuracy", "name": "Accuracy", "description": "The factual accuracy of any claims made"}
    ],
    ModelTask.CHAT: [
        {"id": "helpfulness", "name": "Helpfulness", "description": "How helpful the response is in addressing the query"},
        {"id": "correctness", "name": "Correctness", "description": "How factually correct the information is"},
        {"id": "clarity", "name": "Clarity", "description": "How clear and understandable the response is"},
        {"id": "safety", "name": "Safety", "description": "Whether the response avoids harmful or inappropriate content"}
    ],
    ModelTask.SUMMARIZATION: [
        {"id": "coherence", "name": "Coherence", "description": "How logical and well-structured the summary is"},
        {"id": "coverage", "name": "Coverage", "description": "How well the summary covers the main points"},
        {"id": "conciseness", "name": "Conciseness", "description": "How concise and to-the-point the summary is"},
        {"id": "accuracy", "name": "Accuracy", "description": "How accurately the summary reflects the source"}
    ],
    ModelTask.QUESTION_ANSWERING: [
        {"id": "correctness", "name": "Correctness", "description": "How correct the answer is based on the context"},
        {"id": "completeness", "name": "Completeness", "description": "How complete the answer is"},
        {"id": "relevance", "name": "Relevance", "description": "How relevant the answer is to the question"},
        {"id": "conciseness", "name": "Conciseness", "description": "How concise and to-the-point the answer is"}
    ],
    # Default dimensions for all other tasks
    "default": [
        {"id": "accuracy", "name": "Accuracy", "description": "The factual accuracy of the model's response"},
        {"id": "relevance", "name": "Relevance", "description": "How relevant the response is to the query"},
        {"id": "completeness", "name": "Completeness", "description": "How complete and comprehensive the response is"},
        {"id": "coherence", "name": "Coherence", "description": "How logical and well-structured the response is"}
    ]
}

def get_default_dimensions_for_task(task):
    """
    Get the default evaluation dimensions for a specific task.
    
    Args:
        task: The model task type
        
    Returns:
        List of dimension objects
    """
    return DEFAULT_EVALUATION_DIMENSIONS.get(task, DEFAULT_EVALUATION_DIMENSIONS["default"])