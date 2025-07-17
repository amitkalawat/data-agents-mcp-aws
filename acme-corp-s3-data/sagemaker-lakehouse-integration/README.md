# SageMaker Lakehouse Integration for ACME Corp S3 Tables

This directory contains scripts and configuration for integrating ACME Corp data with Amazon SageMaker Lakehouse using S3 Tables and the AWS Data Processing MCP Server.

## Overview

This integration enables:
- 📊 S3 Tables storage in SageMaker Lakehouse format
- 🔍 Query execution via Amazon Athena
- 🤖 AI agent access through AWS Data Processing MCP Server
- 📈 Analytics in SageMaker Studio

## Directory Structure

```
sagemaker-lakehouse-integration/
├── setup_s3_tables_lakehouse.py    # Main setup script
├── upload_to_lakehouse.sh          # Upload data to S3 Tables
├── setup_mcp_server.sh             # Configure MCP server
├── athena_queries.py               # Athena query examples
├── ai_agent_query_examples.py      # AI agent integration examples
├── mcp-dataprocessing-config.json  # MCP server configuration
└── lakehouse_config.json           # Generated configuration (after setup)
```

## Setup Instructions

### 1. Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.8+ installed
- IAM permissions for S3, Glue, Athena, and SageMaker

### 2. Create S3 Tables in SageMaker Lakehouse

```bash
# Run the setup script
python3 setup_s3_tables_lakehouse.py
```

This will:
- Create an S3 Table bucket (`acme-corp-lakehouse-{account-id}`)
- Create IAM role for lakehouse access
- Create Glue database (`acme_corp_lakehouse`)
- Register all 6 ACME Corp tables in Glue Data Catalog

### 3. Upload Data to Lakehouse

```bash
# Make sure you've prepared the Parquet files first
cd ..
python3 prepare_s3_tables.py
cd sagemaker-lakehouse-integration

# Upload to S3 Tables
./upload_to_lakehouse.sh
```

### 4. Setup AWS Data Processing MCP Server

```bash
# Install and configure MCP server
./setup_mcp_server.sh

# Test the server
uvx awslabs.aws-dataprocessing-mcp-server@latest --allow-write
```

### 5. Query Your Data

#### Using Amazon Athena

```python
# Run example queries
python3 athena_queries.py
```

#### Using AI Agents

```python
# See AI agent integration examples
python3 ai_agent_query_examples.py
```

## Table Schema

### User Details (`user_details`)
- User demographics and subscription information
- 10,000 records

### Streaming Analytics (`streaming_analytics`)
- User viewing behavior and engagement
- 50,000 session records

### Content Library (`content_library`)
- Content metadata and ratings
- 20 content items

### Campaigns (`campaigns`)
- Marketing campaign metadata
- 100 campaigns

### Campaign Performance (`campaign_performance`)
- Daily campaign metrics
- 10,000 performance records

### Attribution Data (`attribution_data`)
- User conversion attribution
- 5,000 attribution records

## Example Queries

### 1. Subscription Analysis
```sql
SELECT subscription_plan, COUNT(*) as users, AVG(monthly_price) as avg_price
FROM user_details
GROUP BY subscription_plan
```

### 2. Content Engagement
```sql
SELECT c.genre, AVG(s.engagement_score) as avg_engagement
FROM streaming_analytics s
JOIN content_library c ON s.content_id = c.content_id
GROUP BY c.genre
```

### 3. Campaign ROI
```sql
SELECT campaign_name, 
       (SUM(attributed_revenue) - SUM(spend)) / SUM(spend) * 100 as roi_percentage
FROM campaigns c
JOIN campaign_performance p ON c.campaign_id = p.campaign_id
JOIN attribution_data a ON c.campaign_id = a.campaign_id
GROUP BY campaign_name
```

## AI Agent Integration

The AWS Data Processing MCP Server enables AI agents to:

1. **Discover Tables**
   - List all tables in the lakehouse
   - Get table schemas automatically

2. **Execute Queries**
   - Natural language to SQL conversion
   - Direct Athena query execution
   - Result processing and formatting

3. **Data Operations**
   - Read operations (default)
   - Write operations (with `--allow-write` flag)
   - Glue catalog management

## Security Considerations

- IAM role follows principle of least privilege
- Read-only access by default
- Table bucket versioning enabled
- Athena workgroup isolation supported

## Troubleshooting

### Common Issues

1. **Bucket Creation Failed**
   - Check AWS credentials
   - Verify region settings
   - Ensure unique bucket name

2. **Glue Table Registration Failed**
   - Verify IAM permissions
   - Check database exists
   - Validate schema format

3. **MCP Server Connection Issues**
   - Confirm AWS credentials configured
   - Check Python version (3.10+)
   - Verify uv installation

## Next Steps

1. **SageMaker Studio Integration**
   - Access tables via SageMaker Data Wrangler
   - Build ML models using lakehouse data
   - Create feature stores

2. **Advanced Analytics**
   - Set up scheduled Athena queries
   - Create QuickSight dashboards
   - Implement real-time analytics

3. **AI Agent Enhancement**
   - Add custom query templates
   - Implement caching strategies
   - Build conversational interfaces