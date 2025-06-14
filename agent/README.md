# RisenOne Fire Analysis Multi-Agent System

## Overview

This project implements an AI-powered fire risk analysis system designed specifically for Forest Service scientists and fire management personnel. Built on Google's Agent Development Kit (ADK), it provides natural language interfaces for complex fire danger calculations, weather analysis, and predictive modeling that traditionally require manual spreadsheet work.

The system integrates with the RisenOne Data Mesh platform to deliver real-time fire risk insights through conversational AI, replacing time-consuming manual processes with instant, intelligent analysis.

## 🔥 Agent Architecture

| Agent | Role | Capabilities |
|-------|------|-------------|
| **fire_analysis_coordinator** | Root Orchestrator | Manages conversations, routes queries, coordinates multi-agent responses |
| **weather_analysis_agent** | Meteorological Analysis | Weather station data processing, forecast interpretation, atmospheric modeling |
| **fire_risk_agent** | Danger Assessment | Fire danger index calculations, risk scoring, spread probability analysis |
| **ml_prediction_agent** | Predictive Modeling | BigQuery ML fire spread models, crew positioning optimization, resource allocation |

### Key Features

* **Natural Language Fire Queries:** Ask complex questions like "What's the fire risk in Zone 7 tomorrow based on wind forecasts?"
* **Automated Calculations:** Replace manual spreadsheet work with instant AI-driven fire danger computations
* **Real-time Data Integration:** Connects to weather stations, fire detection systems, and field observations
* **Predictive Analytics:** 7-day fire risk forecasting (3-day historical + current + 3-day prediction)
* **Map Integration:** Seamlessly integrates with OpenLayers-based geospatial interface
* **Multi-Zone Analysis:** Supports analysis across multiple Forest Service zones and regions

## 🌡️ Data Sources

The system processes multiple types of fire-related data:

* **Weather Station Data:** Temperature, humidity, wind speed/direction, precipitation from NOAA and local stations
* **Fire Danger Data:** Current fire detection, danger indices, fuel moisture levels, burning index
* **Field Observations:** Scientist-collected vegetation data, soil conditions, fuel loads, ground assessments
* **Satellite Data:** Google Earth Engine integration for vegetation monitoring and large-scale analysis
* **Historical Data:** Fire spread patterns, weather correlations, seasonal trends

## 🚀 Quick Start

### Prerequisites

* Google Cloud Project with Vertex AI enabled
* Python 3.12+
* Poetry package manager
* Access to RisenOne AWS data sources (optional for hybrid mode)

### Installation

1. **Activate Environment:**
   ```bash
   source activate_env.sh
   ```

2. **Configure Environment:**
   Edit `agent/.env` with your GCP project details:
   ```bash
   GOOGLE_CLOUD_PROJECT="your-project-id"
   GOOGLE_CLOUD_LOCATION="us-central1"
   BQ_DATASET_ID="risenone_fire_analysis"
   ```

3. **Start the Agent:**
   ```bash
   # CLI Mode
   adk run data_science
   
   # Web Interface
   adk web
   ```

## 💬 Example Interactions

### Fire Risk Assessment
```
🧑‍🔬 Scientist: "Should we position crews in Zone 7 based on tomorrow's forecast?"

🤖 Agent: "Based on tomorrow's forecast for Zone 7:
- Wind speeds: 15-25 mph from SW
- Humidity: 25-35% (CRITICAL)
- Fire danger index: EXTREME (90/100)

Recommended crew positioning:
✅ Station 12 crews at coordinates [47.2, -114.1] 
✅ Pre-position 8 additional crews at Forward Base Alpha
⚠️ High probability fire spread toward populated areas

Expected response time: <8 minutes for 85% of Zone 7"
```

### Weather Pattern Analysis
```
🧑‍🔬 Scientist: "How do current drought conditions compare to historical fire seasons?"

🤖 Agent: "Current drought analysis vs. historical data:
- Soil moisture: 15% below 20-year average
- Precipitation deficit: 2.3 inches since April
- Similar to 2018 and 2003 fire seasons

Risk factors:
🔴 Extended dry period (45+ days)
🔴 Fuel moisture content: CRITICAL (8-12%)
🟡 Wind patterns: Moderate concern

Historical correlation shows 78% probability of significant fire activity in next 14 days under these conditions."
```

### Predictive Modeling
```
🧑‍🔬 Scientist: "If we get 15 mph winds from the east, how would fire spread from the Miller Creek area?"

🤖 Agent: "Fire spread simulation for Miller Creek with 15 mph easterly winds:

Hour 1-3: 
- Spread rate: 6 chains/hour northeast
- Containment probability: 65% with current resources

Hour 3-6:
- Potential area: 1,200 acres
- Structures at risk: 12 buildings
- Evacuation trigger: Hour 4

Recommended actions:
🚨 Deploy air resources immediately
🚁 Position crews at Highway 200 as fire break
📞 Notify evacuation coordinators for Sunset Valley area"
```

