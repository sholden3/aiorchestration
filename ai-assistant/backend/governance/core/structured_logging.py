"""
File: ai-assistant/backend/governance/core/structured_logging.py
Purpose: Structured logging with correlation IDs for request tracing
Architecture: Provides centralized logging with request correlation and structured output
Dependencies: logging, contextvars, uuid, json, datetime, typing
Owner: Dr. Sarah Chen

@fileoverview Structured JSON logging with correlation IDs and request tracing
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Centralized structured logging with correlation tracking
@business_logic JSON log formatting, correlation ID propagation, operation timing
@integration_points All backend services, FastAPI middleware, monitoring systems
@error_handling Exception serialization, stack trace capture, error context
@performance Minimal overhead, async-safe context vars, efficient JSON serialization
"""

import logging
import json
import uuid
import time
from contextvars import ContextVar
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from functools import wraps
import traceback
import sys

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

# Context variable for additional context
logging_context_var: ContextVar[Dict[str, Any]] = ContextVar('logging_context', default={})


@dataclass
class LogEntry:
    """
    Structured log entry with all relevant metadata.
    
    Attributes:
        timestamp: ISO format timestamp
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        correlation_id: Request correlation ID for tracing
        message: Log message
        context: Additional context data
        location: Code location (file, function, line)
        duration_ms: Operation duration in milliseconds
        error: Error information if applicable
    """
    timestamp: str
    level: str
    correlation_id: Optional[str]
    message: str
    context: Dict[str, Any]
    location: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(asdict(self), default=str)


