#!/bin/bash

# Upload ACME Corp data to SageMaker Lakehouse S3 Tables
# This script uploads the Parquet files to the S3 Table bucket

set -e

# Load configuration
if [ ! -f "lakehouse_config.json" ]; then
    echo "❌ Error: lakehouse_config.json not found. Run setup_s3_tables_lakehouse.py first."
    exit 1
fi

# Extract bucket name from config
BUCKET_NAME=$(python3 -c "import json; print(json.load(open('lakehouse_config.json'))['bucket_name'])")
REGION=$(python3 -c "import json; print(json.load(open('lakehouse_config.json'))['region'])")

echo "🚀 Uploading ACME Corp data to SageMaker Lakehouse"
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo

# Check if parquet files exist
if [ ! -d "../s3_tables_format" ]; then
    echo "❌ Error: ../s3_tables_format directory not found"
    echo "Please run prepare_s3_tables.py in the parent directory first"
    exit 1
fi

# Upload user details
echo "📤 Uploading user details..."
aws s3 cp ../s3_tables_format/users/user_details.parquet \
    s3://$BUCKET_NAME/tables/users/user_details/user_details.parquet \
    --region $REGION

# Upload streaming analytics
echo "📤 Uploading streaming analytics..."
aws s3 cp ../s3_tables_format/streaming/streaming_analytics.parquet \
    s3://$BUCKET_NAME/tables/streaming/streaming_analytics/streaming_analytics.parquet \
    --region $REGION

aws s3 cp ../s3_tables_format/streaming/content_library.parquet \
    s3://$BUCKET_NAME/tables/streaming/content_library/content_library.parquet \
    --region $REGION

# Upload ad campaign data
echo "📤 Uploading ad campaign data..."
aws s3 cp ../s3_tables_format/ad_campaign/campaigns.parquet \
    s3://$BUCKET_NAME/tables/ad_campaign/campaigns/campaigns.parquet \
    --region $REGION

aws s3 cp ../s3_tables_format/ad_campaign/campaign_performance.parquet \
    s3://$BUCKET_NAME/tables/ad_campaign/campaign_performance/campaign_performance.parquet \
    --region $REGION

aws s3 cp ../s3_tables_format/ad_campaign/attribution_data.parquet \
    s3://$BUCKET_NAME/tables/ad_campaign/attribution_data/attribution_data.parquet \
    --region $REGION

echo
echo "✅ Upload complete!"
echo
echo "You can now query your data using:"
echo "1. Amazon Athena - Use database: acme_corp_lakehouse"
echo "2. SageMaker Studio - Access via Lakehouse integration"
echo "3. AWS Data Processing MCP Server - For AI agent queries"