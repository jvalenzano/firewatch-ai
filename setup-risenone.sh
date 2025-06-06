#!/bin/bash
# setup-risenone.sh - Cross-platform setup for RisenOne AI Agent
# Compatible with: Mac, Linux, WSL
# Usage: ./setup-risenone.sh

set -e  # Exit on any error

echo "🚀 RisenOne AI Agent Setup Starting..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 0: Environment Validation
print_step "Step 0: Validating Environment..."

# Check if we're in the correct repository structure
if [[ ! -d "agent" ]] || [[ ! -f "setup-risenone.sh" ]]; then
    print_error "Not in risenone-fire-analysis-agent root directory"
    print_error "Expected structure:"
    echo "  risenone-fire-analysis-agent/"
    echo "  ├── agent/"
    echo "  ├── setup-risenone.sh"
    echo "  └── setup-risenone.ps1"
    exit 1
fi

# Check agent directory structure
if [[ ! -f "agent/pyproject.toml" ]] || [[ ! -d "agent/data_science" ]]; then
    print_error "Missing agent/pyproject.toml or agent/data_science/ folder"
    print_error "Expected agent directory structure:"
    echo "  agent/"
    echo "  ├── pyproject.toml"
    echo "  ├── data_science/"
    echo "  └── .env (or .env-example)"
    exit 1
fi

print_success "Environment validation passed"

# Step 1: Prerequisites Check
print_step "Step 1: Checking Prerequisites..."

# Check Poetry
if ! command -v poetry &> /dev/null; then
    print_error "Poetry not found. Install from: https://python-poetry.org/docs/"
    echo "Quick install: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check Python versions available
echo "Available Python versions:"
for py_cmd in python3.12 python3.13 python3 python; do
    if command -v $py_cmd &> /dev/null; then
        version=$($py_cmd --version 2>&1)
        echo "  Found: $py_cmd -> $version"
    fi
done

print_success "Prerequisites check passed"

# Step 2: Poetry Environment Setup
print_step "Step 2: Setting up Poetry Environment..."

# Change to agent directory for all Poetry operations
cd agent

# Ensure we use Python 3.12+ if available
if command -v python3.12 &> /dev/null; then
    poetry env use python3.12
    print_success "Using Python 3.12"
elif command -v python3.13 &> /dev/null; then
    poetry env use python3.13
    print_success "Using Python 3.13"
else
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_warning "Using system Python $PYTHON_VERSION"
    poetry env use python3
fi

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
poetry install

# Get virtual environment path
VENV_PATH=$(poetry env info --path)
print_success "Virtual environment: $VENV_PATH"

# Create activation helper in root directory
cd ..
echo "Creating environment activation helper..."
cat > activate_env.sh << EOF
#!/bin/bash
# Auto-generated environment activation script
export POETRY_VENV_PATH="$VENV_PATH"
source "$VENV_PATH/bin/activate"
echo "🐍 RisenOne environment activated"
echo "Python: \$(which python)"
echo "Version: \$(python --version)"
echo ""
echo "To launch agent: cd agent && adk web"
EOF
chmod +x activate_env.sh

print_success "Poetry environment configured"

# Step 3: Environment Configuration
print_step "Step 3: Checking Environment Configuration..."

# Check .env file in agent directory
if [[ ! -f "agent/.env" ]]; then
    print_warning "agent/.env file not found"
    if [[ -f "agent/.env-example" ]]; then
        echo "Creating agent/.env from agent/.env-example..."
        cp agent/.env-example agent/.env
        print_warning "Please edit agent/.env file with your configuration"
    else
        print_error "No agent/.env or agent/.env-example file found"
        exit 1
    fi
fi

# Verify key environment variables
if ! grep -q "GOOGLE_CLOUD_PROJECT" agent/.env; then
    print_warning "GOOGLE_CLOUD_PROJECT not found in agent/.env"
fi

if ! grep -q "GOOGLE_GENAI_USE_VERTEXAI.*1" agent/.env; then
    print_warning "Verify GOOGLE_GENAI_USE_VERTEXAI=1 in agent/.env"
fi

print_success "Environment configuration checked"

# Step 4: Google Cloud Authentication
print_step "Step 4: Google Cloud Authentication..."

# Clear any stale credentials
echo "Clearing existing credentials..."
gcloud auth revoke --all 2>/dev/null || true

# Check if running in CI/automated environment
if [[ -n "$CI" ]] || [[ -n "$GITHUB_ACTIONS" ]] || [[ -n "$AUTOMATED_SETUP" ]]; then
    print_warning "Automated environment detected. Skipping interactive authentication."
    print_warning "Set up authentication manually with:"
    echo "gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery"
