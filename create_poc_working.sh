#!/bin/bash

# RisenOne Fire Risk AI POC - Working Issue Creation
# Usage: ./create_poc_working.sh

echo "🔥 Creating POC-DA-1 issue..."

# Create issue with simpler body formatting
gh issue create \
    --title "POC-DA-1: GCP Environment Setup and API Integration" \
    --body "## 🎯 Objective
Establish GCP project foundation and Weather.gov API integration

## 📋 Tasks
- [ ] Create GCP project \`risenone-fire-risk-poc\`
- [ ] Enable APIs: Vertex AI, Cloud Run, Cloud Storage, BigQuery
- [ ] Configure billing with \$200 limit and IAM roles
- [ ] Implement Weather.gov API integration with 30-min refresh
- [ ] Test API calls for Zone 7 (Montana/Idaho) current conditions and forecasts
- [ ] Create error handling for API downtime scenarios

## ✅ Acceptance Criteria
- ✅ Live Weather.gov API connection retrieving data every 30 minutes
- ✅ GCP environment operational with proper permissions
- ✅ Current conditions available for 5+ Zone 7 stations

## 📊 Success Metrics
- API response time < 5 seconds
- 99% API call success rate
- All required GCP services accessible" \
    --label "ADK-Core,development,priority-high"

echo "✅ POC-DA-1 issue created!"
echo "🔗 View issues: gh issue list --label ADK-Core"
