from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models.feedback import Feedback
from app.models.interaction import Interaction
from app.utils.user_client import user_client

class LeaderboardService:
    """Service for managing leaderboards and user rankings."""
    
    @staticmethod
    def get_user_rankings(
        time_period: str = 'all_time',
        category: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get user rankings based on various metrics.
        
        Args:
            time_period: Time period for rankings ('daily', 'weekly', 'monthly', 'all_time')
            category: Optional category filter
            limit: Number of users to return
            
        Returns:
            Dictionary with user rankings and metrics
        """
     
        now = datetime.utcnow()
        if time_period == 'daily':
            start_date = now - timedelta(days=1)
        elif time_period == 'weekly':
            start_date = now - timedelta(weeks=1)
        elif time_period == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = None
        
        feedback_query = db.session.query(
            Feedback.user_id,
            func.count(Feedback.id).label('feedback_count'),
            func.sum(case(
                (Feedback.validation_status == 'ACCEPTED', 1),
                else_=0
            )).label('accepted_feedback')
        ).group_by(Feedback.user_id)
        
        if start_date:
            feedback_query = feedback_query.filter(Feedback.created_at >= start_date)
        if category:
            feedback_query = feedback_query.filter(Feedback.category == category)
            
        interaction_query = db.session.query(
            Interaction.user_id,
            func.count(Interaction.id).label('interaction_count'),
            func.sum(case(
                (Interaction.status == 'COMPLETED', 1),
                else_=0
            )).label('completed_interactions')
        ).group_by(Interaction.user_id)
        
        if start_date:
            interaction_query = interaction_query.filter(Interaction.started_at >= start_date)
            
        user_metrics = {}
        for user_id, feedback_count, accepted_feedback in feedback_query.all():
            if user_id not in user_metrics:
                user_metrics[user_id] = {
                    'feedback_count': 0,
                    'accepted_feedback': 0,
                    'interaction_count': 0,
                    'completed_interactions': 0,
                    'total_points': 0
                }
            user_metrics[user_id]['feedback_count'] = feedback_count
            user_metrics[user_id]['accepted_feedback'] = accepted_feedback
            user_metrics[user_id]['total_points'] += (feedback_count * 5) + (accepted_feedback * 10)
        for user_id, interaction_count, completed_interactions in interaction_query.all():
            if user_id not in user_metrics:
                user_metrics[user_id] = {
                    'feedback_count': 0,
                    'accepted_feedback': 0,
                    'interaction_count': 0,
                    'completed_interactions': 0,
                    'total_points': 0
                }
            user_metrics[user_id]['interaction_count'] = interaction_count
            user_metrics[user_id]['completed_interactions'] = completed_interactions
            user_metrics[user_id]['total_points'] += (interaction_count * 2) + (completed_interactions * 5)
      
        sorted_users = sorted(
            user_metrics.items(),
            key=lambda x: x[1]['total_points'],
            reverse=True
        )[:limit]
        
        user_ids = [user_id for user_id, _ in sorted_users]
        try:
            user_profiles = user_client.get_bulk_profiles(user_ids)
        except Exception as e:
            logger.error(f"Error fetching user profiles: {str(e)}")
            user_profiles = {}
    
        rankings = []
        for rank, (user_id, metrics) in enumerate(sorted_users, 1):
            user_profile = user_profiles.get(str(user_id), {})
            rankings.append({
                'rank': rank,
                'user_id': str(user_id),
                'username': user_profile.get('username', 'Unknown'),
                'display_name': user_profile.get('display_name', 'Unknown'),
                'metrics': metrics
            })
            
        return {
            'success': True,
            'time_period': time_period,
            'category': category,
            'rankings': rankings
        }
    
    @staticmethod
    def get_user_achievements(user_id: str) -> Dict[str, Any]:
        """
        Get achievements and badges for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with user achievements
        """
    
        feedback_count = Feedback.query.filter_by(user_id=user_id).count()
        accepted_feedback = Feedback.query.filter_by(
            user_id=user_id,
            validation_status='ACCEPTED'
        ).count()
        
        interaction_count = Interaction.query.filter_by(user_id=user_id).count()
        completed_interactions = Interaction.query.filter_by(
            user_id=user_id,
            status='COMPLETED'
        ).count()
        
      
        achievements = []
        if feedback_count >= 100:
            achievements.append({
                'name': 'Feedback Master',
                'description': 'Submitted 100+ feedback entries',
                'icon': 'star',
                'unlocked_at': datetime.utcnow().isoformat()
            })
            
        if accepted_feedback >= 50:
            achievements.append({
                'name': 'Quality Contributor',
                'description': 'Had 50+ feedback entries accepted',
                'icon': 'check-circle',
                'unlocked_at': datetime.utcnow().isoformat()
            })
            
        if interaction_count >= 50:
            achievements.append({
                'name': 'Active User',
                'description': 'Completed 50+ interactions',
                'icon': 'activity',
                'unlocked_at': datetime.utcnow().isoformat()
            })
            
        if completed_interactions >= 25:
            achievements.append({
                'name': 'Dedicated Tester',
                'description': 'Completed 25+ full interactions',
                'icon': 'award',
                'unlocked_at': datetime.utcnow().isoformat()
            })
            
        return {
            'success': True,
            'achievements': achievements,
            'metrics': {
                'feedback_count': feedback_count,
                'accepted_feedback': accepted_feedback,
                'interaction_count': interaction_count,
                'completed_interactions': completed_interactions
            }
        } 