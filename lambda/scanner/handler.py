import boto3
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Initialize AWS clients
ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    Scans EC2 instances and identifies idle ones based on CPU usage.
    """
    print("Starting EC2 idle instance scan...")
    
    try:
        # Get all EC2 instances
        instances = get_all_instances()
        print(f"Found {len(instances)} EC2 instances to analyze")
        
        # Analyze each instance
        idle_instances = []
        for instance in instances:
            if is_instance_idle(instance):
                idle_instances.append(instance)
        
        # Log results
        print(f"\n{'='*50}")
        print(f"SCAN COMPLETE")
        print(f"{'='*50}")
        print(f"Total instances scanned: {len(instances)}")
        print(f"Idle instances found: {len(idle_instances)}")
        
        if idle_instances:
            print(f"\n⚠️  IDLE INSTANCES DETECTED:")
            for instance in idle_instances:
                print(f"  - Instance ID: {instance['InstanceId']}")
                print(f"    Name: {instance.get('Name', 'N/A')}")
                print(f"    Type: {instance['InstanceType']}")
                print(f"    Avg CPU: {instance['AvgCPU']:.2f}%")
                print(f"    State: {instance['State']}")
                print()
        else:
            print("✅ No idle instances found!")
        
        # Return results
        return {
            'statusCode': 200,
            'body': json.dumps({
                'total_instances': len(instances),
                'idle_instances': len(idle_instances),
                'idle_details': idle_instances
            })
        }
        
    except Exception as e:
        print(f"❌ Error during scan: {str(e)}")
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
                # Extract relevant information
                instance_info = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'LaunchTime': instance['LaunchTime'].isoformat()
                }
                
                # Get instance name from tags
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
    # Only check running instances
    if instance['State'] != 'running':
        return False
    
    try:
        # Get CPU metrics from CloudWatch for the last 7 days
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
            Period=3600,  # 1 hour intervals
            Statistics=['Average']
        )
        
        # Calculate average CPU usage
        if response['Datapoints']:
            datapoints = response['Datapoints']
            avg_cpu = sum(dp['Average'] for dp in datapoints) / len(datapoints)
            instance['AvgCPU'] = avg_cpu
            
            # Consider idle if average CPU < 5%
            if avg_cpu < 5.0:
                return True
        else:
            # No datapoints means instance might be very new or no metrics
            print(f"⚠️  No CPU metrics found for {instance['InstanceId']}")
            instance['AvgCPU'] = 0.0
            
    except Exception as e:
        print(f"Error checking CPU for {instance['InstanceId']}: {str(e)}")
        instance['AvgCPU'] = 0.0
    
    return False