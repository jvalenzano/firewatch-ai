# 🗄️ BigQuery Dataset Cleanup Guide - RisenOne Fire Risk Agent

**✅ CLEANUP COMPLETED SUCCESSFULLY - January 2025**  
**Status:** Archive - This cleanup has been completed. See `.cursor/scratchpad.md` for execution results.  
**Result:** Single authoritative dataset `fire_risk_poc` with 17,386 records across 5 complete tables.

---

**Project:** RisenOne Fire Risk AI - POC  
**Objective:** Standardize and clean up duplicate BigQuery datasets  
**Priority:** High - Affects agent functionality and data completeness  
**IDE Target:** Cursor with terminal command execution capability

---

## 🎯 **Problem Summary**

### **Current State**
- **Two duplicate datasets** in BigQuery with overlapping but inconsistent data
- **Agent configuration inconsistency** causing incomplete data access
- **Missing tables** preventing full fire analysis capabilities

### **Datasets Identified**
1. **`fire_risk_poc`** - Incomplete (2/5 tables) - Currently used by agent
2. **`poc_fire_data`** - More complete (4/5 tables) - Has additional weather/fuel data

### **Impact**
- Agent can only answer questions about weather stations and NFDR data
- Missing weather summaries and fuel sample analysis capabilities
- Potential client demo limitations due to incomplete dataset

---

## 🔍 **Current Data Inventory**

### **Table Completeness Analysis**
| Table Name | fire_risk_poc | poc_fire_data | Original CSV | Status |
|------------|:-------------:|:-------------:|-------------|---------|
| `station_metadata` | ✅ (01:37 UTC) | ✅ (04:46 UTC) | StationMetaData.csv | Duplicate |
| `nfdr_daily_summary` | ✅ (01:37 UTC) | ✅ (04:46 UTC) | nfdrDailySummary.csv | Duplicate |
| `weather_daily_summary` | ❌ Missing | ✅ (04:46 UTC) | wxDailySummary.csv | Incomplete |
| `fuel_samples` | ❌ Missing | ✅ (04:46 UTC) | fieldSample.csv | Incomplete |
| `site_metadata` | ❌ Missing | ❌ Missing | Site_Metadata.csv | Not uploaded |

### **Agent Configuration**
- **Current Setting:** `BQ_DATASET_ID=fire_risk_poc` (incomplete dataset)
- **Location:** `/Users/jasonvalenzano/risen-one-science-research-agent/agent/.env`
- **Production Agent ID:** `6609146802375491584`

---

## 🎯 **Cleanup Goals**

### **Primary Objectives**
1. **Standardize on single dataset** - Eliminate duplication
2. **Complete data coverage** - All 5 original CSV tables accessible
3. **Maintain agent functionality** - 277 weather stations must continue working
4. **Consistent naming convention** - Follow established project patterns
5. **Clean BigQuery environment** - Remove redundant datasets

### **Success Criteria**
- [ ] Single authoritative dataset with all 5 tables
- [ ] Agent configuration updated and tested
- [ ] All original CSV data accessible via BigQuery
- [ ] Production agent maintains current functionality
- [ ] Enhanced agent capabilities for weather and fuel analysis

---

## 🔧 **Recommended Cleanup Strategy**

### **Phase 1: Data Verification (5 minutes)**
Verify data integrity and completeness before making changes.

```bash
# 1. Check record counts in both datasets
bq query --use_legacy_sql=false "
SELECT 
  'poc_fire_data.nfdr_daily_summary' as table_name,
  COUNT(*) as record_count
FROM \`risenone-ai-prototype.poc_fire_data.nfdr_daily_summary\`
UNION ALL
SELECT 
  'poc_fire_data.station_metadata' as table_name,
  COUNT(*) as record_count  
FROM \`risenone-ai-prototype.poc_fire_data.station_metadata\`
UNION ALL
SELECT 
  'poc_fire_data.weather_daily_summary' as table_name,
  COUNT(*) as record_count
FROM \`risenone-ai-prototype.poc_fire_data.weather_daily_summary\`
UNION ALL
SELECT 
  'poc_fire_data.fuel_samples' as table_name,
  COUNT(*) as record_count  
FROM \`risenone-ai-prototype.poc_fire_data.fuel_samples\`
"

# 2. Compare with fire_risk_poc record counts
bq query --use_legacy_sql=false "
SELECT 
  'fire_risk_poc.nfdr_daily_summary' as table_name,
  COUNT(*) as record_count
FROM \`risenone-ai-prototype.fire_risk_poc.nfdr_daily_summary\`
UNION ALL
SELECT 
  'fire_risk_poc.station_metadata' as table_name,
  COUNT(*) as record_count  
FROM \`risenone-ai-prototype.fire_risk_poc.station_metadata\`
"

# 3. Verify local CSV files are available
ls -la /Users/jasonvalenzano/risen-one-science-research-agent/data/fire_data/data/*.csv
wc -l /Users/jasonvalenzano/risen-one-science-research-agent/data/fire_data/data/*.csv
```

### **Phase 2: Complete Primary Dataset (10 minutes)**
Copy missing tables to fire_risk_poc to make it the complete authoritative dataset.

