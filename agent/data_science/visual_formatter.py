"""
Visual Response Formatter for Fire Weather Intelligence
Transforms technical data into visually stunning intelligence briefings
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import math


class VisualResponseFormatter:
    """Create visually stunning fire weather intelligence responses"""
    
    # Visual risk indicators with emojis and ASCII bars
    RISK_VISUALS = {
        'EXTREME': {
            'emoji': '🔴🔥',
            'bar': '████████████',
            'color_code': 'CRITICAL',
            'action_icon': '🚨',
            'bar_char': '█',
            'threshold': 8.0
        },
        'HIGH': {
            'emoji': '🟠⚠️',
            'bar': '████████░░░░',
            'color_code': 'WARNING', 
            'action_icon': '⚡',
            'bar_char': '█',
            'threshold': 6.0
        },
        'MODERATE': {
            'emoji': '🟡📊',
            'bar': '██████░░░░░░',
            'color_code': 'CAUTION',
            'action_icon': '👁️',
            'bar_char': '█',
            'threshold': 4.0
        },
        'LOW': {
            'emoji': '🟢✅',
            'bar': '███░░░░░░░░░',
            'color_code': 'SAFE',
            'action_icon': '✓',
            'bar_char': '█',
            'threshold': 0.0
        }
    }
    
    # Freshness indicators for cached data
    FRESHNESS_INDICATORS = {
        'live': {'emoji': '🟢', 'text': 'LIVE DATA'},
        'fresh': {'emoji': '🔵', 'text': 'RECENT (<5 min)'},
        'cached': {'emoji': '🟡', 'text': 'CACHED (<30 min)'},
        'stale': {'emoji': '🟠', 'text': 'UPDATE AVAILABLE'}
    }
    
    def format_fire_weather_response(self, data: Dict, freshness: str = 'live') -> str:
        """Create visually enhanced fire weather briefing"""
        
        # Determine overall risk level
        risk_level = self._determine_risk_level(data)
        visuals = self.RISK_VISUALS[risk_level]
        
        # Create header with dynamic visual elements
        timestamp = datetime.now().strftime('%B %d, %Y - %I:%M %p')
        region = data.get('region', 'Unknown').upper()
        fire_index = data.get('fire_index', data.get('avg_fire_index', 0))
        
        # Add freshness indicator
        freshness_indicator = self.FRESHNESS_INDICATORS.get(freshness, self.FRESHNESS_INDICATORS['live'])
        
        response = f"""
{visuals['emoji']} **FIRE WEATHER INTELLIGENCE BRIEFING** {visuals['emoji']}
═══════════════════════════════════════════════════════════

{freshness_indicator['emoji']} **Data Status**: {freshness_indicator['text']}
📅 **Date**: {timestamp}
📍 **Region**: {region}
🎯 **Overall Risk**: {visuals['bar']} {risk_level}

