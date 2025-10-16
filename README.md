# AWS Cost Optimizer

AI-powered AWS cost monitoring and optimization tool with automated scanning, real-time dashboards, and natural language insights.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/shrinidhi3012/aws-cost-optimizer-dashboard)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 🎯 Project Status

**✅ Phases 1-6 Complete!**

- ✅ **Phase 1**: EC2 idle instance detection
- ✅ **Phase 2**: DynamoDB persistence  
- ✅ **Phase 3**: Automated 6-hour scanning
- ✅ **Phase 4**: AWS Cost Explorer integration
- ✅ **Phase 5**: Interactive Streamlit dashboard + Docker
- ✅ **Phase 6**: AI-powered insights with Ollama (Mistral)

## 🚀 Features

### Automated Monitoring
- **6-hour scanning**: Runs automatically at 00:00, 06:00, 12:00, 18:00 UTC
- **Idle detection**: Identifies EC2 instances with <5% CPU usage
- **Historical tracking**: Stores scan data in DynamoDB
- **Cost analysis**: Daily AWS spend tracking via Cost Explorer

### Interactive Dashboard
- **Real-time metrics**: Scans, idle instances, potential savings
- **Visual analytics**: Charts for scan activity, cost trends, CPU distribution
- **Filtering**: By time period, instance state, idle status
- **AI Assistant**: Ask questions about your AWS costs in natural language

### AI Intelligence
- **Natural language queries**: "Why are my costs high?"
- **Contextual recommendations**: Based on YOUR actual AWS data
- **Multiple interfaces**: CLI scripts, interactive chat, dashboard integration
- **Powered by Ollama (Mistral)**: Local LLM for privacy

## 📊 Demo

**Current Findings from Real Data:**
- 8 scans collected over 2 days
- 2 unique instances monitored
- 50% idle rate detected (4 out of 8 scans)
- **$0.25 potential savings** identified

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  EventBridge │──►   │    Lambda    │                   │
│  │  (Scheduler) │      │   Scanner    │                   │
│  └──────────────┘      └──────┬───────┘                   │
│     Cron: */6 hrs              │                           │
│                               ▼                           │
│                        ┌──────────────┐                   │
│                        │  DynamoDB    │                   │
│                        │ Scan History │                   │
│                        └──────────────┘                   │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  EventBridge │──►   │    Lambda    │                   │
│  │  (Daily)     │      │ Cost Analyzer│                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                           │
│                               ├──► Cost Explorer API       │
│                               │                           │
│                               ▼                           │
│                        ┌──────────────┐                   │
│                        │  DynamoDB    │                   │
│                        │ Cost History │                   │
│                        └──────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Queries data
                            │
                   ┌────────┴──────────┐
                   │   Local Machine   │
                   ├───────────────────┤
                   │                   │
                   │  Streamlit        │
                   │  Dashboard   ◄────┤── Ollama (AI)
                   │                   │
                   │  Docker or Local  │
                   └───────────────────┘
```

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Cloud** | AWS (Lambda, DynamoDB, EventBridge, Cost Explorer, CloudWatch) |
| **Language** | Python 3.13 |
| **Frontend** | Streamlit, Plotly |
| **AI** | Ollama (Mistral 7B) |
| **Containers** | Docker, Docker Compose |
| **IaC** | AWS CLI (Terraform planned for Phase 8) |
| **CI/CD** | GitHub Actions (planned for Phase 10) |

## 📦 Installation

### Prerequisites
- AWS Account with CLI configured
- Python 3.13+
- Docker Desktop (optional)
- Ollama installed (for AI features)

### Quick Start

#### 1. Clone Repository
```bash
git clone https://github.com/Shrinidhi3012/aws-cost-optimizer.git
cd aws-cost-optimizer
```

#### 2. Deploy AWS Infrastructure
```bash
# Configure AWS CLI
aws configure

# Create DynamoDB tables, Lambda functions, EventBridge rules
# (See detailed setup in docs/SETUP.md)
```

#### 3. Run Dashboard Locally
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r dashboard/requirements.txt

# Start Ollama (for AI features)
ollama serve

# Run dashboard
cd dashboard
streamlit run app.py
```

Open http://localhost:8501

## 🐳 Docker Deployment

### Pull from DockerHub
```bash
docker pull shrinidhi3012/aws-cost-optimizer-dashboard:latest
```

### Run with Docker Compose
```bash
# Start Ollama first (for AI features)
ollama serve

# Start dashboard
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop
docker-compose down
```

**Note**: AI features require Ollama running on host machine

## 🤖 AI Assistant Usage

### CLI Insights
```bash
python3 scripts/ai_insights.py
```

### Interactive Chat
```bash
python3 scripts/ai_chat.py
```

### Dashboard Integration
Ask questions directly in the dashboard's AI Assistant panel!

**Example Questions:**
- "Why is my idle rate 50%?"
- "What instances should I terminate?"
- "How can I reduce my AWS bill?"
- "What's the best optimization strategy?"

## 💰 Cost

**100% Free Tier Eligible!**

- Lambda: 1M requests/month (using ~120/month = 0.012%)
- DynamoDB: 25GB storage (using <1MB)
- EventBridge: Unlimited rules (free forever)
- Cost Explorer: First 50 requests/month free
- **Total monthly cost: $0** ✅

## 📈 Future Enhancements

- ⏳ **Phase 7**: Advanced scanning (RDS, EBS, S3, untagged resources)
- ⏳ **Phase 8**: Terraform infrastructure as code
- ⏳ **Phase 9**: Enhanced containerization
- ⏳ **Phase 10**: CI/CD pipeline with GitHub Actions
- ⏳ **Phase 11**: CloudWatch alarms and SNS notifications
- ⏳ **Phase 12**: Complete documentation and demo video

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome!

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

**Shrinidhi Kulkarni**
- GitHub: [@Shrinidhi3012](https://github.com/Shrinidhi3012)
- DockerHub: [shrinidhi3012](https://hub.docker.com/u/shrinidhi3012)

## 🙏 Acknowledgments

- Built as a portfolio project to demonstrate AWS, Python, Docker, and AI integration skills
- Inspired by real-world cost optimization challenges in cloud infrastructure

---

**⭐ If you find this project useful, please consider giving it a star!**