from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class EventType(Enum):
    """Types of events in a soccer match"""
    MATCH_START = "match_start"
    MATCH_END = "match_end"
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    HALF_TIME = "half_time"
    PENALTY = "penalty"
    CORNER = "corner"
    FOUL = "foul"
    OFFSIDE = "offside"
    VAR_REVIEW = "var_review"


class UserActionType(Enum):
    """Types of user actions during match"""
    VIEW_START = "view_start"
    VIEW_END = "view_end"
    REACTION = "reaction"
    COMMENT = "comment"
    SHARE = "share"
    PREDICTION = "prediction"
    BET_PLACED = "bet_placed"
    PLAYER_RATING = "player_rating"
    HIGHLIGHT_SAVED = "highlight_saved"


@dataclass
class MatchEvent:
    """Soccer match event data"""
    match_id: str
    event_id: str
    event_type: EventType
    timestamp: datetime
    minute: int
    team_id: Optional[str] = None
    player_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserInteraction:
    """User interaction during match"""
    user_id: str
    match_id: str
    interaction_id: str
    action_type: UserActionType
    timestamp: datetime
    session_id: str
    device_type: str
    location: Optional[Dict[str, float]] = None  # lat, lon
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class StreamMessage:
    """Combined message for Kafka streaming"""
    message_id: str
    match_id: str
    timestamp: datetime
    match_event: Optional[MatchEvent] = None
    user_interaction: Optional[UserInteraction] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message_id": self.message_id,
            "match_id": self.match_id,
            "timestamp": self.timestamp.isoformat(),
            "match_event": {
                "match_id": self.match_event.match_id,
                "event_id": self.match_event.event_id,
                "event_type": self.match_event.event_type.value,
                "timestamp": self.match_event.timestamp.isoformat(),
                "minute": self.match_event.minute,
                "team_id": self.match_event.team_id,
                "player_id": self.match_event.player_id,
                "metadata": self.match_event.metadata
            } if self.match_event else None,
            "user_interaction": {
                "user_id": self.user_interaction.user_id,
                "match_id": self.user_interaction.match_id,
                "interaction_id": self.user_interaction.interaction_id,
                "action_type": self.user_interaction.action_type.value,
                "timestamp": self.user_interaction.timestamp.isoformat(),
                "session_id": self.user_interaction.session_id,
                "device_type": self.user_interaction.device_type,
                "location": self.user_interaction.location,
                "metadata": self.user_interaction.metadata
            } if self.user_interaction else None
        }