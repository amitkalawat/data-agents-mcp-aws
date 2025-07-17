# ACME Corp S3 Tables Setup Guide

## Quick Start

1. **Prepare data for S3 Tables** (Already completed)
   ```bash
   python3 prepare_s3_tables.py
   ```

2. **Upload to S3**
   ```bash
   export S3_BUCKET=your-bucket-name
   export AWS_REGION=us-east-1
   cd s3_tables_format
   ./upload_to_s3.sh
   ```

3. **Install MCP Server**
   ```bash
   # Install uv from Astral
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install the S3 Tables MCP server
   uvx awslabs.s3-tables-mcp-server@latest
   ```

4. **Run Strands SDK App**
   ```bash
   cd strands-app
   ./run_app.sh
   ```

## Data Overview

- **6 tables** converted to Parquet format
- **3 categories**: Ad Campaigns, Streaming Analytics, User Details
- **Format**: S3 Tables (Parquet with Snappy compression)

## Next Steps

1. Configure AWS credentials
2. Create S3 bucket if needed
3. Upload data using provided script
4. Launch the Strands SDK app to query your data