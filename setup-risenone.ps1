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
