# Project Context: Google ADK Fire Risk Analysis Agent

**IMPORTANT: This project uses Google's Agent Development Kit (google-adk) framework - NOT standard Google Cloud AI services.**

## Key Project Details

### **Framework & Architecture**
- **Agent Framework**: `google-adk` (open-source agentic framework)
- **Purpose**: Specifically chosen for advanced data science agent capabilities
- **Deployment**: Google Cloud Vertex AI Reasoning Engine with custom ADK implementation
- **API Behavior**: Does NOT follow standard Vertex AI API patterns (no direct query/streamQuery)

### **Deployed Agent Information**
- **Agent Name**: RisenOne Fire Risk Analysis Agent v3.2
- **Agent ID**: `999913466485538816`
- **Project**: `risenone-ai-prototype`
- **Location**: `us-central1`
- **Status**: Production-ready, operational
- **Framework**: `google-adk` (critical distinction)

### **Data Infrastructure**
- **Primary Data**: Fire risk analysis with 9,513+ records
- **BigQuery Datasets**: 
  - `fire_risk_poc` (9,513 records)
  - `poc_fire_data`
- **Current Config Issue**: Agent points to `forecasting_sticker_sales` dataset (needs correction)
- **Data Capabilities**: Weather stations, NFDR calculations, fire danger ratings

### **Technical Specifications**
- **Base Models**: Gemini 2.0 Flash (multiple specialized agents)
- **Python Version**: 3.12
- **Deployment Method**: Pickle object + requirements via GCS
- **Service Account**: `agent-client-access@risenone-ai-prototype.iam.gserviceaccount.com`

### **API Integration Notes**
- **Standard Vertex AI commands will NOT work** (e.g., `gcloud ai reasoning-engines` commands fail)
- **Session-based API required** for google-adk framework
- **Custom authentication flow** needed for external integration
- **Terry Integration**: Requires ADK-specific API patterns, not standard REST endpoints

## Common LLM Mistakes to Avoid

❌ **Don't assume standard Google Cloud AI APIs**  
❌ **Don't suggest `gcloud ai` commands** (most won't work with ADK)  
❌ **Don't use generic Vertex AI integration patterns**  
❌ **Don't ignore the google-adk framework requirements**  

✅ **Do recognize this is a custom ADK deployment**  
✅ **Do account for ADK-specific API patterns**  
✅ **Do understand session-based interaction model**  
✅ **Do reference ADK documentation when needed**  

---

**Use this context to avoid confusion about why standard Google Cloud AI approaches don't work with our google-adk based fire risk analysis agent.**
