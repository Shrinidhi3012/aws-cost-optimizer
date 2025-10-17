# 💰 AWS Cost Optimizer

**An intelligent AWS cost optimization tool that automatically identifies idle resources, tracks spending, and provides AI-powered recommendations to reduce cloud costs.**

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB%20%7C%20EventBridge-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)](https://www.terraform.io/)


---

## 🎯 Problem Statement

Organizations waste **30-40% of their AWS spend** on idle or underutilized resources. Manual auditing is time-consuming and often misses optimization opportunities.

**AWS Cost Optimizer solves this by:**
- 🔍 **Automatically scanning** EC2, EBS, RDS, S3, and Lambda resources
- 📊 **Tracking costs** in real-time using AWS Cost Explorer
- 🤖 **Providing AI-powered insights** for optimization recommendations
- ⏰ **Scheduling automated scans** every 6 hours
- 💾 **Storing historical data** for trend analysis

---

## ✨ Key Features

### 🔍 Multi-Resource Scanning
- **EC2 Instances:** Detects idle instances with <5% CPU utilization
- **EBS Volumes:** Identifies unattached volumes wasting storage costs
- **RDS Databases:** Finds stopped or idle database instances
- **S3 Buckets:** Analyzes storage costs and lifecycle policies
- **Lambda Functions:** Identifies over-provisioned or unused functions
- **Compliance:** Flags untagged resources for governance

### 📊 Cost Analytics
- Real-time AWS spending breakdown by service
- Historical cost trends and projections
- Potential monthly savings calculations
- Detailed cost attribution per resource

### 🤖 AI-Powered Insights
- Natural language queries: "What are my idle resources?"
- Intelligent recommendations using Ollama (Mistral-7B)
- Context-aware optimization suggestions
- Interactive chat interface

### 🚀 Automation
- EventBridge scheduled scans (every 6 hours)
- Automated cost analysis (daily)
- DynamoDB storage for historical tracking
- Email notifications (optional)

### 📈 Interactive Dashboard
- Real-time metrics and visualizations
- Filterable resource tables
- Cost trend charts
- AI chat interface
- Export capabilities

---

## 🛠️ Tech Stack

### AWS Services
- **Lambda:** Serverless compute for scanners
- **DynamoDB:** NoSQL database for scan results
- **EventBridge:** Scheduled automation
- **Cost Explorer:** Cost tracking API
- **IAM:** Security and permissions
- **CloudWatch:** Logging and monitoring

### Application Stack
- **Python 3.13:** Core application language
- **Boto3:** AWS SDK for Python
- **Streamlit:** Interactive web dashboard
- **Docker:** Containerization
- **Ollama (Mistral-7B):** AI-powered insights
- **Terraform:** Infrastructure as Code

### DevOps
- **Git/GitHub:** Version control
- **Docker Compose:** Container orchestration
- **Terraform:** Infrastructure provisioning

---
**⭐ If you find this project useful, please star the repository!**