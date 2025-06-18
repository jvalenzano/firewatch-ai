# RisenOne Fire Analysis Agent

> **Modernizing Forest Service wildfire response through intelligent automation**

## 🎯 Project Overview

The RisenOne Fire Analysis Agent represents a collaborative effort between **TechTrend Inc.** and **RisenOne Consulting** to transform how Forest Service scientists analyze fire risk and make critical resource allocation decisions. Built on Google's Agent Development Kit (ADK), this system replaces time-consuming manual calculations with conversational AI that delivers instant, intelligent insights.

## 🎨 Interactive Architecture Visualizations

<div align="center">

[![Complete Architecture](https://img.shields.io/badge/🏗️_Complete_Architecture-Interactive_Overview-667eea?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://github.techtrend.us/pages/USDA-AI-Innovation-Hub/risen-one-science-research-agent/docs/architecture/interactive/risenone_architecture.html)

📚 **[Complete Architecture Documentation →](https://github.techtrend.us/pages/USDA-AI-Innovation-Hub/risen-one-science-research-agent/docs/architecture/)**

</div>

### The Challenge

Forest Service scientists currently spend hours downloading weather data, fire danger indices, and field observations into spreadsheets to manually calculate fire spread probabilities, risk assessments, and crew positioning strategies. This manual process is:

- ⏱️ **Time-consuming**: Hours of work for each analysis
- ❌ **Error-prone**: Manual calculations introduce risk
- 📊 **Limited scope**: Can't easily run multiple scenarios
- 💰 **Expensive**: Existing tools cost significantly more while providing less value

### The Solution

Our multi-agent AI system enables scientists to ask natural language questions like:

*"Should we position crews in Zone 7 based on tomorrow's forecast?"*

And receive immediate, comprehensive analysis including:
- Fire danger calculations and risk scoring
- Optimal crew positioning recommendations  
- Weather pattern analysis and 7-day forecasts
- Predictive fire spread modeling
- Interactive map visualizations

## 🏗️ Architecture Overview

<div align="center">

![Architecture Overview](docs/architecture/diagrams/simple-overview.svg)

**📊 [View Detailed Multi-Agent System Diagram →](https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent/blob/phase-ii/docs/architecture/diagrams/multi-agent-detail.svg)**

</div>

### Key Components

| Component | Description | Technology |
|-----------|-------------|------------|
| **Fire Analysis Coordinator** | Root orchestrator managing conversations and routing queries | Vertex AI Agent Engine |
| **Weather Analysis Agent** | Meteorological data processing and forecast interpretation | Gemini 2.0 Flash |
| **Fire Risk Agent** | Danger index calculations and risk assessments | BigQuery ML |
| **ML Prediction Agent** | Fire spread modeling and crew optimization | Google Earth Engine |

## 🚀 Quick Start

### Prerequisites
- Google Cloud Project with Vertex AI enabled
- Python 3.12+
- Poetry package manager
- Access to RisenOne data sources (optional)

### Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent.git
   cd risen-one-science-research-agent
   ./setup-risenone.sh
   ```

2. **Configure Environment**
   ```bash
   # Copy and edit configuration
   cp agent/.env-example agent/.env
   nano agent/.env
   ```

3. **Start the System**
   ```bash
   # Activate environment
   source activate_env.sh
   
   # Navigate to agent directory
   cd agent
   
   # Web interface (recommended)
   adk web
   
   # Or CLI mode
   adk run data_science
   ```

Navigate to `http://localhost:8000` to access the interactive interface.

## 📁 Repository Structure

```
risenone-fire-analysis-agent/
├── README.md                 # This file - project overview
├── setup-risenone.sh         # Cross-platform setup script (Mac/Linux)
├── setup-risenone.ps1        # Windows PowerShell setup script
├── agent/                    # Core agent implementation
│   ├── data_science/         # Multi-agent system code
│   ├── README.md            # Technical implementation guide
│   ├── pyproject.toml       # Dependencies and configuration
│   └── .env                 # Environment configuration
├── docs/                    # Documentation and architecture
│   ├── architecture/        # Interactive system design diagrams
│   ├── internal/           # Internal team documentation
│   ├── DEVELOPER_GUIDE.md   # Detailed development guide
│   └── QUICK_START.md      # Getting started guide
├── deployment/              # Vertex AI deployment tools
└── .github/                 # GitHub templates and workflows
```

## 💬 Example Interactions

### Fire Risk Assessment
```
🧑‍🔬 Scientist: "What's the fire risk in Zone 7 for the next 3 days?"

🤖 Agent: "Zone 7 Fire Risk Analysis (Next 72 Hours):

📅 Today: MODERATE (65/100)
📅 Tomorrow: HIGH (82/100) 
📅 Day 3: EXTREME (94/100)

Key factors:
🌡️ Rising temperatures (95°F peak)
💨 Increasing winds (15-25 mph SW)
💧 Dropping humidity (25% by Day 3)
🌧️ No precipitation forecast

Recommendations:
✅ Pre-position crews at Station 12
⚠️ Monitor wind shift at 14:00 tomorrow
🚨 Consider evacuation prep for Day 3"
```

### Resource Optimization
```
🧑‍🔬 Scientist: "Optimize crew positioning for maximum Zone 7 coverage"

🤖 Agent: "Optimal Crew Deployment Strategy:

🎯 3 strategic positions identified:
• Base Alpha: [47.2°N, -114.1°W] - 8 crews
• Station 12: [47.1°N, -114.3°W] - 6 crews  
• Forward Post: [47.0°N, -114.0°W] - 4 crews

📊 Coverage Analysis:
• Response time: <8 minutes for 85% of zone
• Risk mitigation: 78% effective
• Resource efficiency: 92% optimal

💰 Cost-benefit: $2.3M savings vs. traditional deployment"
```

## 🌟 Key Benefits

### For Forest Service Scientists
- **Instant Analysis**: Get answers in seconds, not hours
- **Better Decisions**: Run multiple scenarios quickly
- **Risk Reduction**: AI-validated calculations minimize errors
- **Cost Savings**: Reduce expensive manual labor and tools

### For IT and Leadership  
- **Hybrid Architecture**: Minimal disruption to existing AWS platform
- **Scalable**: Handle peak fire season workloads automatically
- **FedRAMP Ready**: Built for government security requirements
- **Future-Proof**: Clear migration path to full cloud modernization

## 🔧 Development

### Contributing
This project follows the collaborative model between TechTrend Inc. and RisenOne Consulting:

- **TechTrend**: AI/ML development, GCP integration, ADK implementation
- **RisenOne**: Domain expertise, AWS platform, Forest Service workflows
- **Joint**: Architecture decisions, testing, deployment

### Development Setup
```bash
# Run setup script for your platform
./setup-risenone.sh          # Mac/Linux/WSL
# or .\setup-risenone.ps1    # Windows

# Navigate to agent directory
cd agent

# Install development dependencies  
poetry install --with=dev

# Run tests
poetry run pytest tests/

# Run evaluations
poetry run pytest eval/
```

## 👥 For Developers

- **[Internal Documentation](docs/internal/)** - Team handoffs, architecture decisions, meeting notes
- **[Technical Guide](agent/README.md)** - Deep technical implementation details
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development workflows and agent connection details
- **[Quick Start Guide](docs/QUICK_START.md)** - Fast setup and testing workflows
- **[Architecture Diagrams](docs/architecture/)** - Interactive system visualizations

## 🚀 Deployment

### Current Production Status
- **Agent Engine**: ✅ ACTIVE on Vertex AI
- **Display Name**: RisenOne Fire Analysis Agent
- **Architecture**: Ultra-minimal (production-optimized)
- **Status**: Ready for fire analysis queries

### Development Environment
```bash
# Local testing
cd agent
adk web
```

### Production Deployment
The agent is already deployed to Vertex AI Agent Engine. For updates:

```bash
# Build for Vertex AI Agent Engine
cd agent
poetry build --format=wheel --output=deployment

# Deploy updates to GCP
cd deployment/
python3 deploy.py --update
```

## 🤝 Partnership

This project represents the collaboration between:

**TechTrend Inc.**
- AI/ML expertise and GCP specialization
- Vertex AI Agent Engine implementation  
- USDA Innovation Hub leadership

**RisenOne Consulting**
- Forest Service domain knowledge
- Existing data mesh platform
- Fire analysis workflow expertise

**Shared Vision**: Modernize wildfire response through intelligent automation while maintaining the reliability and security required for critical emergency operations.

## 📚 Resources

- [Technical Implementation Guide](agent/README.md) - Deep technical details
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development workflows and agent connection
- [Architecture Documentation](docs/architecture/) - System design
- [Quick Start Guide](docs/QUICK_START.md) - Fast setup guide

## 🆘 Support

### For Technical Issues
- Check [Technical README](agent/README.md) for troubleshooting
- Review [Developer Guide](docs/DEVELOPER_GUIDE.md) for agent connection details
- Review logs at `agent/logs/`
- Test individual components with `agent/test_agent.py`

### For Business Questions
- **TechTrend Team**: Ziaur Rahman, Jason Valenzano
- **RisenOne Team**: Matt Reiss, Terry Kleoppel

## ⚠️ Important Notes

**This is a production-ready system with active Vertex AI deployment.**

Current capabilities:
- ✅ Fire analysis conversations and domain knowledge
- ✅ Ultra-minimal architecture for reliable emergency response
- ✅ Production deployment on Vertex AI Agent Engine
- 🔄 Weather data integration (Phase 2)
- 🔄 Advanced ML predictions (Phase 3)

For production considerations:
- Implement comprehensive error handling for emergency situations
- Add redundant data sources and failover mechanisms
- Establish audit logging for all fire-related decisions
- Include data validation for safety-critical outputs
- Implement role-based access controls

---

**Built with ❤️ for Forest Service Scientists**  
*A TechTrend Inc. & RisenOne Consulting Collaboration*

*Powered by Google Cloud AI • Agent Development Kit • Vertex AI*