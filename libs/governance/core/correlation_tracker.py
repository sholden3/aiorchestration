#!/usr/bin/env python3
"""
@fileoverview Correlation tracking system for end-to-end request tracing
@author Alex Novak v3.0 - 2025-01-28
@architecture Backend/Integration - Core governance tracking
@responsibility Track all governance operations with correlation IDs for debugging
@dependencies uuid, datetime, json, threading
@integration_points All governance components, logging system, audit trail
@testing_strategy Unit tests for ID generation, integration tests for tracking flow
@governance Alex's 3 AM debugging requirement - full traceability

Business Logic Summary:
- Generate unique correlation IDs for all operations
- Track operation lifecycle from start to finish
- Maintain debug traces for troubleshooting

Architecture Integration:
- Central component for request tracking
- Integrates with all governance operations
- Provides debugging information for failures
"""

import uuid
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging


class OperationStatus(Enum):
    """Status of a tracked operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class CorrelationContext:
    """
    Context for a correlated operation
    
    @business_logic Tracks complete lifecycle of governance operations
    @validation All fields validated on creation
    @error_handling Graceful handling of missing data
    """
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    user: str = ""
    operation_type: str = ""
    operation_name: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: OperationStatus = OperationStatus.PENDING
    
    # Tracking data
    metadata: Dict[str, Any] = field(default_factory=dict)
    debug_trace: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    checkpoints: Dict[str, datetime] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def add_trace(self, message: str):
        """Add debug trace with timestamp"""
        timestamp = datetime.now().isoformat()
        self.debug_trace.append(f"[{timestamp}] {message}")
    
    def add_event(self, event_type: str, data: Any):
        """Add event to correlation"""
        self.events.append({
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
    
    def add_checkpoint(self, name: str):
        """Add performance checkpoint"""
        self.checkpoints[name] = datetime.now()
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate operation duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        elif self.status == OperationStatus.IN_PROGRESS:
            return (datetime.now() - self.start_time).total_seconds() * 1000
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        data['status'] = self.status.value
        
        # Convert checkpoint datetimes
        data['checkpoints'] = {
            k: v.isoformat() for k, v in self.checkpoints.items()
        }
        
        return data


class CorrelationTracker:
    """
    Correlation tracking system for governance operations
    
    @architecture_role Central tracking for all governance operations
    @business_logic Maintains correlation context for debugging
    @failure_modes Thread-safe operations, automatic cleanup of old correlations
    @debugging_info All operations tracked with full context
    
    Defensive Programming Patterns:
    - Thread-safe with locks
    - Automatic cleanup of old correlations
    - Bounded history size
    
    Integration Boundaries:
    - Used by all governance components
    - Integrates with logging system
    - Feeds audit trail
    
    Sarah's Framework Check:
    - What breaks first: Memory if correlations not cleaned up
    - How we know: Memory monitoring and size limits
    - Plan B: Automatic cleanup of old correlations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize correlation tracker
        
        @param config Optional configuration overrides
        """
        self.config = config or {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Active correlations
        self.active_correlations: Dict[str, CorrelationContext] = {}
        
        # Historical correlations (bounded)
        self.correlation_history: List[CorrelationContext] = []
        self.max_history_size = self.config.get('max_history_size', 1000)
        
        # Persistence
        self.persistence_enabled = self.config.get('persistence_enabled', True)
        self.persistence_path = Path(self.config.get(
            'persistence_path', 
            '.governance/correlations'
        ))
        
        if self.persistence_enabled:
            self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # Cleanup settings
        self.auto_cleanup_enabled = self.config.get('auto_cleanup_enabled', True)
        self.correlation_ttl_seconds = self.config.get('correlation_ttl_seconds', 3600)
        
        # Logging
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")
        
        # Start cleanup thread if enabled
        if self.auto_cleanup_enabled:
            self._start_cleanup_thread()
    
    def create_correlation(
        self,
        operation_type: str,
        operation_name: str,
        user: str = "",
        session_id: Optional[str] = None,
        parent_correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CorrelationContext:
        """
        Create new correlation context
        
        @business_rule All operations must have correlation
        @validation Operation type and name required
        @side_effects Adds to active correlations
        @returns New correlation context
        """
        correlation = CorrelationContext(
            operation_type=operation_type,
            operation_name=operation_name,
            user=user,
            session_id=session_id,
            parent_correlation_id=parent_correlation_id,
            metadata=metadata or {}
        )
        
        correlation.status = OperationStatus.IN_PROGRESS
        correlation.add_trace(f"Correlation created for {operation_type}:{operation_name}")
        
        with self._lock:
            self.active_correlations[correlation.correlation_id] = correlation
        
        self.logger.info(
            f"Created correlation {correlation.correlation_id} for {operation_type}",
            extra={'correlation_id': correlation.correlation_id}
        )
        
        return correlation
    
    def get_correlation(self, correlation_id: str) -> Optional[CorrelationContext]:
        """
        Get correlation by ID
        
        @param correlation_id Correlation ID to retrieve
        @returns Correlation context or None if not found
        """
        with self._lock:
            # Check active correlations
            if correlation_id in self.active_correlations:
                return self.active_correlations[correlation_id]
            
            # Check history
            for correlation in self.correlation_history:
                if correlation.correlation_id == correlation_id:
                    return correlation
        
        return None
    
    def update_correlation(
        self,
        correlation_id: str,
        status: Optional[OperationStatus] = None,
        metadata_update: Optional[Dict[str, Any]] = None,
        add_trace: Optional[str] = None,
        add_error: Optional[str] = None,
        add_warning: Optional[str] = None
    ) -> bool:
        """
        Update correlation context
        
        @param correlation_id ID to update
        @param status New status
        @param metadata_update Metadata to merge
        @param add_trace Trace message to add
        @param add_error Error to add
        @param add_warning Warning to add
        @returns True if updated, False if not found
        """
        with self._lock:
            correlation = self.active_correlations.get(correlation_id)
            
            if not correlation:
                return False
            
            if status:
                correlation.status = status
                if status in [OperationStatus.COMPLETED, OperationStatus.FAILED]:
                    correlation.end_time = datetime.now()
            
            if metadata_update:
                correlation.metadata.update(metadata_update)
            
            if add_trace:
                correlation.add_trace(add_trace)
            
            if add_error:
                correlation.errors.append(add_error)
                correlation.add_trace(f"ERROR: {add_error}")
            
            if add_warning:
                correlation.warnings.append(add_warning)
                correlation.add_trace(f"WARNING: {add_warning}")
            
            return True
    
    def complete_correlation(
        self,
        correlation_id: str,
        status: OperationStatus = OperationStatus.COMPLETED,
        result: Optional[Any] = None
    ):
        """
        Complete correlation and move to history
        
        @param correlation_id ID to complete
        @param status Final status
        @param result Operation result
        
        Sarah's Framework Check:
        - What breaks first: Memory if history unbounded
        - How we know: History size monitoring
        - Plan B: Automatic trimming of old entries
        """
        with self._lock:
            correlation = self.active_correlations.get(correlation_id)
            
            if not correlation:
                self.logger.warning(f"Correlation {correlation_id} not found for completion")
                return
            
            # Update final state
            correlation.status = status
            correlation.end_time = datetime.now()
            
            if result:
                correlation.metadata['result'] = result
            
            # Calculate final metrics
            duration = correlation.calculate_duration()
            if duration:
                correlation.metrics['total_duration_ms'] = duration
            
            correlation.add_trace(f"Correlation completed with status {status.value}")
            
            # Persist if enabled
            if self.persistence_enabled:
                self._persist_correlation(correlation)
            
            # Move to history
            self.correlation_history.append(correlation)
            del self.active_correlations[correlation_id]
            
            # Trim history if needed
            if len(self.correlation_history) > self.max_history_size:
                self.correlation_history = self.correlation_history[-self.max_history_size:]
        
        self.logger.info(
            f"Completed correlation {correlation_id} with status {status.value}",
            extra={'correlation_id': correlation_id}
        )
    
    def add_checkpoint(self, correlation_id: str, checkpoint_name: str):
        """Add performance checkpoint to correlation"""
        with self._lock:
            correlation = self.active_correlations.get(correlation_id)
            if correlation:
                correlation.add_checkpoint(checkpoint_name)
                correlation.add_trace(f"Checkpoint: {checkpoint_name}")
    
    def add_metric(self, correlation_id: str, metric_name: str, value: float):
        """Add metric to correlation"""
        with self._lock:
            correlation = self.active_correlations.get(correlation_id)
            if correlation:
                correlation.metrics[metric_name] = value
                correlation.add_trace(f"Metric {metric_name}: {value}")
    
    def get_active_correlations(self) -> List[CorrelationContext]:
        """Get all active correlations"""
        with self._lock:
            return list(self.active_correlations.values())
    
    def get_correlation_history(
        self,
        limit: Optional[int] = None,
        filter_fn: Optional[Any] = None
    ) -> List[CorrelationContext]:
        """
        Get correlation history with optional filtering
        
        @param limit Maximum number of results
        @param filter_fn Optional filter function
        @returns List of historical correlations
        """
        with self._lock:
            history = self.correlation_history.copy()
            
            if filter_fn:
                history = [c for c in history if filter_fn(c)]
            
            if limit:
                history = history[-limit:]
            
            return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get tracker statistics
        
        @returns Statistics about correlation tracking
        """
        with self._lock:
            # Calculate status distribution
            status_counts = {}
            for correlation in self.correlation_history:
                status = correlation.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate average durations
            durations = [
                c.calculate_duration() 
                for c in self.correlation_history 
                if c.calculate_duration()
            ]
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                'active_correlations': len(self.active_correlations),
                'history_size': len(self.correlation_history),
                'status_distribution': status_counts,
                'average_duration_ms': avg_duration,
                'max_history_size': self.max_history_size,
                'persistence_enabled': self.persistence_enabled,
                'auto_cleanup_enabled': self.auto_cleanup_enabled
            }
    
    def _persist_correlation(self, correlation: CorrelationContext):
        """Persist correlation to disk"""
        try:
            file_path = self.persistence_path / f"{correlation.correlation_id}.json"
            
            with open(file_path, 'w') as f:
                json.dump(correlation.to_dict(), f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to persist correlation: {e}")
    
    def _cleanup_old_correlations(self):
        """Clean up old correlations that exceeded TTL"""
        with self._lock:
            now = datetime.now()
            expired = []
            
            for correlation_id, correlation in self.active_correlations.items():
                age = (now - correlation.start_time).total_seconds()
                
                if age > self.correlation_ttl_seconds:
                    expired.append(correlation_id)
            
            for correlation_id in expired:
                self.logger.warning(
                    f"Auto-completing expired correlation {correlation_id}"
                )
                self.complete_correlation(
                    correlation_id,
                    OperationStatus.TIMEOUT
                )
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        import threading
        
        def cleanup_loop():
            while self.auto_cleanup_enabled:
                threading.Event().wait(60)  # Check every minute
                self._cleanup_old_correlations()
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def shutdown(self):
        """Clean shutdown of tracker"""
        self.auto_cleanup_enabled = False
        
        # Complete all active correlations
        with self._lock:
            for correlation_id in list(self.active_correlations.keys()):
                self.complete_correlation(
                    correlation_id,
                    OperationStatus.CANCELLED
                )
        
        self.logger.info("Correlation tracker shutdown complete")


# Global tracker instance
_global_tracker = None


def get_correlation_tracker(config: Optional[Dict[str, Any]] = None) -> CorrelationTracker:
    """
    Get or create global correlation tracker
    
    @param config Configuration for new tracker
    @returns Global correlation tracker instance
    """
    global _global_tracker
    
    if _global_tracker is None:
        _global_tracker = CorrelationTracker(config)
    
    return _global_tracker