class StructuredLogger:
    """
    Logger that outputs structured JSON logs with correlation IDs.
    
    This logger ensures all log entries include correlation IDs for
    request tracing and outputs logs in a structured JSON format
    for easy parsing and analysis.
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name)
            level: Logging level
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # Create JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False
    
    def _create_log_entry(
        self,
        level: str,
        message: str,
        extra_context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        duration_ms: Optional[float] = None
    ) -> LogEntry:
        """
        Create a structured log entry.
        
        Args:
            level: Log level
            message: Log message
            extra_context: Additional context to include
            error: Exception object if applicable
            duration_ms: Operation duration
            
        Returns:
            LogEntry object
        """
        # Get correlation ID from context
        correlation_id = correlation_id_var.get()
        
        # Get base context from context var
        base_context = logging_context_var.get().copy()
        
        # Merge with extra context
        if extra_context:
            base_context.update(extra_context)
        
        # Get caller information
        frame = sys._getframe(2)
        location = {
            'file': frame.f_code.co_filename,
            'function': frame.f_code.co_name,
            'line': frame.f_lineno
        }
        
        # Create error dict if exception provided
        error_dict = None
        if error:
            error_dict = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        
        return LogEntry(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            level=level,
            correlation_id=correlation_id,
            message=message,
            context=base_context,
            location=location,
            duration_ms=duration_ms,
            error=error_dict
        )
    
    def debug(self, message: str, **context):
        """Log debug message with context."""
        entry = self._create_log_entry('DEBUG', message, context)
        self.logger.debug(entry.to_json())
    
    def info(self, message: str, **context):
        """Log info message with context."""
        entry = self._create_log_entry('INFO', message, context)
        self.logger.info(entry.to_json())
    
    def warning(self, message: str, **context):
        """Log warning message with context."""
        entry = self._create_log_entry('WARNING', message, context)
        self.logger.warning(entry.to_json())
    
    def error(self, message: str, error: Optional[Exception] = None, **context):
        """Log error message with exception details."""
        entry = self._create_log_entry('ERROR', message, context, error=error)
        self.logger.error(entry.to_json())
    
    def critical(self, message: str, error: Optional[Exception] = None, **context):
        """Log critical message with exception details."""
        entry = self._create_log_entry('CRITICAL', message, context, error=error)
        self.logger.critical(entry.to_json())
    
    def log_operation(self, operation: str, **context):
        """
        Context manager for logging operation with duration.
        
        Args:
            operation: Name of the operation
            **context: Additional context
            
        Example:
            with logger.log_operation('database_query', query='SELECT *'):
                result = await db.execute(query)
        """
        return OperationLogger(self, operation, context)


class OperationLogger:
    """
    Context manager for logging operations with timing.
    
    Automatically logs start, completion, and duration of operations.
    """
    
    def __init__(self, logger: StructuredLogger, operation: str, context: Dict[str, Any]):
        """
        Initialize operation logger.
        
        Args:
            logger: Parent structured logger
            operation: Operation name
            context: Operation context
        """
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Start operation timing."""
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation}", operation=self.operation, **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete operation and log results."""
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation}",
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                **self.context
            )
        else:
            self.logger.error(
                f"Failed {self.operation}",
                error=exc_val,
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                **self.context
            )
        
        # Don't suppress exceptions
        return False


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    
    Ensures all log records are formatted as JSON for
    consistent parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        # If message is already JSON, return as-is
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Create structured log entry
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'correlation_id': correlation_id_var.get(),
            'message': record.getMessage(),
            'logger': record.name,
            'location': {
                'file': record.pathname,
                'function': record.funcName,
                'line': record.lineno
            }
        }
        
        # Add exception info if present
        if record.exc_info:
            entry['error'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(entry, default=str)


class CorrelationIDManager:
    """
    Manager for correlation IDs across request lifecycle.
    
    Handles generation, propagation, and cleanup of correlation IDs
    for request tracing.
    """
    
    @staticmethod
    def generate() -> str:
        """
        Generate a new correlation ID.
        
        Returns:
            UUID string for correlation
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def set(correlation_id: Optional[str] = None) -> str:
        """
        Set correlation ID for current context.
        
        Args:
            correlation_id: Correlation ID to set (generates new if None)
            
        Returns:
            The set correlation ID
        """
        if correlation_id is None:
            correlation_id = CorrelationIDManager.generate()
        
        correlation_id_var.set(correlation_id)
        return correlation_id
    
    @staticmethod
    def get() -> Optional[str]:
        """
        Get current correlation ID.
        
        Returns:
            Current correlation ID or None
        """
        return correlation_id_var.get()
    
    @staticmethod
    def clear():
        """Clear correlation ID from context."""
        correlation_id_var.set(None)


def with_correlation_id(func):
    """
    Decorator to ensure function runs with correlation ID.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
        
    Example:
        @with_correlation_id
        async def process_request(request):
            # Will have correlation ID in context
            logger.info("Processing request")
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Set correlation ID if not present
        if CorrelationIDManager.get() is None:
            CorrelationIDManager.set()
        
        try:
            return await func(*args, **kwargs)
        finally:
            # Clear correlation ID after execution
            CorrelationIDManager.clear()
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Set correlation ID if not present
        if CorrelationIDManager.get() is None:
            CorrelationIDManager.set()
        
        try:
            return func(*args, **kwargs)
        finally:
            # Clear correlation ID after execution
            CorrelationIDManager.clear()
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def add_logging_context(**context):
    """
    Add context to all logs in current scope.
    
    Args:
        **context: Key-value pairs to add to logging context
        
    Example:
        add_logging_context(user_id='123', action='create_session')
        logger.info("Session created")  # Will include user_id and action
    """
    current_context = logging_context_var.get().copy()
    current_context.update(context)
    logging_context_var.set(current_context)


def clear_logging_context():
    """Clear all logging context."""
    logging_context_var.set({})


# Create module-level loggers
governance_logger = StructuredLogger('governance')
api_logger = StructuredLogger('api')
system_logger = StructuredLogger('system')


# Configure root logger to use structured format
def configure_structured_logging(level: int = logging.INFO):
    """
    Configure all loggers to use structured format.
    
    Args:
        level: Default logging level
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Add structured handler
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(handler)
    
    # Configure specific loggers
    for name in ['uvicorn', 'fastapi', 'sqlalchemy']:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.propagate = False
    
    system_logger.info("Structured logging configured", level=logging.getLevelName(level))