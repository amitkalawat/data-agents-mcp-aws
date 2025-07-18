# Data Agents MCP AWS

This repository demonstrates the integration of AI agents with AWS data services using the Model Context Protocol (MCP), Amazon Bedrock, and Strands framework.

## 🚀 Latest Updates

- ✅ **S3 Tables Integration**: Successfully loaded 75,120 rows into AWS S3 Tables
- ✅ **Strands + MCP**: Created working integration with S3 Tables MCP server
- ✅ **Natural Language Queries**: Query data using plain English via Bedrock
- ✅ **Production Ready**: All infrastructure deployed and tested

## 📁 Repository Structure

```
data-agent-experiment/
├── acme-corp-data/              # Local data processing with MCP servers
├── acme-corp-s3-data/           # AWS S3 Tables lakehouse implementation
├── docs/                        # Documentation and guides
├── examples/                    # Working code examples
└── soccer-streaming/            # Real-time streaming analytics
```

## 🎯 Key Features

- **Natural Language to SQL**: Query data using plain English powered by Claude 3.5
- **AWS S3 Tables**: Apache Iceberg format for ACID transactions
- **Strands Integration**: AI agent framework with MCP protocol
- **Amazon Bedrock**: LLM-powered query generation
- **Real-time Analytics**: Streaming data processing examples

## 📊 Data Overview

### ACME Corp E-commerce Analytics
- **Users**: 10,000 customer records with demographics
- **Streaming**: 50,000 viewing sessions with genre analytics  
- **Campaigns**: 100 marketing campaigns with performance metrics
- **Attribution**: 5,000 conversion tracking records
- **Content**: 20 titles in content library

### Current S3 Tables
- `user_details_loaded` - Customer information
- `streaming_analytics_loaded` - Viewing behavior
- `campaigns_loaded` - Marketing campaigns
- `campaign_performance_loaded` - Campaign metrics
- `attribution_data_loaded` - Conversion tracking
- `content_library_loaded` - Content metadata

## 🛠️ Technology Stack

- **AWS Services**: S3 Tables, Athena, Glue, Bedrock, EC2
- **AI/ML**: Claude 3.5 Sonnet via Amazon Bedrock
- **MCP Servers**: AWS S3 Tables MCP Server
- **Frameworks**: Strands for AI agents
- **Languages**: Python 3.10+

## 📖 Documentation

- [S3 Tables Setup](./docs/S3_TABLES_FINAL_STATUS.md) - Current S3 Tables configuration
- [Strands MCP Guide](./docs/STRANDS_S3_TABLES_MCP_GUIDE.md) - Integration guide
- [Implementation Summary](./docs/STRANDS_MCP_S3TABLES_SUMMARY.md) - What was built

## 🚦 Quick Start

### 1. Run Standalone Example
```bash
cd examples
python3 s3_tables_agent_standalone.py
```

### 2. Full MCP Integration
```bash
# Terminal 1 - Start MCP server
uvx awslabs.s3-tables-mcp-server@latest --allow-write

# Terminal 2 - Run Strands client  
cd examples
python3 strands_mcp_example_complete.py --run
```

### 3. Example Queries
- "Show me the top 5 users by watch time"
- "What are the most popular content genres?"
- "Which campaigns have the best CTR?"

## 📈 Performance

- Simple queries: ~400-500ms
- Aggregations: ~600-800ms
- Complex joins: ~900-1200ms
- 75,120 total rows queryable

## 🔗 Resources

- **Repository**: [github.com/amitkalawat/data-agents-mcp-aws](https://github.com/amitkalawat/data-agents-mcp-aws)
- **AWS S3 Tables MCP**: [github.com/awslabs/mcp](https://github.com/awslabs/mcp/tree/main/src/s3-tables-mcp-server)
- **Strands Framework**: [strandsagents.com](https://strandsagents.com/)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

## 📄 License

MIT License - See LICENSE file for details

---

Built with ❤️ using AWS, Claude, and Strands