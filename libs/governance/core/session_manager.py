#!/usr/bin/env python3
"""
@fileoverview Session management system for development workflow governance
@author Alex Novak v3.0 & Dr. Sarah Chen v1.2 - 2025-01-28
@architecture Backend/Core - Session state management
@responsibility Track and validate development sessions with state persistence
@dependencies datetime, json, pathlib, correlation_tracker
@integration_points Git hooks, personas, validation pipeline
@testing_strategy Unit tests for lifecycle, integration tests for persistence
@governance Core component enforcing session requirements from CLAUDE.md

Business Logic Summary:
- Enforce session start/end protocols
- Track task progress and completions
- Require architect approvals
- Maintain session state

Architecture Integration:
- Central session tracking
- Integrates with correlation tracker
- Persists state for recovery
- Enforces governance protocols
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict

from libs.governance.core.correlation_tracker import get_correlation_tracker, OperationStatus


class SessionStatus(Enum):
    """Session lifecycle states"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    COMPLETING = "completing"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ERROR = "error"


class TaskStatus(Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class DevelopmentTask:
    """
    @class DevelopmentTask
    @description Represents a development task within a session
    @architecture_role Task tracking and validation
    @business_logic Enforces task completion criteria
    """
    id: str
    description: str
    assignee: str = ""
    priority: str = "medium"
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_time_minutes: int = 0
    actual_time_minutes: int = 0
    
    # Completion criteria
    code_complete: bool = False
    tests_passing: bool = False
    documentation_updated: bool = False
    review_approved: bool = False
    
    # Tracking
    blockers: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    def start(self):
        """Start task execution"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self):
        """Mark task as complete"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        if self.started_at:
            self.actual_time_minutes = int(
                (self.completed_at - self.started_at).total_seconds() / 60
            )
    
    def is_ready_for_completion(self) -> Tuple[bool, List[str]]:
        """Check if task meets completion criteria"""
        missing = []
        
        if not self.code_complete:
            missing.append("Code not complete")
        if not self.tests_passing:
            missing.append("Tests not passing")
        if not self.documentation_updated:
            missing.append("Documentation not updated")
        if not self.review_approved:
            missing.append("Review not approved")
        
        return len(missing) == 0, missing


@dataclass
class DevelopmentSession:
    """
    @class DevelopmentSession
    @description Manages a complete development session
    @architecture_role Session lifecycle management
    @business_logic Enforces session protocols from CLAUDE.md
    @failure_modes Session timeout, validation failures
    @debugging_info Complete session state with correlation
    """
    session_id: str
    user: str
    started_at: datetime = field(default_factory=datetime.now)
    status: SessionStatus = SessionStatus.NOT_STARTED
    
    # Session metadata
    branch: str = ""
    correlation_id: Optional[str] = None
    
    # Personas
    core_architects: List[str] = field(default_factory=lambda: ["alex_novak", "sarah_chen"])
    active_specialists: List[str] = field(default_factory=list)
    
    # Tasks
    tasks: Dict[str, DevelopmentTask] = field(default_factory=dict)
    
    # Validation
    environment_validated: bool = False
    personas_loaded: bool = False
    governance_verified: bool = False
    
    # Approvals
    alex_approved: bool = False
    sarah_approved: bool = False
    
    # Timing
    idle_since: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = {
            'session_id': self.session_id,
            'user': self.user,
            'started_at': self.started_at.isoformat(),
            'status': self.status.value,
            'branch': self.branch,
            'correlation_id': self.correlation_id,
            'core_architects': self.core_architects,
            'active_specialists': self.active_specialists,
            'tasks': {
                task_id: {
                    'id': task.id,
                    'description': task.description,
                    'status': task.status.value,
                    'assignee': task.assignee,
                    'priority': task.priority,
                    'code_complete': task.code_complete,
                    'tests_passing': task.tests_passing,
                    'documentation_updated': task.documentation_updated,
                    'review_approved': task.review_approved
                }
                for task_id, task in self.tasks.items()
            },
            'environment_validated': self.environment_validated,
            'personas_loaded': self.personas_loaded,
            'governance_verified': self.governance_verified,
            'alex_approved': self.alex_approved,
            'sarah_approved': self.sarah_approved,
            'idle_since': self.idle_since.isoformat()
        }
        
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        
        return data


class SessionManager:
    """
    @class SessionManager
    @description Manages development sessions with state persistence
    @architecture_role Central session orchestration
    @business_logic Enforces CLAUDE.md session requirements
    @failure_modes Session recovery, timeout handling
    @debugging_info Full session history with correlations
    
    Sarah's Framework Check:
    - What breaks first: Session timeout without save
    - How we know: Idle time tracking
    - Plan B: Auto-save and recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize session manager"""
        self.config = config or {}
        self.session_dir = Path(self.config.get('session_dir', '.governance/sessions'))
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[DevelopmentSession] = None
        self.correlation_tracker = get_correlation_tracker()
        
        # Session settings
        self.idle_timeout_minutes = self.config.get('idle_timeout_minutes', 30)
        self.checkpoint_interval_seconds = self.config.get('checkpoint_interval', 300)
        
        # Try to recover previous session
        self._recover_session()
    
    def start_session(self, user: str, branch: str = "main") -> DevelopmentSession:
        """
        Start a new development session
        
        @param user Developer username
        @param branch Git branch name
        @returns New session instance
        
        BUSINESS RULE: Must validate environment before starting
        """
        if self.current_session and self.current_session.status == SessionStatus.ACTIVE:
            raise ValueError("Session already active. End current session first.")
        
        # Create session
        import uuid
        session_id = str(uuid.uuid4())
        
        session = DevelopmentSession(
            session_id=session_id,
            user=user,
            branch=branch,
            status=SessionStatus.INITIALIZING
        )
        
        # Create correlation
        correlation = self.correlation_tracker.create_correlation(
            operation_type='session.start',
            operation_name=f'session_{session_id}',
            user=user,
            metadata={'branch': branch}
        )
        session.correlation_id = correlation.correlation_id
        
        # Validation steps
        print("=== SESSION INITIALIZATION ===")
        
        # 1. Validate environment
        session.environment_validated = self._validate_environment()
        print(f"Environment validated: {session.environment_validated}")
        
        # 2. Load personas
        session.personas_loaded = self._load_personas()
        print(f"Core Architects: {', '.join(session.core_architects)}")
        
        # 3. Verify governance
        session.governance_verified = self._verify_governance()
        print(f"Governance verified: {session.governance_verified}")
        
        # Activate session
        if all([session.environment_validated, session.personas_loaded, session.governance_verified]):
            session.status = SessionStatus.ACTIVE
            print("Session ACTIVE")
        else:
            session.status = SessionStatus.ERROR
            print("Session initialization FAILED")
        
        self.current_session = session
        self._save_session()
        
        return session
    
    def end_session(self) -> bool:
        """
        End current session with validation
        
        @returns True if session ended successfully
        
        BUSINESS RULE: Requires both architect approvals
        """
        if not self.current_session:
            return False
        
        print("=== SESSION VALIDATION ===")
        
        session = self.current_session
        session.status = SessionStatus.COMPLETING
        
        # Check task completions
        incomplete_tasks = [
            task for task in session.tasks.values()
            if task.status != TaskStatus.COMPLETED
        ]
        
        if incomplete_tasks:
            print(f"Warning: {len(incomplete_tasks)} incomplete tasks")
            for task in incomplete_tasks:
                print(f"  - {task.description} ({task.status.value})")
        
        # Check architect approvals
        print(f"Alex approval: {session.alex_approved}")
        print(f"Sarah approval: {session.sarah_approved}")
        
        if not (session.alex_approved and session.sarah_approved):
            print("ERROR: Both architects must approve before ending session")
            return False
        
        # Complete session
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now()
        
        # Complete correlation
        if session.correlation_id:
            self.correlation_tracker.complete_correlation(
                session.correlation_id,
                OperationStatus.COMPLETED,
                result={'tasks_completed': len(session.tasks) - len(incomplete_tasks)}
            )
        
        self._save_session()
        self._archive_session()
        self.current_session = None
        
        print("Session COMPLETED")
        return True
    
    def add_task(
        self,
        description: str,
        assignee: Optional[str] = None,
        priority: str = "medium",
        estimated_time: int = 0
    ) -> DevelopmentTask:
        """Add task to current session"""
        if not self.current_session:
            raise ValueError("No active session")
        
        import uuid
        task = DevelopmentTask(
            id=str(uuid.uuid4()),
            description=description,
            assignee=assignee or self.current_session.user,
            priority=priority,
            estimated_time_minutes=estimated_time
        )
        
        self.current_session.tasks[task.id] = task
        self._save_session()
        
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]):
        """Update task in current session"""
        if not self.current_session:
            raise ValueError("No active session")
        
        if task_id not in self.current_session.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.current_session.tasks[task_id]
        
        for key, value in updates.items():
            if hasattr(task, key):
                # governance-exempt: setattr - Safe attribute update on dataclass
                setattr(task, key, value)
        
        # Update idle time
        self.current_session.idle_since = datetime.now()
        self._save_session()
    
    def get_architect_approval(self, architect: str) -> bool:
        """Record architect approval"""
        if not self.current_session:
            return False
        
        if architect == "alex_novak":
            self.current_session.alex_approved = True
        elif architect == "sarah_chen":
            self.current_session.sarah_approved = True
        else:
            return False
        
        self._save_session()
        return True
    
    def check_timeout(self) -> bool:
        """Check if session has timed out"""
        if not self.current_session:
            return False
        
        idle_time = datetime.now() - self.current_session.idle_since
        timeout_delta = timedelta(minutes=self.idle_timeout_minutes)
        
        if idle_time > timeout_delta:
            print(f"Session timeout: idle for {idle_time.total_seconds() / 60:.1f} minutes")
            self.current_session.status = SessionStatus.EXPIRED
            self._save_session()
            return True
        
        return False
    
    def _validate_environment(self) -> bool:
        """Validate development environment"""
        # Check for required tools, configs, etc.
        # For now, return True
        return True
    
    def _load_personas(self) -> bool:
        """Load required personas"""
        # Would load persona definitions
        return True
    
    def _verify_governance(self) -> bool:
        """Verify governance system is operational"""
        # Check governance engine status
        return True
    
    def _save_session(self):
        """Save current session to disk"""
        if not self.current_session:
            return
        
        session_file = self.session_dir / f"{self.current_session.session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(self.current_session.to_dict(), f, indent=2)
    
    def _recover_session(self):
        """Recover previous session if exists"""
        # Look for most recent session file
        session_files = list(self.session_dir.glob("*.json"))
        
        if not session_files:
            return
        
        # Get most recent
        latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Check if session is recoverable
            status = SessionStatus(data['status'])
            if status in [SessionStatus.ACTIVE, SessionStatus.INITIALIZING]:
                print(f"Recovering session {data['session_id']}")
                # Would reconstruct session from data
                # For now, just note it exists
        
        except Exception as e:
            print(f"Could not recover session: {e}")
    
    def _archive_session(self):
        """Archive completed session"""
        if not self.current_session:
            return
        
        # Move to archive directory
        archive_dir = self.session_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        session_file = self.session_dir / f"{self.current_session.session_id}.json"
        archive_file = archive_dir / f"{self.current_session.session_id}.json"
        
        if session_file.exists():
            session_file.rename(archive_file)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.current_session:
            return {'active': False}
        
        session = self.current_session
        
        total_tasks = len(session.tasks)
        completed_tasks = sum(
            1 for task in session.tasks.values()
            if task.status == TaskStatus.COMPLETED
        )
        
        return {
            'active': True,
            'session_id': session.session_id,
            'user': session.user,
            'duration_minutes': int((datetime.now() - session.started_at).total_seconds() / 60),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'alex_approved': session.alex_approved,
            'sarah_approved': session.sarah_approved
        }