"""
@fileoverview Production hardening stress test suite for system validation
@author Sam Martinez v3.2.0 & Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Comprehensive stress testing framework
@responsibility Validate system stability and performance under production load
@dependencies aiohttp, asyncio, websockets, json, time
@integration_points Backend API endpoints, WebSocket server, database, cache
@testing_strategy Concurrent load testing, memory stress, connection limits, failure recovery
@governance Ensures production readiness and performance standards

Business Logic Summary:
- Test 100+ concurrent WebSocket connections
- Validate API response times under load
- Stress test cache performance
- Test database connection pooling
- Measure memory usage patterns
- Validate graceful degradation

Architecture Integration:
- Phase 4 production hardening component
- Tests all backend subsystems
- Validates resource management
- Ensures scalability requirements
- Monitors system health under stress

Sarah's Framework Check:
- What breaks first: WebSocket connection limits at 100+
- How we know: Connection refused errors and metrics
- Plan B: Connection pooling and rate limiting
  - 1000+ requests/second API throughput
  - 8-hour stability without memory leaks
  - <500ms p95 response time under load
"""

import asyncio
import time
import random
import psutil
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import websockets
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class StressTestMetrics:
    """Metrics collected during stress testing"""
    test_name: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    memory_samples: List[float]
    cpu_samples: List[float]
    errors: List[str]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def p50_response_time(self) -> float:
        """Calculate 50th percentile response time"""
        if not self.response_times:
            return 0
        return statistics.median(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    @property
    def p99_response_time(self) -> float:
        """Calculate 99th percentile response time"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    @property
    def avg_memory_mb(self) -> float:
        """Average memory usage in MB"""
        if not self.memory_samples:
            return 0
        return statistics.mean(self.memory_samples)
    
    @property
    def peak_memory_mb(self) -> float:
        """Peak memory usage in MB"""
        if not self.memory_samples:
            return 0
        return max(self.memory_samples)
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        return f"""
=== Stress Test Report: {self.test_name} ===
Duration: {self.duration_seconds:.2f} seconds
Total Requests: {self.total_requests:,}
Successful: {self.successful_requests:,} ({self.success_rate:.2f}%)
Failed: {self.failed_requests:,}

Response Times:
  P50: {self.p50_response_time:.3f}s
  P95: {self.p95_response_time:.3f}s
  P99: {self.p99_response_time:.3f}s

Resource Usage:
  Avg Memory: {self.avg_memory_mb:.2f} MB
  Peak Memory: {self.peak_memory_mb:.2f} MB
  
Unique Errors: {len(set(self.errors))}
"""


class WebSocketStressTester:
    """Stress test WebSocket connections"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.metrics = None
        self.connections = []
    
    async def create_connection(self, connection_id: int) -> websockets.WebSocketClientProtocol:
        """Create a single WebSocket connection"""
        try:
            ws = await websockets.connect(f"{self.base_url}/ws")
            await ws.send(json.dumps({
                "type": "auth",
                "user_id": f"stress_user_{connection_id}"
            }))
            return ws
        except Exception as e:
            logger.error(f"Failed to create connection {connection_id}: {e}")
            raise
    
    async def stress_test_connections(self, num_connections: int = 100) -> StressTestMetrics:
        """Test WebSocket connection limits and stability"""
        logger.info(f"Starting WebSocket stress test with {num_connections} connections")
        
        metrics = StressTestMetrics(
            test_name="WebSocket Connection Stress",
            duration_seconds=0,
            total_requests=num_connections,
            successful_requests=0,
            failed_requests=0,
            response_times=[],
            memory_samples=[],
            cpu_samples=[],
            errors=[]
        )
        
        start_time = time.time()
        
        # Create connections concurrently
        tasks = []
        for i in range(num_connections):
            tasks.append(self.create_connection(i))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                metrics.failed_requests += 1
                metrics.errors.append(str(result))
            else:
                metrics.successful_requests += 1
                self.connections.append(result)
        
        # Keep connections alive for 10 seconds
        logger.info(f"Established {len(self.connections)} connections, holding for 10s")
        await asyncio.sleep(10)
        
        # Send messages through all connections
        message_tasks = []
        for ws in self.connections:
            if not ws.closed:
                message_tasks.append(ws.send(json.dumps({
                    "type": "ping",
                    "timestamp": time.time()
                })))
        
        await asyncio.gather(*message_tasks, return_exceptions=True)
        
        # Clean up connections
        for ws in self.connections:
            try:
                await ws.close()
            except:
                pass
        
        metrics.duration_seconds = time.time() - start_time
        self.metrics = metrics
        
        return metrics
    
    async def stress_test_broadcast(self, num_connections: int = 50, messages_per_second: int = 100) -> StressTestMetrics:
        """Test message broadcasting performance"""
        logger.info(f"Starting broadcast stress test: {num_connections} connections, {messages_per_second} msg/s")
        
        metrics = StressTestMetrics(
            test_name="WebSocket Broadcast Stress",
            duration_seconds=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            response_times=[],
            memory_samples=[],
            cpu_samples=[],
            errors=[]
        )
        
        start_time = time.time()
        
        # Establish connections
        for i in range(num_connections):
            try:
                ws = await self.create_connection(i)
                self.connections.append(ws)
            except Exception as e:
                metrics.errors.append(str(e))
        
        logger.info(f"Established {len(self.connections)} connections for broadcast test")
        
        # Send messages at specified rate for 30 seconds
        test_duration = 30
        message_interval = 1.0 / messages_per_second
        end_time = time.time() + test_duration
        
        while time.time() < end_time:
            message_start = time.time()
            
            # Broadcast to all connections
            tasks = []
            for ws in self.connections:
                if not ws.closed:
                    tasks.append(ws.send(json.dumps({
                        "type": "broadcast",
                        "data": f"Message at {time.time()}",
                        "sequence": metrics.total_requests
                    })))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            metrics.total_requests += len(tasks)
            for result in results:
                if isinstance(result, Exception):
                    metrics.failed_requests += 1
                    metrics.errors.append(str(result))
                else:
                    metrics.successful_requests += 1
            
            # Track response time
            response_time = time.time() - message_start
            metrics.response_times.append(response_time)
            
            # Sleep to maintain rate
            sleep_time = message_interval - response_time
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Cleanup
        for ws in self.connections:
            try:
                await ws.close()
            except:
                pass
        
        metrics.duration_seconds = time.time() - start_time
        self.metrics = metrics
        
        return metrics


class APIStressTester:
    """Stress test REST API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.metrics = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> tuple:
        """Make a single API request and measure response time"""
        start_time = time.time()
        try:
            async with self.session.request(method, f"{self.base_url}{endpoint}", json=data) as response:
                await response.text()
                response_time = time.time() - start_time
                return response.status, response_time, None
        except Exception as e:
            response_time = time.time() - start_time
            return 0, response_time, str(e)
    
    async def stress_test_endpoint(self, endpoint: str, requests_per_second: int = 100, duration_seconds: int = 60) -> StressTestMetrics:
        """Stress test a specific endpoint"""
        logger.info(f"Starting API stress test: {endpoint} at {requests_per_second} req/s for {duration_seconds}s")
        
        metrics = StressTestMetrics(
            test_name=f"API Stress: {endpoint}",
            duration_seconds=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            response_times=[],
            memory_samples=[],
            cpu_samples=[],
            errors=[]
        )
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        request_interval = 1.0 / requests_per_second
        
        while time.time() < end_time:
            batch_start = time.time()
            
            # Send batch of requests
            tasks = []
            for _ in range(requests_per_second):
                tasks.append(self.make_request(endpoint))
            
            results = await asyncio.gather(*tasks)
            
            # Process results
            for status, response_time, error in results:
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if error:
                    metrics.failed_requests += 1
                    metrics.errors.append(error)
                elif status == 200:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1
                    metrics.errors.append(f"HTTP {status}")
            
            # Sample system resources
            process = psutil.Process()
            metrics.memory_samples.append(process.memory_info().rss / 1024 / 1024)
            metrics.cpu_samples.append(process.cpu_percent())
            
            # Sleep to maintain rate
            elapsed = time.time() - batch_start
            sleep_time = 1.0 - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        metrics.duration_seconds = time.time() - start_time
        self.metrics = metrics
        
        return metrics


class CacheStressTester:
    """Stress test cache operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = None
    
    async def stress_test_cache(self, operations_per_second: int = 1000, cache_size: int = 10000) -> StressTestMetrics:
        """Test cache performance under heavy load"""
        logger.info(f"Starting cache stress test: {operations_per_second} ops/s, {cache_size} keys")
        
        metrics = StressTestMetrics(
            test_name="Cache Stress Test",
            duration_seconds=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            response_times=[],
            memory_samples=[],
            cpu_samples=[],
            errors=[]
        )
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Pre-populate cache
            logger.info("Pre-populating cache...")
            for i in range(min(100, cache_size)):
                key = f"stress_key_{i}"
                data = {"value": f"data_{i}", "timestamp": time.time()}
                
                try:
                    async with session.post(f"{self.base_url}/cache/{key}", json=data) as response:
                        if response.status == 200:
                            metrics.successful_requests += 1
                        else:
                            metrics.failed_requests += 1
                except Exception as e:
                    metrics.errors.append(str(e))
                    metrics.failed_requests += 1
            
            # Perform mixed read/write operations for 30 seconds
            test_duration = 30
            end_time = time.time() + test_duration
            operation_interval = 1.0 / operations_per_second
            
            logger.info("Starting cache operations...")
            while time.time() < end_time:
                op_start = time.time()
                
                # 80% reads, 20% writes
                if random.random() < 0.8:
                    # Read operation
                    key = f"stress_key_{random.randint(0, cache_size - 1)}"
                    try:
                        async with session.get(f"{self.base_url}/cache/{key}") as response:
                            await response.text()
                            metrics.response_times.append(time.time() - op_start)
                            if response.status == 200:
                                metrics.successful_requests += 1
                            else:
                                metrics.failed_requests += 1
                    except Exception as e:
                        metrics.errors.append(str(e))
                        metrics.failed_requests += 1
                else:
                    # Write operation
                    key = f"stress_key_{random.randint(0, cache_size - 1)}"
                    data = {"value": f"updated_{time.time()}", "timestamp": time.time()}
                    try:
                        async with session.put(f"{self.base_url}/cache/{key}", json=data) as response:
                            metrics.response_times.append(time.time() - op_start)
                            if response.status == 200:
                                metrics.successful_requests += 1
                            else:
                                metrics.failed_requests += 1
                    except Exception as e:
                        metrics.errors.append(str(e))
                        metrics.failed_requests += 1
                
                metrics.total_requests += 1
                
                # Maintain rate
                elapsed = time.time() - op_start
                if elapsed < operation_interval:
                    await asyncio.sleep(operation_interval - elapsed)
        
        metrics.duration_seconds = time.time() - start_time
        self.metrics = metrics
        
        return metrics


class MemoryLeakDetector:
    """Detect memory leaks during extended operation"""
    
    def __init__(self):
        self.memory_samples = []
        self.start_memory = 0
        self.monitoring = False
    
    async def monitor_memory(self, interval_seconds: int = 60, duration_hours: int = 8):
        """Monitor memory usage over extended period"""
        logger.info(f"Starting memory leak detection for {duration_hours} hours")
        
        self.monitoring = True
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        end_time = time.time() + (duration_hours * 3600)
        sample_count = 0
        
        while time.time() < end_time and self.monitoring:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            self.memory_samples.append({
                "timestamp": datetime.now(),
                "memory_mb": current_memory,
                "delta_mb": current_memory - self.start_memory,
                "sample": sample_count
            })
            
            sample_count += 1
            
            # Log every 10 samples
            if sample_count % 10 == 0:
                logger.info(f"Memory sample {sample_count}: {current_memory:.2f} MB (Δ{current_memory - self.start_memory:+.2f} MB)")
            
            # Check for significant leak (>100MB growth per hour)
            if len(self.memory_samples) > 60:  # After first hour
                hourly_growth = (current_memory - self.memory_samples[-60]["memory_mb"])
                if hourly_growth > 100:
                    logger.warning(f"Potential memory leak detected: {hourly_growth:.2f} MB/hour growth")
            
            await asyncio.sleep(interval_seconds)
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze memory samples for leak patterns"""
        if len(self.memory_samples) < 2:
            return {"status": "insufficient_data"}
        
        memory_values = [s["memory_mb"] for s in self.memory_samples]
        
        # Calculate linear regression to detect trend
        n = len(memory_values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(memory_values) / n
        
        numerator = sum((x[i] - x_mean) * (memory_values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Slope represents MB growth per sample
        hourly_growth = slope * 60  # Assuming 1-minute samples
        
        return {
            "status": "leak_detected" if hourly_growth > 10 else "stable",
            "start_memory_mb": self.start_memory,
            "end_memory_mb": memory_values[-1],
            "total_growth_mb": memory_values[-1] - self.start_memory,
            "hourly_growth_mb": hourly_growth,
            "samples_collected": len(self.memory_samples),
            "peak_memory_mb": max(memory_values),
            "recommendation": "Memory leak detected" if hourly_growth > 10 else "Memory usage stable"
        }


async def run_full_stress_suite():
    """Run complete stress testing suite"""
    logger.info("=" * 80)
    logger.info("Starting Phase 4 Production Hardening Stress Tests")
    logger.info("=" * 80)
    
    results = {}
    
    # 1. WebSocket Connection Stress Test
    logger.info("\n[1/5] WebSocket Connection Stress Test")
    ws_tester = WebSocketStressTester()
    ws_metrics = await ws_tester.stress_test_connections(num_connections=100)
    results["websocket_connections"] = ws_metrics
    print(ws_metrics.generate_report())
    
    # 2. WebSocket Broadcast Stress Test
    logger.info("\n[2/5] WebSocket Broadcast Stress Test")
    ws_tester = WebSocketStressTester()
    broadcast_metrics = await ws_tester.stress_test_broadcast(
        num_connections=50,
        messages_per_second=100
    )
    results["websocket_broadcast"] = broadcast_metrics
    print(broadcast_metrics.generate_report())
    
    # 3. API Endpoint Stress Test
    logger.info("\n[3/5] API Endpoint Stress Test")
    async with APIStressTester() as api_tester:
        # Test health endpoint
        health_metrics = await api_tester.stress_test_endpoint(
            "/health",
            requests_per_second=1000,
            duration_seconds=30
        )
        results["api_health"] = health_metrics
        print(health_metrics.generate_report())
        
        # Test agent endpoint
        agent_metrics = await api_tester.stress_test_endpoint(
            "/agent/execute",
            requests_per_second=100,
            duration_seconds=30
        )
        results["api_agent"] = agent_metrics
        print(agent_metrics.generate_report())
    
    # 4. Cache Stress Test
    logger.info("\n[4/5] Cache Stress Test")
    cache_tester = CacheStressTester()
    cache_metrics = await cache_tester.stress_test_cache(
        operations_per_second=500,
        cache_size=1000
    )
    results["cache"] = cache_metrics
    print(cache_metrics.generate_report())
    
    # 5. Short Memory Leak Detection (10 minutes for quick validation)
    logger.info("\n[5/5] Memory Leak Detection (10-minute quick test)")
    leak_detector = MemoryLeakDetector()
    # For production hardening phase, run shorter test
    leak_task = asyncio.create_task(
        leak_detector.monitor_memory(interval_seconds=30, duration_hours=0.167)  # 10 minutes
    )
    
    # Run some operations while monitoring
    await asyncio.sleep(600)  # 10 minutes
    leak_detector.monitoring = False
    leak_results = await leak_task
    results["memory_leak"] = leak_results
    
    print("\n" + "=" * 80)
    print("MEMORY LEAK DETECTION RESULTS")
    print("=" * 80)
    print(json.dumps(leak_results, indent=2, default=str))
    
    # Generate final summary
    print("\n" + "=" * 80)
    print("STRESS TEST SUITE SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, metrics in results.items():
        if isinstance(metrics, StressTestMetrics):
            status = "✅ PASS" if metrics.success_rate > 95 and metrics.p95_response_time < 0.5 else "❌ FAIL"
            if "FAIL" in status:
                all_passed = False
            print(f"{test_name}: {status}")
            print(f"  - Success Rate: {metrics.success_rate:.2f}%")
            print(f"  - P95 Response: {metrics.p95_response_time:.3f}s")
        elif test_name == "memory_leak":
            status = "✅ PASS" if metrics.get("status") == "stable" else "❌ FAIL"
            if "FAIL" in status:
                all_passed = False
            print(f"{test_name}: {status}")
            print(f"  - Status: {metrics.get('status')}")
            print(f"  - Growth: {metrics.get('total_growth_mb', 0):.2f} MB")
    
    print("\n" + "=" * 80)
    print(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    # Run the full stress test suite
    asyncio.run(run_full_stress_suite())