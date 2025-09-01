"""
Database package initialization
"""

from .database import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    init_db,
    drop_db,
    DatabaseManager
)

from .models import (
    Base,
    Rule,
    Practice,
    Template,
    Session,
    AIDecision,
    AuditLog,
    PracticeApplication,
    TemplateUsage,
    Tag,
    TemplateVariable,
    RuleSeverity,
    RuleStatus,
    TemplateType,
    SessionStatus
)

from .seeds import seed_all

__all__ = [
    # Database
    'engine',
    'SessionLocal',
    'get_db',
    'get_db_session',
    'init_db',
    'drop_db',
    'DatabaseManager',
    
    # Models
    'Base',
    'Rule',
    'Practice',
    'Template',
    'Session',
    'AIDecision',
    'AuditLog',
    'PracticeApplication',
    'TemplateUsage',
    'Tag',
    'TemplateVariable',
    
    # Enums
    'RuleSeverity',
    'RuleStatus',
    'TemplateType',
    'SessionStatus',
    
    # Seeds
    'seed_all'
]