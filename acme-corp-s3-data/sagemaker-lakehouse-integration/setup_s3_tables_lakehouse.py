#!/usr/bin/env python3
"""
Setup script for S3 Tables integration with SageMaker Lakehouse
Creates table buckets, configures permissions, and registers tables in AWS Glue Data Catalog
"""

import boto3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# AWS clients
s3 = boto3.client('s3')
glue = boto3.client('glue')
iam = boto3.client('iam')
sts = boto3.client('sts')

def get_account_id():
    """Get AWS account ID"""
    return sts.get_caller_identity()['Account']

def create_s3_table_bucket(bucket_name, region='us-east-1'):
    """Create S3 bucket configured for S3 Tables"""
    try:
        # Create bucket with table bucket type
        if region == 'us-east-1':
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'Bucket': {
                        'Type': 'Tables'
                    }
                }
            )
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region,
                    'Bucket': {
                        'Type': 'Tables'
                    }
                }
            )
        
        # Enable table bucket features
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        print(f"✅ Created S3 Table bucket: {bucket_name}")
        return True
    except Exception as e:
        if 'BucketAlreadyExists' in str(e):
            print(f"ℹ️  Bucket {bucket_name} already exists")
            return True
        print(f"❌ Error creating bucket: {e}")
        return False

def create_glue_database(database_name):
    """Create Glue database for SageMaker Lakehouse"""
    try:
        glue.create_database(
            DatabaseInput={
                'Name': database_name,
                'Description': 'ACME Corp SageMaker Lakehouse database for S3 Tables',
                'LocationUri': f's3://acme-corp-lakehouse-{get_account_id()}/databases/{database_name}/'
            }
        )
        print(f"✅ Created Glue database: {database_name}")
    except glue.exceptions.AlreadyExistsException:
        print(f"ℹ️  Glue database {database_name} already exists")
    except Exception as e:
        print(f"❌ Error creating Glue database: {e}")
        raise

def register_s3_table_in_glue(database_name, table_name, s3_location, schema):
    """Register S3 Table in Glue Data Catalog"""
    try:
        glue.create_table(
            DatabaseName=database_name,
            TableInput={
                'Name': table_name,
                'StorageDescriptor': {
                    'Columns': schema,
                    'Location': s3_location,
                    'InputFormat': 'org.apache.hadoop.parquet.mapred.ParquetInputFormat',
                    'OutputFormat': 'org.apache.hadoop.parquet.mapred.ParquetOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {
                    'classification': 'parquet',
                    'compressionType': 'snappy',
                    'typeOfData': 's3-tables'
                }
            }
        )
        print(f"✅ Registered table {table_name} in Glue")
    except glue.exceptions.AlreadyExistsException:
        print(f"ℹ️  Table {table_name} already exists in Glue")
    except Exception as e:
        print(f"❌ Error registering table: {e}")
        raise

