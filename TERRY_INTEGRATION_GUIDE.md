# 🔥 RisenOne Fire Risk Analysis Agent - Integration Guide

**For: Terry (Client Integration)**  
**Date: June 11, 2025**  
**Status: PRODUCTION READY** ✅

---

## 🎯 **Quick Start Summary**

Your **Fire Risk Analysis Agent** is deployed and ready for integration! This agent provides AI-powered fire risk analysis with access to 15,821 fire data records including 278 weather stations with NFDR (National Fire Danger Rating) calculations.

### **📋 Key Details**
- **Agent Endpoint:** `999913466485538816`
- **Project:** `risenone-ai-prototype` 
- **Location:** `us-central1`
- **Status:** OPERATIONAL (95% reliability with retry logic)
- **Fire Data:** 278 weather stations, 9,235 NFDR calculations, 15,821 total records

---

## 🔑 **Authentication Setup**

### **Service Account Credentials**
You have been provided with a service account JSON key file:
- **Service Account:** `agent-client-access@risenone-ai-prototype.iam.gserviceaccount.com`
- **Key File:** `agent-client-access-key.json`
- **Scope:** `https://www.googleapis.com/auth/cloud-platform`

### **Setup Instructions**
```bash
# Option 1: Environment Variable (Recommended)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/agent-client-access-key.json"

# Option 2: Direct key loading in code (see examples below)
```

---

## 🌐 **REST API Integration**

### **Primary Endpoint (Streaming)**
```
https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/999913466485538816:streamQuery?alt=sse
```

### **Standard Query Endpoint**
```
https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/999913466485538816:query
```

---

## 💻 **Python Integration Example**

```python
import requests
import json
import time
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class FireRiskAgentClient:
    def __init__(self, service_account_path):
        """Initialize client with service account credentials"""
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.base_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/999913466485538816"
    
    def get_access_token(self):
        """Get fresh access token"""
        self.credentials.refresh(Request())
        return self.credentials.token
    
    def query_fire_risk(self, message, user_id="client", max_retries=3):
        """Query with retry logic for 95% reliability"""
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "class_method": "stream_query",
            "input": {
                "user_id": user_id,
                "message": message
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}:streamQuery?alt=sse",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=60
                )
                
                if response.status_code == 200:
                    full_response = ""
                    for line in response.iter_lines(decode_unicode=True):
                        if line and line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if 'content' in data and 'parts' in data['content']:
                                    for part in data['content']['parts']:
                                        if 'text' in part:
                                            full_response += part['text'] + "\n"
                            except json.JSONDecodeError:
                                continue
                    
                    if full_response.strip() and len(full_response) > 10:
                        return {
                            "success": True,
                            "response": full_response.strip(),
                            "attempt": attempt + 1
                        }
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}

# Usage Example
client = FireRiskAgentClient('agent-client-access-key.json')

# Test fire data access
result = client.query_fire_risk("How many weather stations do we have fire data for?")
print(f"Success: {result['success']}")
print(f"Response: {result.get('response', result.get('error'))}")
```

---

## 🔥 **Fire Data Capabilities**

### **Available Data**
- **Weather Stations:** 278 stations with geographic metadata
- **NFDR Calculations:** 9,235 fire danger assessments
- **Weather Records:** 3,866 weather observations
- **Fuel Samples:** 2,442 fuel moisture measurements
- **Total Records:** 15,821 fire data points

### **Sample Queries**
```python
test_queries = [
    "How many weather stations do we have fire data for?",  # Returns 278
    "What fire analysis capabilities do you have?",
    "Show me fire danger levels",
    "Which stations have extreme fire danger ratings?",
    "What weather data affects fire risk?"
]
```

---

## ⚠️ **Important Notes**

### **Reliability & Best Practices**
- **Success Rate:** 95% with retry logic (3 attempts recommended)
- **Response Time:** 15-30 seconds for fire analysis
- **Timeout:** 60 seconds recommended
- **Always implement retry logic** as shown in examples

### **Expected Behavior**
- Fire data queries consistently return meaningful results
- Station count queries should mention "278 weather stations"
- Complex analysis may require multiple focused queries
- 5% of requests may need retry due to framework limitations

---

## 🧪 **Quick Validation Test**

```python
def validate_integration():
    client = FireRiskAgentClient('agent-client-access-key.json')
    
    # Test fire data access
    result = client.query_fire_risk("How many weather stations do we have fire data for?")
    if result['success'] and '278' in result['response']:
        print("✅ Fire data access: OK (278 stations confirmed)")
        return True
    else:
        print("⚠️ May need retry - implement retry logic")
        return False

# Run validation
if validate_integration():
    print("🎉 Integration ready for production!")
```

---

## 📞 **Support**

### **System Information**
- **Agent Version:** v3.2
- **Resource ID:** 999913466485538816
- **Status:** OPERATIONAL ✅
- **Integration:** PRODUCTION READY

### **Troubleshooting**
1. **Authentication Issues:** Verify service account key file path
2. **Empty Responses:** Implement 3-attempt retry logic (examples provided)
3. **Timeouts:** Use 60+ second timeouts for complex queries

---

## 🎉 **Ready for Production**

Your Fire Risk Analysis Agent provides:
- ✅ **15,821 fire data records** ready for analysis
- ✅ **AI-powered insights** via natural language queries
- ✅ **95% reliability** with retry logic
- ✅ **REST API integration** with authentication
- ✅ **Production stability** with comprehensive fire capabilities

**Start with the Python example above and you'll have robust fire risk analysis integrated into your applications!**

---

*Integration Status: PRODUCTION READY* ✅  
*Last Updated: June 11, 2025* 