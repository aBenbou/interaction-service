# app/services/dimension_service.py
import logging
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.dimension import EvaluationDimension
from app.utils.model_client import ModelClient
from app.utils.model_constants import get_default_dimensions_for_task
from app.utils.event_publisher import EventPublisher

logger = logging.getLogger(__name__)

class DimensionService:
    """Business logic for evaluation dimensions."""
    
    @staticmethod
    def create_dimension(model_id, name, description, created_by):
        """
        Create a new evaluation dimension.
        
        Args:
            model_id: ID of the model
            name: Name of the dimension
            description: Description of the dimension
            created_by: ID of the user creating the dimension
            
        Returns:
            Created dimension or error dictionary
        """
        # Validate model exists if it's not a special case
        if model_id != 'all':
            model_client = ModelClient()
            if not model_client.validate_model(model_id):
                return {"error": "Model not found or not deployed"}
        
        # Check if dimension already exists for this model
        existing = EvaluationDimension.query.filter(
            EvaluationDimension.model_id == model_id,
            EvaluationDimension.name == name
        ).first()
        
        if existing:
            return {"error": "Dimension with this name already exists for this model"}
        
        dimension = EvaluationDimension(
            model_id=model_id,
            name=name,
            description=description,
            created_by=created_by
        )
        
        try:
            db.session.add(dimension)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Dimension with this name already exists for this model"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating dimension: {str(e)}")
            return {"error": f"Error creating dimension: {str(e)}"}
        
        # Publish event
        EventPublisher.publish('dimension.created', {
            'dimension_id': str(dimension.id),
            'model_id': dimension.model_id,
            'name': dimension.name,
            'created_by': str(dimension.created_by)
        })
        
        return dimension
    
    @staticmethod
    def get_model_dimensions(model_id, active_only=True):
        """
        Get all dimensions for a specific model.
        
        Args:
            model_id: ID of the model
            active_only: Filter to active dimensions only
            
        Returns:
            List of dimensions
        """
        query = EvaluationDimension.query.filter(
            (EvaluationDimension.model_id == model_id) | 
            (EvaluationDimension.model_id == 'all')
        )
        
        if active_only:
            query = query.filter(EvaluationDimension.is_active == True)
        
        dimensions = query.all()
        
        # If no dimensions found, create default ones based on model type
        if not dimensions:
            # Check with model service for the model's task
            model_client = ModelClient()
            default_dimensions = model_client.get_model_dimensions(model_id)
            
            if default_dimensions:
                # Convert to DB objects but don't save yet
                return [
                    EvaluationDimension(
                        id=dim.get('id'),
                        model_id=model_id,
                        name=dim.get('name'),
                        description=dim.get('description'),
                        created_by='00000000-0000-0000-0000-000000000000',  # System user
                        is_active=True
                    )
                    for dim in default_dimensions
                ]
        
        return dimensions
    
    @staticmethod
    def update_dimension(dimension_id, name=None, description=None, is_active=None):
        """
        Update an evaluation dimension.
        
        Args:
            dimension_id: ID of the dimension
            name: Optional new name
            description: Optional new description
            is_active: Optional new active status
            
        Returns:
            Updated dimension or error dictionary
        """
        dimension = EvaluationDimension.query.get(dimension_id)
        if not dimension:
            return {"error": "Dimension not found"}
        
        if name is not None:
            # Check for name conflicts
            existing = EvaluationDimension.query.filter(
                EvaluationDimension.model_id == dimension.model_id,
                EvaluationDimension.name == name,
                EvaluationDimension.id != dimension_id
            ).first()
            
            if existing:
                return {"error": "Another dimension with this name already exists for this model"}
            
            dimension.name = name
            
        if description is not None:
            dimension.description = description
            
        if is_active is not None:
            dimension.is_active = is_active
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating dimension: {str(e)}")
            return {"error": f"Error updating dimension: {str(e)}"}
        
        # Publish event
        EventPublisher.publish('dimension.updated', {
            'dimension_id': str(dimension.id),
            'model_id': dimension.model_id,
            'name': dimension.name,
            'is_active': dimension.is_active
        })
        
        return dimension
    
    @staticmethod
    def delete_dimension(dimension_id):
        """
        Delete an evaluation dimension.
        
        Args:
            dimension_id: ID of the dimension
            
        Returns:
            Success dictionary or error dictionary
        """
        dimension = EvaluationDimension.query.get(dimension_id)
        if not dimension:
            return {"error": "Dimension not found"}
        
        try:
            db.session.delete(dimension)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting dimension: {str(e)}")
            return {"error": f"Error deleting dimension: {str(e)}"}
        
        # Publish event
        EventPublisher.publish('dimension.deleted', {
            'dimension_id': str(dimension_id),
            'model_id': dimension.model_id,
            'name': dimension.name
        })
        
        return {"success": True, "message": f"Dimension {dimension_id} deleted"}
    
    @staticmethod
    def create_default_dimensions(model_id, task, created_by):
        """
        Create default dimensions for a model based on its task.
        
        Args:
            model_id: ID of the model
            task: Task of the model
            created_by: ID of the user creating the dimensions
            
        Returns:
            List of created dimensions
        """
        # Get default dimensions for this task
        default_dims = get_default_dimensions_for_task(task)
        created_dimensions = []
        
        for dim in default_dims:
            dimension = EvaluationDimension(
                model_id=model_id,
                name=dim['name'],
                description=dim['description'],
                created_by=created_by
            )
            
            try:
                db.session.add(dimension)
                db.session.commit()
                created_dimensions.append(dimension)
                
                # Publish event
                EventPublisher.publish('dimension.created', {
                    'dimension_id': str(dimension.id),
                    'model_id': dimension.model_id,
                    'name': dimension.name,
                    'created_by': str(dimension.created_by)
                })
                
            except IntegrityError:
                db.session.rollback()
                logger.info(f"Dimension {dim['name']} already exists for model {model_id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating dimension: {str(e)}")
        
        return created_dimensions