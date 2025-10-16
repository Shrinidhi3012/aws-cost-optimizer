#!/usr/bin/env python3
"""
Generate AI-powered insights using Ollama
"""
import boto3
import subprocess
import json
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
scans_table = dynamodb.Table('CostOptimizerScans')
costs_table = dynamodb.Table('CostAnalysisHistory')

def get_data_summary():
    """Gather data for AI analysis"""
    # Get last 7 days of scans
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
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
    
    # Get cost data
    cost_response = costs_table.scan()
    cost_data = cost_response.get('Items', [])
    
    # Build summary
    idle_scans = [s for s in all_scans if s.get('is_idle', False)]
    unique_instances = set(s['instance_id'] for s in all_scans)
    
    # Get instance details
    instance_details = {}
    for scan in all_scans:
        inst_id = scan['instance_id']
        if inst_id not in instance_details:
            instance_details[inst_id] = {
                'name': scan.get('instance_name', 'N/A'),
                'type': scan.get('instance_type', 'unknown'),
                'scans': 0,
                'idle_scans': 0,
                'avg_cpu_total': 0
            }
        instance_details[inst_id]['scans'] += 1
        if scan.get('is_idle', False):
            instance_details[inst_id]['idle_scans'] += 1
        instance_details[inst_id]['avg_cpu_total'] += float(scan.get('avg_cpu', 0))
    
    # Calculate averages
    for inst_id, details in instance_details.items():
        details['avg_cpu'] = details['avg_cpu_total'] / details['scans'] if details['scans'] > 0 else 0
        details['idle_percentage'] = (details['idle_scans'] / details['scans'] * 100) if details['scans'] > 0 else 0
    
    total_savings = sum(float(c.get('potential_savings', 0)) for c in cost_data)
    
    summary = {
        'total_scans': len(all_scans),
        'idle_scans': len(idle_scans),
        'unique_instances': len(unique_instances),
        'idle_percentage': (len(idle_scans) / len(all_scans) * 100) if all_scans else 0,
        'potential_savings': total_savings,
        'date_range': f"{start_date} to {end_date}",
        'instance_details': instance_details
    }
    
    return summary

def query_ollama(prompt):
    """Query Ollama with a prompt"""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral', prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "AI response timed out. Please try again."
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def generate_ai_insights():
    """Generate AI insights using Ollama"""
    print("📊 Gathering AWS cost and usage data...")
    summary = get_data_summary()
    
    print(f"\n{'='*70}")
    print("DATA SUMMARY")
    print(f"{'='*70}")
    print(f"Date Range: {summary['date_range']}")
    print(f"Total Scans: {summary['total_scans']}")
    print(f"Idle Scans Detected: {summary['idle_scans']}")
    print(f"Unique Instances: {summary['unique_instances']}")
    print(f"Idle Percentage: {summary['idle_percentage']:.1f}%")
    print(f"Potential Savings: ${summary['potential_savings']:.2f}")
    
    if summary['instance_details']:
        print(f"\nInstance Breakdown:")
        for inst_id, details in summary['instance_details'].items():
            print(f"  • {inst_id} ({details['name']})")
            print(f"    Type: {details['type']}, Avg CPU: {details['avg_cpu']:.2f}%, Idle: {details['idle_percentage']:.0f}%")
    
    print(f"{'='*70}\n")
    
    # Create prompt for Ollama
    instance_info = "\n".join([
        f"- {inst_id}: {details['name']}, {details['type']}, {details['avg_cpu']:.2f}% avg CPU, {details['idle_percentage']:.0f}% idle rate"
        for inst_id, details in summary['instance_details'].items()
    ])
    
    prompt = f"""You are an AWS cost optimization expert. Analyze this data and provide 3-5 specific, actionable recommendations.

Data Summary:
- Total scans: {summary['total_scans']}
- Idle instances detected: {summary['idle_scans']} ({summary['idle_percentage']:.1f}%)
- Unique instances: {summary['unique_instances']}
- Potential savings: ${summary['potential_savings']:.2f}
- Date range: {summary['date_range']}

Instance Details:
{instance_info if instance_info else "No instances currently running"}

Provide practical AWS cost optimization recommendations. Be specific and actionable. Format as numbered list. Keep response under 300 words."""
    
    print("🤖 Querying Ollama AI for insights...")
    print("(This may take 15-30 seconds...)\n")
    
    ai_response = query_ollama(prompt)
    
    print(f"{'='*70}")
    print("AI-GENERATED INSIGHTS")
    print(f"{'='*70}\n")
    print(ai_response)
    print(f"\n{'='*70}")

if __name__ == '__main__':
    generate_ai_insights()