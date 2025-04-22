# app/utils/model_client.py
import logging
from urllib.parse import urljoin
from app.utils.client_base import BaseClient, ClientResponse
from typing import Dict, List, Any, Optional, Union
import requests
import json

logger = logging.getLogger(__name__)

class ModelClient(BaseClient):
    """Client for communicating with the Model Service API."""
    
    def __init__(self, base_url=None):
        """
        Initialize the Model Client.
        
        Args:
            base_url: Base URL for the Model Service API (default: from config)
        """
        super().__init__(
            service_name="Model Service",
            base_url_config_key="MODEL_SERVICE_URL",
            base_url=base_url,
            timeout=30
        )
    
    def list_endpoints(self) -> ClientResponse:
        """
        Get a list of active model endpoints.
        
        Returns:
            ClientResponse with endpoints data or error
        """
        response = self.get('/endpoints')
        
        # Extract endpoints from response for backward compatibility
        if response.success and response.data:
            endpoints = response.data.get('endpoints', [])
            
            # Standardize field names to snake_case for easier access
            standardized_endpoints = []
            for endpoint in endpoints:
                standardized_endpoints.append({
                    'endpoint_name': endpoint.get('endpointName', ''),
                    'status': endpoint.get('status', ''),
                    'instance_type': endpoint.get('instanceType', ''),
                    'creation_time': endpoint.get('creationTime', '')
                })
            return ClientResponse(True, data=standardized_endpoints)
        
        return response
    
    def get_endpoint(self, endpoint_name: str) -> ClientResponse:
        """
        Get detailed information about a specific endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            
        Returns:
            ClientResponse with endpoint data or error
        """
        return self.get(f'/endpoint/{endpoint_name}')
    
    def query_endpoint(self, endpoint_name: str, query_text: str, 
                      context: Optional[Union[Dict, str]] = None, 
                      parameters: Optional[Dict] = None):
        """
        Query a model endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            query_text: Text query to send to the model
            context: Optional context for models that require it (dict or string)
            parameters: Optional parameters for the model
            
        Returns:
            Dictionary with model response data or error information
        """
        try:
            payload = {"query": query_text}
            
            if context is not None:
                # Convert dictionary context to a JSON string
                if isinstance(context, dict):
                    context = json.dumps(context)
                payload["context"] = context
                
            if parameters is not None:
                payload["parameters"] = parameters
            
            # Use the post() method from BaseClient
            response = self.post(f'/endpoint/{endpoint_name}/query', json=payload)
            
            # Extract the data part of the response
            if response.success:
                return response.data  # Return just the data portion
            else:
                # Return error dictionary that can be processed by the calling code
                return {"error": response.error or "Unknown error"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to Model Service when querying {endpoint_name}")
            return {"error": "Model service unavailable", 
                   "content": "I'm sorry, the model service is currently unavailable. Please try again later."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying endpoint {endpoint_name}: {str(e)}")
            return {"error": str(e)}
    
    def chat_completion(self, model_id: str, messages: List[Dict], endpoint_name: Optional[str] = None) -> Dict:
        """
        Call the OpenAI-compatible chat completion endpoint.
        
        Args:
            model_id: ID of the model to use
            messages: List of message objects (role, content)
            endpoint_name: Optional explicit endpoint name to use
            
        Returns:
            Dictionary with generated completion or error information
        """
        try:
            payload = {
                "model": model_id,
                "messages": messages
            }
            
            # Add endpoint name to the request if provided
            if endpoint_name:
                payload["endpoint_name"] = endpoint_name
            
            # Use the post() method from BaseClient
            response = self.post('/chat/completions', json=payload)
            
            # Extract the data part of the response
            if response.success:
                return response.data  # Return just the data portion
            else:
                # Special handling for 404 not deployed error for backward compatibility
                if response.status_code == 404:
                    return {"error": "Model not deployed", "details": "The specified model is not currently deployed"}
                
                # Return error dictionary that can be processed by the calling code
                return {"error": response.error or "Unknown error"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to Model Service when calling chat completion for {model_id}")
            return {"error": "Model service unavailable", 
                   "content": "I'm sorry, the model service is currently unavailable. Please try again later."}
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            return {"error": f"Failed to get chat completion: {str(e)}"}
    
    def get_model_dimensions(self, model_id: str) -> ClientResponse:
        """
        Get evaluation dimensions for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            ClientResponse with dimensions or default dimensions
        """
        # This would be updated to make an actual API call in production
        # For now keeping the default dimensions behavior
        
        # Default dimensions that could apply to most models
        default_dimensions = [
            {
                "id": "accuracy",
                "name": "Accuracy",
                "description": "The factual accuracy of the model's response"
            },
            {
                "id": "relevance",
                "name": "Relevance",
                "description": "How relevant the response is to the query"
            },
            {
                "id": "completeness",
                "name": "Completeness",
                "description": "How complete and comprehensive the response is"
            },
            {
                "id": "coherence",
                "name": "Coherence",
                "description": "How logical and well-structured the response is"
            }
        ]
        
        # Return success response with default dimensions
        return ClientResponse(True, data=default_dimensions)
    
    def validate_model(self, model_id: str, model_version: Optional[str] = None) -> bool:
        """
        Validate that a model exists and is currently deployed.
        
        Args:
            model_id: ID of the model
            model_version: Optional version of the model
            
        Returns:
            Boolean indicating if the model is valid and deployed
        """
        try:
            # Call the dedicated validation endpoint
            params = {}
            if model_version:
                params['model_version'] = model_version
                
            response = self.get(f'/models/validate/{model_id}', params=params)
            
            if not response.success:
                logger.warning(f"Failed to validate model {model_id}: {response.error}")
                return False
            
            # Check if the model is valid according to the response
            return response.data.get('valid', False)
        except Exception as e:
            logger.error(f"Error validating model {model_id}: {str(e)}")
            return False