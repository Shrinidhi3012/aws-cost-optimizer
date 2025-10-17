# AWS Cost Optimizer - Terraform Infrastructure

This directory contains Terraform configuration to deploy the entire AWS Cost Optimizer infrastructure.

## 📋 What Gets Created

- **3 DynamoDB Tables**: Scan results, cost history, advanced findings
- **3 Lambda Functions**: EC2 scanner, cost analyzer, advanced scanner
- **1 IAM Role**: With appropriate permissions for all Lambda functions
- **3 EventBridge Rules**: Automated schedules for each scanner
- **3 CloudWatch Log Groups**: For Lambda function logs

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0 installed

### Deployment
```bash
# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Deploy infrastructure
terraform apply

# View outputs
terraform output
```

### Cleanup
```bash
terraform destroy
```

## 📝 Configuration

Edit `variables.tf` or create `terraform.tfvars`:
```hcl
aws_region                  = "us-east-1"
environment                 = "production"
scanner_schedule            = "cron(0 */6 * * ? *)"  # Every 6 hours
cost_analyzer_schedule      = "cron(0 0 * * ? *)"    # Daily at midnight
advanced_scanner_schedule   = "cron(0 1 * * ? *)"    # Daily at 1 AM
idle_cpu_threshold          = 5
```

## 🏗️ Architecture
```
┌─────────────────────────────────────────┐
│           EventBridge Rules             │
│  • Every 6 hours (EC2 Scanner)         │
│  • Daily midnight (Cost Analyzer)       │
│  • Daily 1 AM (Advanced Scanner)        │
└──────────────┬──────────────────────────┘
               │ Triggers
               ▼
┌─────────────────────────────────────────┐
│         Lambda Functions                │
│  • EC2IdleScanner                       │
│  • CostAnalyzer                         │
│  • AdvancedResourceScanner              │
└──────────────┬──────────────────────────┘
               │ Writes to
               ▼
┌─────────────────────────────────────────┐
│         DynamoDB Tables                 │
│  • CostOptimizerScans                   │
│  • CostAnalysisHistory                  │
│  • AdvancedResourceScans                │
└─────────────────────────────────────────┘
```

## 📊 Outputs

After deployment, Terraform displays:
- DynamoDB table names
- Lambda function ARNs
- IAM role details
- EventBridge schedules
- Deployment summary

## 💰 Cost

All resources use:
- DynamoDB: On-demand billing (pay per request)
- Lambda: Free tier eligible (1M requests/month)
- EventBridge: Free
- CloudWatch Logs: 7-day retention

**Estimated monthly cost: $0-2** (within AWS Free Tier for moderate usage)

## 🔒 Security

- IAM role follows principle of least privilege
- Lambda functions have minimal required permissions
- No public endpoints
- CloudWatch Logs for audit trail

## 📚 Files

- `main.tf` - Provider and core configuration
- `variables.tf` - Input variables
- `dynamodb.tf` - DynamoDB table definitions
- `iam.tf` - IAM roles and policies
- `lambda.tf` - Lambda function definitions
- `eventbridge.tf` - EventBridge scheduling rules
- `outputs.tf` - Output values after deployment
- `README.md` - This file

## 🤝 Contributing

This infrastructure is part of the AWS Cost Optimizer project. See main repository README for details.