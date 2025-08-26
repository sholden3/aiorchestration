#!/usr/bin/env python3
"""
Claude CLI Governance Integration v9.3
Implements governance-enforced Claude CLI operations with intelligent oversight
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from unified_governance_orchestrator import UnifiedGovernanceOrchestrator, CollaborationPhase
from ai_orchestration_engine import AIOrchestrationEngine, AITask, TaskPriority
from conversation_manager import ConversationManager, ConversationType
from token_optimization_engine import TokenOptimizationEngine, OptimizationStrategy
from production_governance_system import ProductionGovernanceSystem, GovernanceAction, GovernanceScope

logger = logging.getLogger(__name__)


class ClaudeCommand(Enum):
    """Available Claude CLI commands"""
    CHAT = "chat"
    EDIT = "edit"
    WRITE = "write"
    READ = "read"
    ANALYZE = "analyze"
    REFACTOR = "refactor"
    TEST = "test"
    DEPLOY = "deploy"
    REVIEW = "review"
    OPTIMIZE = "optimize"


class GovernanceLevel(Enum):
    """Governance enforcement levels"""
    NONE = "none"
    ADVISORY = "advisory"
    ENFORCED = "enforced"
    STRICT = "strict"


class ClaudeOperation:
    """Represents a Claude CLI operation with governance context"""
    
    def __init__(
        self,
        command: ClaudeCommand,
        args: List[str],
        governance_level: GovernanceLevel = GovernanceLevel.ENFORCED,
        context: Optional[Dict[str, Any]] = None
    ):
        self.operation_id = f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
        self.command = command
        self.args = args
        self.governance_level = governance_level
        self.context = context or {}
        self.created_at = datetime.now()
        self.governance_approved = False
        self.governance_decision = None
        self.execution_result = None


class ClaudeGovernanceIntegration:
    """Main Claude CLI governance integration system"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize all governance and orchestration components"""
        self.governance = UnifiedGovernanceOrchestrator()
        self.production_governance = ProductionGovernanceSystem(
            project_root or Path.cwd()
        )
        self.orchestrator = AIOrchestrationEngine(self.governance)
        self.conversation_manager = ConversationManager(self.orchestrator)
        self.token_optimizer = TokenOptimizationEngine()
        
        # Claude CLI configuration
        self.claude_cli_path = "claude"  # Assumes Claude Code CLI is in PATH
        self.default_governance_level = GovernanceLevel.ENFORCED
        
        # Governance rules for different operations
        self.governance_rules = {
            ClaudeCommand.WRITE: {
                "requires_approval": True,
                "risk_level": "medium",
                "review_personas": ["Dr. Sarah Chen", "Emily Watson"],
                "auto_backup": True
            },
            ClaudeCommand.EDIT: {
                "requires_approval": True,
                "risk_level": "medium", 
                "review_personas": ["Dr. Sarah Chen", "Emily Watson"],
                "auto_backup": True
            },
            ClaudeCommand.DEPLOY: {
                "requires_approval": True,
                "risk_level": "high",
                "review_personas": ["Dr. Sarah Chen", "Marcus Rodriguez", "Emily Watson"],
                "additional_checks": ["security", "performance", "rollback_plan"]
            },
            ClaudeCommand.REFACTOR: {
                "requires_approval": True,
                "risk_level": "high",
                "review_personas": ["Dr. Sarah Chen", "Marcus Rodriguez"],
                "additional_checks": ["test_coverage", "impact_analysis"]
            },
            ClaudeCommand.CHAT: {
                "requires_approval": False,
                "risk_level": "low",
                "auto_optimize": True
            },
            ClaudeCommand.READ: {
                "requires_approval": False,
                "risk_level": "low"
            },
            ClaudeCommand.ANALYZE: {
                "requires_approval": False,
                "risk_level": "low",
                "auto_optimize": True
            }
        }
        
        # Track active operations
        self.active_operations: Dict[str, ClaudeOperation] = {}
        self.completed_operations: Dict[str, ClaudeOperation] = {}
        
    async def initialize(self):
        """Initialize all components"""
        await self.orchestrator.start_orchestration()
        logger.info("Claude CLI Governance Integration v9.3 initialized")
        
    async def execute_claude_command(
        self,
        command: ClaudeCommand,
        args: List[str],
        governance_level: Optional[GovernanceLevel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute Claude CLI command with governance oversight"""
        
        # Create operation
        operation = ClaudeOperation(
            command=command,
            args=args,
            governance_level=governance_level or self.default_governance_level,
            context=context or {}
        )
        
        self.active_operations[operation.operation_id] = operation
        
        try:
            # Apply governance based on level
            if operation.governance_level != GovernanceLevel.NONE:
                governance_result = await self._apply_governance(operation)
                operation.governance_decision = governance_result
                
                if not governance_result.get("approved", False):
                    return {
                        "success": False,
                        "operation_id": operation.operation_id,
                        "error": "Governance check failed",
                        "governance_feedback": governance_result.get("feedback", "No feedback provided"),
                        "recommendations": governance_result.get("recommendations", [])
                    }
                
                operation.governance_approved = True
            
            # Optimize command if applicable
            if self._should_optimize(operation):
                operation = await self._optimize_operation(operation)
            
            # Execute Claude CLI command
            execution_result = await self._execute_claude_cli(operation)
            operation.execution_result = execution_result
            
            # Post-execution governance
            await self._post_execution_governance(operation)
            
            # Move to completed
            self.completed_operations[operation.operation_id] = operation
            del self.active_operations[operation.operation_id]
            
            return {
                "success": True,
                "operation_id": operation.operation_id,
                "result": execution_result,
                "governance_applied": operation.governance_level != GovernanceLevel.NONE,
                "optimization_applied": operation.context.get("optimization_applied", False)
            }
            
        except Exception as e:
            logger.error(f"Claude command execution failed: {str(e)}")
            operation.execution_result = {"error": str(e)}
            
            return {
                "success": False,
                "operation_id": operation.operation_id,
                "error": str(e),
                "governance_applied": operation.governance_level != GovernanceLevel.NONE
            }
    
    async def _apply_governance(self, operation: ClaudeOperation) -> Dict[str, Any]:
        """Apply governance rules to Claude operation"""
        
        command_rules = self.governance_rules.get(operation.command, {})
        
        # Check if approval required
        if command_rules.get("requires_approval", False):
            
            # Create governance request
            governance_request = {
                "type": "claude_cli_operation",
                "command": operation.command.value,
                "args": operation.args,
                "risk_level": command_rules.get("risk_level", "low"),
                "context": operation.context,
                "operation_id": operation.operation_id
            }
            
            # Get governance decision
            if operation.governance_level == GovernanceLevel.STRICT:
                # Full governance collaboration
                collaboration_result = await self.governance.collaborate(governance_request)
                
                return {
                    "approved": collaboration_result.final_consensus.value in ["high", "medium"],
                    "feedback": "Full governance collaboration completed",
                    "recommendations": collaboration_result.recommendations,
                    "evidence": collaboration_result.evidence_trail
                }
                
            elif operation.governance_level == GovernanceLevel.ENFORCED:
                # Production governance check
                production_decision = await self.production_governance.execute_governance_action(
                    action_type=GovernanceAction.CODE_REVIEW,
                    scope=GovernanceScope.PROJECT,
                    request_data=governance_request
                )
                
                return {
                    "approved": production_decision.consensus_level.value in ["high", "medium"],
                    "feedback": production_decision.rationale,
                    "recommendations": production_decision.implementation_plan.get("recommendations", [])
                }
                
            elif operation.governance_level == GovernanceLevel.ADVISORY:
                # Advisory only - always approve but provide guidance
                advisory_result = await self._generate_advisory_guidance(operation)
                
                return {
                    "approved": True,
                    "feedback": "Advisory guidance provided",
                    "recommendations": advisory_result.get("recommendations", [])
                }
        
        # No approval required
        return {"approved": True, "feedback": "No governance approval required"}
    
    async def _generate_advisory_guidance(self, operation: ClaudeOperation) -> Dict[str, Any]:
        """Generate advisory guidance for Claude operations"""
        
        guidance_task = AITask(
            task_id=f"advisory_{operation.operation_id}",
            task_type="advisory_guidance",
            description=f"Provide advisory guidance for Claude {operation.command.value} operation",
            input_data={
                "command": operation.command.value,
                "args": operation.args,
                "context": operation.context
            },
            priority=TaskPriority.LOW,
            estimated_tokens=1000
        )
        
        # Submit to orchestrator
        task_id = await self.orchestrator.submit_task(guidance_task)
        
        # Wait for completion
        await asyncio.sleep(1)
        
        if task_id in self.orchestrator.completed_tasks:
            result = self.orchestrator.completed_tasks[task_id]
            return result.result or {}
        
        return {"recommendations": ["Consider reviewing command parameters for optimization"]}
    
    def _should_optimize(self, operation: ClaudeOperation) -> bool:
        """Determine if operation should be optimized"""
        command_rules = self.governance_rules.get(operation.command, {})
        return command_rules.get("auto_optimize", False)
    
    async def _optimize_operation(self, operation: ClaudeOperation) -> ClaudeOperation:
        """Optimize Claude operation for token efficiency"""
        
        try:
            # Optimize arguments that contain text content
            for i, arg in enumerate(operation.args):
                if len(arg) > 500:  # Only optimize substantial text
                    optimization_result = await self.token_optimizer.optimize_request(
                        content=arg,
                        strategy=OptimizationStrategy.BALANCED
                    )
                    
                    if optimization_result.tokens_saved > 50:  # Significant savings
                        operation.args[i] = optimization_result.optimized_content
                        operation.context["optimization_applied"] = True
                        operation.context["tokens_saved"] = optimization_result.tokens_saved
            
        except Exception as e:
            logger.warning(f"Operation optimization failed: {str(e)}")
        
        return operation
    
    async def _execute_claude_cli(self, operation: ClaudeOperation) -> Dict[str, Any]:
        """Execute actual Claude CLI command"""
        
        try:
            # Build command
            cmd = [self.claude_cli_path, operation.command.value] + operation.args
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=300  # 5 minute timeout
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore"),
                "command": " ".join(cmd)
            }
            
        except asyncio.TimeoutError:
            return {
                "returncode": -1,
                "error": "Command timeout after 5 minutes"
            }
        except FileNotFoundError:
            return {
                "returncode": -1,
                "error": f"Claude CLI not found at: {self.claude_cli_path}"
            }
        except Exception as e:
            return {
                "returncode": -1,
                "error": str(e)
            }
    
    async def _post_execution_governance(self, operation: ClaudeOperation):
        """Apply post-execution governance checks"""
        
        # Log operation for audit trail
        audit_data = {
            "operation_id": operation.operation_id,
            "command": operation.command.value,
            "governance_level": operation.governance_level.value,
            "success": operation.execution_result.get("returncode") == 0,
            "timestamp": operation.created_at.isoformat()
        }
        
        # Store in governance system (would log to audit trail in production)
        logger.info(f"Governance audit: {audit_data}")
    
    async def claude_chat(
        self,
        message: str,
        governance_level: GovernanceLevel = GovernanceLevel.ADVISORY
    ) -> Dict[str, Any]:
        """Governance-enhanced Claude chat"""
        return await self.execute_claude_command(
            ClaudeCommand.CHAT,
            [message],
            governance_level,
            {"message_type": "chat"}
        )
    
    async def claude_edit_file(
        self,
        file_path: str,
        instructions: str,
        governance_level: GovernanceLevel = GovernanceLevel.ENFORCED
    ) -> Dict[str, Any]:
        """Governance-enhanced file editing"""
        return await self.execute_claude_command(
            ClaudeCommand.EDIT,
            [file_path, instructions],
            governance_level,
            {"operation_type": "file_edit", "target_file": file_path}
        )
    
    async def claude_write_file(
        self,
        file_path: str,
        content: str,
        governance_level: GovernanceLevel = GovernanceLevel.ENFORCED
    ) -> Dict[str, Any]:
        """Governance-enhanced file writing"""
        return await self.execute_claude_command(
            ClaudeCommand.WRITE,
            [file_path, content],
            governance_level,
            {"operation_type": "file_write", "target_file": file_path}
        )
    
    async def claude_analyze_code(
        self,
        file_path: str,
        analysis_type: str = "general",
        governance_level: GovernanceLevel = GovernanceLevel.ADVISORY
    ) -> Dict[str, Any]:
        """Governance-enhanced code analysis"""
        return await self.execute_claude_command(
            ClaudeCommand.ANALYZE,
            [file_path, f"--type={analysis_type}"],
            governance_level,
            {"operation_type": "code_analysis", "target_file": file_path}
        )
    
    async def claude_refactor_code(
        self,
        file_path: str,
        refactor_instructions: str,
        governance_level: GovernanceLevel = GovernanceLevel.STRICT
    ) -> Dict[str, Any]:
        """Governance-enhanced code refactoring"""
        return await self.execute_claude_command(
            ClaudeCommand.REFACTOR,
            [file_path, refactor_instructions],
            governance_level,
            {"operation_type": "code_refactor", "target_file": file_path}
        )
    
    async def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific operation"""
        
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            return {
                "status": "active",
                "operation": {
                    "id": operation.operation_id,
                    "command": operation.command.value,
                    "governance_level": operation.governance_level.value,
                    "created_at": operation.created_at.isoformat(),
                    "governance_approved": operation.governance_approved
                }
            }
        elif operation_id in self.completed_operations:
            operation = self.completed_operations[operation_id]
            return {
                "status": "completed",
                "operation": {
                    "id": operation.operation_id,
                    "command": operation.command.value,
                    "governance_level": operation.governance_level.value,
                    "created_at": operation.created_at.isoformat(),
                    "governance_approved": operation.governance_approved,
                    "success": operation.execution_result.get("returncode") == 0 if operation.execution_result else False
                }
            }
        
        return None
    
    async def get_governance_analytics(self) -> Dict[str, Any]:
        """Get governance analytics for Claude operations"""
        
        total_operations = len(self.completed_operations)
        
        if total_operations == 0:
            return {
                "total_operations": 0,
                "governance_levels": {},
                "success_rates": {},
                "command_distribution": {}
            }
        
        # Analyze completed operations
        governance_levels = {}
        success_rates = {}
        command_distribution = {}
        
        for operation in self.completed_operations.values():
            # Governance levels
            level = operation.governance_level.value
            governance_levels[level] = governance_levels.get(level, 0) + 1
            
            # Success rates
            success = operation.execution_result.get("returncode") == 0 if operation.execution_result else False
            success_rates[level] = success_rates.get(level, {"success": 0, "total": 0})
            success_rates[level]["total"] += 1
            if success:
                success_rates[level]["success"] += 1
            
            # Command distribution
            cmd = operation.command.value
            command_distribution[cmd] = command_distribution.get(cmd, 0) + 1
        
        # Calculate success percentages
        for level in success_rates:
            if success_rates[level]["total"] > 0:
                success_rates[level]["percentage"] = (
                    success_rates[level]["success"] / success_rates[level]["total"]
                ) * 100
        
        return {
            "total_operations": total_operations,
            "governance_levels": governance_levels,
            "success_rates": success_rates,
            "command_distribution": command_distribution,
            "analytics_timestamp": datetime.now().isoformat()
        }


async def main():
    """Demonstration of Claude CLI governance integration"""
    
    print("=" * 80)
    print("CLAUDE CLI GOVERNANCE INTEGRATION v9.3 - DEMONSTRATION")
    print("=" * 80)
    
    # Initialize integration
    integration = ClaudeGovernanceIntegration()
    await integration.initialize()
    
    print("\n1. TESTING GOVERNANCE LEVELS")
    print("-" * 50)
    
    # Test different governance levels
    test_message = "Analyze the performance implications of adding caching to our database layer"
    
    # Advisory level (minimal governance)
    print("Testing ADVISORY governance level...")
    result1 = await integration.claude_chat(test_message, GovernanceLevel.ADVISORY)
    print(f"  Result: {'SUCCESS' if result1['success'] else 'FAILED'}")
    print(f"  Governance applied: {result1['governance_applied']}")
    
    # Enforced level (production governance)
    print("\nTesting ENFORCED governance level...")
    result2 = await integration.claude_chat(test_message, GovernanceLevel.ENFORCED)
    print(f"  Result: {'SUCCESS' if result2['success'] else 'FAILED'}")
    print(f"  Governance applied: {result2['governance_applied']}")
    
    print("\n2. TESTING FILE OPERATIONS WITH GOVERNANCE")
    print("-" * 50)
    
    # Test file editing with governance
    test_file = "test_governance.py"
    test_content = "# Test file for governance demonstration\nprint('Hello, governed world!')"
    
    print("Testing file write with ENFORCED governance...")
    write_result = await integration.claude_write_file(
        test_file,
        test_content,
        GovernanceLevel.ENFORCED
    )
    print(f"  Write result: {'SUCCESS' if write_result['success'] else 'FAILED'}")
    if not write_result['success']:
        print(f"  Governance feedback: {write_result.get('governance_feedback', 'None')}")
    
    print("\n3. TESTING CODE ANALYSIS")
    print("-" * 50)
    
    # Test code analysis
    analysis_result = await integration.claude_analyze_code(
        "unified_governance_orchestrator.py",
        "security",
        GovernanceLevel.ADVISORY
    )
    print(f"  Analysis result: {'SUCCESS' if analysis_result['success'] else 'FAILED'}")
    if analysis_result['success']:
        print(f"  Optimization applied: {analysis_result.get('optimization_applied', False)}")
    
    print("\n4. GOVERNANCE ANALYTICS")
    print("-" * 50)
    
    # Get governance analytics
    analytics = await integration.get_governance_analytics()
    print(f"Total operations processed: {analytics['total_operations']}")
    print(f"Governance level distribution: {analytics['governance_levels']}")
    print(f"Command distribution: {analytics['command_distribution']}")
    
    for level, stats in analytics['success_rates'].items():
        if stats['total'] > 0:
            print(f"  {level.upper()} success rate: {stats['percentage']:.1f}%")
    
    print("\n5. SYSTEM STATUS")
    print("-" * 50)
    
    # Check orchestration status
    orch_status = integration.orchestrator.get_orchestration_status()
    print(f"Orchestration running: {orch_status['is_running']}")
    print(f"Active agents: {orch_status['agents']['active']}")
    print(f"Completed tasks: {orch_status['tasks']['completed']}")
    
    print("\n" + "=" * 80)
    print("CLAUDE CLI GOVERNANCE INTEGRATION DEMONSTRATION COMPLETE")
    print("=" * 80)
    
    print("\nFeatures Demonstrated:")
    print("  - Multi-level governance enforcement (Advisory/Enforced/Strict)")
    print("  - Integration with existing governance orchestrator")
    print("  - Token optimization for Claude commands")
    print("  - Audit trail and analytics")
    print("  - Risk-based operation approval")
    print("  - Real-time governance decision making")
    
    print("\nNext Steps:")
    print("  - Connect to actual Claude CLI executable")
    print("  - Add custom governance rules configuration")
    print("  - Implement governance rule learning")
    print("  - Add governance dashboard UI")


if __name__ == "__main__":
    asyncio.run(main())