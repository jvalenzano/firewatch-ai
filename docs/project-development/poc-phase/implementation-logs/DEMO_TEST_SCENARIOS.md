# 🔥 Fire Risk AI - Demo Test Scenarios

**Test Environment**: ADK Web Interface (http://localhost:8000)
**Agent**: Local development version with NFDRS capabilities
**Objective**: Validate all fire risk functionality before stakeholder demo

## 📋 **Test Scenarios**

### **Scenario 1: Basic Fire Data Query**
**Query**: "How many weather stations do we have fire data for?"
**Expected**: "277 weather stations" or similar count
**Purpose**: Confirm basic database connectivity
**Success Criteria**: Returns accurate station count

### **Scenario 2: Station-Specific Fire Analysis**
**Query**: "What's the fire danger for station BROWNSBORO?"
**Expected**: Station-specific weather data and fire danger assessment
**Purpose**: Test station lookup and fire calculations
**Success Criteria**: Returns weather conditions and burning index data

### **Scenario 3: Recent Fire Conditions**
**Query**: "What are the current fire danger levels? Show me the latest data."
**Expected**: Recent weather station data with fire danger analysis
**Purpose**: Test real-time data access and analysis
**Success Criteria**: Returns recent data with fire danger classifications

### **Scenario 4: Manual Fire Danger Calculation**
**Query**: "Calculate NFDRS fire danger for temperature 85°F, humidity 25%, wind speed 12 mph"
**Expected**: Step-by-step NFDRS calculation with burning index
**Purpose**: Test manual parameter fire danger calculation
**Success Criteria**: Shows NFDRS formula components and final classification

### **Scenario 5: Multi-Station Comparison**
**Query**: "Compare fire danger levels across multiple weather stations"
**Expected**: Analysis of fire conditions at different locations
**Purpose**: Test comparative analysis capability
**Success Criteria**: Shows multiple stations with relative fire danger levels

### **Scenario 6: Fire Science Explanation**
**Query**: "Explain how NFDRS fire danger calculations work"
**Expected**: Educational response about fire science formulas
**Purpose**: Test knowledge of fire science domain
**Success Criteria**: Accurate explanation of NFDRS components

## 📊 **Validation Checklist**

### **Technical Validation**
- [ ] Agent responds within 30 seconds
- [ ] Database queries execute successfully
- [ ] Fire calculations produce reasonable results
- [ ] Station-specific data retrieval works
- [ ] Multi-query sessions maintain context

### **Content Validation**
- [ ] Fire danger classifications are accurate (LOW/MODERATE/HIGH/VERY HIGH/EXTREME)
- [ ] NFDRS formulas mentioned correctly
- [ ] Weather data appears realistic
- [ ] Burning index values within expected ranges (0-999)
- [ ] Professional terminology used appropriately

### **User Experience Validation**
- [ ] Responses are clear and actionable
- [ ] Technical details balanced with usability
- [ ] Natural language interface intuitive
- [ ] Error handling graceful
- [ ] Follow-up questions answered appropriately

## 🎯 **Success Criteria**

**Demo Ready**: All scenarios work smoothly
**Stakeholder Ready**: Responses are professional and accurate
**Production Ready**: No critical issues or failures
**Business Ready**: Clear value demonstration

---

**Use this as your testing guide during the ADK web demo session.** 