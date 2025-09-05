# Workflow Governance System: Managed TODO & Process Enforcement

A comprehensive system for enforcing structured development workflows with governance hooks at every step, integrated TODO management, and AI persona validation.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Governance System                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Workflow State  │◄►│ TODO Manager    │◄►│ Hook Validator  │  │
│  │ Machine         │  │ & Enforcer      │  │ & Executor      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────────────────────────────────────────────────┤
│  │           Persona Consensus Integration                     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │  │ Dr. Sarah   │ │ Marcus      │ │ Emily       │ │ Custom │ │
│  │  │ Chen        │ │ Rodriguez   │ │ Watson      │ │ Expert │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
│  └─────────────────────────────────────────────────────────────┘
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────────────────────────────────────────────────┤
│  │              External Integration Layer                     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  │ Claude Code │ │ Git Hooks   │ │ CI/CD       │           │
│  │  │ Hooks       │ │ Integration │ │ Pipeline    │           │
│  │  └─────────────┘ └─────────────┘ └─────────────┘           │
│  └─────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components Implementation

### 1. Workflow State Machine

```python
#!/usr/bin/env python3
"""
Workflow State Machine - Defines and enforces development workflow states
"""
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import asyncio

class WorkflowState(Enum):
    """Allowed workflow states"""
    IDLE = "idle"
    CONTEXT_PULL = "context_pull"
    PERSONA_CONSENSUS = "persona_consensus" 
    CONSENSUS_VALIDATION = "consensus_validation"
    IMPLEMENTATION_PLAN = "implementation_plan"
    PLAN_VALIDATION = "plan_validation"
    PHASE_CREATION = "phase_creation"
    PHASE_VALIDATION = "phase_validation"
    FEATURE_IMPLEMENTATION = "feature_implementation"
    CODE_VALIDATION = "code_validation"
    FEATURE_TESTING = "feature_testing"
    TEST_VALIDATION = "test_validation"
    RECURSIVE_TESTING = "recursive_testing"
    RECURSIVE_VALIDATION = "recursive_validation"
    PRE_COMMIT = "pre_commit"
    COMMIT_EXECUTION = "commit_execution"
    POST_COMMIT = "post_commit"
    PRE_POST = "pre_post"
    POST_EXECUTION = "post_execution"
    POST_POST = "post_post"
    PRE_CLEANUP = "pre_cleanup"
    DOCUMENTATION_UPDATE = "documentation_update"
    CLEANUP_EXECUTION = "cleanup_execution"
    CLEANUP_VALIDATION = "cleanup_validation"
    COMPLETED = "completed"

@dataclass
class WorkflowTransition:
    """Defines a workflow state transition"""
    from_state: WorkflowState
    to_state: WorkflowState
    hook_functions: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    required_artifacts: List[str] = field(default_factory=list)
    timeout_minutes: int = 60
    auto_transition: bool = False
    requires_approval: bool = False

@dataclass  
class WorkflowContext:
    """Context for a workflow execution"""
    workflow_id: str
    feature_name: str
    current_state: WorkflowState
    started_at: datetime
    updated_at: datetime
    artifacts: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    persona_decisions: Dict[str, Any] = field(default_factory=dict)
    hook_execution_log: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowStateMachine:
    """Manages workflow state transitions and validation"""
    
    def __init__(self, config_path: str = ".governance/workflows/config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_workflow_config()
        self.transitions = self.build_transition_graph()
        self.active_workflows: Dict[str, WorkflowContext] = {}
        
    def load_workflow_config(self) -> Dict[str, Any]:
        """Load workflow configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        # Default workflow configuration
        return {
            "default_timeout_minutes": 60,
            "require_approval": {
                "states": ["consensus_validation", "plan_validation", "cleanup_validation"],
                "approvers": ["alex_novak", "sarah_chen"]
            },
            "auto_transitions": {
                "commit_execution": "post_commit",
                "post_execution": "post_post"
            },
            "artifacts": {
                "persona_consensus": ["consensus_report.md", "decision_log.json"],
                "implementation_plan": ["implementation_plan.md", "architecture_diagram.md"],
                "phase_creation": ["phase_definition.md", "milestone_tracker.json"],
                "feature_implementation": ["source_code", "unit_tests"],
                "feature_testing": ["test_results.json", "coverage_report.html"],
                "documentation_update": ["updated_docs", "changelog.md"]
            },
            "hooks": {
                "pre_state_hooks": {},
                "post_state_hooks": {},
                "validation_hooks": {}
            }
        }
    
    def build_transition_graph(self) -> Dict[WorkflowState, List[WorkflowTransition]]:
        """Build the allowed state transition graph"""
        transitions = {
            WorkflowState.IDLE: [
                WorkflowTransition(
                    from_state=WorkflowState.IDLE,
                    to_state=WorkflowState.CONTEXT_PULL,
                    hook_functions=["initialize_context", "pull_project_state"],
                    validation_rules=["validate_workspace", "check_git_status"],
                    required_artifacts=[]
                )
            ],
            WorkflowState.CONTEXT_PULL: [
                WorkflowTransition(
                    from_state=WorkflowState.CONTEXT_PULL,
                    to_state=WorkflowState.PERSONA_CONSENSUS,
                    hook_functions=["invoke_persona_consensus"],
                    validation_rules=["validate_context_completeness"],
                    required_artifacts=["context_summary.md"]
                )
            ],
            WorkflowState.PERSONA_CONSENSUS: [
                WorkflowTransition(
                    from_state=WorkflowState.PERSONA_CONSENSUS,
                    to_state=WorkflowState.CONSENSUS_VALIDATION,
                    hook_functions=["validate_consensus_quality"],
                    validation_rules=["check_persona_agreement", "validate_evidence"],
                    required_artifacts=["consensus_report.md", "decision_log.json"],
                    requires_approval=True
                )
            ],
            WorkflowState.CONSENSUS_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.CONSENSUS_VALIDATION,
                    to_state=WorkflowState.IMPLEMENTATION_PLAN,
                    hook_functions=["create_implementation_plan"],
                    validation_rules=["consensus_approved"],
                    required_artifacts=["validated_consensus.json"]
                )
            ],
            WorkflowState.IMPLEMENTATION_PLAN: [
                WorkflowTransition(
                    from_state=WorkflowState.IMPLEMENTATION_PLAN,
                    to_state=WorkflowState.PLAN_VALIDATION,
                    hook_functions=["validate_plan_completeness", "check_plan_standards"],
                    validation_rules=["plan_meets_architecture_standards", "plan_saved_correctly"],
                    required_artifacts=["implementation_plan.md", "architecture_diagram.md"],
                    requires_approval=True
                )
            ],
            WorkflowState.PLAN_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.PLAN_VALIDATION,
                    to_state=WorkflowState.PHASE_CREATION,
                    hook_functions=["create_development_phases"],
                    validation_rules=["plan_approved"],
                    required_artifacts=["approved_plan.json"]
                )
            ],
            WorkflowState.PHASE_CREATION: [
                WorkflowTransition(
                    from_state=WorkflowState.PHASE_CREATION,
                    to_state=WorkflowState.PHASE_VALIDATION,
                    hook_functions=["validate_phases"],
                    validation_rules=["phases_meet_standards", "phases_saved_correctly"],
                    required_artifacts=["phase_definition.md", "milestone_tracker.json"]
                )
            ],
            WorkflowState.PHASE_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.PHASE_VALIDATION,
                    to_state=WorkflowState.FEATURE_IMPLEMENTATION,
                    hook_functions=["begin_implementation"],
                    validation_rules=["phases_approved"],
                    required_artifacts=["approved_phases.json"]
                )
            ],
            WorkflowState.FEATURE_IMPLEMENTATION: [
                WorkflowTransition(
                    from_state=WorkflowState.FEATURE_IMPLEMENTATION,
                    to_state=WorkflowState.CODE_VALIDATION,
                    hook_functions=["validate_code_quality"],
                    validation_rules=["code_meets_standards", "tests_written"],
                    required_artifacts=["source_code", "unit_tests"]
                )
            ],
            WorkflowState.CODE_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.CODE_VALIDATION,
                    to_state=WorkflowState.FEATURE_TESTING,
                    hook_functions=["run_feature_tests"],
                    validation_rules=["code_quality_approved"],
                    required_artifacts=["validated_code.json"]
                )
            ],
            WorkflowState.FEATURE_TESTING: [
                WorkflowTransition(
                    from_state=WorkflowState.FEATURE_TESTING,
                    to_state=WorkflowState.TEST_VALIDATION,
                    hook_functions=["analyze_test_results"],
                    validation_rules=["tests_executed", "results_collected"],
                    required_artifacts=["test_results.json", "coverage_report.html"]
                )
            ],
            WorkflowState.TEST_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.TEST_VALIDATION,
                    to_state=WorkflowState.RECURSIVE_TESTING,
                    hook_functions=["initiate_recursive_tests"],
                    validation_rules=["test_results_satisfactory"],
                    required_artifacts=["validated_tests.json"]
                ),
                WorkflowTransition(
                    from_state=WorkflowState.TEST_VALIDATION,
                    to_state=WorkflowState.FEATURE_IMPLEMENTATION,
                    hook_functions=["return_to_implementation"],
                    validation_rules=["test_results_require_changes"],
                    required_artifacts=["test_failure_analysis.json"]
                )
            ],
            WorkflowState.RECURSIVE_TESTING: [
                WorkflowTransition(
                    from_state=WorkflowState.RECURSIVE_TESTING,
                    to_state=WorkflowState.RECURSIVE_VALIDATION,
                    hook_functions=["validate_recursive_results"],
                    validation_rules=["recursive_tests_completed"],
                    required_artifacts=["recursive_test_results.json"]
                )
            ],
            WorkflowState.RECURSIVE_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.RECURSIVE_VALIDATION,
                    to_state=WorkflowState.PRE_COMMIT,
                    hook_functions=["prepare_for_commit"],
                    validation_rules=["recursive_results_satisfactory"],
                    required_artifacts=["final_validation.json"]
                ),
                WorkflowTransition(
                    from_state=WorkflowState.RECURSIVE_VALIDATION,
                    to_state=WorkflowState.RECURSIVE_TESTING,
                    hook_functions=["retry_recursive_tests"],
                    validation_rules=["recursive_results_need_retry"],
                    required_artifacts=["retry_analysis.json"]
                )
            ],
            WorkflowState.PRE_COMMIT: [
                WorkflowTransition(
                    from_state=WorkflowState.PRE_COMMIT,
                    to_state=WorkflowState.COMMIT_EXECUTION,
                    hook_functions=["execute_commit"],
                    validation_rules=["pre_commit_validations_passed"],
                    required_artifacts=["pre_commit_results.json"],
                    auto_transition=True
                )
            ],
            WorkflowState.COMMIT_EXECUTION: [
                WorkflowTransition(
                    from_state=WorkflowState.COMMIT_EXECUTION,
                    to_state=WorkflowState.POST_COMMIT,
                    hook_functions=["post_commit_cleanup"],
                    validation_rules=[],
                    required_artifacts=["commit_hash.txt"],
                    auto_transition=True
                )
            ],
            WorkflowState.POST_COMMIT: [
                WorkflowTransition(
                    from_state=WorkflowState.POST_COMMIT,
                    to_state=WorkflowState.PRE_POST,
                    hook_functions=["prepare_for_post"],
                    validation_rules=["post_commit_cleanup_completed"],
                    required_artifacts=["cleanup_results.json"]
                )
            ],
            WorkflowState.PRE_POST: [
                WorkflowTransition(
                    from_state=WorkflowState.PRE_POST,
                    to_state=WorkflowState.POST_EXECUTION,
                    hook_functions=["execute_post_operations"],
                    validation_rules=["pre_post_validations_passed"],
                    required_artifacts=["pre_post_results.json"],
                    auto_transition=True
                )
            ],
            WorkflowState.POST_EXECUTION: [
                WorkflowTransition(
                    from_state=WorkflowState.POST_EXECUTION,
                    to_state=WorkflowState.POST_POST,
                    hook_functions=["finalize_post_operations"],
                    validation_rules=[],
                    required_artifacts=["post_results.json"],
                    auto_transition=True
                )
            ],
            WorkflowState.POST_POST: [
                WorkflowTransition(
                    from_state=WorkflowState.POST_POST,
                    to_state=WorkflowState.PRE_CLEANUP,
                    hook_functions=["prepare_for_cleanup"],
                    validation_rules=["post_operations_completed"],
                    required_artifacts=["post_completion.json"]
                )
            ],
            WorkflowState.PRE_CLEANUP: [
                WorkflowTransition(
                    from_state=WorkflowState.PRE_CLEANUP,
                    to_state=WorkflowState.DOCUMENTATION_UPDATE,
                    hook_functions=["update_documentation"],
                    validation_rules=["cleanup_prerequisites_met"],
                    required_artifacts=["cleanup_checklist.json"]
                )
            ],
            WorkflowState.DOCUMENTATION_UPDATE: [
                WorkflowTransition(
                    from_state=WorkflowState.DOCUMENTATION_UPDATE,
                    to_state=WorkflowState.CLEANUP_EXECUTION,
                    hook_functions=["execute_cleanup"],
                    validation_rules=["documentation_updated"],
                    required_artifacts=["updated_docs", "changelog.md"]
                )
            ],
            WorkflowState.CLEANUP_EXECUTION: [
                WorkflowTransition(
                    from_state=WorkflowState.CLEANUP_EXECUTION,
                    to_state=WorkflowState.CLEANUP_VALIDATION,
                    hook_functions=["validate_cleanup"],
                    validation_rules=["cleanup_executed"],
                    required_artifacts=["cleanup_results.json"],
                    requires_approval=True
                )
            ],
            WorkflowState.CLEANUP_VALIDATION: [
                WorkflowTransition(
                    from_state=WorkflowState.CLEANUP_VALIDATION,
                    to_state=WorkflowState.COMPLETED,
                    hook_functions=["finalize_workflow"],
                    validation_rules=["cleanup_approved", "no_missing_artifacts"],
                    required_artifacts=["final_validation.json"]
                )
            ]
        }
        
        return transitions
    
    async def transition_workflow(self, workflow_id: str, to_state: WorkflowState, 
                                force: bool = False) -> Dict[str, Any]:
        """Execute a workflow state transition"""
        if workflow_id not in self.active_workflows:
            return {
                "success": False,
                "error": f"Workflow {workflow_id} not found"
            }
        
        workflow = self.active_workflows[workflow_id]
        current_state = workflow.current_state
        
        # Find valid transition
        valid_transitions = self.transitions.get(current_state, [])
        transition = None
        
        for t in valid_transitions:
            if t.to_state == to_state:
                transition = t
                break
        
        if not transition and not force:
            return {
                "success": False,
                "error": f"Invalid transition from {current_state} to {to_state}",
                "valid_transitions": [t.to_state.value for t in valid_transitions]
            }
        
        # Execute transition
        try:
            result = await self.execute_transition(workflow, transition, force)
            
            if result["success"]:
                # Update workflow state
                workflow.current_state = to_state
                workflow.updated_at = datetime.now()
                
                # Log transition
                workflow.hook_execution_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "transition": f"{current_state.value} -> {to_state.value}",
                    "hooks_executed": transition.hook_functions if transition else [],
                    "validation_results": result.get("validation_results", {}),
                    "forced": force
                })
                
                # Save workflow state
                self.save_workflow_state(workflow)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Transition execution failed: {e}",
                "exception": str(e)
            }
    
    async def execute_transition(self, workflow: WorkflowContext, 
                               transition: Optional[WorkflowTransition], 
                               force: bool) -> Dict[str, Any]:
        """Execute the hooks and validations for a transition"""
        if not transition and not force:
            return {"success": False, "error": "No transition definition"}
        
        results = {
            "success": True,
            "hook_results": {},
            "validation_results": {},
            "artifacts_checked": {},
            "approval_status": {}
        }
        
        if not transition:
            # Force transition without validation
            return results
        
        # Execute pre-hooks
        for hook_func in transition.hook_functions:
            try:
                hook_result = await self.execute_hook(hook_func, workflow)
                results["hook_results"][hook_func] = hook_result
                
                if not hook_result.get("success", True):
                    results["success"] = False
                    break
                    
            except Exception as e:
                results["hook_results"][hook_func] = {
                    "success": False,
                    "error": str(e)
                }
                results["success"] = False
                break
        
        # Run validations if hooks succeeded
        if results["success"]:
            for validation_rule in transition.validation_rules:
                try:
                    validation_result = await self.execute_validation(validation_rule, workflow)
                    results["validation_results"][validation_rule] = validation_result
                    
                    if not validation_result.get("passed", False):
                        results["success"] = False
                        break
                        
                except Exception as e:
                    results["validation_results"][validation_rule] = {
                        "passed": False,
                        "error": str(e)
                    }
                    results["success"] = False
                    break
        
        # Check required artifacts if validations passed
        if results["success"]:
            for artifact in transition.required_artifacts:
                artifact_check = self.check_artifact_exists(artifact, workflow)
                results["artifacts_checked"][artifact] = artifact_check
                
                if not artifact_check.get("exists", False):
                    results["success"] = False
                    break
        
        # Check approval requirements if everything else passed
        if results["success"] and transition.requires_approval:
            approval_result = await self.check_approval_status(workflow, transition)
            results["approval_status"] = approval_result
            
            if not approval_result.get("approved", False):
                results["success"] = False
        
        return results
    
    async def execute_hook(self, hook_name: str, workflow: WorkflowContext) -> Dict[str, Any]:
        """Execute a specific workflow hook"""
        # This would integrate with your existing hook system
        hook_registry = WorkflowHookRegistry()
        
        if hook_registry.has_hook(hook_name):
            return await hook_registry.execute_hook(hook_name, workflow)
        else:
            # Fallback to mock execution for undefined hooks
            return {
                "success": True,
                "message": f"Mock execution of {hook_name}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_validation(self, validation_name: str, 
                               workflow: WorkflowContext) -> Dict[str, Any]:
        """Execute a validation rule"""
        validator_registry = WorkflowValidatorRegistry()
        
        if validator_registry.has_validator(validation_name):
            return await validator_registry.execute_validation(validation_name, workflow)
        else:
            # Default validation - check if basic requirements are met
            return {
                "passed": True,
                "message": f"Default validation for {validation_name}",
                "timestamp": datetime.now().isoformat()
            }
    
    def check_artifact_exists(self, artifact_name: str, 
                             workflow: WorkflowContext) -> Dict[str, Any]:
        """Check if required artifact exists"""
        artifacts_dir = Path(f".governance/workflows/{workflow.workflow_id}/artifacts")
        artifact_path = artifacts_dir / artifact_name
        
        return {
            "exists": artifact_path.exists(),
            "path": str(artifact_path),
            "size": artifact_path.stat().st_size if artifact_path.exists() else 0,
            "modified": artifact_path.stat().st_mtime if artifact_path.exists() else None
        }
    
    async def check_approval_status(self, workflow: WorkflowContext, 
                                  transition: WorkflowTransition) -> Dict[str, Any]:
        """Check if required approvals are obtained"""
        required_approvers = self.config.get("require_approval", {}).get("approvers", [])
        
        # This would integrate with your persona system
        approvals = {}
        for approver in required_approvers:
            # Check if approver has signed off on this transition
            approval_key = f"{transition.from_state.value}_{transition.to_state.value}"
            approvals[approver] = workflow.persona_decisions.get(f"{approver}_approval_{approval_key}", False)
        
        approved_count = sum(1 for approved in approvals.values() if approved)
        required_count = len(required_approvers)
        
        return {
            "approved": approved_count >= required_count,
            "approvals": approvals,
            "required": required_count,
            "received": approved_count
        }
    
    def save_workflow_state(self, workflow: WorkflowContext) -> None:
        """Persist workflow state to disk"""
        workflow_dir = Path(f".governance/workflows/{workflow.workflow_id}")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = workflow_dir / "state.json"
        
        # Convert dataclass to dict for serialization
        workflow_data = {
            "workflow_id": workflow.workflow_id,
            "feature_name": workflow.feature_name,
            "current_state": workflow.current_state.value,
            "started_at": workflow.started_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "artifacts": workflow.artifacts,
            "validation_results": workflow.validation_results,
            "persona_decisions": workflow.persona_decisions,
            "hook_execution_log": workflow.hook_execution_log,
            "metadata": workflow.metadata
        }
        
        with open(state_file, 'w') as f:
            json.dump(workflow_data, f, indent=2)
    
    def create_workflow(self, feature_name: str, workflow_type: str = "feature") -> str:
        """Create a new workflow instance"""
        import uuid
        
        workflow_id = f"{workflow_type}_{uuid.uuid4().hex[:8]}"
        
        workflow = WorkflowContext(
            workflow_id=workflow_id,
            feature_name=feature_name,
            current_state=WorkflowState.IDLE,
            started_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.active_workflows[workflow_id] = workflow
        self.save_workflow_state(workflow)
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[workflow_id]
        valid_transitions = self.transitions.get(workflow.current_state, [])
        
        return {
            "workflow_id": workflow_id,
            "feature_name": workflow.feature_name,
            "current_state": workflow.current_state.value,
            "started_at": workflow.started_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "next_possible_states": [t.to_state.value for t in valid_transitions],
            "artifacts_created": len(workflow.artifacts),
            "validations_passed": len([v for v in workflow.validation_results.values() if v.get("passed", False)]),
            "personas_involved": list(workflow.persona_decisions.keys())
        }
```

