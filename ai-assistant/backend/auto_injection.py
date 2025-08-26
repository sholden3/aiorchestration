"""
Auto-Injection Session Management System
Automatically injects context and session state for AI agents
Evidence-Based Implementation with Cross-Persona Validation
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from base_patterns import OrchestrationResult
from specialized_databases import SpecializedDatabases
from rules_enforcement import RulesEnforcementEngine

logger = logging.getLogger(__name__)

class InjectionType(Enum):
    """Types of context injection"""
    SYSTEM_PROMPT = "system_prompt"      # Base system instructions
    CONTEXT = "context"                  # Current context/state
    RULES = "rules"                      # Governance rules
    MEMORY = "memory"                    # Historical patterns
    CONSTRAINTS = "constraints"          # Operational constraints

class SessionState:
    """Maintains state for an agent session"""
    
    def __init__(self, session_id: str, agent_id: str):
        self.session_id = session_id
        self.agent_id = agent_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.injection_history: List[Dict] = []
        self.context_stack: List[Dict] = []
        self.max_context_depth = 10
        self.metrics = {
            'total_injections': 0,
            'successful_injections': 0,
            'failed_injections': 0,
            'context_switches': 0
        }
    
    def add_injection(self, injection_type: InjectionType, content: Any, success: bool):
        """Record an injection"""
        self.injection_history.append({
            'type': injection_type.value,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'content_hash': hashlib.md5(str(content).encode()).hexdigest()[:8]
        })
        
        self.metrics['total_injections'] += 1
        if success:
            self.metrics['successful_injections'] += 1
        else:
            self.metrics['failed_injections'] += 1
        
        self.last_updated = datetime.now()
    
    def push_context(self, context: Dict):
        """Push new context onto stack"""
        self.context_stack.append({
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
        # Maintain max depth
        if len(self.context_stack) > self.max_context_depth:
            self.context_stack = self.context_stack[-self.max_context_depth:]
        
        self.metrics['context_switches'] += 1
    
    def get_current_context(self) -> Optional[Dict]:
        """Get current context from top of stack"""
        if self.context_stack:
            return self.context_stack[-1]['context']
        return None
    
    def to_dict(self) -> Dict:
        """Convert session state to dictionary"""
        return {
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'metrics': self.metrics,
            'current_context': self.get_current_context(),
            'context_depth': len(self.context_stack),
            'recent_injections': self.injection_history[-5:]
        }

class AutoInjectionManager:
    """
    Manages automatic context injection for AI agents
    Sarah: Ensures consistent agent context
    Marcus: Efficient context management with caching
    Emily: Clear session state visibility
    """
    
    def __init__(self, db: Optional[SpecializedDatabases] = None,
                 rules_engine: Optional[RulesEnforcementEngine] = None):
        self.db = db or SpecializedDatabases()
        self.rules_engine = rules_engine or RulesEnforcementEngine()
        self.sessions: Dict[str, SessionState] = {}
        self.injection_templates: Dict[InjectionType, str] = {}
        self.max_sessions = 100
        self.session_timeout_hours = 24
        
        # Initialize default injection templates
        self._initialize_templates()
        
        logger.info("Auto-injection manager initialized")
    
    def _initialize_templates(self):
        """Initialize default injection templates"""
        self.injection_templates[InjectionType.SYSTEM_PROMPT] = """
You are an AI assistant with the following core principles:
- Evidence-based reasoning only
- No assumptions without verification
- Clear communication of uncertainty
- Measurement and validation required for all claims
"""
        
        self.injection_templates[InjectionType.RULES] = """
Governance Rules:
1. No magic variables or hardcoded values
2. All performance claims require evidence
3. Cross-validation required for critical decisions
4. Zero tolerance for unverified assumptions
"""
        
        self.injection_templates[InjectionType.CONSTRAINTS] = """