┌─────────────────────────────────────────────────────────┐
│ 🔥 FIRE WEATHER INDEX: {fire_index:.1f}/10.0                         │
│ {self._create_visual_gauge(fire_index)}  │
└─────────────────────────────────────────────────────────┘
"""
        
        # Add station-specific visual cards if available
        if 'stations' in data and data['stations']:
            response += self._create_station_cards(data['stations'])
        elif 'station_data' in data:
            response += self._create_single_station_card(data)
        
        # Add operational recommendations
        response += self._create_operational_section(risk_level, data)
        
        # Add forecast visualization if available
        if 'forecast' in data and data['forecast']:
            response += self._create_forecast_visualization(data['forecast'])
        
        return response
    
    def _determine_risk_level(self, data: Dict) -> str:
        """Determine overall risk level from data"""
        
        # Try different ways to get fire index
        fire_index = (
            data.get('fire_index') or 
            data.get('avg_fire_index') or 
            data.get('fire_weather_index') or 
            0
        )
        
        # If we have stations, use max fire index
        if 'stations' in data and data['stations']:
            fire_indices = []
            for station in data['stations']:
                station_fwi = (
                    station.get('fire_index') or
                    station.get('fwi') or
                    station.get('fire_weather_index') or
                    0
                )
                fire_indices.append(station_fwi)
            
            if fire_indices:
                fire_index = max(fire_indices)
        
        # Determine risk level based on fire index
        if fire_index >= 8.0:
            return 'EXTREME'
        elif fire_index >= 6.0:
            return 'HIGH'
        elif fire_index >= 4.0:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _create_visual_gauge(self, value: float) -> str:
        """Create ASCII gauge visualization"""
        # Normalize value to 0-40 range for visualization
        normalized_value = max(0, min(10, value))  # Clamp to 0-10
        filled = int((normalized_value / 10.0) * 40)
        empty = 40 - filled
        
        gauge = f"[{'█' * filled}{'░' * empty}]"
        
        # Add markers and labels
        markers = "\n         │         │         │         │         │"
        labels = "\n         0        2.5       5.0       7.5       10"
        
        return gauge + markers + labels
    
    def _create_station_cards(self, stations: List[Dict]) -> str:
        """Create visual station information cards"""
        cards = "\n📊 **STATION CONDITIONS**\n"
        cards += "─" * 55 + "\n\n"
        
        for station in stations:
            risk = self._get_station_risk(station)
            visual = self.RISK_VISUALS[risk]
            
            # Extract station data with fallbacks
            name = station.get('name', station.get('station_name', 'Unknown'))
            station_id = station.get('id', station.get('station_id', 'N/A'))
            temp = station.get('temp', station.get('temperature', 0))
            humidity = station.get('humidity', station.get('relative_humidity', 0))
            wind = station.get('wind', station.get('wind_speed', 0))
            fwi = station.get('fwi', station.get('fire_index', station.get('fire_weather_index', 0)))
            
            cards += f"""
┌─ {name} ({station_id}) ─────────────────────────────────┐
│ {visual['emoji']} Risk Level: {visual['bar']} {risk}     │
│ 🌡️  Temp: {temp:.0f}°F    💧 RH: {humidity:.0f}%        │
│ 💨 Wind: {wind:.0f} mph   🔥 FWI: {fwi:.1f}/10          │
└──────────────────────────────────────────────────────────┘
"""
        
        return cards
    
    def _create_single_station_card(self, data: Dict) -> str:
        """Create visual card for single station data"""
        cards = "\n📊 **STATION CONDITIONS**\n"
        cards += "─" * 55 + "\n\n"
        
        # Extract station data
        station_name = data.get('station_name', data.get('station', 'Unknown'))
        temp = data.get('temperature', data.get('temp', 0))
        humidity = data.get('relative_humidity', data.get('humidity', 0))
        wind = data.get('wind_speed', data.get('wind', 0))
        fwi = data.get('fire_weather_index', data.get('fire_index', data.get('fwi', 0)))
        
        risk = self._determine_risk_from_fwi(fwi)
        visual = self.RISK_VISUALS[risk]
        
        cards += f"""
