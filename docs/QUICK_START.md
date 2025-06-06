# RisenOne Fire Analysis Agent - Quick Start

## Activate Environment
```bash
source activate_env.sh
```

## Launch Agent
```bash
adk web
# Visit: http://localhost:8000
```

## Test Queries (Fire Analysis)

### Initial Test:
- "Hi, What data do you have access to?"

### Fire Risk Analysis:
- "What's the fire danger in Zone 7 based on current weather conditions?"
- "Should we position crews in northern Montana tomorrow?"
- "Calculate fire spread probability with 15 mph winds from the east"

### Weather Analysis:
- "How do current drought conditions compare to historical fire seasons?"
- "What's the 7-day forecast for fire risk in this region?"

### Crew Positioning:
- "Optimize crew deployment for maximum coverage in high-risk areas"
- "What's the response time for current crew positions?"

### Follow-up Questions:
- "What if we add 2 more crews to that area?"
- "How confident are you in this prediction?"
- "Show me this on the map"

## Deploy to Production
```bash
cd deployment/
python3 deploy.py --create
```

## Architecture Diagrams
Visit the interactive architecture documentation:
- **Multi-Agent System**: [View Interactive Diagram](https://techtrend.github.io/USDA-AI-Innovation-Hub/risenone-fire-analysis-agent/docs/architecture/interactive/risen_one_mas_architecture.html)
- **AWS-GCP Integration**: [View Interactive Diagram](https://techtrend.github.io/USDA-AI-Innovation-Hub/risenone-fire-analysis-agent/docs/architecture/interactive/risen_one_integration_architecture.html)

## Troubleshooting

### Authentication Issues:
```bash
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery
```

### Environment Issues:
```bash
# Re-run setup
./setup-risenone.sh

# Reset poetry environment
cd agent && poetry env remove python && poetry install
```

### Agent Issues:
```bash
# Check logs when running
adk web

# Verify configuration
cat agent/.env

# Test agent directly
cd agent && python test_agent.py
```

### Common Error Solutions:
- **"No data available"**: Check BigQuery dataset configuration in `.env`
- **"Authentication failed"**: Re-run `gcloud auth application-default login`
- **"Agent not responding"**: Verify all environment variables in `agent/.env`
- **"Import errors"**: Ensure poetry environment is activated

## Expected Responses

### For "Hi, What data do you have access to?":
Agent should respond about available fire analysis data including weather stations, fire danger indices, and field observations.

### For Fire Risk Queries:
Agent should provide:
- Risk level (LOW/MODERATE/HIGH/EXTREME)
- Contributing factors (weather, fuel moisture, wind)
- Recommended actions
- Confidence levels

### For Crew Positioning:
Agent should suggest:
- Optimal crew locations with coordinates
- Coverage analysis percentages
- Response time estimates
- Resource allocation recommendations

---

**Note**: This agent is designed for Forest Service fire analysis workflows. All test queries focus on fire risk assessment, weather analysis, and crew positioning decisions.