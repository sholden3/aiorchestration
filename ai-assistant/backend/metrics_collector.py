"""
Business Context: System metrics collection for monitoring and optimization
Architecture Pattern: Observer pattern for metrics aggregation
Performance Requirements: Minimal overhead, async collection
Business Logic: Track token usage, cache performance, response times
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects and aggregates system performance metrics
    Business Value: Monitor token savings, cache effectiveness, system health
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics collector with rolling window
        """
        self.window_size = window_size
        
        # Rolling windows for metrics
        self.response_times = deque(maxlen=window_size)
        self.cache_hits = deque(maxlen=window_size)
        self.token_usage = deque(maxlen=window_size)
        
        # Cumulative metrics
        self.total_cache_hits = 0
        self.total_cache_misses = 0
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
        self.total_requests = 0
        
        # Persona metrics
        self.persona_usage = {}
        
        # Time-based metrics
        self.hourly_metrics = []
        self.start_time = datetime.now()
        
    def record_cache_hit(self):
        """Record a cache hit"""
        self.total_cache_hits += 1
        self.cache_hits.append(1)
        
    def record_cache_miss(self):
        """Record a cache miss"""
        self.total_cache_misses += 1
        self.cache_hits.append(0)
        
    def record_response_time(self, time_ms: int):
        """Record response time in milliseconds"""
        self.response_times.append(time_ms)
        self.total_requests += 1
        
    def record_token_usage(self, used: int, saved: int = 0):
        """Record token usage"""
        self.total_tokens_used += used
        self.total_tokens_saved += saved
        self.token_usage.append({'used': used, 'saved': saved})
        
    def record_persona_usage(self, persona: str):
        """Record persona usage"""
        if persona not in self.persona_usage:
            self.persona_usage[persona] = 0
        self.persona_usage[persona] += 1
        
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.total_cache_hits + self.total_cache_misses
        if total == 0:
            return 0.0
        return (self.total_cache_hits / total) * 100
        
    def get_average_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
        
    def get_p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]
        
    def get_token_savings_rate(self) -> float:
        """Calculate token savings percentage"""
        if self.total_tokens_used == 0:
            return 0.0
        
        total_without_cache = self.total_tokens_used + self.total_tokens_saved
        if total_without_cache == 0:
            return 0.0
            
        return (self.total_tokens_saved / total_without_cache) * 100
        
    def get_persona_distribution(self) -> Dict[str, float]:
        """Get percentage distribution of persona usage"""
        total = sum(self.persona_usage.values())
        if total == 0:
            return {}
            
        return {
            persona: (count / total) * 100
            for persona, count in self.persona_usage.items()
        }
        
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary
        Business Value: Dashboard metrics for monitoring
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': int(uptime),
            'total_requests': self.total_requests,
            'requests_per_minute': (self.total_requests / uptime * 60) if uptime > 0 else 0,
            'cache': {
                'hit_rate': round(self.get_cache_hit_rate(), 2),
                'total_hits': self.total_cache_hits,
                'total_misses': self.total_cache_misses
            },
            'response_times': {
                'average_ms': round(self.get_average_response_time(), 2),
                'p95_ms': round(self.get_p95_response_time(), 2),
                'min_ms': min(self.response_times) if self.response_times else 0,
                'max_ms': max(self.response_times) if self.response_times else 0
            },
            'tokens': {
                'total_used': self.total_tokens_used,
                'total_saved': self.total_tokens_saved,
                'savings_rate': round(self.get_token_savings_rate(), 2),
                'estimated_cost_saved': round(self.total_tokens_saved * 0.00002, 2)  # Rough estimate
            },
            'personas': self.get_persona_distribution()
        }
        
    async def start_collection(self):
        """
        Start periodic metrics collection
        Runs every minute to aggregate metrics
        """
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Snapshot current metrics
                snapshot = {
                    'timestamp': datetime.now().isoformat(),
                    'cache_hit_rate': self.get_cache_hit_rate(),
                    'avg_response_time': self.get_average_response_time(),
                    'token_savings_rate': self.get_token_savings_rate(),
                    'requests_per_minute': self.total_requests / 1 if self.total_requests > 0 else 0
                }
                
                self.hourly_metrics.append(snapshot)
                
                # Keep only last 60 minutes
                if len(self.hourly_metrics) > 60:
                    self.hourly_metrics.pop(0)
                    
                logger.debug(f"Metrics snapshot: {snapshot}")
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                
    def reset(self):
        """Reset all metrics"""
        self.response_times.clear()
        self.cache_hits.clear()
        self.token_usage.clear()
        self.total_cache_hits = 0
        self.total_cache_misses = 0
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
        self.total_requests = 0
        self.persona_usage.clear()
        self.hourly_metrics.clear()
        self.start_time = datetime.now()
        
        logger.info("Metrics reset")