┌─ {station_name} ──────────────────────────────────────────┐
│ {visual['emoji']} Risk Level: {visual['bar']} {risk}     │
│ 🌡️  Temp: {temp:.0f}°F    💧 RH: {humidity:.0f}%        │
│ 💨 Wind: {wind:.0f} mph   🔥 FWI: {fwi:.1f}/10          │
└──────────────────────────────────────────────────────────┘
"""
        
        return cards
    
    def _get_station_risk(self, station: Dict) -> str:
        """Get risk level for individual station"""
        fwi = station.get('fwi', station.get('fire_index', station.get('fire_weather_index', 0)))
        return self._determine_risk_from_fwi(fwi)
    
    def _determine_risk_from_fwi(self, fwi: float) -> str:
        """Determine risk level from fire weather index"""
        if fwi >= 8.0:
            return 'EXTREME'
        elif fwi >= 6.0:
            return 'HIGH'
        elif fwi >= 4.0:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _create_operational_section(self, risk_level: str, data: Dict) -> str:
        """Create operational guidance with visual emphasis"""
        visual = self.RISK_VISUALS[risk_level]
        
        section = f"\n{visual['action_icon']} **OPERATIONAL GUIDANCE** {visual['action_icon']}\n"
        section += "═" * 55 + "\n\n"
        
        # Get risk-specific recommendations
        recommendations = self._get_risk_recommendations(risk_level)
        
        for i, rec in enumerate(recommendations, 1):
            section += f"  {i}. {rec['icon']} **{rec['action']}**\n"
            section += f"     └─ {rec['detail']}\n\n"
        
        return section
    
    def _get_risk_recommendations(self, risk_level: str) -> List[Dict]:
        """Get operational recommendations based on risk level"""
        
        recommendations = {
            'EXTREME': [
                {
                    'icon': '🚨',
                    'action': 'IMMEDIATE ACTION REQUIRED',
                    'detail': 'Deploy all available resources, restrict public access'
                },
                {
                    'icon': '🚒',
                    'action': 'Pre-position Equipment',
                    'detail': 'Stage Type 1 engines at high-risk areas'
                },
                {
                    'icon': '📡',
                    'action': 'Continuous Monitoring',
                    'detail': '15-minute weather observations, real-time reporting'
                }
            ],
            'HIGH': [
                {
                    'icon': '⚡',
                    'action': 'Increase Readiness',
                    'detail': 'Pre-position resources, brief crews on conditions'
                },
                {
                    'icon': '👁️',
                    'action': 'Enhanced Monitoring',
                    'detail': 'Hourly weather observations required'
                },
                {
                    'icon': '📞',
                    'action': 'Coordinate Communications',
                    'detail': 'Ensure all crews on tactical frequency'
                }
            ],
            'MODERATE': [
                {
                    'icon': '📊',
                    'action': 'Standard Monitoring',
                    'detail': 'Regular weather observations, maintain readiness'
                },
                {
                    'icon': '🛠️',
                    'action': 'Equipment Check',
                    'detail': 'Verify all equipment operational and accessible'
                },
                {
                    'icon': '📋',
                    'action': 'Review Plans',
                    'detail': 'Update suppression plans based on conditions'
                }
            ],
            'LOW': [
                {
                    'icon': '✅',
                    'action': 'Normal Operations',
                    'detail': 'Standard patrol and monitoring procedures'
                },
                {
                    'icon': '🔧',
                    'action': 'Maintenance Window',
                    'detail': 'Good time for equipment maintenance and training'
                },
                {
                    'icon': '📚',
                    'action': 'Training Opportunity',
                    'detail': 'Conduct drills and prepare for higher risk periods'
                }
            ]
        }
        
        return recommendations.get(risk_level, recommendations['LOW'])
    
    def _create_forecast_visualization(self, forecast: List[Dict]) -> str:
        """Create visual forecast timeline"""
        viz = "\n📅 **7-DAY FIRE WEATHER OUTLOOK**\n"
        viz += "─" * 55 + "\n\n"
        
        # Timeline visualization
        for day in forecast[:7]:
            fire_index = day.get('fire_index', day.get('predicted_fire_index', 0))
            date_str = day.get('date', day.get('forecast_date', 'Unknown'))
            
            # Create risk emoji and bar
            risk_emoji = self._get_risk_emoji(fire_index)
            bar_length = max(0, min(50, int(fire_index * 5)))  # Scale to 50 chars, clamp
            bar = '█' * bar_length
            
            viz += f"{date_str:>10} {risk_emoji} {bar:<50} {fire_index:.1f}\n"
        
        return viz
    
    def _get_risk_emoji(self, fire_index: float) -> str:
        """Get risk emoji based on fire index"""
        if fire_index >= 8.0:
            return '🔴'
        elif fire_index >= 6.0:
            return '🟠'
        elif fire_index >= 4.0:
            return '🟡'
        else:
            return '🟢'
    
    def format_fire_danger_calculation(self, data: Dict) -> str:
        """Format NFDRS fire danger calculation results"""
        
        risk_level = self._determine_risk_from_fwi(data.get('burning_index', 0))
        visual = self.RISK_VISUALS[risk_level]
        
        response = f"""
{visual['emoji']} **NFDRS FIRE DANGER CALCULATION** {visual['emoji']}
═══════════════════════════════════════════════════════════

