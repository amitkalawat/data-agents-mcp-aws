#!/usr/bin/env python3
"""
Working Athena queries for ACME Corp data in SageMaker Lakehouse
Fixed column names based on actual schema
"""

import boto3
import time
import pandas as pd
from datetime import datetime

class AthenaQueryExecutor:
    def __init__(self, database='acme_corp_lakehouse', workgroup='primary'):
        self.athena = boto3.client('athena', region_name='us-west-2')
        self.s3 = boto3.client('s3', region_name='us-west-2')
        self.database = database
        self.workgroup = workgroup
        self.output_location = f's3://acme-corp-lakehouse-{boto3.client("sts").get_caller_identity()["Account"]}/athena-results/'
    
    def execute_query(self, query, query_name=None):
        """Execute Athena query and return results"""
        print(f"Executing query: {query_name or 'Custom Query'}")
        
        try:
            # Start query execution
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location},
                WorkGroup=self.workgroup
            )
            
            query_execution_id = response['QueryExecutionId']
            
            # Wait for query to complete
            while True:
                result = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                status = result['QueryExecution']['Status']['State']
                
                if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    break
                
                time.sleep(1)
            
            if status == 'SUCCEEDED':
                # Get query results
                results = self.athena.get_query_results(QueryExecutionId=query_execution_id)
                return self._process_results(results)
            else:
                error = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                print(f"Query failed: {error}")
                return None
                
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def _process_results(self, results):
        """Process Athena query results into pandas DataFrame"""
        rows = results['ResultSet']['Rows']
        if len(rows) <= 1:
            return pd.DataFrame()
        
        # Extract column names
        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        
        # Extract data
        data = []
        for row in rows[1:]:
            data.append([col.get('VarCharValue', None) for col in row['Data']])
        
        return pd.DataFrame(data, columns=columns)

# Query examples with correct column names
def run_working_queries():
    executor = AthenaQueryExecutor()
    
    # 1. User subscription analysis - WORKS
    print("\n1. USER SUBSCRIPTION ANALYSIS")
    print("-" * 50)
    
    subscription_query = """
    SELECT 
        subscription_plan,
        COUNT(*) as user_count,
        AVG(CAST(monthly_price AS DOUBLE)) as avg_monthly_price,
        SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) as active_users,
        ROUND(100.0 * SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) / COUNT(*), 2) as active_percentage
    FROM user_details
    GROUP BY subscription_plan
    ORDER BY user_count DESC
    """
    
    result = executor.execute_query(subscription_query, "Subscription Analysis")
    if result is not None:
        print(result)
    
    # 2. User demographics analysis
    print("\n2. USER DEMOGRAPHICS")
    print("-" * 50)
    
    demographics_query = """
    SELECT 
        gender,
        COUNT(*) as user_count,
        AVG(CAST(age AS DOUBLE)) as avg_age,
        MIN(age) as min_age,
        MAX(age) as max_age
    FROM user_details
    WHERE gender IS NOT NULL
    GROUP BY gender
    ORDER BY user_count DESC
    """
    
    result = executor.execute_query(demographics_query, "Demographics Analysis")
    if result is not None:
        print(result)
    
    # 3. Payment methods distribution
    print("\n3. PAYMENT METHODS")
    print("-" * 50)
    
    payment_query = """
    SELECT 
        payment_method,
        COUNT(*) as user_count,
        AVG(lifetime_value) as avg_lifetime_value,
        SUM(lifetime_value) as total_lifetime_value
    FROM user_details
    GROUP BY payment_method
    ORDER BY total_lifetime_value DESC
    """
    
    result = executor.execute_query(payment_query, "Payment Methods")
    if result is not None:
        print(result)
    
    # 4. Streaming content analysis
    print("\n4. STREAMING CONTENT POPULARITY")
    print("-" * 50)
    
    content_query = """
    SELECT 
        title,
        genre,
        COUNT(*) as view_count,
        COUNT(DISTINCT user_id) as unique_viewers,
        AVG(watch_duration_minutes) as avg_watch_duration,
        AVG(completion_rate) as avg_completion_rate
    FROM streaming_analytics
    GROUP BY title, genre
    ORDER BY view_count DESC
    LIMIT 10
    """
    
    result = executor.execute_query(content_query, "Content Popularity")
    if result is not None:
        print(result)
    
    # 5. Campaign performance overview
    print("\n5. CAMPAIGN PERFORMANCE OVERVIEW")
    print("-" * 50)
    
    campaign_query = """
    SELECT 
        c.campaign_type,
        COUNT(DISTINCT c.campaign_id) as campaign_count,
        SUM(p.impressions) as total_impressions,
        SUM(p.clicks) as total_clicks,
        ROUND(100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0), 2) as overall_ctr,
        SUM(p.spend) as total_spend
    FROM campaigns c
    JOIN campaign_performance p ON c.campaign_id = p.campaign_id
    GROUP BY c.campaign_type
    ORDER BY total_spend DESC
    """
    
    result = executor.execute_query(campaign_query, "Campaign Performance")
    if result is not None:
        print(result)
    
    # 6. Attribution summary
    print("\n6. ATTRIBUTION MODEL EFFECTIVENESS")
    print("-" * 50)
    
    attribution_query = """
    SELECT 
        attribution_model,
        COUNT(*) as attribution_count,
        SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) as conversions,
        AVG(attribution_weight) as avg_weight,
        SUM(conversion_value) as total_conversion_value
    FROM attribution_data
    GROUP BY attribution_model
    ORDER BY total_conversion_value DESC
    """
    
    result = executor.execute_query(attribution_query, "Attribution Models")
    if result is not None:
        print(result)
    
    # 7. Cross-table analysis: Active users by device
    print("\n7. ACTIVE USERS BY PRIMARY DEVICE")
    print("-" * 50)
    
    device_query = """
    SELECT 
        primary_device,
        subscription_plan,
        COUNT(*) as user_count,
        AVG(lifetime_value) as avg_lifetime_value
    FROM user_details
    WHERE is_active = true
    GROUP BY primary_device, subscription_plan
    ORDER BY primary_device, user_count DESC
    """
    
    result = executor.execute_query(device_query, "Device Analysis")
    if result is not None:
        print(result.head(15))  # Show first 15 rows

if __name__ == "__main__":
    print("🔍 ACME Corp Working Athena Queries")
    print("=" * 70)
    run_working_queries()