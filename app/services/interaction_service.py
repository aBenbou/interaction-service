# app/services/interaction_service.py
import logging
import requests
from datetime import datetime
from flask import current_app
from uuid import uuid4
from app import db
from app.models.interaction import Interaction
from app.utils.model_client import ModelClient
from app.utils.event_publisher import EventPublisher
from app.utils.user_client import user_client, UserClient

logger = logging.getLogger(__name__)

class InteractionService:
    """Business logic for user-model interactions."""
    
    @staticmethod
    def create_interaction(user_id, model_id, model_version, endpoint_name=None, metadata=None):
        """
        Create a new interaction session.
        
        Args:
            user_id: ID of the user (string format matching Auth Service's public_id)
            model_id: ID of the model
            model_version: Version of the model
            endpoint_name: Optional endpoint name (if not provided, one will be found)
            metadata: Optional metadata dictionary
            
        Returns:
            Created interaction or error dictionary
        """
        # Ensure user_id is a string
        user_id = str(user_id) if user_id else None
        
        # Initialize model client
        model_client = ModelClient()
        
        # Validate model exists via Model Service
        if not model_client.validate_model(model_id, model_version):
            return {"error": "Model not found or inactive"}
        
        # If endpoint not specified, find an appropriate endpoint
        endpoints_response = model_client.list_endpoints()
        if not endpoints_response.success or not endpoints_response.data:
            return {"error": "No active endpoints available"}
        
        endpoints = endpoints_response.data
        
        if not endpoint_name:
            # Try to find an endpoint for this specific model
            for endpoint in endpoints:
                endpoint_response = model_client.get_endpoint(endpoint.get('endpointName'))
                if not endpoint_response.success:
                    continue
                
                config = endpoint_response.data
                if not config or 'models' not in config:
                    continue
                
                for model in config.get('models', []):
                    if model.get('id') == model_id:
                        endpoint_name = endpoint.get('endpointName')
                        break
                
                if endpoint_name:
                    break
            
            # If still no endpoint, return error
            if not endpoint_name:
                return {"error": f"No active endpoint found for model {model_id}"}
        
        # Get user profile information to enrich metadata
        user_profile = user_client.get_profile(user_id)
        if user_profile:
            # Enrich metadata with user profile information
            user_metadata = {
                'username': user_profile.get('username'),
                'expertise': []
            }
            
            # Get expertise areas directly using user_client
            expertise_response = user_client.get(
                f'/api/profiles/{user_id}/expertise',
                headers={"Authorization": f"Bearer {user_client.get_app_token()}"}
            )
            
            if expertise_response.success and expertise_response.data.get('success'):
                expertise_areas = expertise_response.data.get('expertise_areas', [])
                user_metadata['expertise'] = [
                    {
                        'domain': area.get('domain') or area.get('name'),
                        'level': area.get('level')
                    }
                    for area in expertise_areas
                ]
            
            # Update metadata with user information
            if not metadata:
                metadata = {}
            metadata['user'] = user_metadata
        
        # Create the interaction
        interaction = Interaction(
            user_id=user_id,
            model_id=model_id,
            model_version=model_version,
            endpoint_name=endpoint_name,
            interaction_metadata=metadata or {}
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        # Publish event
        EventPublisher.publish('interaction.started', {
            'interaction_id': str(interaction.id),
            'user_id': interaction.user_id,
            'model_id': interaction.model_id,
            'endpoint_name': interaction.endpoint_name
        })
        
        return interaction
    
    @staticmethod
    def get_interaction(interaction_id):
        """
        Get interaction by ID.
        
        Args:
            interaction_id: ID of the interaction
            
        Returns:
            Interaction object or None if not found
        """
        return Interaction.query.get(interaction_id)
    
    @staticmethod
    def get_user_interactions(user_id, page=1, per_page=10, status=None, model_id=None):
        """
        Get interactions for a user with pagination.
        
        Args:
            user_id: ID of the user (string format matching Auth Service's public_id)
            page: Page number (1-indexed)
            per_page: Number of items per page
            status: Optional filter by status
            model_id: Optional filter by model ID
            
        Returns:
            Tuple of (interactions list, total count)
        """
        # Ensure user_id is a string
        user_id = str(user_id) if user_id else None
        
        query = Interaction.query.filter(Interaction.user_id == user_id)
        
        if status:
            query = query.filter(Interaction.status == status)
        if model_id:
            query = query.filter(Interaction.model_id == model_id)
        
        query = query.order_by(Interaction.started_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return paginated.items, paginated.total
    
    @staticmethod
    def end_interaction(interaction_id, status='COMPLETED'):
        """
        End an active interaction.
        
        Args:
            interaction_id: ID of the interaction
            status: New status (COMPLETED or ABANDONED)
            
        Returns:
            Updated interaction or None if not found
        """
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            return None
        
        if status not in ('COMPLETED', 'ABANDONED'):
            status = 'COMPLETED'
        
        interaction.status = status
        interaction.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Publish event
        EventPublisher.publish('interaction.completed', {
            'interaction_id': str(interaction.id),
            'user_id': interaction.user_id,
            'status': interaction.status
        })
        
        return interaction