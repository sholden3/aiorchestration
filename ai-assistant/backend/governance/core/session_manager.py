"""
File: ai-assistant/backend/governance/core/session_manager.py
Purpose: Manages user sessions with singleton pattern and timeout handling
Architecture: Provides centralized session management for the governance system
Dependencies: asyncio, datetime, typing, uuid
Owner: Dr. Sarah Chen

@fileoverview Session management with singleton pattern and automatic cleanup
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Singleton session manager with timeout and cleanup
@business_logic Session creation, validation, timeout management, automatic cleanup
@integration_points Governance validators, API endpoints, authentication systems
@error_handling Session limit enforcement, graceful expiry, cleanup on failure
@performance O(1) session operations, background cleanup task, memory efficient
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import asyncio
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """
    Represents a user session with metadata and lifecycle information.
    
    Attributes:
        id: Unique session identifier
        user_id: Associated user identifier
        created_at: Session creation timestamp
        last_accessed: Last activity timestamp
        metadata: Additional session data
        is_active: Whether session is currently active
    """
    id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def touch(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.utcnow()
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """
        Check if session has expired based on timeout.
        
        Args:
            timeout_seconds: Session timeout in seconds
            
        Returns:
            True if session has expired
        """
        if not self.is_active:
            return True
        
        expiry_time = self.last_accessed + timedelta(seconds=timeout_seconds)
        return datetime.utcnow() > expiry_time


class SessionManager:
    """
    Singleton session manager for centralized session handling.
    
    This class manages all active sessions, handles timeouts, and provides
    session validation capabilities. Implements singleton pattern to ensure
    only one instance exists across the application.
    """
    
    _instance: Optional['SessionManager'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls, *args, **kwargs):
        """
        Ensure singleton pattern - only one instance exists.
        
        Returns:
            The single SessionManager instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize session manager (only on first instantiation).
        
        Args:
            config: Session manager configuration
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
        
        self.config = config or {}
        self.sessions: Dict[str, Session] = {}
        self.timeout_seconds = self.config.get('session_timeout', 3600)
        self.max_sessions = self.config.get('max_sessions', 10000)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = True
        
        logger.info(f"SessionManager initialized with timeout={self.timeout_seconds}s")
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task for session cleanup."""
        try:
            loop = asyncio.get_running_loop()
            self._cleanup_task = loop.create_task(self._cleanup_expired_sessions())
        except RuntimeError:
            # No event loop running yet
            logger.debug("Cleanup task will start when event loop is available")
    
    async def _cleanup_expired_sessions(self):
        """
        Background task to clean up expired sessions periodically.
        
        Runs every minute to remove expired sessions and free memory.
        """
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                expired = []
                for session_id, session in self.sessions.items():
                    if session.is_expired(self.timeout_seconds):
                        expired.append(session_id)
                
                for session_id in expired:
                    await self.destroy_session(session_id)
                
                if expired:
                    logger.info(f"Cleaned up {len(expired)} expired sessions")
                    
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    async def create_session(self, user_id: Optional[str] = None, metadata: Dict[str, Any] = None) -> Session:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            metadata: Optional session metadata
            
        Returns:
            Created session object
            
        Raises:
            SessionLimitError: If maximum session limit reached
            
        Example:
            session = await manager.create_session(
                user_id="user123",
                metadata={'ip': '192.168.1.1'}
            )
        """
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Try cleanup first
            await self._cleanup_expired_sessions()
            if len(self.sessions) >= self.max_sessions:
                raise Exception(f"Maximum session limit ({self.max_sessions}) reached")
        
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        session = Session(
            id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session
        logger.debug(f"Created session {session_id} for user {user_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object if found and valid, None otherwise
        """
        session = self.sessions.get(session_id)
        
        if session and not session.is_expired(self.timeout_seconds):
            session.touch()  # Update last accessed
            return session
        
        return None
    
    async def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session exists and is active.
        
        Args:
            session_id: Session identifier to validate
            
        Returns:
            True if session is valid and active
        """
        session = await self.get_session(session_id)
        return session is not None and session.is_active
    
    async def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a session.
        
        Args:
            session_id: Session identifier to destroy
            
        Returns:
            True if session was destroyed, False if not found
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_active = False
            del self.sessions[session_id]
            logger.debug(f"Destroyed session {session_id}")
            return True
        
        return False
    
    async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session identifier
            metadata: Metadata to merge with existing
            
        Returns:
            True if updated successfully
        """
        session = await self.get_session(session_id)
        
        if session:
            session.metadata.update(metadata)
            return True
        
        return False
    
    def get_active_sessions(self) -> List[Session]:
        """
        Get all active (non-expired) sessions.
        
        Returns:
            List of active session objects
        """
        active = []
        for session in self.sessions.values():
            if not session.is_expired(self.timeout_seconds):
                active.append(session)
        
        return active
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session manager statistics.
        
        Returns:
            Dictionary containing:
                - total_sessions: Total number of sessions
                - active_sessions: Number of active sessions
                - expired_sessions: Number of expired sessions
                - oldest_session: Timestamp of oldest session
                - newest_session: Timestamp of newest session
        """
        active = self.get_active_sessions()
        total = len(self.sessions)
        expired = total - len(active)
        
        stats = {
            'total_sessions': total,
            'active_sessions': len(active),
            'expired_sessions': expired,
            'oldest_session': None,
            'newest_session': None
        }
        
        if self.sessions:
            sorted_sessions = sorted(self.sessions.values(), key=lambda s: s.created_at)
            stats['oldest_session'] = sorted_sessions[0].created_at.isoformat()
            stats['newest_session'] = sorted_sessions[-1].created_at.isoformat()
        
        return stats