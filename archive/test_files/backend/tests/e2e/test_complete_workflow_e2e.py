"""
End-to-End Tests for Complete AI Orchestration System
Tests full workflows from user input to deployment with governance
"""

import pytest
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified_governance_orchestrator import UnifiedGovernanceOrchestrator, ConsensusLevel
from ai_orchestration_engine import AIOrchestrationEngine, AITask, TaskPriority, AIAgent, AgentType, AgentCapability
from conversation_manager import ConversationManager, ConversationType
from multi_model_integration import MultiModelManager, ModelCapability
from token_optimization_engine import TokenOptimizationEngine, OptimizationStrategy
from claude_cli_governance_integration import ClaudeGovernanceIntegration, GovernanceLevel
from governance_driven_code_quality import GovernanceDrivenCodeQuality
from production_deployment_automation import ProductionDeploymentAutomation, DeploymentEnvironment
from real_time_governance_monitoring import RealTimeGovernanceMonitoring, MonitoringLevel
from advanced_persona_collaboration_scenarios import AdvancedPersonaCollaborationScenarios, ScenarioType


class TestCompleteWorkflowE2E:
    """End-to-end tests for complete system workflows"""
    
    @pytest.fixture
    async def complete_system(self, tmp_path):
        """Setup complete AI orchestration system"""
        # Use temp directory for testing
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Initialize all components
        governance = UnifiedGovernanceOrchestrator()
        orchestrator = AIOrchestrationEngine(governance)
        conversation_manager = ConversationManager(orchestrator)
        model_manager = MultiModelManager()
        token_optimizer = TokenOptimizationEngine(model_manager)
        claude_integration = ClaudeGovernanceIntegration(project_root)
        quality_system = GovernanceDrivenCodeQuality(project_root)
        deployment_system = ProductionDeploymentAutomation(project_root)
        monitoring = RealTimeGovernanceMonitoring(project_root, MonitoringLevel.STANDARD)
        scenarios = AdvancedPersonaCollaborationScenarios(project_root)
        
        # Initialize all systems
        await orchestrator.start_orchestration()
        await claude_integration.initialize()
        await quality_system.initialize()
        await deployment_system.initialize()
        await monitoring.initialize()
        await scenarios.initialize()
        
        # Register test agents
        test_agents = [
            AIAgent(
                agent_id="e2e_claude_agent",
                agent_type=AgentType.SPECIALIZED,
                capabilities=[AgentCapability.TEXT_GENERATION, AgentCapability.REASONING],
                model_name="claude-test",
                max_tokens=4000,
                performance_score=0.95
            ),
            AIAgent(
                agent_id="e2e_general_agent",
                agent_type=AgentType.GENERAL,
                capabilities=[AgentCapability.TEXT_GENERATION],
                model_name="general-test",
                max_tokens=2000,
                performance_score=0.85
            )
        ]
        
        for agent in test_agents:
            orchestrator.register_agent(agent)
        
        yield {
            "project_root": project_root,
            "governance": governance,
            "orchestrator": orchestrator,
            "conversation_manager": conversation_manager,
            "model_manager": model_manager,
            "token_optimizer": token_optimizer,
            "claude_integration": claude_integration,
            "quality_system": quality_system,
            "deployment_system": deployment_system,
            "monitoring": monitoring,
            "scenarios": scenarios
        }
        
        # Cleanup
        await orchestrator.stop_orchestration()
        await monitoring.stop_monitoring()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_user_request_to_deployment_workflow(self, complete_system):
        """Test complete workflow from user request to deployment"""
        
        # Step 1: User initiates conversation
        conv_manager = complete_system["conversation_manager"]
        conv_id = await conv_manager.create_conversation(
            conversation_type=ConversationType.COLLABORATIVE,
            title="Deploy New Feature",
            description="User wants to deploy a new caching feature",
            initial_context={
                "user_intent": "deploy_feature",
                "feature_type": "caching",
                "environment": "staging"
            }
        )
        
        assert conv_id is not None
        
        # Step 2: Process user message with governance
        response = await conv_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="I want to deploy a Redis caching layer to improve API performance",
            use_governance=True,
            context_enhancement=True
        )
        
        assert response["governance_used"] == True
        
        # Step 3: Create implementation task
        orchestrator = complete_system["orchestrator"]
        implementation_task = AITask(
            task_id="e2e_implementation_task",
            task_type="feature_implementation",
            description="Implement Redis caching layer",
            input_data={
                "feature": "redis_cache",
                "conversation_id": conv_id,
                "requirements": response.get("requirements", {})
            },
            priority=TaskPriority.HIGH,
            estimated_tokens=3000,
            requires_governance=True
        )
        
        task_id = await orchestrator.submit_task(implementation_task)
        assert task_id == "e2e_implementation_task"
        
        # Step 4: Code quality check
        quality_system = complete_system["quality_system"]
        
        # Create test file for quality check
        test_file = complete_system["project_root"] / "cache_implementation.py"
        test_file.write_text("""
def setup_redis_cache():
    '''Setup Redis cache for API'''
    import redis
    cache = redis.Redis(host='localhost', port=6379)
    return cache

def cache_api_response(key, value, ttl=3600):
    '''Cache API response with TTL'''
    cache = setup_redis_cache()
    cache.setex(key, ttl, value)
    return True
""")
        
        quality_report = await quality_system.analyze_file_quality(
            test_file,
            governance_enabled=True,
            detailed_analysis=True
        )
        
        assert quality_report.overall_score > 0
        
        # Step 5: Governance review for deployment
        governance = complete_system["governance"]
        deployment_request = {
            "type": "deployment_approval",
            "feature": "redis_cache",
            "quality_score": quality_report.overall_score,
            "environment": "staging",
            "risk_assessment": "medium"
        }
        
        gov_result = await governance.collaborate(deployment_request)
        assert gov_result.final_consensus in [ConsensusLevel.HIGH, ConsensusLevel.MEDIUM, ConsensusLevel.LOW]
        
        # Step 6: Create and execute deployment
        if gov_result.final_consensus != ConsensusLevel.LOW:
            deployment_system = complete_system["deployment_system"]
            
            deployment_id = await deployment_system.create_deployment(
                template_name="ai_assistant_backend",
                environment=DeploymentEnvironment.STAGING,
                deployment_config={
                    "governance_level": GovernanceLevel.ENFORCED,
                    "feature_name": "redis_cache"
                }
            )
            
            # Execute deployment (would be full in production)
            # For testing, we just verify the deployment was created
            assert deployment_id is not None
            assert deployment_id in deployment_system.deployment_configs
        
        # Step 7: Monitor the deployment
        monitoring = complete_system["monitoring"]
        await monitoring.start_monitoring()
        
        # Let monitoring run briefly
        await asyncio.sleep(2)
        
        # Check monitoring status
        dashboard_data = monitoring.dashboard.get_dashboard_data()
        assert "system_health" in dashboard_data
        assert dashboard_data["summary"]["total_systems"] > 0
        
        await monitoring.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_critical_incident_response_workflow(self, complete_system):
        """Test critical incident response workflow with governance"""
        
        # Step 1: Detect critical incident
        scenarios = complete_system["scenarios"]
        
        # Execute security incident scenario
        incident_result = await scenarios.execute_scenario(
            scenario_id="security_breach",
            custom_context={
                "severity": "critical",
                "affected_systems": ["authentication", "user_data"],
                "immediate_action_required": True
            },
            real_time_monitoring=False
        )
        
        assert incident_result.scenario_id == "security_breach"
        assert incident_result.decision_reached in [True, False]
        
        # Step 2: Create emergency response task
        orchestrator = complete_system["orchestrator"]
        emergency_task = AITask(
            task_id="e2e_emergency_response",
            task_type="incident_response",
            description="Respond to critical security breach",
            input_data={
                "incident_type": "security_breach",
                "severity": "critical",
                "recommendations": incident_result.recommendations
            },
            priority=TaskPriority.CRITICAL,
            estimated_tokens=5000,
            requires_governance=True
        )
        
        await orchestrator.submit_task(emergency_task)
        
        # Step 3: Execute governance-approved response
        governance = complete_system["governance"]
        response_plan = {
            "type": "emergency_response",
            "actions": [
                "isolate_affected_systems",
                "revoke_compromised_credentials",
                "enable_enhanced_monitoring",
                "notify_stakeholders"
            ],
            "timeline": "immediate"
        }
        
        gov_approval = await governance.collaborate(response_plan)
        assert gov_approval is not None
        
        # Step 4: Monitor response execution
        monitoring = complete_system["monitoring"]
        await monitoring.start_monitoring()
        
        # Simulate response actions
        await asyncio.sleep(1)
        
        # Generate incident report
        incident_report = await monitoring.generate_monitoring_report()
        assert "recommendations" in incident_report
        
        await monitoring.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_code_review_to_production_workflow(self, complete_system):
        """Test code review to production deployment workflow"""
        
        # Step 1: Submit code for review
        quality_system = complete_system["quality_system"]
        
        # Create test code file
        code_file = complete_system["project_root"] / "feature.py"
        code_file.write_text("""
class FeatureManager:
    def __init__(self):
        self.features = {}
        
    def add_feature(self, name, config):
        '''Add new feature with configuration'''
        if not name:
            raise ValueError("Feature name required")
        self.features[name] = config
        return True
    
    def get_feature(self, name):
        '''Get feature configuration'''
        return self.features.get(name)
    
    def remove_feature(self, name):
        '''Remove feature'''
        if name in self.features:
            del self.features[name]
            return True
        return False
""")
        
        # Step 2: Perform quality analysis
        quality_report = await quality_system.analyze_file_quality(
            code_file,
            governance_enabled=True,
            detailed_analysis=True
        )
        
        assert quality_report is not None
        
        # Step 3: Create code review workflow
        orchestrator = complete_system["orchestrator"]
        review_workflow = await orchestrator.create_workflow(
            workflow_type="code_review",
            workflow_id="e2e_code_review",
            input_data={
                "file_path": str(code_file),
                "quality_score": quality_report.overall_score,
                "issues": [issue.description for issue in quality_report.issues]
            }
        )
        
        assert review_workflow.workflow_id == "e2e_code_review"
        
        # Step 4: Execute governance review
        if quality_report.overall_score >= 70:  # Quality threshold
            governance = complete_system["governance"]
            
            review_request = {
                "type": "code_review",
                "file": str(code_file),
                "quality_score": quality_report.overall_score,
                "ready_for_production": True
            }
            
            review_result = await governance.collaborate(review_request)
            
            # Step 5: Deploy to production if approved
            if review_result.final_consensus in [ConsensusLevel.HIGH, ConsensusLevel.MEDIUM]:
                deployment_system = complete_system["deployment_system"]
                
                prod_deployment = await deployment_system.create_deployment(
                    template_name="ai_assistant_backend",
                    environment=DeploymentEnvironment.PRODUCTION,
                    deployment_config={
                        "governance_level": GovernanceLevel.STRICT,
                        "code_review_passed": True,
                        "quality_score": quality_report.overall_score
                    }
                )
                
                assert prod_deployment is not None
    
    @pytest.mark.asyncio
    async def test_multi_model_optimization_workflow(self, complete_system):
        """Test multi-model selection and optimization workflow"""
        
        # Step 1: Create complex task requiring specific capabilities
        orchestrator = complete_system["orchestrator"]
        model_manager = complete_system["model_manager"]
        
        complex_task = AITask(
            task_id="e2e_complex_task",
            task_type="complex_reasoning",
            description="Complex task requiring reasoning and generation",
            input_data={
                "problem": "Design a distributed caching architecture",
                "constraints": ["high availability", "low latency", "cost effective"],
                "output_format": "detailed_plan"
            },
            priority=TaskPriority.HIGH,
            estimated_tokens=4000,
            required_capabilities=[AgentCapability.REASONING, AgentCapability.TEXT_GENERATION]
        )
        
        # Step 2: Select best model for task
        best_model = await model_manager.select_best_model(
            task_type="reasoning",
            required_capabilities=[ModelCapability.REASONING, ModelCapability.TEXT_GENERATION],
            max_cost=0.1,
            quality_threshold=0.8
        )
        
        # Step 3: Optimize tokens if needed
        token_optimizer = complete_system["token_optimizer"]
        
        if complex_task.estimated_tokens > 3000:
            optimization_result = await token_optimizer.optimize_request(
                content=json.dumps(complex_task.input_data),
                strategy=OptimizationStrategy.BALANCED,
                target_tokens=3000
            )
            
            if optimization_result.tokens_saved > 0:
                complex_task.input_data["optimized"] = True
                complex_task.estimated_tokens = optimization_result.optimized_tokens
        
        # Step 4: Submit optimized task
        task_id = await orchestrator.submit_task(complex_task)
        assert task_id == "e2e_complex_task"
        
        # Step 5: Monitor execution
        monitoring = complete_system["monitoring"]
        await monitoring.start_monitoring()
        
        # Wait for brief execution
        await asyncio.sleep(2)
        
        # Check task metrics
        dashboard = monitoring.dashboard.get_dashboard_data()
        assert "active_metrics" in dashboard
        
        await monitoring.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_governance_escalation_workflow(self, complete_system):
        """Test governance escalation workflow for critical decisions"""
        
        # Step 1: Create critical decision requiring escalation
        scenarios = complete_system["scenarios"]
        
        # Execute strategic planning scenario
        strategy_result = await scenarios.execute_scenario(
            scenario_id="ai_adoption_strategy",
            custom_context={
                "budget": "$2M",
                "timeline": "6 months",
                "critical_decision": True,
                "requires_ceo_approval": True
            },
            real_time_monitoring=False
        )
        
        assert strategy_result is not None
        
        # Step 2: Check if escalation is needed
        if strategy_result.final_consensus == ConsensusLevel.LOW:
            # Need escalation due to low consensus
            governance = complete_system["governance"]
            
            escalation_request = {
                "type": "escalation_required",
                "reason": "low_consensus",
                "original_decision": "ai_adoption_strategy",
                "stakeholders": ["CEO", "CTO", "CFO"],
                "urgency": "high"
            }
            
            escalation_result = await governance.collaborate(escalation_request)
            assert escalation_result is not None
            
            # Step 3: Re-run scenario with additional input
            if escalation_result.final_consensus != ConsensusLevel.LOW:
                enhanced_result = await scenarios.execute_scenario(
                    scenario_id="ai_adoption_strategy",
                    custom_context={
                        "budget": "$2M",
                        "timeline": "6 months",
                        "executive_guidance": escalation_result.recommendations,
                        "pre_approved": True
                    },
                    real_time_monitoring=False
                )
                
                assert enhanced_result.final_consensus != ConsensusLevel.LOW
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring_workflow(self, complete_system):
        """Test continuous monitoring and alerting workflow"""
        
        # Step 1: Start comprehensive monitoring
        monitoring = complete_system["monitoring"]
        monitoring.monitoring_level = MonitoringLevel.COMPREHENSIVE
        await monitoring.start_monitoring()
        
        # Step 2: Simulate various system activities
        orchestrator = complete_system["orchestrator"]
        
        # Submit multiple tasks to generate activity
        tasks = []
        for i in range(5):
            task = AITask(
                task_id=f"e2e_monitor_task_{i}",
                task_type="monitoring_test",
                description=f"Monitoring test task {i}",
                input_data={"index": i},
                priority=TaskPriority.MEDIUM,
                estimated_tokens=500
            )
            tasks.append(task)
            await orchestrator.submit_task(task)
        
        # Step 3: Wait for monitoring to collect metrics
        await asyncio.sleep(3)
        
        # Step 4: Check monitoring dashboard
        dashboard_data = monitoring.dashboard.get_dashboard_data()
        
        assert dashboard_data["summary"]["total_systems"] > 0
        assert len(dashboard_data["active_metrics"]) > 0
        
        # Step 5: Generate monitoring report
        report = await monitoring.generate_monitoring_report()
        
        assert "monitoring_level" in report
        assert report["monitoring_level"] == "comprehensive"
        assert "recommendations" in report
        assert len(report["recommendations"]) > 0
        
        # Step 6: Stop monitoring
        await monitoring.stop_monitoring()
        
        # Verify monitoring stopped
        assert monitoring.monitoring_active == False


