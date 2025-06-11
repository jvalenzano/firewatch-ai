# 🚨 **CRITICAL DEPLOYMENT ISSUE - TECHNICAL SOLUTION REQUIRED**

## **📊 Executive Summary**

**STATUS**: **RED** - Core functionality blocked by environment variable configuration failure  
**IMPACT**: Terry integration impossible, stakeholder demo at risk  
**TIMELINE**: Immediate resolution required for POC schedule  
**ROOT CAUSE**: Agent Engine runtime not receiving environment variables despite correct deployment setup

---

## **🔍 Technical Analysis**

### **✅ Working Components**
- **Agent Framework**: Deployment, authentication, basic routing functional
- **Data Layer**: 15,821 fire records successfully loaded in BigQuery `poc_fire_data`
- **Infrastructure**: GCP services, service accounts, Cloud Run environment operational
- **Transfer Logic**: Root agent → database_agent handoff working correctly

### **❌ Critical Failure Point**
```
Root Agent → database_agent → tools.get_database_settings() → SILENT FAILURE
```
**Issue**: Environment variables not available in Agent Engine runtime despite correct deployment configuration

---

## **🛠 Immediate Resolution Strategy**

### **Option 1: Hardcode Configuration (Quick Fix - 30 minutes)**

# Emergency Fix: Hardcode database configuration
# Replace get_env_var() calls in database agent

def get_database_settings():
    """Emergency hardcoded configuration for POC"""
    return {
        'project_id': 'risenone-ai-prototype',
        'dataset_id': 'poc_fire_data',
        'location': 'us-central1'
    }

# Modified database agent initialization
def initialize_database_agent():
    """Initialize with hardcoded settings"""
    try:
        config = get_database_settings()
        
        # Initialize BigQuery client with hardcoded project
        from google.cloud import bigquery
        client = bigquery.Client(project=config['project_id'])
        
        # Verify dataset exists
        dataset_ref = client.dataset(config['dataset_id'])
        dataset = client.get_dataset(dataset_ref)
        
        print(f"✅ Database agent connected to {config['dataset_id']}")
        return client, config
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Quick deployment script modification
HARDCODED_CONFIG = {
    'BQ_PROJECT_ID': 'risenone-ai-prototype',
    'BQ_DATASET_ID': 'poc_fire_data',
    'BQ_LOCATION': 'us-central1'
}

# Replace all get_env_var() calls with direct dictionary access
def get_config_value(key):
    return HARDCODED_CONFIG.get(key)

---

### **Option 2: Environment Variable Debugging (Comprehensive Fix - 2 hours)**

# Comprehensive Environment Variable Debugging

import os
import json
from typing import Dict, Any

def debug_environment_variables():
    """Comprehensive environment debugging for Agent Engine"""
    
    debug_info = {
        'timestamp': datetime.now().isoformat(),
        'environment_variables': {},
        'expected_variables': ['BQ_PROJECT_ID', 'BQ_DATASET_ID', 'BQ_LOCATION'],
        'agent_context': {},
        'runtime_info': {}
    }
    
    # 1. Check all environment variables
    debug_info['environment_variables'] = dict(os.environ)
    
    # 2. Check specific fire-related variables
    fire_vars = {}
    for var in debug_info['expected_variables']:
        fire_vars[var] = {
            'value': os.getenv(var),
            'exists': var in os.environ,
            'length': len(os.getenv(var, ''))
        }
    debug_info['fire_variables'] = fire_vars
    
    # 3. Check Agent Engine context
    try:
        # Check if running in Agent Engine
        debug_info['runtime_info'] = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'user': os.getenv('USER', 'unknown'),
            'home': os.getenv('HOME', 'unknown')
        }
    except Exception as e:
        debug_info['runtime_error'] = str(e)
    
    return debug_info

def enhanced_get_env_var(var_name: str, default: str = None, debug: bool = True):
    """Enhanced environment variable getter with comprehensive debugging"""
    
    if debug:
        print(f"🔍 Attempting to get environment variable: {var_name}")
    
    # Method 1: Standard os.getenv
    value = os.getenv(var_name)
    if value:
        if debug:
            print(f"✅ Found via os.getenv: {var_name}={value}")
        return value
    
    # Method 2: Direct os.environ access
    try:
        value = os.environ[var_name]
        if debug:
            print(f"✅ Found via os.environ: {var_name}={value}")
        return value
    except KeyError:
        if debug:
            print(f"❌ Not found in os.environ: {var_name}")
    
    # Method 3: Check with prefix variations
    for prefix in ['', 'GOOGLE_CLOUD_', 'GCP_', 'VERTEX_']:
        prefixed_name = f"{prefix}{var_name}"
        value = os.getenv(prefixed_name)
        if value:
            if debug:
                print(f"✅ Found with prefix: {prefixed_name}={value}")
            return value
    
    # Method 4: Fallback to hardcoded values for POC
    fallback_values = {
        'BQ_PROJECT_ID': 'risenone-ai-prototype',
        'BQ_DATASET_ID': 'poc_fire_data',
        'BQ_LOCATION': 'us-central1'
    }
    
    if var_name in fallback_values:
        if debug:
            print(f"⚠️ Using fallback value: {var_name}={fallback_values[var_name]}")
        return fallback_values[var_name]
    
    if debug:
        print(f"❌ FAILED to find: {var_name}")
        print(f"Available environment variables: {list(os.environ.keys())}")
    
    if default:
        return default
    
    raise EnvironmentError(f"Required environment variable {var_name} not found")

