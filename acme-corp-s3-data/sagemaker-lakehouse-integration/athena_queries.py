#!/usr/bin/env python3
"""
Athena query examples for ACME Corp data in SageMaker Lakehouse
Demonstrates how to query S3 Tables data using Amazon Athena
"""

import boto3
import time
import pandas as pd
from datetime import datetime

class AthenaQueryExecutor:
    def __init__(self, database='acme_corp_lakehouse', workgroup='primary'):
        self.athena = boto3.client('athena')
        self.s3 = boto3.client('s3')
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

# Query examples
def run_example_queries():
    executor = AthenaQueryExecutor()
    
    # 1. User subscription analysis
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
    
    # 2. Content engagement by genre
    print("\n2. CONTENT ENGAGEMENT BY GENRE")
    print("-" * 50)
    
    engagement_query = """
    SELECT 
        c.genre,
        COUNT(DISTINCT s.session_id) as total_sessions,
        AVG(s.watch_duration_minutes) as avg_watch_duration,
        AVG(s.completion_rate) as avg_completion_rate,
        AVG(s.engagement_score) as avg_engagement_score
    FROM streaming_analytics s
    JOIN content_library c ON s.content_id = c.content_id
    GROUP BY c.genre
    ORDER BY avg_engagement_score DESC
    """
    
    result = executor.execute_query(engagement_query, "Content Engagement")
    if result is not None:
        print(result)
    
    # 3. Campaign ROI analysis
    print("\n3. CAMPAIGN ROI ANALYSIS")
    print("-" * 50)
    
    roi_query = """
    WITH campaign_totals AS (
        SELECT 
            c.campaign_id,
            c.campaign_name,
            c.campaign_type,
            c.budget,
            SUM(p.spend) as total_spend,
            SUM(p.impressions) as total_impressions,
            SUM(p.clicks) as total_clicks,
            SUM(p.conversions) as total_conversions,
            AVG(p.ctr) as avg_ctr
        FROM campaigns c
        JOIN campaign_performance p ON c.campaign_id = p.campaign_id
        GROUP BY c.campaign_id, c.campaign_name, c.campaign_type, c.budget
    ),
    attribution_totals AS (
        SELECT 
            campaign_id,
            SUM(attributed_revenue) as total_attributed_revenue
        FROM attribution_data
        GROUP BY campaign_id
    )
    SELECT 
        ct.campaign_name,
        ct.campaign_type,
        ct.budget,
        ct.total_spend,
        ct.total_conversions,
        COALESCE(at.total_attributed_revenue, 0) as revenue,
        ROUND((COALESCE(at.total_attributed_revenue, 0) - ct.total_spend) / ct.total_spend * 100, 2) as roi_percentage
    FROM campaign_totals ct
    LEFT JOIN attribution_totals at ON ct.campaign_id = at.campaign_id
    WHERE ct.total_spend > 0
    ORDER BY roi_percentage DESC
    LIMIT 10
    """
    
    result = executor.execute_query(roi_query, "Campaign ROI")
    if result is not None:
        print(result)
    
    # 4. User viewing patterns
    print("\n4. USER VIEWING PATTERNS")
    print("-" * 50)
    
    viewing_patterns_query = """
    SELECT 
        HOUR(CAST(s.timestamp AS TIMESTAMP)) as hour_of_day,
        s.device_type,
        COUNT(*) as session_count,
        AVG(s.watch_duration_minutes) as avg_duration
    FROM streaming_analytics s
    GROUP BY HOUR(CAST(s.timestamp AS TIMESTAMP)), s.device_type
    ORDER BY hour_of_day, device_type
    """
    
    result = executor.execute_query(viewing_patterns_query, "Viewing Patterns")
    if result is not None:
        print(result.head(20))  # Show first 20 rows
    
    # 5. Cross-dataset analysis: Campaign effectiveness by user segment
    print("\n5. CAMPAIGN EFFECTIVENESS BY USER SEGMENT")
    print("-" * 50)
    
    cross_analysis_query = """
    WITH user_segments AS (
        SELECT 
            user_id,
            subscription_plan,
            CASE 
                WHEN age < 25 THEN '18-24'
                WHEN age < 35 THEN '25-34'
                WHEN age < 45 THEN '35-44'
                WHEN age < 55 THEN '45-54'
                ELSE '55+'
            END as age_group
        FROM user_details
        WHERE is_active = true
    ),
    user_attribution AS (
        SELECT 
            a.user_id,
            a.campaign_id,
            a.attributed_revenue,
            c.campaign_type
        FROM attribution_data a
        JOIN campaigns c ON a.campaign_id = c.campaign_id
    )
    SELECT 
        us.age_group,
        us.subscription_plan,
        ua.campaign_type,
        COUNT(DISTINCT ua.user_id) as converted_users,
        AVG(ua.attributed_revenue) as avg_revenue_per_user
    FROM user_segments us
    JOIN user_attribution ua ON us.user_id = ua.user_id
    GROUP BY us.age_group, us.subscription_plan, ua.campaign_type
    HAVING COUNT(DISTINCT ua.user_id) > 5
    ORDER BY avg_revenue_per_user DESC
    """
    
    result = executor.execute_query(cross_analysis_query, "Campaign Effectiveness by Segment")
    if result is not None:
        print(result)

if __name__ == "__main__":
    print("🔍 ACME Corp Athena Query Examples")
    print("=" * 70)
    run_example_queries()