"""
@fileoverview Unit tests for database models
@author Maya Patel v1.0 - QA & Testing Lead
@architecture Testing - Unit tests
@business_logic Validate model behavior and relationships
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database.models import (
    Base, Rule, Practice, Template, Session as DBSession,
    AIDecision, AuditLog, PracticeApplication, TemplateUsage,
    RuleSeverity, RuleStatus, TemplateType, SessionStatus
)

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

class TestRuleModel:
    """Test Rule model"""
    
    def test_create_rule(self, db_session):
        """Test creating a rule"""
        rule = Rule(
            name="test_rule",
            description="Test rule description",
            category="testing",
            severity=RuleSeverity.WARNING,
            status=RuleStatus.ACTIVE,
            condition="test_condition",
            action="test_action",
            author="Test Author"
        )
        
        db_session.add(rule)
        db_session.commit()
        
        assert rule.id is not None
        assert rule.name == "test_rule"
        assert rule.severity == RuleSeverity.WARNING
        assert rule.status == RuleStatus.ACTIVE
        assert rule.version == 1
        assert rule.enforcement_count == 0
        assert rule.violation_count == 0
    
    def test_rule_unique_name(self, db_session):
        """Test that rule names must be unique"""
        rule1 = Rule(
            name="unique_rule",
            condition="condition1",
            action="action1"
        )
        rule2 = Rule(
            name="unique_rule",  # Same name
            condition="condition2",
            action="action2"
        )
        
        db_session.add(rule1)
        db_session.commit()
        
        db_session.add(rule2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_rule_severity_validation(self, db_session):
        """Test rule severity validation"""
        rule = Rule(
            name="severity_test",
            condition="test",
            action="test"
        )
        
        # Valid severities
        for severity in [RuleSeverity.INFO, RuleSeverity.WARNING, 
                        RuleSeverity.ERROR, RuleSeverity.CRITICAL]:
            rule.severity = severity
            assert rule.severity == severity
        
        # Invalid severity
        with pytest.raises(ValueError):
            rule.severity = "invalid_severity"
    
    def test_rule_to_dict(self, db_session):
        """Test rule serialization"""
        rule = Rule(
            name="dict_test",
            description="Test serialization",
            category="test",
            severity=RuleSeverity.INFO,
            status=RuleStatus.ACTIVE,
            condition="test",
            action="test",
            parameters={"key": "value"}
        )
        
        db_session.add(rule)
        db_session.commit()
        
        rule_dict = rule.to_dict()
        assert rule_dict['name'] == "dict_test"
        assert rule_dict['severity'] == RuleSeverity.INFO
        assert rule_dict['parameters'] == {"key": "value"}
        assert 'id' in rule_dict
        assert 'created_at' in rule_dict
    
    def test_rule_hierarchy(self, db_session):
        """Test parent-child rule relationships"""
        parent_rule = Rule(
            name="parent_rule",
            condition="parent",
            action="parent"
        )
        
        child_rule = Rule(
            name="child_rule",
            condition="child",
            action="child",
            parent=parent_rule
        )
        
        db_session.add(parent_rule)
        db_session.add(child_rule)
        db_session.commit()
        
        assert child_rule.parent_id == parent_rule.id
        assert child_rule in parent_rule.children
        assert child_rule.parent == parent_rule

class TestPracticeModel:
    """Test Practice model"""
    
    def test_create_practice(self, db_session):
        """Test creating a practice"""
        practice = Practice(
            name="Test Practice",
            category="testing",
            description="Test practice description",
            rationale="Why this is important",
            examples=["Example 1", "Example 2"],
            anti_patterns=["Don't do this"],
            author="Test Author"
        )
        
        db_session.add(practice)
        db_session.commit()
        
        assert practice.id is not None
        assert practice.name == "Test Practice"
        assert practice.score_weight == 1.0
        assert practice.votes_up == 0
        assert practice.votes_down == 0
        assert len(practice.examples) == 2
    
    def test_practice_effectiveness_calculation(self, db_session):
        """Test effectiveness score calculation"""
        practice = Practice(
            name="Effectiveness Test",
            category="test",
            description="Test"
        )
        
        # No votes
        assert practice.calculate_effectiveness() == 0.5
        
        # All positive votes
        practice.votes_up = 10
        practice.votes_down = 0
        assert practice.calculate_effectiveness() == 1.0
        
        # Mixed votes
        practice.votes_up = 7
        practice.votes_down = 3
        assert practice.calculate_effectiveness() == 0.7
        
        # All negative votes
        practice.votes_up = 0
        practice.votes_down = 5
        assert practice.calculate_effectiveness() == 0.0
    
    def test_practice_to_dict(self, db_session):
        """Test practice serialization"""
        practice = Practice(
            name="Serialization Test",
            category="test",
            description="Test",
            examples=["Ex1", "Ex2"],
            effectiveness_score=0.85,
            adoption_rate=0.75
        )
        
        db_session.add(practice)
        db_session.commit()
        
        practice_dict = practice.to_dict()
        assert practice_dict['name'] == "Serialization Test"
        assert practice_dict['effectiveness_score'] == 0.85
        assert practice_dict['adoption_rate'] == 0.75
        assert practice_dict['examples'] == ["Ex1", "Ex2"]

class TestTemplateModel:
    """Test Template model"""
    
    def test_create_template(self, db_session):
        """Test creating a template"""
        template = Template(
            name="Test Template",
            type=TemplateType.CODE,
            category="testing",
            template_content="{{variable}} template",
            variables={"variable": {"type": "string", "required": True}},
            author="Test Author"
        )
        
        db_session.add(template)
        db_session.commit()
        
        assert template.id is not None
        assert template.name == "Test Template"
        assert template.type == TemplateType.CODE
        assert template.version == 1
        assert template.usage_count == 0
        assert "variable" in template.variables
    
    def test_template_type_validation(self, db_session):
        """Test template type validation"""
        template = Template(
            name="Type Test",
            type=TemplateType.DOCUMENTATION,
            template_content="test"
        )
        
        # Valid types
        for template_type in [TemplateType.DOCUMENTATION, TemplateType.CODE,
                             TemplateType.PROMPT, TemplateType.PERSONA,
                             TemplateType.WORKFLOW]:
            template.type = template_type
            assert template.type == template_type
        
        # Invalid type
        with pytest.raises(ValueError):
            template.type = "invalid_type"
    
    def test_template_versioning(self, db_session):
        """Test template versioning"""
        template_v1 = Template(
            name="Versioned Template",
            type=TemplateType.CODE,
            template_content="Version 1",
            version=1
        )
        
        db_session.add(template_v1)
        db_session.commit()
        
        template_v2 = Template(
            name="Versioned Template",
            type=TemplateType.CODE,
            template_content="Version 2",
            version=2,
            parent=template_v1
        )
        
        db_session.add(template_v2)
        db_session.commit()
        
        assert template_v2.parent_id == template_v1.id
        assert template_v2 in template_v1.children
        assert template_v2.version == 2

class TestSessionModel:
    """Test Session model"""
    
    def test_create_session(self, db_session):
        """Test creating a session"""
        session = DBSession(
            session_id="test_session_123",
            architects=["Alex Novak", "Dr. Sarah Chen"],
            status=SessionStatus.ACTIVE,
            start_time=datetime.utcnow(),
            environment={"platform": "test", "version": "1.0"}
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.session_id == "test_session_123"
        assert len(session.architects) == 2
        assert session.status == SessionStatus.ACTIVE
        assert session.environment["platform"] == "test"
    
    def test_session_duration_calculation(self, db_session):
        """Test session duration calculation"""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=2, minutes=30)
        
        session = DBSession(
            session_id="duration_test",
            architects=["Test"],
            start_time=start_time,
            end_time=end_time
        )
        
        session.calculate_duration()
        assert session.duration_minutes == 150  # 2.5 hours = 150 minutes
    
    def test_session_unique_id(self, db_session):
        """Test that session IDs must be unique"""
        session1 = DBSession(
            session_id="unique_session",
            architects=["Test"],
            start_time=datetime.utcnow()
        )
        
        session2 = DBSession(
            session_id="unique_session",  # Same ID
            architects=["Test"],
            start_time=datetime.utcnow()
        )
        
        db_session.add(session1)
        db_session.commit()
        
        db_session.add(session2)
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestAIDecisionModel:
    """Test AIDecision model"""
    
    def test_create_ai_decision(self, db_session):
        """Test creating an AI decision"""
        decision = AIDecision(
            decision_type="code_generation",
            persona="Senior Developer",
            task="Generate unit test",
            input_context={"code": "def test(): pass"},
            decision_chain=[
                {"step": 1, "action": "analyze"},
                {"step": 2, "action": "generate"}
            ],
            output={"test": "def test_test(): assert True"},
            confidence=0.95,
            execution_time_ms=1500,
            tokens_used=250,
            cost=0.05
        )
        
        db_session.add(decision)
        db_session.commit()
        
        assert decision.id is not None
        assert decision.decision_type == "code_generation"
        assert decision.confidence == 0.95
        assert decision.tokens_used == 250
        assert len(decision.decision_chain) == 2
    
    def test_ai_decision_approval(self, db_session):
        """Test AI decision approval workflow"""
        decision = AIDecision(
            decision_type="test",
            task="test task"
        )
        
        # Initially not approved
        assert decision.approved is None
        
        # Approve the decision
        decision.approved = True
        decision.approval_by = "Maya Patel"
        decision.approval_notes = "Looks good"
        
        db_session.add(decision)
        db_session.commit()
        
        assert decision.approved is True
        assert decision.approval_by == "Maya Patel"

class TestAuditLogModel:
    """Test AuditLog model"""
    
    def test_create_audit_log(self, db_session):
        """Test creating an audit log entry"""
        audit = AuditLog(
            event_type="rule_created",
            entity_type="rule",
            entity_id="rule_123",
            action="create",
            actor="Test User",
            ip_address="127.0.0.1",
            before_state=None,
            after_state={"name": "new_rule", "status": "active"},
            metadata={"source": "api"}
        )
        
        db_session.add(audit)
        db_session.commit()
        
        assert audit.id is not None
        assert audit.event_type == "rule_created"
        assert audit.actor == "Test User"
        assert audit.after_state["name"] == "new_rule"
        assert audit.metadata["source"] == "api"
    
    def test_audit_log_relationships(self, db_session):
        """Test audit log relationships"""
        # Create a session
        session = DBSession(
            session_id="audit_test",
            architects=["Test"],
            start_time=datetime.utcnow()
        )
        
        # Create a rule
        rule = Rule(
            name="audit_rule",
            condition="test",
            action="test"
        )
        
        db_session.add(session)
        db_session.add(rule)
        db_session.commit()
        
        # Create audit log linked to both
        audit = AuditLog(
            event_type="test",
            entity_type="test",
            entity_id="test",
            action="test",
            actor="Test",
            session=session,
            rule=rule
        )
        
        db_session.add(audit)
        db_session.commit()
        
        assert audit.session_id == session.id
        assert audit.rule_id == rule.id
        assert audit in session.audit_logs
        assert audit in rule.audit_logs

class TestRelationships:
    """Test model relationships"""
    
    def test_practice_applications(self, db_session):
        """Test practice application tracking"""
        practice = Practice(
            name="Applied Practice",
            category="test",
            description="Test"
        )
        
        db_session.add(practice)
        db_session.commit()
        
        application = PracticeApplication(
            practice=practice,
            project_id="project_123",
            context={"environment": "production"},
            effectiveness_rating=4,
            notes="Worked well"
        )
        
        db_session.add(application)
        db_session.commit()
        
        assert application.practice_id == practice.id
        assert application in practice.applications
        assert application.effectiveness_rating == 4
    
    def test_template_usage(self, db_session):
        """Test template usage tracking"""
        template = Template(
            name="Used Template",
            type=TemplateType.CODE,
            template_content="test"
        )
        
        db_session.add(template)
        db_session.commit()
        
        usage = TemplateUsage(
            template=template,
            used_by="Test User",
            variable_values={"var": "value"},
            output_generated="Generated output",
            success=True,
            feedback="Great template!"
        )
        
        db_session.add(usage)
        db_session.commit()
        
        assert usage.template_id == template.id
        assert usage in template.usage_logs
        assert usage.success is True

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])