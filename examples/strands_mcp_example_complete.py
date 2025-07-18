#!/usr/bin/env python3
"""
Complete Strands + S3 Tables MCP Integration Example

This demonstrates how to use Strands with the AWS S3 Tables MCP server
following the pattern from https://strandsagents.com/latest/documentation/docs/examples/python/mcp_calculator/
"""

import asyncio
import subprocess
import time
import os
import sys
from typing import Dict, Any, List

# Configuration for our S3 Tables
S3_TABLES_CONFIG = {
    "bucket": "acme-corp-s3tables-878687028155",
    "bucket_arn": "arn:aws:s3tables:us-west-2:878687028155:bucket/cca0ff7e-0eeb-422f-8678-8894c191e393",
    "database": "acme_s3tables_iceberg",
    "region": "us-west-2"
}

# Example queries to demonstrate
EXAMPLE_QUERIES = [
    "List all S3 table buckets",
    "Show me the namespaces in bucket acme-corp-s3tables-878687028155",
    "What tables exist in the user_data namespace?",
    "Query the top 5 users from user_details_loaded table by total watch time",
    "Find the most popular content genres from streaming_analytics_loaded",
    "Show campaign performance metrics from campaigns_loaded and campaign_performance_loaded tables"
]

def setup_mcp_server_config():
    """Create MCP server configuration"""
    config = {
        "mcpServers": {
            "awslabs.s3-tables-mcp-server": {
                "command": "uvx",
                "args": ["awslabs.s3-tables-mcp-server@latest", "--allow-write"],
                "env": {
                    "AWS_REGION": S3_TABLES_CONFIG["region"]
                }
            }
        }
    }
    
    # Save config for reference
    import json
    with open('mcp_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created MCP server configuration")
    return config

async def run_strands_example():
    """Run the Strands + MCP example"""
    
    print("\n🚀 Strands + S3 Tables MCP Integration Example")
    print("=" * 60)
    
    try:
        # Import required modules
        from mcp.client.streamable_http import streamablehttp_client
        from strands import Agent
        from strands.tools.mcp.mcp_client import MCPClient
        
        # Create transport
        def create_streamable_http_transport():
            return streamablehttp_client("http://localhost:8000/mcp/")
        
        # Create MCP client
        print("\n📡 Connecting to S3 Tables MCP Server...")
        streamable_http_mcp_client = MCPClient(create_streamable_http_transport)
        
        with streamable_http_mcp_client:
            # List available tools
            print("\n🔧 Discovering available tools...")
            tools = streamable_http_mcp_client.list_tools_sync()
            
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool.name}: {tool.description[:60]}...")
            
            # Create Strands agent
            print("\n🤖 Creating Strands agent with S3 Tables tools...")
            agent = Agent(
                tools=tools,
                model="gpt-4",  # or your preferred model
                system_prompt="""You are a data analyst expert with access to AWS S3 Tables.
                Use the available tools to query and analyze data from S3 Tables.
                Provide clear, structured responses with insights from the data."""
            )
            
            # Run example queries
            print("\n📊 Running example queries...")
            print("=" * 60)
            
            for i, query in enumerate(EXAMPLE_QUERIES, 1):
                print(f"\n{i}. Query: {query}")
                print("-" * 40)
                
                try:
                    # Method 1: Conversational approach
                    response = await agent(query)
                    print(f"Response: {response}")
                    
                    # Method 2: Direct tool access (if applicable)
                    # For example, if querying specific tools:
                    # if "list_table_buckets" in query.lower():
                    #     result = await agent.tool.list_table_buckets()
                    #     print(f"Direct result: {result}")
                    
                except Exception as e:
                    print(f"Error: {e}")
                
                # Small delay between queries
                await asyncio.sleep(1)
            
            # Interactive mode
            print("\n\n💬 Interactive Mode")
            print("=" * 60)
            print("You can now ask questions about your S3 Tables data.")
            print("Type 'exit' to quit.\n")
            
            while True:
                try:
                    user_query = input("🔍 Your query: ").strip()
                    
                    if user_query.lower() == 'exit':
                        break
                    
                    if user_query:
                        response = await agent(user_query)
                        print(f"\n📊 Response: {response}\n")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}\n")
    
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n📦 Please install required packages:")
        print("   pip install strands mcp")
        print("   uvx install awslabs.s3-tables-mcp-server@latest")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def create_standalone_example():
    """Create a standalone example that doesn't require running separate processes"""
    
    example = """#!/usr/bin/env python3
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
        print(f"\\nQuery: {q}")
        print("-" * 40)
        result = agent.query(q)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            for record in result['data'][:5]:
                print(record)
"""
    
    with open('s3_tables_agent_standalone.py', 'w') as f:
        f.write(example)
    
    os.chmod('s3_tables_agent_standalone.py', 0o755)
    print("✅ Created standalone example: s3_tables_agent_standalone.py")

def main():
    """Main function"""
    print("🏗️ Strands + S3 Tables MCP Integration Setup")
    print("=" * 60)
    
    # Setup configuration
    setup_mcp_server_config()
    
    # Create standalone example
    create_standalone_example()
    
    print("\n📚 Setup Complete!")
    print("\nTo run the full MCP integration:")
    print("1. Start MCP server: uvx awslabs.s3-tables-mcp-server@latest --allow-write")
    print("2. Run this script with: python strands_mcp_example_complete.py --run")
    
    print("\nTo run the standalone example:")
    print("  python s3_tables_agent_standalone.py")
    
    # Check if we should run the example
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        print("\n" + "=" * 60)
        asyncio.run(run_strands_example())

if __name__ == "__main__":
    main()