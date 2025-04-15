# app/utils/auth_client.py
import requests
from typing import Dict, Any, Optional
from uuid import UUID
from flask import current_app

def validate_token(token: str) -> Dict[str, Any]:
    """Validate a JWT token with the Auth Service"""
    try:
        auth_service_url = current_app.config['AUTH_SERVICE_URL']
        response = requests.get(
            f"{auth_service_url}/api/auth/validate-jwt",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'message': 'Invalid token'
            }
    except Exception as e:
        current_app.logger.error(f"Error validating token: {str(e)}")
        return {
            'success': False,
            'message': 'Error validating token'
        }

def get_user_permissions(user_id: UUID) -> Dict[str, Any]:
    """Get user permissions from the Auth Service"""
    try:
        auth_service_url = current_app.config['AUTH_SERVICE_URL']
        app_token = current_app.config.get('AUTH_SERVICE_TOKEN', 'placeholder-token')
        
        response = requests.get(
            f"{auth_service_url}/api/roles/user/{user_id}/permissions",
            headers={"Authorization": f"Bearer {app_token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'message': 'Error fetching user permissions',
                'permissions': []
            }
    except Exception as e:
        current_app.logger.error(f"Error fetching user permissions: {str(e)}")
        return {
            'success': False,
            'message': 'Error fetching user permissions',
            'permissions': []
        }

def has_permission(user_id: UUID, permission_name: str) -> bool:
    """Check if a user has a specific permission"""
    user_permissions = get_user_permissions(user_id)
    
    if user_permissions.get('success', False):
        permissions = user_permissions.get('permissions', [])
        return permission_name in permissions
    
    return False

def is_admin(user_id: UUID) -> bool:
    """Check if a user is an admin"""
    admin_permissions = ['interaction:view_any', 'interaction:admin', 'admin']
    for perm in admin_permissions:
        if has_permission(user_id, perm):
            return True
    return False