#!/usr/bin/env python3
"""
View advanced resource scan results
"""
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AdvancedResourceScans')

def view_advanced_scans():
    """View advanced scan findings"""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    all_findings = []
    current_date = start_date
    
    while current_date <= end_date:
        try:
            response = table.query(
                KeyConditionExpression='scan_date = :date',
                ExpressionAttributeValues={':date': str(current_date)}
            )
            all_findings.extend(response['Items'])
        except:
            pass
        current_date += timedelta(days=1)
    
    if not all_findings:
        print("No advanced scan data found.")
        return
    
    # Group by resource type
    by_type = defaultdict(list)
    for finding in all_findings:
        by_type[finding['resource_type']].append(finding)
    
    # Calculate totals
    total_savings = sum(float(f.get('estimated_monthly_cost', 0)) for f in all_findings)
    
    print(f"\n{'='*70}")
    print(f"ADVANCED RESOURCE SCAN RESULTS")
    print(f"{'='*70}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Total Findings: {len(all_findings)}")
    print(f"Potential Monthly Savings: ${total_savings:.2f}")
    print(f"\nBreakdown by Resource Type:")
    
    for resource_type, findings in sorted(by_type.items()):
        type_savings = sum(float(f.get('estimated_monthly_cost', 0)) for f in findings)
        print(f"  {resource_type}: {len(findings)} findings (${type_savings:.2f}/month)")
    
    print(f"\n{'='*70}")
    print(f"DETAILED FINDINGS")
    print(f"{'='*70}\n")
    
    # Display findings by type
    for resource_type, findings in sorted(by_type.items()):
        print(f"\n {resource_type.upper().replace('_', ' ')}")
        print(f"{'-'*70}")
        
        for finding in findings:
            print(f"\n  Resource: {finding['resource_id']}")
            print(f"  Issue: {finding['issue']}")
            print(f"  Estimated Cost: ${float(finding.get('estimated_monthly_cost', 0)):.2f}/month")
            print(f"  Severity: {finding.get('severity', 'unknown')}")
            print(f"  Recommendation: {finding.get('recommendation', 'N/A')}")
            
            if resource_type == 'ebs_volume':
                print(f"  Size: {finding.get('size_gb', 'N/A')} GB")
                print(f"  Type: {finding.get('volume_type', 'N/A')}")
                print(f"  Age: {finding.get('age_days', 'N/A')} days")
            elif resource_type == 'rds_instance':
                print(f"  Instance Class: {finding.get('instance_class', 'N/A')}")
                print(f"  Avg CPU: {float(finding.get('avg_cpu', 0)):.2f}%")
            elif resource_type == 'lambda_function':
                print(f"  Memory: {finding.get('memory_mb', 'N/A')} MB")
                print(f"  Weekly Invocations: {finding.get('weekly_invocations', 'N/A')}")
            elif resource_type == 'ec2_untagged':
                print(f"  Missing Tags: {finding.get('missing_tags', 'N/A')}")
    
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    view_advanced_scans()