## 🛠️ Technical Architecture

### Multi-Agent Coordination
The system uses Google's Agent Development Kit multi-agent framework where each specialized agent maintains its own session memory while sharing context through the root coordinator.

### Data Pipeline
```
AWS Data Mesh → API Bridge → GCP Processing → Agent Analysis → Map Visualization
     ↓              ↓            ↓              ↓             ↓
Weather/Fire     Authentication  BigQuery ML   AI Insights   OpenLayers
Field Data       & Security      Earth Engine  Natural Lang. Interactive UI
```

### Integration Points
* **AWS S3 Integration:** Real-time data fetching from existing RisenOne platform
* **BigQuery ML:** Fire spread prediction models and statistical analysis
* **Google Earth Engine:** Satellite imagery and vegetation monitoring
* **OpenLayers Map:** Geospatial visualization and risk overlay generation

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
GOOGLE_CLOUD_PROJECT="risenone-ai-prototype"
BQ_DATASET_ID="fire_risk_poc"

# Agent Models
FIRE_COORDINATOR_MODEL="gemini-2.0-flash-001"
WEATHER_AGENT_MODEL="gemini-2.0-flash-001"
FIRE_RISK_AGENT_MODEL="gemini-2.0-flash-001"
ML_PREDICTION_AGENT_MODEL="gemini-2.0-flash-001"

# Fire Analysis Specific
FIRE_ZONE_DEFAULT="zone_7"
FORECAST_DAYS=7
WEATHER_UPDATE_INTERVAL=3600
```

### BigQuery Schema
The system expects these tables in your BigQuery dataset (`fire_risk_poc`):
* `station_metadata` - Weather station locations and classifications (278 stations)
* `nfdr_daily_summary` - Fire danger calculations and burning indices (9,235 records)
* `weather_daily_summary` - Weather observations affecting fire risk (3,866 records)
* `fuel_samples` - Fuel moisture field measurements (2,442 records)
* `site_metadata` - Observation site details and information (1,565 records)
* **Total Records:** 17,386 accessible for comprehensive fire analysis

## 🧪 Testing Fire Analysis

Test the system with fire-specific scenarios:

```bash
# Run fire analysis tests
poetry run pytest tests/test_fire_analysis.py

# Test weather integration
poetry run pytest tests/test_weather_agents.py

# Evaluate prediction accuracy
poetry run pytest eval/test_fire_predictions.py
```

## 🚀 Deployment

### Local Development
```bash
# Start web interface for testing
adk web
# Navigate to http://localhost:8000
```

### Production Deployment
```bash
# Build for Vertex AI Agent Engine
poetry build --format=wheel --output=deployment

# Deploy to GCP
cd deployment/
python3 deploy.py --create
```

## 🔗 Integration with RisenOne Platform

This agent system is designed to integrate with the existing RisenOne Data Mesh platform:

* **Hybrid Architecture:** Agents run on GCP while data remains on AWS during transition
* **API Integration:** RESTful endpoints for map interface communication
* **Real-time Updates:** WebSocket connections for live fire data streaming
* **Authentication:** Secure service account integration with existing platform

## 📚 For Forest Service Scientists

### Common Fire Analysis Workflows

1. **Morning Briefing Preparation:**
   - "Summarize overnight fire activity and today's risk forecast"
   - "Which zones need priority attention based on weather conditions?"

2. **Resource Allocation:**
   - "Optimize crew positioning for maximum coverage in high-risk areas"
   - "Calculate response times for current crew deployment"

3. **Incident Response:**
   - "Model fire spread scenarios for the Blackfoot Fire"
   - "Identify evacuation trigger points and timing"

4. **Long-term Planning:**
   - "Analyze seasonal fire patterns for budget planning"
   - "Identify areas needing fuel reduction based on risk modeling"

## 🆘 Troubleshooting

### Common Issues

* **Authentication Errors:** Ensure `gcloud auth application-default login` is completed
* **Data Access Issues:** Verify BigQuery permissions and dataset existence
* **Agent Coordination Problems:** Check session state and agent model configurations
* **Weather Data Delays:** Confirm API keys and data source connectivity

### Support Resources

* Check logs at `/logs/agent_activity.log`
* Test individual agents: `adk run data_science --agent=weather_analysis_agent`
* Validate data connections: `python scripts/test_data_sources.py`

## 🚨 Production Considerations

⚠️ **This is a prototype system for Forest Service evaluation.**

For production deployment:
- Implement comprehensive error handling for critical fire situations
- Add redundant data sources and failover mechanisms  
- Establish audit logging for all fire-related decisions and recommendations
- Include data validation and quality checks for safety-critical outputs
- Implement role-based access controls for different user types

---

**Built for Forest Service Scientists by TechTrend Inc. & RisenOne Consulting**
*Modernizing wildfire response through intelligent automation*