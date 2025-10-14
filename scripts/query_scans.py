#!/usr/bin/env python3
"""
Query and display scan results from DynamoDB
"""
import boto3
from decimal import Decimal
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CostOptimizerScans')

def get_scans_for_date(scan_date):
    """Get all scans for a specific date"""
    response = table.query(
        KeyConditionExpression='scan_date = :date',
        ExpressionAttributeValues={':date': scan_date}
    )
    return response['Items']

def display_scans(items):
    """Pretty print scan results"""
    if not items:
        print("No scans found for this date.")
        return
    
    print(f"\n{'='*70}")
    print(f"Found {len(items)} instance scan(s)")
    print(f"{'='*70}\n")
    
    for item in items:
        print(f"Instance ID: {item['instance_id']}")
        print(f"  Name: {item.get('instance_name', 'N/A')}")
        print(f"  Type: {item['instance_type']}")
        print(f"  State: {item['instance_state']}")
        print(f"  Avg CPU: {float(item['avg_cpu']):.4f}%")
        print(f"  Is Idle: {'⚠️  YES' if item['is_idle'] else '✅ NO'}")
        print(f"  Scan Time: {item['scan_timestamp']}")
        print()

if __name__ == '__main__':
    # Get today's date
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    print(f"Querying scans for: {today}")
    scans = get_scans_for_date(today)
    display_scans(scans)
    
    # Show idle count
    idle_count = sum(1 for scan in scans if scan['is_idle'])
    print(f"Summary: {idle_count} idle instance(s) out of {len(scans)} total")