else
    # Interactive authentication
    echo "Starting authentication (browser will open)..."
    gcloud auth application-default login \
        --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery

    # Set quota project from .env file
    PROJECT_ID=$(grep "GOOGLE_CLOUD_PROJECT" agent/.env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [[ -n "$PROJECT_ID" ]]; then
        echo "Setting quota project to: $PROJECT_ID"
        gcloud auth application-default set-quota-project "$PROJECT_ID"
    else
        print_warning "Could not determine project ID from agent/.env"
    fi

    # Verify authentication
    echo "Verifying authentication..."
    ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
    if [[ -n "$ACCESS_TOKEN" ]]; then
        print_success "Authentication successful"
        echo "Token: ${ACCESS_TOKEN:0:50}..."
    else
        print_error "Authentication failed"
        exit 1
    fi
fi

# Step 5: Final Setup and Testing
print_step "Step 5: Final Setup and Testing..."

# Activate environment for testing
source "$VENV_PATH/bin/activate"
cd agent

# Test basic imports
echo "Testing Python environment..."
python -c "import google.adk; print('✅ ADK import successful')" || {
    print_error "ADK import failed"
    exit 1
}

python -c "import google.cloud.bigquery; print('✅ BigQuery import successful')" || {
    print_error "BigQuery import failed"
    exit 1
}

print_success "Python environment test passed"

# Create quick test script in root
cd ..
cat > test_agent.py << 'EOF'
#!/usr/bin/env python3
"""Quick test script for RisenOne agent"""
import subprocess
import sys
import os

def test_agent():
    print("🧪 Testing RisenOne Agent...")
    
    # Change to agent directory
    original_dir = os.getcwd()
    agent_dir = os.path.join(original_dir, 'agent')
    
    if not os.path.exists(agent_dir):
        print("❌ Agent directory not found")
        return False
    
    os.chdir(agent_dir)
    
    try:
        print("Starting ADK web server...")
        process = subprocess.Popen(['adk', 'web'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Give it time to start
        import time
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ ADK web server started successfully")
            print("🌐 Visit: http://localhost:8000")
            print("💬 Test query: 'Hi, What data do you have access to?'")
            
            # Terminate the process
            process.terminate()
            return True
        else:
            print("❌ ADK web server failed to start")
            stdout, stderr = process.communicate()
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
EOF

chmod +x test_agent.py

# Create quick start guide
cat > QUICK_START.md << 'EOF'
# RisenOne Fire Analysis Agent - Quick Start

## Activate Environment
```bash
source activate_env.sh
```

## Launch Agent
```bash
cd agent
adk web
# Visit: http://localhost:8000
```

## Test Queries for Fire Analysis
- "Hi, What fire analysis capabilities do you have?"
- "What's the fire risk for Zone 7 tomorrow?"
- "Show me weather data for northern Montana"
- "Calculate fire danger index for current conditions"

## Project Structure
```
risenone-fire-analysis-agent/
├── agent/                  # Main agent code
│   ├── data_science/      # Agent implementation
│   ├── pyproject.toml     # Dependencies
│   └── .env              # Configuration
├── activate_env.sh        # Environment activation
├── test_agent.py         # Quick testing
└── QUICK_START.md        # This file
```

## Development Workflow
1. **Start session**: `source activate_env.sh`
2. **Work in agent dir**: `cd agent`
3. **Launch for testing**: `adk web`
4. **Deploy changes**: Follow ADK deployment docs

## Troubleshooting
- Re-run setup: `./setup-risenone.sh`
- Check logs when running `adk web`
- Verify agent/.env configuration
- Test imports: `python -c "import google.adk"`

## Next Steps
- Configure your specific fire data sources in agent/.env
- Customize fire analysis models in agent/data_science/
- Add your BigQuery datasets and tables
- Deploy to production GCP environment
EOF

print_success "Setup completed successfully!"

echo ""
echo "🎉 RisenOne Fire Analysis Agent Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Activate environment: source activate_env.sh"
echo "2. Change to agent directory: cd agent"
echo "3. Launch agent: adk web"
echo "4. Visit: http://localhost:8000"
echo "5. Test query: 'Hi, What fire analysis capabilities do you have?'"
echo ""
echo "📋 Quick test: python test_agent.py"
echo "📖 Documentation: QUICK_START.md"
echo ""
echo "🔥 Ready for fire analysis development!"