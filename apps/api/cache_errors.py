"""
FIX C2: Cache-specific error handling with recovery strategies
Architecture: Dr. Sarah Chen
Pattern: Defensive error boundaries with circuit breaker
"""
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CacheErrorType(Enum):
    """Types of cache errors for monitoring and recovery"""
    DISK_CORRUPTION = "disk_corruption"
    DISK_IO_ERROR = "disk_io_error" 
    SERIALIZATION_ERROR = "serialization_error"
    MEMORY_PRESSURE = "memory_pressure"
    TIMEOUT_ERROR = "timeout_error"
    INDEX_CORRUPTION = "index_corruption"

class CacheError(Exception):
    """Base cache error with recovery context"""
    
    def __init__(self, message: str, error_type: CacheErrorType, 
                 key: Optional[str] = None, recoverable: bool = True):
        super().__init__(message)
        self.error_type = error_type
        self.key = key
        self.recoverable = recoverable
        self.logged = False
    
    def log_once(self):
        """Log error only once to prevent spam"""
        if not self.logged:
            logger.error(f"Cache error [{self.error_type.value}]: {self} (key: {self.key})")
            self.logged = True

class CacheDiskCorruptionError(CacheError):
    """Specific error for corrupted cache files"""
    
    def __init__(self, key: str, file_path: str, original_error: Exception):
        super().__init__(
            f"Corrupted cache file: {file_path}",
            CacheErrorType.DISK_CORRUPTION,
            key=key,
            recoverable=True
        )
        self.file_path = file_path
        self.original_error = original_error

class CacheDiskIOError(CacheError):
    """Specific error for disk I/O failures"""
    
    def __init__(self, operation: str, key: str, original_error: Exception):
        super().__init__(
            f"Disk I/O error during {operation}",
            CacheErrorType.DISK_IO_ERROR,
            key=key,
            recoverable=True
        )
        self.operation = operation
        self.original_error = original_error

class CacheCircuitBreakerOpenError(CacheError):
    """Error when circuit breaker is open"""
    
    def __init__(self, message: str = "Cache circuit breaker is OPEN"):
        super().__init__(
            message,
            CacheErrorType.TIMEOUT_ERROR,
            recoverable=False
        )