# Enhanced deployment configuration
def deploy_with_debug():
    """Deploy agent with enhanced environment debugging"""
    
    # Pre-deployment environment check
    print("🔍 Pre-deployment environment check:")
    debug_info = debug_environment_variables()
    
    # Export variables explicitly
    os.environ['BQ_PROJECT_ID'] = 'risenone-ai-prototype'
    os.environ['BQ_DATASET_ID'] = 'poc_fire_data'
    os.environ['BQ_LOCATION'] = 'us-central1'
    
    print("✅ Environment variables explicitly set")
    
    # Verify before deployment
    for var in ['BQ_PROJECT_ID', 'BQ_DATASET_ID', 'BQ_LOCATION']:
        value = enhanced_get_env_var(var, debug=True)
        print(f"✅ Verified: {var}={value}")
    
    return debug_info

## **⚡ IMMEDIATE ACTION PLAN**

### **🎯 Phase 1: Emergency Fix (Next 30 Minutes)**

1. **Modify Database Agent Configuration**
   ```bash
   cd /Users/jasonvalenzano/risenone-fire-analysis-agent/deployment
   cp agent_tools.py agent_tools_backup.py  # Backup current version
   ```

2. **Apply Hardcoded Configuration**
   - Replace all `get_env_var()` calls with hardcoded values
   - Target: `poc_fire_data` dataset in `risenone-ai-prototype`
   - Test locally before deployment

3. **Emergency Deployment**
   ```bash
   python deploy.py --create --project_id=risenone-ai-prototype --location=us-central1 --bucket=risenone-ai-prototype-adk-staging
   ```

4. **Immediate Testing**
   ```bash
   curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/[NEW_ID]:streamQuery?alt=sse \
        -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "How many weather stations do we have fire data for?"}}'
   ```

**SUCCESS CRITERIA**: Database agent responds with "278 weather stations"




---

### **🔧 Phase 2: Production-Ready Fix (Next 2 Hours)**

# Production-Ready Environment Variable Solution

## 🎯 Implementation Strategy

### **Step 1: Enhanced Environment Configuration (30 minutes)**

1. **Create environment configuration module**
   ```python
   # config.py
   import os
   from typing import Dict, Optional
   
   class FireRiskConfig:
       def __init__(self):
           self.config = self._load_configuration()
       
       def _load_configuration(self) -> Dict[str, str]:
           """Load configuration with multiple fallback methods"""
           
           # Method 1: Environment variables
           config = {
               'project_id': os.getenv('BQ_PROJECT_ID'),
               'dataset_id': os.getenv('BQ_DATASET_ID'), 
               'location': os.getenv('BQ_LOCATION')
           }
           
           # Method 2: Agent Engine metadata
           if not all(config.values()):
               config.update(self._get_agent_metadata())
           
           # Method 3: Hardcoded fallbacks for POC
           defaults = {
               'project_id': 'risenone-ai-prototype',
               'dataset_id': 'poc_fire_data',
               'location': 'us-central1'
           }
           
           for key, value in defaults.items():
               if not config.get(key):
                   config[key] = value
           
           return config
       
       def get(self, key: str) -> Optional[str]:
           return self.config.get(key)
   ```

2. **Modify agent initialization**
   ```python
   # Initialize with robust configuration
   fire_config = FireRiskConfig()
   
   def get_database_client():
       project_id = fire_config.get('project_id')
       client = bigquery.Client(project=project_id)
       return client, fire_config.config
   ```

### **Step 2: Container Environment Setup (45 minutes)**

1. **Dockerfile modifications**
   ```dockerfile
   # Explicitly set environment variables
   ENV BQ_PROJECT_ID=risenone-ai-prototype
   ENV BQ_DATASET_ID=poc_fire_data
   ENV BQ_LOCATION=us-central1
   
   # Copy configuration
   COPY config.py /app/config.py
   ```

