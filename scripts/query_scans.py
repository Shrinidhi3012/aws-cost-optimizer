#!/usr/bin/env python3
"""
Query and display scan results from DynamoDB
Supports multiple scans per day (6-hour intervals)
"""
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

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
    
    scans_by_time = defaultdict(list)
    for item in items:
        scan_hour = item.get('scan_hour', 'unknown')
        scans_by_time[scan_hour].append(item)
    
    unique_instances = set(item['instance_id'] for item in items)
    
    print(f"\n{'='*70}")
    print(f"Found {len(items)} scan record(s) for {len(unique_instances)} unique instance(s)")
    print(f"Scans performed at {len(scans_by_time)} different time(s)")
    print(f"{'='*70}\n")
    
    for scan_time in sorted(scans_by_time.keys()):
        scan_items = scans_by_time[scan_time]
        unique_in_scan = set(item['instance_id'] for item in scan_items)
        
        print(f" Scan Time: {scan_time} UTC")
        print(f"   Unique instances in this scan: {len(unique_in_scan)}")
        print(f"   Total scan records: {len(scan_items)}")
        
        instances = defaultdict(list)
        for item in scan_items:
            instances[item['instance_id']].append(item)
        
        for instance_id, records in instances.items():
            if len(records) > 1:
                print(f"\n   Instance scanned {len(records)} times at this hour:")
            else:
                print(f"\n   Instance:")
            
            # Show the most recent scan for this instance
            latest_record = max(records, key=lambda x: x['scan_timestamp'])
            
            print(f"     Instance ID: {latest_record['instance_id']}")
            print(f"     Name: {latest_record.get('instance_name', 'N/A')}")
            print(f"     Type: {latest_record['instance_type']}")
            print(f"     State: {latest_record['instance_state']}")
            print(f"     Avg CPU: {float(latest_record['avg_cpu']):.4f}%")
            print(f"     Is Idle: {'  YES' if latest_record['is_idle'] else ' NO'}")
            
            if len(records) > 1:
                print(f"     Scan timestamps:")
                for rec in records:
                    print(f"       - {rec['scan_timestamp']}")
        
        print(f"\n{'-'*70}\n")

def get_idle_summary(items):
    """Get summary of idle instances (unique instances, not records)"""
    scans_by_time = defaultdict(lambda: {'instances': set(), 'idle_instances': set()})
    
    for item in items:
        scan_hour = item.get('scan_hour', 'unknown')
        instance_id = item['instance_id']
        
        scans_by_time[scan_hour]['instances'].add(instance_id)
        if item['is_idle']:
            scans_by_time[scan_hour]['idle_instances'].add(instance_id)
    
    print(f"{'='*70}")
    print("UNIQUE IDLE INSTANCES BY SCAN TIME")
    print(f"{'='*70}")
    for scan_time in sorted(scans_by_time.keys()):
        stats = scans_by_time[scan_time]
        idle_count = len(stats['idle_instances'])
        total_count = len(stats['instances'])
        print(f"{scan_time} UTC: {idle_count} idle / {total_count} unique instance(s)")
    
    # Overall summary
    all_instances = set(item['instance_id'] for item in items)
    all_idle = set(item['instance_id'] for item in items if item['is_idle'])
    
    print(f"\n{'='*70}")
    print(f"OVERALL: {len(all_idle)} unique idle instance(s) out of {len(all_instances)} total")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    print(f"Querying scans for: {today}")
    scans = get_scans_for_date(today)
    
    if scans:
        display_scans(scans)
        get_idle_summary(scans)
    else:
        print("No scan data found for today.")