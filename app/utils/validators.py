# app/utils/validators.py
import uuid
from datetime import datetime

def is_valid_uuid(uuid_str):
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_str: String to check
        
    Returns:
        Boolean indicating if valid
    """
    try:
        uuid_obj = uuid.UUID(str(uuid_str))
        return True
    except (ValueError, AttributeError, TypeError):
        return False
    
def is_valid_iso_date(date_str):
    """
    Check if a string is a valid ISO date.
    
    Args:
        date_str: String to check
        
    Returns:
        Boolean indicating if valid
    """
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError, TypeError):
        return False

def validate_pagination(page, per_page):
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        Tuple of (page, per_page)
    """
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
        
    try:
        per_page = int(per_page)
        if per_page < 1:
            per_page = 10
        elif per_page > 100:
            per_page = 100
    except (ValueError, TypeError):
        per_page = 10
        
    return page, per_page

def validate_rating_score(score):
    """
    Validate a rating score.
    
    Args:
        score: Score to validate
        
    Returns:
        Validated score (1-5) or None if invalid
    """
    try:
        score_int = int(score)
        if 1 <= score_int <= 5:
            return score_int
        return None
    except (ValueError, TypeError):
        return None