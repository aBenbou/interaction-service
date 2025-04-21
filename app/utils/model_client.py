# app/utils/model_client.py
import logging
from urllib.parse import urljoin
from app.utils.client_base import BaseClient, ClientResponse
from typing import Dict, List, Any, Optional, Union
import requests

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
            return ClientResponse(True, data=endpoints)
        
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
                      context: Optional[Dict] = None, 
                      parameters: Optional[Dict] = None) -> ClientResponse:
        """
        Query a model endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            query_text: Text query to send to the model
            context: Optional context for models that require it
            parameters: Optional parameters for the model
            
        Returns:
            ClientResponse with model response or error
        """
        try:
            payload = {"query": query_text}
            
            if context is not None:
                payload["context"] = context
                
            if parameters is not None:
                payload["parameters"] = parameters
            
            url = self._build_url(f'/endpoint/{endpoint_name}/query')
            response = self._session.post(
                url, 
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return ClientResponse(True, data=response.json())
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to Model Service when querying {endpoint_name}")
            return ClientResponse(
                False,
                error="Model service unavailable",
                data={"content": "I'm sorry, the model service is currently unavailable. Please try again later."}
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying endpoint {endpoint_name}: {str(e)}")
            return ClientResponse(False, error=str(e))
    
    def chat_completion(self, model_id: str, messages: List[Dict]) -> ClientResponse:
        """
        Call the OpenAI-compatible chat completion endpoint.
        
        Args:
            model_id: ID of the model to use
            messages: List of message objects (role, content)
            
        Returns:
            ClientResponse with generated completion or error
        """
        payload = {
            "model": model_id,
            "messages": messages
        }
        
        response = self.post('/chat/completions', json=payload)
        
        # Special handling for 404 not deployed error for backward compatibility
        if not response.success and response.status_code == 404:
            return ClientResponse(
                False, 
                error="Model not deployed", 
                data={"details": "The specified model is not currently deployed"}
            )
        
        return response
    
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
            # Get all endpoints
            endpoints_response = self.list_endpoints()
            if not endpoints_response.success:
                return False
            
            endpoints = endpoints_response.data
            if not endpoints:
                return False
            
            # Check if any endpoint is running this model
            for endpoint in endpoints:
                endpoint_response = self.get_endpoint(endpoint.get('endpointName'))
                if not endpoint_response.success:
                    continue
                
                config = endpoint_response.data
                if not config or 'models' not in config:
                    continue
                
                for model in config.get('models', []):
                    if model.get('id') == model_id:
                        # If version is specified, check it matches
                        if model_version and model.get('version') != model_version:
                            continue
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error validating model {model_id}: {str(e)}")
            return False