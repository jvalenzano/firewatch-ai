# RisenOne Fire Analysis Agent - Developer Guide

## 🎯 Project Overview

**Mission**: Transform Forest Service fire risk analysis from manual spreadsheet calculations to intelligent AI-powered workflows.

**Partnership**: TechTrend Inc. (AI/ML expertise) + RisenOne Consulting (Forest Service domain knowledge)

**Technology Stack**: Google ADK multi-agent system, Vertex AI, BigQuery ML, Google Earth Engine

**Target Users**: Forest Service scientists analyzing fire danger, crew positioning, and weather forecasting

---

## 🏗️ System Architecture

### Multi-Agent Design
```
🤖 fire_analysis_coordinator (Root)
├── 🌡️ weather_analysis_agent (Meteorological data & forecasting)
├── 🔥 fire_risk_agent (Danger calculations & risk assessment)
└── 🧠 ml_prediction_agent (BigQuery ML models & predictions)
```

### Platform Integration
```
AWS Data Mesh (Existing) ←→ API Bridge ←→ GCP AI Platform (New)
├── Weather station data              ├── Vertex AI Agent Engine
├── Fire danger indices               ├── BigQuery ML models
├── Field observations                ├── Google Earth Engine
└── OpenLayers map interface          └── Gemini 2.0 Flash
```

### Repository Structure
```
risenone-fire-analysis-agent/
├── README.md                     # Project overview with architecture navigation
├── agent/                        # ADK agent implementation
│   ├── data_science/            # Multi-agent system code
│   ├── .env                     # Environment configuration (NEVER commit)
│   ├── pyproject.toml           # Dependencies and Poetry config
│   └── README.md                # Technical implementation details
├── docs/                        # Documentation and architecture
│   ├── architecture/            # Interactive HTML diagrams
│   │   ├── index.html          # Architecture landing page
│   │   └── interactive/        # 4 interactive visualizations
│   ├── internal/               # Team documentation
│   │   └── handoffs/           # Developer handoff materials
│   ├── DEVELOPER_GUIDE.md      # This file
│   └── QUICK_START.md          # Fast setup guide
├── deployment/                  # Vertex AI deployment tools
│   ├── deploy.py               # Production deployment script
│   └── test_deployment.py      # Remote agent testing
└── setup-risenone.*           # Cross-platform setup scripts
```

---

## 🚀 Development Environment Setup

