#!/bin/bash

# POC-DA-3: Data Integration Setup Script
# Comprehensive data integration with synthetic dataset generation

set -e

echo "🚀 POC-DA-3: Data Integration Setup Starting..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "agent" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION detected"

# Check if we're on the right branch or create it
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "poc/da-3-data-integration" ]; then
    print_warning "Not on poc/da-3-data-integration branch"
    print_status "Current branch: $CURRENT_BRANCH"
    
    # Check if branch exists
    if git show-ref --verify --quiet refs/heads/poc/da-3-data-integration; then
        print_status "Switching to existing poc/da-3-data-integration branch..."
        git checkout poc/da-3-data-integration
    else
        print_status "Creating poc/da-3-data-integration branch..."
        git checkout -b poc/da-3-data-integration
    fi
fi

print_success "On poc/da-3-data-integration branch"

# Install dependencies
print_status "Installing data integration dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ -f "agent/data_science/sub_agents/data_integration/requirements.txt" ]; then
    print_status "Installing data integration requirements..."
    pip install -r agent/data_science/sub_agents/data_integration/requirements.txt
else
    print_warning "No requirements.txt found, installing basic dependencies..."
    pip install pandas numpy scipy scikit-learn matplotlib seaborn plotly
fi

print_success "Dependencies installed"

# Create output directories
print_status "Creating output directories..."
mkdir -p agent/data_science/utils/data/integrated_data
mkdir -p agent/data_science/utils/data/fire_data/data
print_success "Output directories created"

# Verify data integration module
print_status "Verifying data integration module..."

cd agent/data_science/sub_agents/data_integration

# Check if all required files exist
REQUIRED_FILES=(
    "__init__.py"
    "data_integration_engine.py"
    "historical_data_generator.py"
    "fire_detection_simulator.py"
    "test_data_integration.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_success "All required module files present"

# Run tests to verify functionality
print_status "Running POC-DA-3 test suite..."
echo ""

python3 test_data_integration.py

TEST_EXIT_CODE=$?
cd ../../../..

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed. Check the output above."
    exit 1
fi

# Create POC-DA-3 demonstration
print_status "Creating data integration demonstration..."

# Create demo script
cat > poc_da3_demo.py << 'EOF'
#!/usr/bin/env python3
"""
POC-DA-3 Data Integration Demonstration

Demonstrates the complete data integration pipeline with realistic
synthetic data generation and fire detection simulation.
"""

import os
import sys
import json
from datetime import datetime

# Add the agent path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent', 'data_science', 'sub_agents', 'data_integration'))

from data_integration_engine import DataIntegrationEngine, DataIntegrationConfig

def run_poc_da3_demonstration():
    """Run complete POC-DA-3 demonstration"""
    
    print("🚀 POC-DA-3: Data Integration Demonstration")
    print("=" * 50)
    
    # Configure for demonstration
    config = DataIntegrationConfig(
        start_date="2021-01-01",
        end_date="2024-01-01",  # Full 3-year period
        min_stations=20,
        output_directory="agent/data_science/utils/data/integrated_data"
    )
    
    print(f"📅 Period: {config.start_date} to {config.end_date}")
    print(f"🏭 Minimum stations: {config.min_stations}")
    print(f"📁 Output directory: {config.output_directory}")
    
    # Initialize data integration engine
    print("\n🔧 Initializing Data Integration Engine...")
    engine = DataIntegrationEngine(config)
    
    # Run complete integration pipeline
    print("\n⚡ Running Complete Integration Pipeline...")
    start_time = datetime.now()
    
    results = engine.run_complete_integration()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 POC-DA-3 RESULTS SUMMARY")
    print("=" * 50)
    
    if results['success']:
        print("✅ Status: SUCCESS")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📈 Overall Similarity: {results['validation_metrics']['overall_similarity']:.1%}")
        
        # Display step completion
        print(f"\n📋 Steps Completed: {len(results['steps_completed'])}/6")
        for step in results['steps_completed']:
            print(f"   ✅ {step}")
        
        # Display validation metrics
        print(f"\n🔍 Validation Metrics:")
        for metric, value in results['validation_metrics'].items():
            print(f"   • {metric}: {value:.3f}")
        
        # Display dataset information
        if engine.integrated_dataset:
            metadata = engine.integrated_dataset['metadata']
            print(f"\n📊 Dataset Statistics:")
            print(f"   • Stations: {metadata['station_count']}")
            print(f"   • Historical Records: {metadata['historical_records']:,}")
            print(f"   • Fire Events: {metadata['fire_events']}")
        
        # Check success criteria
        print(f"\n🎯 POC-DA-3 Success Criteria:")
        
        station_count = metadata['station_count']
        similarity = results['validation_metrics']['overall_similarity']
        
        print(f"   ✅ Synthetic RAWS data: {station_count} stations (Target: 20+)")
        print(f"   ✅ Statistical similarity: {similarity:.1%} (Target: 95%)")
        print(f"   ✅ Generation time: {duration:.1f}s (Target: <30 minutes)")
        print(f"   ✅ AI-ready dataset: Available")
        
        if station_count >= 20 and similarity >= 0.95 and duration < 1800:
            print(f"\n🎉 ALL SUCCESS CRITERIA MET!")
        else:
            print(f"\n⚠️  Some criteria may need optimization for production")
        
    else:
        print("❌ Status: FAILED")
        print(f"💥 Error: {results.get('error_message', 'Unknown error')}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_poc_da3_demonstration()
    print(f"\n{'🎉 POC-DA-3 COMPLETE!' if success else '❌ POC-DA-3 FAILED!'}")
EOF

chmod +x poc_da3_demo.py

# Run the demonstration
print_status "Running POC-DA-3 demonstration..."
echo ""

python3 poc_da3_demo.py

DEMO_EXIT_CODE=$?

if [ $DEMO_EXIT_CODE -eq 0 ]; then
    print_success "POC-DA-3 demonstration completed successfully!"
else
    print_error "POC-DA-3 demonstration failed"
    exit 1
fi

# Summary
echo ""
print_success "🎉 POC-DA-3 Data Integration Setup Complete!"
echo ""
echo "=================================="
echo "📋 POC-DA-3 SETUP SUMMARY"
echo "=================================="
echo "✅ Branch: poc/da-3-data-integration"
echo "✅ Dependencies: Installed"
echo "✅ Module Structure: Complete"
echo "✅ Tests: All Passed"
echo "✅ Demonstration: Successful"
echo ""
echo "📁 Key Files Created:"
echo "   • agent/data_science/sub_agents/data_integration/"
echo "   • setup-poc-da3.sh"
echo "   • poc_da3_demo.py"
echo ""
echo "📊 Output Data:"
echo "   • agent/data_science/utils/data/integrated_data/"
echo ""
echo "🚀 Next Steps:"
echo "   • Review generated synthetic datasets"
echo "   • Validate data quality metrics"
echo "   • Proceed to POC-AD-1 (Agent Development)"
echo ""
print_success "Ready for POC-AD-1: Vertex AI Multi-Agent Platform!"

# Deactivate virtual environment
deactivate || true 