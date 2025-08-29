#!/usr/bin/env python
"""
@fileoverview Stress test runner for Phase 4 production hardening validation
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Test infrastructure for load and stress testing
@responsibility Execute comprehensive stress tests against the backend API
@dependencies asyncio, stress_test_suite module
@integration_points Backend API endpoints, WebSocket connections, database
@testing_strategy Runs full stress test suite including load, memory, and connection tests
@governance Validates system behavior under extreme load conditions

Business Logic Summary:
- Executes comprehensive stress test suite
- Validates system stability under load
- Ensures resource limits are enforced
- Tests failure recovery mechanisms

Architecture Integration:
- Part of Phase 4 production hardening
- Tests all backend endpoints under stress
- Validates WebSocket connection limits
- Ensures graceful degradation under load

Sarah's Framework Check:
- What breaks first: Connection limits or memory exhaustion
- How we know: Test results and error reporting
- Plan B: Graceful test interruption with cleanup
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.stress_test_suite import run_full_stress_suite

if __name__ == "__main__":
    print("🚀 Starting Phase 4 Production Hardening Stress Tests")
    print("⚠️  Make sure the backend is running on http://localhost:8000")
    print("-" * 60)
    
    try:
        results = asyncio.run(run_full_stress_suite())
        print("\n✅ Stress tests completed successfully")
    except KeyboardInterrupt:
        print("\n⚠️ Stress tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Stress tests failed with error: {e}")
        sys.exit(1)