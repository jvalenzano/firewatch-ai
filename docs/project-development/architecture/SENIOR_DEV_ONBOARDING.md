# 🔥 RisenOne Fire Risk AI - Senior Developer Onboarding

**Welcome to the team!** This document provides a quick overview of the project and your immediate priorities.

---

## 📋 Project Overview

**Client:** RisenOne Consulting (US Forest Service)  
**Mission:** Build an AI-powered fire risk analysis system to replace manual 3-4 hour assessments with 30-second automated analysis  
**Tech Stack:** Google ADK (Agent Development Kit), BigQuery, Python  
**Current Phase:** 2-Week POC Development (Critical Path Recovery)

### What We've Built
- ✅ **Infrastructure:** Google ADK multi-agent system deployed (Agent ID: `6609146802375491584`)
- ✅ **Data Pipeline:** 277 weather stations in BigQuery (`fire_risk_poc` dataset with 17,386 records)
- ✅ **API Integration:** REST endpoints with ADK streaming responses
- ✅ **Authentication:** Service account setup for secure access

### The Critical Gap
- ❌ **Database Agent Communication:** Agent-to-agent transfers failing (blocking all fire data queries)
- ❌ **Fire Science Engine:** NFDRS calculations not implemented
- ❌ **UI/Advanced Features:** No interactive capabilities beyond API

---

## 🚨 Critical Next Steps (Your Immediate Focus)

### Priority #1: Fix Database Agent Communication (BLOCKER - Day 1-2)
**Problem:** The root_agent → database_agent transfer fails, preventing all fire data access  
**Your Task:**
1. Debug agent transfer logic in `agent/data_science/agent.py`
2. Fix the handoff mechanism between agents
3. Ensure queries like "How many weather stations?" return actual data (277) not generic responses
4. **Success Criteria:** 100% pass rate for fire data queries, sub-30s response times

### Priority #2: Implement NFDRS Fire Science Engine (Days 3-5)
**Problem:** No actual fire calculations exist despite documentation claims  
**Your Task:**
1. Build the NFDRS calculation engine with these components:
   - Dead/Live Fuel Moisture (1-hr, 10-hr, 100-hr, 1000-hr)
   - Spread Component (wind/slope integration)
   - Energy Release Component
   - Burning Index (final fire danger rating)
2. Integrate calculations with real BigQuery data
3. **Success Criteria:** All calculations match Forest Service standards (±2% tolerance)

### Priority #3: Test Suite & Reality Check (Day 6)
**Problem:** Major gap between documentation and actual functionality  
**Your Task:**
1. Implement comprehensive test suite for all fire queries
2. Document actual vs expected results
3. Create clear gap analysis for stakeholder communication
4. **Success Criteria:** All core queries tested, gaps documented

### Priority #4: UI/Advanced Feature Groundwork (Days 7+)
**Problem:** No user interface exists  
**Your Task:**
1. Create Streamlit UI stubs that connect to the agent
2. Display basic fire risk data and calculations
3. Prepare for future advanced features (multi-region analysis, predictions)
4. **Success Criteria:** Basic UI can display agent results

---

## 🛠️ Technical Quick Start

### Environment Setup
```bash
cd /Users/jasonvalenzano/risen-one-science-research-agent
source venv/bin/activate
cd agent
```

### Key Files to Review
- `agent/data_science/agent.py` - Root agent with broken database_agent transfer
- `agent/data_science/sub_agents/bigquery/agent.py` - Database agent that needs fixing
- `.cursor/scratchpad.md` - Detailed project status and plan
- `docs/internal/06-12-2025-standup.md` - Comprehensive status assessment

### Testing Commands
```bash
# Test agent import
python -c "from data_science.agent import root_agent; print('Agent loaded')"

# Test BigQuery direct access
python -c "from google.cloud import bigquery; client = bigquery.Client(project='risenone-ai-prototype'); print('BigQuery connected')"

# Test production agent
curl -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "How many weather stations?"}}' \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse"
```

---

## 📊 Success Metrics

**Week 1 Goals:**
- Fix database agent communication (currently broken)
- Implement core NFDRS calculations
- Pass all basic fire data queries
- Document gaps for stakeholder communication

**POC Success Criteria:**
- Live fire danger calculation in under 30 seconds
- 95% accuracy vs manual Forest Service methods
- Working demo for stakeholder presentation
- Clear path to production implementation

---

## 🤝 Key Contacts

- **Technical Lead:** Jason Valenzano (project architecture, GCP setup)
- **Client:** RisenOne Consulting (Forest Service requirements)
- **Resources:** Full access to Google Cloud project, BigQuery datasets, ADK documentation

---

**🎯 Your Mission:** Get the agent talking to its database again, then rapidly build the fire science engine. The infrastructure is solid - we just need to make it actually analyze fire risk!

**Questions?** Check `.cursor/scratchpad.md` for detailed context or reach out to the team. 