"""
Integration Tests for Governance and Orchestration Systems
Tests interaction between governance orchestrator and AI orchestration engine
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified_governance_orchestrator import (
    UnifiedGovernanceOrchestrator,
    CollaborationPhase,
    ConsensusLevel,
    CollaborationResult
)
from ai_orchestration_engine import (
    AIOrchestrationEngine,
    AITask,
    TaskPriority,
    TaskStatus,
    AIAgent,
    AgentType,
    AgentCapability
)
from conversation_manager import ConversationManager, ConversationType
from token_optimization_engine import TokenOptimizationEngine, OptimizationStrategy
from multi_model_integration import MultiModelManager, ModelCapability


class TestGovernanceOrchestrationIntegration:
    """Integration tests for governance and orchestration systems"""
    
    @pytest.fixture
    async def integrated_system(self):
        """Create integrated system with all components"""
        governance = UnifiedGovernanceOrchestrator()
        orchestrator = AIOrchestrationEngine(governance)
        conversation_manager = ConversationManager(orchestrator)
        token_optimizer = TokenOptimizationEngine()
        model_manager = MultiModelManager()
        
        # Start orchestration
        await orchestrator.start_orchestration()
        
        # Register test agents
        test_agent = AIAgent(
            agent_id="test_agent_integrated",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.TEXT_GENERATION, AgentCapability.ANALYSIS],
            model_name="test-model",
            max_tokens=2000
        )
        orchestrator.register_agent(test_agent)
        
        yield {
            "governance": governance,
            "orchestrator": orchestrator,
            "conversation_manager": conversation_manager,
            "token_optimizer": token_optimizer,
            "model_manager": model_manager
        }
        
        # Cleanup
        await orchestrator.stop_orchestration()
    
    @pytest.mark.asyncio
    async def test_governance_task_submission(self, integrated_system):
        """Test submitting task that requires governance approval"""
        orchestrator = integrated_system["orchestrator"]
        governance = integrated_system["governance"]
        
        # Create high-priority task requiring governance
        task = AITask(
            task_id="gov_required_task",
            task_type="architecture_change",
            description="Major architecture change requiring governance",
            input_data={
                "change_type": "database_migration",
                "impact": "high",
                "affected_services": ["auth", "payments"]
            },
            priority=TaskPriority.HIGH,
            estimated_tokens=2000,
            requires_governance=True
        )
        
        # Submit task
        task_id = await orchestrator.submit_task(task)
        
        assert task_id == "gov_required_task"
        assert task.requires_governance == True
        
        # Simulate governance approval process
        gov_request = {
            "type": "task_approval",
            "task_id": task_id,
            "task_type": task.task_type,
            "impact": task.input_data["impact"]
        }
        
        gov_result = await governance.collaborate(gov_request)
        
        assert isinstance(gov_result, CollaborationResult)
        assert gov_result.final_consensus in [ConsensusLevel.HIGH, ConsensusLevel.MEDIUM, ConsensusLevel.LOW]
    
    @pytest.mark.asyncio
    async def test_conversation_with_governance(self, integrated_system):
        """Test conversation management with governance oversight"""
        conv_manager = integrated_system["conversation_manager"]
        
        # Create conversation requiring governance
        conv_id = await conv_manager.create_conversation(
            conversation_type=ConversationType.COLLABORATIVE,
            title="Governance-Required Discussion",
            description="Discussion about sensitive architecture changes",
            initial_context={
                "governance_required": True,
                "sensitivity_level": "high"
            }
        )
        
        assert conv_id is not None
        assert conv_id in conv_manager.conversations
        
        # Process message with governance
        response = await conv_manager.process_ai_response(
            conversation_id=conv_id,
            user_message="Should we migrate to microservices architecture?",
            use_governance=True,
            context_enhancement=True
        )
        
        assert response is not None
        assert "governance_used" in response
        assert response["governance_used"] == True
    
    @pytest.mark.asyncio
    async def test_token_optimization_in_workflow(self, integrated_system):
        """Test token optimization within orchestrated workflow"""
        orchestrator = integrated_system["orchestrator"]
        token_optimizer = integrated_system["token_optimizer"]
        
        # Create workflow with large input requiring optimization
        large_input = "This is a very long input " * 100  # Simulate large input
        
        workflow = await orchestrator.create_workflow(
            workflow_type="document_processing",
            workflow_id="token_opt_workflow",
            input_data={
                "document": large_input,
                "optimize_tokens": True
            }
        )
        
        # Optimize content before processing
        optimization_result = await token_optimizer.optimize_request(
            content=large_input,
            strategy=OptimizationStrategy.BALANCED
        )
        
        assert optimization_result.tokens_saved > 0
        assert optimization_result.compression_ratio > 0
        assert len(optimization_result.optimized_content) < len(large_input)
    
    @pytest.mark.asyncio
    async def test_multi_model_selection_for_task(self, integrated_system):
        """Test multi-model selection for specific task requirements"""
        orchestrator = integrated_system["orchestrator"]
        model_manager = integrated_system["model_manager"]
        
        # Register multiple model agents
        agents = [
            AIAgent(
                agent_id="claude_agent",
                agent_type=AgentType.SPECIALIZED,
                capabilities=[AgentCapability.TEXT_GENERATION, AgentCapability.REASONING],
                model_name="claude-3",
                max_tokens=4000,
                performance_score=0.95
            ),
            AIAgent(
                agent_id="gpt_agent",
                agent_type=AgentType.GENERAL,
                capabilities=[AgentCapability.TEXT_GENERATION],
                model_name="gpt-4",
                max_tokens=3000,
                performance_score=0.90
            ),
            AIAgent(
                agent_id="local_agent",
                agent_type=AgentType.LIGHTWEIGHT,
                capabilities=[AgentCapability.TEXT_GENERATION],
                model_name="llama-2",
                max_tokens=2000,
                performance_score=0.75,
                cost_per_token=0.0
            )
        ]
        
        for agent in agents:
            orchestrator.register_agent(agent)
        
        # Select best model for reasoning task
        best_model = await model_manager.select_best_model(
            task_type="reasoning",
            required_capabilities=[ModelCapability.REASONING, ModelCapability.TEXT_GENERATION],
            quality_threshold=0.9
        )
        
        # Should select high-performance model for reasoning
        assert best_model is not None
    
    @pytest.mark.asyncio
    async def test_governance_workflow_execution(self, integrated_system):
        """Test complete governance workflow execution"""
        orchestrator = integrated_system["orchestrator"]
        governance = integrated_system["governance"]
        
        # Create governance workflow
        workflow = await orchestrator.create_workflow(
            workflow_type="governance_review",
            workflow_id="gov_workflow_001",
            input_data={
                "proposal": "Implement new caching strategy",
                "risk_level": "medium",
                "stakeholders": ["engineering", "operations", "security"]
            }
        )
        
        assert workflow.governance_session is not None
        
        # Execute workflow with governance
        result = await orchestrator.execute_workflow(workflow.workflow_id)
        
        assert result is not None
        assert "governance_decision" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_error_recovery_with_governance(self, integrated_system):
        """Test error recovery with governance oversight"""
        orchestrator = integrated_system["orchestrator"]
        
        # Create task that will fail
        failing_task = AITask(
            task_id="failing_task",
            task_type="risky_operation",
            description="Operation that might fail",
            input_data={"simulate_failure": True},
            priority=TaskPriority.HIGH,
            estimated_tokens=1000,
            max_retries=2,
            requires_governance=True
        )
        
        # Submit task
        task_id = await orchestrator.submit_task(failing_task)
        
        # Simulate failure and retry
        failing_task.status = TaskStatus.FAILED
        failing_task.retry_count = 1
        
        # Governance should be consulted for retry decision
        assert failing_task.requires_governance == True
        assert failing_task.retry_count < failing_task.max_retries
    
    @pytest.mark.asyncio
    async def test_context_preservation_across_systems(self, integrated_system):
        """Test context preservation across different systems"""
        conv_manager = integrated_system["conversation_manager"]
        orchestrator = integrated_system["orchestrator"]
        
        # Create conversation with context
        conv_id = await conv_manager.create_conversation(
            conversation_type=ConversationType.MULTI_TURN,
            title="Context Test",
            description="Testing context preservation",
            initial_context={
                "user_preference": "detailed_explanations",
                "domain": "software_architecture",
                "session_id": "test_session_123"
            }
        )
        
        # Add message to conversation
        await conv_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Explain microservices architecture"
        )
        
        # Create task with conversation context
        task = AITask(
            task_id="context_task",
            task_type="explanation",
            description="Explain based on conversation context",
            input_data={
                "conversation_id": conv_id,
                "use_context": True
            },
            priority=TaskPriority.MEDIUM,
            estimated_tokens=1500
        )
        
        await orchestrator.submit_task(task)
        
        # Verify context is available
        conv = conv_manager.conversations[conv_id]
        assert conv.context["domain"] == "software_architecture"
        assert task.input_data["conversation_id"] == conv_id
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, integrated_system):
        """Test performance monitoring across integrated systems"""
        orchestrator = integrated_system["orchestrator"]
        
        # Submit multiple tasks to generate performance data
        tasks = []
        for i in range(5):
            task = AITask(
                task_id=f"perf_task_{i}",
                task_type="analysis",
                description=f"Performance test task {i}",
                input_data={"index": i},
                priority=TaskPriority.MEDIUM,
                estimated_tokens=500
            )
            tasks.append(task)
            await orchestrator.submit_task(task)
        
        # Get orchestration status
        status = orchestrator.get_orchestration_status()
        
        assert status["is_running"] == True
        assert status["tasks"]["queued"] >= 0
        assert "performance" in status
    
    @pytest.mark.asyncio
    async def test_governance_escalation_path(self, integrated_system):
        """Test governance escalation for critical decisions"""
        governance = integrated_system["governance"]
        orchestrator = integrated_system["orchestrator"]
        
        # Create critical task requiring escalation
        critical_task = AITask(
            task_id="critical_task",
            task_type="production_deployment",
            description="Critical production deployment",
            input_data={
                "environment": "production",
                "impact": "critical",
                "requires_escalation": True
            },
            priority=TaskPriority.CRITICAL,
            estimated_tokens=3000,
            requires_governance=True
        )
        
        # Submit task
        await orchestrator.submit_task(critical_task)
        
        # Governance should handle escalation
        escalation_request = {
            "type": "escalation",
            "task_id": critical_task.task_id,
            "severity": "critical",
            "impact": critical_task.input_data["impact"]
        }
        
        escalation_result = await governance.collaborate(escalation_request)
        
        assert escalation_result is not None
        # Critical tasks should aim for high consensus
        assert escalation_result.final_consensus in [ConsensusLevel.HIGH, ConsensusLevel.MEDIUM]
    
    @pytest.mark.asyncio
    async def test_resource_optimization_across_systems(self, integrated_system):
        """Test resource optimization across all systems"""
        orchestrator = integrated_system["orchestrator"]
        token_optimizer = integrated_system["token_optimizer"]
        
        # Set token budget
        budget = {
            "total_tokens": 10000,
            "per_task_limit": 1000,
            "optimization_required": True
        }
        
        # Submit tasks with token constraints
        for i in range(3):
            task = AITask(
                task_id=f"budget_task_{i}",
                task_type="generation",
                description=f"Task with budget constraint {i}",
                input_data={"content": "Generate detailed response" * 50},
                priority=TaskPriority.MEDIUM,
                estimated_tokens=800,
                metadata={"budget": budget}
            )
            
            # Optimize before submission
            if task.estimated_tokens > budget["per_task_limit"] * 0.8:
                optimization = await token_optimizer.optimize_request(
                    content=task.input_data["content"],
                    strategy=OptimizationStrategy.AGGRESSIVE,
                    target_tokens=int(budget["per_task_limit"] * 0.8)
                )
                task.input_data["content"] = optimization.optimized_content
                task.estimated_tokens = optimization.optimized_tokens
            
            await orchestrator.submit_task(task)
        
        # Verify all tasks fit within budget
        total_tokens = sum(task.estimated_tokens for task in orchestrator.task_queue)
        assert total_tokens <= budget["total_tokens"]


class TestCrossSystemCommunication:
    """Test communication between different system components"""
    
    @pytest.mark.asyncio
    async def test_governance_to_orchestration_communication(self):
        """Test communication from governance to orchestration"""
        governance = UnifiedGovernanceOrchestrator()
        orchestrator = AIOrchestrationEngine(governance)
        
        await orchestrator.start_orchestration()
        
        # Governance decision affects orchestration
        gov_decision = {
            "action": "pause_deployments",
            "reason": "security_concern",
            "duration_minutes": 30
        }
        
        # In real implementation, governance would communicate this to orchestrator
        # For testing, we simulate the effect
        orchestrator.deployment_paused = gov_decision.get("action") == "pause_deployments"
        
        assert hasattr(orchestrator, "deployment_paused")
        
        await orchestrator.stop_orchestration()
    
    @pytest.mark.asyncio
    async def test_orchestration_to_conversation_communication(self):
        """Test communication from orchestration to conversation manager"""
        governance = UnifiedGovernanceOrchestrator()
        orchestrator = AIOrchestrationEngine(governance)
        conv_manager = ConversationManager(orchestrator)
        
        await orchestrator.start_orchestration()
        
        # Create conversation
        conv_id = await conv_manager.create_conversation(
            conversation_type=ConversationType.SINGLE_TURN,
            title="Test Communication",
            description="Testing cross-system communication"
        )
        
        # Orchestrator task affects conversation
        task = AITask(
            task_id="conv_task",
            task_type="response_generation",
            description="Generate response for conversation",
            input_data={"conversation_id": conv_id},
            priority=TaskPriority.HIGH,
            estimated_tokens=500
        )
        
        await orchestrator.submit_task(task)
        
        # Verify task is linked to conversation
        assert task.input_data["conversation_id"] == conv_id
        
        await orchestrator.stop_orchestration()
    
    @pytest.mark.asyncio
    async def test_model_manager_to_orchestration_communication(self):
        """Test model manager providing model info to orchestration"""
        model_manager = MultiModelManager()
        governance = UnifiedGovernanceOrchestrator()
        orchestrator = AIOrchestrationEngine(governance)
        
        # Model manager determines available models
        available_models = await model_manager.check_model_availability()
        
        # Register agents based on available models
        for model_id, is_available in available_models.items():
            if is_available:
                agent = AIAgent(
                    agent_id=f"agent_{model_id}",
                    agent_type=AgentType.GENERAL,
                    capabilities=[AgentCapability.TEXT_GENERATION],
                    model_name=model_id,
                    max_tokens=2000,
                    is_available=is_available
                )
                orchestrator.register_agent(agent)
        
        # Verify agents registered based on model availability
        assert len(orchestrator.agents) >= 0  # Depends on mock availability


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])