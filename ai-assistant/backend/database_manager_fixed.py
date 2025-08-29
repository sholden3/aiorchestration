"""
@fileoverview Fixed database manager with race condition prevention (H3)
@author David Kim v2.0 & Dr. Sarah Chen v2.0 - 2025-08-29
@architecture Backend - Database initialization with concurrency control
@responsibility Manage database connections with atomic initialization
@dependencies asyncpg, asyncio, logging, enum, random
@integration_points FastAPI app startup, connection pooling, schema migrations
@testing_strategy Concurrent initialization tests, chaos testing, integration tests
@governance Implements agreed-upon patterns from round table discussion

Business Logic Summary:
- Atomic database initialization using advisory locks
- State machine for initialization phases
- Exponential backoff for connection retry
- Idempotent schema creation
- Separate pools for different operation types

Architecture Integration:
- Uses PostgreSQL advisory locks for distributed coordination
- Integrates with startup coordinator for health checks
- Provides observable state during initialization
- Supports both containerized and local deployments

Sarah's Framework Check:
- What breaks first: Connection attempt if DB unavailable
- How we know: State machine transitions to ERROR state
- Plan B: Exponential backoff retry with eventual degraded mode
"""

import asyncio
import asyncpg
import json
import random
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class DBState(Enum):
    """Database initialization states for observability"""
    UNINITIALIZED = "uninitialized"
    CONNECTING = "connecting"
    ACQUIRING_LOCK = "acquiring_lock"
    CHECKING_SCHEMA = "checking_schema"
    MIGRATING = "migrating"
    VALIDATING = "validating"
    READY = "ready"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class DBInitProgress:
    """Progress tracking for database initialization"""
    state: DBState
    progress: int  # 0-100
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[Exception] = None
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate initialization duration in milliseconds"""
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None


class DatabaseStateMachine:
    """
    State machine for tracking database initialization
    Provides observable state transitions and progress tracking
    """
    
    def __init__(self):
        self._state = DBState.UNINITIALIZED
        self._lock = asyncio.Lock()
        self._initialization_task: Optional[asyncio.Task] = None
        self._error: Optional[Exception] = None
        self._progress = DBInitProgress(
            state=DBState.UNINITIALIZED,
            progress=0,
            message="Not initialized",
            started_at=datetime.now()
        )
        self._transition_callbacks = []
        
    async def transition_to(self, new_state: DBState, progress: int = 0, message: str = ""):
        """
        Transition to a new state with progress update
        
        @param new_state The target state
        @param progress Progress percentage (0-100)
        @param message Human-readable status message
        """
        async with self._lock:
            old_state = self._state
            logger.info(f"DB State transition: {old_state.value} -> {new_state.value} ({progress}%)")
            
            self._state = new_state
            self._progress.state = new_state
            self._progress.progress = progress
            self._progress.message = message
            
            if new_state in [DBState.READY, DBState.ERROR, DBState.DEGRADED]:
                self._progress.completed_at = datetime.now()
            
            # Notify callbacks
            for callback in self._transition_callbacks:
                try:
                    await callback(old_state, new_state, self._progress)
                except Exception as e:
                    logger.error(f"Error in state transition callback: {e}")
    
    def register_callback(self, callback):
        """Register a callback for state transitions"""
        self._transition_callbacks.append(callback)
    
    @property
    def state(self) -> DBState:
        return self._state
    
    @property
    def is_ready(self) -> bool:
        return self._state == DBState.READY
    
    @property
    def is_initializing(self) -> bool:
        return self._state in [
            DBState.CONNECTING,
            DBState.ACQUIRING_LOCK,
            DBState.CHECKING_SCHEMA,
            DBState.MIGRATING,
            DBState.VALIDATING
        ]
    
    @property
    def progress(self) -> DBInitProgress:
        return self._progress
    
    def set_error(self, error: Exception):
        """Record an error that occurred during initialization"""
        self._error = error
        self._progress.error = error


class DatabaseManager:
    """
    Enhanced database manager with race condition prevention (H3 fix)
    Implements advisory locking and state machine patterns
    """
    
    # PostgreSQL advisory lock ID (unique for our application)
    ADVISORY_LOCK_ID = 314159265  # Using digits of pi for uniqueness
    
    def __init__(self, connection_string: str = None):
        """Initialize database manager with enhanced concurrency control"""
        from config import config
        self.config = config
        self.connection_string = connection_string or self._get_default_connection()
        
        # State machine for tracking initialization
        self.state_machine = DatabaseStateMachine()
        
        # Connection pools (separate for different operation types)
        self.app_pool: Optional[asyncpg.Pool] = None
        self.init_pool: Optional[asyncpg.Pool] = None  # Dedicated pool for initialization
        self.analytics_pool: Optional[asyncpg.Pool] = None  # For long-running queries
        
        # Track if we're the initializing process
        self._is_initializer = False
        self._initialization_lock = asyncio.Lock()
        
        logger.info("Enhanced DatabaseManager initialized with race condition prevention")
    
    def _get_default_connection(self) -> str:
        """Get PostgreSQL connection string from configuration"""
        import os
        host = os.getenv('DB_HOST', self.config.systems.db_host)
        port = os.getenv('DB_PORT', str(self.config.systems.db_port))
        user = os.getenv('DB_USER', self.config.systems.db_user)
        password = os.getenv('DB_PASSWORD', self.config.systems.db_password)
        database = os.getenv('DB_NAME', self.config.systems.db_name)
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def initialize(self) -> bool:
        """
        Initialize database with race condition prevention
        Uses advisory locks to ensure only one process initializes
        
        @returns True if initialization successful, False otherwise
        """
        # Prevent multiple initialization attempts in the same process
        async with self._initialization_lock:
            if self.state_machine.is_ready:
                logger.info("Database already initialized")
                return True
            
            if self.state_machine.is_initializing:
                logger.info("Database initialization already in progress")
                return await self._wait_for_initialization()
            
            try:
                # Start initialization
                await self.state_machine.transition_to(
                    DBState.CONNECTING, 10, "Connecting to database"
                )
                
                # Connect with retry
                conn = await self._connect_with_retry()
                
                # Try to acquire advisory lock
                await self.state_machine.transition_to(
                    DBState.ACQUIRING_LOCK, 20, "Acquiring initialization lock"
                )
                
                lock_acquired = await self._try_acquire_lock(conn)
                
                if lock_acquired:
                    # We are the initializer
                    self._is_initializer = True
                    await self._perform_initialization(conn)
                else:
                    # Another process is initializing
                    logger.info("Another process is initializing database, waiting...")
                    await conn.close()
                    return await self._wait_for_initialization()
                
                # Create connection pools
                await self._create_connection_pools()
                
                # Mark as ready
                await self.state_machine.transition_to(
                    DBState.READY, 100, "Database ready"
                )
                
                logger.info(f"Database initialization complete in {self.state_machine.progress.duration_ms:.1f}ms")
                return True
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                self.state_machine.set_error(e)
                await self.state_machine.transition_to(
                    DBState.ERROR, 0, f"Initialization failed: {str(e)}"
                )
                
                # Attempt degraded mode
                return await self._enter_degraded_mode()
            
            finally:
                # Release advisory lock if we hold it
                if self._is_initializer and 'conn' in locals():
                    try:
                        await self._release_lock(conn)
                        await conn.close()
                    except Exception as e:
                        logger.error(f"Error releasing lock: {e}")
    
    async def _connect_with_retry(self, max_attempts: int = 10) -> asyncpg.Connection:
        """
        Connect to database with exponential backoff retry
        
        @param max_attempts Maximum connection attempts
        @returns Database connection
        @raises ConnectionError if all attempts fail
        """
        for attempt in range(max_attempts):
            try:
                conn = await asyncpg.connect(
                    self.connection_string,
                    timeout=10,
                    command_timeout=10
                )
                logger.info(f"Connected to database on attempt {attempt + 1}")
                return conn
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ConnectionError(f"Failed to connect after {max_attempts} attempts: {e}")
                
                # Exponential backoff with jitter
                base_wait = min(2 ** attempt, 30)  # Cap at 30 seconds
                jitter = random.uniform(0, 1)
                wait_time = base_wait + jitter
                
                logger.warning(
                    f"Connection attempt {attempt + 1}/{max_attempts} failed, "
                    f"retrying in {wait_time:.1f}s: {e}"
                )
                
                await self.state_machine.transition_to(
                    DBState.CONNECTING,
                    10 + (attempt * 5),  # Increase progress with attempts
                    f"Retrying connection (attempt {attempt + 2}/{max_attempts})"
                )
                
                await asyncio.sleep(wait_time)
    
    async def _try_acquire_lock(self, conn: asyncpg.Connection) -> bool:
        """
        Try to acquire PostgreSQL advisory lock for initialization
        
        @param conn Database connection
        @returns True if lock acquired, False if already held
        """
        try:
            # pg_try_advisory_lock returns true if lock acquired, false if already held
            result = await conn.fetchval(
                'SELECT pg_try_advisory_lock($1)',
                self.ADVISORY_LOCK_ID
            )
            
            if result:
                logger.info(f"Acquired advisory lock {self.ADVISORY_LOCK_ID}")
            else:
                logger.info(f"Advisory lock {self.ADVISORY_LOCK_ID} already held by another process")
            
            return result
            
        except Exception as e:
            logger.error(f"Error acquiring advisory lock: {e}")
            raise
    
    async def _release_lock(self, conn: asyncpg.Connection):
        """
        Release PostgreSQL advisory lock
        
        @param conn Database connection
        """
        try:
            await conn.execute(
                'SELECT pg_advisory_unlock($1)',
                self.ADVISORY_LOCK_ID
            )
            logger.info(f"Released advisory lock {self.ADVISORY_LOCK_ID}")
        except Exception as e:
            logger.error(f"Error releasing advisory lock: {e}")
    
    async def _perform_initialization(self, conn: asyncpg.Connection):
        """
        Perform actual database initialization (schema creation, migrations)
        
        @param conn Database connection with advisory lock held
        """
        # Check schema version
        await self.state_machine.transition_to(
            DBState.CHECKING_SCHEMA, 30, "Checking schema version"
        )
        
        schema_exists = await self._check_schema_exists(conn)
        
        if not schema_exists:
            # Create schema
            await self.state_machine.transition_to(
                DBState.MIGRATING, 50, "Creating database schema"
            )
            await self._create_schema(conn)
        else:
            # Check for pending migrations
            await self.state_machine.transition_to(
                DBState.MIGRATING, 50, "Checking for migrations"
            )
            await self._run_migrations(conn)
        
        # Validate schema
        await self.state_machine.transition_to(
            DBState.VALIDATING, 80, "Validating database schema"
        )
        await self._validate_schema(conn)
    
    async def _check_schema_exists(self, conn: asyncpg.Connection) -> bool:
        """
        Check if database schema exists
        
        @param conn Database connection
        @returns True if schema exists
        """
        try:
            # Check if our main tables exist
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'cache_entries'
                )
            """)
            return result
        except Exception as e:
            logger.error(f"Error checking schema: {e}")
            return False
    
    async def _create_schema(self, conn: asyncpg.Connection):
        """
        Create database schema (idempotent operation)
        
        @param conn Database connection
        """
        # Each operation wrapped in transaction for atomicity
        async with conn.transaction():
            # Migration tracking table (must be first)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
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
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp DESC)
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
            
            # Record initial schema creation
            await conn.execute("""
                INSERT INTO schema_migrations (name) 
                VALUES ('initial_schema')
                ON CONFLICT (name) DO NOTHING
            """)
            
            logger.info("Database schema created successfully")
    
    async def _run_migrations(self, conn: asyncpg.Connection):
        """
        Run any pending database migrations (idempotent)
        
        @param conn Database connection
        """
        # Define migrations (would normally load from files)
        migrations = [
            # Add new migrations here as needed
            # Each migration should be idempotent
        ]
        
        for migration in migrations:
            # Check if already applied
            applied = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM schema_migrations WHERE name = $1)',
                migration['name']
            )
            
            if not applied:
                logger.info(f"Applying migration: {migration['name']}")
                async with conn.transaction():
                    await conn.execute(migration['sql'])
                    await conn.execute(
                        'INSERT INTO schema_migrations (name) VALUES ($1)',
                        migration['name']
                    )
    
    async def _validate_schema(self, conn: asyncpg.Connection):
        """
        Validate that all required tables and indexes exist
        
        @param conn Database connection
        @raises ValueError if schema validation fails
        """
        required_tables = [
            'schema_migrations',
            'cache_entries',
            'metrics',
            'conversation_history',
            'persona_usage',
            'performance_logs'
        ]
        
        for table in required_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = $1
                )
            """, table)
            
            if not exists:
                raise ValueError(f"Required table '{table}' does not exist")
        
        logger.info("Schema validation successful")
    
    async def _create_connection_pools(self):
        """Create separate connection pools for different operation types"""
        await self.state_machine.transition_to(
            DBState.VALIDATING, 90, "Creating connection pools"
        )
        
        # Main application pool
        self.app_pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=self.config.systems.db_pool_min_size,
            max_size=self.config.systems.db_pool_max_size,
            max_queries=self.config.systems.db_max_queries,
            max_inactive_connection_lifetime=self.config.systems.db_max_inactive_lifetime,
            command_timeout=self.config.systems.db_command_timeout
        )
        
        # Smaller pool for initialization operations
        self.init_pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=1,
            max_size=2,
            command_timeout=30
        )
        
        # Pool for long-running analytics queries
        self.analytics_pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=1,
            max_size=3,
            command_timeout=120  # 2 minutes for analytics
        )
        
        logger.info("Connection pools created successfully")
    
    async def _wait_for_initialization(self, timeout: int = 60) -> bool:
        """
        Wait for another process to complete initialization
        
        @param timeout Maximum wait time in seconds
        @returns True if initialization completed, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 1.0  # Check every second
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                # Try to connect and check if schema is ready
                conn = await asyncpg.connect(
                    self.connection_string,
                    timeout=5,
                    command_timeout=5
                )
                
                schema_ready = await self._check_schema_exists(conn)
                await conn.close()
                
                if schema_ready:
                    logger.info("Database initialized by another process")
                    
                    # Create our connection pools
                    await self._create_connection_pools()
                    
                    await self.state_machine.transition_to(
                        DBState.READY, 100, "Database ready"
                    )
                    return True
                
            except Exception as e:
                logger.debug(f"Still waiting for database initialization: {e}")
            
            await asyncio.sleep(check_interval)
        
        logger.error("Timeout waiting for database initialization")
        return False
    
    async def _enter_degraded_mode(self) -> bool:
        """
        Enter degraded mode when database is unavailable
        Allows application to function with limited capabilities
        
        @returns True if degraded mode successful
        """
        logger.warning("Entering degraded mode - database unavailable")
        
        await self.state_machine.transition_to(
            DBState.DEGRADED, 0, "Running in degraded mode (no database)"
        )
        
        # In degraded mode, we don't have database pools
        self.app_pool = None
        self.init_pool = None
        self.analytics_pool = None
        
        return True
    
    async def get_connection(self, query_type: str = 'app') -> Optional[asyncpg.Connection]:
        """
        Get a database connection from the appropriate pool
        
        @param query_type Type of query: 'app', 'init', or 'analytics'
        @returns Database connection or None in degraded mode
        """
        if self.state_machine.state == DBState.DEGRADED:
            return None
        
        if not self.state_machine.is_ready:
            raise RuntimeError(f"Database not ready: {self.state_machine.state.value}")
        
        pool_map = {
            'app': self.app_pool,
            'init': self.init_pool,
            'analytics': self.analytics_pool
        }
        
        pool = pool_map.get(query_type, self.app_pool)
        if pool:
            return await pool.acquire()
        
        return None
    
    async def release_connection(self, conn: asyncpg.Connection, query_type: str = 'app'):
        """
        Release a database connection back to pool
        
        @param conn Connection to release
        @param query_type Type of query pool
        """
        if conn:
            pool_map = {
                'app': self.app_pool,
                'init': self.init_pool,
                'analytics': self.analytics_pool
            }
            
            pool = pool_map.get(query_type, self.app_pool)
            if pool:
                await pool.release(conn)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check
        
        @returns Health status dictionary
        """
        health = {
            'healthy': False,
            'state': self.state_machine.state.value,
            'initialized': self.state_machine.is_ready,
            'progress': self.state_machine.progress.progress,
            'message': self.state_machine.progress.message
        }
        
        if self.state_machine.is_ready and self.app_pool:
            try:
                async with self.app_pool.acquire() as conn:
                    # Simple query to verify connection
                    await conn.fetchval('SELECT 1')
                    health['healthy'] = True
                    health['pool_size'] = self.app_pool.get_size()
                    health['pool_available'] = self.app_pool.get_idle_size()
            except Exception as e:
                health['error'] = str(e)
        elif self.state_machine.state == DBState.DEGRADED:
            health['degraded'] = True
            health['healthy'] = True  # Degraded but operational
        
        return health
    
    async def shutdown(self):
        """Gracefully shutdown database connections"""
        logger.info("Shutting down database manager")
        
        if self.app_pool:
            await self.app_pool.close()
        if self.init_pool:
            await self.init_pool.close()
        if self.analytics_pool:
            await self.analytics_pool.close()
        
        await self.state_machine.transition_to(
            DBState.UNINITIALIZED, 0, "Shut down"
        )


# Convenience function for FastAPI integration
async def get_database_manager() -> DatabaseManager:
    """
    Get or create database manager instance
    Used for dependency injection in FastAPI
    """
    if not hasattr(get_database_manager, '_instance'):
        get_database_manager._instance = DatabaseManager()
        await get_database_manager._instance.initialize()
    
    return get_database_manager._instance