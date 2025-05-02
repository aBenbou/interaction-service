import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request", "message": str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {"error": "Unauthorized", "message": str(error)}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {"error": "Forbidden", "message": str(error)}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "message": str(error)}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {"error": "Method not allowed", "message": str(error)}, 405
    
    @app.errorhandler(409)
    def conflict(error):
        return {"error": "Conflict", "message": str(error)}, 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return {"error": "Unprocessable entity", "message": str(error)}, 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return {"error": "Too many requests", "message": str(error)}, 429
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {str(error)}")
        return {"error": "Internal server error", "message": str(error)}, 500 