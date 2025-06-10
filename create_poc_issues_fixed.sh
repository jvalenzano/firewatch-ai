#!/bin/bash

# RisenOne Fire Risk AI POC - GitHub Issue Creation Script (Fixed)
# Usage: ./create_poc_issues_fixed.sh
# Prerequisites: GitHub CLI installed and authenticated, run from repo directory

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository check
if ! git remote get-url origin &>/dev/null; then
    echo -e "${RED}Error: Not in a git repository with remote origin${NC}"
    exit 1
fi

# Verify we're in the correct repository
REPO_URL=$(git remote get-url origin)
if [[ ! "$REPO_URL" == *"USDA-AI-Innovation-Hub/risen-one-science-research-agent"* ]]; then
    echo -e "${YELLOW}Warning: You may not be in the risen-one-science-research-agent repository${NC}"
    echo -e "${YELLOW}Current repo: $REPO_URL${NC}"
    echo -e "${YELLOW}Expected: https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent.git${NC}"
fi

# GitHub CLI check
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI not installed. Install with: brew install gh${NC}"
    exit 1
fi

# Authentication check (no hostname needed since already authenticated)
if ! gh auth status &>/dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    exit 1
fi

echo -e "${BLUE}🔥 RisenOne Fire Risk AI POC - GitHub Issue Creation${NC}"
echo -e "${GREEN}✅ Authenticated with GitHub Enterprise${NC}"
echo -e "${YELLOW}Creating milestones and POC issues...${NC}\n"

# Function to create milestones if they don't exist
create_milestone() {
    local title=$1
    local description=$2
    local due_date=$3
    
    if ! gh api repos/:owner/:repo/milestones --jq '.[] | select(.title == "'$title'")' | grep -q .; then
        gh api repos/:owner/:repo/milestones \
            --method POST \
            --field title="$title" \
            --field description="$description" \
            --field due_on="$due_date" > /dev/null
        echo -e "${GREEN}✅ Created milestone: $title${NC}"
    else
        echo -e "${YELLOW}⚠️  Milestone already exists: $title${NC}"
    fi
}

# Function to create issue
create_issue() {
    local issue_number=$1
    local title=$2
    local body=$3
    local labels=$4
    local milestone=$5
    
    echo -e "${BLUE}📝 Creating Issue: $issue_number - $title${NC}"
    
    gh issue create \
        --title "$issue_number: $title" \
        --body "$body" \
        --label "$labels" \
        --milestone "$milestone"
    
    echo -e "${GREEN}✅ Successfully created issue: $issue_number${NC}\n"
}

# Create project milestones (labels already exist)
echo -e "${BLUE}🎯 Creating Project Milestones...${NC}"
create_milestone "Discovery & Architecture" "Foundation planning and system architecture setup" "2025-06-11T23:59:59Z"
create_milestone "Agent Development" "Core AI agent development and implementation" "2025-06-13T23:59:59Z"
create_milestone "Testing & Validation" "System testing and performance validation" "2025-06-18T23:59:59Z"
create_milestone "Governance & Deployment" "Documentation, deployment, and stakeholder demo" "2025-06-20T23:59:59Z"

echo ""

# POC-DA-1: GCP Environment Setup and API Integration
read -r -d '' ISSUE_BODY_DA1 << 'EOF'
## 🎯 Objective
Establish GCP project foundation and Weather.gov API integration

## 📋 Tasks
- [ ] Create GCP project `risenone-fire-risk-poc`
- [ ] Enable APIs: Vertex AI, Cloud Run, Cloud Storage, BigQuery
- [ ] Configure billing with $200 limit and IAM roles
- [ ] Implement Weather.gov API integration with 30-min refresh
- [ ] Test API calls for Zone 7 (Montana/Idaho) current conditions and forecasts
- [ ] Create error handling for API downtime scenarios

## ✅ Acceptance Criteria
- ✅ Live Weather.gov API connection retrieving data every 30 minutes
- ✅ GCP environment operational with proper permissions
- ✅ Current conditions available for 5+ Zone 7 stations

## 🔗 Dependencies
- GCP billing account setup
- Weather.gov API documentation review
- Zone 7 geographic boundary identification

## 📊 Success Metrics
- API response time < 5 seconds
- 99% API call success rate
- All required GCP services accessible

## 📚 Resources
- [Weather.gov API Documentation](https://www.weather.gov/documentation/services-web-api)
- [GCP Vertex AI Setup Guide](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform)
- [Forest Service Zone 7 Boundaries](https://data.fs.usda.gov/geodata/)
EOF

# Create the first issue
create_issue "POC-DA-1" "GCP Environment Setup and API Integration" "$ISSUE_BODY_DA1" "ADK-Core,development,priority-high" "Discovery & Architecture"

echo -e "${GREEN}🎉 First POC issue created successfully!${NC}"
echo -e "${YELLOW}💡 This is the first of 13 POC issues - run the full script to create all${NC}"
echo -e "${BLUE}🔗 View your issues: gh issue list --label ADK-Core${NC}"