### 2. Managed TODO System

```python
#!/usr/bin/env python3
"""
Managed TODO System - Enforces structured TODO creation and workflow compliance
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

class TodoType(Enum):
    """Types of managed TODOs"""
    WORKFLOW_STEP = "workflow_step"
    PERSONA_CONSENSUS = "persona_consensus"
    IMPLEMENTATION_PLAN = "implementation_plan"
    PHASE_DEFINITION = "phase_definition"
    FEATURE_IMPLEMENTATION = "feature_implementation"
    TEST_VALIDATION = "test_validation"
    DOCUMENTATION = "documentation"
    CLEANUP = "cleanup"

class TodoPriority(Enum):
    """TODO priority levels"""
    P0_CRITICAL = "P0"  # Must be done immediately
    P1_HIGH = "P1"      # Must be done this session
    P2_MEDIUM = "P2"    # Should be done this week
    P3_LOW = "P3"       # Can be done when time permits

class TodoStatus(Enum):
    """TODO lifecycle status"""
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    VALIDATION_PENDING = "validation_pending"
    PERSONA_REVIEW = "persona_review"
    APPROVED = "approved"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

@dataclass
class ManagedTodo:
    """A workflow-managed TODO item"""
    id: str
    todo_type: TodoType
    priority: TodoPriority
    status: TodoStatus
    title: str
    description: str
    workflow_id: str
    workflow_state: str
    
    # Workflow integration
    required_artifacts: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    persona_approvals_needed: List[str] = field(default_factory=list)
    blocks_transition_to: List[str] = field(default_factory=list)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Context
    context_data: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    persona_feedback: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    linked_todos: List[str] = field(default_factory=list)
    
class ManagedTodoSystem:
    """Manages workflow-integrated TODO creation and validation"""
    
    def __init__(self, config_path: str = ".governance/todos/config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_todo_config()
        self.todos: Dict[str, ManagedTodo] = {}
        self.todo_templates = self.load_todo_templates()
        
    def load_todo_config(self) -> Dict[str, Any]:
        """Load TODO management configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        return {
            "enforced_format": True,
            "require_workflow_integration": True,
            "auto_priority_assignment": True,
            "persona_validation_required": ["persona_consensus", "implementation_plan"],
            "priority_rules": {
                "P0": {"max_age_hours": 4, "requires_immediate_attention": True},
                "P1": {"max_age_hours": 24, "blocks_workflow": True},
                "P2": {"max_age_days": 7, "can_be_rescheduled": True},
                "P3": {"max_age_days": 30, "optional_completion": True}
            },
            "validation_rules": {
                "title_min_length": 10,
                "description_min_length": 50,
                "require_acceptance_criteria": True,
                "require_definition_of_done": True
            }
        }
    
    def load_todo_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load TODO templates for different workflow steps"""
        return {
            "persona_consensus": {
                "title_template": "Achieve persona consensus on {feature_name} approach",
                "description_template": """
**Objective**: Get consensus from all relevant personas on the approach for {feature_name}

**Required Personas**:
{persona_list}

**Key Questions to Address**:
1. Technical feasibility and architecture approach
2. User experience considerations and design patterns
3. Performance implications and optimization strategies
4. Risk assessment and mitigation strategies

**Acceptance Criteria**:
- [ ] All required personas have provided input
- [ ] Consensus achieved on technical approach
- [ ] Risk assessment completed and documented
- [ ] Decision rationale clearly documented

**Definition of Done**:
- [ ] consensus_report.md created with all persona inputs
- [ ] decision_log.json updated with consensus decision
- [ ] No unresolved conflicts between personas
- [ ] Next steps clearly defined
""",
                "required_artifacts": ["consensus_report.md", "decision_log.json"],
                "validation_rules": ["consensus_achieved", "all_personas_participated"],
                "persona_approvals_needed": ["alex_novak", "sarah_chen"]
            },
            
            "implementation_plan": {
                "title_template": "Create implementation plan for {feature_name}",
                "description_template": """
**Objective**: Develop comprehensive implementation plan for {feature_name}

**Requirements**:
1. Detailed technical specification
2. Architecture diagrams and component breakdown
3. Development timeline with milestones
4. Testing strategy and validation approach
5. Risk assessment and mitigation plans

**Acceptance Criteria**:
- [ ] Implementation plan document created
- [ ] Architecture diagrams completed
- [ ] Timeline with realistic milestones defined
- [ ] Testing strategy documented
- [ ] Performance requirements specified

**Definition of Done**:
- [ ] implementation_plan.md saved in correct location
- [ ] Architecture diagrams included and reviewed
- [ ] Plan approved by required personas
- [ ] Ready for phase creation step
""",
                "required_artifacts": ["implementation_plan.md", "architecture_diagram.md"],
                "validation_rules": ["plan_completeness", "architecture_standards_met"],
                "persona_approvals_needed": ["sarah_chen"]
            },
            
            "phase_definition": {
                "title_template": "Define development phases for {feature_name}",
                "description_template": """
**Objective**: Break down implementation into manageable development phases

**Requirements**:
1. Phase breakdown with clear deliverables
2. Dependencies between phases identified
3. Resource allocation and timeline per phase
4. Success criteria for each phase
5. Risk assessment per phase

**Acceptance Criteria**:
- [ ] All phases clearly defined with scope
- [ ] Dependencies mapped between phases
- [ ] Timeline and resource requirements estimated
- [ ] Success criteria defined for each phase
- [ ] Risk mitigation strategies in place

**Definition of Done**:
- [ ] phase_definition.md created with all phases
- [ ] milestone_tracker.json configured
- [ ] Phase dependencies validated
- [ ] Ready to begin implementation
""",
                "required_artifacts": ["phase_definition.md", "milestone_tracker.json"],
                "validation_rules": ["phases_well_defined", "dependencies_resolved"],
                "persona_approvals_needed": ["alex_novak"]
            },
            
            "feature_implementation": {
                "title_template": "Implement {phase_name} of {feature_name}",
                "description_template": """
**Objective**: Implement the {phase_name} phase of {feature_name}

**Implementation Requirements**:
1. Write production-quality code following standards
2. Create comprehensive unit tests
3. Add integration tests where applicable
4. Update documentation as needed
5. Follow established coding patterns

**Quality Standards**:
- [ ] Code passes all linting checks
- [ ] Test coverage >= 80%
- [ ] No security vulnerabilities introduced
- [ ] Performance requirements met
- [ ] Code reviewed and approved

**Definition of Done**:
- [ ] All code written and tested
- [ ] Tests pass with adequate coverage
- [ ] Code meets quality standards
- [ ] Ready for validation phase
""",
                "required_artifacts": ["source_code", "unit_tests", "integration_tests"],
                "validation_rules": ["code_quality_standards", "test_coverage_adequate"],
                "persona_approvals_needed": []
            }
        }
    
    def create_workflow_todo(self, todo_type: TodoType, workflow_id: str, 
                           workflow_state: str, context: Dict[str, Any]) -> str:
        """Create a workflow-managed TODO"""
        
        # Validate that TODO creation is allowed
        if not self.validate_todo_creation(todo_type, workflow_id, workflow_state):
            raise ValueError(f"TODO creation not allowed for {todo_type} in state {workflow_state}")
        
        # Get template for this TODO type
        template = self.todo_templates.get(todo_type.value, {})
        
        if not template:
            raise ValueError(f"No template found for TODO type: {todo_type}")
        
        # Generate TODO content from template
        title = self.render_template(template.get("title_template", ""), context)
        description = self.render_template(template.get("description_template", ""), context)
        
        # Determine priority automatically
        priority = self.determine_priority(todo_type, workflow_state, context)
        
        # Create TODO ID
        todo_id = f"{todo_type.value}_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create managed TODO
        todo = ManagedTodo(
            id=todo_id,
            todo_type=todo_type,
            priority=priority,
            status=TodoStatus.CREATED,
            title=title,
            description=description,
            workflow_id=workflow_id,
            workflow_state=workflow_state,
            required_artifacts=template.get("required_artifacts", []),
            validation_rules=template.get("validation_rules", []),
            persona_approvals_needed=template.get("persona_approvals_needed", []),
            context_data=context,
            due_date=self.calculate_due_date(priority)
        )
        
        # Set workflow blocking behavior
        todo.blocks_transition_to = self.get_blocked_transitions(todo_type, workflow_state)
        
        # Store TODO
        self.todos[todo_id] = todo
        self.save_todo(todo)
        
        # Notify relevant personas if needed
        if todo.persona_approvals_needed:
            self.notify_personas(todo)
        
        return todo_id
    
    def validate_todo_creation(self, todo_type: TodoType, workflow_id: str, 
                             workflow_state: str) -> bool:
        """Validate that TODO can be created in current context"""
        
        # Check if workflow allows this TODO type in current state
        allowed_todos = {
            "context_pull": [TodoType.WORKFLOW_STEP],
            "persona_consensus": [TodoType.PERSONA_CONSENSUS],
            "implementation_plan": [TodoType.IMPLEMENTATION_PLAN],
            "phase_creation": [TodoType.PHASE_DEFINITION],
            "feature_implementation": [TodoType.FEATURE_IMPLEMENTATION],
            "feature_testing": [TodoType.TEST_VALIDATION],
            "documentation_update": [TodoType.DOCUMENTATION],
            "cleanup_execution": [TodoType.CLEANUP]
        }
        
        if workflow_state in allowed_todos:
            return todo_type in allowed_todos[workflow_state]
        
        return False
    
    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render TODO template with context data"""
        rendered = template
        
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, list):
                value = "\n".join([f"- {item}" for item in value])
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def determine_priority(self, todo_type: TodoType, workflow_state: str, 
                         context: Dict[str, Any]) -> TodoPriority:
        """Automatically determine TODO priority"""
        
        # Critical workflow steps get P0
        critical_steps = ["persona_consensus", "implementation_plan", "feature_testing"]
        if todo_type.value in critical_steps:
            return TodoPriority.P0_CRITICAL
        
        # Implementation tasks get P1
        if todo_type == TodoType.FEATURE_IMPLEMENTATION:
            return TodoPriority.P1_HIGH
        
        # Documentation and cleanup get P2
        if todo_type in [TodoType.DOCUMENTATION, TodoType.CLEANUP]:
            return TodoPriority.P2_MEDIUM
        
        # Default to P1
        return TodoPriority.P1_HIGH
    
    def calculate_due_date(self, priority: TodoPriority) -> datetime:
        """Calculate due date based on priority"""
        now = datetime.now()
        
        if priority == TodoPriority.P0_CRITICAL:
            return now + timedelta(hours=4)
        elif priority == TodoPriority.P1_HIGH:
            return now + timedelta(hours=24)
        elif priority == TodoPriority.P2_MEDIUM:
            return now + timedelta(days=7)
        else:  # P3
            return now + timedelta(days=30)
    
    def get_blocked_transitions(self, todo_type: TodoType, 
                              current_state: str) -> List[str]:
        """Determine which workflow transitions are blocked by this TODO"""
        
        # Critical TODOs block all forward progress
        if todo_type in [TodoType.PERSONA_CONSENSUS, TodoType.IMPLEMENTATION_PLAN]:
            return ["*"]  # Blocks all transitions
        
        # Other TODOs block specific transitions
        blocking_map = {
            "persona_consensus": ["consensus_validation"],
            "implementation_plan": ["plan_validation"],
            "phase_creation": ["phase_validation"],
            "feature_implementation": ["code_validation"],
            "feature_testing": ["test_validation"],
            "documentation_update": ["cleanup_execution"],
            "cleanup_execution": ["cleanup_validation"]
        }
        
        return blocking_map.get(current_state, [])
    
    def validate_todo_completion(self, todo_id: str) -> Dict[str, Any]:
        """Validate that a TODO can be marked as completed"""
        
        if todo_id not in self.todos:
            return {"valid": False, "error": "TODO not found"}
        
        todo = self.todos[todo_id]
        validation_results = {"valid": True, "checks": {}}
        
        # Check required artifacts exist
        for artifact in todo.required_artifacts:
            artifact_path = Path(f".governance/workflows/{todo.workflow_id}/artifacts/{artifact}")
            exists = artifact_path.exists()
            validation_results["checks"][f"artifact_{artifact}"] = {
                "passed": exists,
                "message": f"Artifact {artifact} {'exists' if exists else 'missing'}"
            }
            
            if not exists:
                validation_results["valid"] = False
        
        # Run validation rules
        for rule in todo.validation_rules:
            rule_result = self.execute_validation_rule(rule, todo)
            validation_results["checks"][f"rule_{rule}"] = rule_result
            
            if not rule_result.get("passed", False):
                validation_results["valid"] = False
        
        # Check persona approvals if needed
        if todo.persona_approvals_needed:
            for persona in todo.persona_approvals_needed:
                approval_key = f"{persona}_approval"
                has_approval = todo.persona_feedback.get(approval_key, False)
                validation_results["checks"][f"approval_{persona}"] = {
                    "passed": has_approval,
                    "message": f"Approval from {persona} {'received' if has_approval else 'pending'}"
                }
                
                if not has_approval:
                    validation_results["valid"] = False
        
        return validation_results
    
    def execute_validation_rule(self, rule_name: str, todo: ManagedTodo) -> Dict[str, Any]:
        """Execute a specific validation rule"""
        
        # Implementation would connect to your validation system
        rule_implementations = {
            "consensus_achieved": self.validate_consensus_achieved,
            "all_personas_participated": self.validate_persona_participation,
            "plan_completeness": self.validate_plan_completeness,
            "architecture_standards_met": self.validate_architecture_standards,
            "phases_well_defined": self.validate_phases_definition,
            "dependencies_resolved": self.validate_dependencies_resolved,
            "code_quality_standards": self.validate_code_quality,
            "test_coverage_adequate": self.validate_test_coverage
        }
        
        if rule_name in rule_implementations:
            return rule_implementations[rule_name](todo)
        else:
            return {"passed": True, "message": f"Default validation for {rule_name}"}
    
    # Validation rule implementations (these would integrate with your governance system)
    def validate_consensus_achieved(self, todo: ManagedTodo) -> Dict[str, Any]:
        """Validate that persona consensus was achieved"""
        consensus_file = Path(f".governance/workflows/{todo.workflow_id}/artifacts/consensus_report.md")
        
        if not consensus_file.exists():
            return {"passed": False, "message": "Consensus report not found"}
        
        # Check consensus report content
        with open(consensus_file) as f:
            content = f.read()
        
        # Look for consensus indicators
        consensus_indicators = ["consensus achieved", "agreement reached", "approved by all"]
        has_consensus = any(indicator in content.lower() for indicator in consensus_indicators)
        
        return {
            "passed": has_consensus,
            "message": "Consensus achieved" if has_consensus else "No clear consensus found"
        }
    
    def validate_persona_participation(self, todo: ManagedTodo) -> Dict[str, Any]:
        """Validate that all required personas participated"""
        required_personas = todo.context_data.get("persona_list", [])
        
        # Check if all personas provided feedback
        feedback_count = len([k for k in todo.persona_feedback.keys() if k.endswith("_feedback")])
        
        return {
            "passed": feedback_count >= len(required_personas),
            "message": f"Got feedback from {feedback_count}/{len(required_personas)} personas"
        }
    
    def validate_plan_completeness(self, todo: ManagedTodo) -> Dict[str, Any]:
        """Validate implementation plan completeness"""
        plan_file = Path(f".governance/workflows/{todo.workflow_id}/artifacts/implementation_plan.md")
        
        if not plan_file.exists():
            return {"passed": False, "message": "Implementation plan not found"}
        
        with open(plan_file) as f:
            content = f.read()
        
        # Check for required sections
        required_sections = ["technical specification", "architecture", "timeline", "testing", "risks"]
        missing_sections = []
        
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        return {
            "passed": len(missing_sections) == 0,
            "message": f"Missing sections: {missing_sections}" if missing_sections else "All sections present"
        }
    
    def save_todo(self, todo: ManagedTodo) -> None:
        """Save TODO to persistent storage"""
        todos_dir = Path(f".governance/workflows/{todo.workflow_id}/todos")
        todos_dir.mkdir(parents=True, exist_ok=True)
        
        todo_file = todos_dir / f"{todo.id}.json"
        
        # Convert to dict for serialization
        todo_data = {
            "id": todo.id,
            "todo_type": todo.todo_type.value,
            "priority": todo.priority.value,
            "status": todo.status.value,
            "title": todo.title,
            "description": todo.description,
            "workflow_id": todo.workflow_id,
            "workflow_state": todo.workflow_state,
            "required_artifacts": todo.required_artifacts,
            "validation_rules": todo.validation_rules,
            "persona_approvals_needed": todo.persona_approvals_needed,
            "blocks_transition_to": todo.blocks_transition_to,
            "created_at": todo.created_at.isoformat(),
            "assigned_to": todo.assigned_to,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
            "context_data": todo.context_data,
            "validation_results": todo.validation_results,
            "persona_feedback": todo.persona_feedback,
            "tags": todo.tags,
            "linked_todos": todo.linked_todos
        }
        
        with open(todo_file, 'w') as f:
            json.dump(todo_data, f, indent=2)
    
    def notify_personas(self, todo: ManagedTodo) -> None:
        """Notify required personas about TODO requiring their attention"""
        # This would integrate with your persona notification system
        print(f"🔔 Notifying personas {todo.persona_approvals_needed} about TODO: {todo.title}")
    
    def force_todo_structure(self, raw_todo_text: str) -> Optional[str]:
        """Convert unstructured TODO to managed format or reject it"""
        
        if not self.config.get("enforced_format", True):
            return raw_todo_text
        
        # Reject unstructured TODOs that don't follow managed format
        managed_pattern = r"TODO\(managed:(\w+):(\w+)\):"
        
        if not re.match(managed_pattern, raw_todo_text):
            return None  # Reject - must use managed TODO creation
        
        return raw_todo_text
    
    def get_workflow_blocking_todos(self, workflow_id: str) -> List[ManagedTodo]:
        """Get all TODOs that are blocking workflow progression"""
        blocking_todos = []
        
        for todo in self.todos.values():
            if (todo.workflow_id == workflow_id and 
                todo.status not in [TodoStatus.COMPLETED, TodoStatus.CANCELLED] and
                todo.blocks_transition_to):
                blocking_todos.append(todo)
        
        return blocking_todos
```

