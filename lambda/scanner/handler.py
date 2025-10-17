import boto3
import json
from datetime import datetime, timedelta
from typing import List, Dict
from decimal import Decimal

# Initialize AWS clients
ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CostOptimizerScans')

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    Scans EC2 instances, identifies idle ones, and stores results in DynamoDB.
    Runs every 6 hours to capture intraday patterns.
    """
    print("Starting EC2 idle instance scan...")
    
    # Get current date and timestamp
    scan_date = datetime.utcnow().strftime('%Y-%m-%d')
    scan_timestamp = datetime.utcnow().isoformat()
    scan_hour = datetime.utcnow().strftime('%H:%M')
    
    print(f"Scan Date: {scan_date}")
    print(f"Scan Time: {scan_hour} UTC")
    
    try:
        # Get all EC2 instances
        instances = get_all_instances()
        print(f"Found {len(instances)} EC2 instances to analyze")
        
        idle_instances = []
        all_scan_results = []
        
        for instance in instances:
            is_idle = is_instance_idle(instance)
            
            scan_id = f"{instance['InstanceId']}#{scan_timestamp}"
            
            scan_item = {
                'scan_date': scan_date,
                'scan_id': scan_id,
                'scan_timestamp': scan_timestamp,
                'scan_hour': scan_hour,
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'instance_state': instance['State'],
                'launch_time': instance['LaunchTime'],
                'avg_cpu': Decimal(str(instance.get('AvgCPU', 0.0))),
                'is_idle': is_idle,
                'instance_name': instance.get('Name', 'N/A')
            }
            
            # Store in DynamoDB
            try:
                table.put_item(Item=scan_item)
                print(f"Stored scan result for {instance['InstanceId']} at {scan_hour}")
            except Exception as e:
                print(f"Failed to store {instance['InstanceId']} in DynamoDB: {str(e)}")
            
            all_scan_results.append(scan_item)
            
            if is_idle:
                idle_instances.append(instance)
        
        # Log results
        print(f"\n{'='*50}")
        print(f"SCAN COMPLETE")
        print(f"{'='*50}")
        print(f"Scan Date: {scan_date}")
        print(f"Scan Time: {scan_hour} UTC")
        print(f"Total instances scanned: {len(instances)}")
        print(f"Idle instances found: {len(idle_instances)}")
        print(f"Results stored in DynamoDB: {len(all_scan_results)}")
        
        if idle_instances:
            print(f"\n IDLE INSTANCES DETECTED:")
            for instance in idle_instances:
                print(f"  - Instance ID: {instance['InstanceId']}")
                print(f"    Name: {instance.get('Name', 'N/A')}")
                print(f"    Type: {instance['InstanceType']}")
                print(f"    Avg CPU: {instance['AvgCPU']:.2f}%")
                print(f"    State: {instance['State']}")
                print()
        else:
            print(" No idle instances found!")
        
        # Return results
        return {
            'statusCode': 200,
            'body': json.dumps({
                'scan_date': scan_date,
                'scan_timestamp': scan_timestamp,
                'scan_hour': scan_hour,
                'total_instances': len(instances),
                'idle_instances': len(idle_instances),
                'stored_in_dynamodb': len(all_scan_results),
                'idle_details': idle_instances
            }, default=str)
        }
        
    except Exception as e:
        print(f" Error during scan: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_all_instances() -> List[Dict]:
    """
    Retrieve all EC2 instances in the account.
    Returns a list of instance details.
    """
    instances = []
    
    try:
        response = ec2_client.describe_instances()
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'LaunchTime': instance['LaunchTime'].isoformat()
                }
                
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_info['Name'] = tag['Value']
                            break
                
                instances.append(instance_info)
                
    except Exception as e:
        print(f"Error retrieving instances: {str(e)}")
        raise
    
    return instances


def is_instance_idle(instance: Dict) -> bool:
    """
    Check if an instance is idle based on CPU usage.
    An instance is considered idle if:
    - It's in 'running' state
    - Average CPU usage over last 7 days is < 5%
    """
    if instance['State'] != 'running':
        instance['AvgCPU'] = 0.0
        return False
    
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance['InstanceId']
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            datapoints = response['Datapoints']
            avg_cpu = sum(dp['Average'] for dp in datapoints) / len(datapoints)
            instance['AvgCPU'] = avg_cpu
            
            if avg_cpu < 5.0:
                return True
        else:
            print(f" No CPU metrics found for {instance['InstanceId']}")
            instance['AvgCPU'] = 0.0
            
    except Exception as e:
        print(f"Error checking CPU for {instance['InstanceId']}: {str(e)}")
        instance['AvgCPU'] = 0.0
    
    return False