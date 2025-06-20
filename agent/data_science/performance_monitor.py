"""
Performance Monitoring System for RisenOne Fire Risk Agent
Tracks response times, cache performance, and query patterns
"""

import time
import json
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return {
            'metric_name': self.metric_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }

@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""
    metric_name: str
    count: int
    mean: float
    median: float
    p95: float
    p99: float
    min_value: float
    max_value: float
    period_start: datetime
    period_end: datetime

class PerformanceMonitor:
    """
    Central performance monitoring system
    Tracks metrics, calculates statistics, and provides alerts
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.thresholds = {
            'response_time': {
                'p50_target': 0.5,
                'p95_target': 2.0,
                'p99_target': 3.0,
                'alert_threshold': 5.0
            },
            'cache_hit_rate': {
                'target': 0.95,
                'warning': 0.90,
                'alert': 0.85
            },
            'error_rate': {
                'target': 0.01,
                'warning': 0.03,
                'alert': 0.05
            }
        }
        self.query_distribution = defaultdict(int)
        self._start_time = datetime.now()
        
    def record_metric(self, metric_name: str, value: float, metadata: Dict = None):
        """Record a single metric value"""
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.metrics[metric_name].append(metric)
        
        # Check thresholds
        self._check_threshold(metric_name, value)
        
        # Log if debugging
        logger.debug(f"Recorded {metric_name}: {value:.3f}")
        
    def record_query_type(self, query_type: str):
        """Track distribution of query types"""
        self.query_distribution[query_type] += 1
        
    def _check_threshold(self, metric_name: str, value: float):
        """Check if metric exceeds thresholds and log warnings"""
        if metric_name == 'response_time' and value > self.thresholds['response_time']['alert_threshold']:
            logger.warning(f"Response time {value:.2f}s exceeds alert threshold")
        elif metric_name == 'cache_hit_rate' and value < self.thresholds['cache_hit_rate']['alert']:
            logger.warning(f"Cache hit rate {value:.2%} below alert threshold")
            
    def get_stats(self, metric_name: str, time_window: timedelta = None) -> Optional[PerformanceStats]:
        """Calculate statistics for a metric over a time window"""
        if metric_name not in self.metrics:
            return None
            
        metrics = self.metrics[metric_name]
        
        # Filter by time window if specified
        if time_window:
            cutoff = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp >= cutoff]
            
        if not metrics:
            return None
            
        values = [m.value for m in metrics]
        values.sort()
        
        return PerformanceStats(
            metric_name=metric_name,
            count=len(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            p95=values[int(len(values) * 0.95)] if len(values) > 20 else max(values),
            p99=values[int(len(values) * 0.99)] if len(values) > 100 else max(values),
            min_value=min(values),
            max_value=max(values),
            period_start=metrics[0].timestamp,
            period_end=metrics[-1].timestamp
        )
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics summary"""
        # Calculate uptime
        uptime = datetime.now() - self._start_time
        
        # Get response time stats
        response_stats = self.get_stats('response_time', timedelta(minutes=5))
        
        # Calculate cache hit rate from recent metrics
        cache_metrics = self.metrics.get('cache_hit', [])[-100:]  # Last 100 queries
        cache_hit_rate = sum(m.value for m in cache_metrics) / len(cache_metrics) if cache_metrics else 0
        
        # Calculate error rate
        error_metrics = self.metrics.get('error', [])[-100:]
        error_rate = sum(m.value for m in error_metrics) / len(error_metrics) if error_metrics else 0
        
        # Query distribution
        total_queries = sum(self.query_distribution.values())
        distribution = {
            query_type: count / total_queries if total_queries > 0 else 0
            for query_type, count in self.query_distribution.items()
        }
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_queries': total_queries,
            'response_time': {
                'p50': response_stats.median if response_stats else None,
                'p95': response_stats.p95 if response_stats else None,
                'p99': response_stats.p99 if response_stats else None,
                'mean': response_stats.mean if response_stats else None
            },
            'cache_hit_rate': cache_hit_rate,
            'error_rate': error_rate,
            'query_distribution': distribution,
            'timestamp': datetime.now().isoformat()
        }
        
    def generate_report(self) -> str:
        """Generate a human-readable performance report"""
        metrics = self.get_current_metrics()
        
        report = f"""
🎯 Performance Report - RisenOne Fire Risk Agent
================================================

📊 System Uptime: {metrics['uptime_seconds'] / 3600:.1f} hours
📈 Total Queries: {metrics['total_queries']:,}

⚡ Response Times (last 5 minutes):
  • Median (p50): {metrics['response_time']['p50']:.3f}s
  • 95th percentile: {metrics['response_time']['p95']:.3f}s  
  • 99th percentile: {metrics['response_time']['p99']:.3f}s
  • Average: {metrics['response_time']['mean']:.3f}s

💾 Cache Performance:
  • Hit Rate: {metrics['cache_hit_rate']:.1%}

❌ Error Rate: {metrics['error_rate']:.2%}

📊 Query Distribution:
"""
        for query_type, percentage in metrics['query_distribution'].items():
            report += f"  • {query_type}: {percentage:.1%}\n"
            
        report += f"\n⏰ Report Generated: {metrics['timestamp']}"
        
        return report
        
    def export_metrics(self, filepath: str):
        """Export all metrics to JSON file"""
        export_data = {
            'metrics': {
                name: [m.to_dict() for m in metrics]
                for name, metrics in self.metrics.items()
            },
            'query_distribution': dict(self.query_distribution),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Exported metrics to {filepath}")

# Singleton instance
_monitor = PerformanceMonitor()

# Decorator for easy performance tracking
def track_performance(metric_name: str = 'response_time'):
    """
    Decorator to track function execution time
    
    Usage:
        @track_performance('nfdrs_calculation')
        def calculate_fire_danger(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record successful execution
                _monitor.record_metric(metric_name, duration, {
                    'function': func.__name__,
                    'success': True
                })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failed execution
                _monitor.record_metric(metric_name, duration, {
                    'function': func.__name__,
                    'success': False,
                    'error': str(e)
                })
                
                # Also record error
                _monitor.record_metric('error', 1.0, {
                    'function': func.__name__,
                    'error_type': type(e).__name__
                })
                
                raise
                
        return wrapper
    return decorator

# Convenience functions
def record_cache_hit(hit: bool):
    """Record a cache hit or miss"""
    _monitor.record_metric('cache_hit', 1.0 if hit else 0.0)
    
def record_query_type(query_type: str):
    """Record the type of query being processed"""
    _monitor.record_query_type(query_type)
    
def get_performance_monitor() -> PerformanceMonitor:
    """Get the singleton performance monitor instance"""
    return _monitor

# Example usage in agent.py:
# from performance_monitor import track_performance, record_cache_hit, record_query_type
#
# @track_performance('query_processing')
# async def process_query(self, query: str):
#     # Classify query type
#     query_type = self.classify_query_type(query)
#     record_query_type(query_type)
#     
#     # Check cache
#     if cached := self.cache.get(query):
#         record_cache_hit(True)
#         return cached
#     
#     record_cache_hit(False)
#     # ... process query ...