Operational Constraints:
- Session timeout: 24 hours
- Maximum context depth: 10 levels
- Evidence required for all optimizations
- Mandatory error handling for all operations
"""
    
    async def create_session(self, agent_id: str, initial_context: Optional[Dict] = None) -> OrchestrationResult[str]:
        """
        Create new auto-injection session
        Marcus: Measured session creation performance
        """
        import time
        start_time = time.perf_counter()
        
        # Check session limits
        if len(self.sessions) >= self.max_sessions:
            # Clean up old sessions first
            await self.cleanup_expired_sessions()
            
            if len(self.sessions) >= self.max_sessions:
                return OrchestrationResult.error(
                    f"Maximum sessions ({self.max_sessions}) reached"
                )
        
        # Generate session ID
        session_id = f"{agent_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create session state
        session = SessionState(session_id, agent_id)
        
        # Set initial context if provided
        if initial_context:
            session.push_context(initial_context)
        
        # Perform initial injections
        success = await self._perform_initial_injections(session)
        
        if success:
            self.sessions[session_id] = session
            creation_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"Session {session_id} created in {creation_ms:.2f}ms")
            return OrchestrationResult.ok(session_id, creation_ms=creation_ms)
        else:
            return OrchestrationResult.error("Failed to perform initial injections")
    
    async def _perform_initial_injections(self, session: SessionState) -> bool:
        """Perform initial context injections for session"""
        required_injections = [
            InjectionType.SYSTEM_PROMPT,
            InjectionType.RULES,
            InjectionType.CONSTRAINTS
        ]
        
        for injection_type in required_injections:
            content = self.injection_templates.get(injection_type, "")
            
            # Validate injection doesn't contain assumptions
            validation = await self.rules_engine.enforce_assumption_prevention(content)
            if validation.success and validation.metadata.get('changes'):
                content = validation.data
                logger.info(f"Cleaned assumptions from {injection_type.value}")
            
            session.add_injection(injection_type, content, True)
        
        return True
    
    async def inject_context(
        self,
        session_id: str,
        injection_type: InjectionType,
        content: Any
    ) -> OrchestrationResult[bool]:
        """
        Inject context into session
        Sarah: Validates context before injection
        """
        session = self.sessions.get(session_id)
        if not session:
            return OrchestrationResult.error(f"Session {session_id} not found")
        
        # Validate content with rules engine
        validation_result = await self.rules_engine.check_pre_execution(
            action=f"inject_{injection_type.value}",
            context={'content': content}
        )
        
        if not validation_result.success:
            session.add_injection(injection_type, content, False)
            return OrchestrationResult.error(
                f"Injection blocked by rules: {validation_result.error}"
            )
        
        # Perform injection
        try:
            if injection_type == InjectionType.CONTEXT:
                session.push_context(content)
            
            session.add_injection(injection_type, content, True)
            logger.debug(f"Injected {injection_type.value} into session {session_id}")
            
            return OrchestrationResult.ok(True)
            
        except Exception as e:
            logger.error(f"Injection failed: {e}")
            session.add_injection(injection_type, content, False)
            return OrchestrationResult.error(str(e))
    
    async def get_session_context(self, session_id: str) -> OrchestrationResult[Dict]:
        """
        Get current session context
        Emily: Returns clear session state
        """
        session = self.sessions.get(session_id)
        if not session:
            return OrchestrationResult.error(f"Session {session_id} not found")
        
        context = {
            'session_state': session.to_dict(),
            'current_context': session.get_current_context(),
            'injection_templates': {
                k.value: v[:100] + "..." if len(v) > 100 else v
                for k, v in self.injection_templates.items()
            }
        }
        
        return OrchestrationResult.ok(context)
    
    async def inject_learning_patterns(
        self,
        session_id: str,
        pattern_category: Optional[str] = None
    ) -> OrchestrationResult[int]:
        """
        Inject relevant learning patterns from database
        Marcus: Efficiently retrieves and caches patterns
        """
        session = self.sessions.get(session_id)
        if not session:
            return OrchestrationResult.error(f"Session {session_id} not found")
        
        if not self.db.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        # Get relevant patterns
        patterns = await self.db.get_learning_patterns(
            category=pattern_category,
            limit=10
        )
        
        if patterns:
            # Build pattern context
            pattern_context = {
                'learned_patterns': [
                    {
                        'pattern': p.pattern,
                        'category': p.category,
                        'success_rate': p.success_rate
                    }
                    for p in patterns
                    if p.success_rate > 0.7  # Only inject successful patterns
                ]
            }
            
            # Inject as memory
            result = await self.inject_context(
                session_id,
                InjectionType.MEMORY,
                pattern_context
            )
            
            if result.success:
                logger.info(f"Injected {len(pattern_context['learned_patterns'])} patterns")
                return OrchestrationResult.ok(len(pattern_context['learned_patterns']))
        
        return OrchestrationResult.ok(0)
    
    async def rotate_context(self, session_id: str, new_context: Dict) -> OrchestrationResult[bool]:
        """
        Rotate to new context while preserving history
        Emily: Maintains clear context transitions
        """
        session = self.sessions.get(session_id)
        if not session:
            return OrchestrationResult.error(f"Session {session_id} not found")
        
        # Validate new context
        validation = await self.rules_engine.validate_data(
            new_context,
            "context_rotation"
        )
        
        if not validation.success:
            return OrchestrationResult.error(
                f"Context validation failed: {validation.error}"
            )
        
        # Push new context
        session.push_context(new_context)
        
        return OrchestrationResult.ok(
            True,
            context_depth=len(session.context_stack)
        )
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        Marcus: Efficient resource management
        """
        now = datetime.now()
        timeout = timedelta(hours=self.session_timeout_hours)
        
        expired = []
        for session_id, session in self.sessions.items():
            if now - session.last_updated > timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session {session_id}")
        
        return len(expired)
    
    def get_active_sessions(self) -> List[Dict]:
        """Get list of active sessions"""
        return [
            {
                'session_id': sid,
                'agent_id': session.agent_id,
                'created_at': session.created_at.isoformat(),
                'last_updated': session.last_updated.isoformat(),
                'metrics': session.metrics
            }
            for sid, session in self.sessions.items()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get injection manager statistics
        Marcus: Real metrics from actual operations
        """
        total_injections = sum(s.metrics['total_injections'] for s in self.sessions.values())
        successful = sum(s.metrics['successful_injections'] for s in self.sessions.values())
        failed = sum(s.metrics['failed_injections'] for s in self.sessions.values())
        
        return {
            'active_sessions': len(self.sessions),
            'max_sessions': self.max_sessions,
            'total_injections': total_injections,
            'successful_injections': successful,
            'failed_injections': failed,
            'success_rate': successful / total_injections if total_injections > 0 else 0,
            'avg_context_depth': sum(len(s.context_stack) for s in self.sessions.values()) / len(self.sessions) if self.sessions else 0,
            'sessions_by_agent': {}  # Would group by agent_id
        }
    
    async def export_session(self, session_id: str) -> OrchestrationResult[Dict]:
        """Export session state for persistence or analysis"""
        session = self.sessions.get(session_id)
        if not session:
            return OrchestrationResult.error(f"Session {session_id} not found")
        
        export_data = {
            'session': session.to_dict(),
            'injection_history': session.injection_history,
            'context_stack': session.context_stack,
            'export_timestamp': datetime.now().isoformat()
        }
        
        return OrchestrationResult.ok(export_data)
    
    async def import_session(self, session_data: Dict) -> OrchestrationResult[str]:
        """Import previously exported session"""
        try:
            # Validate session data structure
            required_keys = ['session', 'injection_history', 'context_stack']
            if not all(k in session_data for k in required_keys):
                return OrchestrationResult.error("Invalid session data structure")
            
            # Create new session
            session_info = session_data['session']
            session = SessionState(
                session_info['session_id'],
                session_info['agent_id']
            )
            
            # Restore state
            session.injection_history = session_data['injection_history']
            session.context_stack = session_data['context_stack']
            session.metrics = session_info.get('metrics', session.metrics)
            
            self.sessions[session.session_id] = session
            
            logger.info(f"Imported session {session.session_id}")
            return OrchestrationResult.ok(session.session_id)
            
        except Exception as e:
            logger.error(f"Session import failed: {e}")
            return OrchestrationResult.error(str(e))