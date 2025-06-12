# 🔥 RisenOne Fire Risk Analysis Agent - External Client Integration Guide
**For: Terry (External AWS Client Integration)**
**Date: June 11, 2025**
**Status: PRODUCTION READY - EXTERNAL CLIENT ACCESS** ✅

---

## 🎯 **EXTERNAL CLIENT INTEGRATION (NO GCP CLI REQUIRED)**

### **📦 INTEGRATION PACKAGE PROVIDED**
- **Service Account Credentials:** `client-access-key.json` (provided securely)
- **Agent ID:** `6609146802375491584` (verified operational)
- **Fire Data Access:** 278 weather stations with comprehensive fire risk data (17,386 total records)
- **API Type:** Standard REST API (works from any cloud environment)

---

## 🔑 **AUTHENTICATION (Service Account)**

### **📁 Service Account File Structure**
```json
{
  "type": "service_account",
  "project_id": "risenone-ai-prototype",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "agent-client-access@risenone-ai-prototype.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### **🐍 Python Token Generation (AWS Compatible)**
```python
import json
import time
import jwt
import requests
from datetime import datetime, timedelta

def generate_access_token(service_account_file):
    """Generate access token from service account JSON (no gcloud CLI required)"""

    # Load service account credentials
    with open(service_account_file, 'r') as f:
        credentials = json.load(f)

    # JWT payload for Google OAuth2
    now = int(time.time())
    payload = {
        'iss': credentials['client_email'],
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'aud': 'https://oauth2.googleapis.com/token',
        'iat': now,
        'exp': now + 3600  # 1 hour expiration
    }

    # Sign JWT with private key
    private_key = credentials['private_key']
    assertion = jwt.encode(payload, private_key, algorithm='RS256')

    # Exchange JWT for access token
    token_request = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': assertion
    }

    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data=token_request,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise Exception(f"Token generation failed: {response.text}")

# Usage example
token = generate_access_token('client-access-key.json')
print(f"Access Token: {token[:50]}...")
```

### **🟢 Node.js Token Generation (AWS Compatible)**
```javascript
const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

async function generateAccessToken(serviceAccountFile) {
    // Load service account credentials
    const credentials = JSON.parse(fs.readFileSync(serviceAccountFile, 'utf8'));

    // JWT payload for Google OAuth2
    const now = Math.floor(Date.now() / 1000);
    const payload = {
        iss: credentials.client_email,
        scope: 'https://www.googleapis.com/auth/cloud-platform',
        aud: 'https://oauth2.googleapis.com/token',
        iat: now,
        exp: now + 3600  // 1 hour expiration
    };

    // Sign JWT with private key
    const assertion = jwt.sign(payload, credentials.private_key, { algorithm: 'RS256' });

    // Exchange JWT for access token
    try {
        const response = await axios.post('https://oauth2.googleapis.com/token',
            `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${assertion}`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        return response.data.access_token;
    } catch (error) {
        throw new Error(`Token generation failed: ${error.response?.data || error.message}`);
    }
}

// Usage example
generateAccessToken('client-access-key.json')
    .then(token => console.log(`Access Token: ${token.substring(0, 50)}...`))
    .catch(error => console.error(error));
```

---

## 🔥 **FIRE RISK AGENT API INTEGRATION**

### **✅ VERIFIED WORKING ENDPOINT**
```
POST https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse
```

### **🐍 Complete Python Integration Example**
```python
import json
import requests
import time
import jwt

class RisenOneFireRiskClient:
    def __init__(self, service_account_file):
        self.service_account_file = service_account_file
        self.agent_id = "6609146802375491584"
        self.base_url = "https://us-central1-aiplatform.googleapis.com/v1"
        self.access_token = None
        self.token_expires = 0

    def _generate_access_token(self):
        """Generate fresh access token from service account"""
        with open(self.service_account_file, 'r') as f:
            credentials = json.load(f)

        now = int(time.time())
        payload = {
            'iss': credentials['client_email'],
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'aud': 'https://oauth2.googleapis.com/token',
            'iat': now,
            'exp': now + 3600
        }

        assertion = jwt.encode(payload, credentials['private_key'], algorithm='RS256')

        token_request = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': assertion
        }

        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_request,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expires = now + 3500  # Refresh 5 minutes early
            return self.access_token
        else:
            raise Exception(f"Token generation failed: {response.text}")

    def _get_valid_token(self):
        """Get valid access token, refreshing if needed"""
        if not self.access_token or time.time() >= self.token_expires:
            self._generate_access_token()
        return self.access_token

    def query_fire_data(self, user_id, message, session_id=None):
        """Query the fire risk analysis agent"""
        token = self._get_valid_token()

        url = f"{self.base_url}/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/{self.agent_id}:streamQuery"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "class_method": "stream_query",
            "input": {
                "user_id": user_id,
                "message": message
            }
        }

        if session_id:
            payload["input"]["session_id"] = session_id

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            params={'alt': 'sse'},
            stream=True,
            timeout=60
        )

        if response.status_code == 200:
            return self._parse_streaming_response(response)
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    def _parse_streaming_response(self, response):
        """Parse streaming SSE response"""
        results = []
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    results.append(data)
                except json.JSONDecodeError:
                    continue
        return results

