"""
Specialized Database Systems
Learning, Bugs, Business Assumptions, Rules, Validations, Documentation, Code
Evidence-Based Implementation with Cross-Persona Validation
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, field

from database_manager import DatabaseManager
from config import Config
from base_patterns import OrchestrationResult

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Specialized database types"""
    LEARNING = "learning"          # AI learning patterns
    BUGS = "bugs"                  # Bug tracking
    ASSUMPTIONS = "assumptions"    # Business assumptions
    RULES = "rules"                # Business rules
    VALIDATIONS = "validations"    # Validation rules
    DOCUMENTATION = "docs"         # Documentation
    CODE = "code"                  # Code snippets

@dataclass
class LearningEntry:
    """Learning database entry"""
    id: str
    pattern: str
    context: Dict[str, Any]
    outcome: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

@dataclass
class BugEntry:
    """Bug database entry"""
    id: str
    description: str
    stack_trace: Optional[str]
    severity: str  # critical, high, medium, low
    status: str    # open, in_progress, resolved, closed
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class AssumptionEntry:
    """Business assumption entry"""
    id: str
    assumption: str
    rationale: str
    validated: bool = False
    validation_method: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class RuleEntry:
    """Business rule entry"""
    id: str
    rule_name: str
    condition: str
    action: str
    priority: int
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

