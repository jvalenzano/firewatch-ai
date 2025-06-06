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

# Step 1: Verify Prerequisites
print_step "Step 1: Checking Prerequisites..."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "data_science" ]]; then
    print_error "Must run from the data-science directory"
    echo "Expected path: risenone-ai-prototype/adk-samples/python/agents/data-science"
    exit 1
fi

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

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.12"
if [[ $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) -eq 0 ]]; then
    print_warning "Python $PYTHON_VERSION found. Recommended: Python $REQUIRED_VERSION+"
    echo "Attempting to use Poetry's Python management..."
fi

print_success "Prerequisites check passed"

# Step 2: Poetry Environment Setup
print_step "Step 2: Setting up Poetry Environment..."

# Ensure we use Python 3.12+ if available
if command -v python3.12 &> /dev/null; then
    poetry env use python3.12
    print_success "Using Python 3.12"
elif command -v python3.13 &> /dev/null; then
    poetry env use python3.13
    print_success "Using Python 3.13"
else
    print_warning "Using system Python $PYTHON_VERSION"
    poetry env use python3
fi

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
poetry install

# Get virtual environment path
VENV_PATH=$(poetry env info --path)
print_success "Virtual environment: $VENV_PATH"

# Create activation helper
echo "Creating environment activation helper..."
cat > activate_env.sh << EOF
#!/bin/bash
# Auto-generated environment activation script
export POETRY_VENV_PATH="$VENV_PATH"
source "$VENV_PATH/bin/activate"
echo "🐍 RisenOne environment activated"
echo "Python: \$(which python)"
echo "Version: \$(python --version)"
EOF
chmod +x activate_env.sh

print_success "Poetry environment configured"

# Step 3: Environment Configuration
print_step "Step 3: Checking Environment Configuration..."

# Check .env file
if [[ ! -f ".env" ]]; then
    print_warning ".env file not found"
    if [[ -f ".env-example" ]]; then
        echo "Creating .env from .env-example..."
        cp .env-example .env
        print_warning "Please edit .env file with your configuration"
    else
        print_error "No .env or .env-example file found"
        exit 1
    fi
fi

# Verify key environment variables
if ! grep -q "GOOGLE_CLOUD_PROJECT.*risenone-ai-prototype" .env; then
    print_warning "Verify GOOGLE_CLOUD_PROJECT in .env file"
fi

if ! grep -q "GOOGLE_GENAI_USE_VERTEXAI.*1" .env; then
    print_warning "Verify GOOGLE_GENAI_USE_VERTEXAI=1 in .env file"
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

    # Set quota project
    echo "Setting quota project..."
    gcloud auth application-default set-quota-project risenone-ai-prototype

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

# Create quick test script
cat > test_agent.py << 'EOF'
#!/usr/bin/env python3
"""Quick test script for RisenOne agent"""
import subprocess
import sys

def test_agent():
    print("🧪 Testing RisenOne Agent...")
    
    # Test ADK web launch (background)
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

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
EOF

chmod +x test_agent.py

# Create quick start guide
cat > QUICK_START.md << 'EOF'
# RisenOne Quick Start

## Activate Environment
```bash
source activate_env.sh
```

## Launch Agent
```bash
adk web
# Visit: http://localhost:8000
```

## Test Queries
- "Hi, What data do you have access to?"
- "Show me sales by country"
- "Yes" (when asked about transferring to database agent)

## Deploy to Production
```bash
cd deployment/
python deploy.py --create
```

## Troubleshooting
- Re-run setup: `./setup-risenone.sh`
- Check logs when running `adk web`
- Verify .env configuration
EOF

print_success "Setup completed successfully!"

echo ""
echo "🎉 RisenOne AI Agent Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Activate environment: source activate_env.sh"
echo "2. Launch agent: adk web"
echo "3. Visit: http://localhost:8000"
echo "4. Test query: 'Hi, What data do you have access to?'"
echo ""
echo "📋 Quick test: python test_agent.py"
echo "📖 Documentation: QUICK_START.md"
echo ""
echo "Happy coding! 🚀"

# PowerShell version for Windows
cat > setup-risenone.ps1 << 'PSEOF'
# setup-risenone.ps1 - Windows PowerShell setup for RisenOne AI Agent
# Usage: .\setup-risenone.ps1