### 3. Hook Integration System

```python
#!/usr/bin/env python3
"""
Workflow Hook Integration - Connects workflow transitions with validation hooks
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json
from pathlib import Path

class WorkflowHookRegistry:
    """Registry for workflow-specific hooks"""
    
    def __init__(self):
        self.hooks: Dict[str, Callable] = {}
        self.register_default_hooks()
    
    def register_hook(self, hook_name: str, hook_function: Callable) -> None:
        """Register a workflow hook function"""
        self.hooks[hook_name] = hook_function
    
    def has_hook(self, hook_name: str) -> bool:
        """Check if hook is registered"""
        return hook_name in self.hooks
    
    async def execute_hook(self, hook_name: str, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Execute a registered hook"""
        if hook_name not in self.hooks:
            return {"success": False, "error": f"Hook {hook_name} not found"}
        
        try:
            hook_function = self.hooks[hook_name]
            
            # Execute hook (async or sync)
            if asyncio.iscoroutinefunction(hook_function):
                result = await hook_function(workflow)
            else:
                result = hook_function(workflow)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register_default_hooks(self) -> None:
        """Register default workflow hooks"""
        
        # Context management hooks
        self.register_hook("initialize_context", self.initialize_context_hook)
        self.register_hook("pull_project_state", self.pull_project_state_hook)
        
        # Persona integration hooks
        self.register_hook("invoke_persona_consensus", self.invoke_persona_consensus_hook)
        self.register_hook("validate_consensus_quality", self.validate_consensus_quality_hook)
        
        # Planning hooks
        self.register_hook("create_implementation_plan", self.create_implementation_plan_hook)
        self.register_hook("create_development_phases", self.create_development_phases_hook)
        
        # Implementation hooks
        self.register_hook("begin_implementation", self.begin_implementation_hook)
        self.register_hook("validate_code_quality", self.validate_code_quality_hook)
        
        # Testing hooks
        self.register_hook("run_feature_tests", self.run_feature_tests_hook)
        self.register_hook("analyze_test_results", self.analyze_test_results_hook)
        self.register_hook("initiate_recursive_tests", self.initiate_recursive_tests_hook)
        
        # Commit hooks
        self.register_hook("prepare_for_commit", self.prepare_for_commit_hook)
        self.register_hook("execute_commit", self.execute_commit_hook)
        self.register_hook("post_commit_cleanup", self.post_commit_cleanup_hook)
        
        # Documentation and cleanup hooks
        self.register_hook("update_documentation", self.update_documentation_hook)
        self.register_hook("execute_cleanup", self.execute_cleanup_hook)
        self.register_hook("validate_cleanup", self.validate_cleanup_hook)
    
    # Hook implementations
    async def initialize_context_hook(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Initialize workflow context"""
        context_dir = Path(f".governance/workflows/{workflow.workflow_id}")
        context_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial context files
        context_data = {
            "workflow_id": workflow.workflow_id,
            "feature_name": workflow.feature_name,
            "initialized_at": workflow.started_at.isoformat(),
            "project_state": await self.capture_project_state()
        }
        
        context_file = context_dir / "context.json"
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        workflow.artifacts["context.json"] = str(context_file)
        
        return {"context_initialized": True, "context_file": str(context_file)}
    
    async def capture_project_state(self) -> Dict[str, Any]:
        """Capture current project state for context"""
        import subprocess
        
        try:
            # Git status
            git_result = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True)
            
            # Recent commits
            log_result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                      capture_output=True, text=True)
            
            # Current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            
            return {
                "git_status": git_result.stdout,
                "recent_commits": log_result.stdout,
                "current_branch": branch_result.stdout.strip(),
                "working_directory": str(Path.cwd())
            }
        except:
            return {"error": "Could not capture project state"}
    
    async def invoke_persona_consensus_hook(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Trigger persona consensus process"""
        from governance.core.unified_governance_orchestrator import UnifiedGovernanceOrchestrator
        
        orchestrator = UnifiedGovernanceOrchestrator()
        
        # Prepare consensus request
        consensus_request = {
            "feature_name": workflow.feature_name,
            "workflow_id": workflow.workflow_id,
            "context": workflow.artifacts.get("context.json", ""),
            "request_type": "feature_consensus"
        }
        
        # Execute consensus process
        result = await orchestrator.execute_governance_process(
            f"Feature consensus for {workflow.feature_name}",
            consensus_request
        )
        
        # Save consensus results
        artifacts_dir = Path(f".governance/workflows/{workflow.workflow_id}/artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        consensus_file = artifacts_dir / "consensus_report.md"
        with open(consensus_file, 'w') as f:
            f.write(result.get("consensus_report", "# Consensus Report\n\nNo consensus achieved"))
        
        decision_file = artifacts_dir / "decision_log.json"
        with open(decision_file, 'w') as f:
            json.dump(result.get("decision_log", {}), f, indent=2)
        
        workflow.artifacts["consensus_report.md"] = str(consensus_file)
        workflow.artifacts["decision_log.json"] = str(decision_file)
        workflow.persona_decisions.update(result.get("persona_decisions", {}))
        
        return {
            "consensus_achieved": result.get("consensus_achieved", False),
            "personas_participated": result.get("personas_participated", []),
            "consensus_file": str(consensus_file),
            "decision_file": str(decision_file)
        }
    
    def validate_code_quality_hook(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Validate code quality standards"""
        import subprocess
        
        try:
            # Run code quality checks
            quality_results = {}
            
            # Python linting
            flake8_result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
            quality_results["linting"] = {
                "passed": flake8_result.returncode == 0,
                "output": flake8_result.stdout
            }
            
            # Test coverage
            coverage_result = subprocess.run(['python', '-m', 'pytest', '--cov=.'], 
                                           capture_output=True, text=True)
            quality_results["coverage"] = {
                "passed": coverage_result.returncode == 0,
                "output": coverage_result.stdout
            }
            
            # Security scan
            bandit_result = subprocess.run(['bandit', '-r', '.'], 
                                         capture_output=True, text=True)
            quality_results["security"] = {
                "passed": bandit_result.returncode == 0,
                "output": bandit_result.stdout
            }
            
            # Overall quality assessment
            all_passed = all(result["passed"] for result in quality_results.values())
            
            # Save results
            artifacts_dir = Path(f".governance/workflows/{workflow.workflow_id}/artifacts")
            quality_file = artifacts_dir / "code_quality_results.json"
            
            with open(quality_file, 'w') as f:
                json.dump(quality_results, f, indent=2)
            
            workflow.artifacts["code_quality_results.json"] = str(quality_file)
            
            return {
                "quality_passed": all_passed,
                "results": quality_results,
                "quality_file": str(quality_file)
            }
            
        except Exception as e:
            return {"quality_passed": False, "error": str(e)}
    
    def execute_commit_hook(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Execute git commit with validation"""
        import subprocess
        
        try:
            # Prepare commit message
            commit_message = f"feat({workflow.feature_name}): implement workflow step\n\nWorkflow-ID: {workflow.workflow_id}\nState: {workflow.current_state.value}"
            
            # Stage changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit with message
            commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                         capture_output=True, text=True)
            
            if commit_result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                           capture_output=True, text=True)
                commit_hash = hash_result.stdout.strip()
                
                # Save commit info
                artifacts_dir = Path(f".governance/workflows/{workflow.workflow_id}/artifacts")
                commit_file = artifacts_dir / "commit_hash.txt"
                
                with open(commit_file, 'w') as f:
                    f.write(commit_hash)
                
                workflow.artifacts["commit_hash.txt"] = str(commit_file)
                workflow.metadata["commit_hash"] = commit_hash
                
                return {
                    "commit_successful": True,
                    "commit_hash": commit_hash,
                    "commit_message": commit_message
                }
            else:
                return {
                    "commit_successful": False,
                    "error": commit_result.stderr,
                    "output": commit_result.stdout
                }
                
        except Exception as e:
            return {"commit_successful": False, "error": str(e)}

class WorkflowValidatorRegistry:
    """Registry for workflow validation rules"""
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self.register_default_validators()
    
    def register_validator(self, validator_name: str, validator_function: Callable) -> None:
        """Register a validation rule function"""
        self.validators[validator_name] = validator_function
    
    def has_validator(self, validator_name: str) -> bool:
        """Check if validator is registered"""
        return validator_name in self.validators
    
    async def execute_validation(self, validator_name: str, 
                               workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Execute a validation rule"""
        if validator_name not in self.validators:
            return {"passed": False, "error": f"Validator {validator_name} not found"}
        
        try:
            validator_function = self.validators[validator_name]
            
            if asyncio.iscoroutinefunction(validator_function):
                result = await validator_function(workflow)
            else:
                result = validator_function(workflow)
            
            return result
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def register_default_validators(self) -> None:
        """Register default validation rules"""
        
        self.register_validator("validate_workspace", self.validate_workspace)
        self.register_validator("check_git_status", self.check_git_status)
        self.register_validator("validate_context_completeness", self.validate_context_completeness)
        self.register_validator("check_persona_agreement", self.check_persona_agreement)
        self.register_validator("validate_evidence", self.validate_evidence)
        self.register_validator("consensus_approved", self.consensus_approved)
        self.register_validator("plan_meets_architecture_standards", self.plan_meets_architecture_standards)
        self.register_validator("plan_saved_correctly", self.plan_saved_correctly)
        self.register_validator("code_meets_standards", self.code_meets_standards)
        self.register_validator("tests_written", self.tests_written)
        self.register_validator("test_results_satisfactory", self.test_results_satisfactory)
        self.register_validator("cleanup_approved", self.cleanup_approved)
        self.register_validator("no_missing_artifacts", self.no_missing_artifacts)
    
    # Validator implementations
    def validate_workspace(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Validate workspace is ready for development"""
        workspace_checks = {
            "git_repo": (Path.cwd() / ".git").exists(),
            "governance_dir": (Path.cwd() / ".governance").exists(),
            "writable": os.access(Path.cwd(), os.W_OK)
        }
        
        all_passed = all(workspace_checks.values())
        
        return {
            "passed": all_passed,
            "message": "Workspace validation passed" if all_passed else "Workspace validation failed",
            "checks": workspace_checks
        }
    
    def check_git_status(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Check git repository status"""
        import subprocess
        
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            has_changes = bool(result.stdout.strip())
            
            return {
                "passed": True,  # Always pass, just informational
                "message": f"Git status: {'Changes present' if has_changes else 'Clean working tree'}",
                "has_changes": has_changes,
                "status_output": result.stdout
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Git status check failed: {e}",
                "error": str(e)
            }
    
    def check_persona_agreement(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Validate persona consensus was achieved"""
        consensus_file = workflow.artifacts.get("consensus_report.md")
        
        if not consensus_file or not Path(consensus_file).exists():
            return {
                "passed": False,
                "message": "Consensus report not found"
            }
        
        with open(consensus_file) as f:
            content = f.read().lower()
        
        # Look for consensus indicators
        agreement_phrases = [
            "consensus achieved",
            "agreement reached", 
            "all personas agree",
            "approved by consensus"
        ]
        
        has_consensus = any(phrase in content for phrase in agreement_phrases)
        
        return {
            "passed": has_consensus,
            "message": "Persona consensus achieved" if has_consensus else "No clear consensus found"
        }
    
    def code_meets_standards(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Validate code meets quality standards"""
        quality_file = workflow.artifacts.get("code_quality_results.json")
        
        if not quality_file or not Path(quality_file).exists():
            return {
                "passed": False,
                "message": "Code quality results not found"
            }
        
        with open(quality_file) as f:
            quality_results = json.load(f)
        
        # Check if all quality checks passed
        all_passed = all(result.get("passed", False) for result in quality_results.values())
        
        return {
            "passed": all_passed,
            "message": "Code meets quality standards" if all_passed else "Code quality issues found",
            "quality_summary": quality_results
        }
    
    def no_missing_artifacts(self, workflow: 'WorkflowContext') -> Dict[str, Any]:
        """Validate all required artifacts are present"""
        required_artifacts = [
            "consensus_report.md",
            "implementation_plan.md", 
            "phase_definition.md",
            "test_results.json",
            "updated_docs"
        ]
        
        missing_artifacts = []
        for artifact in required_artifacts:
            artifact_path = Path(f".governance/workflows/{workflow.workflow_id}/artifacts/{artifact}")
            if not artifact_path.exists():
                missing_artifacts.append(artifact)
        
        return {
            "passed": len(missing_artifacts) == 0,
            "message": f"All artifacts present" if not missing_artifacts else f"Missing: {missing_artifacts}",
            "missing_artifacts": missing_artifacts
        }
```

