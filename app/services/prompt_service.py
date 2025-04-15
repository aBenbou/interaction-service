# app/services/prompt_service.py
from typing import Dict, Tuple, Optional, Any
from uuid import UUID
from flask import current_app
from app import db
from app.models.interaction import Interaction
from app.models.prompt import Prompt
from app.models.response import Response
from app.utils.event_publisher import publish_event
from app.utils.model_client import ModelClient

class PromptService:
    """Business logic for prompt handling."""
    
    @staticmethod
    def submit_prompt(interaction_id: UUID, content: str, 
                     context: Dict = None, client_metadata: Dict = None) -> Tuple[Prompt, Optional[Response]]:
        """Submit a prompt and generate a response."""
        # Get interaction
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            return None, None
        
        # Get next sequence number
        last_prompt = Prompt.query.filter(
            Prompt.interaction_id == interaction_id
        ).order_by(Prompt.sequence_number.desc()).first()
        
        sequence_number = 1
        if last_prompt:
            sequence_number = last_prompt.sequence_number + 1
        
        # Create prompt
        prompt = Prompt(
            interaction_id=interaction_id,
            content=content,
            sequence_number=sequence_number,
            context=context or {},
            client_metadata=client_metadata or {}
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        # Publish event
        publish_event('interaction.prompt_submitted', {
            'prompt_id': str(prompt.id),
            'interaction_id': str(interaction.id),
            'user_id': str(interaction.user_id),
            'sequence_number': prompt.sequence_number
        })
        
        # Generate response using the Model Service
        try:
            # Call model service to generate response
            response_data = ModelClient.generate_response(
                prompt.content,
                model_id=interaction.model_id,
                model_version=interaction.model_version,
                context=context
            )
            
            # Create response
            response = Response(
                prompt_id=prompt.id,
                content=response_data.get('content', ''),
                processing_time_ms=response_data.get('processing_time_ms'),
                tokens_used=response_data.get('tokens_used'),
                model_confidence=response_data.get('confidence')
            )
            
            db.session.add(response)
            db.session.commit()
            
            # Publish event
            publish_event('interaction.response_received', {
                'response_id': str(response.id),
                'prompt_id': str(prompt.id),
                'interaction_id': str(interaction.id),
                'user_id': str(interaction.user_id),
                'processing_time_ms': response.processing_time_ms
            })
            
            return prompt, response
            
        except Exception as e:
            # Log the error
            current_app.logger.error(f"Error generating response: {str(e)}")
            
            # Create error response
            response = Response(
                prompt_id=prompt.id,
                content="An error occurred while generating the response.",
                error=str(e)
            )
            
            db.session.add(response)
            db.session.commit()
            
            return prompt, response