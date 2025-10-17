import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from decimal import Decimal
import subprocess
import json
import os
import requests

# Page config
st.set_page_config(
    page_title="AWS Cost Optimizer",
    page_icon="💰",
    layout="wide"
)

# Initialize DynamoDB
@st.cache_resource
def get_dynamodb():
    return boto3.resource('dynamodb')

dynamodb = get_dynamodb()
scans_table = dynamodb.Table('CostOptimizerScans')
costs_table = dynamodb.Table('CostAnalysisHistory')
advanced_scans_table = dynamodb.Table('AdvancedResourceScans')
# Decimal to float
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# AI Query Function
def query_ollama(question, data_context):
    """Query Ollama with dashboard data context - works in Docker and locally"""
    try:
        prompt = f"""You are an AWS cost optimization assistant. Answer this question based on the data:

Data Context:
{data_context}

User Question: {question}

Provide a concise, actionable answer in 2-3 sentences."""
        
        
        if os.path.exists('/.dockerenv'):
            
            try:
                response = requests.post(
                    'http://host.docker.internal:11434/api/generate',
                    json={
                        "model": "mistral",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json().get('response', 'No response from AI')
                else:
                    return f"Ollama API error: {response.status_code}. Make sure Ollama is running on host with 'ollama serve'"
                    
            except requests.exceptions.ConnectionError:
                return "Cannot connect to Ollama. Make sure it's running on your host machine with 'ollama serve'"
            except Exception as e:
                return f"Error connecting to Ollama: {str(e)}"
        else:
            result = subprocess.run(
                ['ollama', 'run', 'mistral', prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout.strip()
            
    except subprocess.TimeoutExpired:
        return "Response timed out. Please try a simpler question."
    except Exception as e:
        return f"Error: {str(e)}"

# Title
st.title("AWS Cost Optimizer Dashboard")
st.markdown("Real-time monitoring of AWS resources and cost optimization opportunities")

# Sidebar filters
st.sidebar.header("Filters")

# Date range selector
date_range = st.sidebar.selectbox(
    "Time Period",
    ["Last 7 Days", "Last 30 Days", "All Time"]
)

if date_range == "Last 7 Days":
    days_back = 7
elif date_range == "Last 30 Days":
    days_back = 30
else:
    days_back = 365

# Fetch scan data
@st.cache_data(ttl=300)
def get_scan_data(days_back):
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)
    
    all_scans = []
    current_date = start_date
    
    while current_date <= end_date:
        try:
            response = scans_table.query(
                KeyConditionExpression='scan_date = :date',
                ExpressionAttributeValues={':date': str(current_date)}
            )
            all_scans.extend(response['Items'])
        except:
            pass
        current_date += timedelta(days=1)
    
    return all_scans

# Fetch cost data
@st.cache_data(ttl=300)
def get_cost_data():
    try:
        response = costs_table.scan()
        return response['Items']
    except:
        return []

# Fetch advanced scan data
@st.cache_data(ttl=300)
def get_advanced_scan_data(days_back):
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days_back)
        
        all_findings = []
        current_date = start_date
        
        while current_date <= end_date:
            try:
                response = advanced_scans_table.query(
                    KeyConditionExpression='scan_date = :date',
                    ExpressionAttributeValues={':date': str(current_date)}
                )
                all_findings.extend(response['Items'])
            except:
                pass
            current_date += timedelta(days=1)
        
        return all_findings
    except:
        return []

# Load data
with st.spinner("Loading data..."):
    scans = get_scan_data(days_back)
    costs = get_cost_data()

# Convert to DataFrames
if scans:
    df_scans = pd.DataFrame(scans)
    df_scans['avg_cpu'] = df_scans['avg_cpu'].apply(decimal_to_float)
    df_scans['scan_datetime'] = pd.to_datetime(df_scans['scan_timestamp'])
else:
    df_scans = pd.DataFrame()

if costs:
    df_costs = pd.DataFrame(costs)
    df_costs['total_cost'] = df_costs['total_cost'].apply(decimal_to_float)
    df_costs['potential_savings'] = df_costs['potential_savings'].apply(decimal_to_float)
    df_costs['analysis_date'] = pd.to_datetime(df_costs['analysis_date'])
else:
    df_costs = pd.DataFrame()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_scans.empty:
        total_scans = len(df_scans)
        st.metric("Total Scans", total_scans)
    else:
        st.metric("Total Scans", 0)

with col2:
    if not df_scans.empty:
        unique_instances = df_scans['instance_id'].nunique()
        st.metric("Unique Instances", unique_instances)
    else:
        st.metric("Unique Instances", 0)

with col3:
    if not df_scans.empty:
        idle_count = df_scans['is_idle'].sum()
        idle_pct = (idle_count/len(df_scans)*100)
        st.metric("Idle Instances Found", idle_count, delta=f"{idle_pct:.1f}%")
    else:
        st.metric("Idle Instances Found", 0)

with col4:
    if not df_costs.empty:
        total_savings = df_costs['potential_savings'].sum()
        st.metric("Potential Savings", f"${total_savings:.2f}")
    else:
        st.metric("Potential Savings", "$0.00")

st.markdown("---")

# AI Assistant Section
st.subheader("AI Cost Assistant")

# Detect environment
if os.path.exists('/.dockerenv'):
    st.caption("Running in Docker - connecting to Ollama on host machine")
else:
    st.caption("Running locally")

# Create data context for AI
if not df_scans.empty:
    savings_amount = df_costs['potential_savings'].sum() if not df_costs.empty else 0
    data_context = f"""
Total Scans: {len(df_scans)}
Unique Instances: {df_scans['instance_id'].nunique()}
Idle Rate: {(df_scans['is_idle'].sum()/len(df_scans)*100):.1f}%
Potential Savings: ${savings_amount:.2f}
Average CPU: {df_scans['avg_cpu'].mean():.2f}%
"""
else:
    data_context = "No scan data available yet."

# AI Chat Interface
col_ai_left, col_ai_right = st.columns([2, 1])

with col_ai_left:
    user_question = st.text_input(
        "Ask the AI about your AWS costs:",
        placeholder="e.g., Why is my idle rate high? What should I optimize first?"
    )
    
    if st.button("Ask AI", type="primary"):
        if user_question:
            with st.spinner("AI is analyzing your data..."):
                ai_response = query_ollama(user_question, data_context)
                st.success("**AI Response:**")
                st.write(ai_response)
        else:
            st.warning("Please enter a question first!")

with col_ai_right:
    st.info("""
    ** Try asking:**
    - Why are my costs high?
    - What instances should I stop?
    - How can I save money?
    - What's causing the idle rate?
    """)

st.markdown("---")

# Two columns layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Scan Activity Over Time")
    if not df_scans.empty:
        # Group by date and count scans
        scans_per_day = df_scans.groupby('scan_date').size().reset_index(name='scan_count')
        
        fig = px.bar(
            scans_per_day,
            x='scan_date',
            y='scan_count',
            title='Daily Scan Count',
            labels={'scan_date': 'Date', 'scan_count': 'Number of Scans'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No scan data available yet. Wait for automated scans to run.")

with col_right:
    st.subheader("Cost Trend")
    if not df_costs.empty:
        fig = px.line(
            df_costs,
            x='analysis_date',
            y='potential_savings',
            title='Potential Savings Over Time',
            labels={'analysis_date': 'Date', 'potential_savings': 'Potential Savings ($)'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost analysis data yet. Wait for the daily cost analyzer to run.")

# Instance details
st.markdown("---")
st.subheader("Instance Details")

if not df_scans.empty:
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_idle_only = st.checkbox("Show Idle Instances Only")
    
    with col2:
        selected_state = st.selectbox(
            "Instance State",
            ["All"] + list(df_scans['instance_state'].unique())
        )
    
    # Apply filters
    filtered_df = df_scans.copy()
    
    if show_idle_only:
        filtered_df = filtered_df[filtered_df['is_idle'] == True]
    
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df['instance_state'] == selected_state]
    
    # Display table
    if not filtered_df.empty:
        # Sort by scan_datetime first
        if 'scan_datetime' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('scan_datetime', ascending=False)
        
        # Select display columns
        display_columns = [
            'instance_id', 
            'instance_name', 
            'instance_type', 
            'instance_state', 
            'avg_cpu', 
            'is_idle',
            'scan_date',
            'scan_hour'
        ]
        
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        display_df = filtered_df[available_columns].copy()
        
        display_df = display_df.rename(columns={
            'instance_id': 'Instance ID',
            'instance_name': 'Name',
            'instance_type': 'Type',
            'instance_state': 'State',
            'avg_cpu': 'Avg CPU (%)',
            'is_idle': 'Idle',
            'scan_date': 'Date',
            'scan_hour': 'Time (UTC)'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No instances match the selected filters.")
    
    # CPU Distribution
    st.subheader("CPU Utilization Distribution")
    fig = px.histogram(
        df_scans,
        x='avg_cpu',
        nbins=20,
        title='Distribution of Average CPU Usage',
        labels={'avg_cpu': 'Average CPU (%)', 'count': 'Frequency'}
    )
    fig.add_vline(x=5, line_dash="dash", line_color="red", annotation_text="Idle Threshold (5%)")
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("No scan data available. Your scanner will collect data every 6 hours automatically.")

# Advanced Resource Findings
st.markdown("---")
st.subheader("Advanced Resource Findings")

with st.spinner("Loading advanced scan data..."):
    advanced_findings = get_advanced_scan_data(days_back)

if advanced_findings:
    # Convert to DataFrame
    df_advanced = pd.DataFrame(advanced_findings)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_findings = len(df_advanced)
        st.metric("Total Findings", total_findings)
    
    with col2:
        resource_types = df_advanced['resource_type'].nunique()
        st.metric("Resource Types", resource_types)
    
    with col3:
        if 'estimated_monthly_cost' in df_advanced.columns:
            df_advanced['estimated_monthly_cost'] = df_advanced['estimated_monthly_cost'].apply(decimal_to_float)
            total_potential_savings = df_advanced['estimated_monthly_cost'].sum()
            st.metric("Potential Monthly Savings", f"${total_potential_savings:.2f}")
        else:
            st.metric("Potential Monthly Savings", "$0.00")
    
    with col4:
        high_severity = len(df_advanced[df_advanced.get('severity', '') == 'high']) if 'severity' in df_advanced.columns else 0
        st.metric("High Severity Issues", high_severity, delta="Critical" if high_severity > 0 else "Good")
    
    # Breakdown by resource type
    st.subheader("Findings by Resource Type")
    
    resource_counts = df_advanced['resource_type'].value_counts()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig = px.pie(
            values=resource_counts.values,
            names=resource_counts.index,
            title='Distribution of Findings by Resource Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        fig = px.bar(
            x=resource_counts.index,
            y=resource_counts.values,
            title='Count by Resource Type',
            labels={'x': 'Resource Type', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed findings table
    st.subheader("Detailed Findings")
    
    # Filter by resource type
    selected_resource_type = st.selectbox(
        "Filter by Resource Type",
        ["All"] + list(df_advanced['resource_type'].unique())
    )
    
    filtered_advanced = df_advanced.copy()
    if selected_resource_type != "All":
        filtered_advanced = filtered_advanced[filtered_advanced['resource_type'] == selected_resource_type]
    
    if not filtered_advanced.empty:
        display_cols = ['resource_type', 'resource_id', 'issue', 'severity', 'estimated_monthly_cost', 'recommendation']
        available_cols = [col for col in display_cols if col in filtered_advanced.columns]
        
        display_df = filtered_advanced[available_cols].copy()
        display_df = display_df.rename(columns={
            'resource_type': 'Type',
            'resource_id': 'Resource ID',
            'issue': 'Issue',
            'severity': 'Severity',
            'estimated_monthly_cost': 'Monthly Cost ($)',
            'recommendation': 'Recommendation'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No findings match the selected filter.")
        
else:
    st.info("No advanced scan data available yet. The advanced scanner runs daily at 1 AM UTC.")
    
# Footer
st.markdown("---")
st.markdown("### Auto-refresh: Data updates every 5 minutes")
st.markdown("**Next scan:** Check EventBridge schedule (every 6 hours at 00:00, 06:00, 12:00, 18:00 UTC)")
st.markdown("**AI Assistant:** Powered by Ollama (Mistral) running locally")