## Integration with Existing Systems

### 1. Claude Code Integration

```python
#!/usr/bin/env python3
"""
Claude Code Workflow Integration
Enforces workflow compliance in Claude Code operations
"""

class ClaudeCodeWorkflowIntegration:
    """Integrates workflow management with Claude Code hooks"""
    
    def __init__(self):
        self.workflow_manager = WorkflowStateMachine()
        self.todo_system = ManagedTodoSystem()
    
    def claude_code_pre_tool_use_hook(self, hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Claude Code PreToolUse hook integration"""
        
        # Check if there's an active workflow
        active_workflows = self.get_active_workflows()
        
        if not active_workflows:
            # No active workflow - create one if this is a feature request
            if self.is_feature_request(hook_data):
                workflow_id = self.workflow_manager.create_workflow(
                    feature_name=self.extract_feature_name(hook_data),
                    workflow_type="feature"
                )
                
                return {
                    "allowed": True,
                    "message": f"Created new workflow: {workflow_id}",
                    "workflow_created": workflow_id
                }
        
        # Check workflow compliance for tool use
        for workflow_id in active_workflows:
            blocking_todos = self.todo_system.get_workflow_blocking_todos(workflow_id)
            
            if blocking_todos:
                return {
                    "allowed": False,
                    "message": f"Workflow blocked by {len(blocking_todos)} incomplete TODOs",
                    "blocking_todos": [todo.title for todo in blocking_todos[:3]]
                }
        
        return {"allowed": True, "message": "Workflow compliance validated"}
    
    def force_todo_creation(self, claude_request: str) -> Optional[str]:
        """Force structured TODO creation instead of allowing freeform"""
        
        # Detect TODO creation attempts
        todo_patterns = [
            r"TODO:?\s*(.+)",
            r"#\s*TODO\s*(.+)",
            r"create.*todo.*for\s*(.+)"
        ]
        
        for pattern in todo_patterns:
            match = re.search(pattern, claude_request, re.IGNORECASE)
            if match:
                # Block freeform TODO creation
                return self.suggest_managed_todo_creation(match.group(1))
        
        return None
    
    def suggest_managed_todo_creation(self, todo_description: str) -> str:
        """Suggest proper managed TODO creation"""
        return f"""
❌ Freeform TODO creation blocked by workflow governance.

Instead, use managed TODO creation:

```python
from workflow_governance import ManagedTodoSystem
todo_system = ManagedTodoSystem()

