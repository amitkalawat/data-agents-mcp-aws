import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from msk_config import MSKConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoccerStreamConsumer:
    """Kafka consumer for processing soccer match and user interaction streams"""
    
    def __init__(self, config: Optional[MSKConfig] = None):
        self.config = config or MSKConfig()
        self.consumer = None
        self.handlers = {
            'match_event': self._default_match_event_handler,
            'user_interaction': self._default_user_interaction_handler
        }
        self.stats = {
            'messages_processed': 0,
            'match_events': 0,
            'user_interactions': 0,
            'errors': 0
        }
    
    def subscribe(self, topics: Optional[list] = None):
        """Subscribe to Kafka topics"""
        if not topics:
            topics = [
                self.config.match_events_topic,
                self.config.user_interactions_topic,
                self.config.combined_stream_topic
            ]
        
        try:
            consumer_config = self.config.get_consumer_config()
            consumer_config['value_deserializer'] = lambda m: json.loads(m.decode('utf-8')) if m else None
            
            self.consumer = KafkaConsumer(**consumer_config)
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to subscribe to topics: {e}")
            raise
    
    def set_match_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set custom handler for match events"""
        self.handlers['match_event'] = handler
    
    def set_user_interaction_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set custom handler for user interactions"""
        self.handlers['user_interaction'] = handler
    
    def consume(self, max_messages: Optional[int] = None):
        """Consume messages from subscribed topics"""
        messages_consumed = 0
        
        try:
            for message in self.consumer:
                try:
                    self._process_message(message)
                    messages_consumed += 1
                    
                    if max_messages and messages_consumed >= max_messages:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.stats['errors'] += 1
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()
    
    def _process_message(self, message):
        """Process individual Kafka message"""
        try:
            data = message.value
            self.stats['messages_processed'] += 1
            
            # Process based on message content
            if data.get('match_event'):
                self.stats['match_events'] += 1
                self.handlers['match_event'](data['match_event'])
            
            if data.get('user_interaction'):
                self.stats['user_interactions'] += 1
                self.handlers['user_interaction'](data['user_interaction'])
            
            # Log message metadata
            logger.debug(f"Processed message from {message.topic} "
                        f"partition {message.partition} offset {message.offset}")
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise
    
    def _default_match_event_handler(self, event: Dict[str, Any]):
        """Default handler for match events"""
        event_type = event.get('event_type', 'unknown')
        minute = event.get('minute', 0)
        logger.info(f"Match Event: {event_type} at minute {minute}")
    
    def _default_user_interaction_handler(self, interaction: Dict[str, Any]):
        """Default handler for user interactions"""
        action_type = interaction.get('action_type', 'unknown')
        user_id = interaction.get('user_id', 'unknown')
        logger.info(f"User Interaction: {action_type} by user {user_id}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get consumer statistics"""
        return self.stats.copy()
    
    def close(self):
        """Close consumer connection"""
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer connection closed")
            logger.info(f"Final stats: {self.get_stats()}")


class AnalyticsConsumer(SoccerStreamConsumer):
    """Extended consumer with real-time analytics capabilities"""
    
    def __init__(self, config: Optional[MSKConfig] = None):
        super().__init__(config)
        self.analytics = {
            'active_users': set(),
            'events_by_type': {},
            'user_actions_by_type': {},
            'events_timeline': []
        }
    
    def _process_analytics(self, data: Dict[str, Any]):
        """Process message for analytics"""
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
        
        if data.get('match_event'):
            event = data['match_event']
            event_type = event.get('event_type', 'unknown')
            
            # Count events by type
            self.analytics['events_by_type'][event_type] = \
                self.analytics['events_by_type'].get(event_type, 0) + 1
            
            # Add to timeline
            self.analytics['events_timeline'].append({
                'timestamp': timestamp,
                'type': 'match_event',
                'event_type': event_type,
                'minute': event.get('minute', 0)
            })
        
        if data.get('user_interaction'):
            interaction = data['user_interaction']
            user_id = interaction.get('user_id')
            action_type = interaction.get('action_type', 'unknown')
            
            # Track active users
            if user_id:
                self.analytics['active_users'].add(user_id)
            
            # Count actions by type
            self.analytics['user_actions_by_type'][action_type] = \
                self.analytics['user_actions_by_type'].get(action_type, 0) + 1
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        return {
            'active_users_count': len(self.analytics['active_users']),
            'events_by_type': self.analytics['events_by_type'],
            'user_actions_by_type': self.analytics['user_actions_by_type'],
            'timeline_events_count': len(self.analytics['events_timeline'])
        }