### Prerequisites
- **Python 3.12+** ([Download](https://python.org/downloads/))
- **Poetry** ([Install Guide](https://python-poetry.org/docs/))
- **Google Cloud CLI** ([Install Guide](https://cloud.google.com/sdk/docs/install))
- **Git** with enterprise GitHub access

### Quick Setup
```bash
# Clone repository
git clone https://github.techtrend.us/USDA-AI-Innovation-Hub/risenone-fire-analysis-agent.git
cd risenone-fire-analysis-agent

# Automated setup (recommended)
./setup-risenone.sh

# Manual setup alternative
cd agent
poetry install
source activate_env.sh
```

### Environment Configuration
```bash
# Copy and customize environment file
cd agent
cp .env-example .env
nano .env

# Required variables:
GOOGLE_CLOUD_PROJECT="risenone-ai-prototype"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="1"
BQ_DATASET_ID="risenone_fire_analysis"
```

### Authentication Setup
```bash
# Google Cloud authentication with proper scopes
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery

# Set quota project
gcloud auth application-default set-quota-project risenone-ai-prototype
```

### Verification
```bash
# Test local agent
cd agent
adk web
# Visit: http://localhost:8000

# Test query: "Hi, What data do you have access to?"
# Expected: Response about fire analysis data sources
```

---

## 🔄 Git Workflow & Branching Strategy

### Branch Structure
```
main                    # Production-ready code (protected)
├── develop            # Integration branch for features
├── feature/[name]     # Feature development
├── hotfix/[issue]     # Critical production fixes
└── release/[version]  # Release preparation
```

### Feature Development Process

#### 1. Create Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/fire-weather-integration
```

#### 2. Development Cycle
```bash
# Make changes in agent/ directory
# Test locally: cd agent && adk web

# Stage and commit changes
git add .
git commit -m "feat: add NOAA weather API integration

- Connect to real-time weather station data
- Update fire danger calculation models
- Add weather forecast visualization components"
```

#### 3. Testing Requirements
```bash
# Local testing (required before PR)
cd agent
adk web  # Manual testing in browser

# Automated testing
poetry run pytest tests/        # Unit tests
poetry run pytest eval/        # Integration tests

# Deployment testing (for major features)
cd deployment
python test_deployment.py --resource_id=$RESOURCE_ID
```

#### 4. Pull Request Process
```bash
git push origin feature/fire-weather-integration

# Create PR: feature/fire-weather-integration → develop
# Requirements:
# - All tests passing
# - Code review from team
# - ADK structure compliance verified
```

### Commit Message Standards
```bash
# Format: type(scope): description
feat(weather): add NOAA API integration
fix(agents): resolve fire risk calculation error
docs(architecture): update multi-agent diagrams
refactor(bigquery): optimize ML model queries
test(eval): add fire prediction accuracy tests
```

---

## 🧪 Testing Strategy

### Local Testing
```bash
# Start agent development server
cd agent
adk web

# Test fire-specific queries in browser:
# - "What's the fire risk in Zone 7 tomorrow?"
# - "Should we position crews based on wind forecasts?"
# - "Calculate fire spread probability with current conditions"
```

### Automated Testing
```bash
# Unit tests (fast, isolated)
poetry run pytest tests/ -v

# Integration tests (slower, full system)
poetry run pytest eval/ -v

# Specific test categories
poetry run pytest tests/ -k "test_fire_risk"
poetry run pytest eval/ -k "test_weather_agent"
```

### Production Testing
```bash
# Test deployed agent (staging/production)
export RESOURCE_ID="projects/481721551004/locations/us-central1/reasoningEngines/[ID]"
python deployment/test_deployment.py --resource_id=$RESOURCE_ID --user_id=test_user

# Expected responses for fire queries:
# - Risk levels (LOW/MODERATE/HIGH/EXTREME)
# - Crew positioning recommendations
# - Weather-based predictions
```

### Performance Testing
```bash
# Load testing for multiple concurrent scientists
# Response time targets:
# - Simple queries: <3 seconds
# - Complex multi-region analysis: <10 seconds
# - Crew optimization: <15 seconds
```

---

## 🚀 Deployment Process

### Local Development Deployment
```bash
# Build agent package
cd agent
poetry build --format=wheel --output=deployment

# Test build
cd deployment
python deploy.py --create

# Verify deployment
python test_deployment.py --resource_id=$NEW_RESOURCE_ID
```

### Staging Deployment
```bash
# Deploy to staging environment
export ENVIRONMENT="staging"
python deploy.py --create --env=staging

# Run staging test suite
poetry run pytest eval/ --env=staging
```

### Production Deployment
```bash
# Production deployment (requires approval)
export ENVIRONMENT="production"
python deploy.py --create --env=production

# Post-deployment verification
./scripts/production-health-check.sh
```

### Rollback Process
```bash
# Emergency rollback to previous version
python deploy.py --rollback --resource_id=$PREVIOUS_RESOURCE_ID
```

---

## 🔥 Fire Analysis Domain Specifics

### Key Concepts

**Fire Zones**: Geographic regions for resource management
- Zone 7: Northern Montana (primary development target)
- Multi-zone analysis for large incidents

**Fire Danger Indices**:
- Burning Index (BI): Potential fire intensity
- Energy Release Component (ERC): Available fuel energy
- Spread Component (SC): Forward rate of spread

**Weather Factors**:
- Temperature, humidity, wind speed/direction
- Fuel moisture content (critical for predictions)
- Precipitation forecasts (7-day window)

**Resource Types**:
- Crew positioning and optimization
- Equipment deployment (engines, aircraft)
- Response time calculations

### User Personas

**Fire Scientist**: 
- Needs: Complex analysis, statistical modeling, research data
- Queries: "How do drought conditions correlate with fire spread rates?"

**Incident Commander**:
- Needs: Real-time decisions, crew safety, resource allocation
- Queries: "Where should I position crews for maximum coverage?"

**Fire Weather Specialist**:
- Needs: Meteorological analysis, forecasting, pattern recognition
- Queries: "What's the 7-day fire weather outlook for this region?"

### Sample Test Queries
```bash
# Fire Risk Assessment
"What's the fire danger in Zone 7 based on current conditions?"
"Calculate fire spread probability with 15 mph easterly winds"

# Crew Positioning
"Optimize crew deployment for maximum Zone 7 coverage"
"What's the response time for current crew positions?"

# Weather Analysis
"How do current drought conditions compare to historical fire seasons?"
"Show me the 7-day fire weather forecast for northern Montana"

# Predictive Modeling
"If humidity drops 20% tomorrow, how does fire risk change?"
"Model fire spread scenarios for the Miller Creek area"
```

---

## 👥 Team Collaboration

### Code Review Guidelines

**Required Checks**:
- [ ] Agent runs without errors (`adk web`)
- [ ] All tests pass (`poetry run pytest`)
- [ ] Fire analysis context maintained (no generic examples)
- [ ] ADK structure compliance
- [ ] Environment variables documented
- [ ] New features have test coverage

**Review Focus Areas**:
- Fire domain accuracy (terminology, calculations)
- Agent coordination and memory management
- BigQuery ML model integration
- Error handling for critical fire decisions
- Performance impact on real-time queries

### Communication Channels

**Daily Standups**: Development progress, blockers, coordination
**Sprint Planning**: Feature prioritization, fire season considerations
**Architecture Reviews**: System design, agent interactions, data flow
**Domain Reviews**: Fire analysis accuracy, scientist feedback

### Documentation Standards

**Code Documentation**:
```python
def calculate_fire_danger_index(temperature: float, humidity: float, 
                               wind_speed: float) -> FireDangerLevel:
    """Calculate fire danger index for Forest Service scientists.
    
    Args:
        temperature: Air temperature in Fahrenheit
        humidity: Relative humidity percentage
        wind_speed: Wind speed in mph
        
    Returns:
        FireDangerLevel enum (LOW, MODERATE, HIGH, EXTREME)
        
    Fire Analysis Context:
        Uses National Fire Danger Rating System algorithms
        Integrates with existing Forest Service workflows
    """
```

**Agent Prompt Documentation**:
```python
# Fire Analysis Agent Prompts
# Context: Forest Service scientists analyzing wildfire risk
# Domain: Fire behavior, weather patterns, crew positioning
# Response Style: Professional, data-driven, actionable recommendations
```

---

## 🔧 Troubleshooting

### Common Development Issues

**Authentication Errors**:
```bash
# Re-authenticate with correct scopes
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery
```

**Poetry Environment Issues**:
```bash
# Reset environment
cd agent
poetry env remove --all
poetry install
source activate_env.sh
```

**Agent Loading Errors**:
```bash
# Check configuration
cat agent/.env
# Verify: GOOGLE_CLOUD_PROJECT, BQ_DATASET_ID, etc.

# Check logs
cd agent && adk web
# Look for error messages in terminal
```

**BigQuery Connection Issues**:
```bash
# Verify dataset exists
bq ls risenone_fire_analysis

# Check permissions
gcloud projects get-iam-policy risenone-ai-prototype
```

### Performance Issues

**Slow Query Response**:
- Check BigQuery ML model performance
- Verify efficient agent memory usage
- Monitor API rate limits
- Review complex fire calculations

**Agent Memory Issues**:
- Verify session cleanup
- Check conversation context size
- Monitor multi-agent coordination overhead

### Production Issues

**Agent Not Responding**:
```bash
# Check deployment status
gcloud ai reasoning-engines describe $RESOURCE_ID --region=us-central1

# Review logs
gcloud logging read "resource.type=vertex_ai_reasoning_engine"
```

**Incorrect Fire Analysis**:
- Verify training data quality
- Check model version compatibility
- Review prompt engineering for fire domain
- Validate calculations against known results

---

## 📚 Resources & References

### Project Documentation
- **[Technical Implementation](agent/README.md)** - Deep technical details
- **[Quick Start Guide](QUICK_START.md)** - Fast setup and testing
- **[Architecture Diagrams](architecture/)** - Interactive system visualizations
- **[Internal Documentation](internal/)** - Team handoffs and decisions

### Google Cloud Resources
- **ADK Documentation**: [Agent Development Kit](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit)
- **Vertex AI Guide**: [Vertex AI Docs](https://cloud.google.com/vertex-ai/docs)
- **BigQuery ML**: [BigQuery ML Reference](https://cloud.google.com/bigquery-ml/docs)
- **Agent Engine**: [Reasoning Engine API](https://cloud.google.com/vertex-ai/generative-ai/docs/reasoning-engine)

### Fire Analysis Domain
- **National Fire Danger Rating System**: [NFDRS Documentation](https://www.nwcg.gov/committees/nfdrs/application)
- **Fire Weather Research**: [USFS Fire Science Laboratory](https://www.firelab.org/)
- **Incident Command System**: [NWCG ICS](https://www.nwcg.gov/committees/pms/ics.html)

### Development Tools
- **Poetry Documentation**: [Python Dependency Management](https://python-poetry.org/docs/)
- **GitHub Enterprise**: [TechTrend GitHub Guide](https://github.techtrend.us/docs)
- **VS Code Extensions**: Python, ADK development tools

---

## 🎯 Roadmap & Future Development

### Current Phase: Foundation (✅ Complete)
- [x] Multi-agent architecture deployed
- [x] Basic fire analysis capabilities
- [x] Developer environment and processes
- [x] Interactive architecture documentation

### Phase 2: Fire-Specific Features (🔄 In Progress)
- [ ] Real fire/weather data integration (replace sample data)
- [ ] NOAA weather API connection
- [ ] Enhanced fire danger calculation models
- [ ] Crew positioning optimization algorithms

### Phase 3: Advanced Analytics (📋 Planned)
- [ ] Machine learning fire prediction models
- [ ] Real-time fire spread simulation
- [ ] Multi-region analysis capabilities
- [ ] Historical fire pattern analysis

### Phase 4: Production Hardening (📋 Planned)
- [ ] Performance optimization for fire season loads
- [ ] Enhanced error handling for critical decisions
- [ ] Comprehensive monitoring and alerting
- [ ] Security audit and compliance certification

### Long-term Vision
- Integration with existing Forest Service systems
- Mobile interface for field personnel
- Real-time fire tracking and prediction
- Multi-agency collaboration platform

---

## 🤝 Support & Escalation

### Development Support
- **Primary**: Internal team Slack channels
- **Architecture Questions**: Weekly architecture review meetings
- **Blocking Issues**: Tag `@fire-analysis-team` in GitHub issues

### Domain Expertise
- **Fire Analysis**: RisenOne Consulting domain experts
- **Forest Service Workflows**: Field scientist advisory group
- **Operational Requirements**: Incident commander feedback sessions

### Technical Escalation
- **ADK Issues**: Google Cloud support channels
- **Performance Problems**: TechTrend senior engineers
- **Production Incidents**: 24/7 on-call rotation

---

**Last Updated**: June 2025  
**Version**: 1.0.0  
**Status**: Ready for Collaborative Development 🔥

*Built with ❤️ for Forest Service Scientists*  
*A TechTrend Inc. & RisenOne Consulting Collaboration*