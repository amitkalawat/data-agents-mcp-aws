#!/usr/bin/env python3
import json
import csv
import os
import pandas as pd
from pathlib import Path

def csv_to_s3_table_format(csv_file, output_dir):
    """Convert CSV to S3 Tables format (Parquet)"""
    df = pd.read_csv(csv_file)
    table_name = Path(csv_file).stem
    output_path = os.path.join(output_dir, f"{table_name}.parquet")
    df.to_parquet(output_path, engine='pyarrow', compression='snappy')
    print(f"Converted {csv_file} to {output_path}")
    return output_path

def prepare_s3_tables():
    """Prepare all ACME Corp data for S3 Tables format"""
    s3_tables_dir = "s3_tables_format"
    os.makedirs(s3_tables_dir, exist_ok=True)
    
    # Define data directories
    data_dirs = {
        "ad_campaign": "ad_campaign_data",
        "streaming": "streaming_analytics", 
        "users": "user_details"
    }
    
    converted_files = []
    
    for category, dir_name in data_dirs.items():
        category_dir = os.path.join(s3_tables_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Find all CSV files in the directory
        csv_files = list(Path(dir_name).glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                output_file = csv_to_s3_table_format(str(csv_file), category_dir)
                converted_files.append({
                    "source": str(csv_file),
                    "output": output_file,
                    "category": category
                })
            except Exception as e:
                print(f"Error converting {csv_file}: {e}")
    
    # Create metadata file for S3 Tables
    metadata = {
        "database_name": "acme_corp",
        "tables": []
    }
    
    for file_info in converted_files:
        table_name = Path(file_info["output"]).stem
        metadata["tables"].append({
            "table_name": table_name,
            "category": file_info["category"],
            "file_path": file_info["output"],
            "format": "parquet"
        })
    
    with open(os.path.join(s3_tables_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nCreated S3 Tables metadata: {os.path.join(s3_tables_dir, 'metadata.json')}")
    print(f"Total tables prepared: {len(converted_files)}")
    
    # Create upload script
    create_upload_script(s3_tables_dir, metadata)

def create_upload_script(s3_tables_dir, metadata):
    """Create a script to upload data to S3"""
    upload_script = """#!/bin/bash
# S3 Upload Script for ACME Corp Data Tables

BUCKET_NAME="${S3_BUCKET:-acme-corp-data-tables}"
REGION="${AWS_REGION:-us-east-1}"

echo "Uploading ACME Corp data to S3 bucket: $BUCKET_NAME"
echo "Region: $REGION"

# Create bucket if it doesn't exist
aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Upload all parquet files
"""
    
    for table in metadata["tables"]:
        s3_key = f"tables/{table['category']}/{table['table_name']}.parquet"
        upload_script += f'aws s3 cp "{table["file_path"]}" "s3://$BUCKET_NAME/{s3_key}"\n'
    
    # Upload metadata
    upload_script += f'\n# Upload metadata\naws s3 cp "{os.path.join(s3_tables_dir, "metadata.json")}" "s3://$BUCKET_NAME/metadata.json"\n'
    
    upload_script += """
echo "Upload complete!"
echo "S3 Tables are available at: s3://$BUCKET_NAME/tables/"
"""
    
    script_path = os.path.join(s3_tables_dir, "upload_to_s3.sh")
    with open(script_path, "w") as f:
        f.write(upload_script)
    
    os.chmod(script_path, 0o755)
    print(f"\nCreated upload script: {script_path}")
    print("To upload to S3, run:")
    print(f"  export S3_BUCKET=your-bucket-name")
    print(f"  export AWS_REGION=your-region")
    print(f"  ./{script_path}")

if __name__ == "__main__":
    print("Preparing ACME Corp data for S3 Tables format...")
    prepare_s3_tables()