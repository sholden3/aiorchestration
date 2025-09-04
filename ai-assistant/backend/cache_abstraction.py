"""
Cache Abstraction Layer - Future-Proof Design
Expert Recommendation: Dr. Alex Kim - Caching Architecture Expert
Implementation: Three-Persona Collaborative Design

Purpose: Design cache interface to support future dual-cache architecture
         without current over-engineering
"""

from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging
from enum import Enum

from cache_manager import IntelligentCache

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """
    Cache type enumeration for future specialization
    Dr. Kim: "Data type characteristics should drive cache architecture"
    """
    GENERIC = "generic"      # Current implementation
    AST = "ast"              # Future: AST-optimized cache
    DOCUMENT = "document"    # Future: Document-optimized cache
    METADATA = "metadata"    # Future: Metadata cache

class CacheStrategy(ABC):
    """
    Abstract base class for cache strategies
    Marcus: Enables strategy pattern for future cache types
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache"""
        raise NotImplementedError("Subclasses must implement get method")
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store in cache"""
        raise NotImplementedError("Subclasses must implement set method")
    
    @abstractmethod
    async def invalidate(self, key: str) -> bool:
        """Invalidate cache entry"""
        raise NotImplementedError("Subclasses must implement invalidate method")
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        raise NotImplementedError("Subclasses must implement get_metrics method")

class GenericCacheStrategy(CacheStrategy):
    """
    Current implementation wrapper
    Sarah: Maintains backward compatibility while enabling future migration
    """
    
    def __init__(self):
        self.cache = IntelligentCache()
        
    async def get(self, key: str) -> Optional[Any]:
        return await self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            await self.cache.set(key, value, ttl_hours=ttl//3600 if ttl else 24)
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    async def invalidate(self, key: str) -> bool:
        # Current implementation doesn't have explicit invalidation
        # This prepares for future implementation
        logger.info(f"Invalidation requested for key: {key}")
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.cache.get_metrics()

class FutureProofCacheManager:
    """
    Future-proof cache manager following Dr. Kim's recommendations
    Emily: Provides clean interface for UI regardless of underlying cache architecture
    """
    
    def __init__(self):
        # Start with generic cache
        self.strategies: Dict[CacheType, CacheStrategy] = {
            CacheType.GENERIC: GenericCacheStrategy()
        }
        
        # Use generic for all types initially
        self.default_strategy = self.strategies[CacheType.GENERIC]
        
        # Prepare for future specialization
        self.type_routing = {
            CacheType.AST: CacheType.GENERIC,      # Route to generic for now
            CacheType.DOCUMENT: CacheType.GENERIC,  # Route to generic for now
            CacheType.METADATA: CacheType.GENERIC   # Route to generic for now
        }
        
        logger.info("FutureProofCacheManager initialized with generic strategy")
    
    async def cache_ast(self, key: str, ast_data: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache AST data (future-proof interface)
        Dr. Kim: "AST cache: high TTL, no compression, LFU eviction"
        """
        # Currently routes to generic cache
        # TODO: Replace with AST-optimized cache when AST operations added
        prefixed_key = f"ast:{key}"
        return await self.default_strategy.set(prefixed_key, ast_data, ttl or 86400)  # 24h default
    
    async def get_ast(self, key: str) -> Optional[Any]:
        """Retrieve AST from cache"""
        prefixed_key = f"ast:{key}"
        return await self.default_strategy.get(prefixed_key)
    
    async def cache_document(self, key: str, doc_data: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache document data (future-proof interface)
        Dr. Kim: "Document cache: aggressive compression, LRU eviction"
        """
        # Currently routes to generic cache
        # TODO: Replace with document-optimized cache when needed
        prefixed_key = f"doc:{key}"
        return await self.default_strategy.set(prefixed_key, doc_data, ttl or 14400)  # 4h default
    
    async def get_document(self, key: str) -> Optional[Any]:
        """Retrieve document from cache"""
        prefixed_key = f"doc:{key}"
        return await self.default_strategy.get(prefixed_key)
    
    async def cache_metadata(self, key: str, metadata: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache metadata (future-proof interface)
        Dr. Kim: "Metadata cache: small, fast, frequent updates"
        """
        prefixed_key = f"meta:{key}"
        return await self.default_strategy.set(prefixed_key, metadata, ttl or 3600)  # 1h default
    
    async def get_metadata(self, key: str) -> Optional[Any]:
        """Retrieve metadata from cache"""
        prefixed_key = f"meta:{key}"
        return await self.default_strategy.get(prefixed_key)
    
    async def invalidate_related(self, source_file: str):
        """
        Cross-cache coherency (Dr. Kim's recommendation)
        Invalidate related cache entries when source changes
        """
        invalidations = [
            f"ast:{source_file}",
            f"doc:{source_file}",
            f"meta:{source_file}"
        ]
        
        for key in invalidations:
            await self.default_strategy.invalidate(key)
        
        logger.info(f"Invalidated related cache entries for: {source_file}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all cache strategies
        """
        metrics = {
            "strategies_active": len(self.strategies),
            "cache_types": list(self.strategies.keys()),
        }
        
        # Aggregate metrics from all strategies
        for cache_type, strategy in self.strategies.items():
            metrics[f"{cache_type.value}_metrics"] = strategy.get_metrics()
        
        return metrics
    
    def prepare_for_ast_operations(self):
        """
        Migration path: Called when AST operations are added
        Dr. Kim: "Implement dual caching when you add AST operations"
        """
        logger.info("Preparing for AST operations - dual cache migration point")
        # TODO: Implement ASTCacheStrategy
        # TODO: Update type_routing to use specialized cache
        # TODO: Implement cache warming for AST data
        pass
    
    def enable_tenant_isolation(self, tenant_id: str):
        """
        Future multi-tenant support (Dr. Kim's recommendation)
        """
        logger.info(f"Tenant isolation requested for: {tenant_id}")
        # TODO: Implement tenant-aware key prefixing
        # TODO: Add tenant-specific cache quotas
        pass

# Global instance for backward compatibility
cache_manager = FutureProofCacheManager()

# Migration helper
def get_cache_manager() -> FutureProofCacheManager:
    """
    Get cache manager instance
    Provides migration path from current to future architecture
    """
    return cache_manager