# Usage Example
if __name__ == "__main__":
    # Initialize client with service account
    client = RisenOneFireRiskClient('client-access-key.json')

    # Query fire data
    try:
        response = client.query_fire_data(
            user_id="terry_aws_client",
            message="How many weather stations have fire data?"
        )

        print("Fire Risk Agent Response:")
        for item in response:
            if 'content' in item:
                print(f"- {item['content']}")

    except Exception as e:
        print(f"Error: {e}")
```

### **🟢 Complete Node.js Integration Example**
```javascript
const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

class RisenOneFireRiskClient {
    constructor(serviceAccountFile) {
        this.serviceAccountFile = serviceAccountFile;
        this.agentId = "6609146802375491584";
        this.baseUrl = "https://us-central1-aiplatform.googleapis.com/v1";
        this.accessToken = null;
        this.tokenExpires = 0;
    }

    async _generateAccessToken() {
        const credentials = JSON.parse(fs.readFileSync(this.serviceAccountFile, 'utf8'));

        const now = Math.floor(Date.now() / 1000);
        const payload = {
            iss: credentials.client_email,
            scope: 'https://www.googleapis.com/auth/cloud-platform',
            aud: 'https://oauth2.googleapis.com/token',
            iat: now,
            exp: now + 3600
        };

        const assertion = jwt.sign(payload, credentials.private_key, { algorithm: 'RS256' });

        try {
            const response = await axios.post('https://oauth2.googleapis.com/token',
                `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${assertion}`,
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
            );

            this.accessToken = response.data.access_token;
            this.tokenExpires = now + 3500; // Refresh 5 minutes early
            return this.accessToken;
        } catch (error) {
            throw new Error(`Token generation failed: ${error.response?.data || error.message}`);
        }
    }

    async _getValidToken() {
        const now = Math.floor(Date.now() / 1000);
        if (!this.accessToken || now >= this.tokenExpires) {
            await this._generateAccessToken();
        }
        return this.accessToken;
    }

    async queryFireData(userId, message, sessionId = null) {
        const token = await this._getValidToken();

        const url = `${this.baseUrl}/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/${this.agentId}:streamQuery`;

        const payload = {
            class_method: "stream_query",
            input: {
                user_id: userId,
                message: message
            }
        };

        if (sessionId) {
            payload.input.session_id = sessionId;
        }

        try {
            const response = await axios.post(url, payload, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                params: { alt: 'sse' },
                timeout: 60000,
                responseType: 'stream'
            });

            return this._parseStreamingResponse(response.data);
        } catch (error) {
            throw new Error(`API request failed: ${error.response?.status} - ${error.response?.data || error.message}`);
        }
    }

    _parseStreamingResponse(stream) {
        return new Promise((resolve, reject) => {
            const results = [];
            let buffer = '';

            stream.on('data', chunk => {
                buffer += chunk.toString();
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            results.push(data);
                        } catch (e) {
                            // Skip invalid JSON
                        }
                    }
                }
            });

            stream.on('end', () => resolve(results));
            stream.on('error', reject);
        });
    }
}

