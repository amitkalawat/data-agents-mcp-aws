# Soccer Streaming MCP Server

An MCP (Model Context Protocol) server that provides real-time soccer match data from AWS MSK Kafka streams to AI agents.

## Overview

This MCP server connects to your soccer streaming Kafka topics and provides tools for AI agents to:
- Query live match data
- Analyze user engagement
- Subscribe to real-time events
- Get match predictions based on current data

## Installation

```bash
cd soccer-streaming/mcp-server
npm install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your AWS MSK configuration:
```
MSK_BOOTSTRAP_SERVERS=your-cluster.kafka.us-east-1.amazonaws.com:9092
MSK_SECURITY_PROTOCOL=SSL
```

## Usage

### Running the Server

```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

### Connecting with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "soccer-streaming": {
      "command": "node",
      "args": ["/path/to/soccer-streaming/mcp-server/index.js"],
      "env": {
        "MSK_BOOTSTRAP_SERVERS": "your-cluster.kafka.us-east-1.amazonaws.com:9092"
      }
    }
  }
}
```

## Available Tools

### 1. `get_live_matches`
Returns all currently live matches with basic statistics.

**Example Response:**
```json
{
  "matches": [
    {
      "matchId": "match_001",
      "status": "live",
      "currentMinute": 67,
      "score": { "home": 2, "away": 1 },
      "activeUsers": 4523
    }
  ]
}
```

### 2. `get_match_details`
Get detailed information about a specific match.

**Parameters:**
- `match_id` (string, required): The match identifier

**Example Response:**
```json
{
  "summary": {
    "matchId": "match_001",
    "totalEvents": 45,
    "goals": { "home": 2, "away": 1 },
    "cards": { "yellow": 3, "red": 0 },
    "activeUsers": 4523
  },
  "recentEvents": [...],
  "totalInteractions": 12045
}
```

### 3. `get_recent_events`
Get recent events across all matches.

**Parameters:**
- `limit` (number, optional): Max events to return (default: 10)
- `event_type` (string, optional): Filter by event type

**Example:**
```
get_recent_events(limit=5, event_type="goal")
```

### 4. `get_user_engagement`
Get user engagement statistics.

**Example Response:**
```json
{
  "engagement": {
    "totalUsers": 8932,
    "totalInteractions": 45231,
    "avgInteractionsPerUser": 5.06,
    "actionBreakdown": {
      "reaction": 15234,
      "comment": 8923,
      "share": 3421
    }
  }
}
```

### 5. `subscribe_to_match`
Subscribe to real-time updates for a specific match.

**Parameters:**
- `match_id` (string, required): The match to subscribe to

### 6. `predict_match_outcome`
Get AI predictions for match outcome based on current data.

**Parameters:**
- `match_id` (string, required): The match to predict

**Example Response:**
```json
{
  "prediction": {
    "matchId": "match_001",
    "currentScore": { "home": 2, "away": 1 },
    "predictedWinner": "home",
    "confidence": 0.75,
    "factors": {
      "scoreDifference": 1,
      "recentMomentum": 2,
      "disciplineIssues": { "yellow": 3, "red": 0 }
    }
  }
}
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AWS MSK       │────▶│   MCP Server    │────▶│   AI Agent      │
│   (Kafka)       │     │   (Node.js)     │     │   (Claude)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │
         │                       ├── Data Cache
         │                       ├── Event Aggregation
         │                       └── Tool Handlers
         │
    Kafka Topics:
    - soccer-match-events
    - soccer-user-interactions
    - soccer-match-stream
```

## Features

- **Real-time Data**: Connects directly to Kafka streams
- **In-memory Cache**: Fast access to recent events and statistics
- **Event Aggregation**: Automatic calculation of match statistics
- **User Analytics**: Track engagement patterns
- **Predictive Insights**: Simple ML-based match predictions

## Development

The server uses:
- `@modelcontextprotocol/sdk` for MCP protocol implementation
- `kafkajs` for Kafka connectivity
- In-memory caching for performance

## Troubleshooting

### Connection Issues
- Verify MSK_BOOTSTRAP_SERVERS is correct
- Check network connectivity to AWS MSK cluster
- Ensure security groups allow connection

### No Data Showing
- Verify Kafka topics exist and have data
- Check consumer group permissions
- Review server logs for errors

## License

MIT