#!/usr/bin/env python3
"""
@fileoverview Test file for governance compliant example
@author Sam Martinez v3.2.0 - 2025-01-28
@architecture Testing - Unit tests
@responsibility Test governance compliant example
@dependencies pytest, unittest
@integration_points Tests proper_governance_example module
@testing_strategy Full coverage of all methods
@governance Test file following governance requirements

Business Logic Summary:
- Tests all methods
- Validates error handling
- Ensures compliance

Architecture Integration:
- Part of test suite
- Validates governance compliance
- Can be run in CI/CD
"""

import unittest
from proper_governance_example import GovernanceCompliantExample


class TestGovernanceCompliantExample(unittest.TestCase):
    """
    @class TestGovernanceCompliantExample
    @description Unit tests for governance example
    @architecture_role Validation of compliance
    @business_logic Tests all business rules
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.example = GovernanceCompliantExample()
    
    def tearDown(self):
        """Clean up after tests"""
        self.example.cleanup()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertTrue(self.example.initialized)
        self.assertIsNotNone(self.example.config)
    
    def test_process_data_valid(self):
        """Test processing with valid data"""
        result = self.example.process_data("Test Data")
        self.assertEqual(result, "test data")
    
    def test_process_data_invalid(self):
        """Test processing with invalid data"""
        with self.assertRaises(ValueError):
            self.example.process_data(123)  # Not a string
    
    def test_cleanup(self):
        """Test cleanup method"""
        self.example.cleanup()
        self.assertFalse(self.example.initialized)


if __name__ == "__main__":
    unittest.main()