param(
    [switch]$SkipAuth,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 RisenOne AI Agent Setup Starting..." -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue

function Write-Step($message) {
    Write-Host "📋 $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

# Step 1: Verify Prerequisites
Write-Step "Step 1: Checking Prerequisites..."

# Check if we're in the right directory
if (!(Test-Path "pyproject.toml") -or !(Test-Path "data_science")) {
    Write-Error "Must run from the data-science directory"
    Write-Host "Expected path: risenone-ai-prototype\adk-samples\python\agents\data-science"
    exit 1
}

# Check Poetry
try {
    $poetryVersion = poetry --version
    Write-Success "Poetry found: $poetryVersion"
} catch {
    Write-Error "Poetry not found. Install from: https://python-poetry.org/docs/"
    Write-Host "Quick install: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    exit 1
}

# Check gcloud
try {
    $gcloudVersion = gcloud --version | Select-Object -First 1
    Write-Success "Google Cloud CLI found: $gcloudVersion"
} catch {
    Write-Error "Google Cloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

Write-Success "Prerequisites check passed"

# Step 2: Poetry Environment Setup
Write-Step "Step 2: Setting up Poetry Environment..."

# Try to use Python 3.12+ if available
try {
    python3.12 --version | Out-Null
    poetry env use python3.12
    Write-Success "Using Python 3.12"
} catch {
    try {
        python3.13 --version | Out-Null
        poetry env use python3.13
        Write-Success "Using Python 3.13"
    } catch {
        Write-Warning "Using system Python"
        poetry env use python
    }
}

# Install dependencies
Write-Host "Installing dependencies (this may take a few minutes)..."
poetry install

# Get virtual environment path
$venvPath = poetry env info --path
Write-Success "Virtual environment: $venvPath"

# Create activation helper
$activateScript = @"
# Auto-generated environment activation script for PowerShell
`$env:POETRY_VENV_PATH = "$venvPath"
& "$venvPath\Scripts\Activate.ps1"
Write-Host "🐍 RisenOne environment activated" -ForegroundColor Green
Write-Host "Python: `$(Get-Command python | Select-Object -ExpandProperty Source)"
Write-Host "Version: `$(python --version)"
"@

$activateScript | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
Write-Success "Poetry environment configured"

# Step 3: Environment Configuration
Write-Step "Step 3: Checking Environment Configuration..."

# Check .env file
if (!(Test-Path ".env")) {
    Write-Warning ".env file not found"
    if (Test-Path ".env-example") {
        Write-Host "Creating .env from .env-example..."
        Copy-Item ".env-example" ".env"
        Write-Warning "Please edit .env file with your configuration"
    } else {
        Write-Error "No .env or .env-example file found"
        exit 1
    }
}

# Verify key environment variables
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "GOOGLE_CLOUD_PROJECT.*risenone-ai-prototype") {
    Write-Warning "Verify GOOGLE_CLOUD_PROJECT in .env file"
}

if ($envContent -notmatch "GOOGLE_GENAI_USE_VERTEXAI.*1") {
    Write-Warning "Verify GOOGLE_GENAI_USE_VERTEXAI=1 in .env file"
}

Write-Success "Environment configuration checked"

# Step 4: Google Cloud Authentication
Write-Step "Step 4: Google Cloud Authentication..."

if (!$SkipAuth) {
    # Clear any stale credentials
    Write-Host "Clearing existing credentials..."
    try { gcloud auth revoke --all 2>$null } catch { }

    # Interactive authentication
    Write-Host "Starting authentication (browser will open)..."
    gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/bigquery

    # Set quota project
    Write-Host "Setting quota project..."
    gcloud auth application-default set-quota-project risenone-ai-prototype

    # Verify authentication
    Write-Host "Verifying authentication..."
    $accessToken = gcloud auth application-default print-access-token
    if ($accessToken) {
        Write-Success "Authentication successful"
        Write-Host "Token: $($accessToken.Substring(0, 50))..."
    } else {
        Write-Error "Authentication failed"
        exit 1
    }
} else {
    Write-Warning "Skipping authentication (-SkipAuth specified)"
}

# Step 5: Final Setup and Testing
Write-Step "Step 5: Final Setup and Testing..."

# Activate environment for testing
& "$venvPath\Scripts\Activate.ps1"

# Test basic imports
Write-Host "Testing Python environment..."
try {
    python -c "import google.adk; print('✅ ADK import successful')"
    python -c "import google.cloud.bigquery; print('✅ BigQuery import successful')"
    Write-Success "Python environment test passed"
} catch {
    Write-Error "Python environment test failed"
    exit 1
}

# Create quick start guide
$quickStartContent = @"
# RisenOne Quick Start

## Activate Environment
```powershell
.\activate_env.ps1
```

## Launch Agent
```powershell
adk web
# Visit: http://localhost:8000
```

## Test Queries
- "Hi, What data do you have access to?"
- "Show me sales by country"
- "Yes" (when asked about transferring to database agent)

## Deploy to Production
```powershell
cd deployment
python deploy.py --create
```

## Troubleshooting
- Re-run setup: .\setup-risenone.ps1
- Check logs when running adk web
- Verify .env configuration
"@

$quickStartContent | Out-File -FilePath "QUICK_START.md" -Encoding UTF8

Write-Success "Setup completed successfully!"

Write-Host ""
Write-Host "🎉 RisenOne AI Agent Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Activate environment: .\activate_env.ps1"
Write-Host "2. Launch agent: adk web"
Write-Host "3. Visit: http://localhost:8000"
Write-Host "4. Test query: 'Hi, What data do you have access to?'"
Write-Host ""
Write-Host "📖 Documentation: QUICK_START.md"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
PSEOF

chmod +x setup-risenone.ps1

echo ""
echo "📦 Setup package created:"
echo "  - setup-risenone.sh (Mac/Linux/WSL)"
echo "  - setup-risenone.ps1 (Windows PowerShell)"
echo "  - activate_env.sh (Environment activation)"
echo "  - test_agent.py (Quick testing)"
echo "  - QUICK_START.md (Documentation)"