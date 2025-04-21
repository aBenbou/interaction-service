# app/utils/client_base.py
import logging
import requests
from flask import current_app
from functools import wraps
from typing import Dict, Any, Optional, List, Union, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ClientResponse:
    """Standardized client response object."""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, status_code: int = None):
        """
        Initialize a standardized client response.
        
        Args:
            success: Whether the request was successful
            data: The response data if successful
            error: Error message if unsuccessful
            status_code: HTTP status code (if applicable)
        """
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
    
    def __bool__(self) -> bool:
        """Allow using ClientResponse in boolean contexts to check success."""
        return self.success
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"success": self.success}
        
        if self.data is not None:
            result["data"] = self.data
            
        if self.error:
            result["error"] = self.error
            
        if self.status_code:
            result["status_code"] = self.status_code
            
        return result


class BaseClient:
    """Base client for service communication with standardized error handling."""
    
    def __init__(self, service_name: str, base_url_config_key: str = None, base_url: str = None, timeout: int = 30):
        """
        Initialize the base client.
        
        Args:
            service_name: Name of the service for logging
            base_url_config_key: Config key for service URL (if using config)
            base_url: Direct base URL (overrides config)
            timeout: Request timeout in seconds
        """
        self.service_name = service_name
        self.base_url_config_key = base_url_config_key
        self._base_url = base_url
        self.timeout = timeout
    
    @property
    def base_url(self) -> str:
        """Get the service base URL."""
        if self._base_url:
            return self._base_url
        
        if self.base_url_config_key and current_app:
            return current_app.config.get(self.base_url_config_key)
        
        return None
    
    def handle_request_exception(self, e: Exception, operation: str) -> ClientResponse:
        """
        Standardized exception handling.
        
        Args:
            e: The exception that occurred
            operation: Description of the operation being performed
            
        Returns:
            Standardized error response
        """
        error_message = f"Error in {self.service_name} during {operation}: {str(e)}"
        logger.error(error_message)
        
        if isinstance(e, requests.exceptions.HTTPError):
            return ClientResponse(False, error=error_message, status_code=e.response.status_code)
        elif isinstance(e, requests.exceptions.ConnectionError):
            return ClientResponse(False, error=f"Connection error to {self.service_name}", status_code=503)
        elif isinstance(e, requests.exceptions.Timeout):
            return ClientResponse(False, error=f"Timeout connecting to {self.service_name}", status_code=504)
        else:
            return ClientResponse(False, error=error_message)
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> ClientResponse:
        """
        Make a standardized HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be joined with base_url)
            **kwargs: Additional arguments for requests
            
        Returns:
            Standardized client response
        """
        if not self.base_url:
            return ClientResponse(False, error=f"{self.service_name} URL not configured")
        
        # Set default timeout if not provided
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            # Join URL properly with endpoint
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Make the request
            response = requests.request(method, url, **kwargs)
            
            # Raise for status to catch HTTP errors
            response.raise_for_status()
            
            # Parse JSON if present
            data = None
            if response.text:
                try:
                    data = response.json()
                except ValueError:
                    data = response.text
            
            return ClientResponse(True, data=data, status_code=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return self.handle_request_exception(e, f"{method} {endpoint}")
        except Exception as e:
            return self.handle_request_exception(e, f"{method} {endpoint}")
    
    def get(self, endpoint: str, **kwargs) -> ClientResponse:
        """Make a GET request."""
        return self.make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> ClientResponse:
        """Make a POST request."""
        return self.make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> ClientResponse:
        """Make a PUT request."""
        return self.make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> ClientResponse:
        """Make a DELETE request."""
        return self.make_request('DELETE', endpoint, **kwargs) 