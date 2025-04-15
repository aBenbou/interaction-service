# app/services/interaction_service.py
from typing import Dict, List, Tuple, Optional, Any
from uuid import UUID
from datetime import datetime
from app import db
from app.models.interaction import Interaction
from app.models.prompt import Prompt
from app.utils.event_publisher import publish_event
from sqlalchemy import or_

class InteractionService:
    """Business logic for interaction management."""
    
    @staticmethod
    def create_interaction(user_id: UUID, model_id: str, model_version: str, 
                        tags: List[str] = None, metadata: Dict = None) -> Interaction:
        """Create a new interaction."""
        interaction = Interaction(
            user_id=user_id,
            model_id=model_id,
            model_version=model_version,
            tags=tags or [],
            meta_data=metadata or {}  # Updated attribute name
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        # Publish event
        publish_event('interaction.started', {
            'interaction_id': str(interaction.id),
            'user_id': str(interaction.user_id),
            'model_id': interaction.model_id
        })
        
        return interaction
    
    @staticmethod
    def get_interaction(interaction_id: UUID) -> Optional[Interaction]:
        """Get an interaction by ID."""
        return Interaction.query.get(interaction_id)
    
    @staticmethod
    def get_user_interactions(user_id: UUID, page: int = 1, per_page: int = 10, 
                            status: str = None, model_id: str = None) -> Tuple[List[Interaction], int]:
        """Get interactions for a user with pagination."""
        query = Interaction.query.filter(Interaction.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(Interaction.status == status)
        if model_id:
            query = query.filter(Interaction.model_id == model_id)
        
        # Apply sorting (most recent first)
        query = query.order_by(Interaction.started_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        interactions = query.offset(offset).limit(per_page).all()
        
        return interactions, total
    
    @staticmethod
    def end_interaction(interaction_id: UUID, status: str = 'COMPLETED') -> Optional[Interaction]:
        """End an active interaction."""
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            return None
        
        interaction.status = status
        interaction.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Publish event
        publish_event('interaction.completed', {
            'interaction_id': str(interaction.id),
            'user_id': str(interaction.user_id),
            'status': interaction.status,
            'duration_seconds': interaction.duration_seconds
        })
        
        return interaction
    
    @staticmethod
    def get_interaction_history(interaction_id: UUID) -> List[Dict[str, Any]]:
        """Get all prompts and responses for an interaction."""
        prompts = Prompt.query.filter(
            Prompt.interaction_id == interaction_id
        ).order_by(Prompt.sequence_number).all()
        
        history = []
        for prompt in prompts:
            prompt_dict = prompt.to_dict()
            response_dict = prompt.response.to_dict() if prompt.response else None
            
            history.append({
                'prompt': prompt_dict,
                'response': response_dict
            })
        
        return history
    
    @staticmethod
    def search_interactions(user_id: UUID = None, query: str = None, model_id: str = None, 
                           status: str = None, tags: List[str] = None, 
                           start_date: str = None, end_date: str = None, 
                           page: int = 1, per_page: int = 10) -> Tuple[List[Interaction], int]:
        """Search for interactions based on criteria."""
        interactions_query = Interaction.query
        
        # Apply user filter if specified
        if user_id:
            interactions_query = interactions_query.filter(Interaction.user_id == user_id)
        
        # Apply model filter
        if model_id:
            interactions_query = interactions_query.filter(Interaction.model_id == model_id)
        
        # Apply status filter
        if status:
            interactions_query = interactions_query.filter(Interaction.status == status)
        
        # Apply date range filter
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                interactions_query = interactions_query.filter(Interaction.started_at >= start_datetime)
            except ValueError:
                # Invalid date format, ignore this filter
                pass
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                interactions_query = interactions_query.filter(Interaction.started_at <= end_datetime)
            except ValueError:
                # Invalid date format, ignore this filter
                pass
        
        # Apply tags filter (any of the specified tags)
        if tags and len(tags) > 0:
            # This requires PostgreSQL's array operators
            interactions_query = interactions_query.filter(
                Interaction.tags.overlap(tags)
            )
        
        # Apply text search if query is provided
        if query:
            # Join with prompts to search in content
            interactions_query = interactions_query.join(Prompt).filter(
                or_(
                    Prompt.content.ilike(f'%{query}%'),
                    Interaction.model_id.ilike(f'%{query}%')
                )
            ).distinct()
        
        # Apply sorting (most recent first)
        interactions_query = interactions_query.order_by(Interaction.started_at.desc())
        
        # Get total count
        total = interactions_query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        interactions = interactions_query.offset(offset).limit(per_page).all()
        
        return interactions, total