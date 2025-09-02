#!/usr/bin/env python3
"""
@fileoverview Unit tests for correlation tracking system
@author Alex Novak v3.0 - 2025-01-28
@architecture Testing - Unit tests for correlation tracker
@responsibility Validate correlation tracking functionality
@dependencies pytest, unittest, threading, time
@integration_points Tests correlation_tracker module
@testing_strategy Full coverage of correlation lifecycle
@governance Test file following governance requirements

Business Logic Summary:
- Test correlation creation and lifecycle
- Validate thread safety
- Ensure proper cleanup

Architecture Integration:
- Part of governance test suite
- Validates core tracking component
- Tests defensive patterns
"""

import pytest
import unittest
import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
import shutil

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.correlation_tracker import (
    CorrelationTracker, 
    CorrelationContext, 
    OperationStatus,
    get_correlation_tracker
)


class TestCorrelationContext(unittest.TestCase):
    """
    @class TestCorrelationContext
    @description Unit tests for CorrelationContext
    @architecture_role Validate correlation data structure
    @business_logic Test all correlation context methods
    """
    
    def test_context_creation(self):
        """Test correlation context creation"""
        context = CorrelationContext(
            operation_type='test_op',
            operation_name='test_name',
            user='test_user'
        )
        
        self.assertIsNotNone(context.correlation_id)
        self.assertEqual(context.operation_type, 'test_op')
        self.assertEqual(context.operation_name, 'test_name')
        self.assertEqual(context.user, 'test_user')
        self.assertEqual(context.status, OperationStatus.PENDING)
    
    def test_add_trace(self):
        """Test adding debug traces"""
        context = CorrelationContext()
        context.add_trace("Test message")
        
        self.assertEqual(len(context.debug_trace), 1)
        self.assertIn("Test message", context.debug_trace[0])
    
    def test_add_event(self):
        """Test adding events"""
        context = CorrelationContext()
        context.add_event('test_event', {'data': 'test'})
        
        self.assertEqual(len(context.events), 1)
        self.assertEqual(context.events[0]['type'], 'test_event')
        self.assertEqual(context.events[0]['data']['data'], 'test')
    
    def test_calculate_duration(self):
        """Test duration calculation"""
        context = CorrelationContext()
        context.status = OperationStatus.IN_PROGRESS
        
        # Wait a bit
        time.sleep(0.1)
        
        duration = context.calculate_duration()
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 0)
        
        # Complete and test again
        context.end_time = datetime.now()
        duration = context.calculate_duration()
        self.assertIsNotNone(duration)
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary"""
        context = CorrelationContext(
            operation_type='test',
            metadata={'key': 'value'}
        )
        context.add_checkpoint('checkpoint1')
        
        data = context.to_dict()
        
        self.assertIn('correlation_id', data)
        self.assertIn('operation_type', data)
        self.assertIn('metadata', data)
        self.assertIn('checkpoints', data)
        self.assertEqual(data['status'], 'pending')


class TestCorrelationTracker(unittest.TestCase):
    """
    @class TestCorrelationTracker
    @description Unit tests for CorrelationTracker
    @architecture_role Validate tracker functionality
    @business_logic Test correlation lifecycle management
    """
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temp directory for persistence
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'persistence_path': self.temp_dir,
            'auto_cleanup_enabled': False,  # Disable for testing
            'max_history_size': 10
        }
        self.tracker = CorrelationTracker(self.config)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temp directory
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_correlation(self):
        """Test creating new correlations"""
        correlation = self.tracker.create_correlation(
            operation_type='test_op',
            operation_name='test_name',
            user='test_user',
            metadata={'key': 'value'}
        )
        
        self.assertIsNotNone(correlation)
        self.assertEqual(correlation.operation_type, 'test_op')
        self.assertEqual(correlation.status, OperationStatus.IN_PROGRESS)
        self.assertIn(correlation.correlation_id, self.tracker.active_correlations)
    
    def test_get_correlation(self):
        """Test retrieving correlations by ID"""
        correlation = self.tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        
        # Get from active
        retrieved = self.tracker.get_correlation(correlation.correlation_id)
        self.assertEqual(correlation.correlation_id, retrieved.correlation_id)
        
        # Complete and get from history
        self.tracker.complete_correlation(correlation.correlation_id)
        retrieved = self.tracker.get_correlation(correlation.correlation_id)
        self.assertEqual(correlation.correlation_id, retrieved.correlation_id)
    
    def test_update_correlation(self):
        """Test updating correlation context"""
        correlation = self.tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        
        # Update various fields
        success = self.tracker.update_correlation(
            correlation.correlation_id,
            status=OperationStatus.IN_PROGRESS,
            metadata_update={'new_key': 'new_value'},
            add_trace='Test trace',
            add_error='Test error',
            add_warning='Test warning'
        )
        
        self.assertTrue(success)
        
        # Verify updates
        updated = self.tracker.get_correlation(correlation.correlation_id)
        self.assertEqual(updated.status, OperationStatus.IN_PROGRESS)
        self.assertEqual(updated.metadata['new_key'], 'new_value')
        self.assertIn('Test error', updated.errors)
        self.assertIn('Test warning', updated.warnings)
    
    def test_complete_correlation(self):
        """Test completing correlations"""
        correlation = self.tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        correlation_id = correlation.correlation_id
        
        # Complete with success
        self.tracker.complete_correlation(
            correlation_id,
            OperationStatus.COMPLETED,
            result={'success': True}
        )
        
        # Should move to history
        self.assertNotIn(correlation_id, self.tracker.active_correlations)
        self.assertEqual(len(self.tracker.correlation_history), 1)
        
        # Should have end time and duration
        completed = self.tracker.get_correlation(correlation_id)
        self.assertIsNotNone(completed.end_time)
        self.assertIsNotNone(completed.calculate_duration())
    
    def test_checkpoints_and_metrics(self):
        """Test performance checkpoints and metrics"""
        correlation = self.tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        
        # Add checkpoint
        self.tracker.add_checkpoint(correlation.correlation_id, 'step1')
        
        # Add metric
        self.tracker.add_metric(correlation.correlation_id, 'latency_ms', 42.5)
        
        # Verify
        updated = self.tracker.get_correlation(correlation.correlation_id)
        self.assertIn('step1', updated.checkpoints)
        self.assertEqual(updated.metrics['latency_ms'], 42.5)
    
    def test_history_management(self):
        """Test correlation history management"""
        # Create more correlations than max history
        for i in range(15):
            correlation = self.tracker.create_correlation(
                operation_type=f'test_{i}',
                operation_name='test'
            )
            self.tracker.complete_correlation(correlation.correlation_id)
        
        # History should be bounded
        self.assertEqual(len(self.tracker.correlation_history), 10)
        
        # Should keep most recent
        history = self.tracker.get_correlation_history()
        self.assertEqual(history[-1].operation_type, 'test_14')
    
    def test_statistics(self):
        """Test tracker statistics"""
        # Create some correlations
        for i in range(5):
            correlation = self.tracker.create_correlation(
                operation_type='test',
                operation_name='test'
            )
            if i < 3:
                self.tracker.complete_correlation(
                    correlation.correlation_id,
                    OperationStatus.COMPLETED
                )
        
        stats = self.tracker.get_statistics()
        
        self.assertEqual(stats['active_correlations'], 2)
        self.assertEqual(stats['history_size'], 3)
        self.assertIn('completed', stats['status_distribution'])
        self.assertEqual(stats['status_distribution']['completed'], 3)
    
    def test_persistence(self):
        """Test correlation persistence to disk"""
        correlation = self.tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        correlation_id = correlation.correlation_id
        
        self.tracker.complete_correlation(correlation_id)
        
        # Check file was created
        expected_file = Path(self.temp_dir) / f"{correlation_id}.json"
        self.assertTrue(expected_file.exists())
        
        # Verify content
        with open(expected_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['correlation_id'], correlation_id)
    
    def test_thread_safety(self):
        """Test thread-safe operations"""
        results = []
        
        def create_correlations():
            for i in range(10):
                correlation = self.tracker.create_correlation(
                    operation_type=f'thread_{threading.current_thread().name}_{i}',
                    operation_name='test'
                )
                results.append(correlation.correlation_id)
                time.sleep(0.001)  # Small delay to encourage race conditions
        
        # Create threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_correlations, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All correlations should be created
        self.assertEqual(len(results), 30)
        self.assertEqual(len(set(results)), 30)  # All unique
        self.assertEqual(len(self.tracker.active_correlations), 30)
    
    def test_global_tracker(self):
        """Test global tracker singleton"""
        tracker1 = get_correlation_tracker()
        tracker2 = get_correlation_tracker()
        
        # Should be same instance
        self.assertIs(tracker1, tracker2)
        
        # Create correlation in one
        correlation = tracker1.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        
        # Should be accessible from other
        retrieved = tracker2.get_correlation(correlation.correlation_id)
        self.assertIsNotNone(retrieved)


class TestCorrelationCleanup(unittest.TestCase):
    """
    @class TestCorrelationCleanup
    @description Test automatic cleanup of old correlations
    @architecture_role Validate cleanup mechanisms
    @business_logic Test TTL and auto-cleanup
    """
    
    def test_manual_cleanup(self):
        """Test manual cleanup of expired correlations"""
        tracker = CorrelationTracker({
            'auto_cleanup_enabled': False,
            'correlation_ttl_seconds': 1  # 1 second TTL
        })
        
        # Create correlation
        correlation = tracker.create_correlation(
            operation_type='test',
            operation_name='test'
        )
        correlation_id = correlation.correlation_id
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Manual cleanup
        tracker._cleanup_old_correlations()
        
        # Should be completed with timeout
        self.assertNotIn(correlation_id, tracker.active_correlations)
        completed = tracker.get_correlation(correlation_id)
        self.assertEqual(completed.status, OperationStatus.TIMEOUT)
    
    def test_shutdown_cleanup(self):
        """Test cleanup on tracker shutdown"""
        tracker = CorrelationTracker({
            'auto_cleanup_enabled': False
        })
        
        # Create correlations
        ids = []
        for i in range(3):
            correlation = tracker.create_correlation(
                operation_type='test',
                operation_name='test'
            )
            ids.append(correlation.correlation_id)
        
        # Shutdown
        tracker.shutdown()
        
        # All should be cancelled
        for correlation_id in ids:
            correlation = tracker.get_correlation(correlation_id)
            self.assertEqual(correlation.status, OperationStatus.CANCELLED)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])