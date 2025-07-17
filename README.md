# Data Agent Experiment

This repository contains experimental data streaming solutions and agents.

## Projects

### 1. Soccer Streaming Datasource

A complete solution for streaming user data during live soccer matches using AWS MSK (Managed Streaming for Apache Kafka).

#### Features
- **Match Events**: Goals, cards, substitutions, VAR reviews, etc.
- **User Interactions**: Views, reactions, comments, shares, predictions, bets
- **Real-time Analytics**: Active user tracking, event counting, timeline
- **Batch Processing**: Support for sending multiple events efficiently
- **Environment Configuration**: Easy setup via environment variables
- **MCP Server**: AI agent integration via Model Context Protocol

#### Quick Start

```bash
# Navigate to the soccer streaming directory
cd soccer-streaming

# Install dependencies
pip install -r requirements.txt

# Set AWS MSK configuration
export MSK_BOOTSTRAP_SERVERS="your-cluster.kafka.us-east-1.amazonaws.com:9092"

# Run the demo
python soccer_stream_demo.py
```

#### MCP Server for AI Agents

The project includes an MCP (Model Context Protocol) server that allows AI agents to interact with the streaming data:

```bash
# Install MCP server dependencies
cd soccer-streaming/mcp-server
npm install

# Run the MCP server
npm start
```

The MCP server provides tools for:
- Querying live match data
- Analyzing user engagement
- Getting match predictions
- Subscribing to real-time events

See [MCP Server README](./soccer-streaming/mcp-server/README.md) for integration details.

#### Architecture

The system streams data to three Kafka topics:
- `soccer-match-events` - Match events only
- `soccer-user-interactions` - User interactions only  
- `soccer-match-stream` - Combined stream

#### Files
- `soccer_match_schema.py` - Data models for match events and user interactions
- `msk_config.py` - AWS MSK configuration with environment variable support
- `soccer_stream_producer.py` - Kafka producer for sending match and user data
- `soccer_stream_consumer.py` - Kafka consumer with analytics capabilities
- `soccer_stream_demo.py` - Demo script simulating a live match
- `requirements.txt` - Python dependencies
- `mcp-server/` - MCP server for AI agent integration

For more details, see the [soccer-streaming README](./soccer-streaming/README.md).

### 2. Acme Corp Data Analytics Platform

A comprehensive data analytics platform with MCP servers for AI agent integration.

#### Features
- **User Analytics**: Customer demographics, segmentation, and behavior analysis
- **Streaming Analytics**: Content performance, viewing patterns, and engagement metrics
- **Ad Campaign Management**: Campaign performance, ROI analysis, and optimization
- **AI Agent Integration**: Natural language queries via Strands SDK
- **MCP Servers**: Standardized data access for AI agents

#### Quick Start

```bash
# Navigate to the Acme Corp directory
cd acme-corp-data

# Install and run MCP servers
cd mcp-servers/user-details-mcp && npm install && npm start

# In another terminal
cd mcp-servers/streaming-analytics-mcp && npm install && npm start

# In another terminal  
cd mcp-servers/ad-campaign-mcp && npm install && npm start

# Run the Jupyter notebook for AI agents
jupyter notebook strands_agents_demo.ipynb
```

#### Available MCP Servers
- **User Details**: Customer data, segmentation, similarity analysis
- **Streaming Analytics**: Viewing history, content recommendations, engagement
- **Ad Campaigns**: Campaign performance, attribution, ROI optimization

See [MCP Servers README](./acme-corp-data/mcp-servers/README.md) for detailed documentation.

## Getting Started

Each project has its own directory with specific documentation and requirements.

## License

MIT