📊 **INPUT CONDITIONS**
├─ 🌡️  Temperature: {data.get('temperature', 'N/A')}°F
├─ 💧 Relative Humidity: {data.get('humidity', 'N/A')}%
├─ 💨 Wind Speed: {data.get('wind_speed', 'N/A')} mph
└─ 🌧️ Precipitation: {data.get('precipitation', 'N/A')}"

📈 **CALCULATED VALUES**
├─ Dead Fuel Moisture: {data.get('dead_fuel_moisture', 'N/A')}%
├─ Spread Component: {data.get('spread_component', 'N/A')}
├─ Burning Index: {data.get('burning_index', 'N/A')}
└─ Fire Danger Class: {visual['bar']} {data.get('fire_danger_class', risk_level)}

{visual['action_icon']} **FIRE BEHAVIOR ASSESSMENT** {visual['action_icon']}
═══════════════════════════════════════════════════════════

• **Ignition Potential**: {self._get_ignition_assessment(data)}
• **Rate of Spread**: {self._get_spread_assessment(data)}
• **Intensity Level**: {self._get_intensity_assessment(data)}
"""
        
        return response
    
    def _get_ignition_assessment(self, data: Dict) -> str:
        """Get ignition potential assessment"""
        moisture = data.get('dead_fuel_moisture', 10)
        if moisture < 5:
            return "🔴 EXTREME - Any ignition source will start fire"
        elif moisture < 8:
            return "🟠 HIGH - Most ignition sources will start fire"
        elif moisture < 12:
            return "🟡 MODERATE - Some ignition sources may start fire"
        else:
            return "🟢 LOW - Difficult to ignite"
    
    def _get_spread_assessment(self, data: Dict) -> str:
        """Get rate of spread assessment"""
        spread_component = data.get('spread_component', 0)
        if spread_component > 50:
            return "🔴 EXTREME - Very rapid spread expected"
        elif spread_component > 30:
            return "🟠 HIGH - Rapid spread likely"
        elif spread_component > 15:
            return "🟡 MODERATE - Moderate spread rate"
        else:
            return "🟢 LOW - Slow spread expected"
    
    def _get_intensity_assessment(self, data: Dict) -> str:
        """Get fire intensity assessment"""
        burning_index = data.get('burning_index', 0)
        if burning_index > 80:
            return "🔴 EXTREME - Extreme fire behavior, suppression very difficult"
        elif burning_index > 50:
            return "🟠 HIGH - Active fire behavior, challenging suppression"
        elif burning_index > 25:
            return "🟡 MODERATE - Moderate fire behavior, standard suppression"
        else:
            return "🟢 LOW - Low intensity fire, easy suppression"
    
    def format_database_results(self, rows: List[Dict], sql_string: str = "") -> str:
        """Format database query results with visual appeal"""
        if not rows:
            return "📊 Query executed successfully but returned no results."
        
        # Check for fire danger station queries
        if any(col in str(rows[0]).lower() for col in ['burningindex', 'burning_index', 'fire', 'station']):
            return self._format_fire_station_results(rows)
        
        # Check for count queries
        if len(rows) == 1 and 'count' in str(rows[0]).lower():
            count_value = list(rows[0].values())[0]
            if 'station' in sql_string.lower():
                return f"""
📊 **WEATHER STATION COUNT** 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Total Stations Available: **{count_value:,}**

