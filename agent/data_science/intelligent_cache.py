"""
Intelligent Response Caching System
Provides smart caching with freshness indicators and background refresh capabilities
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, Callable, Any
import threading


class IntelligentResponseCache:
    """Cache responses with freshness tracking and visual indicators"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'background_refreshes': 0,
            'total_requests': 0
        }
        self.refresh_lock = threading.Lock()
        
        # TTL configurations by data type (in minutes)
        self.ttl_config = {
            'weather': 10,     # Real-time weather: 10 minutes (was 5)
            'forecast': 120,   # Forecasts: 2 hours (was 60)
            'fire_danger': 15, # Fire danger calculations: 15 minutes (was 2)
            'historical': 240, # Historical data: 4 hours (was 2)
            'default': 60      # Default: 60 minutes (was 30)
        }
    
    def _generate_cache_key(self, query: str, data_type: str = 'default') -> str:
        """Generate cache key from query and data type"""
        cache_string = f"{data_type}:{query}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _determine_freshness(self, cached_data: Dict) -> str:
        """Determine freshness level of cached data"""
        age_minutes = (datetime.now() - cached_data['timestamp']).total_seconds() / 60
        
        if age_minutes < 1:
            return 'live'  # Less than 1 minute = live
        elif age_minutes < 5:
            return 'fresh'  # Less than 5 minutes = fresh
        elif age_minutes < 30:
            return 'cached'  # Less than 30 minutes = cached
        else:
            return 'stale'  # Older than 30 minutes = stale
    
    def _is_expired(self, cached_data: Dict, data_type: str) -> bool:
        """Check if cached data has expired based on TTL"""
        ttl_minutes = self.ttl_config.get(data_type, self.ttl_config['default'])
        age_minutes = (datetime.now() - cached_data['timestamp']).total_seconds() / 60
        return age_minutes > ttl_minutes
    
    async def get_or_fetch_with_freshness(
        self, 
        query: str, 
        fetch_func: Callable,
        data_type: str = 'default',
        **fetch_kwargs
    ) -> Tuple[str, str]:
        """Get cached response with freshness indicator or fetch fresh data"""
        
        self.cache_stats['total_requests'] += 1
        cache_key = self._generate_cache_key(query, data_type)
        cached_data = self.cache.get(cache_key)
        
        # Check if we have valid cached data
        if cached_data and not self._is_expired(cached_data, data_type):
            self.cache_stats['hits'] += 1
            
            freshness = self._determine_freshness(cached_data)
            
            # Schedule background refresh for stale data
            if freshness == 'stale':
                asyncio.create_task(
                    self._background_refresh(cache_key, fetch_func, data_type, **fetch_kwargs)
                )
            
            return cached_data['response'], freshness
        
        # Cache miss or expired data - fetch fresh
        self.cache_stats['misses'] += 1
        response = await fetch_func(**fetch_kwargs)
        
        # Cache the fresh response
        self._cache_response(cache_key, response, data_type)
        
        return response, 'live'
    
    def _cache_response(self, cache_key: str, response: str, data_type: str = 'default'):
        """Cache a response with metadata"""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now(),
            'data_type': data_type,
            'access_count': 1
        }
    
    async def _background_refresh(
        self, 
        cache_key: str, 
        fetch_func: Callable,
        data_type: str,
        **fetch_kwargs
    ):
        """Background refresh of stale cache data"""
        
        # Prevent multiple background refreshes of same data
        with self.refresh_lock:
            # Check if data was already refreshed by another thread
            cached_data = self.cache.get(cache_key)
            if cached_data and not self._is_expired(cached_data, data_type):
                return
            
            try:
                # Fetch fresh data in background
                fresh_response = await fetch_func(**fetch_kwargs)
                
                # Update cache with fresh data
                self._cache_response(cache_key, fresh_response, data_type)
                
                self.cache_stats['background_refreshes'] += 1
                
            except Exception as e:
                # Log error but don't crash - keep using stale data
                print(f"Background cache refresh failed: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        total = self.cache_stats['total_requests']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'hit_rate_percent': round(hit_rate, 1),
            'total_requests': total,
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'background_refreshes': self.cache_stats['background_refreshes'],
            'cached_items': len(self.cache)
        }
    
    def clear_expired_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self.cache.items():
            data_type = data.get('data_type', 'default')
            ttl_minutes = self.ttl_config.get(data_type, self.ttl_config['default'])
            
            if (current_time - data['timestamp']).total_seconds() / 60 > ttl_minutes:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries matching pattern"""
        if pattern is None:
            # Clear entire cache
            cleared_count = len(self.cache)
            self.cache.clear()
            return cleared_count
        
        # Clear entries matching pattern
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.cache[key]
        
        return len(keys_to_remove)


class CachedFireWeatherAgent:
    """Wrapper for fire weather agent with intelligent caching"""
    
    def __init__(self, agent_instance):
        self.agent = agent_instance
        self.cache = IntelligentResponseCache()
    
    async def get_real_time_fire_weather_conditions_cached(
        self, 
        region: str,
        station_ids: Optional[list] = None
    ) -> str:
        """Get real-time fire weather with intelligent caching"""
        
        # Create query signature for caching
        query_sig = f"weather:{region}:{':'.join(station_ids) if station_ids else 'auto'}"
        
        # Get cached or fresh data
        response, freshness = await self.cache.get_or_fetch_with_freshness(
            query=query_sig,
            fetch_func=self._fetch_weather_data,
            data_type='weather',
            region=region,
            station_ids=station_ids
        )
        
        return response
    
    async def _fetch_weather_data(self, region: str, station_ids: Optional[list] = None) -> str:
        """Fetch fresh weather data from agent"""
        # This would call the actual agent method
        return await self.agent.get_real_time_fire_weather_conditions(region, station_ids)
    
    async def get_fire_weather_forecast_cached(
        self,
        station_id: int,
        days_ahead: int = 1
    ) -> str:
        """Get fire weather forecast with intelligent caching"""
        
        query_sig = f"forecast:{station_id}:{days_ahead}"
        
        response, freshness = await self.cache.get_or_fetch_with_freshness(
            query=query_sig,
            fetch_func=self._fetch_forecast_data,
            data_type='forecast',
            station_id=station_id,
            days_ahead=days_ahead
        )
        
        return response
    
    async def _fetch_forecast_data(self, station_id: int, days_ahead: int) -> str:
        """Fetch fresh forecast data from agent"""
        return await self.agent.get_fire_weather_forecast(station_id, days_ahead)
    
    async def calculate_fire_danger_cached(
        self,
        temperature: float,
        relative_humidity: float,
        wind_speed: float,
        precipitation: float = 0.0
    ) -> str:
        """Calculate fire danger with caching (short TTL since it's instant calculation)"""
        
        # Fire danger calculations are instant, so cache briefly to avoid redundant calls
        query_sig = f"fire_danger:{temperature}:{relative_humidity}:{wind_speed}:{precipitation}"
        
        response, freshness = await self.cache.get_or_fetch_with_freshness(
            query=query_sig,
            fetch_func=self._fetch_fire_danger,
            data_type='fire_danger',
            temperature=temperature,
            relative_humidity=relative_humidity,
            wind_speed=wind_speed,
            precipitation=precipitation
        )
        
        return response
    
    async def _fetch_fire_danger(
        self,
        temperature: float,
        relative_humidity: float,
        wind_speed: float,
        precipitation: float = 0.0
    ) -> str:
        """Fetch fresh fire danger calculation"""
        return await self.agent.calculate_fire_danger(
            temperature, relative_humidity, wind_speed, precipitation
        )
    
    def get_cache_performance_report(self) -> str:
        """Generate cache performance report"""
        stats = self.cache.get_cache_stats()
        
        report = f"""
📊 **CACHE PERFORMANCE REPORT**
════════════════════════════════════════

🎯 **Hit Rate**: {stats['hit_rate_percent']}% (Target: >70%)
📈 **Total Requests**: {stats['total_requests']}
✅ **Cache Hits**: {stats['cache_hits']}
❌ **Cache Misses**: {stats['cache_misses']}
🔄 **Background Refreshes**: {stats['background_refreshes']}
💾 **Cached Items**: {stats['cached_items']}

🚀 **PERFORMANCE BENEFITS**:
• Faster response times for repeated queries
• Reduced Weather.gov API load
• Background refresh maintains data freshness
• Visual freshness indicators for transparency

🔧 **TTL CONFIGURATION**:
• Real-time weather: 5 minutes
• Forecasts: 60 minutes  
• Fire calculations: 2 minutes
• Historical data: 120 minutes
"""
        
        return report


# Global cache instance
intelligent_cache = IntelligentResponseCache()