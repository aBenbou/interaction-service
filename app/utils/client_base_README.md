# Client Base Module

## Overview

The `client_base.py` module provides a standardized approach to service-to-service communication with consistent error handling and response formatting. This module is the foundation for all client utilities (`ModelClient`, `AuthClient`, and `UserClient`).

## Key Components

### ClientResponse

The `ClientResponse` class represents a standardized response object from any service call:

```python
class ClientResponse:
    def __init__(self, success: bool, data: Any = None, error: str = None, status_code: int = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
```

**Features:**
- Boolean evaluation: `if response:` evaluates to the success status
- Dictionary conversion: `response.to_dict()` returns a standardized dict format

### BaseClient

The `BaseClient` class provides core functionality for all service clients:

```python
class BaseClient:
    def __init__(self, service_name: str, base_url_config_key: str = None, 
                 base_url: str = None, timeout: int = 30):
        # ...
```

**Features:**
- Consistent URL construction from configuration
- Standardized HTTP methods (get, post, put, delete)
- Automatic error handling and logging
- Response status code processing
- JSON parsing with error handling

## Error Handling Strategy

All service clients follow a consistent error handling approach:

1. Network/connection errors are caught and returned as failed responses
2. HTTP error codes are processed and returned as failed responses with status codes
3. JSON parsing errors are properly handled
4. All errors are logged with appropriate context
5. Server unavailability is properly communicated with appropriate status codes

## Response Format

All client methods return a `ClientResponse` object with these guarantees:

- `response.success` will be `True` or `False`
- `response.data` will contain parsed data if successful
- `response.error` will contain error messages if unsuccessful
- `response.status_code` will contain HTTP status code when applicable

## Usage Examples

### Basic Request

```python
from app.utils.model_client import ModelClient

def get_model_info(model_id):
    client = ModelClient()
    response = client.get(f'/models/{model_id}')
    
    if response.success:
        return response.data
    else:
        logger.error(f"Failed to get model info: {response.error}")
        return None
```

### Handling Different Status Codes

```python
def create_resource(resource_data):
    client = SomeClient()
    response = client.post('/resources', json=resource_data)
    
    if response.success:
        return response.data
    elif response.status_code == 409:
        # Conflict - resource already exists
        return handle_conflict()
    elif response.status_code == 400:
        # Bad request - validation error
        return handle_validation_error(response.data)
    else:
        # Generic error
        return handle_error(response.error)
```

## Implementation Notes

1. All client methods should return a `ClientResponse` object, not raw data
2. Service-specific clients should extend `BaseClient`
3. Method signatures should include type hints
4. Backward compatibility is maintained through singleton instances
5. All exception handling should be done within the client methods 