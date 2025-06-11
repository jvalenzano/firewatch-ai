#!/usr/bin/env python3
"""
POC-DA-2 Test Script: Geographic Data Foundation Testing
Tests the real weather station data processing and geographic analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def test_station_data_loading():
    """Test loading and processing of real weather station data"""
    print("🧪 Testing Station Data Loading...")
    
    # Load StationMetaData.csv
    data_path = Path('../../utils/data/fire_data/data')
    station_file = data_path / 'StationMetaData.csv'
    
    if not station_file.exists():
        print("❌ Station metadata file not found")
        return False
    
    df = pd.read_csv(station_file)
    print(f"✅ Loaded {len(df)} weather stations from StationMetaData.csv")
    
    # Validate required columns
    required_columns = ['Station ID', 'Station Name', 'Latitude', 'Longitude', 'Elevation', 'Aspect']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return False
    
    print("✅ All required columns present")
    return True, df

def analyze_geographic_coverage(df):
    """Analyze geographic coverage of weather stations"""
    print("\n🌍 Analyzing Geographic Coverage...")
    
    # Basic statistics
    elevations = df['Elevation'].values
    latitudes = df['Latitude'].values
    longitudes = df['Longitude'].values
    
    print(f"📍 Geographic Extent:")
    print(f"   Latitude: {latitudes.min():.2f}° to {latitudes.max():.2f}°")
    print(f"   Longitude: {longitudes.min():.2f}° to {longitudes.max():.2f}°")
    print(f"   Elevation: {elevations.min():,} to {elevations.max():,} ft")
    
    print(f"\n📊 Elevation Statistics:")
    print(f"   Mean: {elevations.mean():.0f} ft")
    print(f"   Median: {np.median(elevations):.0f} ft")
    print(f"   Std Dev: {elevations.std():.0f} ft")
    
    # Aspect distribution
    aspect_counts = df['Aspect'].value_counts()
    print(f"\n🧭 Aspect Distribution (Top 10):")
    for aspect, count in aspect_counts.head(10).items():
        percentage = (count / len(df)) * 100
        print(f"   {aspect}: {count} stations ({percentage:.1f}%)")
    
    return {
        'total_stations': len(df),
        'latitude_range': [float(latitudes.min()), float(latitudes.max())],
        'longitude_range': [float(longitudes.min()), float(longitudes.max())],
        'elevation_range': [int(elevations.min()), int(elevations.max())],
        'elevation_stats': {
            'mean': float(elevations.mean()),
            'median': float(np.median(elevations)),
            'std': float(elevations.std())
        },
        'aspect_distribution': aspect_counts.to_dict()
    }

def extract_state_regions(df):
    """Extract state and region information from coordinates"""
    print("\n🗺️  Extracting State and Region Information...")
    
    state_regions = {
        'CA': 'West Coast', 'OR': 'West Coast', 'WA': 'West Coast',
        'AZ': 'Southwest', 'NM': 'Southwest', 'NV': 'Southwest', 'UT': 'Southwest',
        'CO': 'Rocky Mountain', 'WY': 'Rocky Mountain', 'MT': 'Rocky Mountain', 'ID': 'Rocky Mountain',
        'TX': 'South Central', 'OK': 'South Central', 'KS': 'South Central',
        'FL': 'Southeast', 'GA': 'Southeast', 'AL': 'Southeast', 'SC': 'Southeast', 'NC': 'Southeast',
        'TN': 'Southeast', 'KY': 'Southeast', 'VA': 'Southeast', 'WV': 'Southeast',
        'MN': 'Great Lakes', 'WI': 'Great Lakes', 'MI': 'Great Lakes',
        'ND': 'Northern Plains', 'SD': 'Northern Plains', 'NE': 'Northern Plains',
        'IA': 'Midwest', 'MO': 'Midwest', 'AR': 'Midwest', 'LA': 'Midwest', 'MS': 'Midwest',
        'NY': 'Northeast', 'PA': 'Northeast', 'MD': 'Northeast', 'NJ': 'Northeast', 'NH': 'Northeast'
    }
    
    def extract_state_from_coordinates(lat, lon):
        """Simple state extraction based on coordinate ranges"""
        if -125 <= lon <= -114 and 32 <= lat <= 42:
            return 'CA'
        elif -124 <= lon <= -116 and 42 <= lat <= 49:
            return 'WA' if lon > -120 else 'OR'
        elif -114 <= lon <= -109 and 31 <= lat <= 37:
            return 'AZ'
        elif -109 <= lon <= -103 and 31 <= lat <= 37:
            return 'NM'
        elif -120 <= lon <= -114 and 35 <= lat <= 42:
            return 'NV'
        elif -106 <= lon <= -93 and 25 <= lat <= 36:
            return 'TX'
        elif -87 <= lon <= -80 and 24 <= lat <= 31:
            return 'FL'
        else:
            return 'Unknown'
    
    # Extract states and regions
    df['State'] = df.apply(lambda row: extract_state_from_coordinates(row['Latitude'], row['Longitude']), axis=1)
    df['Region'] = df['State'].map(state_regions).fillna('Unknown')
    
    # Region distribution
    region_counts = df['Region'].value_counts()
    print(f"🏞️  Region Distribution:")
    for region, count in region_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {region}: {count} stations ({percentage:.1f}%)")
    
    return region_counts.to_dict()

def identify_high_elevation_stations(df, threshold=7000):
    """Identify high-elevation stations for fire risk analysis"""
    print(f"\n⛰️  High-Elevation Stations (>{threshold:,} ft):")
    
    high_elevation = df[df['Elevation'] > threshold].copy()
    high_elevation = high_elevation.sort_values('Elevation', ascending=False)
    
    print(f"Found {len(high_elevation)} stations above {threshold:,} ft")
    
    if len(high_elevation) > 0:
        print(f"Top 10 highest stations:")
        for _, station in high_elevation.head(10).iterrows():
            print(f"   {station['Station Name']}: {station['Elevation']:,} ft ({station.get('State', 'Unknown')})")
    
    return len(high_elevation)

def create_geographic_clusters(df, n_clusters=8):
    """Create geographic clusters using simple distance-based grouping"""
    print(f"\n🎯 Creating {n_clusters} Geographic Clusters...")
    
    try:
        from sklearn.cluster import KMeans
        
        # Prepare coordinate data
        coordinates = df[['Latitude', 'Longitude']].values
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(coordinates)
        
        df['Cluster'] = cluster_labels
        
        # Analyze clusters
        cluster_summary = []
        for cluster_id in range(n_clusters):
            cluster_stations = df[df['Cluster'] == cluster_id]
            
            cluster_info = {
                'cluster_id': cluster_id,
                'station_count': len(cluster_stations),
                'center_lat': float(cluster_stations['Latitude'].mean()),
                'center_lon': float(cluster_stations['Longitude'].mean()),
                'avg_elevation': float(cluster_stations['Elevation'].mean()),
                'elevation_range': [int(cluster_stations['Elevation'].min()), 
                                  int(cluster_stations['Elevation'].max())]
            }
            cluster_summary.append(cluster_info)
            
            print(f"   Cluster {cluster_id}: {len(cluster_stations)} stations, "
                  f"avg elevation {cluster_info['avg_elevation']:.0f} ft")
        
        print("✅ Geographic clustering completed")
        return cluster_summary
        
    except ImportError:
        print("⚠️  scikit-learn not available, skipping clustering")
        return []

def generate_poc_summary(df, geographic_stats, region_distribution, high_elevation_count, clusters):
    """Generate comprehensive POC-DA-2 summary"""
    print("\n📋 POC-DA-2 Summary Report:")
    print("=" * 50)
    
    summary = {
        'poc_phase': 'POC-DA-2',
        'title': 'Geographic Data Foundation and RAWS Station Mapping',
        'completion_status': 'In Progress',
        'data_source': 'Real client weather station data',
        'total_stations': geographic_stats['total_stations'],
        'geographic_coverage': {
            'latitude_span': geographic_stats['latitude_range'][1] - geographic_stats['latitude_range'][0],
            'longitude_span': geographic_stats['longitude_range'][1] - geographic_stats['longitude_range'][0],
            'elevation_span': geographic_stats['elevation_range'][1] - geographic_stats['elevation_range'][0]
        },
        'regional_distribution': region_distribution,
        'high_elevation_stations': high_elevation_count,
        'geographic_clusters': len(clusters),
        'key_achievements': [
            f"Processed {geographic_stats['total_stations']} real weather stations",
            f"Mapped stations across {len(region_distribution)} geographic regions",
            f"Identified {high_elevation_count} high-elevation stations for fire risk analysis",
            f"Created {len(clusters)} geographic clusters for regional analysis"
        ]
    }
    
    print(f"✅ Total Stations Processed: {summary['total_stations']}")
    print(f"✅ Geographic Regions: {len(region_distribution)}")
    print(f"✅ High-Elevation Stations: {high_elevation_count}")
    print(f"✅ Geographic Clusters: {len(clusters)}")
    
    return summary

def main():
    """Main test function for POC-DA-2"""
    print("🚀 POC-DA-2: Geographic Data Foundation Testing")
    print("=" * 60)
    
    # Test 1: Load station data
    result = test_station_data_loading()
    if not result:
        print("❌ Failed to load station data")
        return
    
    success, df = result
    
    # Test 2: Analyze geographic coverage
    geographic_stats = analyze_geographic_coverage(df)
    
    # Test 3: Extract state and region information
    region_distribution = extract_state_regions(df)
    
    # Test 4: Identify high-elevation stations
    high_elevation_count = identify_high_elevation_stations(df)
    
    # Test 5: Create geographic clusters
    clusters = create_geographic_clusters(df)
    
    # Test 6: Generate POC summary
    summary = generate_poc_summary(df, geographic_stats, region_distribution, high_elevation_count, clusters)
    
    # Export results
    output_file = 'poc_da2_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n💾 Test results exported to: {output_file}")
    print("\n🎉 POC-DA-2 Geographic Foundation Testing Complete!")

if __name__ == "__main__":
    main() 