# app/utils/user_client.py
import requests
from typing import Dict, Any, Optional
from uuid import UUID
from flask import current_app

def get_user_profile(user_id: UUID) -> Optional[Dict[str, Any]]:
    """Get user profile from User Profile Service"""
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        app_token = current_app.config.get('USER_SERVICE_TOKEN', 'placeholder-token')
        
        response = requests.get(
            f"{user_service_url}/api/profiles/{user_id}",
            headers={"Authorization": f"Bearer {app_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                return result.get('profile')
        
        current_app.logger.warning(f"Failed to get user profile: {response.status_code}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error fetching user profile: {str(e)}")
        return None