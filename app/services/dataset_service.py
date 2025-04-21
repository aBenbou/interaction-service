# app/services/dataset_service.py
import logging
import json
import csv
from io import StringIO
from flask import current_app
from app import db
from app.models.feedback import Feedback
from app.models.response import Response
from app.models.prompt import Prompt
from app.models.interaction import Interaction
from app.models.dataset import DatasetEntry
from app.utils.event_publisher import EventPublisher

logger = logging.getLogger(__name__)

class DatasetService:
    """Business logic for dataset management."""
    
    @staticmethod
    def create_entry_from_feedback(feedback_id):
        """
        Create a dataset entry from validated feedback.
        
        Args:
            feedback_id: ID of the validated feedback
            
        Returns:
            Created dataset entry or existing entry if already exists
        """
        # Check if entry already exists
        existing = DatasetEntry.query.filter(DatasetEntry.feedback_id == feedback_id).first()
        if existing:
            return existing
        
        # Get related data
        feedback = Feedback.query.get(feedback_id)
        if not feedback or feedback.status != 'VALIDATED':
            return {"error": "Feedback not found or not validated"}
            
        response = Response.query.get(feedback.response_id)
        if not response:
            return {"error": "Associated response not found"}
            
        prompt = Prompt.query.get(response.prompt_id)
        if not prompt:
            return {"error": "Associated prompt not found"}
            
        interaction = Interaction.query.get(prompt.interaction_id)
        if not interaction:
            return {"error": "Associated interaction not found"}
        
        # Find any correction from dimension ratings
        correct_response = None
        dimension_ratings_data = []
        
        for rating in feedback.dimension_ratings:
            dimension_data = {
                'dimension_id': str(rating.dimension_id),
                'dimension_name': rating.dimension.name if rating.dimension else "Unknown",
                'score': rating.score,
                'justification': rating.justification
            }
            
            if rating.correct_response:
                correct_response = rating.correct_response
                dimension_data['correct_response'] = correct_response
                
            dimension_ratings_data.append(dimension_data)
        
        # Create dataset entry
        entry = DatasetEntry(
            feedback_id=feedback_id,
            model_id=interaction.model_id,
            prompt_text=prompt.content,
            response_text=response.content,
            correct_response=correct_response,
            metadata={
                'model_version': interaction.model_version,
                'endpoint_name': interaction.endpoint_name,
                'dimension_ratings': dimension_ratings_data,
                'overall_comment': feedback.overall_comment,
                'feedback_user_id': str(feedback.user_id),
                'interaction_id': str(interaction.id)
            }
        )
        
        db.session.add(entry)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating dataset entry: {str(e)}")
            return {"error": f"Error creating dataset entry: {str(e)}"}
        
        # Publish event
        EventPublisher.publish('dataset.entry_created', {
            'entry_id': str(entry.id),
            'model_id': entry.model_id,
            'feedback_id': str(feedback_id)
        })
        
        return entry
    
    @staticmethod
    def get_model_dataset(model_id, page=1, per_page=100):
        """
        Get dataset entries for a specific model.
        
        Args:
            model_id: ID of the model
            page: Page number (1-indexed)
            per_page: Number of items per page
            
        Returns:
            Tuple of (dataset entries, total count)
        """
        query = DatasetEntry.query.filter(DatasetEntry.model_id == model_id)
        query = query.order_by(DatasetEntry.created_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return paginated.items, paginated.total
    
    @staticmethod
    def export_dataset(model_id, format='json'):
        """
        Export dataset for a specific model.
        
        Args:
            model_id: ID of the model
            format: Export format ('json' or 'csv')
            
        Returns:
            Dataset in the requested format or error dictionary
        """
        entries = DatasetEntry.query.filter(DatasetEntry.model_id == model_id).all()
        
        if not entries:
            return {"error": f"No dataset entries found for model {model_id}"}
        
        if format == 'json':
            dataset = [entry.to_training_format() for entry in entries]
            return json.dumps(dataset, indent=2)
        elif format == 'csv':
            # Simplified CSV export
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['prompt', 'response', 'correct_response', 'average_rating'])
            
            for entry in entries:
                # Calculate average rating
                ratings = entry.metadata.get('dimension_ratings', [])
                avg_rating = 0
                if ratings:
                    avg_rating = sum(r.get('score', 0) for r in ratings) / len(ratings)
                
                writer.writerow([
                    entry.prompt_text,
                    entry.response_text,
                    entry.correct_response or '',
                    f"{avg_rating:.2f}"
                ])
                
            return output.getvalue()
        else:
            return {"error": "Unsupported format. Use 'json' or 'csv'"}