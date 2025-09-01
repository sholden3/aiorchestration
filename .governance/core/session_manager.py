#!/usr/bin/env python3
"""
@fileoverview Centralized session management for governance system
@author Marcus Rivera v1.0 - DevOps Specialist
@architecture Infrastructure - Session lifecycle management
@business_logic Handles session creation, validation, expiry, and archival
"""

import json
import os
import sys
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class SessionStatus(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    WARNING = "warning"
    EXPIRED = "expired"
    ENDED = "ended"
    INVALID = "invalid"

@dataclass
class SessionInfo:
    """Session data structure"""
    session_id: str
    start_time: str  # ISO format with timezone
    architects: list
    status: str
    environment: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class SessionManager:
    """Manages development session lifecycle"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.root_dir = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.root_dir / ".governance/config/governance-config.json"
        self.config = self._load_config()
        self.session_file = self.root_dir / self.config["session"]["storage_path"]
        self.platform_config = self._get_platform_config()
        
    def _load_config(self) -> Dict:
        """Load governance configuration"""
        if not self.config_path.exists():
            return self._default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config: {e}", file=sys.stderr)
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Fallback configuration"""
        return {
            "session": {
                "max_duration_hours": 8,
                "warning_threshold_hours": 7,
                "timezone": "UTC",
                "storage_path": ".governance/session/current.json"
            },
            "platform": {
                "windows": {"python_command": "python"},
                "unix": {"python_command": "python3"}
            }
        }
    
    def _get_platform_config(self) -> Dict:
        """Get platform-specific configuration"""
        is_windows = platform.system().lower() == "windows"
        platform_key = "windows" if is_windows else "unix"
        return self.config.get("platform", {}).get(platform_key, {})
    
    def create_session(self, architects: Optional[list] = None) -> SessionInfo:
        """Create a new development session"""
        session_id = str(int(datetime.now().timestamp()))
        
        # Use UTC for consistency
        start_time = datetime.now(timezone.utc).isoformat()
        
        # Get architects from config if not provided
        if architects is None:
            architects = self.config.get("session", {}).get("require_architects", 
                                                            ["Alex Novak", "Dr. Sarah Chen"])
        
        # Capture environment info
        environment = {
            "platform": platform.system(),
            "python_version": sys.version.split()[0],
            "working_directory": str(Path.cwd()),
            "timezone": str(datetime.now().astimezone().tzinfo),
            "encoding": sys.getdefaultencoding()
        }
        
        session = SessionInfo(
            session_id=session_id,
            start_time=start_time,
            architects=architects,
            status=SessionStatus.ACTIVE.value,
            environment=environment,
            metadata={"created_by": "session_manager", "version": "1.0.0"}
        )
        
        # Ensure directory exists
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save session
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2)
        
        return session
    
    def validate_session(self) -> Tuple[bool, str, Optional[SessionInfo]]:
        """
        Validate current session status
        Returns: (is_valid, message, session_info)
        """
        if not self.session_file.exists():
            return False, "No session found. Run: ./validate-session-start.sh", None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = SessionInfo.from_dict(data)
            
            # Parse start time with timezone awareness
            start_time_str = session.start_time
            
            # Handle different time formats
            if start_time_str.endswith('Z'):
                # Convert Z to +00:00 for fromisoformat
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            elif '+' in start_time_str or start_time_str.endswith(('00', '00:00')):
                # Already has timezone
                start_time = datetime.fromisoformat(start_time_str)
            else:
                # No timezone, assume UTC
                start_time = datetime.fromisoformat(start_time_str).replace(tzinfo=timezone.utc)
            
            # Calculate duration in UTC
            now_utc = datetime.now(timezone.utc)
            duration_hours = (now_utc - start_time).total_seconds() / 3600
            
            max_hours = self.config["session"]["max_duration_hours"]
            warning_hours = self.config["session"]["warning_threshold_hours"]
            
            if duration_hours > max_hours:
                session.status = SessionStatus.EXPIRED.value
                return False, f"Session expired ({duration_hours:.1f} hours > {max_hours} hours)", session
            elif duration_hours > warning_hours:
                session.status = SessionStatus.WARNING.value
                return True, f"Session near expiry ({duration_hours:.1f} hours)", session
            else:
                session.status = SessionStatus.ACTIVE.value
                return True, f"Session active ({duration_hours:.1f} hours)", session
                
        except Exception as e:
            return False, f"Session validation error: {e}", None
    
    def end_session(self, reason: str = "normal") -> bool:
        """End current session and archive it"""
        is_valid, msg, session = self.validate_session()
        
        if not session:
            print("No active session to end")
            return False
        
        # Update session status
        session.status = SessionStatus.ENDED.value
        session.metadata = session.metadata or {}
        session.metadata["end_time"] = datetime.now(timezone.utc).isoformat()
        session.metadata["end_reason"] = reason
        
        # Archive session
        archive_dir = self.root_dir / ".governance/session/archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_file = archive_dir / f"session_{session.session_id}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2)
        
        # Remove current session
        if self.session_file.exists():
            self.session_file.unlink()
        
        print(f"Session {session.session_id} ended and archived")
        return True
    
    def get_session_info(self) -> Dict:
        """Get formatted session information"""
        is_valid, msg, session = self.validate_session()
        
        if not session:
            return {"status": "none", "message": msg}
        
        # Parse times for display
        start_time = datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        duration = now - start_time
        
        return {
            "status": session.status,
            "session_id": session.session_id,
            "architects": session.architects,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "duration": str(duration).split('.')[0],  # Remove microseconds
            "message": msg,
            "environment": session.environment
        }

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Session Management CLI")
    parser.add_argument("action", choices=["create", "validate", "end", "info"],
                       help="Action to perform")
    parser.add_argument("--architects", nargs="+", help="Architects for new session")
    parser.add_argument("--reason", default="normal", help="Reason for ending session")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    manager = SessionManager(Path(args.config) if args.config else None)
    
    if args.action == "create":
        session = manager.create_session(args.architects)
        print(f"Created session {session.session_id}")
        print(json.dumps(session.to_dict(), indent=2))
    
    elif args.action == "validate":
        is_valid, msg, session = manager.validate_session()
        print(f"Valid: {is_valid}")
        print(f"Message: {msg}")
        if session:
            print(f"Session: {session.session_id}")
    
    elif args.action == "end":
        success = manager.end_session(args.reason)
        sys.exit(0 if success else 1)
    
    elif args.action == "info":
        info = manager.get_session_info()
        print(json.dumps(info, indent=2))