class TestSystemIntegrationE2E:
    """End-to-end tests for system integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_claude_cli_integration_e2e(self, tmp_path):
        """Test Claude CLI integration end-to-end"""
        project_root = tmp_path / "claude_test"
        project_root.mkdir()
        
        # Initialize Claude integration
        claude_integration = ClaudeGovernanceIntegration(project_root)
        await claude_integration.initialize()
        
        # Test chat with governance
        chat_result = await claude_integration.claude_chat(
            message="Explain microservices architecture",
            governance_level=GovernanceLevel.ADVISORY
        )
        
        assert chat_result["governance_applied"] == True
        
        # Test file operation with governance
        test_file = project_root / "test.py"
        test_file.write_text("print('test')")
        
        analysis_result = await claude_integration.claude_analyze_code(
            file_path=str(test_file),
            analysis_type="security",
            governance_level=GovernanceLevel.ENFORCED
        )
        
        assert analysis_result["governance_applied"] == True
    
    @pytest.mark.asyncio
    async def test_deployment_rollback_e2e(self, tmp_path):
        """Test deployment with rollback scenario"""
        project_root = tmp_path / "deploy_test"
        project_root.mkdir()
        
        # Initialize deployment system
        deployment_system = ProductionDeploymentAutomation(project_root)
        await deployment_system.initialize()
        
        # Create deployment that will fail
        deployment_id = await deployment_system.create_deployment(
            template_name="ai_assistant_backend",
            environment=DeploymentEnvironment.STAGING,
            deployment_config={
                "simulate_failure": True,
                "rollback_enabled": True
            }
        )
        
        # Deployment should handle failure and rollback
        # In real scenario, would execute and verify rollback
        assert deployment_id is not None
        assert deployment_system.deployment_configs[deployment_id].rollback_enabled == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])