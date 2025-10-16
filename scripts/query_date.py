#!/usr/bin/env python3
import boto3
import sys
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CostOptimizerScans')

def get_scans_for_date(scan_date):
    response = table.query(
        KeyConditionExpression='scan_date = :date',
        ExpressionAttributeValues={':date': scan_date}
    )
    return response['Items']

if __name__ == '__main__':
    scan_date = sys.argv[1] if len(sys.argv) > 1 else datetime.utcnow().strftime('%Y-%m-%d')
    
    print(f"Querying scans for: {scan_date}")
    scans = get_scans_for_date(scan_date)
    
    if scans:
        print(f"Found {len(scans)} scan record(s)")
        for item in scans:
            print(f"\n  Time: {item.get('scan_hour', 'unknown')} UTC")
            print(f"  Instance: {item['instance_id']}")
            print(f"  Name: {item.get('instance_name', 'N/A')}")
            print(f"  State: {item['instance_state']}")
            print(f"  CPU: {float(item['avg_cpu']):.2f}%")
            print(f"  Idle: {item['is_idle']}")
    else:
        print("No scan data found for this date.")
