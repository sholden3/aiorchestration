"""
AI Orchestration System - Comprehensive Test Suite
Testing framework for all governance and orchestration components
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Test configuration
TEST_CONFIG = {
    "test_timeout": 30,  # seconds
    "async_timeout": 10,  # seconds
    "mock_external_services": True,
    "test_data_dir": Path(__file__).parent / "fixtures",
    "coverage_threshold": 80,  # percentage
    "integration_test_env": "test",
    "e2e_test_env": "staging"
}

# Test markers for pytest
MARKERS = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interactions",
    "e2e": "End-to-end tests for complete workflows",
    "slow": "Tests that take more than 5 seconds",
    "governance": "Tests for governance components",
    "orchestration": "Tests for orchestration components",
    "deployment": "Tests for deployment components",
    "monitoring": "Tests for monitoring components"
}