#!/bin/bash
set -e

echo "🚀 Creating test resources for AWS Cost Optimizer demo..."

# Get default VPC and subnet
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0].SubnetId' --output text)

echo "Using VPC: $VPC_ID"
echo "Using Subnet: $SUBNET_ID"

# Get the latest Amazon Linux 2023 AMI for current region
echo "Finding latest Amazon Linux 2023 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023.*-x86_64" "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

echo "Using AMI: $AMI_ID"

# 1. Launch "idle" EC2 instance (t3.micro - free tier)
echo ""
echo "📦 Creating idle EC2 instance..."
IDLE_INSTANCE=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --subnet-id $SUBNET_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo-idle-instance},{Key=Environment,Value=demo},{Key=Owner,Value=cost-optimizer},{Key=Project,Value=demo}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Created idle instance: $IDLE_INSTANCE"

# 2. Launch "active" EC2 instance (properly tagged)
echo ""
echo "📦 Creating active EC2 instance..."
ACTIVE_INSTANCE=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --subnet-id $SUBNET_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo-active-instance},{Key=Environment,Value=production},{Key=Owner,Value=devops-team},{Key=Project,Value=web-app}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Created active instance: $ACTIVE_INSTANCE"

# 3. Launch "untagged" EC2 instance (missing required tags)
echo ""
echo "📦 Creating untagged EC2 instance..."
UNTAGGED_INSTANCE=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --subnet-id $SUBNET_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo-untagged-instance}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Created untagged instance: $UNTAGGED_INSTANCE"

# Wait for instances to start
echo ""
echo "⏳ Waiting 30 seconds for instances to start..."
sleep 30

# 4. Create unused EBS volume
echo ""
echo "💾 Creating unused EBS volume..."
UNUSED_VOLUME=$(aws ec2 create-volume \
    --size 8 \
    --availability-zone us-east-1a \
    --volume-type gp3 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=demo-unused-volume},{Key=Environment,Value=demo}]' \
    --query 'VolumeId' \
    --output text)

echo "✅ Created unused volume: $UNUSED_VOLUME"

# 5. Create EBS volume and attach to active instance
echo ""
echo "💾 Creating attached EBS volume..."
ATTACHED_VOLUME=$(aws ec2 create-volume \
    --size 10 \
    --availability-zone us-east-1a \
    --volume-type gp3 \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=demo-attached-volume},{Key=Environment,Value=production}]' \
    --query 'VolumeId' \
    --output text)

echo "✅ Created attached volume: $ATTACHED_VOLUME"

# Wait for volume to be available
echo "⏳ Waiting for volume to become available..."
aws ec2 wait volume-available --volume-ids $ATTACHED_VOLUME

# Attach volume to active instance
aws ec2 attach-volume \
    --volume-id $ATTACHED_VOLUME \
    --instance-id $ACTIVE_INSTANCE \
    --device /dev/sdf

echo "✅ Attached volume to instance"

# 6. Create S3 bucket
echo ""
echo "🪣 Creating S3 bucket for demo..."
BUCKET_NAME="aws-cost-optimizer-demo-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

echo "✅ Created S3 bucket: $BUCKET_NAME"

# Upload a small test file
echo "test data" > /tmp/demo-file.txt
aws s3 cp /tmp/demo-file.txt s3://$BUCKET_NAME/
rm /tmp/demo-file.txt

echo "✅ Uploaded test file to bucket"

# Save resource IDs for cleanup
cat > test-resources.json << RESOURCES
{
  "instances": ["$IDLE_INSTANCE", "$ACTIVE_INSTANCE", "$UNTAGGED_INSTANCE"],
  "volumes": ["$UNUSED_VOLUME", "$ATTACHED_VOLUME"],
  "buckets": ["$BUCKET_NAME"],
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
RESOURCES

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ TEST RESOURCES CREATED SUCCESSFULLY!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "  • EC2 Instances: 3 (t3.micro - Free Tier)"
echo "    - $IDLE_INSTANCE (idle - will trigger detection)"
echo "    - $ACTIVE_INSTANCE (active - properly tagged)"
echo "    - $UNTAGGED_INSTANCE (untagged - compliance issue)"
echo ""
echo "  • EBS Volumes: 2"
echo "    - $UNUSED_VOLUME (unused - will trigger detection)"
echo "    - $ATTACHED_VOLUME (attached to $ACTIVE_INSTANCE)"
echo ""
echo "  • S3 Buckets: 1"
echo "    - $BUCKET_NAME"
echo ""
echo "💰 Cost: \$0.00 (Free Tier - 750 hours/month t3.micro)"
echo "⏱️  Safe Runtime: 2-3 days (still within free tier)"
echo ""
echo "📝 Resource IDs saved to: test-resources.json"
echo ""
echo "🔍 Next steps:"
echo "   1. Wait 2 minutes for instances to fully boot"
echo "   2. Run scanners:"
echo "      aws lambda invoke --function-name cost-optimizer-scanner --payload '{}' response.json"
echo "      aws lambda invoke --function-name cost-optimizer-advanced-scanner --payload '{}' advanced-response.json"
echo "   3. View in dashboard: cd dashboard && streamlit run app.py"
echo ""
echo "🧹 Cleanup on Sunday: ./scripts/cleanup_test_resources.sh"
echo "═══════════════════════════════════════════════════════════"