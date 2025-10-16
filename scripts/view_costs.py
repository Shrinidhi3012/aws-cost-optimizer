#!/usr/bin/env python3
"""
View cost analysis history
"""
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CostAnalysisHistory')

def view_cost_history():
    response = table.scan()
    items = response['Items']
    
    if not items:
        print("No cost analysis data found.")
        return
    
    # Sort by date
    items.sort(key=lambda x: x['analysis_date'], reverse=True)
    
    print(f"\n{'='*70}")
    print(f"COST ANALYSIS HISTORY")
    print(f"{'='*70}\n")
    
    for item in items:
        print(f"Analysis Date: {item['analysis_date']}")
        print(f"Period: {item['period_start']} to {item['period_end']}")
        print(f"Total Cost: ${float(item['total_cost']):.2f}")
        print(f"EC2 Cost: ${float(item['ec2_cost']):.2f}")
        print(f"Potential Savings: ${float(item['potential_savings']):.2f}")
        
        if 'top_services' in item:
            print(f"\nTop Services:")
            for service, cost in item['top_services'].items():
                print(f"  - {service}: ${float(cost):.4f}")
        
        print(f"\n{'-'*70}\n")

if __name__ == '__main__':
    view_cost_history()
