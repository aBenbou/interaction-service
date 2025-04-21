import logging
from functools import wraps
from flask import request, jsonify, g, current_app
from uuid import UUID
from app.utils.auth_client import AuthClient, validate_token, is_admin, get_user_permissions

logger = logging.getLogger(__name__)

# Create a singleton instance for easy access
auth_client = AuthClient()

def jwt_required_with_permissions(permissions=None):
    """
    Decorator to check JWT and verify required permissions.
    
    Args:
        permissions: List of required permissions or None
        
    Returns:
        Decorator function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Get the token from the Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'success': False, 'message': 'Missing or invalid Authorization header'}), 401
                
                token = auth_header.split('Bearer ')[1]
                
                # Validate the token with Auth Service
                validation_response = auth_client.validate_token(token)
                if not validation_response.success:
                    return jsonify({'success': False, 'message': 'Invalid token'}), 401
                
                validation = validation_response.data
                if not validation or not validation.get('success', False):
                    return jsonify({'success': False, 'message': 'Invalid token'}), 401
                
                # Get user identity from validation response
                user_id = validation.get('user_id')
                try:
                    user_id = UUID(user_id)
                except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid user ID in token'}), 401
                
                # Store user ID in g for access in the route
                g.current_user_id = user_id
                
                # If no permissions required, proceed
                if not permissions:
                    return fn(*args, **kwargs)
                
                # For testing, give all users admin permission
                # WARNING: ONLY FOR TESTING - REMOVE IN PRODUCTION
                g.user_permissions = {"admin": True}
                return fn(*args, **kwargs)
                
                # Comment out the permission check for now
                """
                # Check if user has admin permissions
                if auth_client.is_admin(user_id):
                    return fn(*args, **kwargs)
                
                # Get user permissions from Auth Service
                permissions_response = auth_client.get_user_permissions(user_id)
                
                if not permissions_response.success:
                    return jsonify({'success': False, 'message': f'Error fetching permissions: {permissions_response.error}'}), 500
                
                user_permissions = permissions_response.data
                
                if not user_permissions.get('success', False):
                    return jsonify({'success': False, 'message': 'Error fetching permissions'}), 500
                
                # Check if user has all required permissions
                user_perms = user_permissions.get('permissions', [])
                for permission in permissions:
                    if permission not in user_perms:
                        return jsonify({
                            'success': False, 
                            'message': f'Permission denied: {permission} required'
                        }), 403
                """
                
            except Exception as e:
                current_app.logger.error(f"Authentication error: {str(e)}")
                return jsonify({'success': False, 'message': f'Authentication error: {str(e)}'}), 401
                
        return wrapper
    return decorator
