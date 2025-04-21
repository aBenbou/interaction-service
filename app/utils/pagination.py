# app/utils/pagination.py
from flask import request

def get_pagination_params(request_obj=None):
    """
    Extract pagination parameters from request.
    
    Args:
        request_obj: Request object (defaults to Flask request)
        
    Returns:
        Tuple of (page, per_page)
    """
    if request_obj is None:
        request_obj = request
        
    try:
        page = max(1, int(request_obj.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
        
    try:
        per_page = min(int(request_obj.args.get('per_page', 10)), 100)
    except (ValueError, TypeError):
        per_page = 10
        
    return page, per_page
