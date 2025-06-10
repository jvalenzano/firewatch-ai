#!/bin/bash

# Create POC-DA-2 if missing
echo "📝 Creating POC-DA-2: Geographic Data Foundation and RAWS Station Mapping"

gh issue create \
    --title "POC-DA-2: Geographic Data Foundation and RAWS Station Mapping" \
    --body "## 🎯 Objective
Set up geographic boundaries and weather station locations for Zone 7

## 📋 Tasks
- [ ] Source Forest Service Zone 7 boundary data (GeoJSON format)
- [ ] Identify and map RAWS station locations within demonstration area
- [ ] Create static coordinate files for weather station mapping
- [ ] Test geographic data visualization capabilities
- [ ] Validate boundary accuracy for demonstration region

## ✅ Acceptance Criteria
- ✅ Zone 7 geographic boundaries loaded and display correctly
- ✅ RAWS station coordinates mapped and accessible
- ✅ Geographic data ready for map visualization integration

## 📊 Success Metrics
- Geographic data loads in < 2 seconds
- All RAWS stations within Zone 7 boundaries
- Data format validated for frontend integration" \
    --label "ADK-Core,geospatial,development"

echo "✅ POC-DA-2 created successfully"
