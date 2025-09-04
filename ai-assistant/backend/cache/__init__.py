"""
Cache Module

Provides caching functionality with Redis or in-memory fallback.

Recovery Note: Created 2025-09-03 during dependency recovery (DEC-2025-010)
"""

# Cache configuration
CACHE_TTL_DEFAULT = 300  # 5 minutes
CACHE_TTL_SHORT = 60     # 1 minute
CACHE_TTL_LONG = 3600    # 1 hour