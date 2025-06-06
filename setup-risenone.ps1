# setup-risenone.ps1 - Windows PowerShell setup for RisenOne Fire Analysis Agent
# Usage: .\setup-risenone.ps1

param(
    [switch]$SkipAuth,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 RisenOne Fire Analysis Agent Setup Starting..." -ForegroundColor Blue
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

# Step 0: Environment Validation
Write-Step "Step 0: Validating Environment..."

# Check if we're in the correct repository structure
if (!(Test-Path "agent") -or !(Test-Path "setup-risenone.ps1")) {
    Write-Error "Not in risenone-fire-analysis-agent root directory"
    Write-Error "Expected structure:"
    Write-Host "  risenone-fire-analysis-agent\"
    Write-Host "  ├── agent\"
    Write-Host "  ├── setup-risenone.sh"
    Write-Host "  └── setup-risenone.ps1"
    exit 1
}

# Check agent directory structure
if (!(Test-Path "agent\pyproject.toml") -or !(Test-Path "agent\data_science")) {
    Write-Error "Missing agent\pyproject.toml or agent\data_science\ folder"
    Write-Error "Expected agent directory structure:"
    Write-Host "  agent\"
    Write-Host "  ├── pyproject.toml"
    Write-Host "  ├── data_science\"
    Write-Host "  └── .env (or .env-example)"
    exit 1
}

Write-Success "Environment validation passed"

# Step 1: Prerequisites Check
Write-Step "Step 1: Checking Prerequisites..."

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

# Check Python versions available
Write-Host "Available Python versions:"
$pythonCommands = @("python3.12", "python3.13", "python3", "python")
foreach ($pyCmd in $pythonCommands) {
    try {
        $version = & $pyCmd --version 2>&1
        Write-Host "  Found: $pyCmd -> $version"
    } catch {
        # Command not found, skip silently
    }
}

Write-Success "Prerequisites check passed"

# Step 2: Poetry Environment Setup
Write-Step "Step 2: Setting up Poetry Environment..."

# Change to agent directory for all Poetry operations
Set-Location agent

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
        try {
            $pythonVersion = python --version
            Write-Warning "Using system Python: $pythonVersion"
            poetry env use python
        } catch {
            Write-Error "No compatible Python found"
            exit 1
        }
    }
}

# Install dependencies
Write-Host "Installing dependencies (this may take a few minutes)..."
poetry install

# Get virtual environment path
$venvPath = poetry env info --path
Write-Success "Virtual environment: $venvPath"

# Create activation helper in root directory
Set-Location ..
Write-Host "Creating environment activation helper..."
$activateScript = @"
# Auto-generated environment activation script for PowerShell
`$env:POETRY_VENV_PATH = "$venvPath"
& "$venvPath\Scripts\Activate.ps1"
Write-Host "🐍 RisenOne environment activated" -ForegroundColor Green
Write-Host "Python: `$(Get-Command python | Select-Object -ExpandProperty Source)"
Write-Host "Version: `$(python --version)"
Write-Host ""
Write-Host "To launch agent: cd agent; adk web"
"@

$activateScript | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
Write-Success "Poetry environment configured"

# Step 3: Environment Configuration
Write-Step "Step 3: Checking Environment Configuration..."

# Check .env file in agent directory
if (!(Test-Path "agent\.env")) {
    Write-Warning "agent\.env file not found"
    if (Test-Path "agent\.env-example") {
        Write-Host "Creating agent\.env from agent\.env-example..."
        Copy-Item "agent\.env-example" "agent\.env"
        Write-Warning "Please edit agent\.env file with your configuration"
    } else {
        Write-Error "No agent\.env or agent\.env-example file found"
        exit 1
    }
}

# Verify key environment variables
$envContent = Get-Content "agent\.env" -Raw
if ($envContent -notmatch "GOOGLE_CLOUD_PROJECT") {
    Write-Warning "GOOGLE_CLOUD_PROJECT not found in agent\.env"
}

