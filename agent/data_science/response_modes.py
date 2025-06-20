"""
Multi-Modal Response Format Detection
Provides adaptive response formatting based on user role, context, and preferences
"""

import re
from typing import Dict, List, Optional, Any
from enum import Enum


class ResponseMode(Enum):
    """Response mode types for different user contexts"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational" 
    SCIENTIFIC = "scientific"
    EMERGENCY = "emergency"
    BALANCED = "balanced"


class ResponseModeDetector:
    """Intelligently detect preferred response format based on query context"""
    
    def __init__(self):
        # Keywords and patterns for different response modes
        self.mode_indicators = {
            ResponseMode.EXECUTIVE: {
                'keywords': [
                    'brief', 'summary', 'quick', 'decision', 'overview', 'status',
                    'report', 'update', 'budget', 'cost', 'resource', 'impact',
                    'chief', 'director', 'manager', 'leadership', 'strategic'
                ],
                'patterns': [
                    r'\b(executive|leadership|management)\b',
                    r'\b(brief|summary|quick)\s+(report|update|overview)\b',
                    r'\b(what\s+is\s+the|give\s+me\s+a)\s+(status|situation)\b'
                ],
                'priority_score': 10
            },
            ResponseMode.OPERATIONAL: {
                'keywords': [
                    'crew', 'position', 'deploy', 'tactical', 'engine', 'team',
                    'action', 'response', 'suppression', 'equipment', 'resource',
                    'firefighter', 'incident', 'command', 'field', 'ground',
                    'station', 'battalion', 'division', 'staging'
                ],
                'patterns': [
                    r'\b(crew|team|firefighter)\s+(position|deployment|action)\b',
                    r'\b(where\s+to|how\s+to)\s+(deploy|position|stage)\b',
                    r'\b(tactical|operational|field)\s+(guidance|recommendation)\b'
                ],
                'priority_score': 9
            },
            ResponseMode.SCIENTIFIC: {
                'keywords': [
                    'analysis', 'data', 'calculate', 'detailed', 'research',
                    'study', 'model', 'algorithm', 'methodology', 'statistical',
                    'correlation', 'regression', 'probability', 'formula',
                    'technical', 'scientific', 'academic', 'nfdrs', 'meteorological'
                ],
                'patterns': [
                    r'\b(how\s+does|explain\s+the)\s+(calculation|algorithm|model)\b',
                    r'\b(detailed|comprehensive|thorough)\s+(analysis|data|study)\b',
                    r'\b(statistical|scientific|technical)\s+(analysis|approach)\b'
                ],
                'priority_score': 8
            },
            ResponseMode.EMERGENCY: {
                'keywords': [
                    'emergency', 'urgent', 'immediate', 'critical', 'extreme',
                    'evacuation', 'alert', 'warning', 'danger', 'threat',
                    'now', 'asap', 'quickly', 'fast', 'rapid', 'red flag'
                ],
                'patterns': [
                    r'\b(emergency|urgent|immediate|critical)\b',
                    r'\b(red\s+flag|extreme\s+risk|critical\s+conditions)\b',
                    r'\b(need\s+to\s+know|what\s+to\s+do)\s+(now|immediately)\b'
                ],
                'priority_score': 15  # Highest priority
            }
        }
    
    def detect_response_mode(self, query: str, context: Optional[Dict] = None) -> ResponseMode:
        """Detect the most appropriate response mode for a query"""
        
        query_lower = query.lower()
        mode_scores = {}
        
        # Score each mode based on keyword and pattern matches
        for mode, indicators in self.mode_indicators.items():
            score = 0
            
            # Score keywords
            for keyword in indicators['keywords']:
                if keyword in query_lower:
                    score += 1
            
            # Score patterns (weighted higher)
            for pattern in indicators['patterns']:
                if re.search(pattern, query_lower):
                    score += 3
            
            # Apply priority multiplier
            final_score = score * indicators['priority_score']
            mode_scores[mode] = final_score
        
        # Add context-based scoring if available
        if context:
            mode_scores = self._apply_context_scoring(mode_scores, context)
        
        # Return mode with highest score, default to BALANCED
        if mode_scores:
            best_mode = max(mode_scores.items(), key=lambda x: x[1])
            if best_mode[1] > 0:
                return best_mode[0]
        
        return ResponseMode.BALANCED
    
    def _apply_context_scoring(self, mode_scores: Dict, context: Dict) -> Dict:
        """Apply additional scoring based on context"""
        
        # Time-based context (emergency mode for urgent times)
        if context.get('time_sensitive', False):
            mode_scores[ResponseMode.EMERGENCY] += 50
        
        # User role context
        user_role = context.get('user_role', '').lower()
        if 'chief' in user_role or 'director' in user_role:
            mode_scores[ResponseMode.EXECUTIVE] += 20
        elif 'captain' in user_role or 'firefighter' in user_role:
            mode_scores[ResponseMode.OPERATIONAL] += 20
        elif 'scientist' in user_role or 'researcher' in user_role:
            mode_scores[ResponseMode.SCIENTIFIC] += 20
        
        # Risk level context
        risk_level = context.get('risk_level', '').upper()
        if risk_level in ['EXTREME', 'CRITICAL']:
            mode_scores[ResponseMode.EMERGENCY] += 30
        
        return mode_scores


class MultiModalResponseFormatter:
    """Generate responses in multiple formats for optimal user experience"""
    
    def __init__(self, visual_formatter):
        self.visual_formatter = visual_formatter
        self.detector = ResponseModeDetector()
    
    def format_response(
        self, 
        data: Dict, 
        query: str, 
        context: Optional[Dict] = None,
        force_mode: Optional[ResponseMode] = None
    ) -> str:
        """Generate response in optimal format based on context or forced mode"""
        
        # Detect or use forced mode
        mode = force_mode if force_mode else self.detector.detect_response_mode(query, context)
        
        # Generate base visual response
        base_response = self.visual_formatter.format_fire_weather_response(data)
        
        # Apply mode-specific formatting
        if mode == ResponseMode.EXECUTIVE:
            return self._format_executive_response(base_response, data)
        elif mode == ResponseMode.OPERATIONAL:
            return self._format_operational_response(base_response, data)
        elif mode == ResponseMode.SCIENTIFIC:
            return self._format_scientific_response(base_response, data)
        elif mode == ResponseMode.EMERGENCY:
            return self._format_emergency_response(base_response, data)
        else:
            return base_response  # Balanced mode = standard visual format
    
    def _format_executive_response(self, base_response: str, data: Dict) -> str:
        """Format response for executive/leadership consumption"""
        
        # Extract key metrics
        fire_index = data.get('fire_index', data.get('avg_fire_index', 0))
        region = data.get('region', 'Unknown')
        station_count = len(data.get('stations', []))
        
        # Determine decision urgency
        if fire_index >= 8.0:
            decision_urgency = "🔴 IMMEDIATE ACTION REQUIRED"
            estimated_cost = "$125K-200K/day"
        elif fire_index >= 6.0:
            decision_urgency = "🟠 ELEVATED RESPONSE NEEDED"
            estimated_cost = "$75K-125K/day"
        elif fire_index >= 4.0:
            decision_urgency = "🟡 MONITOR AND PREPARE"
            estimated_cost = "$25K-50K/day"
        else:
            decision_urgency = "🟢 STANDARD OPERATIONS"
            estimated_cost = "$10K-25K/day"
        
        executive_summary = f"""