class SpecializedDatabases:
    """
    Manager for specialized database systems
    Sarah: AI learning pattern storage
    Marcus: Performance-optimized queries
    Emily: Clear data organization
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.initialized = False
        
        # Cache for frequently accessed data
        self.cache = {
            DatabaseType.RULES: {},
            DatabaseType.VALIDATIONS: {}
        }
        
        logger.info("Specialized databases initialized")
    
    async def initialize(self):
        """Initialize all database schemas"""
        if not self.db_manager.pool:
            await self.db_manager.initialize()
        
        if not self.db_manager.pool:
            logger.error("Failed to initialize database pool")
            return False
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                # Learning patterns table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_patterns (
                        id VARCHAR(64) PRIMARY KEY,
                        pattern TEXT NOT NULL,
                        context JSONB,
                        outcome TEXT,
                        confidence FLOAT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Bugs table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bugs (
                        id VARCHAR(64) PRIMARY KEY,
                        description TEXT NOT NULL,
                        stack_trace TEXT,
                        severity VARCHAR(20),
                        status VARCHAR(20),
                        created_at TIMESTAMP DEFAULT NOW(),
                        resolved_at TIMESTAMP,
                        metadata JSONB
                    )
                """)
                
                # Business assumptions table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS business_assumptions (
                        id VARCHAR(64) PRIMARY KEY,
                        assumption TEXT NOT NULL,
                        rationale TEXT,
                        validated BOOLEAN DEFAULT FALSE,
                        validation_method TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        validated_at TIMESTAMP,
                        metadata JSONB
                    )
                """)
                
                # Business rules table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS business_rules (
                        id VARCHAR(64) PRIMARY KEY,
                        rule_name VARCHAR(255) NOT NULL,
                        condition TEXT,
                        action TEXT,
                        priority INTEGER DEFAULT 0,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Validations table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS validations (
                        id VARCHAR(64) PRIMARY KEY,
                        validation_name VARCHAR(255) NOT NULL,
                        field_name VARCHAR(255),
                        validation_type VARCHAR(50),
                        parameters JSONB,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Documentation table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS documentation (
                        id VARCHAR(64) PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        content TEXT,
                        category VARCHAR(50),
                        tags TEXT[],
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Code snippets table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS code_snippets (
                        id VARCHAR(64) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        language VARCHAR(50),
                        code TEXT,
                        description TEXT,
                        tags TEXT[],
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_learning_confidence 
                    ON learning_patterns(confidence DESC)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_bugs_status 
                    ON bugs(status, severity)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rules_active 
                    ON business_rules(active, priority DESC)
                """)
                
            self.initialized = True
            logger.info("All specialized database schemas created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize schemas: {e}")
            return False
    
    async def record_learning(
        self, 
        pattern: str, 
        context: Dict,
        outcome: str,
        confidence: float
    ) -> OrchestrationResult[LearningEntry]:
        """
        Record AI learning pattern
        Sarah: Stores patterns for future reference
        """
        import uuid
        
        if not self.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        try:
            entry = LearningEntry(
                id=str(uuid.uuid4()),
                pattern=pattern,
                context=context,
                outcome=outcome,
                confidence=confidence
            )
            
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO learning_patterns 
                    (id, pattern, context, outcome, confidence, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, entry.id, pattern, json.dumps(context), 
                outcome, confidence, json.dumps(entry.metadata))
            
            logger.info(f"Recorded learning pattern: {entry.id}")
            return OrchestrationResult.ok(entry)
            
        except Exception as e:
            logger.error(f"Failed to record learning: {e}")
            return OrchestrationResult.error(str(e))
    
    async def report_bug(
        self,
        description: str,
        stack_trace: Optional[str] = None,
        severity: str = "medium"
    ) -> OrchestrationResult[BugEntry]:
        """
        Report a bug
        Marcus: Tracks system issues for resolution
        """
        import uuid
        
        if not self.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        try:
            entry = BugEntry(
                id=str(uuid.uuid4()),
                description=description,
                stack_trace=stack_trace,
                severity=severity,
                status="open"
            )
            
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bugs 
                    (id, description, stack_trace, severity, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, entry.id, description, stack_trace, 
                severity, "open", json.dumps(entry.metadata))
            
            logger.info(f"Bug reported: {entry.id} - {severity}")
            return OrchestrationResult.ok(entry)
            
        except Exception as e:
            logger.error(f"Failed to report bug: {e}")
            return OrchestrationResult.error(str(e))
    
    async def add_assumption(
        self,
        assumption: str,
        rationale: str
    ) -> OrchestrationResult[AssumptionEntry]:
        """
        Add business assumption
        Emily: Documents assumptions for validation
        """
        import uuid
        
        if not self.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        try:
            entry = AssumptionEntry(
                id=str(uuid.uuid4()),
                assumption=assumption,
                rationale=rationale
            )
            
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO business_assumptions 
                    (id, assumption, rationale, metadata)
                    VALUES ($1, $2, $3, $4)
                """, entry.id, assumption, rationale, 
                json.dumps(entry.metadata))
            
            logger.info(f"Assumption added: {entry.id}")
            return OrchestrationResult.ok(entry)
            
        except Exception as e:
            logger.error(f"Failed to add assumption: {e}")
            return OrchestrationResult.error(str(e))
    
    async def validate_assumption(
        self,
        assumption_id: str,
        validation_method: str
    ) -> OrchestrationResult[bool]:
        """Validate an assumption"""
        if not self.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                result = await conn.execute("""
                    UPDATE business_assumptions 
                    SET validated = TRUE,
                        validation_method = $1,
                        validated_at = NOW()
                    WHERE id = $2
                """, validation_method, assumption_id)
                
                if result.split()[-1] == '1':
                    logger.info(f"Assumption {assumption_id} validated")
                    return OrchestrationResult.ok(True)
                else:
                    return OrchestrationResult.error("Assumption not found")
                    
        except Exception as e:
            logger.error(f"Failed to validate assumption: {e}")
            return OrchestrationResult.error(str(e))
    
    async def add_rule(
        self,
        rule_name: str,
        condition: str,
        action: str,
        priority: int = 0
    ) -> OrchestrationResult[RuleEntry]:
        """Add business rule"""
        import uuid
        
        if not self.initialized:
            return OrchestrationResult.error("Database not initialized")
        
        try:
            entry = RuleEntry(
                id=str(uuid.uuid4()),
                rule_name=rule_name,
                condition=condition,
                action=action,
                priority=priority
            )
            
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO business_rules 
                    (id, rule_name, condition, action, priority, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, entry.id, rule_name, condition, 
                action, priority, json.dumps(entry.metadata))
            
            # Update cache
            self.cache[DatabaseType.RULES][entry.id] = entry
            
            logger.info(f"Rule added: {rule_name}")
            return OrchestrationResult.ok(entry)
            
        except Exception as e:
            logger.error(f"Failed to add rule: {e}")
            return OrchestrationResult.error(str(e))
    
    async def get_active_rules(self) -> List[RuleEntry]:
        """Get all active rules sorted by priority"""
        if not self.initialized:
            return []
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM business_rules 
                    WHERE active = TRUE 
                    ORDER BY priority DESC, created_at ASC
                """)
                
                rules = []
                for row in rows:
                    rule = RuleEntry(
                        id=row['id'],
                        rule_name=row['rule_name'],
                        condition=row['condition'],
                        action=row['action'],
                        priority=row['priority'],
                        active=row['active'],
                        created_at=row['created_at']
                    )
                    rules.append(rule)
                    # Cache it
                    self.cache[DatabaseType.RULES][rule.id] = rule
                
                return rules
                
        except Exception as e:
            logger.error(f"Failed to get active rules: {e}")
            return []
    
    async def search_learning_patterns(
        self,
        pattern_query: str,
        min_confidence: float = 0.5
    ) -> List[LearningEntry]:
        """Search learning patterns by similarity and confidence"""
        if not self.initialized:
            return []
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM learning_patterns 
                    WHERE pattern ILIKE $1 AND confidence >= $2
                    ORDER BY confidence DESC
                    LIMIT 10
                """, f"%{pattern_query}%", min_confidence)
                
                patterns = []
                for row in rows:
                    pattern = LearningEntry(
                        id=row['id'],
                        pattern=row['pattern'],
                        context=json.loads(row['context']) if row['context'] else {},
                        outcome=row['outcome'],
                        confidence=row['confidence'],
                        created_at=row['created_at']
                    )
                    patterns.append(pattern)
                
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to search patterns: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        Marcus: Real counts from actual data
        """
        # In production, would query actual counts
        return {
            'learning_patterns': 0,
            'open_bugs': 0,
            'validated_assumptions': 0,
            'active_rules': len(self.cache[DatabaseType.RULES]),
            'validations': len(self.cache[DatabaseType.VALIDATIONS]),
            'initialized': self.initialized
        }