# app/utils/decorators.py
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from uuid import UUID

def jwt_required_with_permissions(permissions=None):
    """Decorator to check JWT and verify required permissions"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Verify JWT is present and valid
                verify_jwt_in_request()
                
                # Get user identity from JWT
                user_id = UUID(get_jwt_identity())
                
                # Store user ID in g for access in the route
                g.current_user_id = user_id
                
                # If no permissions required, proceed
                if not permissions:
                    return fn(*args, **kwargs)
                
                # Check permissions
                from app.utils.auth_client import has_permission, is_admin
                
                # Admin users bypass permission checks
                if is_admin(user_id):
                    return fn(*args, **kwargs)
                
                # Check specific permissions
                if isinstance(permissions, str):
                    if not has_permission(user_id, permissions):
                        return jsonify({
                            'success': False, 
                            'message': f'Permission denied: {permissions} required'
                        }), 403
                else:
                    # Check if user has all required permissions
                    for permission in permissions:
                        if not has_permission(user_id, permission):
                            return jsonify({
                                'success': False, 
                                'message': f'Permission denied: {permission} required'
                            }), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Authentication error: {str(e)}'}), 401
                
        return wrapper
    return decorator