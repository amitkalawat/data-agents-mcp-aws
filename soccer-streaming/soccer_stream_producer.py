import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

from soccer_match_schema import StreamMessage, MatchEvent, UserInteraction, EventType, UserActionType
from msk_config import MSKConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoccerStreamProducer:
    """Kafka producer for streaming soccer match and user interaction data"""
    
    def __init__(self, config: Optional[MSKConfig] = None):
        self.config = config or MSKConfig()
        self.producer = None
        self._init_producer()
    
    def _init_producer(self):
        """Initialize Kafka producer with MSK configuration"""
        try:
            producer_config = self.config.get_producer_config()
            producer_config['value_serializer'] = lambda v: json.dumps(v).encode('utf-8')
            
            self.producer = KafkaProducer(**producer_config)
            logger.info(f"Connected to MSK cluster: {self.config.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to MSK: {e}")
            raise
    
    def send_match_event(self, match_event: MatchEvent) -> None:
        """Send match event to Kafka"""
        try:
            message = StreamMessage(
                message_id=str(uuid.uuid4()),
                match_id=match_event.match_id,
                timestamp=datetime.utcnow(),
                match_event=match_event
            )
            
            future = self.producer.send(
                self.config.match_events_topic,
                value=message.to_dict(),
                key=match_event.match_id.encode('utf-8')
            )
            
            # Handle success/failure
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
        except Exception as e:
            logger.error(f"Error sending match event: {e}")
            raise
    
    def send_user_interaction(self, user_interaction: UserInteraction) -> None:
        """Send user interaction to Kafka"""
        try:
            message = StreamMessage(
                message_id=str(uuid.uuid4()),
                match_id=user_interaction.match_id,
                timestamp=datetime.utcnow(),
                user_interaction=user_interaction
            )
            
            future = self.producer.send(
                self.config.user_interactions_topic,
                value=message.to_dict(),
                key=user_interaction.user_id.encode('utf-8')
            )
            
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
        except Exception as e:
            logger.error(f"Error sending user interaction: {e}")
            raise
    
    def send_combined_stream(self, match_event: Optional[MatchEvent] = None, 
                           user_interaction: Optional[UserInteraction] = None) -> None:
        """Send combined stream message containing both match event and user interaction"""
        try:
            if not match_event and not user_interaction:
                raise ValueError("At least one of match_event or user_interaction must be provided")
            
            match_id = match_event.match_id if match_event else user_interaction.match_id
            
            message = StreamMessage(
                message_id=str(uuid.uuid4()),
                match_id=match_id,
                timestamp=datetime.utcnow(),
                match_event=match_event,
                user_interaction=user_interaction
            )
            
            future = self.producer.send(
                self.config.combined_stream_topic,
                value=message.to_dict(),
                key=match_id.encode('utf-8')
            )
            
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
        except Exception as e:
            logger.error(f"Error sending combined stream: {e}")
            raise
    
    def _on_send_success(self, record_metadata):
        """Callback for successful message send"""
        logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} "
                   f"at offset {record_metadata.offset}")
    
    def _on_send_error(self, excp):
        """Callback for failed message send"""
        logger.error(f"Failed to send message: {excp}")
    
    def flush(self):
        """Flush all pending messages"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Producer connection closed")


class BatchProducer(SoccerStreamProducer):
    """Extended producer with batch processing capabilities"""
    
    def send_batch_events(self, events: list) -> Dict[str, int]:
        """Send multiple events in batch"""
        stats = {"match_events": 0, "user_interactions": 0, "errors": 0}
        
        for event in events:
            try:
                if isinstance(event, MatchEvent):
                    self.send_match_event(event)
                    stats["match_events"] += 1
                elif isinstance(event, UserInteraction):
                    self.send_user_interaction(event)
                    stats["user_interactions"] += 1
            except Exception as e:
                logger.error(f"Error processing batch event: {e}")
                stats["errors"] += 1
        
        self.flush()
        return stats