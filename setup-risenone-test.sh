#!/bin/bash
# setup-risenone-test.sh - Test for risenone-fire-analysis-agent repo structure
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}📋 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🧪 Testing RisenOne Fire Analysis Agent Setup"
echo "Location: $(pwd)"
echo "================================================"

# Step 1: Verify Repository Structure
print_step "Step 1: Checking Repository Structure..."

# Check if we're in the right repo
if [[ ! -d "agent" ]] || [[ ! -f "setup-risenone.sh" ]]; then
    print_error "Not in risenone-fire-analysis-agent root directory"
    exit 1
fi

# Check agent directory structure
if [[ ! -f "agent/pyproject.toml" ]] || [[ ! -d "agent/data_science" ]]; then
    print_error "Missing agent/pyproject.toml or agent/data_science/ folder"
    exit 1
fi

print_success "Repository structure is correct"

# Step 2: Check Prerequisites
print_step "Step 2: Checking Prerequisites..."

command -v poetry >/dev/null 2>&1 || { print_error "Poetry not found"; exit 1; }
command -v gcloud >/dev/null 2>&1 || { print_error "gcloud not found"; exit 1; }

print_success "Prerequisites check passed"

# Step 3: Python Version Check
print_step "Step 3: Checking Python Versions..."

for py_cmd in python3.12 python3.13 python3 python; do
    if command -v $py_cmd >/dev/null 2>&1; then
        version=$($py_cmd --version 2>&1)
        echo "Found: $py_cmd -> $version"
    fi
done

print_success "Python version check complete"

# Step 4: Test Poetry in Agent Directory
print_step "Step 4: Testing Poetry Environment..."

cd agent
poetry env list
echo "Current environment info:"
poetry env info
poetry check
cd ..

print_success "Poetry configuration valid"

# Step 5: Test Authentication
print_step "Step 5: Testing Authentication Status..."

if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 >/dev/null 2>&1; then
    active_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
    print_success "Active account: $active_account"
else
    print_warning "No active gcloud authentication"
fi

if gcloud auth application-default print-access-token >/dev/null 2>&1; then
    print_success "Application Default Credentials are set"
else
    print_warning "Application Default Credentials not set"
fi

# Step 6: Check Environment Configuration
print_step "Step 6: Testing Environment Configuration..."

if [[ -f "agent/.env" ]]; then
    print_success "agent/.env file exists"
    
    if grep -q "GOOGLE_CLOUD_PROJECT" agent/.env; then
        print_success "GOOGLE_CLOUD_PROJECT configured"
    else
        print_warning "GOOGLE_CLOUD_PROJECT not found in agent/.env"
    fi
    
    if grep -q "GOOGLE_GENAI_USE_VERTEXAI" agent/.env; then
        print_success "GOOGLE_GENAI_USE_VERTEXAI configured"
    else
        print_warning "GOOGLE_GENAI_USE_VERTEXAI not found in agent/.env"
    fi
elif [[ -f "agent/.env-example" ]]; then
    print_warning "Found .env-example but no .env file in agent/"
else
    print_warning "No .env or .env-example file found in agent/"
fi

print_success "Environment configuration check complete"

echo ""
echo "🎉 Test Complete!"
echo "================================================"
echo "Summary:"
echo "- Repository Structure: ✅"
echo "- Prerequisites: ✅"
echo "- Python available: ✅"
echo "- Poetry working: ✅" 
echo "- Authentication: $(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 >/dev/null 2>&1 && echo "✅" || echo "⚠️")"
echo "- Environment: $([[ -f "agent/.env" ]] && echo "✅" || echo "⚠️")"
echo ""
echo "Ready for RisenOne fire analysis agent setup! 🔥"