# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the RisenOne Fire Analysis Agent - a production Google Cloud AI system using the Agent Development Kit (ADK) v1.0.0. It implements a multi-agent architecture for wildfire risk analysis and fire danger calculations for the Forest Service.

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

### Common Development Tasks
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
python deploy.py --create
```

### Testing Fire Calculations
```bash
python test_nfdrs.py
python test_real_fire_data.py
```

## Architecture Overview

### Multi-Agent System Structure

The system follows an "Ultra-Minimal Production" strategy with a hierarchical agent architecture:

1. **Root Agent** (`agent/data_science/`)
   - Fire Analysis Coordinator that routes queries to appropriate sub-agents
   - Handles direct fire danger calculations via integrated tools
   - Manages conversation flow and user interactions

2. **Sub-Agents** (`agent/data_science/sub_agents/`)
   - **database_agent**: Natural language to SQL for BigQuery fire data queries
   - **data_integration**: Manages synthetic data generation and historical data
   - **geographic**: Geospatial analysis capabilities (future enhancement)
   - **analytics_agent**: Statistical analysis (placeholder)
   - **bqml_agent**: Machine learning capabilities (placeholder)

### Fire Calculations Module (`agent/fire_calculations/`)

Implements complete NFDRS (National Fire Danger Rating System) engine:
- `nfdrs_engine.py`: Core fire danger calculations
- `models.py`: Data models for fire inputs/outputs
- `fuel_models.py`: NFDRS fuel model definitions
- `fire_tables.py`: Lookup tables for fire behavior
- `utilities.py`: Helper functions

Key calculations include:
- Dead fuel moisture
- Spread component
- Burning index
- Fire danger rating (LOW to EXTREME)

### Data Flow

1. User query → Root Agent analyzes intent
2. Fire calculation queries → Direct tool execution
3. Database queries → Database sub-agent → BigQuery
4. Results formatted and returned to user

### Key Integration Points

- **BigQuery Dataset**: `fire_risk_poc` contains fire occurrence and weather data
- **Vertex AI**: Deployed as conversational agent on Agent Engine
- **Environment Variables**: Configure in `agent/.env` (see pyproject.toml for required vars)

### Development Tips

- Always test fire calculations with `test_nfdrs.py` after changes
- Sub-agents can be tested independently via their test files
- Use ADK web interface for interactive development
- Check deployment logs with `python list_agents.py` in deployment/
- Fire-specific SQL optimizations are in `database_agent/fire_enhancements.py`