if ($envContent -notmatch "GOOGLE_GENAI_USE_VERTEXAI.*1") {
    Write-Warning "Verify GOOGLE_GENAI_USE_VERTEXAI=1 in agent\.env"
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

    # Set quota project from .env file
    $projectMatch = Select-String -Path "agent\.env" -Pattern "GOOGLE_CLOUD_PROJECT\s*=\s*(.+)" 
    if ($projectMatch) {
        $projectId = $projectMatch.Matches[0].Groups[1].Value.Trim().Trim('"').Trim("'")
        Write-Host "Setting quota project to: $projectId"
        gcloud auth application-default set-quota-project $projectId
    } else {
        Write-Warning "Could not determine project ID from agent\.env"
    }

    # Verify authentication
    Write-Host "Verifying authentication..."
    try {
        $accessToken = gcloud auth application-default print-access-token
        if ($accessToken) {
            Write-Success "Authentication successful"
            Write-Host "Token: $($accessToken.Substring(0, 50))..."
        } else {
            Write-Error "Authentication failed"
            exit 1
        }
    } catch {
        Write-Error "Authentication verification failed"
        exit 1
    }
} else {
    Write-Warning "Skipping authentication (-SkipAuth specified)"
}

# Step 5: Final Setup and Testing
Write-Step "Step 5: Final Setup and Testing..."

# Activate environment for testing
& "$venvPath\Scripts\Activate.ps1"
Set-Location agent

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

# Create quick test script in root
Set-Location ..
$testScript = @'
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
'@

$testScript | Out-File -FilePath "test_agent.py" -Encoding UTF8

# Create quick start guide
$quickStartContent = @"
# RisenOne Fire Analysis Agent - Quick Start

## Activate Environment
``````powershell
.\activate_env.ps1
``````

## Launch Agent
``````powershell
cd agent
adk web
# Visit: http://localhost:8000
``````

## Test Queries for Fire Analysis
- "Hi, What fire analysis capabilities do you have?"
- "What's the fire risk for Zone 7 tomorrow?"
- "Show me weather data for northern Montana"
- "Calculate fire danger index for current conditions"

## Project Structure
``````
risenone-fire-analysis-agent\
├── agent\                  # Main agent code
│   ├── data_science\      # Agent implementation
│   ├── pyproject.toml     # Dependencies
│   └── .env              # Configuration
├── activate_env.ps1       # Environment activation
├── test_agent.py         # Quick testing
└── QUICK_START.md        # This file
``````

## Development Workflow
1. **Start session**: ``.\activate_env.ps1``
2. **Work in agent dir**: ``cd agent``
3. **Launch for testing**: ``adk web``
4. **Deploy changes**: Follow ADK deployment docs

## Troubleshooting
- Re-run setup: ``.\setup-risenone.ps1``
- Check logs when running ``adk web``
- Verify agent\.env configuration
- Test imports: ``python -c "import google.adk"``

## Next Steps
- Configure your specific fire data sources in agent\.env
- Customize fire analysis models in agent\data_science\
- Add your BigQuery datasets and tables
- Deploy to production GCP environment
"@

$quickStartContent | Out-File -FilePath "QUICK_START.md" -Encoding UTF8

Write-Success "Setup completed successfully!"

Write-Host ""
Write-Host "🎉 RisenOne Fire Analysis Agent Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Activate environment: .\activate_env.ps1"
Write-Host "2. Change to agent directory: cd agent"
Write-Host "3. Launch agent: adk web"
Write-Host "4. Visit: http://localhost:8000"
Write-Host "5. Test query: 'Hi, What fire analysis capabilities do you have?'"
Write-Host ""
Write-Host "📋 Quick test: python test_agent.py"
Write-Host "📖 Documentation: QUICK_START.md"
Write-Host ""
Write-Host "🔥 Ready for fire analysis development!" -ForegroundColor Green