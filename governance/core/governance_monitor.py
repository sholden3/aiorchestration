"""
@fileoverview Real-time governance activity monitoring and visibility system
@author Dr. Sarah Chen v1.0 & Priya Sharma v1.0 - 2025-08-29
@architecture Backend - Governance monitoring and observability
@responsibility Monitor governance operations, track decisions, provide visibility
@dependencies asyncio, datetime, typing, enum, json, dataclasses
@integration_points Governance engine, validators, personas, hooks
@testing_strategy Unit tests for event tracking, integration tests for monitoring flow
@governance Provides audit trail and real-time visibility into governance operations

Business Logic Summary:
- Track all governance events in real-time
- Monitor validation decisions and interventions
- Provide colored terminal output for visibility
- Track metrics and performance data
- Generate audit trails for compliance

Architecture Integration:
- Observes all governance operations
- Integrates with engine and validators
- Provides real-time feedback
- Supports async event handling
- Enables debugging and troubleshooting

Sarah's Framework Check:
- What breaks first: Event queue overflow under high load
- How we know: Queue size monitoring and alerts
- Plan B: Event sampling and aggregation
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from dataclasses import dataclass, field
import sys

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class GovernanceEventType(Enum):
    """Types of governance events for monitoring"""
    SYSTEM_START = "system_start"
    AGENT_SPAWN_REQUEST = "agent_spawn_request"
    AGENT_SPAWN_VALIDATED = "agent_spawn_validated"
    AGENT_SPAWN_REJECTED = "agent_spawn_rejected"
    COMMAND_VALIDATED = "command_validated"
    COMMAND_REJECTED = "command_rejected"
    DECISION_INTERCEPTED = "decision_intercepted"
    DECISION_MODIFIED = "decision_modified"
    PERSONA_CONSULTED = "persona_consulted"
    RISK_ASSESSED = "risk_assessed"
    RESOURCE_CHECK = "resource_check"
    VIOLATION_DETECTED = "violation_detected"
    HALLUCINATION_DETECTED = "hallucination_detected"
    HOOK_TRIGGERED = "hook_triggered"
    AUDIT_LOGGED = "audit_logged"


@dataclass
class GovernanceEvent:
    """Represents a governance event"""
    event_type: GovernanceEventType
    timestamp: datetime
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL
    actor: Optional[str] = None  # Who/what triggered this


class GovernanceMonitor:
    """
    Real-time governance activity monitor
    Provides visible proof of governance operations
    """
    
    def __init__(self, verbose: bool = True, log_to_file: bool = True):
        self.verbose = verbose
        self.log_to_file = log_to_file
        self.events: List[GovernanceEvent] = []
        self.event_count = 0
        self.start_time = datetime.now()
        
        # Statistics
        self.stats = {
            "total_validations": 0,
            "approvals": 0,
            "rejections": 0,
            "modifications": 0,
            "violations": 0,
            "personas_consulted": 0,
            "hooks_triggered": 0
        }
        
        # Output file
        if self.log_to_file:
            self.log_file = f"governance_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        self._print_header()
    
    def _print_header(self):
        """Print governance monitor header"""
        if self.verbose:
            print(f"\n{Colors.BOLD}{Colors.HEADER}" + "=" * 80 + Colors.END)
            print(f"{Colors.BOLD}{Colors.CYAN}[GOVERNANCE MONITOR ACTIVE]{Colors.END}")
            print(f"{Colors.BOLD}{Colors.HEADER}" + "=" * 80 + Colors.END)
            print(f"{Colors.GREEN}Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
            print(f"{Colors.YELLOW}Monitoring Level: FULL VISIBILITY{Colors.END}")
            print(f"{Colors.HEADER}" + "-" * 80 + Colors.END + "\n")
    
    def log_event(self, event: GovernanceEvent):
        """Log a governance event with visibility"""
        self.events.append(event)
        self.event_count += 1
        
        # Update statistics
        self._update_stats(event)
        
        # Format the output
        output = self._format_event(event)
        
        # Print to console if verbose
        if self.verbose:
            print(output)
        
        # Log to file
        if self.log_to_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{output}\n")
    
    def _format_event(self, event: GovernanceEvent) -> str:
        """Format event for display"""
        # Choose color based on severity
        color = Colors.GREEN
        icon = "[OK]"
        
        if event.severity == "WARNING":
            color = Colors.YELLOW
            icon = "[!]"
        elif event.severity == "ERROR":
            color = Colors.RED
            icon = "[X]"
        elif event.severity == "CRITICAL":
            color = Colors.RED + Colors.BOLD
            icon = "[ALERT]"
        
        # Build output
        timestamp = event.timestamp.strftime('%H:%M:%S.%f')[:-3]
        
        output = f"{color}[{timestamp}] {icon} {event.event_type.value.upper()}{Colors.END}\n"
        output += f"  {Colors.BOLD}Description:{Colors.END} {event.description}\n"
        
        if event.actor:
            output += f"  {Colors.BOLD}Actor:{Colors.END} {event.actor}\n"
        
        if event.details:
            output += f"  {Colors.BOLD}Details:{Colors.END}\n"
            for key, value in event.details.items():
                output += f"    • {key}: {value}\n"
        
        return output
    
    def _update_stats(self, event: GovernanceEvent):
        """Update statistics based on event"""
        if "VALIDATED" in event.event_type.value:
            self.stats["total_validations"] += 1
            if "REJECTED" not in event.event_type.value:
                self.stats["approvals"] += 1
        
        if "REJECTED" in event.event_type.value:
            self.stats["rejections"] += 1
        
        if event.event_type == GovernanceEventType.DECISION_MODIFIED:
            self.stats["modifications"] += 1
        
        if event.event_type == GovernanceEventType.VIOLATION_DETECTED:
            self.stats["violations"] += 1
        
        if event.event_type == GovernanceEventType.PERSONA_CONSULTED:
            self.stats["personas_consulted"] += 1
        
        if event.event_type == GovernanceEventType.HOOK_TRIGGERED:
            self.stats["hooks_triggered"] += 1
    
    def show_statistics(self):
        """Display current statistics"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}" + "=" * 60 + Colors.END)
        print(f"{Colors.BOLD}GOVERNANCE STATISTICS{Colors.END}")
        print(f"{Colors.CYAN}" + "-" * 60 + Colors.END)
        print(f"Runtime: {runtime:.1f} seconds")
        print(f"Total Events: {self.event_count}")
        print(f"\nValidations:")
        print(f"  • Total: {self.stats['total_validations']}")
        print(f"  • Approved: {Colors.GREEN}{self.stats['approvals']}{Colors.END}")
        print(f"  • Rejected: {Colors.RED}{self.stats['rejections']}{Colors.END}")
        print(f"  • Modified: {Colors.YELLOW}{self.stats['modifications']}{Colors.END}")
        print(f"\nActivity:")
        print(f"  • Violations Detected: {self.stats['violations']}")
        print(f"  • Personas Consulted: {self.stats['personas_consulted']}")
        print(f"  • Hooks Triggered: {self.stats['hooks_triggered']}")
        print(f"{Colors.CYAN}" + "=" * 60 + Colors.END + "\n")
    
    def log_agent_spawn_request(self, agent_type: str, agent_name: str, metadata: Dict[str, Any]):
        """Log agent spawn request"""
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.AGENT_SPAWN_REQUEST,
            timestamp=datetime.now(),
            description=f"Request to spawn {agent_type} agent: {agent_name}",
            details={
                "agent_type": agent_type,
                "agent_name": agent_name,
                "metadata": metadata
            },
            severity="INFO",
            actor="User"
        ))
    
    def log_validation_result(self, operation: str, approved: bool, reason: str, risk_level: str = "LOW"):
        """Log validation result"""
        event_type = GovernanceEventType.AGENT_SPAWN_VALIDATED if approved else GovernanceEventType.AGENT_SPAWN_REJECTED
        severity = "INFO" if approved else "WARNING"
        
        self.log_event(GovernanceEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            description=f"{operation} {'APPROVED' if approved else 'REJECTED'}: {reason}",
            details={
                "approved": approved,
                "reason": reason,
                "risk_level": risk_level
            },
            severity=severity,
            actor="Governance System"
        ))
    
    def log_persona_consultation(self, persona: str, decision: str, confidence: float, concerns: List[str]):
        """Log persona consultation"""
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.PERSONA_CONSULTED,
            timestamp=datetime.now(),
            description=f"Consulted {persona} for validation",
            details={
                "persona": persona,
                "decision": decision,
                "confidence": f"{confidence:.2%}",
                "concerns": concerns if concerns else "None"
            },
            severity="INFO",
            actor=persona
        ))
    
    def log_decision_modification(self, original: str, modified: str, reason: str):
        """Log decision modification"""
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.DECISION_MODIFIED,
            timestamp=datetime.now(),
            description=f"AI output modified for compliance: {reason}",
            details={
                "original_snippet": original[:100] + "..." if len(original) > 100 else original,
                "modified_snippet": modified[:100] + "..." if len(modified) > 100 else modified,
                "modification_reason": reason
            },
            severity="WARNING",
            actor="Decision Injector"
        ))
    
    def log_violation(self, violation_type: str, details: str, severity: str = "WARNING"):
        """Log violation detection"""
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.VIOLATION_DETECTED,
            timestamp=datetime.now(),
            description=f"Violation detected: {violation_type}",
            details={
                "type": violation_type,
                "details": details
            },
            severity=severity,
            actor="Smart Rules"
        ))
    
    def log_hook_trigger(self, hook_type: str, context: Dict[str, Any]):
        """Log hook trigger"""
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.HOOK_TRIGGERED,
            timestamp=datetime.now(),
            description=f"Hook triggered: {hook_type}",
            details={
                "hook_type": hook_type,
                "context_keys": list(context.keys()) if context else []
            },
            severity="INFO",
            actor="Hook System"
        ))
    
    def log_resource_check(self, resource: str, current: Any, limit: Any, available: Any):
        """Log resource check"""
        severity = "WARNING" if current > limit * 0.8 else "INFO"
        
        self.log_event(GovernanceEvent(
            event_type=GovernanceEventType.RESOURCE_CHECK,
            timestamp=datetime.now(),
            description=f"Resource check: {resource}",
            details={
                "resource": resource,
                "current": current,
                "limit": limit,
                "available": available
            },
            severity=severity,
            actor="Resource Manager"
        ))


# Singleton instance
_monitor_instance: Optional[GovernanceMonitor] = None


def get_monitor() -> GovernanceMonitor:
    """Get or create the singleton monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = GovernanceMonitor()
    return _monitor_instance


def show_governance_banner():
    """Show that governance is active"""
    print(f"""
{Colors.BOLD}{Colors.CYAN}
+==============================================================+
|                                                              |
|    GOVERNANCE SYSTEM ACTIVE AND MONITORING ALL OPERATIONS   |
|                                                              |
|  Every AI decision passes through:                          |
|  * Pre-validation hooks                                     |
|  * Smart rule checking                                      |
|  * Multi-persona consultation                               |
|  * Risk assessment                                          |
|  * Hallucination detection                                  |
|  * Post-validation audit                                    |
|                                                              |
|  Status: ENFORCING | Level: STRICT | Monitoring: ENABLED    |
+==============================================================+
{Colors.END}
""")