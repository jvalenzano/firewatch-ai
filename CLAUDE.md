# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RisenOne Fire Analysis Agent - a production Google Cloud AI system using the Agent Development Kit (ADK) v1.0.0. Implements a multi-agent architecture for wildfire risk analysis and fire danger calculations for the Forest Service.

**Current Status**: Phase III Complete - Production Ready with Visual Intelligence & Demo Enhancements  
**Performance**: 95.5% station reliability, 0.42s average response time, <1s typical responses  
**Agent Resource ID**: 6609146802375491584 (risenone-ai-prototype)  
**Visual System**: 100% formatting preservation with ASCII gauges and professional layouts  
**Demo Features**: Zone recognition, financial analysis, emergency response templates

## Key Documentation

- **Technical Specification**: `docs/architecture/technical-specification-v3.md` - Complete system architecture with diagrams
- **Architecture Decisions**: `docs/architecture/adr/` - Key design decisions and rationale
- **Test Plan**: `docs/testing/PHASE-III-VALIDATION-TESTING.MD` - Comprehensive validation tests
- **API Documentation**: See agent tools in `data_science/agent.py`

## Development Commands

### Environment Setup
```bash
# Initial setup (one-time)
./setup-risenone.sh        # Mac/Linux
./setup-risenone.ps1       # Windows PowerShell

# Activate environment before work
source activate_env.sh     # Mac/Linux
.\activate_env.ps1         # Windows
cd agent
```

### Quick System Check
```bash
# Test that agent loads without errors
cd agent
python -c "from data_science.agent import agent; print('✅ Agent loaded successfully')"

# Run performance monitoring test
python test_performance_simple.py

# Start ADK Web and test
adk web
# Navigate to http://localhost:8000
# Select "data_science" agent
# Test query: "Calculate fire danger for 90F, 20% humidity, 15mph wind"
```

### Core Development Tasks
```bash
# Install/update dependencies
poetry install

# Run tests
poetry run pytest tests/                    # All tests
poetry run pytest tests/ -k "test_fire_risk" # Specific tests
poetry run pytest -vv -s                    # Verbose output

# Start development server
adk web  # Visit http://localhost:8000

# Build deployment package
poetry build --format=wheel --output=deployment

# Deploy to production
cd deployment
python deploy.py --create  # Initial deployment
python deploy.py --update  # Update existing
```

### Cache Management & Troubleshooting
```bash
# Clear all Python cache when updating modules
pkill -f "adk web" 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
rm -rf .cache 2>/dev/null || true

# Restart ADK web with fresh cache
source ../venv/bin/activate
adk web

# Common issues
# If "python" command not found, use "python3"
# If module import errors, ensure venv is activated
# If wrong import name, check actual export (e.g., Agent vs agent)
```

### Fire-Specific Testing
```bash
# Core integration tests
python test_phase_iii_complete.py      # Full system validation
python test_station_validation.py       # Weather station reliability
python test_nl_enhancement.py          # Natural language processing
python test_visual_enhancement.py      # Visual formatting validation
python test_complete_visual_system.py  # Full visual system test

# Fire calculations
python test_nfdrs.py                   # NFDRS engine validation
python test_real_fire_data.py          # Real data integration
python benchmark_nfdrs.py              # Performance benchmarking
```

## Architecture Overview

### Multi-Agent System with Sequential Patterns

The RisenOne system uses a **hybrid architecture** combining multi-agent coordination with sequential execution patterns. This provides both flexibility and reliability.

#### 1. **Root Agent** (`agent/data_science/agent.py`)
   - Fire Analysis Coordinator routing queries to appropriate sub-agents
   - Integrated tools for direct fire danger calculations
   - Visual intelligence formatting for professional briefings
   - **Sequential Pattern**: Processes queries through defined steps

#### 2. **Sequential Query Processing** (`agent/data_science/query_enhancement.py`)
   - **QueryDecomposer** breaks complex queries into sequential steps:
     1. Intent Recognition → 2. Parameter Extraction → 3. Tool Selection → 4. Execution
   - Handles comparison queries, temporal analysis, and decision support
   - Each step builds upon previous results

