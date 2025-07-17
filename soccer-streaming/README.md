# Soccer Streaming Datasource

A real-time data streaming solution for live soccer matches using AWS MSK (Managed Streaming for Apache Kafka). This system captures both match events and user interactions during live games.

## Overview

This datasource streams two types of data:
1. **Match Events** - Goals, cards, substitutions, and other game events
2. **User Interactions** - Viewer reactions, comments, shares, predictions, and bets

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Match Events   │────▶│   AWS MSK       │────▶│   Consumers     │
└─────────────────┘     │   (Kafka)       │     └─────────────────┘
                        │                 │
┌─────────────────┐     │ Topics:         │     ┌─────────────────┐
│User Interactions│────▶│ - match-events  │────▶│   Analytics     │
└─────────────────┘     │ - user-actions  │     └─────────────────┘
                        │ - combined      │
                        └─────────────────┘
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Configure AWS MSK connection via environment variables:

```bash
# Required
export MSK_BOOTSTRAP_SERVERS="your-cluster.kafka.us-east-1.amazonaws.com:9092"

# Optional
export MSK_SECURITY_PROTOCOL="SSL"  # Default: SSL
export MATCH_EVENTS_TOPIC="soccer-match-events"  # Default topic name
export USER_INTERACTIONS_TOPIC="soccer-user-interactions"
export CONSUMER_GROUP_ID="soccer-analytics-group"
```

## Usage

### 1. Run the Demo

```bash
python soccer_stream_demo.py
```

This simulates a 90-minute match compressed into 10 seconds with random events and user interactions.

### 2. Producer Example

```python
from soccer_stream_producer import SoccerStreamProducer
from soccer_match_schema import MatchEvent, EventType
from datetime import datetime

# Initialize producer
producer = SoccerStreamProducer()

# Send a goal event
goal_event = MatchEvent(
    match_id="match_001",
    event_id="evt_001",
    event_type=EventType.GOAL,
    timestamp=datetime.utcnow(),
    minute=42,
    team_id="arsenal",
    player_id="player_7"
)

producer.send_match_event(goal_event)
producer.flush()
```

### 3. Consumer Example

```python
from soccer_stream_consumer import AnalyticsConsumer

# Initialize consumer
consumer = AnalyticsConsumer()

# Set custom handlers
def handle_goal(event):
    print(f"GOAL! {event['team_id']} scores!")

consumer.set_match_event_handler(handle_goal)

# Start consuming
consumer.subscribe()
consumer.consume(max_messages=100)

# Get analytics
stats = consumer.get_analytics_summary()
print(f"Active users: {stats['active_users_count']}")
```

## Data Schemas

### Match Events
- `MATCH_START`, `MATCH_END`
- `GOAL`, `PENALTY`
- `YELLOW_CARD`, `RED_CARD`
- `SUBSTITUTION`
- `CORNER`, `FOUL`, `OFFSIDE`
- `VAR_REVIEW`

### User Interactions
- `VIEW_START`, `VIEW_END`
- `REACTION`, `COMMENT`, `SHARE`
- `PREDICTION`, `BET_PLACED`
- `PLAYER_RATING`, `HIGHLIGHT_SAVED`

## Features

- **Real-time Streaming**: Low-latency event delivery
- **Batch Processing**: Efficient bulk event handling
- **Analytics**: Built-in consumer with real-time statistics
- **Flexible Schema**: Extensible event and interaction types
- **Error Handling**: Robust error handling and retry logic
- **Environment Config**: Easy configuration management

## Production Considerations

1. **Scaling**: Use multiple consumer instances with the same group ID
2. **Monitoring**: Track lag, throughput, and error rates
3. **Security**: Configure SSL/SASL for production MSK clusters
4. **Partitioning**: Use match_id for event partitioning, user_id for interactions
5. **Retention**: Configure topic retention based on analytics needs

## Troubleshooting

### Connection Issues
```bash
# Test MSK connectivity
telnet your-cluster.kafka.us-east-1.amazonaws.com 9092
```

### SSL Certificate Issues
Ensure CA certificate is properly configured:
```bash
export MSK_SSL_CA_LOCATION="/path/to/ca-cert.pem"
```

## AI Analytics with Strands SDK

The project includes a Jupyter notebook demonstrating how to use AI agents to analyze soccer streaming data:

### Running the Analytics Notebook

1. Install dependencies:
```bash
pip install strands-sdk pandas matplotlib seaborn
```

2. Start the MCP server:
```bash
cd mcp-server
npm install
npm start
```

3. Run the notebook:
```bash
jupyter notebook soccer_analytics_agents.ipynb
```

### Available AI Agents

- **Match Analyst** - Tactical analysis and game insights
- **Fan Engagement Specialist** - User behavior and engagement optimization
- **Match Predictor** - Outcome predictions and betting analysis
- **Broadcasting Director** - Content and highlight optimization

### Example Analytics

The notebook demonstrates:
- Real-time match monitoring
- Fan engagement analysis
- Predictive analytics for match outcomes
- Multi-agent collaboration for complex insights
- Executive dashboard generation
- Custom analytics functions

See [soccer_analytics_agents.ipynb](./soccer_analytics_agents.ipynb) for detailed examples.

## License

MIT