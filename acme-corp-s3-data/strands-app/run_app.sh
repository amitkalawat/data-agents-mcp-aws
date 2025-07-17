#!/bin/bash

# ACME Corp Data Query App Runner

echo "🚀 Starting ACME Corp Data Query App with Strands SDK"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export S3_BUCKET="${S3_BUCKET:-acme-corp-data-tables}"
export AWS_REGION="${AWS_REGION:-us-east-1}"

echo ""
echo "Configuration:"
echo "- S3 Bucket: $S3_BUCKET"
echo "- AWS Region: $AWS_REGION"
echo ""

# Run the Streamlit app
echo "Starting Streamlit app..."
streamlit run acme_data_query_app.py --server.port 8501 --server.address localhost