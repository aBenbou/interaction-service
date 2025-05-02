# app/services/feedback_service.py
import logging
import uuid
from flask import current_app, g
from app import db
from app.models.response import Response
from app.models.prompt import Prompt
from app.models.interaction import Interaction
from app.models.feedback import Feedback
from app.models.dimension import EvaluationDimension
from app.models.dimension_rating import DimensionRating
from app.utils.event_publisher import EventPublisher
from app.utils.user_client import UserClient, has_role
from app.services.validation_service import ValidationService
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime
from app.utils.user_client import user_client

logger = logging.getLogger(__name__)

class FeedbackService:
    """Service for managing feedback on model responses."""
    
    @staticmethod
    def submit_feedback(
        interaction_id: UUID,
        prompt_id: UUID,
        user_id: str,
        category: str,
        rating: Optional[int] = None,
        binary_evaluation: Optional[bool] = None,
        ranking: Optional[int] = None,
        justification: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for a model response.
        
        Args:
            interaction_id: ID of the interaction
            prompt_id: ID of the prompt
            user_id: ID of the user submitting feedback
            category: Feedback category (e.g., 'accuracy', 'relevance')
            rating: Optional 1-5 rating
            binary_evaluation: Optional yes/no evaluation
            ranking: Optional ranking for multiple responses
            justification: Optional explanation
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with feedback data or error
        """
      
        interaction = Interaction.query.get(interaction_id)
        prompt = Prompt.query.get(prompt_id)
        
        if not interaction or not prompt:
            return {
                'success': False,
                'message': 'Interaction or prompt not found'
            }
        
    
        if not any([rating is not None, binary_evaluation is not None, ranking is not None]):
            return {
                'success': False,
                'message': 'Must provide at least one type of evaluation'
            }
        
        if rating is not None and not (1 <= rating <= 5):
            return {
                'success': False,
                'message': 'Rating must be between 1 and 5'
            }
        
        feedback = Feedback(
            interaction_id=interaction_id,
            prompt_id=prompt_id,
            user_id=user_id,
            model_id=interaction.model_id,
            model_version=interaction.model_version,
            category=category,
            rating=rating,
            binary_evaluation=binary_evaluation,
            ranking=ranking,
            justification=justification,
            metadata=metadata or {}
        )
        
        db.session.add(feedback)
        db.session.commit()
        
       
        EventPublisher.publish('feedback.submitted', {
            'feedback_id': str(feedback.id),
            'interaction_id': str(interaction_id),
            'user_id': user_id,
            'category': category
        })
        
        return {
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }
    
    @staticmethod
    def validate_feedback(
        feedback_id: UUID,
        validator_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate submitted feedback.
        
        Args:
            feedback_id: ID of the feedback to validate
            validator_id: ID of the validator
            status: New status (ACCEPTED or REJECTED)
            notes: Optional validation notes
            
        Returns:
            Dictionary with updated feedback data or error
        """
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {
                'success': False,
                'message': 'Feedback not found'
            }
        
        if status not in ('ACCEPTED', 'REJECTED'):
            return {
                'success': False,
                'message': 'Invalid status. Use ACCEPTED or REJECTED'
            }
        
   
        feedback.validation_status = status
        feedback.validator_id = validator_id
        feedback.validation_notes = notes
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
   
        EventPublisher.publish('feedback.validated', {
            'feedback_id': str(feedback.id),
            'validator_id': validator_id,
            'status': status
        })
        
        return {
            'success': True,
            'message': 'Feedback validated successfully',
            'feedback': feedback.to_dict()
        }
    
    @staticmethod
    def get_feedback(
        feedback_id: UUID,
        include_private: bool = False
    ) -> Dict[str, Any]:
        """
        Get feedback by ID.
        
        Args:
            feedback_id: ID of the feedback
            include_private: Whether to include private fields
            
        Returns:
            Dictionary with feedback data or error
        """
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {
                'success': False,
                'message': 'Feedback not found'
            }
        
        return {
            'success': True,
            'feedback': feedback.to_dict()
        }
    
    @staticmethod
    def get_user_feedback(
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get feedback submitted by a user.
        
        Args:
            user_id: ID of the user
            status: Optional filter by validation status
            category: Optional filter by category
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with feedback list and pagination info
        """
        query = Feedback.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(validation_status=status)
        if category:
            query = query.filter_by(category=category)
        
      
        query = query.order_by(Feedback.created_at.desc())
        
 
        paginated = query.paginate(page=page, per_page=per_page)
        
        return {
            'success': True,
            'feedback': [f.to_dict() for f in paginated.items],
            'pagination': {
                'total': paginated.total,
                'pages': paginated.pages,
                'page': page,
                'per_page': per_page
            }
        }
    
    @staticmethod
    def get_pending_validation(
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get feedback pending validation.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with feedback list and pagination info
        """
        query = Feedback.query.filter_by(validation_status='PENDING')
        query = query.order_by(Feedback.created_at.asc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return {
            'success': True,
            'feedback': [f.to_dict() for f in paginated.items],
            'pagination': {
                'total': paginated.total,
                'pages': paginated.pages,
                'page': page,
                'per_page': per_page
            }
        }

    @staticmethod
    def create_feedback(response_id, user_id, dimension_ratings, overall_comment=None):
        """
        Create feedback for a model response.
        
        Args:
            response_id: ID of the response
            user_id: ID of the user providing feedback (string format matching Auth Service's public_id)
            dimension_ratings: List of dimension rating objects
            overall_comment: Optional overall comment
            
        Returns:
            Created feedback or error dictionary
        """
        user_id = str(user_id) if user_id else None
        
   
        response = Response.query.get(response_id)
        if not response:
            return {"error": "Response not found"}
        
      
        prompt = Prompt.query.get(response.prompt_id)
        if not prompt:
            return {"error": "Associated prompt not found"}
            
        interaction = Interaction.query.get(prompt.interaction_id)
        if not interaction:
            return {"error": "Associated interaction not found"}
  
        existing = Feedback.query.filter(
            Feedback.response_id == response_id,
            Feedback.user_id == user_id
        ).first()
        
        if existing:
            return {"error": "You have already provided feedback for this response"}
        
    
        feedback = Feedback(
            response_id=response_id,
            user_id=user_id,
            overall_comment=overall_comment
        )
        
        db.session.add(feedback)
        db.session.flush()  
        

        for rating_data in dimension_ratings:
            dimension_id = rating_data.get('dimension_id')
            score = rating_data.get('score')
            justification = rating_data.get('justification')
            correct_response = rating_data.get('correct_response')
            
        
            dimension = None
            try:
             
                uuid_obj = uuid.UUID(str(dimension_id))
                dimension = EvaluationDimension.query.get(uuid_obj)
            except (ValueError, TypeError):
              
                dimension = EvaluationDimension.query.filter(
                    db.or_(
                        EvaluationDimension.model_id == interaction.model_id,
                        EvaluationDimension.model_id == 'all'
                    ),
                    EvaluationDimension.name.ilike(dimension_id)
                ).first()
                
            if not dimension:
                db.session.rollback()
                return {"error": f"Dimension {dimension_id} not found. Please use a valid dimension ID or name"}
                    
         
            if dimension.model_id != interaction.model_id and dimension.model_id != 'all':
                db.session.rollback()
                return {"error": f"Dimension {dimension.name} is not applicable to this model"}
           
            try:
                score_int = int(score)
                if not 1 <= score_int <= 5:
                    db.session.rollback()
                    return {"error": "Score must be between 1 and 5"}
            except (ValueError, TypeError):
                db.session.rollback()
                return {"error": "Score must be a number between 1 and 5"}
            
            rating = DimensionRating(
                feedback_id=feedback.id,
                dimension_id=dimension.id,  
                score=score_int,
                justification=justification,
                correct_response=correct_response
            )
            
            db.session.add(rating)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving feedback: {str(e)}")
            return {"error": f"Error saving feedback: {str(e)}"}
     
        EventPublisher.publish('feedback.submitted', {
            'feedback_id': str(feedback.id),
            'user_id': user_id,
            'response_id': str(response_id),
            'model_id': interaction.model_id
        })
        
     
        try:
            if has_role(user_id, 'validator'):
                ValidationService.auto_validate_validator_feedback(feedback.id, user_id)
                
            user_client = UserClient()
            user_client.update_contribution_points(user_id, 'feedback_submitted')
        except Exception as e:
            logger.error(f"Error in post-feedback processing: {str(e)}")
        
        return feedback
    
    @staticmethod
    def get_feedback(feedback_id, include_user_info=False):
        """
        Get feedback by ID with its dimension ratings.
        
        Args:
            feedback_id: ID of the feedback
            include_user_info: Whether to include user profile information
            
        Returns:
            Feedback object with ratings or None if not found
        """
        feedback = Feedback.query.options(
            db.joinedload(Feedback.dimension_ratings).joinedload(DimensionRating.dimension)
        ).get(feedback_id)
        
        if not feedback:
            return None
 
        if include_user_info and feedback:
            try:
                user_client = UserClient()
                user_profile = user_client.get_profile(feedback.user_id)
                if user_profile:
                 
                    g.user_profiles = getattr(g, 'user_profiles', {})
                    g.user_profiles[str(feedback.user_id)] = user_profile
            except Exception as e:
                logger.error(f"Error getting user profile: {str(e)}")
        
        return feedback
    
    @staticmethod
    def get_pending_feedback(page=1, per_page=10, model_id=None, include_user_info=False):
        """
        Get pending feedback awaiting validation.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            model_id: Optional filter by model ID
            include_user_info: Whether to include user profile information
            
        Returns:
            Tuple of (feedback items, total count)
        """
        query = Feedback.query.filter(Feedback.status == 'PENDING')
        
        if model_id:
            query = query.join(Response).join(Prompt).join(Interaction).filter(
                Interaction.model_id == model_id
            )
            
        query = query.order_by(Feedback.submitted_at.asc())  
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        if include_user_info and paginated.items:
            user_ids = [str(item.user_id) for item in paginated.items]
            try:
                user_client = UserClient()
                user_profiles = user_client.get_bulk_profiles(user_ids)
                if user_profiles:
                    g.user_profiles = getattr(g, 'user_profiles', {})
                    for user_id, profile in user_profiles.items():
                        g.user_profiles[user_id] = profile
            except Exception as e:
                logger.error(f"Error getting user profiles: {str(e)}")
        
        return paginated.items, paginated.total
    
    @staticmethod
    def get_user_feedback(user_id, page=1, per_page=10, status=None, include_user_info=False):
        """
        Get feedback submitted by a specific user.
        
        Args:
            user_id: ID of the user (string format matching Auth Service's public_id)
            page: Page number (1-indexed)
            per_page: Number of items per page
            status: Optional filter by feedback status
            include_user_info: Whether to include user profile information
            
        Returns:
            Tuple of (feedback items, total count)
        """
     
        user_id = str(user_id) if user_id else None
        
        query = Feedback.query.filter(Feedback.user_id == user_id)
        
        if status:
            query = query.filter(Feedback.status == status)
        
        query = query.order_by(Feedback.submitted_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        if include_user_info and paginated.items:
            try:
                user_client = UserClient()
                user_profile = user_client.get_profile(user_id)
                if user_profile:
                    g.user_profiles = getattr(g, 'user_profiles', {})
                    g.user_profiles[str(user_id)] = user_profile
            except Exception as e:
                logger.error(f"Error getting user profile: {str(e)}")
        
        return paginated.items, paginated.total
    
    @staticmethod
    def get_response_feedback(response_id, page=1, per_page=10, include_user_info=False):
        """
        Get all feedback for a specific response.
        
        Args:
            response_id: ID of the response
            page: Page number (1-indexed)
            per_page: Number of items per page
            include_user_info: Whether to include user profile information
            
        Returns:
            Tuple of (feedback items, total count)
        """
        query = Feedback.query.filter(Feedback.response_id == response_id)
        query = query.order_by(Feedback.submitted_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        if include_user_info and paginated.items:
            user_ids = [str(item.user_id) for item in paginated.items]
            try:
                user_client = UserClient()
                user_profiles = user_client.get_bulk_profiles(user_ids)
                if user_profiles:
                    g.user_profiles = getattr(g, 'user_profiles', {})
                    for user_id, profile in user_profiles.items():
                        g.user_profiles[user_id] = profile
            except Exception as e:
                logger.error(f"Error getting user profiles: {str(e)}")
        
        return paginated.items, paginated.total
    
    @staticmethod
    def get_feedback_with_connections(feedback_id, requesting_user_id):
        """
        Get feedback with information about the requesting user's connection to the feedback author.
        
        Args:
            feedback_id: ID of the feedback
            requesting_user_id: ID of the user requesting the feedback
            
        Returns:
            Feedback object enriched with connection information or None if not found
        """
        feedback = FeedbackService.get_feedback(feedback_id, include_user_info=True)
        
        if not feedback or requesting_user_id == feedback.user_id:
        
            return feedback
            
        try:
            user_client = UserClient()
            connections = user_client.get_user_connections(requesting_user_id)
            g.user_connections = getattr(g, 'user_connections', {})
            for connection in connections:
                other_user_id = connection.get('other_user_id')
                if other_user_id == str(feedback.user_id):
                    g.user_connections[str(feedback.user_id)] = {
                        'status': connection.get('status'),
                        'connected_since': connection.get('connected_since')
                    }
                    break
        except Exception as e:
            logger.error(f"Error getting user connections: {str(e)}")
            
        return feedback