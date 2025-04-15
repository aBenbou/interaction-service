# app/utils/event_publisher.py
import json
from typing import Dict, Any
import requests
from datetime import datetime
from flask import current_app

def publish_event(event_type: str, event_data: Dict[str, Any]) -> bool:
    """Publish an event to the event bus/message broker
    
    Args:
        event_type: Type of event (e.g., 'interaction.created')
        event_data: Event data
        
    Returns:
        True if published successfully, False otherwise
    """
    try:
        # Check if event publishing is enabled
        if not current_app.config.get('EVENT_BUS_ENABLED', False):
            current_app.logger.info(f"Event publishing disabled. Event type: {event_type}")
            return True
        
        # Prepare event
        event = {
            'type': event_type,
            'data': event_data,
            'service': 'interaction_service',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Determine event bus type and publish accordingly
        event_bus_type = current_app.config.get('EVENT_BUS_TYPE', 'http')
        
        if event_bus_type == 'http':
            return _publish_http(event)
        elif event_bus_type == 'rabbitmq':
            return _publish_rabbitmq(event)
        elif event_bus_type == 'kafka':
            return _publish_kafka(event)
        else:
            current_app.logger.error(f"Unsupported event bus type: {event_bus_type}")
            return False
    
    except Exception as e:
        current_app.logger.error(f"Error publishing event: {str(e)}")
        return False

def _publish_http(event: Dict[str, Any]) -> bool:
    """Publish event to HTTP endpoint"""
    try:
        event_bus_url = current_app.config['EVENT_BUS_URL']
        response = requests.post(
            event_bus_url,
            json=event,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except Exception as e:
        current_app.logger.error(f"HTTP event publishing error: {str(e)}")
        return False

def _publish_rabbitmq(event: Dict[str, Any]) -> bool:
    """Publish event to RabbitMQ"""
    try:
        # This would use pika or other RabbitMQ client
        current_app.logger.info("RabbitMQ publishing not implemented yet")
        return False
    except Exception as e:
        current_app.logger.error(f"RabbitMQ event publishing error: {str(e)}")
        return False

def _publish_kafka(event: Dict[str, Any]) -> bool:
    """Publish event to Kafka"""
    try:
        # This would use kafka-python or other Kafka client
        current_app.logger.info("Kafka publishing not implemented yet")
        return False
    except Exception as e:
        current_app.logger.error(f"Kafka event publishing error: {str(e)}")
        return False