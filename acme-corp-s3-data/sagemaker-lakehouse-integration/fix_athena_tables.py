#!/usr/bin/env python3
"""
Fix Athena table definitions for proper Parquet support
Updates Glue tables with correct SerDe configuration
"""

import boto3
import json
from botocore.exceptions import ClientError

def fix_glue_tables():
    """Update Glue tables with correct Parquet SerDe configuration"""
    
    glue = boto3.client('glue', region_name='us-west-2')
    database_name = 'acme_corp_lakehouse'
    account_id = boto3.client('sts').get_caller_identity()['Account']
    bucket_name = f'acme-corp-lakehouse-{account_id}'
    
    # Define correct table configurations
    tables = {
        "user_details": {
            "location": f"s3://{bucket_name}/tables/users/user_details/",
            "columns": [
                {"Name": "user_id", "Type": "string"},
                {"Name": "email", "Type": "string"},
                {"Name": "age", "Type": "bigint"},
                {"Name": "gender", "Type": "string"},
                {"Name": "country", "Type": "string"},
                {"Name": "city", "Type": "string"},
                {"Name": "subscription_plan", "Type": "string"},
                {"Name": "monthly_price", "Type": "double"},
                {"Name": "signup_date", "Type": "string"},
                {"Name": "is_active", "Type": "boolean"},
                {"Name": "last_payment_date", "Type": "string"},
                {"Name": "primary_device", "Type": "string"},
                {"Name": "num_profiles", "Type": "bigint"},
                {"Name": "payment_method", "Type": "string"},
                {"Name": "lifetime_value", "Type": "double"},
                {"Name": "referral_source", "Type": "string"},
                {"Name": "language_preference", "Type": "string"}
            ]
        },
        "streaming_analytics": {
            "location": f"s3://{bucket_name}/tables/streaming/streaming_analytics/",
            "columns": [
                {"Name": "session_id", "Type": "string"},
                {"Name": "user_id", "Type": "string"},
                {"Name": "content_id", "Type": "string"},
                {"Name": "title", "Type": "string"},
                {"Name": "content_type", "Type": "string"},
                {"Name": "genre", "Type": "string"},
                {"Name": "view_date", "Type": "string"},
                {"Name": "view_time", "Type": "string"},
                {"Name": "device_type", "Type": "string"},
                {"Name": "watch_duration_minutes", "Type": "bigint"},
                {"Name": "completion_rate", "Type": "double"},
                {"Name": "rating_given", "Type": "double"},
                {"Name": "paused_count", "Type": "bigint"},
                {"Name": "rewind_count", "Type": "bigint"},
                {"Name": "country", "Type": "string"},
                {"Name": "bandwidth_mbps", "Type": "double"},
                {"Name": "video_quality", "Type": "string"},
                {"Name": "subtitle_language", "Type": "string"}
            ]
        },
        "content_library": {
            "location": f"s3://{bucket_name}/tables/streaming/content_library/",
            "columns": [
                {"Name": "content_id", "Type": "string"},
                {"Name": "title", "Type": "string"},
                {"Name": "type", "Type": "string"},
                {"Name": "genres", "Type": "string"},
                {"Name": "release_year", "Type": "bigint"},
                {"Name": "rating", "Type": "double"},
                {"Name": "runtime", "Type": "bigint"},
                {"Name": "episodes", "Type": "bigint"}
            ]
        },
        "campaigns": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/campaigns/",
            "columns": [
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "campaign_name", "Type": "string"},
                {"Name": "campaign_type", "Type": "string"},
                {"Name": "objective", "Type": "string"},
                {"Name": "start_date", "Type": "string"},
                {"Name": "end_date", "Type": "string"},
                {"Name": "budget", "Type": "double"},
                {"Name": "target_audience", "Type": "string"},
                {"Name": "target_countries", "Type": "string"},
                {"Name": "promoted_content_id", "Type": "string"},
                {"Name": "promoted_content_title", "Type": "string"}
            ]
        },
        "campaign_performance": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/campaign_performance/",
            "columns": [
                {"Name": "performance_id", "Type": "string"},
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "date", "Type": "string"},
                {"Name": "platform", "Type": "string"},
                {"Name": "impressions", "Type": "bigint"},
                {"Name": "clicks", "Type": "bigint"},
                {"Name": "click_through_rate", "Type": "double"},
                {"Name": "views", "Type": "bigint"},
                {"Name": "view_rate", "Type": "double"},
                {"Name": "spend", "Type": "double"},
                {"Name": "cost_per_click", "Type": "double"},
                {"Name": "cost_per_thousand_impressions", "Type": "double"},
                {"Name": "conversions", "Type": "bigint"},
                {"Name": "conversion_rate", "Type": "double"},
                {"Name": "signups", "Type": "bigint"},
                {"Name": "subscriptions", "Type": "bigint"},
                {"Name": "revenue_generated", "Type": "double"}
            ]
        },
        "attribution_data": {
            "location": f"s3://{bucket_name}/tables/ad_campaign/attribution_data/",
            "columns": [
                {"Name": "attribution_id", "Type": "string"},
                {"Name": "user_id", "Type": "string"},
                {"Name": "campaign_id", "Type": "string"},
                {"Name": "touchpoint_date", "Type": "string"},
                {"Name": "touchpoint_type", "Type": "string"},
                {"Name": "platform", "Type": "string"},
                {"Name": "device", "Type": "string"},
                {"Name": "attribution_model", "Type": "string"},
                {"Name": "attribution_weight", "Type": "double"},
                {"Name": "converted", "Type": "boolean"},
                {"Name": "conversion_value", "Type": "double"}
            ]
        }
    }
    
    print(f"🔧 Fixing Glue tables in database: {database_name}")
    print(f"Account: {account_id}")
    print()
    
    for table_name, config in tables.items():
        try:
            # Delete existing table
            try:
                glue.delete_table(DatabaseName=database_name, Name=table_name)
                print(f"🗑️  Deleted existing table: {table_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'EntityNotFoundException':
                    raise
            
            # Create table with correct configuration
            table_input = {
                'Name': table_name,
                'StorageDescriptor': {
                    'Columns': config['columns'],
                    'Location': config['location'],
                    'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                        'Parameters': {
                            'serialization.format': '1'
                        }
                    },
                    'StoredAsSubDirectories': False
                },
                'PartitionKeys': [],
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {
                    'EXTERNAL': 'TRUE',
                    'parquet.compression': 'SNAPPY',
                    'classification': 'parquet',
                    'compressionType': 'snappy',
                    'typeOfData': 'file'
                }
            }
            
            glue.create_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            
            print(f"✅ Created table: {table_name}")
            
        except Exception as e:
            print(f"❌ Error fixing table {table_name}: {e}")
    
    print()
    print("✅ Table fixes complete!")
    print()
    print("You can now run Athena queries. Example:")
    print(f"  SELECT COUNT(*) FROM {database_name}.user_details;")

def create_athena_workgroup():
    """Create Athena workgroup with results location"""
    athena = boto3.client('athena', region_name='us-west-2')
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    workgroup_name = 'acme-lakehouse-workgroup'
    results_location = f's3://acme-corp-lakehouse-{account_id}/athena-results/'
    
    try:
        athena.create_work_group(
            Name=workgroup_name,
            Configuration={
                'ResultConfigurationUpdates': {
                    'OutputLocation': results_location
                },
                'EnforceWorkGroupConfiguration': True,
                'PublishCloudWatchMetricsEnabled': True
            },
            Description='Workgroup for ACME Corp Lakehouse queries'
        )
        print(f"✅ Created Athena workgroup: {workgroup_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidRequestException':
            print(f"ℹ️  Workgroup {workgroup_name} already exists")
        else:
            raise

if __name__ == "__main__":
    fix_glue_tables()
    create_athena_workgroup()