#### 3. **Sub-Agents** (`agent/data_science/sub_agents/`)
   - **bigquery/**: Natural language to SQL for fire data queries
   - **data_integration/**: Synthetic data generation and historical data
   - **weather/**: Weather.gov API integration
   - **fire_detection/**: NASA FIRMS active fire detection
   - **bqml/**: Machine learning fire prediction models
   - **Coordination**: Sub-agents are called sequentially to avoid race conditions

#### 4. **Fire Calculations** (`agent/data_science/fire_calculations/`)
   - Complete NFDRS (National Fire Danger Rating System) implementation
   - **Sequential Pipeline**: Weather → Fuel Moisture → Spread → Burning Index → Rating
   - Dead fuel moisture, spread component, burning index calculations
   - Fire danger rating classification (LOW to EXTREME)

#### 5. **Visual Intelligence System** (`agent/data_science/`)
   - `visual_formatter.py`: ASCII gauges, risk indicators, professional briefings
   - `response_modes.py`: Multi-modal responses (Executive, Operational, Scientific, Emergency)
   - `intelligent_cache.py`: Smart caching with freshness indicators (99.8% performance improvement)
   - `query_enhancement.py`: Natural language decomposition and regional station mapping

### Architecture Benefits

- **Predictable Execution**: Sequential patterns ensure consistent results
- **Easy Debugging**: Each step can be traced and validated
- **Performance**: Caching and parallel execution where appropriate
- **Flexibility**: Multi-agent system allows for complex queries
- **Reliability**: 95.5% station reliability with proper error handling

### Key Integration Points

- **BigQuery Dataset**: `fire_risk_poc` - fire occurrence and weather data
- **Vertex AI**: Deployed as conversational agent on Agent Engine
- **Weather.gov API**: Real-time weather data for 21+ validated stations
- **Environment Variables**: Configure in `agent/.env` (see pyproject.toml)

## Configuration Verification

### Quick Health Check
```bash
# Run from agent directory
python verify_system_health.py
```

### Critical Configuration Settings
```bash
# agent/.env - MUST contain these exact values:
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=risenone-ai-prototype
GOOGLE_CLOUD_LOCATION=us-central1
BQ_PROJECT_ID=risenone-ai-prototype
BQ_DATASET_ID=fire_risk_poc  # ⚠️ NOT 'forecasting_sticker_sales'
```

### Common Configuration Issues & Solutions

1. **Wrong Dataset Error**
   - **Symptom**: Agent returns generic responses, no station data
   - **Cause**: BQ_DATASET_ID set to wrong value
   - **Fix**: Ensure BQ_DATASET_ID=fire_risk_poc

2. **Import Errors**
   - **Symptom**: ModuleNotFoundError when starting agent
   - **Cause**: Not in correct directory or venv not activated
   - **Fix**: `cd agent && source ../venv/bin/activate`

3. **BigQuery Timeout**
   - **Symptom**: Queries timeout after 30 seconds
   - **Cause**: Large queries without optimization
   - **Fix**: Use intelligent_cache.py and query optimization

4. **Visual Formatting Lost**
   - **Symptom**: Plain text responses instead of formatted output
   - **Cause**: Sub-agents not preserving formatting
   - **Fix**: Ensure all agents use visual_formatter.py

### Critical Bug Fixes

5. **Coroutine Serialization Error**
   - **Symptom**: `{"error": "Unable to serialize unknown type: <class 'coroutine'>"}` in ADK Web
   - **Cause**: ADK cannot serialize async functions as tools
   - **Fix**: Convert all tool functions from `async def` to regular `def` and use the `run_async()` helper:
   ```python
   # Wrong - causes error
   async def my_tool():
       return await some_async_operation()
   
   # Correct - works with ADK
   def my_tool():
       return run_async(some_async_operation())
   ```

## Performance Achievements

### Phase II Optimization (COMPLETE)
- Response time: 15-30s → <10s (target achieved)
- BigQuery timeout: 30s → 12s (60% improvement)
- Schema caching: 5-minute TTL, eliminates repeated overhead
- Average performance: 4.86s across all query types

### Phase III Enhancements (COMPLETE)
- Natural language query decomposition
- Regional station mapping (CA/OR/WA/CO/AZ + extended coverage)
- Visual intelligence with ASCII gauges and risk indicators
- Multi-modal response formatting based on user role
- Intelligent caching with freshness indicators

## Agent Capabilities

### Real-Time Weather Intelligence
- **Tool**: `get_real_time_fire_weather_conditions(location)`
- **Enhanced Tool**: `get_weather_by_location(location, forecast_days=None)`
- **Location Formats**: Cities, station names, ICAO codes, coordinates, landmarks, regions, ZIP codes
- **Performance**: 0.17s average response time
- **Coverage**: 21+ validated weather stations across western US

### 7-Day Fire Weather Forecasting
- **Tool**: `get_fire_weather_forecast(location, forecast_days=3)`
- **Natural Language**: Accepts city names, station names, coordinates, etc.
- **Model**: BQML Linear Regression (R² = 0.46)
- **Training Data**: 8,958 weather-fire correlation records

### Weather Location Resolution
- **Module**: `data_science/weather_resolver.py`
- **Supported Formats**:
  - Cities: "Denver", "Los Angeles, CA"
  - Stations: "BROWNSBORO", "BLACK HILLS"
  - ICAO: "KDEN", "KLAX"
  - Coordinates: "37.7749, -122.4194"
  - Landmarks: "Yosemite", "Grand Canyon"
  - Regions: "northern california", "bay area"
  - ZIP codes: "90210", "80202"

### NFDRS Fire Danger Calculations
- **Tool**: `calculate_fire_danger(temp, humidity, wind, precipitation)`
- **Performance**: 0.000002s per calculation (622K calculations/second)
- **Standard**: Full NFDRS-compliant formulas

### Historical Fire Analysis
- **Tool**: `get_fire_danger_for_station(station_name, limit)`
- **Data**: BigQuery integration with 17,386 fire records from 278 stations

## Performance Monitoring

The system includes built-in performance monitoring (`data_science/performance_monitor.py`):

### Using Performance Decorators
```python
from performance_monitor import track_performance, record_cache_hit

@track_performance('my_operation')
def my_function():
    # Your code here
    pass

# Record cache hits/misses
record_cache_hit(True)  # Cache hit
record_cache_hit(False) # Cache miss
```

### Viewing Performance Metrics
```python
from performance_monitor import get_performance_monitor
monitor = get_performance_monitor()
print(monitor.generate_report())

# Export metrics to JSON
monitor.export_metrics('performance_metrics.json')
```

## Validated Weather Station Coverage

### Automatic Station Name Mapping (NEW)
The system now automatically converts fire station names to Weather.gov airport codes:
- **BROWNSBORO** → KSDF (Louisville)
- **BLACK HILLS** → KRAP (Rapid City)
- **BISON CREEK** → KDEN (Denver)
- **WESTWOOD** → KBUR (Los Angeles)
- See `STATION_FORMAT_GUIDE.md` for complete mapping

### Station Coverage (95.5% Reliability)
```yaml
Working Stations:
  California: [KCEC, KSTS, KBUR, KFAT, KSAN, KMOD]
  Oregon: [KPDX, KEUG, KBDN]  # KALE removed - no data
  Washington: [KSEA, KGEG, KPUW, KOLM]
  Colorado: [KDEN, KCOS]
  Arizona: [KPHX, KTUS, KFLG]
  
Extended Coverage:
  Nevada: [KLAS, KRNO, KELY]
  Montana: [KBIL, KGPI, KHLN, KMSO]
  Utah: [KSLC, KCDC, KVGU, KPVU]
  Idaho: [KBOI, KSUN, KLWS, KIDA]
  New Mexico: [KABQ, KROW, KFMN]
```

## Visual Enhancement System

### Visual Intelligence Features
- **ASCII Gauge Visualizations**: Dynamic fire weather index gauges (0-10 scale)
- **Risk Level Indicators**: Color-coded bars with emojis (🔴🟠🟡🟢)
- **Professional Station Cards**: Formatted layouts with critical metrics
- **Forecast Timelines**: 7-day visual trend analysis
- **Operational Guidance**: Action-oriented recommendations with icons

### Multi-Modal Response Intelligence
- **Executive Mode**: 30-second decision briefs with cost estimates
- **Operational Mode**: Tactical crew positioning and equipment deployment
- **Scientific Mode**: Detailed meteorological analysis with data tables
- **Emergency Mode**: Critical action alerts with immediate deployment
- **Balanced Mode**: Standard visual intelligence briefings

### Intelligent Caching System
- **Live Data**: Real-time freshness indicators
- **Fresh Cache**: <5 minutes with performance optimization
- **Cached Data**: <30 minutes with background refresh
- **Performance**: 99.8% cache hit improvement, <0.1ms formatting speed

## Key Files and Locations

### Core Agent Files
- **Main Agent**: `data_science/agent.py` - Root agent with visual formatting & demo tools
- **Query Enhancement**: `data_science/query_enhancement.py` - NL processing
- **Visual Formatter**: `data_science/visual_formatter.py` - ASCII visualizations & database formatting
- **Demo Enhancements**: `data_science/demo_enhancements.py` - Zone recognition & financial analysis
- **Response Modes**: `data_science/response_modes.py` - Multi-modal responses
- **Intelligent Cache**: `data_science/intelligent_cache.py` - Smart caching

### Fire Calculations
- **NFDRS Engine**: `data_science/fire_calculations/nfdrs_engine.py`
- **Fuel Models**: `data_science/fire_calculations/fuel_models.py`
- **Fire Tables**: `data_science/fire_calculations/fire_tables.py`

### Sub-Agents
- **Database Agent**: `data_science/sub_agents/bigquery/agent.py` - Visual SQL results
- **Tools**: `data_science/sub_agents/bigquery/tools.py` - Query execution with formatting

### Test Files
- **Integration Tests**: `test_phase_iii_complete.py`, `test_station_validation.py`
- **Visual Tests**: `test_visual_enhancement.py`, `test_complete_visual_system.py`
- **Demo Tests**: `test_demo_enhancements.py` - Zone & financial validation
- **Performance**: `benchmark_nfdrs.py`, `test_production_performance.py`

### Weather System Files
- **Weather Resolver**: `data_science/weather_resolver.py` - Natural language location parsing
- **Location Database**: 80+ cities, 20+ landmarks, 20+ fire stations, 20+ regions
- **Test Files**: `test_forecast_natural_language.py` - Validates flexible input handling

## Production Deployment

### Deployment Commands
```bash
# Build deployment package
cd agent
poetry build --format=wheel --output=deployment

# Deploy to Vertex AI
cd deployment/
python deploy.py --create  # Initial deployment
python deploy.py --update  # Update existing agent
```

### Production Status
- **READY FOR PRODUCTION**: ✅
- All integration tests passing (14/14 including visual enhancements)
- Station reliability validated (95.5%)
- Performance targets exceeded (<0.1ms visual formatting)
- Error handling production-grade
- Visual Enhancement System production ready (80% test success rate)

## Recent Enhancements (Phase III Complete)

### Visual System Fixes
1. **Database Query Formatting** - SQL results now use visual formatter
2. **Agent Instruction Updates** - Preserves formatting throughout chain
3. **Multi-Agent Coordination** - Sub-agents maintain visual responses
4. **100% Format Preservation** - No more plain text summaries

### Demo Enhancements  
1. **Zone Recognition** - "Zone 7" triggers emergency responses
2. **Financial Analysis** - ROI/cost comparison capabilities
3. **Emergency Templates** - Dramatic responses with metrics
4. **Response Timing** - Shows <3 second analysis times

### New Tools Added
- `analyze_fire_zone` - Zone emergency management
- `analyze_financial_impact` - Financial ROI analysis
- `explain_fire_danger_level` - Educational content

### Station Mapping Enhancement (June 19, 2025)
- **Automatic Conversion** - Fire station names → ICAO codes
- **Seamless Integration** - Works with existing weather tools
- **12 Station Mappings** - BROWNSBORO, BLACK HILLS, etc.
- **Backward Compatible** - ICAO codes still work directly

### Weather API Natural Language Enhancement (June 20, 2025)
- **Universal Location Support** - 8 different input formats
- **Forecast Integration** - Natural language for all weather queries
- **Intelligent Resolver** - Fuzzy matching with confidence scoring
- **Comprehensive Database** - 80+ cities, landmarks, regions mapped

## Voice Integration Plan (Future Sprint)

### Feature 1: Intelligent Voice Alerts
- Proactive voice alerts for critical fire updates
- Two AI voice personas (urgent/standard) based on severity
- Browser notifications + Web Audio API

### Feature 2: Push-to-Talk Voice Query
- Simple voice queries with instant visual+audio response
- <200ms perceived response time using pre-cached acknowledgments
- Pre-optimized demo scenarios for instant response