# app/services/validation_service.py
import logging
from flask import current_app
from app import db
from app.models.feedback import Feedback
from app.models.validation import ValidationRecord
from app.utils.event_publisher import EventPublisher
from app.utils.auth_client import AuthClient, has_permission
from app.utils.user_client import UserClient, has_role
from app.services.dataset_service import DatasetService

logger = logging.getLogger(__name__)

class ValidationService:
    """Business logic for feedback validation."""
    
    @staticmethod
    def validate_feedback(feedback_id, validator_id, is_valid, notes=None):
        """
        Validate a feedback submission.
        
        Args:
            feedback_id: ID of the feedback
            validator_id: ID of the validator (string format matching Auth Service's public_id)
            is_valid: Boolean indicating if feedback is valid
            notes: Optional validation notes
            
        Returns:
            Created validation record or error dictionary
        """
        # Ensure validator_id is a string
        validator_id = str(validator_id) if validator_id else None
        
        # Check if user has validator expertise
        has_validator_role = has_role(validator_id, 'validator')
        is_admin_user = has_permission(validator_id, 'admin')
        
        if not (has_validator_role or is_admin_user):
            return {"error": "Not authorized to validate feedback. Validator expertise required."}
            
        # Check if feedback exists
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {"error": "Feedback not found"}
        
        # Check if feedback is already validated
        if feedback.status != 'PENDING':
            return {"error": "Feedback has already been validated"}
        
        # Ensure validator isn't validating their own feedback (unless they're an admin)
        if str(feedback.user_id) == str(validator_id) and not has_permission(validator_id, 'admin'):
            return {"error": "Validators cannot validate their own feedback"}
        
        # Create validation record
        validation = ValidationRecord(
            feedback_id=feedback_id,
            validator_id=validator_id,
            is_valid=is_valid,
            notes=notes
        )
        
        db.session.add(validation)
        
        # Update feedback status
        feedback.status = 'VALIDATED' if is_valid else 'REJECTED'
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving validation: {str(e)}")
            return {"error": f"Error saving validation: {str(e)}"}
        
        # Publish event
        event_type = 'feedback.validated' if is_valid else 'feedback.rejected'
        EventPublisher.publish(event_type, {
            'feedback_id': str(feedback.id),
            'validator_id': validator_id,  # Already a string, no conversion needed
            'is_valid': is_valid
        })
        
        # If valid, create dataset entry
        if is_valid:
            try:
                DatasetService.create_entry_from_feedback(feedback_id)
                
                # Update user progression
                # This would normally be handled by a separate service listening to events
                # but for simplicity we'll call it directly
                user_client = UserClient()
                user_client.update_contribution_points(feedback.user_id, 'feedback_validated')
            except Exception as e:
                # Don't fail the validation if dataset creation fails
                logger.error(f"Error in post-validation processing: {str(e)}")
        
        # Update validator contribution points
        try:
            user_client = UserClient()
            user_client.update_contribution_points(validator_id, 'validation_performed')
        except Exception as e:
            # Don't fail the validation if user service call fails
            logger.error(f"Error updating validator points: {str(e)}")
        
        return validation
    
    @staticmethod
    def auto_validate_validator_feedback(feedback_id, validator_id):
        """
        Automatically validate feedback created by validators.
        
        Args:
            feedback_id: ID of the feedback
            validator_id: ID of the validator who created the feedback (string format matching Auth Service's public_id)
            
        Returns:
            Created validation record or None if error
        """
        # Ensure validator_id is a string
        validator_id = str(validator_id) if validator_id else None
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return None
        
        # Create validation record for automatic validation
        validation = ValidationRecord(
            feedback_id=feedback_id,
            validator_id=validator_id,  # Self-validation
            is_valid=True,
            notes="Auto-validated (validator-created feedback)"
        )
        
        db.session.add(validation)
        
        # Update feedback status
        feedback.status = 'VALIDATED'
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error auto-validating feedback: {str(e)}")
            return None
        
        # Create dataset entry
        try:
            DatasetService.create_entry_from_feedback(feedback_id)
        except Exception as e:
            logger.error(f"Error creating dataset entry during auto-validation: {str(e)}")
        
        # Publish event
        EventPublisher.publish('feedback.auto_validated', {
            'feedback_id': str(feedback.id),
            'validator_id': validator_id  # Already a string, no conversion needed
        })
        
        return validation
    
    @staticmethod
    def get_validator_stats(validator_id):
        """
        Get validation statistics for a validator.
        
        Args:
            validator_id: ID of the validator (string format matching Auth Service's public_id)
            
        Returns:
            Dictionary with validation statistics
        """
        # Ensure validator_id is a string
        validator_id = str(validator_id) if validator_id else None
        
        total_validations = ValidationRecord.query.filter(
            ValidationRecord.validator_id == validator_id
        ).count()
        
        approved_validations = ValidationRecord.query.filter(
            ValidationRecord.validator_id == validator_id,
            ValidationRecord.is_valid == True
        ).count()
        
        recent_validations = ValidationRecord.query.filter(
            ValidationRecord.validator_id == validator_id
        ).order_by(ValidationRecord.validated_at.desc()).limit(10).all()
        
        return {
            'total_validations': total_validations,
            'approved_validations': approved_validations,
            'approval_rate': approved_validations / total_validations if total_validations > 0 else 0,
            'recent_validations': [v.to_dict() for v in recent_validations]
        }