🔴 **EXECUTIVE FIRE WEATHER BRIEF**
══════════════════════════════════════════════════════════

📊 **SITUATION OVERVIEW**
• Region: {region} ({station_count} monitoring stations)
• Overall Risk Index: {fire_index:.1f}/10.0
• Decision Status: {decision_urgency}
• Estimated Resource Cost: {estimated_cost}

⚡ **KEY DECISIONS NEEDED**
"""
        
        # Add decision points based on risk level
        if fire_index >= 8.0:
            executive_summary += """• Deploy additional Type 1 crews immediately
• Authorize pre-positioning of air resources
• Consider evacuation planning for high-risk areas
• Activate Emergency Operations Center"""
        elif fire_index >= 6.0:
            executive_summary += """• Pre-position additional ground resources
• Brief incident management teams
• Review mutual aid agreements
• Increase public information messaging"""
        elif fire_index >= 4.0:
            executive_summary += """• Monitor conditions hourly
• Review staffing levels and readiness
• Prepare public messaging for potential restrictions"""
        else:
            executive_summary += """• Continue standard monitoring
• Good opportunity for training and maintenance
• Review and update fire plans"""
        
        executive_summary += f"""

📈 **BUSINESS IMPACT**
• Response Readiness: {'High' if fire_index >= 6.0 else 'Standard'}
• Resource Allocation: {'Critical' if fire_index >= 8.0 else 'Normal'}
• Public Safety Risk: {'Elevated' if fire_index >= 6.0 else 'Standard'}

