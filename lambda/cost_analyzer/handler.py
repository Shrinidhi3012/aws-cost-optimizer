import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List
from decimal import Decimal

# Initialize AWS clients
ce_client = boto3.client('ce')
dynamodb = boto3.resource('dynamodb')
scans_table = dynamodb.Table('CostOptimizerScans')
costs_table = dynamodb.Table('CostAnalysisHistory')

def lambda_handler(event, context):
    """
    Fetch AWS costs from Cost Explorer and analyze spending.
    """
    print("Starting cost analysis...")
    
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        print(f"Analyzing costs from {start_date} to {end_date}")
        
        # Fetch cost data
        cost_data = get_cost_by_service(start_date, end_date)
        
        # Get EC2 costs
        ec2_costs = cost_data.get('Amazon Elastic Compute Cloud - Compute', 0.0)
        
        idle_savings = calculate_idle_instance_savings(start_date, end_date)
        
        total_cost = sum(cost_data.values())
        
        # Log results
        print(f"\n{'='*60}")
        print(f"COST ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Date Range: {start_date} to {end_date}")
        print(f"Total AWS Cost: ${total_cost:.2f}")
        print(f"EC2 Cost: ${ec2_costs:.2f}")
        print(f"Potential Savings from Idle Instances: ${idle_savings:.2f}")
        print(f"\nTop 5 Services by Cost:")
        
        sorted_costs = sorted(cost_data.items(), key=lambda x: x[1], reverse=True)[:5]
        for service, cost in sorted_costs:
            print(f"  - {service}: ${cost:.2f}")
        
        # Store cost analysis in DynamoDB
        analysis_record = {
            'analysis_date': str(end_date),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'period_start': str(start_date),
            'period_end': str(end_date),
            'total_cost': Decimal(str(total_cost)),
            'ec2_cost': Decimal(str(ec2_costs)),
            'potential_savings': Decimal(str(idle_savings)),
            'top_services': {k: Decimal(str(v)) for k, v in sorted_costs}
        }
        
        try:
            costs_table.put_item(Item=analysis_record)
            print(f"Stored cost analysis in DynamoDB")
        except Exception as e:
            print(f"Failed to store in DynamoDB: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'period': {
                    'start': str(start_date),
                    'end': str(end_date)
                },
                'total_cost': float(total_cost),
                'ec2_cost': float(ec2_costs),
                'potential_savings': float(idle_savings),
                'top_services': dict(sorted_costs),
                'cost_by_service': cost_data
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error during cost analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_cost_by_service(start_date, end_date) -> Dict[str, float]:
    """
    Fetch AWS costs grouped by service using Cost Explorer.
    """
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': str(start_date),
                'End': str(end_date)
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        # Aggregate costs by service
        service_costs = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if service in service_costs:
                    service_costs[service] += cost
                else:
                    service_costs[service] = cost
        
        return service_costs
        
    except Exception as e:
        print(f"Error fetching cost data: {str(e)}")
        return {}


def calculate_idle_instance_savings(start_date, end_date) -> float:
    """
    Calculate potential savings from idle instances based on scan data.
    Estimates cost per hour for idle instances.
    """
    try:
        total_idle_hours = 0
        
        current_date = start_date
        while current_date < end_date:
            scan_date_str = str(current_date)
            
            response = scans_table.query(
                KeyConditionExpression='scan_date = :date',
                ExpressionAttributeValues={':date': scan_date_str}
            )
            
            # Count idle instances
            idle_count = sum(1 for item in response['Items'] if item.get('is_idle', False))
            
            total_idle_hours += (idle_count * 6)
            
            current_date += timedelta(days=1)
        
        estimated_savings = total_idle_hours * 0.0104
        
        print(f"  Detected {total_idle_hours} idle instance-hours")
        print(f"  Estimated savings: ${estimated_savings:.2f}")
        
        return estimated_savings
        
    except Exception as e:
        print(f"Error calculating idle savings: {str(e)}")
        return 0.0