```bash
# 1. Copy missing tables from poc_fire_data to fire_risk_poc
bq cp risenone-ai-prototype:poc_fire_data.weather_daily_summary risenone-ai-prototype:fire_risk_poc.weather_daily_summary
bq cp risenone-ai-prototype:poc_fire_data.fuel_samples risenone-ai-prototype:fire_risk_poc.fuel_samples

# 2. Upload missing Site_Metadata.csv to complete the dataset
cd /Users/jasonvalenzano/risen-one-science-research-agent/agent
python data_science/utils/create_bq_table.py \
  --csv_file ../data/fire_data/data/Site_Metadata.csv \
  --table_name site_metadata \
  --dataset fire_risk_poc

# 3. Verify all tables now exist in fire_risk_poc
bq ls risenone-ai-prototype:fire_risk_poc
```

### **Phase 3: Test Agent Functionality (5 minutes)**
Ensure agent still works with enhanced dataset.

```bash
# 1. Verify agent configuration is correct
cd /Users/jasonvalenzano/risen-one-science-research-agent/agent
grep -E "(BQ_DATASET_ID|BQ_PROJECT_ID)" .env

# 2. Test agent import with complete dataset
python -c "from dotenv import load_dotenv; load_dotenv(); from data_science.agent import root_agent; print('✅ Agent ready with complete dataset')"

# 3. Test production agent with enhanced capabilities
curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "class_method": "stream_query",
    "input": {
      "user_id": "cleanup_test",
      "message": "How many weather stations do we have data for and what types of data tables are available?"
    }
  }' \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/risenone-ai-prototype/locations/us-central1/reasoningEngines/6609146802375491584:streamQuery?alt=sse"
```

### **Phase 4: Cleanup Duplicate Dataset (2 minutes)**
Remove the duplicate poc_fire_data dataset after verification.

```bash
# 1. Final verification that fire_risk_poc is complete
bq query --use_legacy_sql=false "
SELECT 
  table_name,
  row_count,
  creation_time
FROM \`risenone-ai-prototype.fire_risk_poc.INFORMATION_SCHEMA.TABLES\`
ORDER BY creation_time
"

# 2. Delete duplicate dataset (CAUTION: Irreversible)
bq rm -r -f risenone-ai-prototype:poc_fire_data

# 3. Verify cleanup
bq ls risenone-ai-prototype:poc_fire_data  # Should return "Not found"
```

---

## ⚠️ **Safety Considerations**

### **Before Starting**
- [ ] **Backup verification**: Ensure local CSV files are intact
- [ ] **Agent stability**: Production agent `6609146802375491584` is operational
- [ ] **No active demos**: Confirm no client demonstrations are scheduled

### **Rollback Plan**
If issues arise during cleanup:
1. **Recreate poc_fire_data** from local CSV files using `create_bq_table.py`
2. **Switch agent configuration** back to poc_fire_data temporarily
3. **Investigate and resolve** specific issues before proceeding

### **Validation Steps**
After each phase:
- [ ] **Record counts match** expected values from original CSVs
- [ ] **Agent import test** passes without errors
- [ ] **Production agent** responds correctly to test queries

---

## 📊 **Expected Outcomes**

### **Enhanced Agent Capabilities**
After cleanup, the agent will support:
- **Weather Analysis**: "What was the temperature range at station BROWNSBORO last week?"
- **Fuel Moisture Queries**: "Show me fuel samples with high moisture content"
- **Integrated Fire Risk**: "Correlate weather patterns with fuel moisture for fire danger assessment"
- **Site Management**: "List all observation sites in California with their metadata"

### **Clean Infrastructure**
- **Single authoritative dataset**: `fire_risk_poc` with all 5 tables
- **Consistent naming**: Following established project conventions
- **Complete data coverage**: All original CSV files accessible via BigQuery
- **Reduced confusion**: No duplicate datasets causing configuration issues

---

## 🔍 **Troubleshooting Guide**

### **Common Issues**
- **Permission errors**: Ensure BigQuery Admin role for dataset operations
- **Import failures**: Check CSV file formatting and column name consistency
- **Agent import errors**: Verify virtual environment is activated and dependencies installed

### **Validation Queries**
```bash
# Check total station count (should be 277)
bq query --use_legacy_sql=false "SELECT COUNT(DISTINCT stationId) FROM \`risenone-ai-prototype.fire_risk_poc.nfdr_daily_summary\`"

# Verify all expected tables exist
bq query --use_legacy_sql=false "SELECT table_name FROM \`risenone-ai-prototype.fire_risk_poc.INFORMATION_SCHEMA.TABLES\` ORDER BY table_name"
```

---

## 📋 **Post-Cleanup Tasks**

### **Documentation Updates**
- [ ] Update project README with current dataset structure
- [ ] Revise Terry Integration Guide with enhanced capabilities
- [ ] Document new agent query examples for weather and fuel data

### **Team Communication**
- [ ] Notify team of enhanced agent capabilities
- [ ] Update project board with completed cleanup
- [ ] Schedule demo of new weather and fuel analysis features

---

**Execution Time Estimate:** 20-25 minutes  
**Risk Level:** Low (with proper backups and validation)  
**Impact:** High (significantly enhances agent capabilities)

**Ready for Cursor execution with terminal commands and real-time validation.**