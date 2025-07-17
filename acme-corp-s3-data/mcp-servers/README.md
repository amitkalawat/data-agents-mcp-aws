# Acme Corp MCP Servers

This directory contains Model Context Protocol (MCP) servers for Acme Corp's various data sources. These servers allow AI agents to interact with the data through a standardized interface.

## Available MCP Servers

### 1. User Details MCP Server (`user-details-mcp/`)

Provides access to customer demographic and subscription data.

**Tools Available:**
- `get_users` - Query users with filters (age, gender, subscription, location)
- `get_user_by_id` - Get specific user details
- `get_user_statistics` - Aggregate statistics about the user base
- `get_user_segments` - Segment users by various criteria
- `find_similar_users` - Find users similar to a reference user

**Example Usage:**
```javascript
// Get premium users aged 25-35
get_users({
  age_min: 25,
  age_max: 35,
  subscription_type: "Premium",
  limit: 50
})
```

### 2. Streaming Analytics MCP Server (`streaming-analytics-mcp/`)

Provides access to content viewing history and engagement metrics.

**Tools Available:**
- `get_viewing_history` - Query viewing records with filters
- `get_popular_content` - Get most-watched content by timeframe
- `get_user_metrics` - Detailed viewing metrics for a specific user
- `get_content_details` - Information about specific content
- `get_content_recommendations` - Personalized recommendations
- `get_engagement_analytics` - Platform-wide engagement metrics

**Example Usage:**
```javascript
// Get this week's popular content
get_popular_content({
  limit: 10,
  timeframe: "week"
})
```

### 3. Ad Campaign MCP Server (`ad-campaign-mcp/`)

Provides access to advertising campaign data and performance metrics.

**Tools Available:**
- `get_campaigns` - List campaigns with filters
- `get_campaign_performance` - Detailed metrics for a campaign
- `get_attribution_analysis` - Conversion path analysis
- `compare_campaigns` - Side-by-side campaign comparison
- `get_optimization_recommendations` - AI-powered suggestions
- `get_campaign_roi` - ROI calculations

**Example Usage:**
```javascript
// Get performance for a specific campaign
get_campaign_performance({
  campaign_id: "camp_001",
  date_from: "2024-01-01",
  date_to: "2024-01-31"
})
```

## Installation

Each server requires Node.js 18+ and can be installed independently:

```bash
cd user-details-mcp
npm install
```

## Running the Servers

### Standalone Mode
```bash
cd user-details-mcp
npm start
```

### Development Mode (with auto-reload)
```bash
cd user-details-mcp
npm run dev
```

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "acme-user-details": {
      "command": "node",
      "args": ["/path/to/user-details-mcp/index.js"]
    },
    "acme-streaming": {
      "command": "node",
      "args": ["/path/to/streaming-analytics-mcp/index.js"]
    },
    "acme-campaigns": {
      "command": "node",
      "args": ["/path/to/ad-campaign-mcp/index.js"]
    }
  }
}
```

## Integration with Strands SDK

See the [Jupyter notebook example](../strands_agents_demo.ipynb) for how to use these MCP servers with the Strands SDK to create intelligent agents.

```python
from strands import Agent, MCPClient

# Create MCP client
client = MCPClient(
    name="user-details",
    command="node",
    args=["path/to/user-details-mcp/index.js"]
)

# Create agent with access to the MCP server
agent = Agent(
    name="Customer Analyst",
    mcp_clients=[client]
)

# Query the data
response = await agent.query("What are our user demographics?")
```

## Architecture

Each MCP server follows the same pattern:

1. **Data Loading**: CSV files are loaded into memory on startup
2. **Caching**: Data is cached for fast access
3. **Tool Handlers**: Each tool processes requests and returns JSON
4. **Error Handling**: Graceful error handling with meaningful messages

## Development

To add new tools to an MCP server:

1. Add the tool definition in `ListToolsRequestSchema` handler
2. Implement the tool logic in `CallToolRequestSchema` handler
3. Update the cache class if new data processing is needed

## Performance Considerations

- Data is loaded into memory for fast access
- No database required - works directly with CSV files
- Suitable for datasets up to ~100MB
- For larger datasets, consider adding pagination or database backend

## Troubleshooting

### Server won't start
- Check Node.js version (requires 18+)
- Verify CSV files exist in expected locations
- Check for port conflicts

### No data returned
- Ensure CSV files have the expected column names
- Check file permissions
- Verify data format matches expectations

### Performance issues
- Consider limiting result sizes with the `limit` parameter
- Use filters to reduce data processing
- Monitor memory usage for large datasets