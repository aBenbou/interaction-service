# app/services/prompt_service.py
import logging
import time
from flask import current_app
from app import db
from app.models.interaction import Interaction
from app.models.prompt import Prompt
from app.models.response import Response
from app.utils.model_client import ModelClient
from app.utils.event_publisher import EventPublisher

logger = logging.getLogger(__name__)

class PromptService:
    """Business logic for handling prompts and responses."""
    
    @staticmethod
    def submit_prompt(interaction_id, content, context=None):
        """
        Submit a prompt and generate a response.
        
        Args:
            interaction_id: ID of the interaction
            content: Text content of the prompt
            context: Optional context dictionary
            
        Returns:
            Tuple of (prompt, response) or (error dict, None)
        """
        # Get interaction
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            return {"error": "Interaction not found"}, None
        
        if interaction.status != 'ACTIVE':
            return {"error": "Interaction is not active"}, None
        
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
            context=context or {}
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        # Publish event
        EventPublisher.publish('interaction.prompt_submitted', {
            'prompt_id': str(prompt.id),
            'interaction_id': str(interaction.id),
            'user_id': str(interaction.user_id)
        })
        
        # Generate response using the Model Service
        model_client = ModelClient()
        
        try:
            # Record start time for timing calculation
            start_time = time.time()
            
            # Call model service to generate response
            response_data = model_client.query_endpoint(
                endpoint_name=interaction.endpoint_name,
                query_text=content,
                context=context
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Handle errors from model service
            if 'error' in response_data:
                logger.error(f"Error from model service: {response_data['error']}")
                response = Response(
                    prompt_id=prompt.id,
                    content=f"Error: {response_data['error']}",
                    processing_time_ms=processing_time_ms,
                    model_endpoint=interaction.endpoint_name
                )
            else:
                # Extract response content based on model type
                response_content = response_data
                
                # Handle different response formats from different model types
                if isinstance(response_data, dict):
                    if 'generated_text' in response_data:
                        response_content = response_data['generated_text']
                    elif 'answer' in response_data:
                        response_content = response_data['answer']
                    elif 'response' in response_data:
                        response_content = response_data['response']
                    elif 'content' in response_data:
                        response_content = response_data['content']
                    else:
                        # If we can't find a standard field, use the whole response
                        response_content = str(response_data)
                
                # Create response
                response = Response(
                    prompt_id=prompt.id,
                    content=response_content,
                    processing_time_ms=processing_time_ms,
                    tokens_used=response_data.get('tokens_used') if isinstance(response_data, dict) else None,
                    model_endpoint=interaction.endpoint_name
                )
            
            db.session.add(response)
            db.session.commit()
            
            # Publish event
            EventPublisher.publish('interaction.response_received', {
                'response_id': str(response.id),
                'prompt_id': str(prompt.id),
                'interaction_id': str(interaction.id)
            })
            
            return prompt, response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            
            # Create error response
            response = Response(
                prompt_id=prompt.id,
                content="An error occurred while generating the response.",
                model_endpoint=interaction.endpoint_name
            )
            
            db.session.add(response)
            db.session.commit()
            
            return prompt, response
    
    @staticmethod
    def get_interaction_history(interaction_id):
        """
        Get all prompts and responses for an interaction.
        
        Args:
            interaction_id: ID of the interaction
            
        Returns:
            List of prompt-response pairs in chronological order
        """
        prompts = Prompt.query.filter(
            Prompt.interaction_id == interaction_id
        ).order_by(Prompt.sequence_number).all()
        
        history = []
        for prompt in prompts:
            history.append({
                'prompt': prompt.to_dict(),
                'response': prompt.response.to_dict() if prompt.response else None
            })
        
        return history
    
    @staticmethod
    def submit_chat_message(interaction_id, message, system_prompt=None):
        """
        Submit a chat message using the OpenAI-compatible chat completion endpoint.
        
        Args:
            interaction_id: ID of the interaction
            message: User message content
            system_prompt: Optional system prompt
            
        Returns:
            Tuple of (prompt, response) or (error dict, None)
        """
        # Get interaction
        interaction = Interaction.query.get(interaction_id)
        if not interaction:
            return {"error": "Interaction not found"}, None
        
        if interaction.status != 'ACTIVE':
            return {"error": "Interaction is not active"}, None
        
        # Build chat history from previous prompts/responses
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Get previous messages
        previous_exchanges = PromptService.get_interaction_history(interaction_id)
        for exchange in previous_exchanges:
            prompt_content = exchange['prompt']['content'] if exchange['prompt'] else ""
            messages.append({"role": "user", "content": prompt_content})
            
            response_content = exchange['response']['content'] if exchange['response'] else ""
            if response_content:
                messages.append({"role": "assistant", "content": response_content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Create prompt record
        sequence_number = len(previous_exchanges) + 1
        prompt = Prompt(
            interaction_id=interaction_id,
            content=message,
            sequence_number=sequence_number,
            context={"system_prompt": system_prompt} if system_prompt else {}
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        # Publish event
        EventPublisher.publish('interaction.chat_message_submitted', {
            'prompt_id': str(prompt.id),
            'interaction_id': str(interaction.id),
            'user_id': str(interaction.user_id)
        })
        
        # Generate response using chat completion endpoint
        model_client = ModelClient()
        
        try:
            # Record start time for timing calculation
            start_time = time.time()
            
            # Call model service chat completion
            response_data = model_client.chat_completion(
                model_id=interaction.model_id,
                messages=messages
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Handle errors from model service
            if 'error' in response_data:
                logger.error(f"Error from chat completion: {response_data['error']}")
                response = Response(
                    prompt_id=prompt.id,
                    content=f"Error: {response_data['error']}",
                    processing_time_ms=processing_time_ms,
                    model_endpoint=interaction.endpoint_name
                )
            else:
                # Extract response content
                response_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                if not response_content:
                    logger.warning("Received empty or malformed response from chat completion")
                    response_content = "No response generated."
                
                # Get token usage if available
                tokens_used = response_data.get('usage', {}).get('total_tokens')
                
                # Create response
                response = Response(
                    prompt_id=prompt.id,
                    content=response_content,
                    processing_time_ms=processing_time_ms,
                    tokens_used=tokens_used,
                    model_endpoint=interaction.endpoint_name
                )
            
            db.session.add(response)
            db.session.commit()
            
            # Publish event
            EventPublisher.publish('interaction.chat_response_received', {
                'response_id': str(response.id),
                'prompt_id': str(prompt.id),
                'interaction_id': str(interaction.id)
            })
            
            return prompt, response
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            
            # Create error response
            response = Response(
                prompt_id=prompt.id,
                content="An error occurred while generating the chat response.",
                model_endpoint=interaction.endpoint_name
            )
            
            db.session.add(response)
            db.session.commit()
            
            return prompt, response