// Usage Example
async function main() {
    const client = new RisenOneFireRiskClient('client-access-key.json');

    try {
        const response = await client.queryFireData(
            "terry_aws_client",
            "How many weather stations have fire data?"
        );

        console.log("Fire Risk Agent Response:");
        response.forEach(item => {
            if (item.content) {
                console.log(`- ${JSON.stringify(item.content)}`);
            }
        });
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}

main();
```

---

## 🔥 **FIRE DATA CAPABILITIES**
- **Weather Stations:** 278 stations with comprehensive fire risk data
- **NFDR Calculations:** 9,235 fire danger ratings and burning index values
- **Weather Observations:** 3,866 temperature, humidity, wind, precipitation records
- **Fuel Moisture Measurements:** 2,442 live and dead fuel moisture content samples
- **Site Metadata:** 1,565 observation site details and location information
- **Total Fire Records:** 17,386 accessible for comprehensive analysis
- **Geographic Analysis:** Station-based fire danger mapping across regions

---

## 📋 **EXTERNAL CLIENT INTEGRATION CHECKLIST**
- [ ] Service account JSON file saved securely (`client-access-key.json`)
- [ ] Python/Node.js JWT library installed (`pip install pyjwt` or `npm install jsonwebtoken`)
- [ ] Token generation function implemented
- [ ] Agent ID configured: `6609146802375491584`
- [ ] API endpoint tested with sample queries
- [ ] Error handling implemented for token refresh
- [ ] Streaming response parsing working

---

## 🔧 **SAMPLE FIRE ANALYSIS QUERIES**
```python
# Weather station count
response = client.query_fire_data("user123", "How many weather stations have fire data?")

# Fire risk analysis by station
response = client.query_fire_data("user123", "What's the fire danger level for station BROWNSBORO?")

# Regional fire analysis
response = client.query_fire_data("user123", "Show me fire risk data for California stations")

# NFDR calculations
response = client.query_fire_data("user123", "What are the burning index values for recent observations?")

# Fuel moisture analysis
response = client.query_fire_data("user123", "Show me fuel moisture measurements for the last week")
```

---

## ⚠️ **IMPORTANT NOTES FOR EXTERNAL INTEGRATION**

### **🔐 Security**
- **Store service account JSON securely** (AWS Secrets Manager recommended)
- **Never commit credentials** to version control
- **Rotate tokens regularly** (automatically handled by client libraries)
- **Use HTTPS only** for all API communications

### **🔄 Token Management**
- **Access tokens expire in 1 hour** - implement automatic refresh
- **Client libraries handle refresh automatically**
- **Monitor for 401 responses** and retry with fresh token

### **📊 Response Format**
- **Streaming JSON responses** via Server-Sent Events (SSE)
- **Multi-agent transfers** appear in response metadata
- **Fire data results** in `state_delta` sections
- **Parse incrementally** for real-time updates

### **🚨 Error Handling**
- **Implement retry logic** for network failures
- **Handle authentication errors** with token refresh
- **Timeout management** (60-second default recommended)
- **Log API responses** for debugging

---

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Common Issues:**
1. **Authentication Failures:** Verify service account JSON format and permissions
2. **Token Expiration:** Implement automatic token refresh (handled in examples)
3. **Network Timeouts:** Increase timeout values for complex fire queries
4. **Parsing Errors:** Handle malformed JSON in streaming responses gracefully

### **Testing from AWS:**
```bash
# Test token generation (no gcloud CLI required)
python3 -c "from fire_client import generate_access_token; print(generate_access_token('client-access-key.json')[:50])"

# Test API connectivity
curl -X POST "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "How many weather stations?"}}'
```

---

**✅ PRODUCTION READY FOR EXTERNAL CLIENT INTEGRATION**
- **Zero GCP CLI dependencies** ✅
- **Service account authentication** ✅
- **AWS/Cloud-agnostic integration** ✅
- **Complete code examples provided** ✅
- **278 weather stations accessible (17,386 total records)** ✅
