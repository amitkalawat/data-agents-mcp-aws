import os
from typing import Dict, Any


class MSKConfig:
    """Configuration for AWS MSK (Managed Streaming for Apache Kafka)"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            "MSK_BOOTSTRAP_SERVERS", 
            "your-msk-cluster.kafka.us-east-1.amazonaws.com:9092"
        )
        self.security_protocol = os.getenv("MSK_SECURITY_PROTOCOL", "SSL")
        self.ssl_ca_location = os.getenv("MSK_SSL_CA_LOCATION", "/opt/kafka/ca-cert.pem")
        
        # Topics
        self.match_events_topic = os.getenv("MATCH_EVENTS_TOPIC", "soccer-match-events")
        self.user_interactions_topic = os.getenv("USER_INTERACTIONS_TOPIC", "soccer-user-interactions")
        self.combined_stream_topic = os.getenv("COMBINED_STREAM_TOPIC", "soccer-match-stream")
        
        # Consumer configuration
        self.consumer_group_id = os.getenv("CONSUMER_GROUP_ID", "soccer-analytics-group")
        self.auto_offset_reset = os.getenv("AUTO_OFFSET_RESET", "latest")
        
        # Producer configuration
        self.acks = os.getenv("PRODUCER_ACKS", "all")
        self.retries = int(os.getenv("PRODUCER_RETRIES", "3"))
        self.batch_size = int(os.getenv("PRODUCER_BATCH_SIZE", "16384"))
        self.linger_ms = int(os.getenv("PRODUCER_LINGER_MS", "10"))
        
        # Performance tuning
        self.compression_type = os.getenv("COMPRESSION_TYPE", "snappy")
        self.max_poll_records = int(os.getenv("MAX_POLL_RECORDS", "500"))
        
    def get_producer_config(self) -> Dict[str, Any]:
        """Get Kafka producer configuration"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'acks': self.acks,
            'retries': self.retries,
            'batch_size': self.batch_size,
            'linger_ms': self.linger_ms,
            'compression_type': self.compression_type,
            'value_serializer': lambda v: v.encode('utf-8') if isinstance(v, str) else v
        }
        
        if self.security_protocol == "SSL":
            config['ssl_cafile'] = self.ssl_ca_location
            
        return config
    
    def get_consumer_config(self) -> Dict[str, Any]:
        """Get Kafka consumer configuration"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'group_id': self.consumer_group_id,
            'auto_offset_reset': self.auto_offset_reset,
            'enable_auto_commit': True,
            'max_poll_records': self.max_poll_records,
            'value_deserializer': lambda m: m.decode('utf-8') if m else None
        }
        
        if self.security_protocol == "SSL":
            config['ssl_cafile'] = self.ssl_ca_location
            
        return config