# Data Agents MCP AWS Experiment

This repository demonstrates the integration of AI agents with AWS data services using the Model Context Protocol (MCP) and Amazon Bedrock.

## 📁 Repository Structure

```
data-agent-experiment/
├── acme-corp-data/              # Local data processing with MCP servers
├── acme-corp-s3-data/           # AWS S3 Tables lakehouse implementation
└── soccer-streaming/            # Real-time streaming analytics example
```

## 🚀 Key Features

- **Natural Language to SQL**: Query data using plain English powered by Claude 3.5
- **AWS Integration**: Seamless integration with S3, Athena, Glue, and Bedrock
- **MCP Protocol**: Standardized interface for AI agent communication
- **Real-time Analytics**: Streaming data processing examples

## 📊 Datasets

### ACME Corp Data (E-commerce Analytics)
- User demographics and subscriptions (10K users)
- Streaming analytics (50K sessions)
- Ad campaign performance (100 campaigns)
- Content library metadata

### Soccer Streaming Data
- Real-time match events
- User interactions
- AWS MSK integration

## 🛠️ Technologies

- **AWS Services**: S3, Athena, Glue, Bedrock, MSK
- **AI/ML**: Claude 3.5 Sonnet (via Amazon Bedrock)
- **MCP Servers**: AWS Data Processing MCP Server
- **Languages**: Python, JavaScript (Node.js)

## 📖 Documentation

- [Main README](./README_ACME_LAKEHOUSE.md) - Comprehensive project guide
- [Technical Guide](./acme-corp-s3-data/sagemaker-lakehouse-integration/TECHNICAL_GUIDE.md) - Implementation details
- [Setup Guide](./acme-corp-s3-data/SETUP_GUIDE.md) - Step-by-step setup instructions

## 🔗 Quick Links

- **Repository**: [github.com/amitkalawat/data-agents-mcp-aws](https://github.com/amitkalawat/data-agents-mcp-aws)
- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **AWS Bedrock**: [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

## 🚦 Getting Started

1. Clone the repository
2. Set up AWS credentials
3. Follow the setup guide in `acme-corp-s3-data/SETUP_GUIDE.md`
4. Run example queries using Bedrock integration scripts

## 📄 License

MIT License - See LICENSE file for details

---

Built with ❤️ using AWS and Claude
EOF < /dev/null