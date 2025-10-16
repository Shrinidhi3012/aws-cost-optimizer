import boto3
import json
from datetime import datetime, timedelta
from typing import List, Dict
from decimal import Decimal

# Initialize AWS clients
ec2_client = boto3.client('ec2')
rds_client = boto3.client('rds')
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
cloudwatch_client = boto3.client('cloudwatch')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AdvancedResourceScans')

def lambda_handler(event, context):
    """
    Advanced resource scanner - finds waste across multiple AWS services
    """
    print("Starting advanced resource scan...")
    
    scan_date = datetime.utcnow().strftime('%Y-%m-%d')
    scan_timestamp = datetime.utcnow().isoformat()
    
    all_findings = []
    
    try:
        # Scan unused EBS volumes
        ebs_findings = scan_unused_ebs_volumes()
        all_findings.extend(ebs_findings)
        print(f"Found {len(ebs_findings)} unused EBS volumes")
        
        # Scan idle RDS databases
        rds_findings = scan_idle_rds_instances()
        all_findings.extend(rds_findings)
        print(f"Found {len(rds_findings)} idle RDS instances")
        
        # Scan old S3 buckets
        s3_findings = scan_old_s3_buckets()
        all_findings.extend(s3_findings)
        print(f"Found {len(s3_findings)} underutilized S3 buckets")
        
        # Scan expensive Lambda functions
        lambda_findings = scan_expensive_lambda_functions()
        all_findings.extend(lambda_findings)
        print(f"Found {len(lambda_findings)} expensive Lambda functions")
        
        # Scan untagged resources
        untagged_findings = scan_untagged_resources()
        all_findings.extend(untagged_findings)
        print(f"Found {len(untagged_findings)} untagged resources")
        
        # Store findings in DynamoDB
        for finding in all_findings:
            finding['scan_date'] = scan_date
            finding['scan_timestamp'] = scan_timestamp
            finding['scan_id'] = f"{finding['resource_type']}#{finding['resource_id']}#{scan_timestamp}"
            
            try:
                table.put_item(Item=finding)
            except Exception as e:
                print(f"Error storing finding: {str(e)}")
        
        # Calculate potential savings
        total_savings = sum(float(f.get('estimated_monthly_cost', 0)) for f in all_findings)
        
        print(f"\n{'='*60}")
        print(f"ADVANCED SCAN COMPLETE")
        print(f"{'='*60}")
        print(f"Total findings: {len(all_findings)}")
        print(f"Potential monthly savings: ${total_savings:.2f}")
        print(f"Breakdown:")
        print(f"  - Unused EBS: {len(ebs_findings)}")
        print(f"  - Idle RDS: {len(rds_findings)}")
        print(f"  - Old S3: {len(s3_findings)}")
        print(f"  - Expensive Lambda: {len(lambda_findings)}")
        print(f"  - Untagged: {len(untagged_findings)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'scan_date': scan_date,
                'total_findings': len(all_findings),
                'potential_monthly_savings': total_savings,
                'breakdown': {
                    'ebs': len(ebs_findings),
                    'rds': len(rds_findings),
                    's3': len(s3_findings),
                    'lambda': len(lambda_findings),
                    'untagged': len(untagged_findings)
                }
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error during scan: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def scan_unused_ebs_volumes() -> List[Dict]:
    """Find EBS volumes not attached to any instance"""
    findings = []
    
    try:
        response = ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        
        for volume in response['Volumes']:
            # Get volume age
            create_time = volume['CreateTime']
            age_days = (datetime.utcnow().replace(tzinfo=create_time.tzinfo) - create_time).days
            
            # Estimate cost: ~$0.10/GB-month for gp3
            size_gb = volume['Size']
            monthly_cost = size_gb * 0.10
            
            finding = {
                'resource_type': 'ebs_volume',
                'resource_id': volume['VolumeId'],
                'issue': 'unused_volume',
                'size_gb': Decimal(str(size_gb)),
                'volume_type': volume['VolumeType'],
                'age_days': age_days,
                'estimated_monthly_cost': Decimal(str(monthly_cost)),
                'recommendation': f'Delete unused volume (${monthly_cost:.2f}/month) or attach to instance',
                'severity': 'medium' if monthly_cost < 5 else 'high'
            }
            
            findings.append(finding)
            
    except Exception as e:
        print(f"Error scanning EBS volumes: {str(e)}")
    
    return findings


def scan_idle_rds_instances() -> List[Dict]:
    """Find RDS instances with low utilization"""
    findings = []
    
    try:
        response = rds_client.describe_db_instances()
        
        for db_instance in response['DBInstances']:
            instance_id = db_instance['DBInstanceIdentifier']
            instance_class = db_instance['DBInstanceClass']
            
            # Get CPU metrics
            cpu_metrics = get_rds_cpu_usage(instance_id)
            
            if cpu_metrics and cpu_metrics < 10.0:  # Less than 10% CPU
                # Rough cost estimation based on instance class
                estimated_cost = estimate_rds_cost(instance_class)
                
                finding = {
                    'resource_type': 'rds_instance',
                    'resource_id': instance_id,
                    'issue': 'idle_database',
                    'instance_class': instance_class,
                    'avg_cpu': Decimal(str(cpu_metrics)),
                    'estimated_monthly_cost': Decimal(str(estimated_cost)),
                    'recommendation': f'Consider downsizing or using Aurora Serverless (${estimated_cost:.2f}/month)',
                    'severity': 'high' if estimated_cost > 50 else 'medium'
                }
                
                findings.append(finding)
                
    except Exception as e:
        print(f"Error scanning RDS: {str(e)}")
    
    return findings


def get_rds_cpu_usage(instance_id: str) -> float:
    """Get average CPU usage for RDS instance"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            return sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
    except:
        pass
    
    return None


def estimate_rds_cost(instance_class: str) -> float:
    """Rough RDS cost estimation"""
    # Simplified pricing (actual varies by region)
    pricing = {
        'db.t3.micro': 15,
        'db.t3.small': 30,
        'db.t3.medium': 60,
        'db.t3.large': 120,
        'db.m5.large': 140,
        'db.m5.xlarge': 280,
    }
    
    return pricing.get(instance_class, 100)  # Default estimate


def scan_old_s3_buckets() -> List[Dict]:
    """Find S3 buckets with old data and low access"""
    findings = []
    
    try:
        response = s3_client.list_buckets()
        
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            
            try:
                # Get bucket size (simplified - in production use CloudWatch metrics)
                # For now, just flag buckets older than 1 year
                age_days = (datetime.utcnow().replace(tzinfo=bucket['CreationDate'].tzinfo) - bucket['CreationDate']).days
                
                if age_days > 365:
                    # Rough estimate: $0.023/GB-month
                    estimated_cost = 10  # Placeholder
                    
                    finding = {
                        'resource_type': 's3_bucket',
                        'resource_id': bucket_name,
                        'issue': 'old_bucket',
                        'age_days': age_days,
                        'estimated_monthly_cost': Decimal(str(estimated_cost)),
                        'recommendation': 'Review bucket contents, consider lifecycle policies or deletion',
                        'severity': 'low'
                    }
                    
                    findings.append(finding)
                    
            except Exception as e:
                # Skip buckets we can't access
                pass
                
    except Exception as e:
        print(f"Error scanning S3: {str(e)}")
    
    return findings


def scan_expensive_lambda_functions() -> List[Dict]:
    """Find Lambda functions with high costs but low invocations"""
    findings = []
    
    try:
        response = lambda_client.list_functions()
        
        for function in response['Functions']:
            function_name = function['FunctionName']
            memory_mb = function['MemorySize']
            
            # Get invocation metrics
            invocations = get_lambda_invocations(function_name)
            
            if invocations is not None and invocations < 100:  # Less than 100 invocations/week
                # Estimate cost based on memory and invocations
                estimated_cost = (memory_mb / 1024) * 0.0000166667 * invocations * 4  # Rough monthly
                
                if estimated_cost > 1:  # Only flag if costing more than $1/month
                    finding = {
                        'resource_type': 'lambda_function',
                        'resource_id': function_name,
                        'issue': 'low_utilization',
                        'memory_mb': memory_mb,
                        'weekly_invocations': invocations,
                        'estimated_monthly_cost': Decimal(str(estimated_cost)),
                        'recommendation': 'Consider removing or reducing memory allocation',
                        'severity': 'low'
                    }
                    
                    findings.append(finding)
                    
    except Exception as e:
        print(f"Error scanning Lambda: {str(e)}")
    
    return findings


def get_lambda_invocations(function_name: str) -> int:
    """Get Lambda invocation count"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=604800,  # 1 week
            Statistics=['Sum']
        )
        
        if response['Datapoints']:
            return int(response['Datapoints'][0]['Sum'])
    except:
        pass
    
    return None


def scan_untagged_resources() -> List[Dict]:
    """Find EC2 instances without proper tags"""
    findings = []
    
    try:
        response = ec2_client.describe_instances()
        
        required_tags = ['Environment', 'Owner', 'Project']
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                
                missing_tags = [tag for tag in required_tags if tag not in tags]
                
                if missing_tags:
                    finding = {
                        'resource_type': 'ec2_untagged',
                        'resource_id': instance_id,
                        'issue': 'missing_tags',
                        'missing_tags': str(missing_tags),
                        'estimated_monthly_cost': Decimal('0'),  # No direct cost, but compliance issue
                        'recommendation': f'Add missing tags: {", ".join(missing_tags)}',
                        'severity': 'medium'
                    }
                    
                    findings.append(finding)
                    
    except Exception as e:
        print(f"Error scanning untagged resources: {str(e)}")
    
    return findings