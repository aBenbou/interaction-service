# app/utils/user_client.py
import logging
from functools import lru_cache
from app.utils.client_base import BaseClient, ClientResponse
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class UserClient(BaseClient):
    """Client for communicating with the User Profile Service."""
    
    def __init__(self, base_url=None):
        """
        Initialize the User Client.
        
        Args:
            base_url: Base URL for the User Service API (default: from config)
        """
        super().__init__(
            service_name="User Profile Service",
            base_url_config_key="USER_SERVICE_URL",
            base_url=base_url,
            timeout=30
        )
    
    def get_app_token(self) -> Optional[str]:
        """
        Get application token for service-to-service communication.
        
        Returns:
            Token string or None if not configured
        """
        try:
            from flask import current_app
            from app.utils.auth_client import AuthClient
            
            auth_service_token = current_app.config.get('AUTH_SERVICE_TOKEN')
            if not auth_service_token:
                logger.warning("AUTH_SERVICE_TOKEN not configured")
                return None
                
            return auth_service_token
            
        except Exception as e:
            logger.error(f"Error getting app token: {str(e)}")
            return None
    
    @lru_cache(maxsize=100)
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """
        Get user profile from User Profile Service.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User profile dictionary or None if not found
        """
        app_token = self.get_app_token()
        if not app_token:
            return None
        
        headers = {"Authorization": f"Bearer {app_token}"}
        
        response = self.get(f'/api/profiles/{user_id}', headers=headers)
        
        if response.success:
            if response.data.get('success'):
                return response.data.get('profile')
        
        return None
    
    @lru_cache(maxsize=100)
    def has_role(self, user_id: str, role_name: str) -> bool:
        """
        Check if a user has a specific role by checking expertise areas.
        
        Args:
            user_id: UUID of the user
            role_name: Role to check ('validator' or 'admin')
            
        Returns:
            Boolean indicating if the user has the role
        """
        try:
            # For 'admin', defer to Auth Client
            if role_name == 'admin':
                from app.utils.auth_client import AuthClient
                auth_client = AuthClient()
                return auth_client.is_admin(user_id)
            
            # For 'validator', check expertise areas
            app_token = self.get_app_token()
            if not app_token:
                return False
            
            headers = {"Authorization": f"Bearer {app_token}"}
            
            response = self.get(f'/api/profiles/{user_id}/expertise', headers=headers)
            
            if not response.success:
                return False
            
            result = response.data
            if not result.get('success'):
                return False
            
            # Check if user has validation expertise at EXPERT level
            expertise_areas = result.get('expertise_areas', [])
            for area in expertise_areas:
                if (area.get('name') == 'validation' and 
                    area.get('level') == 'EXPERT'):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking expertise: {str(e)}")
            return False
    
    def get_user_connections(self, user_id: str, status: str = 'ACCEPTED') -> List[str]:
        """
        Get connections for a user.
        
        Args:
            user_id: UUID of the user
            status: Connection status filter
            
        Returns:
            List of connected user IDs
        """
        app_token = self.get_app_token()
        if not app_token:
            return []
        
        headers = {"Authorization": f"Bearer {app_token}"}
        
        response = self.get(f'/api/profiles/{user_id}/connections?status={status}', headers=headers)
        
        if not response.success:
            return []
        
        result = response.data
        if not result.get('success'):
            return []
        
        connections = result.get('connections', [])
        
        # Extract user IDs from both requester and recipient
        connected_ids = []
        for conn in connections:
            requester_id = conn.get('requester_id')
            recipient_id = conn.get('recipient_id')
            
            if requester_id == str(user_id):
                connected_ids.append(recipient_id)
            else:
                connected_ids.append(requester_id)
                
        return connected_ids
    
    @lru_cache(maxsize=50)
    def get_bulk_profiles(self, user_ids: List[str]) -> Dict[str, Dict]:
        """
        Get multiple user profiles in a single request.
        
        Args:
            user_ids: List of user IDs to fetch profiles for
            
        Returns:
            Dictionary mapping user_id to profile data, or empty dict if error
        """
        if not user_ids:
            return {}
        
        app_token = self.get_app_token()
        if not app_token:
            return {}
        
        headers = {
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        
        response = self.post(
            f'/api/profiles/bulk',
            headers=headers,
            json={"user_ids": user_ids}
        )
        
        if not response.success:
            return {}
        
        result = response.data
        if not result.get('success'):
            return {}
        
        return result.get('profiles', {})


# Create a singleton instance for easy access
user_client = UserClient()


# For backwards compatibility
def get_profile(user_id):
    """Get user profile from User Profile Service."""
    return user_client.get_profile(user_id)

def has_role(user_id, role_name):
    """Check if a user has a specific role."""
    return user_client.has_role(user_id, role_name)

def get_user_connections(user_id, status='ACCEPTED'):
    """Get connections for a user."""
    return user_client.get_user_connections(user_id, status)

def get_bulk_profiles(user_ids):
    """Get multiple user profiles in a single request."""
    return user_client.get_bulk_profiles(user_ids)