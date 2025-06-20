## 🧪 **Phase III Validation Testing Script for ADK Web**


### **Pre-Test Setup**
```bash
# Start ADK Web
cd agent
adk web
# Navigate to http://localhost:8000
# Select "data_science" agent
```

# Phase III Manual Validation Testing Plan - RisenOne Fire Risk Agent

**Date:** _______________  
**Tester:** _______________  
**Environment:** ADK Web (http://localhost:8000)  
**Agent ID:** 6609146802375491584  
**Session Recording:** Save JSON after each test suite

---

## 🎯 **Critical Updates Based on Automated Testing**

### ⚠️ **Known Parameter Corrections**
- Use `zone_query` NOT `zone_id` for zone analysis
- Use `analysis_type` NOT `scenario` for financial analysis
- Expect formatted string responses, not JSON

### ✅ **Confirmed Working Features**
- Fire danger calculations with visual gauges
- Station data retrieval (BROWNSBORO confirmed)
- Zone 7 emergency responses
- Financial impact analysis
- Sub-second performance for calculations

---

## 📊 **Updated Metrics Collection Template**

For each test, record:
- **Query Time:** _____ seconds
- **Visual Elements Present:** ASCII Gauge / Emoji / Table / None
- **Classification Shown:** LOW / MODERATE / HIGH / VERY HIGH / EXTREME
- **Response Format:** Formatted Text / Error Message
- **Performance vs Automated:** Faster / Same / Slower

---

## **Test Suite 1: Performance Validation** 🚀

### Test 1.1: Sub-Second Simple Queries
**Query:** `Calculate fire danger for 90°F, 20% humidity, 15 mph wind`
- **Automated Baseline:** 0.000s (near-instant)
- **Expected:** Response in <1 second with visual gauge
- **Manual Response Time:** _______
- **Visual Gauge Present:** Yes / No
- **Classification:** _______

### Test 1.2: Station Data Performance
**Query:** `What's the fire danger at station BROWNSBORO?`
- **Automated Baseline:** 1.459s
- **Expected:** ~1-2 seconds, formatted station card
- **Manual Response Time:** _______
- **Station Card Format:** Yes / No
- **Data Retrieved:** Yes / No

### Test 1.3: Rapid Repeat Query (Cache Test)
**Immediately repeat:** `What's the fire danger at station BROWNSBORO?`
- **Expected:** Faster response due to caching
- **Time Difference:** _______ seconds faster/slower
- **Cache Evidence:** Yes / No / Unclear

---

## **Test Suite 2: Visual Intelligence Verification** 🎨

### Test 2.1: ASCII Gauge Validation
**Query:** `Show fire danger for 85°F, 25% humidity, 12 mph wind`
- **Expected Visual Elements:**
  ```
  🔥 FIRE DANGER ANALYSIS
  
  █████████░░░░░░░░░░░ (visual gauge)
  Classification: MODERATE
  ```
- **ASCII Gauge Present:** Yes / No
- **Emoji Indicators:** 🔴🟠🟡🟢 Present: Yes / No
- **Professional Formatting:** Yes / No

### Test 2.2: Multi-Station Comparison
**Query:** `Compare fire danger at stations BROWNSBORO and BLACK HILLS`
- **Expected:** Side-by-side formatted comparison
- **Comparison Format Clear:** Yes / No
- **Both Stations Shown:** Yes / No
- **Visual Quality (1-10):** _______

---

## **Test Suite 3: Special Features** 🚨

### Test 3.1: Zone 7 Emergency Response
**Query:** `Analyze fire risk for Zone 7`
- **Automated Finding:** Emergency tone triggers correctly
- **Expected:** Dramatic response with 🚨 and EXTREME classification
- **Emergency Formatting:** Yes / No
- **Contains "EXTREME":** Yes / No
- **Evacuation Guidance:** Yes / No

### Test 3.2: Financial Analysis
**Query:** `Analyze financial impact of deployment strategies`
- **Note:** Use "deployment" not "prescribed_burn_vs_suppression"
- **Financial Data Present:** Yes / No
- **Dollar Values Shown:** Yes / No
- **ROI Calculations:** Yes / No

---

## **Test Suite 4: Error Handling** ⚠️

### Test 4.1: Invalid Station Name
**Query:** `What's the fire danger at station INVALID_STATION_XYZ?`
- **Expected:** Graceful error handling
- **Error Message Clear:** Yes / No
- **Suggestions Provided:** Yes / No
- **System Crashed:** Yes / No

### Test 4.2: Extreme Invalid Parameters
**Query:** `Calculate fire danger for -999°F, 150% humidity, -10 mph wind`
- **Expected:** Validation error or adjusted calculation
- **Handled Gracefully:** Yes / No
- **Response Time:** _______

---

## **Test Suite 5: Complex Integration** 🔗

### Test 5.1: Multi-Zone Analysis
**Query:** `Compare fire danger across Zone 7, Zone 8, and Zone 9`
- **Note:** Verify Zone 7 shows emergency formatting
- **All Zones Shown:** Yes / No
- **Zone 7 Different:** Yes / No
- **Response Time:** _______

### Test 5.2: Historical Trend Analysis
**Query:** `Show fire danger trends for BROWNSBORO over the last 7 days`
- **Historical Data Shown:** Yes / No
- **Trend Visualization:** Yes / No
- **Response Time:** _______

---

## **Test Suite 6: Stress Testing** 💪

### Test 6.1: Rapid Fire Calculations
**Action:** Submit these queries in quick succession:
1. `Calculate fire danger for 70°F, 50% humidity, 10 mph wind`
2. `Calculate fire danger for 80°F, 40% humidity, 15 mph wind`
3. `Calculate fire danger for 90°F, 30% humidity, 20 mph wind`
4. `Calculate fire danger for 100°F, 20% humidity, 25 mph wind`
5. `Calculate fire danger for 95°F, 15% humidity, 30 mph wind`

- **All Handled:** Yes / No
- **Any Errors:** Yes / No
- **Average Time:** _______

### Test 6.2: Maximum Complexity Query
**Query:** `Analyze fire risk for all stations in Colorado, predict spread patterns for the next 48 hours, calculate financial impact of different suppression strategies, and recommend optimal crew positioning for Zone 7 emergency response`
- **Handled Successfully:** Yes / No
- **Response Time:** _______
- **All Components Addressed:** Yes / No

---

## **Test Suite 7: Comparison with Automated Results** 📊

### Test 7.1: Baseline Performance Check
Run these exact queries from automated tests:
1. `Calculate fire danger for temperature=85.0, relative_humidity=25.0, wind_speed=15.0`
   - **Automated:** 0.000s
   - **Manual:** _______

2. `Get fire danger for station BROWNSBORO`
   - **Automated:** 1.459s  
   - **Manual:** _______

3. `Analyze Zone 7`
   - **Automated:** 0.000s
   - **Manual:** _______

---

## **Session Summary Checklist**

### Performance Comparison
- [ ] Manual times comparable to automated baseline
- [ ] Visual formatting matches expectations
- [ ] All special features (Zone 7, Financial) working
- [ ] Error handling graceful

### Key Validation Points
- [ ] **String Responses:** Confirmed all responses are formatted text
- [ ] **Parameter Names:** Verified correct parameter usage
- [ ] **Visual Quality:** ASCII gauges and formatting present
- [ ] **Performance:** Sub-second for calculations confirmed

### Critical Success Criteria
1. **Fire calculations <1 second:** Pass / Fail
2. **Visual formatting preserved:** Pass / Fail
3. **Zone 7 emergency active:** Pass / Fail
4. **No system crashes:** Pass / Fail
5. **Station data retrieval <5 seconds:** Pass / Fail

### Final Recommendations
Based on manual testing results:
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Testing Completed By:** _______________  
**Date/Time:** _______________  
**Final Status:** PASS / FAIL / CONDITIONAL PASS

**Comparison Note:** Manual testing _______ (confirmed/revealed issues with/exceeded) automated test results.