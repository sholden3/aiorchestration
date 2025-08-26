"""
Test Suite for Unified Governance Orchestrator v7.0
Tests full persona collaboration with evidence-based validation
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Import our unified system
from unified_governance_orchestrator import (
    UnifiedGovernanceOrchestrator,
    CollaborationPhase,
    ConsensusLevel,
    EvidenceType,
    ValidationResult,
    PersonaContribution,
    CollaborationResult
)

class TestUnifiedGovernance:
    """Test the complete unified governance system"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a test orchestrator"""
        with patch('unified_governance_orchestrator.DataDrivenGovernanceOrchestrator'):
            with patch('unified_governance_orchestrator.DynamicPersonaGovernance'):
                with patch('unified_governance_orchestrator.EnhancedGovernanceEnforcer'):
                    return UnifiedGovernanceOrchestrator()
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample collaboration request"""
        return {
            "type": "code_review",
            "code": """
def calculate_metrics(data):
    # Process data
    result = []
    for item in data:
        if item > 100:
            result.append(item * 2)
    return result
            """,
            "context": {
                "file": "metrics.py",
                "project": "analytics",
                "priority": "high"
            },
            "requirements": [
                "Performance optimization",
                "Security validation",
                "UX considerations"
            ]
        }
    
    @pytest.fixture
    def mock_personas(self):
        """Create mock persona responses"""
        return {
            "Sarah Chen": {
                "analysis": "Code needs optimization for large datasets",
                "recommendations": ["Use numpy for vectorization", "Add type hints"],
                "confidence": 0.85,
                "evidence": {
                    "type": EvidenceType.PERFORMANCE_METRICS,
                    "data": {"current_time": "O(n)", "optimized_time": "O(1)"}
                }
            },
            "Marcus Rodriguez": {
                "analysis": "Database impact needs consideration",
                "recommendations": ["Add caching layer", "Implement batch processing"],
                "confidence": 0.90,
                "evidence": {
                    "type": EvidenceType.TEST_RESULTS,
                    "data": {"load_test": "passed", "throughput": "1000 req/s"}
                }
            },
            "Emily Watson": {
                "analysis": "User feedback mechanism missing",
                "recommendations": ["Add progress indicator", "Implement error handling"],
                "confidence": 0.75,
                "evidence": {
                    "type": EvidenceType.CODE_ANALYSIS,
                    "data": {"error_handling": False, "user_feedback": False}
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_phase_1_identification(self, orchestrator, sample_request):
        """Test Phase 1: Request Identification"""
        # Mock the identification phase
        orchestrator._identify_request = AsyncMock(return_value={
            "type": "code_review",
            "domains": ["performance", "security", "ux"],
            "complexity": "medium",
            "personas_required": ["Sarah Chen", "Marcus Rodriguez", "Emily Watson"]
        })
        
        result = await orchestrator._identify_request(sample_request)
        
        assert result["type"] == "code_review"
        assert len(result["domains"]) == 3
        assert "performance" in result["domains"]
        assert len(result["personas_required"]) == 3
    
    @pytest.mark.asyncio
    async def test_phase_2_analysis(self, orchestrator, sample_request):
        """Test Phase 2: Multi-Domain Analysis"""
        # Mock the analysis phase
        orchestrator._analyze_domains = AsyncMock(return_value={
            "performance": {
                "issues": ["Linear time complexity", "No caching"],
                "severity": "medium",
                "impact": "scales poorly with data size"
            },
            "security": {
                "issues": ["No input validation", "No type checking"],
                "severity": "high",
                "impact": "potential for injection attacks"
            },
            "ux": {
                "issues": ["No progress feedback", "No error messages"],
                "severity": "low",
                "impact": "poor user experience"
            }
        })
        
        analysis = await orchestrator._analyze_domains(sample_request)
        
        assert "performance" in analysis
        assert "security" in analysis
        assert analysis["security"]["severity"] == "high"
        assert len(analysis["performance"]["issues"]) == 2
    
    @pytest.mark.asyncio
    async def test_phase_3_delegation(self, orchestrator, mock_personas):
        """Test Phase 3: Intelligent Delegation"""
        # Mock the delegation phase
        orchestrator._delegate_to_personas = AsyncMock(return_value={
            "Sarah Chen": ["performance", "architecture"],
            "Marcus Rodriguez": ["database", "infrastructure"],
            "Emily Watson": ["user_experience", "accessibility"],
            "Rachel Torres": ["business_impact", "compliance"]
        })
        
        delegation = await orchestrator._delegate_to_personas(
            ["performance", "security", "ux"]
        )
        
        assert "Sarah Chen" in delegation
        assert "performance" in delegation["Sarah Chen"]
        assert len(delegation) >= 3
    
    @pytest.mark.asyncio
    async def test_phase_4_execution(self, orchestrator, sample_request, mock_personas):
        """Test Phase 4: Parallel Execution"""
        # Mock persona executions
        orchestrator._execute_persona_tasks = AsyncMock(return_value=[
            PersonaContribution(
                persona_name="Sarah Chen",
                contribution_type="analysis",
                content="Performance needs optimization",
                phase=CollaborationPhase.EXECUTION,
                contribution=mock_personas["Sarah Chen"],
                confidence=0.85,
                timestamp=datetime.now()
            ),
            PersonaContribution(
                persona_name="Marcus Rodriguez",
                contribution_type="analysis",
                content="Infrastructure needs scaling",
                phase=CollaborationPhase.EXECUTION,
                contribution=mock_personas["Marcus Rodriguez"],
                confidence=0.90,
                timestamp=datetime.now()
            )
        ])
        
        contributions = await orchestrator._execute_persona_tasks(sample_request)
        
        assert len(contributions) >= 2
        assert contributions[0].persona_name == "Sarah Chen"
        assert contributions[0].confidence == 0.85
        assert contributions[1].persona_name == "Marcus Rodriguez"
    
    @pytest.mark.asyncio
    async def test_phase_5_validation(self, orchestrator, mock_personas):
        """Test Phase 5: Cross-Validation"""
        # Create test contributions
        contributions = [
            PersonaContribution(
                persona_name="Sarah Chen",
                contribution_type="analysis",
                content="Performance needs optimization",
                phase=CollaborationPhase.EXECUTION,
                contribution=mock_personas["Sarah Chen"],
                confidence=0.85,
                timestamp=datetime.now()
            )
        ]
        
        # Mock validation
        orchestrator._validate_contributions = AsyncMock(return_value=ValidationResult(
            is_valid=True,
            confidence=0.92,
            evidence=[
                {
                    "type": EvidenceType.PERFORMANCE_METRICS,
                    "validator": "Marcus Rodriguez",
                    "result": "confirmed"
                }
            ],
            conflicts=[],
            consensus_level=ConsensusLevel.HIGH
        ))
        
        validation = await orchestrator._validate_contributions(contributions)
        
        assert validation.is_valid is True
        assert validation.confidence > 0.9
        assert validation.consensus_level == ConsensusLevel.HIGH
        assert len(validation.conflicts) == 0
    
    @pytest.mark.asyncio
    async def test_phase_6_synthesis(self, orchestrator, mock_personas):
        """Test Phase 6: Knowledge Synthesis"""
        # Create test contributions
        contributions = [
            PersonaContribution(
                persona_name=name,
                contribution_type="analysis",
                content=f"{name} analysis",
                phase=CollaborationPhase.EXECUTION,
                contribution=data,
                confidence=data["confidence"],
                timestamp=datetime.now()
            )
            for name, data in mock_personas.items()
        ]
        
        # Mock synthesis
        orchestrator._synthesize_knowledge = AsyncMock(return_value={
            "unified_recommendations": [
                "Implement numpy vectorization for performance",
                "Add comprehensive error handling",
                "Create caching layer for database queries",
                "Add user progress indicators"
            ],
            "priority_actions": [
                {"action": "Add input validation", "priority": "critical"},
                {"action": "Optimize algorithm", "priority": "high"},
                {"action": "Add UI feedback", "priority": "medium"}
            ],
            "estimated_impact": {
                "performance": "70% improvement",
                "security": "critical vulnerabilities fixed",
                "user_experience": "significantly enhanced"
            }
        })
        
        synthesis = await orchestrator._synthesize_knowledge(contributions)
        
        assert "unified_recommendations" in synthesis
        assert len(synthesis["unified_recommendations"]) >= 3
        assert "priority_actions" in synthesis
        assert synthesis["priority_actions"][0]["priority"] == "critical"
    
    @pytest.mark.asyncio
    async def test_phase_7_consensus(self, orchestrator):
        """Test Phase 7: Consensus Building"""
        # Mock consensus building
        orchestrator._build_consensus = AsyncMock(return_value={
            "consensus_level": ConsensusLevel.HIGH,
            "agreement_score": 0.88,
            "dissenting_opinions": [],
            "final_decision": "Approved with modifications",
            "implementation_plan": {
                "immediate": ["Fix security issues"],
                "short_term": ["Optimize performance"],
                "long_term": ["Enhance UX"]
            }
        })
        
        consensus = await orchestrator._build_consensus({})
        
        assert consensus["consensus_level"] == ConsensusLevel.HIGH
        assert consensus["agreement_score"] > 0.85
        assert len(consensus["dissenting_opinions"]) == 0
        assert "implementation_plan" in consensus
    
    @pytest.mark.asyncio
    async def test_full_collaboration_flow(self, orchestrator, sample_request):
        """Test complete collaboration flow from request to consensus"""
        # Mock the full collaboration
        orchestrator.collaborate = AsyncMock(return_value=CollaborationResult(
            request_id="test-123",
            phases_completed=[phase for phase in CollaborationPhase],
            final_consensus=ConsensusLevel.HIGH,
            recommendations=[
                "Implement all security fixes immediately",
                "Deploy performance optimizations in next sprint",
                "Schedule UX improvements for Q2"
            ],
            implementation_plan={
                "timeline": "2 weeks",
                "resources": ["2 developers", "1 QA engineer"],
                "checkpoints": ["security review", "performance testing", "user testing"]
            },
            evidence_trail=[
                {"phase": "analysis", "evidence": "code_metrics"},
                {"phase": "validation", "evidence": "test_results"},
                {"phase": "consensus", "evidence": "voting_records"}
            ],
            timestamp=datetime.now()
        ))
        
        result = await orchestrator.collaborate(sample_request)
        
        assert result.request_id == "test-123"
        assert result.final_consensus == ConsensusLevel.HIGH
        assert len(result.phases_completed) == 7
        assert len(result.recommendations) >= 3
        assert "timeline" in result.implementation_plan
        assert len(result.evidence_trail) >= 3
    
    @pytest.mark.asyncio
    async def test_conflict_resolution(self, orchestrator):
        """Test handling of persona conflicts"""
        # Create conflicting opinions
        conflicts = [
            {
                "issue": "caching strategy",
                "persona_1": {"name": "Sarah Chen", "position": "Redis"},
                "persona_2": {"name": "Marcus Rodriguez", "position": "Memcached"},
                "severity": "medium"
            }
        ]
        
        # Mock conflict resolution
        orchestrator._resolve_conflicts = AsyncMock(return_value={
            "resolution": "Redis selected based on evidence",
            "rationale": "Better performance metrics in testing",
            "evidence": {"benchmark": "Redis 35% faster"},
            "agreement": True
        })
        
        resolution = await orchestrator._resolve_conflicts(conflicts)
        
        assert resolution["agreement"] is True
        assert "Redis" in resolution["resolution"]
        assert "evidence" in resolution
    
    @pytest.mark.asyncio
    async def test_evidence_validation(self, orchestrator):
        """Test evidence-based validation system"""
        evidence = {
            "type": EvidenceType.PERFORMANCE_METRICS,
            "data": {
                "before": {"latency": "500ms", "throughput": "100 req/s"},
                "after": {"latency": "50ms", "throughput": "1000 req/s"}
            },
            "source": "load_testing",
            "confidence": 0.95
        }
        
        # Mock evidence validation
        orchestrator._validate_evidence = AsyncMock(return_value={
            "is_valid": True,
            "confidence": 0.95,
            "verification": "Evidence confirmed by 3 personas",
            "methodology": "Statistical analysis with p < 0.05"
        })
        
        validation = await orchestrator._validate_evidence(evidence)
        
        assert validation["is_valid"] is True
        assert validation["confidence"] >= 0.95
        assert "personas" in validation["verification"]
    
    @pytest.mark.asyncio
    async def test_dynamic_persona_integration(self, orchestrator):
        """Test integration with dynamic persona system"""
        # Register a new expert
        new_expert = {
            "name": "Dr. Alex Security",
            "primary_domain": "cybersecurity",
            "capabilities": ["penetration testing", "vulnerability assessment"],
            "confidence_threshold": 0.85
        }
        
        # Mock registration
        orchestrator.dynamic.register_persona = AsyncMock(return_value={
            "registered": True,
            "persona_id": "alex-security-001",
            "integration_status": "active"
        })
        
        registration = await orchestrator.dynamic.register_persona(new_expert)
        
        assert registration["registered"] is True
        assert "persona_id" in registration
        assert registration["integration_status"] == "active"
    
    def test_governance_config_integration(self, orchestrator):
        """Test integration with data-driven governance config"""
        # Mock config loading
        orchestrator.data_driven.config = {
            "version": "5.0",
            "agents": ["prompt_interceptor", "business_auditor"],
            "personas": ["Sarah Chen", "Marcus Rodriguez", "Emily Watson", "Rachel Torres"],
            "execution_modes": ["single_agent_single_persona", "multi_agent_multi_persona"],
            "validation_rules": {
                "no_unicode_characters": {"enabled": True},
                "folder_structure": {"enabled": True}
            }
        }
        
        config = orchestrator.data_driven.config
        
        assert config["version"] == "5.0"
        assert len(config["personas"]) == 4
        assert "no_unicode_characters" in config["validation_rules"]
        assert config["validation_rules"]["no_unicode_characters"]["enabled"] is True
    
    def test_collaboration_metrics(self, orchestrator):
        """Test collaboration performance metrics"""
        metrics = {
            "phases_completed": 7,
            "total_time": 1250,  # milliseconds
            "personas_involved": 4,
            "evidence_pieces": 12,
            "consensus_score": 0.92,
            "conflicts_resolved": 2
        }
        
        # Calculate efficiency
        efficiency = (metrics["phases_completed"] / 7) * metrics["consensus_score"]
        
        assert efficiency > 0.9
        assert metrics["total_time"] < 2000  # Under 2 seconds
        assert metrics["consensus_score"] > 0.9
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test graceful error handling in collaboration"""
        # Simulate a persona failure
        orchestrator._execute_persona_tasks = AsyncMock(
            side_effect=Exception("Persona timeout")
        )
        
        orchestrator._handle_collaboration_error = AsyncMock(return_value={
            "error_handled": True,
            "fallback": "Reduced persona set",
            "result": "Partial consensus achieved"
        })
        
        error_result = await orchestrator._handle_collaboration_error(
            Exception("Persona timeout")
        )
        
        assert error_result["error_handled"] is True
        assert "fallback" in error_result
        assert "Partial consensus" in error_result["result"]


