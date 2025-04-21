# app/utils/token_utils.py
import os
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def get_app_token():
    """
    Get an application token from the Auth Service for service-to-service communication.
    
    Returns:
        Token string or None if error
    """
    try:
        auth_service_url = current_app.config.get('AUTH_SERVICE_URL')
        service_api_key = current_app.config.get('SERVICE_API_KEY')
        
        if not auth_service_url or not service_api_key:
            logger.error("Missing AUTH_SERVICE_URL or SERVICE_API_KEY configuration")
            return None
        
        # Get token from Auth Service
        response = requests.post(
            f"{auth_service_url}/api/tokens/validate",
            headers={
                "Authorization": f"Bearer {service_api_key}"
            }
        )
        
        if response.status_code == 200:
            return response.json().get('token')
        else:
            logger.error(f"Failed to get app token: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting app token: {str(e)}")
        return None