todo_id = todo_system.create_workflow_todo(
    todo_type=TodoType.FEATURE_IMPLEMENTATION,  # or appropriate type
    workflow_id="your_active_workflow_id",
    workflow_state="current_state",
    context={{
        "feature_name": "extracted from your request",
        "description": "{todo_description}",
        "priority": "P1"  # will be auto-determined
    }}
)
```

💡 This ensures proper workflow integration, validation, and persona approval workflows.
"""

### 2. Governance Integration Bridge

```python
async def integrate_with_governance(self, workflow_id: str, transition_data: Dict[str, Any]):
    """Integration point with existing governance system"""
    
    from governance.core.runtime_governance import RuntimeGovernanceSystem
    from governance.core.runtime_governance import DecisionContext
    
    governance = RuntimeGovernanceSystem()
    
    # Create governance context for workflow transition
    decision_context = DecisionContext(
        decision_id=f"workflow_transition_{workflow_id}_{datetime.now().isoformat()}",
        agent_id="workflow_manager",
        decision_type="workflow_transition",
        input_data=transition_data,
        proposed_output=transition_data.get("to_state"),
        confidence_score=0.9,
        risk_score=self.calculate_transition_risk(transition_data)
    )
    
    # Use governance system to validate transition
    governance_result = await governance.validate_decision(decision_context)
    
    return governance_result.decision == "approved"
