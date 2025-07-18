#!/usr/bin/env python3
'''
Standalone S3 Tables Query Example using boto3
This can run without the MCP server
'''

import boto3
from typing import Dict, List, Any

class S3TablesQueryAgent:
    def __init__(self, region='us-west-2'):
        self.s3tables = boto3.client('s3tables', region_name=region)
        self.athena = boto3.client('athena', region_name=region)
        self.database = 'acme_s3tables_iceberg'
        self.output_location = 's3://acme-corp-s3tables-878687028155-data/athena-results/'
    
    def natural_language_to_sql(self, query: str) -> str:
        '''Convert natural language to SQL (simplified)'''
        
        # Simple pattern matching for demo
        if "top" in query and "users" in query:
            return '''
                SELECT user_id, user_name, total_watch_time_minutes
                FROM user_details_loaded
                ORDER BY total_watch_time_minutes DESC
                LIMIT 5
            '''
        elif "genre" in query:
            return '''
                SELECT genre, COUNT(*) as views, AVG(watch_duration_minutes) as avg_duration
                FROM streaming_analytics_loaded
                GROUP BY genre
                ORDER BY views DESC
            '''
        elif "campaign" in query:
            return '''
                SELECT c.campaign_name, SUM(cp.impressions) as impressions
                FROM campaigns_loaded c
                JOIN campaign_performance_loaded cp ON c.campaign_id = cp.campaign_id
                GROUP BY c.campaign_name
                ORDER BY impressions DESC
                LIMIT 5
            '''
        else:
            return f"SELECT * FROM user_details_loaded LIMIT 5"
    
    def query(self, natural_language_query: str) -> Dict[str, Any]:
        '''Execute a natural language query'''
        
        # Convert to SQL
        sql = self.natural_language_to_sql(natural_language_query)
        print(f"Generated SQL: {sql}")
        
        # Execute via Athena
        response = self.athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': self.output_location}
        )
        
        query_id = response['QueryExecutionId']
        
        # Wait for completion
        import time
        while True:
            result = self.athena.get_query_execution(QueryExecutionId=query_id)
            status = result['QueryExecution']['Status']['State']
            if status in ['SUCCEEDED', 'FAILED']:
                break
            time.sleep(1)
        
        if status == 'SUCCEEDED':
            results = self.athena.get_query_results(QueryExecutionId=query_id)
            return self._format_results(results)
        else:
            return {'error': result['QueryExecution']['Status'].get('StateChangeReason')}
    
    def _format_results(self, results):
        '''Format Athena results'''
        rows = results['ResultSet']['Rows']
        if not rows:
            return {'data': []}
        
        headers = [col['VarCharValue'] for col in rows[0]['Data']]
        data = []
        
        for row in rows[1:]:
            record = {}
            for i, col in enumerate(row['Data']):
                record[headers[i]] = col.get('VarCharValue', '')
            data.append(record)
        
        return {'headers': headers, 'data': data}

# Example usage
if __name__ == "__main__":
    agent = S3TablesQueryAgent()
    
    queries = [
        "Show me top users by watch time",
        "What are the popular genres?",
        "Show campaign performance"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        print("-" * 40)
        result = agent.query(q)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            for record in result['data'][:5]:
                print(record)
