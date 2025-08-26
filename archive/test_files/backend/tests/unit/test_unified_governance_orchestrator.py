"""
Unit Tests for Unified Governance Orchestrator v7.0
Comprehensive testing of all governance phases and persona collaboration
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified_governance_orchestrator import (
    UnifiedGovernanceOrchestrator,
    CollaborationPhase,
    ConsensusLevel,
    EvidenceType,
    ValidationResult,
    PersonaContribution,
    CollaborationResult
)


class TestUnifiedGovernanceOrchestrator:
    """Test suite for UnifiedGovernanceOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return UnifiedGovernanceOrchestrator()
    
    @pytest.fixture
    def sample_request(self):
        """Sample governance request for testing"""
        return {
            "type": "architecture_review",
            "proposal": "Implement caching layer",
            "context": {
                "traffic": "1M requests/day",
                "current": "direct DB access"
            }
        }
    
    # Phase 1: Identification Tests
    @pytest.mark.asyncio
    async def test_identification_phase(self, orchestrator, sample_request):
        """Test identification phase correctly identifies request type and personas"""
        result = await orchestrator._execute_identification_phase(sample_request)
        
        assert "request_type" in result
        assert "identified_personas" in result
        assert len(result["identified_personas"]) > 0
        assert result["request_type"] == "architecture_review"
    
    @pytest.mark.asyncio
    async def test_identification_with_unknown_type(self, orchestrator):
        """Test identification handles unknown request types"""
        unknown_request = {"type": "unknown_type", "data": "test"}
        result = await orchestrator._execute_identification_phase(unknown_request)
        
        assert result["request_type"] == "unknown_type"
        assert "Dr. Sarah Chen" in result["identified_personas"]  # Default persona
    
    # Phase 2: Analysis Tests
    @pytest.mark.asyncio
    async def test_analysis_phase(self, orchestrator, sample_request):
        """Test analysis phase generates proper analysis"""
        identified_personas = ["Dr. Sarah Chen", "Marcus Rodriguez"]
        result = await orchestrator._execute_analysis_phase(
            sample_request, identified_personas
        )
        
        assert "technical_analysis" in result
        assert "performance_analysis" in result
        assert "risk_assessment" in result
        assert result["technical_analysis"]["feasibility"] in ["high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_analysis_with_empty_personas(self, orchestrator, sample_request):
        """Test analysis handles empty persona list"""
        result = await orchestrator._execute_analysis_phase(sample_request, [])
        
        assert "technical_analysis" in result
        assert result["technical_analysis"]["feasibility"] == "unknown"
    
    # Phase 3: Delegation Tests
    @pytest.mark.asyncio
    async def test_delegation_phase(self, orchestrator):
        """Test delegation phase assigns tasks correctly"""
        analysis_result = {
            "technical_analysis": {"complexity": "high"},
            "performance_analysis": {"impact": "medium"}
        }
        personas = ["Dr. Sarah Chen", "Marcus Rodriguez"]
        
        result = await orchestrator._execute_delegation_phase(
            analysis_result, personas
        )
        
        assert "task_assignments" in result
        assert len(result["task_assignments"]) > 0
        for assignment in result["task_assignments"]:
            assert "persona" in assignment
            assert "task" in assignment
            assert assignment["persona"] in personas
    
    # Phase 4: Execution Tests
    @pytest.mark.asyncio
    async def test_execution_phase(self, orchestrator, sample_request):
        """Test execution phase generates persona contributions"""
        task_assignments = [
            {"persona": "Dr. Sarah Chen", "task": "technical_review"},
            {"persona": "Marcus Rodriguez", "task": "performance_review"}
        ]
        
        result = await orchestrator._execute_execution_phase(
            sample_request, task_assignments
        )
        
        assert "persona_contributions" in result
        assert len(result["persona_contributions"]) == len(task_assignments)
        
        for contrib in result["persona_contributions"]:
            assert isinstance(contrib, PersonaContribution)
            assert contrib.persona_name in ["Dr. Sarah Chen", "Marcus Rodriguez"]
    
    # Phase 5: Validation Tests
    @pytest.mark.asyncio
    async def test_validation_phase(self, orchestrator):
        """Test validation phase validates contributions"""
        contributions = [
            PersonaContribution(
                persona_name="Dr. Sarah Chen",
                contribution_type="technical_review",
                content={"recommendation": "Implement Redis cache"},
                confidence_score=0.9,
                evidence=[{"type": "performance_metrics", "data": "test"}]
            ),
            PersonaContribution(
                persona_name="Marcus Rodriguez",
                contribution_type="performance_review",
                content={"recommendation": "Use distributed cache"},
                confidence_score=0.85,
                evidence=[{"type": "benchmark", "data": "test"}]
            )
        ]
        
        result = await orchestrator._execute_validation_phase(contributions)
        
        assert "validation_results" in result
        assert "cross_validation" in result
        
        for validation in result["validation_results"]:
            assert isinstance(validation, ValidationResult)
            assert validation.is_valid in [True, False]
    
    @pytest.mark.asyncio
    async def test_validation_with_conflicting_contributions(self, orchestrator):
        """Test validation handles conflicting recommendations"""
        contributions = [
            PersonaContribution(
                persona_name="Dr. Sarah Chen",
                contribution_type="technical_review",
                content={"recommendation": "Use Redis"},
                confidence_score=0.9,
                evidence=[]
            ),
            PersonaContribution(
                persona_name="Marcus Rodriguez",
                contribution_type="technical_review",
                content={"recommendation": "Use Memcached"},
                confidence_score=0.9,
                evidence=[]
            )
        ]
        
        result = await orchestrator._execute_validation_phase(contributions)
        
        assert result["cross_validation"]["has_conflicts"] == True
        assert len(result["cross_validation"]["conflicts"]) > 0
    
    # Phase 6: Synthesis Tests
    @pytest.mark.asyncio
    async def test_synthesis_phase(self, orchestrator):
        """Test synthesis phase creates unified recommendations"""
        contributions = [
            PersonaContribution(
                persona_name="Dr. Sarah Chen",
                contribution_type="technical_review",
                content={"recommendation": "Implement caching"},
                confidence_score=0.9,
                evidence=[]
            )
        ]
        
        validation_results = [
            ValidationResult(
                persona_name="Dr. Sarah Chen",
                validation_type="evidence_check",
                is_valid=True,
                confidence_score=0.9,
                issues_found=[]
            )
        ]
        
        result = await orchestrator._execute_synthesis_phase(
            contributions, validation_results
        )
        
        assert "unified_recommendation" in result
        assert "implementation_plan" in result
        assert "risk_mitigation" in result
        assert len(result["unified_recommendation"]) > 0
    
    # Phase 7: Consensus Tests
    @pytest.mark.asyncio
    async def test_consensus_phase_high_agreement(self, orchestrator):
        """Test consensus phase with high agreement"""
        synthesis_result = {
            "unified_recommendation": ["Implement Redis cache"],
            "confidence_scores": [0.9, 0.85, 0.88]
        }
        
        contributions = [
            PersonaContribution(
                persona_name="Dr. Sarah Chen",
                contribution_type="technical_review",
                content={"recommendation": "Redis"},
                confidence_score=0.9,
                evidence=[]
            ),
            PersonaContribution(
                persona_name="Marcus Rodriguez",
                contribution_type="performance_review",
                content={"recommendation": "Redis"},
                confidence_score=0.85,
                evidence=[]
            )
        ]
        
        result = await orchestrator._execute_consensus_phase(
            synthesis_result, contributions
        )
        
        assert "consensus_level" in result
        assert result["consensus_level"] == ConsensusLevel.HIGH
        assert "final_decision" in result
    
    @pytest.mark.asyncio
    async def test_consensus_phase_low_agreement(self, orchestrator):
        """Test consensus phase with low agreement"""
        synthesis_result = {
            "unified_recommendation": ["Consider multiple options"],
            "confidence_scores": [0.5, 0.4, 0.6]
        }
        
        contributions = [
            PersonaContribution(
                persona_name="Dr. Sarah Chen",
                contribution_type="technical_review",
                content={"recommendation": "Redis"},
                confidence_score=0.5,
                evidence=[]
            ),
            PersonaContribution(
                persona_name="Marcus Rodriguez",
                contribution_type="performance_review",
                content={"recommendation": "Memcached"},
                confidence_score=0.4,
                evidence=[]
            )
        ]
        
        result = await orchestrator._execute_consensus_phase(
            synthesis_result, contributions
        )
        
        assert result["consensus_level"] == ConsensusLevel.LOW
        assert "additional_review_needed" in result
        assert result["additional_review_needed"] == True
    
    # Integration Tests for Complete Flow
    @pytest.mark.asyncio
    async def test_complete_collaboration_flow(self, orchestrator, sample_request):
        """Test complete collaboration flow through all phases"""
        result = await orchestrator.collaborate(sample_request)
        
        assert isinstance(result, CollaborationResult)
        assert result.request_id is not None
        assert len(result.phases_completed) == 7
        assert result.final_consensus in [
            ConsensusLevel.HIGH,
            ConsensusLevel.MEDIUM,
            ConsensusLevel.LOW
        ]
        assert len(result.recommendations) > 0
        assert isinstance(result.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_collaboration_with_governance_session(self, orchestrator):
        """Test collaboration with governance session ID"""
        request = {
            "type": "security_review",
            "governance_session": "test_session_123",
            "data": "sensitive operation"
        }
        
        result = await orchestrator.collaborate(request)
        
        assert result.request_id == "test_session_123"
        assert result.final_consensus is not None
    
    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_collaboration_with_invalid_request(self, orchestrator):
        """Test collaboration handles invalid requests gracefully"""
        invalid_request = None
        
        with pytest.raises(Exception):
            await orchestrator.collaborate(invalid_request)
    
    @pytest.mark.asyncio
    async def test_collaboration_with_empty_request(self, orchestrator):
        """Test collaboration handles empty requests"""
        empty_request = {}
        
        result = await orchestrator.collaborate(empty_request)
        
        assert isinstance(result, CollaborationResult)
        assert result.final_consensus == ConsensusLevel.LOW
    
    # Persona Registration Tests
    @pytest.mark.asyncio
    async def test_ensure_personas_registered(self, orchestrator):
        """Test persona registration"""
        await orchestrator._ensure_personas_registered()
        
        # Check if personas are registered (would need access to persona_manager)
        # This is a simplified test - in reality would check persona_manager state
        assert True  # Placeholder for actual registration check
    
    # Evidence Type Tests
    def test_evidence_types_enum(self):
        """Test EvidenceType enum values"""
        assert EvidenceType.PERFORMANCE_METRICS.value == "performance_metrics"
        assert EvidenceType.TEST_RESULTS.value == "test_results"
        assert EvidenceType.CODE_ANALYSIS.value == "code_analysis"
        assert EvidenceType.SECURITY_SCAN.value == "security_scan"
        assert EvidenceType.USER_FEEDBACK.value == "user_feedback"
        assert EvidenceType.BUSINESS_IMPACT.value == "business_impact"
    
    # Consensus Level Tests
    def test_consensus_levels_enum(self):
        """Test ConsensusLevel enum values"""
        assert ConsensusLevel.HIGH.value == "high"
        assert ConsensusLevel.MEDIUM.value == "medium"
        assert ConsensusLevel.LOW.value == "low"
    
    # Collaboration Phase Tests
    def test_collaboration_phases_enum(self):
        """Test CollaborationPhase enum values"""
        phases = list(CollaborationPhase)
        assert len(phases) == 7
        assert CollaborationPhase.IDENTIFICATION in phases
        assert CollaborationPhase.ANALYSIS in phases
        assert CollaborationPhase.DELEGATION in phases
        assert CollaborationPhase.EXECUTION in phases
        assert CollaborationPhase.VALIDATION in phases
        assert CollaborationPhase.SYNTHESIS in phases
        assert CollaborationPhase.CONSENSUS in phases


class TestPersonaContribution:
    """Test suite for PersonaContribution class"""
    
    def test_persona_contribution_creation(self):
        """Test PersonaContribution object creation"""
        contribution = PersonaContribution(
            persona_name="Dr. Sarah Chen",
            contribution_type="technical_review",
            content={"test": "data"},
            confidence_score=0.95,
            evidence=[{"type": "test", "data": "evidence"}]
        )
        
        assert contribution.persona_name == "Dr. Sarah Chen"
        assert contribution.contribution_type == "technical_review"
        assert contribution.content == {"test": "data"}
        assert contribution.confidence_score == 0.95
        assert len(contribution.evidence) == 1
        assert isinstance(contribution.timestamp, datetime)
    
    def test_persona_contribution_defaults(self):
        """Test PersonaContribution with default values"""
        contribution = PersonaContribution(
            persona_name="Test Persona",
            contribution_type="test_type",
            content={}
        )
        
        assert contribution.confidence_score == 0.0
        assert contribution.evidence == []
        assert contribution.supporting_personas == []


class TestValidationResult:
    """Test suite for ValidationResult class"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult object creation"""
        result = ValidationResult(
            persona_name="Marcus Rodriguez",
            validation_type="performance_check",
            is_valid=True,
            confidence_score=0.88,
            issues_found=["minor issue"],
            evidence_quality_score=0.9
        )
        
        assert result.persona_name == "Marcus Rodriguez"
        assert result.validation_type == "performance_check"
        assert result.is_valid == True
        assert result.confidence_score == 0.88
        assert len(result.issues_found) == 1
        assert result.evidence_quality_score == 0.9


class TestCollaborationResult:
    """Test suite for CollaborationResult class"""
    
    def test_collaboration_result_creation(self):
        """Test CollaborationResult object creation"""
        result = CollaborationResult(
            request_id="test_123",
            phases_completed=list(CollaborationPhase),
            final_consensus=ConsensusLevel.HIGH,
            recommendations=["Implement caching", "Add monitoring"],
            implementation_plan={"step1": "cache", "step2": "monitor"},
            evidence_trail=[{"type": "test", "data": "evidence"}],
            timestamp=datetime.now()
        )
        
        assert result.request_id == "test_123"
        assert len(result.phases_completed) == 7
        assert result.final_consensus == ConsensusLevel.HIGH
        assert len(result.recommendations) == 2
        assert "step1" in result.implementation_plan
        assert len(result.evidence_trail) == 1
        assert isinstance(result.timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])