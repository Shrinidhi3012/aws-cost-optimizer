# AWS Cost Optimizer

An AI-powered tool that automatically scans AWS accounts, identifies cost-saving opportunities, and provides natural language insights.

## Project Status
🚧 **In Development** - Currently implementing Phase 1: Core Scanner

## Features (Planned)
- ✅ Phase 1: EC2 idle instance detection
- ⏳ Phase 2: DynamoDB persistence
- ⏳ Phase 3: Automated scheduling
- ⏳ Phase 4: Cost tracking
- ⏳ Phase 5: Web dashboard
- ⏳ Phase 6: AI-powered insights
- ⏳ Phases 7-12: Advanced features

## Tech Stack
- **Cloud**: AWS (Lambda, DynamoDB, EventBridge)
- **Language**: Python 3.13
- **AI**: Ollama (Mistral)
- **IaC**: Terraform
- **Containers**: Docker
- **CI/CD**: GitHub Actions

## Setup
Prerequisites:
- AWS Account
- AWS CLI configured
- Python 3.13+
- Docker Desktop
## 🐳 Docker Deployment

### Pull from DockerHub
```bash
docker pull shrinidhi3012/aws-cost-optimizer-dashboard:latest
```

### Run with Docker
```bash
docker run -p 8501:8501 \
  -v ~/.aws:/root/.aws:ro \
  shrinidhi3012/aws-cost-optimizer-dashboard:latest
```

Then open: http://localhost:8501

### Run with Docker Compose
```bash
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop
docker-compose down
```

### Build Locally
```bash
cd dashboard
docker build -t aws-cost-optimizer-dashboard .
```

---

## 📊 Dashboard Features
- Real-time AWS resource monitoring
- Cost optimization insights
- Interactive charts and graphs
- Idle instance detection
- Historical trend analysis
