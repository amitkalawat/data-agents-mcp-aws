#!/usr/bin/env python3
"""
ACME Corp Data Query App using Strands SDK
Queries S3 Tables data through MCP server
"""

import os
import json
import streamlit as st
from strands import Agent, MCP
import pandas as pd
from datetime import datetime

# Configure the app
st.set_page_config(
    page_title="ACME Corp Data Analytics",
    page_icon="📊",
    layout="wide"
)

# Initialize Strands Agent with MCP
@st.cache_resource
def init_agent():
    """Initialize Strands Agent with S3 Tables MCP server"""
    mcp_config = {
        "server": "acme-s3-tables",
        "bucket": os.getenv("S3_BUCKET", "acme-corp-data-tables"),
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
    
    agent = Agent(
        name="acme-data-analyst",
        mcp_servers=["awslabs.s3-tables-mcp-server"],
        config=mcp_config
    )
    return agent

# Main app
def main():
    st.title("🏢 ACME Corp Data Analytics Platform")
    st.markdown("Query and analyze ACME Corp data stored in S3 Tables")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Data Categories")
        category = st.selectbox(
            "Select data category:",
            ["Ad Campaigns", "Streaming Analytics", "User Details", "Custom Query"]
        )
        
        st.header("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tables", "6")
        with col2:
            st.metric("Data Format", "Parquet")
    
    # Initialize agent
    try:
        agent = init_agent()
    except Exception as e:
        st.error(f"Failed to initialize Strands Agent: {e}")
        return
    
    # Main content area
    if category == "Ad Campaigns":
        st.header("📈 Ad Campaign Analytics")
        
        tabs = st.tabs(["Campaign Performance", "Attribution Analysis", "Campaign Details"])
        
        with tabs[0]:
            st.subheader("Campaign Performance Overview")
            query = st.text_area(
                "SQL Query:",
                value="""SELECT 
    campaign_id,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    AVG(ctr) as avg_ctr,
    SUM(spend) as total_spend,
    AVG(cpm) as avg_cpm
FROM ad_campaign.campaign_performance
GROUP BY campaign_id
ORDER BY total_spend DESC
LIMIT 10""",
                height=150
            )
            
            if st.button("Run Query", key="perf_query"):
                with st.spinner("Querying S3 Tables..."):
                    try:
                        result = agent.query(query)
                        st.dataframe(result, use_container_width=True)
                        
                        # Visualizations
                        col1, col2 = st.columns(2)
                        with col1:
                            st.bar_chart(result.set_index('campaign_id')['total_spend'])
                        with col2:
                            st.line_chart(result.set_index('campaign_id')['avg_ctr'])
                    except Exception as e:
                        st.error(f"Query failed: {e}")
        
        with tabs[1]:
            st.subheader("Attribution Analysis")
            attribution_query = st.text_area(
                "Attribution Query:",
                value="""SELECT 
    attribution_model,
    COUNT(*) as conversions,
    AVG(attributed_revenue) as avg_revenue
FROM ad_campaign.attribution_data
GROUP BY attribution_model""",
                height=100
            )
            
            if st.button("Analyze Attribution", key="attr_query"):
                with st.spinner("Analyzing attribution data..."):
                    try:
                        result = agent.query(attribution_query)
                        st.dataframe(result)
                        st.pie_chart(result.set_index('attribution_model')['conversions'])
                    except Exception as e:
                        st.error(f"Query failed: {e}")
    
    elif category == "Streaming Analytics":
        st.header("📺 Streaming Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Content Performance")
            content_query = """SELECT 
    c.title,
    c.genre,
    COUNT(s.user_id) as total_views,
    AVG(s.engagement_score) as avg_engagement
FROM streaming.streaming_analytics s
JOIN streaming.content_library c ON s.content_id = c.content_id
GROUP BY c.title, c.genre
ORDER BY total_views DESC
LIMIT 20"""
            
            if st.button("Analyze Content"):
                with st.spinner("Analyzing streaming data..."):
                    try:
                        result = agent.query(content_query)
                        st.dataframe(result)
                    except Exception as e:
                        st.error(f"Query failed: {e}")
        
        with col2:
            st.subheader("User Engagement Trends")
            engagement_query = """SELECT 
    DATE(timestamp) as date,
    AVG(engagement_score) as avg_engagement,
    COUNT(DISTINCT user_id) as unique_users
FROM streaming.streaming_analytics
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 30"""
            
            if st.button("Show Trends"):
                with st.spinner("Loading trends..."):
                    try:
                        result = agent.query(engagement_query)
                        st.line_chart(result.set_index('date')['avg_engagement'])
                    except Exception as e:
                        st.error(f"Query failed: {e}")
    
    elif category == "User Details":
        st.header("👥 User Analytics")
        
        user_query = st.text_area(
            "User Analysis Query:",
            value="""SELECT 
    account_type,
    COUNT(*) as user_count,
    AVG(age) as avg_age,
    COUNT(CASE WHEN subscription_status = 'active' THEN 1 END) as active_users
FROM users.user_details
GROUP BY account_type""",
            height=120
        )
        
        if st.button("Analyze Users"):
            with st.spinner("Analyzing user data..."):
                try:
                    result = agent.query(user_query)
                    st.dataframe(result)
                    
                    # User distribution chart
                    st.bar_chart(result.set_index('account_type')['user_count'])
                except Exception as e:
                    st.error(f"Query failed: {e}")
    
    else:  # Custom Query
        st.header("🔍 Custom Query")
        st.markdown("Write your own SQL query to analyze ACME Corp data")
        
        # Show available tables
        with st.expander("Available Tables"):
            st.markdown("""
            **Ad Campaign Data:**
            - `ad_campaign.campaigns` - Campaign metadata
            - `ad_campaign.campaign_performance` - Performance metrics
            - `ad_campaign.attribution_data` - Attribution analysis
            
            **Streaming Data:**
            - `streaming.streaming_analytics` - User streaming behavior
            - `streaming.content_library` - Content metadata
            
            **User Data:**
            - `users.user_details` - User demographics and status
            """)
        
        custom_query = st.text_area(
            "Enter SQL Query:",
            height=200,
            placeholder="SELECT * FROM ad_campaign.campaigns LIMIT 10"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Execute Query", type="primary"):
                if custom_query:
                    with st.spinner("Executing query..."):
                        try:
                            result = agent.query(custom_query)
                            st.success("Query executed successfully!")
                            st.dataframe(result, use_container_width=True)
                            
                            # Export option
                            csv = result.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"acme_query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"Query failed: {e}")
                else:
                    st.warning("Please enter a query")
    
    # Footer
    st.markdown("---")
    st.markdown("🚀 Powered by Strands SDK and AWS S3 Tables MCP Server")

if __name__ == "__main__":
    main()