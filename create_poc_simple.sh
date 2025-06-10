#!/bin/bash

# RisenOne Fire Risk AI POC - Simple Issue Creation (No Milestones)
# Usage: ./create_poc_simple.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔥 RisenOne Fire Risk AI POC - Simple Issue Creation${NC}"
echo -e "${GREEN}✅ Authenticated with GitHub Enterprise${NC}"
echo -e "${YELLOW}Creating POC-DA-1 issue...${NC}\n"

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

echo -e "${BLUE}📝 Creating Issue: POC-DA-1 - GCP Environment Setup and API Integration${NC}"

gh issue create \
    --title "POC-DA-1: GCP Environment Setup and API Integration" \
    --body "$ISSUE_BODY_DA1" \
    --label "ADK-Core,development,priority-high"

echo -e "${GREEN}✅ Successfully created POC-DA-1 issue!${NC}\n"
echo -e "${BLUE}🔗 View your issues: gh issue list --label ADK-Core${NC}"