```

## Usage Examples

### 1. Start a Feature Workflow

```bash
# Initialize new feature workflow
python workflow_manager.py create-workflow \
  --feature-name "user-authentication-system" \
  --type "feature"

# This creates managed TODOs automatically:
# 1. Context Pull TODO
# 2. Persona Consensus TODO  
# 3. Implementation Plan TODO
# etc.
```

### 2. Workflow State Management

```python
# Get workflow status
workflow_status = workflow_manager.get_workflow_status("feature_auth_12345")

# Force transition (emergency override)
await workflow_manager.transition_workflow(
    workflow_id="feature_auth_12345",
    to_state=WorkflowState.FEATURE_IMPLEMENTATION,
    force=True
)

# Normal transition (with validation)
result = await workflow_manager.transition_workflow(
    workflow_id="feature_auth_12345", 
    to_state=WorkflowState.CONSENSUS_VALIDATION
)
```

### 3. TODO Governance

```python
# Create structured TODO (replaces freeform)
todo_id = todo_system.create_workflow_todo(
    todo_type=TodoType.PERSONA_CONSENSUS,
    workflow_id="feature_auth_12345",
    workflow_state="persona_consensus",
    context={
        "feature_name": "user authentication system",
        "persona_list": ["sarah_chen", "marcus_rodriguez", "emily_watson"],
        "technical_complexity": "high"
    }
)

# Validate TODO completion
validation_result = todo_system.validate_todo_completion(todo_id)
if validation_result["valid"]:
    todo.status = TodoStatus.COMPLETED
```

## Benefits of This System

1. **Enforced Structure**: No more ad-hoc TODOs or workflow deviations
2. **Persona Integration**: Built-in governance and validation at every step
3. **Audit Trail**: Complete tracking of decisions and validations
4. **Workflow Compliance**: Automatic blocking of invalid transitions
5. **Claude Code Integration**: Seamless integration with existing AI tooling
6. **Quality Gates**: Multiple validation points ensure standards compliance
7. **Context Preservation**: Rich context maintained throughout workflow
8. **Emergency Overrides**: Force capabilities for exceptional circumstances

This system transforms chaotic development into a structured, governed, and validated process while maintaining flexibility through configuration and emergency overrides.