"""
@fileoverview Shared enums used across backend services
@author Dr. Sarah Chen & Alex Novak - Enterprise Architects
@architecture Shared Types Library
@description Central enum definitions for type safety across Python services
"""

from enum import Enum, auto
from typing import List


# ============== GOVERNANCE ENUMS ==============

class RuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    MEDIUM = "medium"
    ERROR = "error"
    CRITICAL = "critical"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class RuleStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== TEMPLATE ENUMS ==============

class TemplateType(str, Enum):
    CODE = "code"
    CONFIG = "config"
    DOCUMENT = "document"
    DOCUMENTATION = "documentation"
    WORKFLOW = "workflow"
    ANALYSIS = "analysis"
    PROMPT = "prompt"
    PERSONA = "persona"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== SESSION ENUMS ==============

class SessionStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    EXPIRED = "expired"
    ENDED = "ended"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== DECISION ENUMS ==============

class DecisionType(str, Enum):
    CODE_GENERATION = "CODE_GENERATION"
    ARCHITECTURE = "ARCHITECTURE"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    DOCUMENTATION = "DOCUMENTATION"
    TESTING = "TESTING"
    DEPLOYMENT = "DEPLOYMENT"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== CACHE ENUMS ==============

class CacheLevel(str, Enum):
    L1_MEMORY = "L1_MEMORY"
    L2_REDIS = "L2_REDIS"
    L3_DATABASE = "L3_DATABASE"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== CONNECTION ENUMS ==============

class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class WebSocketState(int, Enum):
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3
    
    @classmethod
    def values(cls) -> List[int]:
        return [e.value for e in cls]


# ============== AUDIT ENUMS ==============

class AuditEventType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACCESS = "ACCESS"
    VALIDATE = "VALIDATE"
    ENFORCE = "ENFORCE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


class EntityType(str, Enum):
    RULE = "RULE"
    PRACTICE = "PRACTICE"
    TEMPLATE = "TEMPLATE"
    SESSION = "SESSION"
    DECISION = "DECISION"
    USER = "USER"
    SYSTEM = "SYSTEM"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== GOVERNANCE LEVELS ==============

class GovernanceLevel(str, Enum):
    NONE = "none"
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"
    EXTREME = "extreme"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]


# ============== HOOK TYPES ==============

class HookType(str, Enum):
    PRE_COMMIT = "pre_commit"
    POST_COMMIT = "post_commit"
    PRE_PUSH = "pre_push"
    POST_PUSH = "post_push"
    PRE_MERGE = "pre_merge"
    POST_MERGE = "post_merge"
    
    @classmethod
    def values(cls) -> List[str]:
        return [e.value for e in cls]