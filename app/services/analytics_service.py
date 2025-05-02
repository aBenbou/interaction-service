from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import db
from app.models.interaction import Interaction
from app.models.feedback import Feedback
from app.models.prompt import Prompt
from app.utils.user_client import user_client

class AnalyticsService:
    """Service for analytics and metrics."""
    
    @staticmethod
    def get_user_engagement_metrics(
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get user engagement metrics.
        
        Args:
            user_id: ID of the user
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with engagement metrics
        """
        interaction_query = Interaction.query.filter_by(user_id=user_id)
        
        if start_date:
            interaction_query = interaction_query.filter(Interaction.started_at >= start_date)
        if end_date:
            interaction_query = interaction_query.filter(Interaction.started_at <= end_date)
        
        total_interactions = interaction_query.count()
        completed_interactions = interaction_query.filter_by(status='COMPLETED').count()
        
        prompt_query = Prompt.query.join(Interaction).filter(Interaction.user_id == user_id)
        if start_date:
            prompt_query = prompt_query.filter(Prompt.created_at >= start_date)
        if end_date:
            prompt_query = prompt_query.filter(Prompt.created_at <= end_date)
        
        total_prompts = prompt_query.count()
 
        feedback_query = Feedback.query.filter_by(user_id=user_id)
        if start_date:
            feedback_query = feedback_query.filter(Feedback.created_at >= start_date)
        if end_date:
            feedback_query = feedback_query.filter(Feedback.created_at <= end_date)
        
        total_feedback = feedback_query.count()
        accepted_feedback = feedback_query.filter_by(validation_status='ACCEPTED').count()
        
        return {
            'success': True,
            'metrics': {
                'total_interactions': total_interactions,
                'completed_interactions': completed_interactions,
                'completion_rate': (completed_interactions / total_interactions * 100) if total_interactions > 0 else 0,
                'total_prompts': total_prompts,
                'prompts_per_interaction': (total_prompts / total_interactions) if total_interactions > 0 else 0,
                'total_feedback': total_feedback,
                'accepted_feedback': accepted_feedback,
                'feedback_acceptance_rate': (accepted_feedback / total_feedback * 100) if total_feedback > 0 else 0
            }
        }
    
    @staticmethod
    def get_model_performance_metrics(
        model_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get model performance metrics.
        
        Args:
            model_id: ID of the model
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with performance metrics
        """
      
        interaction_query = Interaction.query.filter_by(model_id=model_id)
        
        if start_date:
            interaction_query = interaction_query.filter(Interaction.started_at >= start_date)
        if end_date:
            interaction_query = interaction_query.filter(Interaction.started_at <= end_date)
        
        total_interactions = interaction_query.count()
        completed_interactions = interaction_query.filter_by(status='COMPLETED').count()
        
        feedback_query = Feedback.query.filter_by(model_id=model_id)
        if start_date:
            feedback_query = feedback_query.filter(Feedback.created_at >= start_date)
        if end_date:
            feedback_query = feedback_query.filter(Feedback.created_at <= end_date)
        
        category_ratings = {}
        for category in ['accuracy', 'relevance', 'helpfulness']:
            category_feedback = feedback_query.filter_by(category=category).all()
            if category_feedback:
                ratings = [f.rating for f in category_feedback if f.rating is not None]
                if ratings:
                    category_ratings[category] = {
                        'average': sum(ratings) / len(ratings),
                        'count': len(ratings)
                    }
       
        binary_feedback = feedback_query.filter(Feedback.binary_evaluation.isnot(None)).all()
        positive_evaluations = sum(1 for f in binary_feedback if f.binary_evaluation)
        
        return {
            'success': True,
            'metrics': {
                'total_interactions': total_interactions,
                'completed_interactions': completed_interactions,
                'completion_rate': (completed_interactions / total_interactions * 100) if total_interactions > 0 else 0,
                'category_ratings': category_ratings,
                'binary_evaluations': {
                    'total': len(binary_feedback),
                    'positive': positive_evaluations,
                    'positive_rate': (positive_evaluations / len(binary_feedback) * 100) if binary_feedback else 0
                }
            }
        }
    
    @staticmethod
    def get_system_metrics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get system-wide metrics.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with system metrics
        """
   
        interaction_query = Interaction.query
        feedback_query = Feedback.query
      
        if start_date:
            interaction_query = interaction_query.filter(Interaction.started_at >= start_date)
            feedback_query = feedback_query.filter(Feedback.created_at >= start_date)
        if end_date:
            interaction_query = interaction_query.filter(Interaction.started_at <= end_date)
            feedback_query = feedback_query.filter(Feedback.created_at <= end_date)
        
     
        total_interactions = interaction_query.count()
        active_users = interaction_query.distinct(Interaction.user_id).count()
        
        total_feedback = feedback_query.count()
        pending_validation = feedback_query.filter_by(validation_status='PENDING').count()
        accepted_feedback = feedback_query.filter_by(validation_status='ACCEPTED').count()
        
        response_times = []
        for interaction in interaction_query.all():
            prompts = Prompt.query.filter_by(interaction_id=interaction.id).all()
            for prompt in prompts:
                if prompt.response and prompt.response.processing_time_ms:
                    response_times.append(prompt.response.processing_time_ms)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'success': True,
            'metrics': {
                'total_interactions': total_interactions,
                'active_users': active_users,
                'interactions_per_user': (total_interactions / active_users) if active_users > 0 else 0,
                'total_feedback': total_feedback,
                'pending_validation': pending_validation,
                'accepted_feedback': accepted_feedback,
                'feedback_acceptance_rate': (accepted_feedback / total_feedback * 100) if total_feedback > 0 else 0,
                'average_response_time_ms': avg_response_time
            }
        } 