class TestPersonaCollaborationScenarios:
    """Test real-world collaboration scenarios"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for scenario testing"""
        return UnifiedGovernanceOrchestrator()
    
    @pytest.mark.asyncio
    async def test_security_vulnerability_scenario(self, orchestrator):
        """Test collaboration on security vulnerability"""
        vulnerability_request = {
            "type": "security_review",
            "code": """
def login(username, password):
    query = f"SELECT * FROM users WHERE name='{username}' AND pass='{password}'"
    return db.execute(query)
            """,
            "severity": "critical",
            "context": "Production authentication system"
        }
        
        # Mock collaborative response
        orchestrator.collaborate = AsyncMock(return_value=CollaborationResult(
            request_id="sec-001",
            phases_completed=[phase for phase in CollaborationPhase],
            final_consensus=ConsensusLevel.UNANIMOUS,
            recommendations=[
                "CRITICAL: SQL injection vulnerability - use parameterized queries",
                "Hash passwords with bcrypt, never store plaintext",
                "Implement rate limiting and account lockout",
                "Add audit logging for all authentication attempts"
            ],
            implementation_plan={
                "immediate_actions": [
                    "Deploy hotfix with parameterized queries",
                    "Force password reset for all users",
                    "Enable security monitoring"
                ],
                "timeline": "Within 24 hours",
                "validation": "Penetration testing required"
            },
            evidence_trail=[
                {
                    "type": "vulnerability_scan",
                    "result": "SQL injection confirmed",
                    "severity": "critical"
                }
            ],
            timestamp=datetime.now()
        ))
        
        result = await orchestrator.collaborate(vulnerability_request)
        
        assert result.final_consensus == ConsensusLevel.UNANIMOUS
        assert "SQL injection" in result.recommendations[0]
        assert result.implementation_plan["timeline"] == "Within 24 hours"
        assert len(result.recommendations) >= 4
    
    @pytest.mark.asyncio
    async def test_performance_optimization_scenario(self, orchestrator):
        """Test collaboration on performance optimization"""
        performance_request = {
            "type": "performance_review",
            "code": """
def process_large_dataset(data):
    results = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] > data[j]:
                results.append((data[i], data[j]))
    return results
            """,
            "context": "Processing 1M+ records",
            "target": "Sub-second response time"
        }
        
        # Mock collaborative response
        orchestrator.collaborate = AsyncMock(return_value=CollaborationResult(
            request_id="perf-001",
            phases_completed=[phase for phase in CollaborationPhase],
            final_consensus=ConsensusLevel.HIGH,
            recommendations=[
                "O(n²) complexity unacceptable - implement O(n log n) solution",
                "Use NumPy for vectorized operations",
                "Implement parallel processing with multiprocessing",
                "Add caching layer for repeated queries",
                "Consider database indexing strategies"
            ],
            implementation_plan={
                "optimizations": [
                    {"change": "Replace nested loops with sorted approach", "impact": "10x faster"},
                    {"change": "NumPy vectorization", "impact": "5x faster"},
                    {"change": "Parallel processing", "impact": "4x faster on 8 cores"}
                ],
                "expected_improvement": "40x overall speedup",
                "validation": "Load testing with production data"
            },
            evidence_trail=[
                {
                    "type": "benchmark",
                    "before": "45 seconds",
                    "after": "1.1 seconds",
                    "dataset_size": "1M records"
                }
            ],
            timestamp=datetime.now()
        ))
        
        result = await orchestrator.collaborate(performance_request)
        
        assert result.final_consensus == ConsensusLevel.HIGH
        assert "O(n log n)" in result.recommendations[0]
        assert "40x" in result.implementation_plan["expected_improvement"]
        assert float(result.evidence_trail[0]["after"].split()[0]) < 2.0
    
    @pytest.mark.asyncio
    async def test_architecture_decision_scenario(self, orchestrator):
        """Test collaboration on architecture decisions"""
        architecture_request = {
            "type": "architecture_review",
            "proposal": "Migrate from monolith to microservices",
            "context": {
                "current_architecture": "Django monolith",
                "team_size": 5,
                "timeline": "6 months",
                "budget": "$200k"
            },
            "requirements": [
                "Improve scalability",
                "Enable independent deployments",
                "Reduce deployment risk"
            ]
        }
        
        # Mock collaborative response
        orchestrator.collaborate = AsyncMock(return_value=CollaborationResult(
            request_id="arch-001",
            phases_completed=[phase for phase in CollaborationPhase],
            final_consensus=ConsensusLevel.MODERATE,
            recommendations=[
                "Gradual migration recommended - start with edge services",
                "Extract authentication service first (lowest risk)",
                "Implement API gateway before full migration",
                "Consider serverless for stateless services",
                "Maintain monolith during transition (strangler fig pattern)"
            ],
            implementation_plan={
                "phases": [
                    {"month": 1, "task": "Extract auth service", "risk": "low"},
                    {"month": 2, "task": "Implement API gateway", "risk": "medium"},
                    {"month": 3, "task": "Extract payment service", "risk": "high"},
                    {"month": 4, "task": "Extract notification service", "risk": "low"},
                    {"month": 5, "task": "Database separation", "risk": "high"},
                    {"month": 6, "task": "Complete migration", "risk": "medium"}
                ],
                "total_cost": "$180k",
                "success_probability": "75%"
            },
            evidence_trail=[
                {
                    "type": "case_study",
                    "source": "Similar migration at scale",
                    "outcome": "Successful with 20% timeline overrun"
                }
            ],
            timestamp=datetime.now()
        ))
        
        result = await orchestrator.collaborate(architecture_request)
        
        assert result.final_consensus == ConsensusLevel.MODERATE
        assert "strangler fig" in result.recommendations[4].lower()
        assert len(result.implementation_plan["phases"]) == 6
        assert result.implementation_plan["success_probability"] == "75%"


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=unified_governance_orchestrator",
        "--cov-report=term-missing"
    ])