✅ All stations ready for fire danger analysis
🌡️ Real-time weather data available
🔥 NFDRS calculations supported
"""
            else:
                return f"📊 Query Result: **{count_value:,}**"
        
        # For other results, format as a nice table
        return self._format_as_visual_table(rows)
    
    def _format_fire_station_results(self, rows: List[Dict]) -> str:
        """Format fire station query results"""
        output = ["🔥 **FIRE DANGER ANALYSIS RESULTS** 🔥"]
        output.append("━" * 60)
        output.append("")
        
        # Group stations by risk level based on burning index
        extreme_risk = []
        very_high_risk = []
        high_risk = []
        moderate_risk = []
        
        for row in rows:
            # Try different column name variations
            burning_index = None
            station_name = None
            
            # Find burning index
            for key in row.keys():
                if 'burning' in key.lower() or 'bi' in key.lower():
                    burning_index = float(row[key]) if row[key] else 0
                if 'station' in key.lower() and 'name' in key.lower():
                    station_name = row[key]
                elif 'stationname' in key.lower():
                    station_name = row[key]
            
            if burning_index is not None and station_name:
                station_info = (station_name, burning_index)
                if burning_index > 100:
                    extreme_risk.append(station_info)
                elif burning_index > 75:
                    very_high_risk.append(station_info)
                elif burning_index > 50:
                    high_risk.append(station_info)
                else:
                    moderate_risk.append(station_info)
        
        # Display by risk level
        if extreme_risk:
            output.append("🔴 **EXTREME RISK STATIONS** (BI > 100)")
            output.append("⚠️ IMMEDIATE ACTION REQUIRED")
            for name, bi in sorted(extreme_risk, key=lambda x: x[1], reverse=True)[:10]:
                gauge = self._create_mini_gauge(bi, max_val=150)
                output.append(f"├─ {gauge} {name}: **{bi:.1f}**")
            if len(extreme_risk) > 10:
                output.append(f"└─ ... and {len(extreme_risk) - 10} more extreme risk stations")
            output.append("")
        
        if very_high_risk:
            output.append("🟠 **VERY HIGH RISK STATIONS** (BI: 75-100)")
            for name, bi in sorted(very_high_risk, key=lambda x: x[1], reverse=True)[:5]:
                gauge = self._create_mini_gauge(bi, max_val=150)
                output.append(f"├─ {gauge} {name}: {bi:.1f}")
            if len(very_high_risk) > 5:
                output.append(f"└─ ... and {len(very_high_risk) - 5} more very high risk stations")
            output.append("")
        
        if high_risk:
            output.append("🟡 **HIGH RISK STATIONS** (BI: 50-75)")
            for name, bi in sorted(high_risk, key=lambda x: x[1], reverse=True)[:5]:
                gauge = self._create_mini_gauge(bi, max_val=150)
                output.append(f"├─ {gauge} {name}: {bi:.1f}")
            if len(high_risk) > 5:
                output.append(f"└─ ... and {len(high_risk) - 5} more high risk stations")
            output.append("")
        
        # Summary statistics
        total_high_risk = len(extreme_risk) + len(very_high_risk) + len(high_risk)
        output.append("📊 **SUMMARY STATISTICS**")
        output.append(f"├─ 🔴 Extreme Risk: {len(extreme_risk)} stations")
        output.append(f"├─ 🟠 Very High Risk: {len(very_high_risk)} stations")
        output.append(f"├─ 🟡 High Risk: {len(high_risk)} stations")
        output.append(f"└─ 📈 Total High Risk: **{total_high_risk} stations**")
        
        return "\n".join(output)
    
    def _create_mini_gauge(self, value: float, max_val: float = 100) -> str:
        """Create a mini gauge for inline display"""
        percentage = min(value / max_val, 1.0)
        filled = int(percentage * 5)
        return "█" * filled + "▱" * (5 - filled)
    
    def _format_as_visual_table(self, rows: List[Dict], max_rows: int = 10) -> str:
        """Format generic query results as a visual table"""
        if not rows:
            return "No results found."
        
        output = ["📊 **QUERY RESULTS** 📊"]
        output.append("━" * 60)
        output.append(f"Total Records: {len(rows)}")
        output.append("")
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Create table header
        header = "│ " + " │ ".join(f"{col[:15]:^15}" for col in columns) + " │"
        separator = "├" + "┼".join("─" * 17 for _ in columns) + "┤"
        
        output.append("┌" + "┬".join("─" * 17 for _ in columns) + "┐")
        output.append(header)
        output.append(separator)
        
        # Add rows
        for i, row in enumerate(rows[:max_rows]):
            row_str = "│ "
            for col in columns:
                value = str(row.get(col, ""))[:15]
                row_str += f"{value:^15} │ "
            output.append(row_str)
        
        output.append("└" + "┴".join("─" * 17 for _ in columns) + "┘")
        
        if len(rows) > max_rows:
            output.append(f"\n... and {len(rows) - max_rows} more rows")
        
        return "\n".join(output)


# Global formatter instance
visual_formatter = VisualResponseFormatter()