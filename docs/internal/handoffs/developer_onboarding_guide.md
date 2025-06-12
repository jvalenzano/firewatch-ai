# 🔥 RisenOne Fire Risk Agent - Developer Onboarding Guide

**Welcome to the RisenOne Fire Risk AI Platform!**  
This guide will get you set up with a complete local development environment for our Google Cloud AI agent system.

---

## 🎯 **Project Overview**

### **Mission**
Transform Forest Service fire risk analysis from 3-4 hour manual spreadsheet calculations to 30-second AI-powered workflows.

### **Technology Stack**
- **AI Platform**: Google ADK (Agent Development Kit) with Vertex AI
- **Models**: Gemini 2.0 Flash multi-agent system
- **Data**: BigQuery with fire risk datasets (277+ weather stations)
- **Development**: Python 3.12, virtual environments
- **Repository**: GitHub Enterprise

### **What You'll Build**
- Local fire risk agent development environment
- Access to production-grade fire data (NFDR calculations, weather stations)
- Ability to deploy new agents to Google Cloud
- Integration with 277 weather stations across the US

---

## ⚙️ **Prerequisites**

### **Required Software**
- **Python 3.12+** - [Download here](https://python.org/downloads/)
- **Google Cloud CLI** - [Install guide](https://cloud.google.com/sdk/docs/install)
- **Git** with GitHub Enterprise access
- **Code Editor** - VS Code, Cursor, or your preferred IDE

### **Required Access**
- **GitHub Enterprise**: Access to `github.techtrend.us`
- **Google Cloud Project**: `risenone-ai-prototype`
- **TechTrend Email**: For authentication and access

---

## 🚀 **Setup Process (30 minutes)**

### **Step 1: Clean Environment Setup (5 minutes)**

If you have any existing project files, start fresh:

```bash
# Remove any existing project directory
cd ~/
rm -rf risenone-fire-analysis-agent risen-one-science-research-agent

# Navigate to your development directory
cd ~/  # or wherever you keep projects
```

### **Step 2: Clone Repository (3 minutes)**

```bash
# Clone the repository with correct naming
git clone https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent.git

# Navigate into the project
cd risen-one-science-research-agent

# Verify repository structure
ls -la
# You should see: agent/, docs/, deployment/, data/, README.md, etc.
```

### **Step 3: Python Virtual Environment (5 minutes)**

**⚠️ CRITICAL: This project uses `venv`, not Poetry or conda**

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment (REQUIRED for all development)
source venv/bin/activate

# Verify activation - you should see (venv) in your prompt
# ✅ Correct: user@host (venv) $
# ❌ Wrong:   user@host $

# Verify Python and pip paths
which python  # Should show: .../risen-one-science-research-agent/venv/bin/python
which pip     # Should show: .../risen-one-science-research-agent/venv/bin/pip
```

### **Step 4: Install Dependencies (5 minutes)**

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install vertexai absl-py python-dotenv

# Install agent package in development mode
pip install -e ./agent

# Verify installations
python -c "import vertexai; print('✅ vertexai ready')"
python -c "from absl import app, flags; print('✅ absl ready')"
python -c "from dotenv import load_dotenv; print('✅ dotenv ready')"
```

### **Step 5: Environment Configuration (5 minutes)**

```bash
# Navigate to agent directory
cd agent

# Copy environment template
cp .env-example .env

# Edit environment file
nano .env  # or code .env if using VS Code
```

**Required .env Configuration:**
```bash
# Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
GOOGLE_GENAI_USE_VERTEXAI=1

# Vertex backend config
GOOGLE_CLOUD_PROJECT=risenone-ai-prototype
GOOGLE_CLOUD_LOCATION=us-central1

# Set up BigQuery Agent
BQ_PROJECT_ID=risenone-ai-prototype
BQ_DATASET_ID=fire_risk_poc

# Leave these as defaults
NL2SQL_METHOD="BASELINE"
BQML_RAG_CORPUS_NAME=''
CODE_INTERPRETER_EXTENSION_NAME=''

# Models (leave as defaults)
ROOT_AGENT_MODEL='gemini-2.0-flash-001'
ANALYTICS_AGENT_MODEL='gemini-2.0-flash-001'
BIGQUERY_AGENT_MODEL='gemini-2.0-flash-001'
BASELINE_NL2SQL_MODEL='gemini-2.0-flash-001'
CHASE_NL2SQL_MODEL='gemini-2.0-flash-001'
BQML_AGENT_MODEL='gemini-2.0-flash-001'
```

### **Step 6: Google Cloud Authentication (7 minutes)**

```bash
# Return to project root
cd /path/to/risen-one-science-research-agent

# Authenticate with Google Cloud
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery

# Set quota project
gcloud auth application-default set-quota-project risenone-ai-prototype

# Clear any conflicting environment variables
unset GOOGLE_APPLICATION_CREDENTIALS

# Verify authentication works
gcloud auth application-default print-access-token
# Should return a long token string
```

---

## ✅ **Verification & Testing**

### **Test 1: Agent Development Environment**
```bash
# Navigate to agent directory
cd agent

# Test agent import (this will create a Code Interpreter extension - takes ~20 seconds)
python -c "from dotenv import load_dotenv; load_dotenv(); from data_science.agent import root_agent; print('✅ Fire Risk Agent development environment ready')"

# Expected output:
# No CODE_INTERPRETER_ID found in the environment. Create a new one.
# Creating Extension... (takes ~20 seconds)
# Extension created. Resource name: projects/.../extensions/...
# ✅ Fire Risk Agent development environment ready
```

### **Test 2: Production Agent Connectivity**
```bash
# Test the production agent (this confirms everything is working)
curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "class_method": "stream_query",
    "input": {
      "user_id": "onboarding_test",
      "message": "How many weather stations do we have fire data for?"
    }
  }' \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse"

# Expected response should include:
# "There are 277 weather stations with fire data."
```

### **Test 3: Local Development Server (Optional)**
```bash
# Start local development server
adk web

# Visit: http://localhost:8000
# Test query: "How many weather stations do we have fire data for?"
# Should get response about 277 weather stations
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue: `pip: command not found`**
```bash
# Virtual environment not activated
source venv/bin/activate
# Verify with: which pip
```

### **Issue: `ModuleNotFoundError: No module named 'vertexai'`**
```bash
# Install missing packages
source venv/bin/activate
pip install vertexai absl-py python-dotenv
```

### **Issue: `File ./client-access-key.json was not found`**
```bash
# Clear conflicting environment variable
unset GOOGLE_APPLICATION_CREDENTIALS
# Then test agent import again
```

### **Issue: `Getting metadata from plugin failed with error: Reauthentication is needed`**
```bash
# Re-authenticate with Google Cloud
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery
```

### **Issue: Agent can't access fire data**
```bash
# Check .env configuration
grep -E "(BQ_DATASET_ID|BQ_PROJECT_ID)" agent/.env
# Should show:
# BQ_PROJECT_ID=risenone-ai-prototype
# BQ_DATASET_ID=fire_risk_poc
```

---

## 🎯 **Development Workflow**

### **Daily Development Routine**
```bash
# 1. Navigate to project and activate environment
cd /path/to/risen-one-science-research-agent
source venv/bin/activate

# 2. Pull latest changes
git pull origin main

# 3. Start development server (optional)
cd agent
adk web

# 4. Make changes and test
python -c "from dotenv import load_dotenv; load_dotenv(); from data_science.agent import root_agent; print('Agent ready')"
```

### **Git Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name
git push -u origin feature/your-feature-name

# Development cycle
git add .
git commit -m "Add new fire analysis feature"
git push origin feature/your-feature-name

# Merge back to main when ready
```

### **Deployment to Google Cloud**
```bash
# Deploy new agent when features are ready
cd deployment
python deploy.py --create \
  --project_id risenone-ai-prototype \
  --location us-central1 \
  --bucket risenone-ai-prototype-adk-staging
```

---

## 🔥 **Fire Analysis Capabilities**

### **Current Data Access**
- **277 Weather Stations** with fire risk data
- **NFDR Calculations** (National Fire Danger Rating System)
- **Weather Observations** (temperature, humidity, wind, precipitation)
- **Fuel Moisture Samples** (dead and live vegetation)
- **Station Metadata** (locations, elevations, aspects)

### **Example Queries You Can Test**
```bash
# Basic data access
"How many weather stations do we have fire data for?"

# Station information
"Show me weather stations in California"

# Fire danger analysis
"What's the fire danger level for station BROWNSBORO?"

# Weather data
"What was the temperature range at weather stations last week?"

# Fuel analysis
"Show me fuel moisture samples from dead vegetation"
```

---

## 📚 **Key Project Resources**

### **Documentation**
- **[TERRY_INTEGRATION_GUIDE.md](./TERRY_INTEGRATION_GUIDE.md)** - Client API usage
- **[DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)** - Detailed technical guide
- **[README.md](./README.md)** - Project overview and data sources

### **Important File Locations**
- **Agent Code**: `agent/data_science/agent.py`
- **Environment Config**: `agent/.env`
- **Deployment Scripts**: `deployment/deploy.py`
- **Fire Data**: `data/fire_data/data/*.csv`

### **Production Resources**
- **Production Agent ID**: `6609146802375491584`
- **Google Cloud Project**: `risenone-ai-prototype`
- **BigQuery Dataset**: `fire_risk_poc`
- **Location**: `us-central1`

---

## 🎉 **Success Checklist**

After completing this guide, you should have:

- [ ] ✅ **Local repository** cloned with correct naming
- [ ] ✅ **Virtual environment** activated (venv in prompt)
- [ ] ✅ **Dependencies installed** (vertexai, absl-py, python-dotenv)
- [ ] ✅ **Agent package** installed in development mode
- [ ] ✅ **Environment configured** (.env file with correct values)
- [ ] ✅ **Google Cloud authenticated** (token generation working)
- [ ] ✅ **Agent development ready** (import test passes)
- [ ] ✅ **Production agent access** (277 weather stations response)
- [ ] ✅ **Local development server** working (optional)

---

## 🆘 **Getting Help**

### **Common Commands Reference**
```bash
# Always run this first when starting development
source venv/bin/activate

# Test agent is working
cd agent && python -c "from dotenv import load_dotenv; load_dotenv(); from data_science.agent import root_agent; print('Agent ready')"

# Test production agent
curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" -H "Content-Type: application/json" -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "How many weather stations do we have fire data for?"}}' "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse"
```

### **Team Support**
- **Technical Issues**: Check troubleshooting section above
- **Access Issues**: Contact team lead for Google Cloud/GitHub permissions
- **Agent Behavior**: Review existing agent code and documentation

---

**🎯 You're now ready to develop advanced fire risk analysis features for the Forest Service! The agent gives you access to real fire data from 277 weather stations across the United States.**

**⚠️ Remember: Always run `source venv/bin/activate` before starting development work!**