2. **Cloud Run deployment configuration**
   ```yaml
   # cloud-run-config.yaml
   apiVersion: serving.knative.dev/v1
   kind: Service
   spec:
     template:
       metadata:
         annotations:
           run.googleapis.com/execution-environment: gen2
       spec:
         containers:
         - image: gcr.io/risenone-ai-prototype/fire-risk-agent
           env:
           - name: BQ_PROJECT_ID
             value: "risenone-ai-prototype"
           - name: BQ_DATASET_ID  
             value: "poc_fire_data"
           - name: BQ_LOCATION
             value: "us-central1"
   ```

### **Step 3: Agent Engine Integration (30 minutes)**

1. **Enhanced deployment script**
   ```python
   def deploy_with_environment():
       # Set environment variables in multiple locations
       env_vars = {
           'BQ_PROJECT_ID': 'risenone-ai-prototype',
           'BQ_DATASET_ID': 'poc_fire_data', 
           'BQ_LOCATION': 'us-central1'
       }
       
       # Method 1: OS environment
       os.environ.update(env_vars)
       
       # Method 2: Agent configuration
       agent_config = {
           'environment_variables': env_vars,
           'runtime_config': env_vars
       }
       
       # Deploy with explicit configuration
       return deploy_agent(config=agent_config)
   ```

### **Step 4: Comprehensive Testing (15 minutes)**

1. **Multi-level testing approach**
   ```bash
   # Test 1: Environment variable availability
   python -c "import os; print('BQ_DATASET_ID:', os.getenv('BQ_DATASET_ID'))"
   
   # Test 2: Database connectivity
   python -c "from config import FireRiskConfig; print(FireRiskConfig().config)"
   
   # Test 3: Agent functionality
   curl [AGENT_ENDPOINT] -d '{"message": "Test fire data access"}'
   ```

## 🎯 Success Criteria

- ✅ Environment variables accessible in Agent Engine runtime
- ✅ Database agent responds to fire data queries  
- ✅ 278 weather stations query returns successfully
- ✅ Terry integration endpoints functional
- ✅ Production-ready configuration management

## 🚨 Rollback Plan

If production fix fails:
1. Revert to hardcoded configuration
2. Deploy emergency fix agent
3. Continue with POC demonstration
4. Address environment issue post-demo

## 📊 Timeline Impact

- **Emergency Fix**: POC demo ready in 30 minutes
- **Production Fix**: Robust solution in 2 hours
- **Zero impact** on stakeholder demo timeline
- **Full Terry integration** enabled immediately after fix

---

## **🎯 EXECUTIVE DECISION MATRIX**

| Approach | Timeline | Risk | Demo Ready | Production Ready | Effort |
|----------|----------|------|------------|------------------|---------|
| **Hardcode Fix** | 30 min | LOW | ✅ YES | ⚠️ Needs work | LOW |
| **Environment Debug** | 2 hours | MEDIUM | ✅ YES | ✅ YES | MEDIUM |
| **Container Rebuild** | 4 hours | HIGH | ⚠️ Maybe | ✅ YES | HIGH |

---

## **📋 RECOMMENDED EXECUTION SEQUENCE**

### **🚨 IMMEDIATE (Next 30 minutes)**
1. **Execute Emergency Fix** - Apply hardcoded configuration
2. **Deploy & Test** - Validate fire data queries work
3. **Document Working Agent ID** - Provide to Terry for integration testing

### **🔧 SHORT-TERM (Next 2 hours)** 
1. **Implement Production Fix** - Environment variable debugging
2. **Comprehensive Testing** - Multi-scenario validation
3. **Update Terry Documentation** - Production-ready endpoints

### **🎯 VALIDATION COMMANDS**

**Test Fire Data Access:**
```bash
# Expected Response: "There are 278 weather stations with fire data available"
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json" \
     [AGENT_ENDPOINT]:streamQuery?alt=sse \
     -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "How many weather stations do we have fire data for?"}}'
```

**Test NFDR Calculations:**
```bash
# Expected Response: Fire danger calculations with weather correlation
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json" \
     [AGENT_ENDPOINT]:streamQuery?alt=sse \
     -d '{"class_method": "stream_query", "input": {"user_id": "test", "message": "Show me stations with extreme fire danger ratings"}}'
```

---

## **🎯 BOTTOM LINE RECOMMENDATION**

**EXECUTE EMERGENCY FIX IMMEDIATELY** - This is a blocking issue for the entire POC demonstration. The hardcoded configuration approach provides immediate resolution with minimal risk, ensuring Terry integration proceeds and stakeholder demo requirements are met.

**Priority**: Get the POC working NOW, optimize for production AFTER the demo is secured.

refer to `emergency-fix-code.md` file (code modifications) needed for the emergency fix. 