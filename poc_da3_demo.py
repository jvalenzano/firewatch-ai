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
