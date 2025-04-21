import requests
import logging

logger = logging.getLogger(__name__)

def check_service_availability(service_name, url, timeout=5):
    """
    Check if a service is available.
    
    Args:
        service_name: Name of the service
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Boolean indicating if service is available
    """
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            logger.info(f"{service_name} is available")
            return True
        else:
            logger.warning(f"{service_name} health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"Could not connect to {service_name}: {str(e)}")
        return False 