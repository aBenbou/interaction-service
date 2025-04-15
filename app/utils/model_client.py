import time
import requests
from typing import Dict, Any
from flask import current_app

class ModelClient:
    """Client for interacting with AI models."""
    
    @staticmethod
    def generate_response(prompt_text: str, model_id: str, model_version: str, context: Dict = None) -> Dict[str, Any]:
        """
        Generate a response from an AI model by calling the Model Service API.
        
        Args:
            prompt_text: The text to send to the model
            model_id: The ID of the model to use
            model_version: The version of the model to use
            context: Additional context for the model
            
        Returns:
            Dict containing the model's response
        """
        try:
            # Get the model service URL from config
            model_service_url = current_app.config.get('MODEL_SERVICE_URL', 'http://model_api:8000')
            
            # Prepare the request payload
            payload = {
                "prompt": prompt_text,
                "model_id": model_id,
                "model_version": model_version,
                "context": context or {}
            }
            
            # Start timing
            start_time = time.time()
            
            # Make the API call to the model service
            response = requests.post(
                f"{model_service_url}/api/models/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Calculate processing time (in case API call fails)
            end_time = time.time()
            processing_time_ms = int((end_time - start_time) * 1000)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Extract the response data
                result = response.json()
                
                # Return the formatted response
                return {
                    'content': result.get('content', ''),
                    'processing_time_ms': result.get('processing_time_ms', processing_time_ms),
                    'tokens_used': result.get('tokens_used', 0),
                    'confidence': result.get('confidence', 0.0)
                }
            else:
                # Handle HTTP error
                error_msg = f"Model service HTTP error: {response.status_code} - {response.text}"
                current_app.logger.error(error_msg)
                
                return {
                    'content': "I'm sorry, I encountered an issue while processing your request.",
                    'processing_time_ms': processing_time_ms,
                    'tokens_used': 0,
                    'confidence': 0.0,
                    'error': error_msg
                }
                
        except Exception as e:
            # Log the error
            current_app.logger.error(f"Error calling model service: {str(e)}")
            
            # Return an error response
            return {
                'content': "I'm sorry, I encountered an issue while processing your request.",
                'processing_time_ms': 0,
                'tokens_used': 0,
                'confidence': 0.0,
                'error': str(e)
            }