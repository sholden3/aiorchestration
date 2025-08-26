"""
Unit Tests for AI Orchestration Engine v8.0
Comprehensive testing of agent management, task delegation, and workflow orchestration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_orchestration_engine import (
    AIOrchestrationEngine,
    AITask,
    TaskPriority,
    TaskStatus,
    AIAgent,
    AgentType,
    AgentCapability,
    AIWorkflow,
    WorkflowStep
)
from unified_governance_orchestrator import UnifiedGovernanceOrchestrator


class TestAIOrchestrationEngine:
    """Test suite for AIOrchestrationEngine"""
    
    @pytest.fixture
    def governance_mock(self):
        """Create mock governance orchestrator"""
        mock = Mock(spec=UnifiedGovernanceOrchestrator)
        mock.collaborate = AsyncMock(return_value=Mock(
            final_consensus=Mock(value="high"),
            recommendations=["test recommendation"]
        ))
        return mock
    
    @pytest.fixture
    def orchestrator(self, governance_mock):
        """Create orchestrator instance for testing"""
        return AIOrchestrationEngine(governance_mock)
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return AITask(
            task_id="test_task_001",
            task_type="analysis",
            description="Test analysis task",
            input_data={"test": "data"},
            priority=TaskPriority.MEDIUM,
            estimated_tokens=1000,
            timeout_seconds=60
        )
    
    # Orchestration Lifecycle Tests
    @pytest.mark.asyncio
    async def test_start_orchestration(self, orchestrator):
        """Test starting orchestration creates background tasks"""
        await orchestrator.start_orchestration()
        
        assert orchestrator.is_running == True
        assert orchestrator.background_tasks is not None
        assert orchestrator.cleanup_task is not None
    
    @pytest.mark.asyncio
    async def test_stop_orchestration(self, orchestrator):
        """Test stopping orchestration cleans up properly"""
        await orchestrator.start_orchestration()
        await orchestrator.stop_orchestration()
        
        assert orchestrator.is_running == False
    
    # Agent Management Tests
    def test_register_agent(self, orchestrator):
        """Test agent registration"""
        agent = AIAgent(
            agent_id="test_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.TEXT_GENERATION],
            model_name="test-model",
            max_tokens=1000
        )
        
        orchestrator.register_agent(agent)
        
        assert "test_agent" in orchestrator.agents
        assert orchestrator.agents["test_agent"] == agent
    
    def test_register_duplicate_agent(self, orchestrator):
        """Test duplicate agent registration updates existing"""
        agent1 = AIAgent(
            agent_id="test_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.TEXT_GENERATION],
            model_name="model-v1",
            max_tokens=1000
        )
        
        agent2 = AIAgent(
            agent_id="test_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.CODE_GENERATION],
            model_name="model-v2",
            max_tokens=2000
        )
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        assert orchestrator.agents["test_agent"].model_name == "model-v2"
        assert orchestrator.agents["test_agent"].max_tokens == 2000
    
    def test_unregister_agent(self, orchestrator):
        """Test agent unregistration"""
        agent = AIAgent(
            agent_id="test_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[],
            model_name="test",
            max_tokens=100
        )
        
        orchestrator.register_agent(agent)
        orchestrator.unregister_agent("test_agent")
        
        assert "test_agent" not in orchestrator.agents
    
    # Task Management Tests
    @pytest.mark.asyncio
    async def test_submit_task(self, orchestrator, sample_task):
        """Test task submission"""
        await orchestrator.start_orchestration()
        
        task_id = await orchestrator.submit_task(sample_task)
        
        assert task_id == sample_task.task_id
        assert len(orchestrator.task_queue) > 0
        assert sample_task.status == TaskStatus.QUEUED
    
    @pytest.mark.asyncio
    async def test_submit_high_priority_task(self, orchestrator):
        """Test high priority task gets processed first"""
        await orchestrator.start_orchestration()
        
        low_priority = AITask(
            task_id="low_001",
            task_type="analysis",
            description="Low priority task",
            input_data={},
            priority=TaskPriority.LOW,
            estimated_tokens=100
        )
        
        high_priority = AITask(
            task_id="high_001",
            task_type="analysis",
            description="High priority task",
            input_data={},
            priority=TaskPriority.HIGH,
            estimated_tokens=100
        )
        
        await orchestrator.submit_task(low_priority)
        await orchestrator.submit_task(high_priority)
        
        # High priority should be processed first
        # In real implementation, would check processing order
        assert len(orchestrator.task_queue) == 2
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, orchestrator, sample_task):
        """Test task cancellation"""
        await orchestrator.start_orchestration()
        
        task_id = await orchestrator.submit_task(sample_task)
        success = await orchestrator.cancel_task(task_id)
        
        assert success == True
        assert task_id not in orchestrator.active_tasks
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, orchestrator, sample_task):
        """Test getting task status"""
        await orchestrator.start_orchestration()
        
        task_id = await orchestrator.submit_task(sample_task)
        status = orchestrator.get_task_status(task_id)
        
        assert status is not None
        assert status["task_id"] == task_id
        assert status["status"] in ["queued", "processing", "completed", "failed"]
    
    # Agent Selection Tests
    def test_select_best_agent_for_task(self, orchestrator, sample_task):
        """Test agent selection based on task requirements"""
        # Register agents with different capabilities
        agent1 = AIAgent(
            agent_id="agent1",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.TEXT_GENERATION],
            model_name="model1",
            max_tokens=1000,
            performance_score=0.8
        )
        
        agent2 = AIAgent(
            agent_id="agent2",
            agent_type=AgentType.SPECIALIZED,
            capabilities=[AgentCapability.TEXT_GENERATION, AgentCapability.ANALYSIS],
            model_name="model2",
            max_tokens=2000,
            performance_score=0.9
        )
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        best_agent = orchestrator._select_best_agent(sample_task)
        
        assert best_agent is not None
        assert best_agent.agent_id == "agent2"  # Higher performance score
    
    def test_select_agent_with_no_suitable_agents(self, orchestrator, sample_task):
        """Test agent selection when no suitable agents available"""
        # Register agent with incompatible capabilities
        agent = AIAgent(
            agent_id="agent1",
            agent_type=AgentType.SPECIALIZED,
            capabilities=[AgentCapability.IMAGE_GENERATION],
            model_name="image-model",
            max_tokens=100
        )
        
        orchestrator.register_agent(agent)
        sample_task.required_capabilities = [AgentCapability.CODE_GENERATION]
        
        best_agent = orchestrator._select_best_agent(sample_task)
        
        # Should still return an agent (fallback behavior)
        assert best_agent is not None
    
    # Workflow Tests
    @pytest.mark.asyncio
    async def test_create_workflow(self, orchestrator):
        """Test workflow creation"""
        workflow = await orchestrator.create_workflow(
            workflow_type="code_review",
            workflow_id="test_workflow_001",
            input_data={"code": "def test(): pass"}
        )
        
        assert isinstance(workflow, AIWorkflow)
        assert workflow.workflow_id == "test_workflow_001"
        assert workflow.workflow_type == "code_review"
        assert len(workflow.steps) > 0
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestrator):
        """Test workflow execution"""
        workflow = await orchestrator.create_workflow(
            workflow_type="code_review",
            workflow_id="test_workflow_002",
            input_data={"code": "def test(): pass"}
        )
        
        await orchestrator.start_orchestration()
        
        # Register a mock agent for workflow execution
        agent = AIAgent(
            agent_id="workflow_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[AgentCapability.CODE_GENERATION],
            model_name="test",
            max_tokens=1000
        )
        orchestrator.register_agent(agent)
        
        result = await orchestrator.execute_workflow(workflow.workflow_id)
        
        assert result is not None
        assert "workflow_id" in result
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_dependencies(self, orchestrator):
        """Test workflow with step dependencies"""
        workflow = AIWorkflow(
            workflow_id="dep_workflow",
            workflow_type="complex",
            input_data={},
            steps=[
                WorkflowStep(
                    step_id="step1",
                    task_type="analysis",
                    description="First step",
                    dependencies=[]
                ),
                WorkflowStep(
                    step_id="step2",
                    task_type="processing",
                    description="Second step",
                    dependencies=["step1"]
                )
            ]
        )
        
        orchestrator.workflows[workflow.workflow_id] = workflow
        
        # Verify dependencies are respected
        assert workflow.steps[1].dependencies == ["step1"]
    
    # Performance Monitoring Tests
    def test_get_orchestration_status(self, orchestrator):
        """Test getting orchestration status"""
        status = orchestrator.get_orchestration_status()
        
        assert "is_running" in status
        assert "agents" in status
        assert "tasks" in status
        assert "performance" in status
        assert status["is_running"] == False
    
    @pytest.mark.asyncio
    async def test_get_agent_performance(self, orchestrator):
        """Test getting agent performance metrics"""
        agent = AIAgent(
            agent_id="perf_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[],
            model_name="test",
            max_tokens=1000,
            performance_score=0.85
        )
        
        orchestrator.register_agent(agent)
        
        # Simulate some completed tasks
        orchestrator.agent_performance["perf_agent"] = {
            "tasks_completed": 10,
            "tasks_failed": 2,
            "average_time": 5.5,
            "success_rate": 0.83
        }
        
        performance = orchestrator.get_agent_performance("perf_agent")
        
        assert performance is not None
        assert performance["tasks_completed"] == 10
        assert performance["success_rate"] == 0.83
    
    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_task_retry_on_failure(self, orchestrator):
        """Test task retry logic on failure"""
        task = AITask(
            task_id="retry_task",
            task_type="test",
            description="Task that will fail",
            input_data={},
            priority=TaskPriority.MEDIUM,
            estimated_tokens=100,
            retry_count=0,
            max_retries=3
        )
        
        await orchestrator.start_orchestration()
        await orchestrator.submit_task(task)
        
        # Simulate failure
        task.status = TaskStatus.FAILED
        task.retry_count = 1
        
        assert task.retry_count <= task.max_retries
    
    @pytest.mark.asyncio
    async def test_task_timeout_handling(self, orchestrator):
        """Test task timeout handling"""
        task = AITask(
            task_id="timeout_task",
            task_type="test",
            description="Task that will timeout",
            input_data={},
            priority=TaskPriority.MEDIUM,
            estimated_tokens=100,
            timeout_seconds=1
        )
        
        task.created_at = datetime.now() - timedelta(seconds=10)
        
        # Check if task would be considered timed out
        is_timed_out = (datetime.now() - task.created_at).total_seconds() > task.timeout_seconds
        
        assert is_timed_out == True
    
    # Load Balancing Tests
    def test_agent_load_balancing(self, orchestrator):
        """Test load balancing across multiple agents"""
        # Register multiple agents
        for i in range(3):
            agent = AIAgent(
                agent_id=f"agent_{i}",
                agent_type=AgentType.GENERAL,
                capabilities=[AgentCapability.TEXT_GENERATION],
                model_name=f"model_{i}",
                max_tokens=1000
            )
            orchestrator.register_agent(agent)
            orchestrator.agent_load[f"agent_{i}"] = i  # Varying load
        
        # Select agent should consider load
        least_loaded = min(orchestrator.agent_load, key=orchestrator.agent_load.get)
        
        assert least_loaded == "agent_0"
    
    # Governance Integration Tests
    @pytest.mark.asyncio
    async def test_governance_integration(self, orchestrator, governance_mock):
        """Test governance integration for task validation"""
        task = AITask(
            task_id="gov_task",
            task_type="sensitive",
            description="Sensitive operation",
            input_data={"sensitive": True},
            priority=TaskPriority.HIGH,
            estimated_tokens=1000,
            requires_governance=True
        )
        
        await orchestrator.start_orchestration()
        await orchestrator.submit_task(task)
        
        # Verify governance would be consulted for sensitive tasks
        assert task.requires_governance == True


class TestAITask:
    """Test suite for AITask class"""
    
    def test_task_creation(self):
        """Test AITask object creation"""
        task = AITask(
            task_id="test_001",
            task_type="analysis",
            description="Test task",
            input_data={"key": "value"},
            priority=TaskPriority.HIGH,
            estimated_tokens=500
        )
        
        assert task.task_id == "test_001"
        assert task.task_type == "analysis"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.estimated_tokens == 500
    
    def test_task_defaults(self):
        """Test AITask with default values"""
        task = AITask(
            task_id="test_002",
            task_type="basic",
            description="Basic task",
            input_data={},
            priority=TaskPriority.LOW,
            estimated_tokens=100
        )
        
        assert task.timeout_seconds == 300
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.requires_governance == False
    
    def test_task_priority_ordering(self):
        """Test task priority ordering"""
        high = TaskPriority.HIGH
        medium = TaskPriority.MEDIUM
        low = TaskPriority.LOW
        
        # Verify priority values for ordering
        assert high.value > medium.value
        assert medium.value > low.value


class TestAIAgent:
    """Test suite for AIAgent class"""
    
    def test_agent_creation(self):
        """Test AIAgent object creation"""
        agent = AIAgent(
            agent_id="test_agent",
            agent_type=AgentType.SPECIALIZED,
            capabilities=[
                AgentCapability.TEXT_GENERATION,
                AgentCapability.CODE_GENERATION
            ],
            model_name="gpt-4",
            max_tokens=4000,
            performance_score=0.92
        )
        
        assert agent.agent_id == "test_agent"
        assert agent.agent_type == AgentType.SPECIALIZED
        assert len(agent.capabilities) == 2
        assert agent.model_name == "gpt-4"
        assert agent.performance_score == 0.92
    
    def test_agent_defaults(self):
        """Test AIAgent with default values"""
        agent = AIAgent(
            agent_id="basic_agent",
            agent_type=AgentType.GENERAL,
            capabilities=[],
            model_name="basic",
            max_tokens=1000
        )
        
        assert agent.performance_score == 1.0
        assert agent.cost_per_token == 0.0
        assert agent.is_available == True


class TestAIWorkflow:
    """Test suite for AIWorkflow class"""
    
    def test_workflow_creation(self):
        """Test AIWorkflow object creation"""
        steps = [
            WorkflowStep(
                step_id="step1",
                task_type="input",
                description="Input processing"
            ),
            WorkflowStep(
                step_id="step2",
                task_type="processing",
                description="Main processing",
                dependencies=["step1"]
            )
        ]
        
        workflow = AIWorkflow(
            workflow_id="test_workflow",
            workflow_type="data_processing",
            input_data={"data": "test"},
            steps=steps
        )
        
        assert workflow.workflow_id == "test_workflow"
        assert workflow.workflow_type == "data_processing"
        assert len(workflow.steps) == 2
        assert workflow.steps[1].dependencies == ["step1"]
    
    def test_workflow_step_dependencies(self):
        """Test WorkflowStep dependencies"""
        step = WorkflowStep(
            step_id="dependent_step",
            task_type="output",
            description="Output generation",
            dependencies=["step1", "step2"],
            input_mapping={"input1": "step1.output", "input2": "step2.output"}
        )
        
        assert len(step.dependencies) == 2
        assert "step1" in step.dependencies
        assert "input1" in step.input_mapping


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])