"""
@fileoverview Shared logging utilities
@author Dr. Sarah Chen - Backend Architect
@architecture Shared Utils Library  
@description Centralized logging with correlation tracking
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import IntEnum
import sys


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class CorrelationLogger:
    """Logger with correlation ID support for distributed tracing"""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.context: Dict[str, Any] = {}
        self.formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s][%(correlation_id)s] %(component)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure root logger
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        
        # Add console handler if not present
        if not root.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self.formatter)
            root.addHandler(handler)
    
    def set_context(self, **kwargs):
        """Set global context for all log messages"""
        self.context.update(kwargs)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            
            # Add correlation filter
            logger.addFilter(self._correlation_filter)
            
            self._loggers[name] = logger
            
        return self._loggers[name]
    
    def _correlation_filter(self, record):
        """Add correlation context to log records"""
        record.correlation_id = self.context.get('correlation_id', '-')
        record.component = self.context.get('component', record.name)
        record.session_id = self.context.get('session_id', '')
        record.user_id = self.context.get('user_id', '')
        return True
    
    @staticmethod
    def format_error(error: Exception) -> Dict[str, Any]:
        """Format exception for structured logging"""
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_args': error.args if hasattr(error, 'args') else []
        }


class ComponentLogger:
    """Logger wrapper for component-specific logging"""
    
    def __init__(self, component: str):
        self.component = component
        self.correlation_logger = CorrelationLogger()
        self.logger = self.correlation_logger.get_logger(component)
        
    def set_context(self, **kwargs):
        """Set context for this logger"""
        self.correlation_logger.set_context(component=self.component, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        extra = {'extra': kwargs} if kwargs else {}
        self.logger.debug(message, **extra)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        extra = {'extra': kwargs} if kwargs else {}
        self.logger.info(message, **extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        extra = {'extra': kwargs} if kwargs else {}
        self.logger.warning(message, **extra)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if error:
            kwargs['error_details'] = CorrelationLogger.format_error(error)
        extra = {'extra': kwargs} if kwargs else {}
        self.logger.error(message, **extra, exc_info=error is not None)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if error:
            kwargs['error_details'] = CorrelationLogger.format_error(error)
        extra = {'extra': kwargs} if kwargs else {}
        self.logger.critical(message, **extra, exc_info=error is not None)


def get_logger(component: str) -> ComponentLogger:
    """Get a component logger"""
    return ComponentLogger(component)


# Global logger instance
logger = get_logger('shared-utils')