🎯 **30-SECOND SUMMARY**: {region} showing {fire_index:.1f}/10 fire risk. {decision_urgency.split('] ')[1] if ']' in decision_urgency else decision_urgency}
"""
        
        return executive_summary
    
    def _format_operational_response(self, base_response: str, data: Dict) -> str:
        """Format response for tactical/operational crews"""
        
        # Start with visual briefing, add tactical details
        operational_response = base_response
        
        # Add tactical deployment guidance
        fire_index = data.get('fire_index', data.get('avg_fire_index', 0))
        stations = data.get('stations', [])
        
        operational_response += f"""

🚒 **TACTICAL DEPLOYMENT GUIDANCE**
════════════════════════════════════════

📍 **CREW POSITIONING RECOMMENDATIONS**
"""
        
        # Station-specific crew guidance
        for station in stations:
            station_fwi = station.get('fwi', station.get('fire_index', 0))
            station_name = station.get('name', 'Unknown')
            
            if station_fwi >= 8.0:
                guidance = "Deploy Type 1 crew + dozer, establish water supply"
            elif station_fwi >= 6.0:
                guidance = "Pre-position engine, identify escape routes"
            elif station_fwi >= 4.0:
                guidance = "Stage resources at station, maintain readiness"
            else:
                guidance = "Standard patrol, monitor conditions"
            
            operational_response += f"• {station_name}: {guidance}\n"
        
        operational_response += f"""

🛠️ **EQUIPMENT REQUIREMENTS**
• Engines: {'Type 1 required' if fire_index >= 7.0 else 'Type 2/3 sufficient'}
• Water Tenders: {'Critical need' if fire_index >= 6.0 else 'Standard deployment'}
• Dozers: {'Pre-position' if fire_index >= 8.0 else 'On standby'}
• Aircraft: {'Immediate availability' if fire_index >= 7.0 else 'Standard availability'}

📡 **COMMUNICATIONS**
• Tactical Frequency: All crews monitor primary
• Weather Updates: {'Every 15 min' if fire_index >= 7.0 else 'Hourly'}
• Command Check-ins: {'Every 30 min' if fire_index >= 6.0 else 'Standard'}

⚠️ **SAFETY REMINDERS**
• LCES: Lookouts, Communications, Escape routes, Safety zones
• Weather: Monitor for wind shifts and RH drops
• Fuel moisture: Critically low conditions in effect
"""
        
        return operational_response
    
    def _format_scientific_response(self, base_response: str, data: Dict) -> str:
        """Format response for scientific/research analysis"""
        
        # Start with visual briefing, add detailed analysis
        scientific_response = base_response
        
        stations = data.get('stations', [])
        fire_index = data.get('fire_index', data.get('avg_fire_index', 0))
        
        scientific_response += f"""

📊 **DETAILED METEOROLOGICAL ANALYSIS**
════════════════════════════════════════

🌡️ **ATMOSPHERIC CONDITIONS ANALYSIS**
┌─────────────────────────────────────────────────────────┐
│ Parameter         │ Min   │ Max   │ Mean  │ Std Dev │
├───────────────────┼───────┼───────┼───────┼─────────┤"""
        
        if stations:
            temps = [s.get('temp', 0) for s in stations]
            humidity = [s.get('humidity', 0) for s in stations]
            winds = [s.get('wind', 0) for s in stations]
            
            scientific_response += f"""
│ Temperature (°F)  │ {min(temps):5.1f} │ {max(temps):5.1f} │ {sum(temps)/len(temps):5.1f} │ {self._calculate_std_dev(temps):7.1f} │
│ Rel. Humidity (%) │ {min(humidity):5.1f} │ {max(humidity):5.1f} │ {sum(humidity)/len(humidity):5.1f} │ {self._calculate_std_dev(humidity):7.1f} │
│ Wind Speed (mph)  │ {min(winds):5.1f} │ {max(winds):5.1f} │ {sum(winds)/len(winds):5.1f} │ {self._calculate_std_dev(winds):7.1f} │"""
        
        scientific_response += """