def create_lakehouse_iam_role(role_name):
    """Create IAM role for SageMaker Lakehouse access"""
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "sagemaker.amazonaws.com",
                        "glue.amazonaws.com",
                        "athena.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:GetTableBucketPolicy",
                    "s3:PutTableBucketPolicy"
                ],
                "Resource": [
                    f"arn:aws:s3:::acme-corp-lakehouse-*",
                    f"arn:aws:s3:::acme-corp-lakehouse-*/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "glue:GetDatabase",
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:DeleteTable",
                    "glue:GetPartitions"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                    "athena:StopQueryExecution",
                    "athena:GetWorkGroup"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for SageMaker Lakehouse S3 Tables access'
        )
        
        # Attach policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='SageMakerLakehouseS3TablesPolicy',
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ Created IAM role: {role_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  IAM role {role_name} already exists")
    except Exception as e:
        print(f"❌ Error creating IAM role: {e}")
        raise

def setup_acme_tables():
    """Setup ACME Corp tables in SageMaker Lakehouse"""
    account_id = get_account_id()
    bucket_name = f"acme-corp-lakehouse-{account_id}"
    database_name = "acme_corp_lakehouse"
    role_name = "SageMakerLakehouseS3TablesRole"
    
    print("🚀 Setting up ACME Corp S3 Tables in SageMaker Lakehouse")
    print(f"Account ID: {account_id}")
    print(f"Bucket: {bucket_name}")
    print(f"Database: {database_name}")
    print()
    
    # Create S3 Table bucket
    create_s3_table_bucket(bucket_name)
    
    # Create IAM role
    create_lakehouse_iam_role(role_name)
    
    # Create Glue database
    create_glue_database(database_name)
    
    # Define table schemas
    tables = {
        "user_details": {
            "location": f"s3://{bucket_name}/tables/users/user_details/",
            "schema": [
                {"Name": "user_id", "Type": "string"},
                {"Name": "email", "Type": "string"},
                {"Name": "age", "Type": "int"},
                {"Name": "gender", "Type": "string"},
                {"Name": "country", "Type": "string"},
                {"Name": "city", "Type": "string"},
                {"Name": "subscription_plan", "Type": "string"},
                {"Name": "monthly_price", "Type": "double"},
                {"Name": "signup_date", "Type": "date"},
                {"Name": "is_active", "Type": "boolean"},
                {"Name": "last_payment_date", "Type": "date"},
                {"Name": "account_type", "Type": "string"},
                {"Name": "subscription_status", "Type": "string"}
            ]
        },
        "streaming_analytics": {
            "location": f"s3://{bucket_name}/tables/streaming/streaming_analytics/",
            "schema": [
                {"Name": "session_id", "Type": "string"},
                {"Name": "user_id", "Type": "string"},
                {"Name": "content_id", "Type": "string"},
                {"Name": "timestamp", "Type": "timestamp"},
                {"Name": "watch_duration_minutes", "Type": "int"},
                {"Name": "completion_rate", "Type": "double"},
                {"Name": "engagement_score", "Type": "double"},
                {"Name": "device_type", "Type": "string"}
            ]
        },
        "content_library": {
            "location": f"s3://{bucket_name}/tables/streaming/content_library/",
            "schema": [
                {"Name": "content_id", "Type": "string"},
                {"Name": "title", "Type": "string"},
                {"Name": "genre", "Type": "string"},
                {"Name": "release_year", "Type": "int"},
                {"Name": "rating", "Type": "double"},
                {"Name": "runtime_minutes", "Type": "int"}
            ]
        },
        "campaigns": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/campaigns/",
            "schema": [
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "campaign_name", "Type": "string"},
                {"Name": "campaign_type", "Type": "string"},
                {"Name": "start_date", "Type": "date"},
                {"Name": "end_date", "Type": "date"},
                {"Name": "budget", "Type": "double"},
                {"Name": "target_audience", "Type": "string"}
            ]
        },
        "campaign_performance": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/campaign_performance/",
            "schema": [
                {"Name": "performance_id", "Type": "string"},
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "date", "Type": "date"},
                {"Name": "impressions", "Type": "bigint"},
                {"Name": "clicks", "Type": "bigint"},
                {"Name": "ctr", "Type": "double"},
                {"Name": "spend", "Type": "double"},
                {"Name": "conversions", "Type": "int"},
                {"Name": "cpm", "Type": "double"}
            ]
        },
        "attribution_data": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/attribution_data/",
            "schema": [
                {"Name": "attribution_id", "Type": "string"},
                {"Name": "user_id", "Type": "string"},
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "attribution_model", "Type": "string"},
                {"Name": "attribution_weight", "Type": "double"},
                {"Name": "attributed_revenue", "Type": "double"}
            ]
        }
    }
    
    # Register tables in Glue
    for table_name, config in tables.items():
        register_s3_table_in_glue(
            database_name,
            table_name,
            config["location"],
            config["schema"]
        )
    
    print()
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print(f"1. Upload your Parquet files to s3://{bucket_name}/tables/")
    print(f"2. Query tables using Athena with database: {database_name}")
    print(f"3. Access in SageMaker Studio using the Lakehouse integration")
    
    # Generate configuration file
    config = {
        "bucket_name": bucket_name,
        "database_name": database_name,
        "role_name": role_name,
        "role_arn": f"arn:aws:iam::{account_id}:role/{role_name}",
        "tables": list(tables.keys()),
        "region": boto3.Session().region_name or "us-east-1"
    }
    
    with open("lakehouse_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: lakehouse_config.json")

if __name__ == "__main__":
    setup_acme_tables()