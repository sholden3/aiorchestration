"""
Business Context: PostgreSQL database management for persistence
Architecture Pattern: Repository pattern with connection pooling
Performance Requirements: Connection pool of 10, <50ms query time
Business Assumptions: Local PostgreSQL installation
"""

import asyncio
import asyncpg
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations
    Business Logic: Persistent storage for cache, metrics, and history
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize database manager with connection pooling
        """
        from config import config
        self.config = config
        self.connection_string = connection_string or self._get_default_connection()
        self.pool: Optional[asyncpg.Pool] = None
        
    def _get_default_connection(self) -> str:
        """Get PostgreSQL connection string from configuration"""
        import os
        # Use environment variables with fallback to config defaults
        host = os.getenv('DB_HOST', self.config.systems.db_host)
        port = os.getenv('DB_PORT', str(self.config.systems.db_port))
        user = os.getenv('DB_USER', self.config.systems.db_user)
        password = os.getenv('DB_PASSWORD', self.config.systems.db_password)
        database = os.getenv('DB_NAME', self.config.systems.db_name)
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def initialize(self):
        """
        Initialize database connection pool and create schema
        Performance: Pool of 10 connections for concurrent operations
        """
        try:
            # Create connection pool with configuration
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=self.config.systems.db_pool_min_size,
                max_size=self.config.systems.db_pool_max_size,
                max_queries=self.config.systems.db_max_queries,
                max_inactive_connection_lifetime=self.config.systems.db_max_inactive_lifetime,
                command_timeout=self.config.systems.db_command_timeout
            )
            
            # Create schema if needed
            await self._create_schema()
            
            logger.info("Database initialized with connection pool")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            # Continue without database for local tool
            self.pool = None
    
    async def _create_schema(self):
        """
        Create database schema for AI assistant
        Business Logic: Tables for cache, metrics, history, personas
        """
        async with self.pool.acquire() as conn:
            # Cache table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key VARCHAR(32) PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    size_bytes INTEGER,
                    tier VARCHAR(10) DEFAULT 'hot'
                )
            """)
            
            # Create index for expiration
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON cache_entries(expires_at)
            """)
            
            # Metrics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    metric_type VARCHAR(50) NOT NULL,
                    value JSONB NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversation history
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id SERIAL PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    response TEXT,
                    persona VARCHAR(50),
                    tokens_used INTEGER,
                    cached BOOLEAN DEFAULT FALSE,
                    execution_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Persona usage statistics
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS persona_usage (
                    persona VARCHAR(50) PRIMARY KEY,
                    usage_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    avg_confidence FLOAT DEFAULT 0,
                    last_used TIMESTAMP
                )
            """)
            
            # Performance logs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id SERIAL PRIMARY KEY,
                    operation VARCHAR(100),
                    duration_ms INTEGER,
                    success BOOLEAN,
                    details JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("Database schema created/verified")
    
    async def save_cache_entry(self, key: str, data: Dict, expires_at: datetime, tier: str = 'hot'):
        """
        Save cache entry to database
        Performance: <50ms insert time
        """
        if not self.pool:
            # Store in memory for testing when no database
            if not hasattr(self, '_mock_cache'):
                self._mock_cache = {}
            self._mock_cache[key] = data
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO cache_entries (key, data, expires_at, size_bytes, tier)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (key) DO UPDATE
                    SET data = $2, expires_at = $3, access_count = cache_entries.access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP, tier = $5
                """, key, json.dumps(data), expires_at, len(json.dumps(data)), tier)
                
        except Exception as e:
            logger.error(f"Failed to save cache entry: {e}")
    
    async def get_cache_entry(self, key: str) -> Optional[Dict]:
        """
        Retrieve cache entry from database
        Performance: <50ms query time
        """
        if not self.pool:
            # Return from memory mock when no database
            if hasattr(self, '_mock_cache'):
                return self._mock_cache.get(key)
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE key = $1 AND expires_at > CURRENT_TIMESTAMP
                    RETURNING data
                """, key)
                
                if row:
                    return json.loads(row['data'])
                    
        except Exception as e:
            logger.error(f"Failed to get cache entry: {e}")
        
        return None
    
    async def save_conversation(
        self,
        prompt: str,
        response: str,
        persona: Optional[str],
        tokens_used: int,
        cached: bool,
        execution_time_ms: int
    ):
        """Save conversation to history"""
        if not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO conversation_history 
                    (prompt, response, persona, tokens_used, cached, execution_time_ms)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, prompt, response, persona, tokens_used, cached, execution_time_ms)
                
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    async def update_persona_usage(self, persona: str, tokens: int, confidence: float):
        """Update persona usage statistics"""
        if not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO persona_usage (persona, usage_count, total_tokens, avg_confidence, last_used)
                    VALUES ($1, 1, $2, $3, CURRENT_TIMESTAMP)
                    ON CONFLICT (persona) DO UPDATE
                    SET usage_count = persona_usage.usage_count + 1,
                        total_tokens = persona_usage.total_tokens + $2,
                        avg_confidence = (persona_usage.avg_confidence * persona_usage.usage_count + $3) 
                                       / (persona_usage.usage_count + 1),
                        last_used = CURRENT_TIMESTAMP
                """, persona, tokens, confidence)
                
        except Exception as e:
            logger.error(f"Failed to update persona usage: {e}")
    
    async def get_persona_statistics(self) -> List[Dict]:
        """Get persona usage statistics"""
        if not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT persona, usage_count, total_tokens, avg_confidence, last_used
                    FROM persona_usage
                    ORDER BY usage_count DESC
                """)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get persona statistics: {e}")
            return []
    
    async def log_performance(self, operation: str, duration_ms: int, success: bool, details: Dict = None):
        """Log performance metrics"""
        if not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO performance_logs (operation, duration_ms, success, details)
                    VALUES ($1, $2, $3, $4)
                """, operation, duration_ms, success, json.dumps(details or {}))
                
        except Exception as e:
            logger.error(f"Failed to log performance: {e}")
    
    async def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        if not self.pool:
            return
        
        try:
            async with self.pool.acquire() as conn:
                deleted = await conn.execute("""
                    DELETE FROM cache_entries
                    WHERE expires_at < CURRENT_TIMESTAMP
                """)
                
                logger.info(f"Cleaned up {deleted} expired cache entries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
    
    async def get_metrics_summary(self) -> Dict:
        """Get summary of system metrics"""
        if not self.pool:
            return {}
        
        try:
            async with self.pool.acquire() as conn:
                # Cache statistics
                cache_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_entries,
                        SUM(access_count) as total_accesses,
                        AVG(access_count) as avg_accesses,
                        SUM(size_bytes) as total_size
                    FROM cache_entries
                    WHERE expires_at > CURRENT_TIMESTAMP
                """)
                
                # Conversation statistics
                conv_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_conversations,
                        AVG(tokens_used) as avg_tokens,
                        AVG(execution_time_ms) as avg_execution_time,
                        SUM(CASE WHEN cached THEN 1 ELSE 0 END) as cached_responses
                    FROM conversation_history
                    WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                """)
                
                return {
                    'cache': dict(cache_stats) if cache_stats else {},
                    'conversations': dict(conv_stats) if conv_stats else {}
                }
                
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")