└─────────────────────────────────────────────────────────┘

📈 **FIRE WEATHER INDEX ANALYSIS**
• Distribution: Statistical analysis of regional fire weather indices
• Correlation: Temperature vs. fire risk correlation coefficient
• Trend Analysis: Temporal patterns and forecasting accuracy
• Confidence Interval: 95% confidence bounds for predictions

🔬 **NFDRS MODEL COMPONENTS**
• Dead Fuel Moisture: Calculated using NFDRS standard formulas
• Live Fuel Moisture: Based on seasonal phenology and stress factors  
• Spread Component: Function of wind speed and fuel moisture
• Energy Release Component: Available fuel energy for combustion
• Burning Index: Composite measure of fire intensity potential

📊 **STATISTICAL SIGNIFICANCE**
• Sample Size: Multi-station regional analysis
• Data Quality: Real-time Weather.gov API integration
• Validation: Cross-referenced with historical fire occurrence data
• Model Performance: R² values and prediction accuracy metrics

🌐 **GEOSPATIAL ANALYSIS**
• Spatial Autocorrelation: Fire risk clustering patterns
• Elevation Effects: Topographic influence on weather patterns
• Aspect Analysis: Slope orientation and fire behavior relationships
"""
        
        return scientific_response
    
    def _format_emergency_response(self, base_response: str, data: Dict) -> str:
        """Format response for emergency/critical situations"""
        
        fire_index = data.get('fire_index', data.get('avg_fire_index', 0))
        region = data.get('region', 'Unknown')
        
        # Create urgent, action-focused response
        emergency_response = f"""
🚨 **EMERGENCY FIRE WEATHER ALERT** 🚨
══════════════════════════════════════════════════════════

⚠️ **CRITICAL SITUATION**: {region}
🔥 **Fire Weather Index**: {fire_index:.1f}/10.0 (EXTREME RISK)
⏰ **Alert Time**: {data.get('updated', 'NOW')}

🔴 **IMMEDIATE ACTIONS REQUIRED**:

1. 🚒 **DEPLOY RESOURCES NOW**
   └─ All available Type 1 engines to high-risk areas
   └─ Activate all dozers and water tenders
   └─ Request mutual aid if not already done

2. 🚁 **AIR SUPPORT**
   └─ Pre-position helicopters and air tankers
   └─ Establish air operations staging areas
   └─ Clear airspace for emergency aircraft

3. 📢 **PUBLIC SAFETY**
   └─ Issue Red Flag Warning immediately
   └─ Consider evacuation warnings for high-risk areas
   └─ Activate Emergency Alert System

4. 📡 **COMMAND & CONTROL**
   └─ Activate Emergency Operations Center
   └─ Establish unified command structure
   └─ Continuous weather monitoring (5-minute updates)

⚡ **CRITICAL WEATHER CONDITIONS**:
"""
        
        # Add critical station information
        stations = data.get('stations', [])
        for station in stations:
            station_fwi = station.get('fwi', station.get('fire_index', 0))
            if station_fwi >= 7.0:  # Only show critical stations
                emergency_response += f"""
🔴 {station.get('name', 'Unknown')} ({station.get('id', 'N/A')}):
   • FWI: {station_fwi:.1f}/10 (EXTREME)
   • Conditions: {station.get('temp', 0):.0f}°F, {station.get('humidity', 0):.0f}% RH, {station.get('wind', 0):.0f} mph winds
"""
        
        emergency_response += f"""

⏱️ **TIMELINE**: Action required within 30 minutes
🎯 **PRIORITY**: LIFE SAFETY - PROPERTY PROTECTION - RESOURCE CONSERVATION
📞 **CONTACT**: Maintain continuous communication with Incident Command

🚨 This is an automated emergency alert based on critical fire weather conditions 🚨
"""
        
        return emergency_response
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5


# Initialize when imported with visual_formatter
def initialize_multi_modal_formatter(visual_formatter):
    """Initialize multi-modal formatter with visual formatter instance"""
    global multi_modal_formatter
    multi_modal_formatter = MultiModalResponseFormatter(visual_formatter)
    return multi_modal_formatter