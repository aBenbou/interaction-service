# app/utils/auth_client.py
import logging
from functools import lru_cache
from app.utils.client_base import BaseClient, ClientResponse
from typing import Optional, Dict, List, Any, Union

logger = logging.getLogger(__name__)

class AuthClient(BaseClient):
    """Client for communicating with the Auth Service."""
    
    def __init__(self, base_url=None):
        """
        Initialize the Auth Client.
        
        Args:
            base_url: Base URL for the Auth Service API (default: from config)
        """
        super().__init__(
            service_name="Auth Service",
            base_url_config_key="AUTH_SERVICE_URL",
            base_url=base_url,
            timeout=30
        )
    
    def validate_token(self, token: str) -> ClientResponse:
        """
        Validate a JWT token with the Auth Service.
        
        Args:
            token: JWT token to validate
            
        Returns:
            ClientResponse with user info or error
        """
        return self.get(
            '/api/auth/validate-jwt',
            headers={"Authorization": f"Bearer {token}"}
        )
    
    def get_user_permissions(self, user_id: str) -> ClientResponse:
        """
        Get user permissions from the Auth Service.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            ClientResponse with permissions data or error
        """
        # Get app token for service-to-service auth
        app_token = self._get_app_token()
        if not app_token:
            return ClientResponse(False, error="Auth Service token not configured")
        
        return self.get(
            f'/api/roles/user/{user_id}/permissions',
            headers={"Authorization": f"Bearer {app_token}"}
        )
    
    def is_admin(self, user_id: str) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Boolean indicating if user is admin
        """
        permissions_response = self.get_user_permissions(user_id)
        
        if permissions_response.success:
            permissions = permissions_response.data.get('permissions', [])
            # Check for admin-related permissions
            admin_permissions = ['user:admin', 'role:admin', 'service:admin', 'admin']
            return any(perm in permissions for perm in admin_permissions)
        
        return False
    
    def is_owner_or_admin(self, user_id: str, profile_id: str) -> bool:
        """
        Check if a user is the owner of a profile or an admin.
        
        Args:
            user_id: UUID of the user
            profile_id: UUID of the profile
            
        Returns:
            Boolean indicating if user is owner or admin
        """
        # User is the owner of the profile
        if user_id == profile_id:
            return True
        
        # User is an admin
        return self.is_admin(user_id)
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: UUID of the user
            permission: Permission to check for
            
        Returns:
            Boolean indicating if user has the permission
        """
        permissions_response = self.get_user_permissions(user_id)
        
        if permissions_response.success:
            permissions = permissions_response.data.get('permissions', [])
            return permission in permissions
        
        return False
    
    def _get_app_token(self) -> Optional[str]:
        """
        Get application token for service-to-service communication.
        
        Returns:
            Token string or None if not configured
        """
        try:
            from flask import current_app
            return current_app.config.get('AUTH_SERVICE_TOKEN')
        except Exception as e:
            logger.error(f"Error getting app token: {str(e)}")
            return None


# For backwards compatibility
def validate_token(token):
    """
    Validate a JWT token with the Auth Service.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Dictionary with user info or None if invalid
    """
    client = AuthClient()
    response = client.validate_token(token)
    
    if response.success:
        return response.data
    return None

def get_user_permissions(user_id):
    """
    Get user permissions from the Auth Service.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        Dictionary with permissions
    """
    client = AuthClient()
    response = client.get_user_permissions(user_id)
    
    if response.success:
        return response.data
    
    return {
        'success': False,
        'message': response.error or 'Error fetching user permissions',
        'permissions': []
    }

def is_admin(user_id):
    """
    Check if a user is an admin.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        Boolean indicating if user is admin
    """
    client = AuthClient()
    return client.is_admin(user_id)

def is_owner_or_admin(user_id, profile_id):
    """
    Check if a user is the owner of a profile or an admin.
    
    Args:
        user_id: UUID of the user
        profile_id: UUID of the profile
        
    Returns:
        Boolean indicating if user is owner or admin
    """
    client = AuthClient()
    return client.is_owner_or_admin(user_id, profile_id)

def has_permission(user_id, permission):
    """
    Check if a user has a specific permission.
    
    Args:
        user_id: UUID of the user
        permission: Permission to check for
        
    Returns:
        Boolean indicating if user has the permission
    """
    client = AuthClient()
    return client.has_permission(user_id, permission)