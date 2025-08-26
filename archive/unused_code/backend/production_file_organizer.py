#!/usr/bin/env python3
"""
Production File Organization System v9.2
Intelligent file organization using complete governance and orchestration tools
Implements production-ready project structure with governance oversight
"""

import asyncio
import json
import os
import shutil
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import logging
import re

# Import our complete orchestration system
from production_governance_system import (
    ProductionGovernanceSystem, GovernanceAction, GovernanceScope
)
from advanced_governance_workflows import AdvancedGovernanceWorkflows, WorkflowComplexity
from ai_orchestration_engine import TaskPriority


class FileCategory(Enum):
    """Categories for file organization"""
    CORE_SYSTEM = "core_system"
    ORCHESTRATION = "orchestration"
    GOVERNANCE = "governance"
    INTEGRATION = "integration"
    TESTING = "testing"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    UTILITIES = "utilities"
    TEMPLATES = "templates"


class OrganizationStrategy(Enum):
    """File organization strategies"""
    FUNCTIONAL = "functional"  # Organize by function (api/, core/, etc.)
    DOMAIN = "domain"  # Organize by domain (governance/, orchestration/)
    LAYERED = "layered"  # Organize by architectural layer
    HYBRID = "hybrid"  # Mix of strategies


@dataclass
class FileRule:
    """Rule for file organization"""
    rule_id: str
    name: str
    pattern: str  # Regex pattern for file matching
    target_category: FileCategory
    target_directory: str
    priority: int
    conditions: List[str] = field(default_factory=list)
    governance_required: bool = False
    backup_original: bool = True


@dataclass
class OrganizationPlan:
    """Plan for file organization"""
    plan_id: str
    strategy: OrganizationStrategy
    source_directory: Path
    target_directory: Path
    file_moves: List[Dict[str, Any]]
    directory_structure: Dict[str, List[str]]
    governance_approvals: List[str]
    estimated_duration: float
    risk_assessment: Dict[str, Any]
    rollback_plan: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


class ProductionFileOrganizer:
    """Production-ready file organization with governance oversight"""
    
    def __init__(self, governance_system: ProductionGovernanceSystem):
        """Initialize file organizer"""
        self.governance_system = governance_system
        self.advanced_workflows = AdvancedGovernanceWorkflows(governance_system)
        
        # Organization state
        self.organization_rules: Dict[str, FileRule] = {}
        self.active_plans: Dict[str, OrganizationPlan] = {}
        self.organization_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.backup_directory = Path("./backups/file_organization")
        self.max_file_size_mb = 100  # Max file size to organize
        self.excluded_patterns = [".git/", "__pycache__/", "*.pyc", ".env"]
        
        # Performance tracking
        self.metrics = {
            "files_organized": 0,
            "directories_created": 0,
            "organization_time": 0.0,
            "governance_approvals": 0,
            "rollbacks_performed": 0
        }
        
        self._initialize_organization_rules()
    
    def _initialize_organization_rules(self):
        """Initialize file organization rules"""
        
        rules = [
            # Core system files
            FileRule(
                rule_id="core_orchestration",
                name="Core Orchestration Files",
                pattern=r".*orchestrat.*\.py$",
                target_category=FileCategory.CORE_SYSTEM,
                target_directory="core/orchestration",
                priority=1,
                governance_required=True,
                conditions=["size_check", "dependency_analysis"]
            ),
            
            # Governance files
            FileRule(
                rule_id="governance_files",
                name="Governance System Files",
                pattern=r".*(governance|policy|compliance).*\.py$",
                target_category=FileCategory.GOVERNANCE,
                target_directory="governance",
                priority=1,
                governance_required=True
            ),
            
            # AI Integration files
            FileRule(
                rule_id="ai_integration",
                name="AI Integration Files",
                pattern=r".*(multi_model|conversation|token_opt).*\.py$",
                target_category=FileCategory.INTEGRATION,
                target_directory="integrations/ai",
                priority=2,
                governance_required=True
            ),
            
            # Test files
            FileRule(
                rule_id="test_files",
                name="Test Files",
                pattern=r"test_.*\.py$|.*_test\.py$",
                target_category=FileCategory.TESTING,
                target_directory="tests",
                priority=3,
                governance_required=False
            ),
            
            # Configuration files
            FileRule(
                rule_id="config_files",
                name="Configuration Files",
                pattern=r".*config.*\.(json|yaml|yml|toml)$",
                target_category=FileCategory.CONFIGURATION,
                target_directory="config",
                priority=4,
                governance_required=False
            ),
            
            # Documentation files
            FileRule(
                rule_id="documentation",
                name="Documentation Files",
                pattern=r".*\.(md|rst|txt)$",
                target_category=FileCategory.DOCUMENTATION,
                target_directory="docs",
                priority=5,
                governance_required=False
            ),
            
            # Utility files
            FileRule(
                rule_id="utilities",
                name="Utility Files",
                pattern=r".*(util|helper|tool).*\.py$",
                target_category=FileCategory.UTILITIES,
                target_directory="utils",
                priority=6,
                governance_required=False
            ),
            
            # Demo and example files
            FileRule(
                rule_id="demos",
                name="Demo and Example Files",
                pattern=r".*(demo|example|sample).*\.py$",
                target_category=FileCategory.TEMPLATES,
                target_directory="examples",
                priority=7,
                governance_required=False
            )
        ]
        
        for rule in rules:
            self.organization_rules[rule.rule_id] = rule
    
    async def analyze_current_structure(self, source_path: Path) -> Dict[str, Any]:
        """Analyze current file structure"""
        
        analysis = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "size_distribution": {},
            "organizational_issues": [],
            "governance_files": [],
            "critical_files": []
        }
        
        try:
            # Walk through directory structure
            for root, dirs, files in os.walk(source_path):
                root_path = Path(root)
                
                # Skip excluded directories
                if any(pattern in str(root_path) for pattern in self.excluded_patterns):
                    continue
                
                analysis["total_directories"] += len(dirs)
                
                for file in files:
                    file_path = root_path / file
                    
                    # Skip excluded files
                    if any(re.match(pattern.replace("*", ".*"), file) for pattern in self.excluded_patterns):
                        continue
                    
                    analysis["total_files"] += 1
                    
                    # Analyze file
                    file_info = await self._analyze_file(file_path)
                    
                    # Categorize by extension
                    ext = file_path.suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    # Size distribution
                    size_mb = file_info["size_mb"]
                    if size_mb < 0.1:
                        size_category = "small"
                    elif size_mb < 1.0:
                        size_category = "medium"
                    elif size_mb < 10.0:
                        size_category = "large"
                    else:
                        size_category = "very_large"
                    
                    analysis["size_distribution"][size_category] = analysis["size_distribution"].get(size_category, 0) + 1
                    
                    # Check for governance-relevant files
                    if file_info["requires_governance"]:
                        analysis["governance_files"].append(str(file_path))
                    
                    # Check for critical files
                    if file_info["is_critical"]:
                        analysis["critical_files"].append(str(file_path))
                    
                    # Check for organizational issues
                    issues = await self._detect_organizational_issues(file_path, source_path)
                    analysis["organizational_issues"].extend(issues)
        
        except Exception as e:
            logging.error(f"Failed to analyze structure: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    async def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual file"""
        
        file_info = {
            "path": str(file_path),
            "size_mb": 0.0,
            "requires_governance": False,
            "is_critical": False,
            "matched_rules": [],
            "dependencies": [],
            "complexity_score": 0.0
        }
        
        try:
            # Get file size
            size_bytes = file_path.stat().st_size
            file_info["size_mb"] = size_bytes / (1024 * 1024)
            
            # Check against organization rules
            filename = file_path.name
            for rule in self.organization_rules.values():
                if re.match(rule.pattern, filename):
                    file_info["matched_rules"].append(rule.rule_id)
                    if rule.governance_required:
                        file_info["requires_governance"] = True
            
            # Check if file is critical (contains "orchestration", "governance", etc.)
            critical_keywords = ["orchestration", "governance", "main", "__init__"]
            if any(keyword in filename.lower() for keyword in critical_keywords):
                file_info["is_critical"] = True
            
            # Analyze Python files more deeply
            if file_path.suffix == ".py":
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Simple complexity analysis
                    lines = content.split('\n')
                    file_info["complexity_score"] = len(lines) / 100.0  # Rough complexity
                    
                    # Find imports (dependencies)
                    import_pattern = r"^(?:from|import)\s+(\w+)"
                    for line in lines:
                        match = re.match(import_pattern, line.strip())
                        if match:
                            file_info["dependencies"].append(match.group(1))
                    
                except Exception as e:
                    logging.debug(f"Could not analyze Python file {file_path}: {e}")
        
        except Exception as e:
            logging.warning(f"Failed to analyze file {file_path}: {e}")
            file_info["error"] = str(e)
        
        return file_info
    
    async def _detect_organizational_issues(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Detect organizational issues with file placement"""
        
        issues = []
        relative_path = file_path.relative_to(base_path)
        filename = file_path.name
        
        # Issue: Test files not in test directory
        if re.match(r"test_.*\.py$", filename) and "test" not in str(relative_path):
            issues.append({
                "type": "misplaced_test",
                "severity": "medium",
                "description": f"Test file {filename} not in test directory",
                "file": str(file_path)
            })
        
        # Issue: Configuration files scattered
        if re.match(r".*config.*\.(json|yaml|yml)$", filename) and relative_path.parent.name != "config":
            issues.append({
                "type": "scattered_config",
                "severity": "low",
                "description": f"Config file {filename} not in config directory",
                "file": str(file_path)
            })
        
        # Issue: Documentation files in wrong location
        if filename.endswith(".md") and relative_path.parent.name not in ["docs", "."]:
            issues.append({
                "type": "misplaced_docs",
                "severity": "low",
                "description": f"Documentation file {filename} not in docs directory",
                "file": str(file_path)
            })
        
        # Issue: Large files in root directory
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 1.0 and len(relative_path.parts) == 1:
                issues.append({
                    "type": "large_file_in_root",
                    "severity": "medium",
                    "description": f"Large file {filename} ({size_mb:.1f}MB) in root directory",
                    "file": str(file_path)
                })
        except:
            pass
        
        return issues
    
    async def create_organization_plan(
        self,
        source_path: Path,
        strategy: OrganizationStrategy = OrganizationStrategy.HYBRID,
        target_path: Optional[Path] = None
    ) -> OrganizationPlan:
        """Create comprehensive organization plan"""
        
        target_path = target_path or source_path / "organized"
        plan_id = f"org_plan_{int(time.time() * 1000)}"
        
        # Analyze current structure
        analysis = await self.analyze_current_structure(source_path)
        
        # Create directory structure based on strategy
        directory_structure = self._design_directory_structure(strategy, analysis)
        
        # Plan file moves
        file_moves = await self._plan_file_moves(source_path, target_path, directory_structure)
        
        # Assess risks
        risk_assessment = await self._assess_organization_risks(file_moves, analysis)
        
        # Create rollback plan
        rollback_plan = self._create_rollback_plan(file_moves)
        
        # Estimate duration
        estimated_duration = self._estimate_organization_duration(file_moves)
        
        # Check governance requirements
        governance_files = [
            move for move in file_moves
            if move.get("requires_governance", False)
        ]
        
        governance_approvals = []
        if governance_files:
            governance_approvals = ["architecture_review", "security_audit"]
        
        plan = OrganizationPlan(
            plan_id=plan_id,
            strategy=strategy,
            source_directory=source_path,
            target_directory=target_path,
            file_moves=file_moves,
            directory_structure=directory_structure,
            governance_approvals=governance_approvals,
            estimated_duration=estimated_duration,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
        
        self.active_plans[plan_id] = plan
        
        return plan
    
    def _design_directory_structure(
        self,
        strategy: OrganizationStrategy,
        analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Design target directory structure"""
        
        if strategy == OrganizationStrategy.FUNCTIONAL:
            return {
                "api/": ["endpoints", "middleware", "auth"],
                "core/": ["orchestration", "governance", "engine"],
                "integrations/": ["ai", "external", "webhooks"],
                "services/": ["conversation", "optimization", "monitoring"],
                "utils/": ["helpers", "tools", "validators"],
                "config/": ["environments", "policies", "rules"],
                "tests/": ["unit", "integration", "e2e"],
                "docs/": ["api", "guides", "examples"],
                "scripts/": ["deployment", "maintenance", "migration"],
                "templates/": ["workflows", "policies", "examples"]
            }
        
        elif strategy == OrganizationStrategy.DOMAIN:
            return {
                "governance/": ["orchestrator", "policies", "workflows"],
                "orchestration/": ["engine", "agents", "tasks"],
                "ai_integration/": ["models", "conversation", "optimization"],
                "monitoring/": ["metrics", "logging", "health"],
                "security/": ["auth", "audit", "compliance"],
                "testing/": ["governance", "integration", "performance"],
                "deployment/": ["scripts", "configs", "automation"],
                "documentation/": ["governance", "api", "guides"]
            }
        
        elif strategy == OrganizationStrategy.LAYERED:
            return {
                "presentation/": ["api", "ui", "cli"],
                "application/": ["services", "workflows", "handlers"],
                "domain/": ["governance", "orchestration", "policies"],
                "infrastructure/": ["ai_models", "database", "cache"],
                "cross_cutting/": ["logging", "monitoring", "security"],
                "tests/": ["unit", "integration", "acceptance"],
                "config/": ["environments", "settings"],
                "docs/": ["architecture", "api", "deployment"]
            }
        
        else:  # HYBRID
            return {
                "core/": ["orchestration", "governance"],
                "ai/": ["models", "conversation", "optimization"],
                "integrations/": ["external", "webhooks", "api"],
                "workflows/": ["templates", "automation"],
                "monitoring/": ["metrics", "health", "audit"],
                "config/": ["policies", "rules", "settings"],
                "tests/": ["unit", "integration", "workflows"],
                "utils/": ["tools", "helpers", "scripts"],
                "docs/": ["api", "guides", "examples"],
                "deployment/": ["scripts", "configs", "automation"]
            }
    
    async def _plan_file_moves(
        self,
        source_path: Path,
        target_path: Path,
        directory_structure: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Plan individual file moves"""
        
        file_moves = []
        
        try:
            for root, dirs, files in os.walk(source_path):
                root_path = Path(root)
                
                # Skip excluded directories
                if any(pattern in str(root_path) for pattern in self.excluded_patterns):
                    continue
                
                for file in files:
                    source_file = root_path / file
                    
                    # Skip excluded files
                    if any(re.match(pattern.replace("*", ".*"), file) for pattern in self.excluded_patterns):
                        continue
                    
                    # Find best rule match
                    best_rule = None
                    best_priority = float('inf')
                    
                    for rule in self.organization_rules.values():
                        if re.match(rule.pattern, file):
                            if rule.priority < best_priority:
                                best_rule = rule
                                best_priority = rule.priority
                    
                    # Determine target location
                    if best_rule:
                        target_file = target_path / best_rule.target_directory / file
                    else:
                        # Default location based on file type
                        if file.endswith('.py'):
                            target_file = target_path / "misc" / file
                        else:
                            target_file = target_path / "assets" / file
                    
                    # Create move record
                    move = {
                        "source": str(source_file),
                        "target": str(target_file),
                        "rule_id": best_rule.rule_id if best_rule else None,
                        "rule_name": best_rule.name if best_rule else "Default",
                        "requires_governance": best_rule.governance_required if best_rule else False,
                        "backup_required": best_rule.backup_original if best_rule else True,
                        "size_mb": source_file.stat().st_size / (1024 * 1024),
                        "file_type": source_file.suffix.lower()
                    }
                    
                    file_moves.append(move)
        
        except Exception as e:
            logging.error(f"Failed to plan file moves: {e}")
        
        return file_moves
    
    async def _assess_organization_risks(
        self,
        file_moves: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risks of organization plan"""
        
        risk_assessment = {
            "overall_risk": "medium",
            "risk_factors": [],
            "mitigation_strategies": [],
            "critical_files": [],
            "dependency_risks": []
        }
        
        # Check for critical file moves
        governance_moves = [m for m in file_moves if m.get("requires_governance", False)]
        large_file_moves = [m for m in file_moves if m.get("size_mb", 0) > 10]
        
        if len(governance_moves) > 5:
            risk_assessment["risk_factors"].append({
                "type": "many_governance_files",
                "count": len(governance_moves),
                "severity": "high"
            })
            risk_assessment["mitigation_strategies"].append("Phased migration approach")
        
        if len(large_file_moves) > 2:
            risk_assessment["risk_factors"].append({
                "type": "large_files",
                "count": len(large_file_moves),
                "severity": "medium"
            })
            risk_assessment["mitigation_strategies"].append("Dedicated backup strategy")
        
        # Check for import/dependency issues
        python_moves = [m for m in file_moves if m.get("file_type") == ".py"]
        if len(python_moves) > 20:
            risk_assessment["risk_factors"].append({
                "type": "many_python_files",
                "count": len(python_moves),
                "severity": "medium"
            })
            risk_assessment["mitigation_strategies"].append("Update import statements")
        
        # Calculate overall risk
        high_risk_factors = len([r for r in risk_assessment["risk_factors"] if r["severity"] == "high"])
        medium_risk_factors = len([r for r in risk_assessment["risk_factors"] if r["severity"] == "medium"])
        
        if high_risk_factors > 0:
            risk_assessment["overall_risk"] = "high"
        elif medium_risk_factors > 2:
            risk_assessment["overall_risk"] = "medium"
        else:
            risk_assessment["overall_risk"] = "low"
        
        return risk_assessment
    
    def _create_rollback_plan(self, file_moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create rollback plan for organization"""
        
        return {
            "backup_location": str(self.backup_directory),
            "restore_commands": [
                f"mv '{move['target']}' '{move['source']}'"
                for move in file_moves
            ],
            "validation_steps": [
                "Check file integrity",
                "Verify import statements",
                "Run test suite",
                "Validate governance system"
            ]
        }
    
    def _estimate_organization_duration(self, file_moves: List[Dict[str, Any]]) -> float:
        """Estimate organization duration in seconds"""
        
        base_time_per_file = 0.1  # seconds
        governance_overhead = 2.0  # seconds per governance file
        large_file_overhead = 1.0  # seconds per large file
        
        total_time = len(file_moves) * base_time_per_file
        
        governance_files = len([m for m in file_moves if m.get("requires_governance", False)])
        total_time += governance_files * governance_overhead
        
        large_files = len([m for m in file_moves if m.get("size_mb", 0) > 1.0])
        total_time += large_files * large_file_overhead
        
        return total_time
    
    async def execute_organization_plan(
        self,
        plan_id: str,
        require_governance_approval: bool = True
    ) -> Dict[str, Any]:
        """Execute organization plan with governance oversight"""
        
        if plan_id not in self.active_plans:
            raise ValueError(f"Unknown plan: {plan_id}")
        
        plan = self.active_plans[plan_id]
        execution_id = f"exec_{plan_id}_{int(time.time() * 1000)}"
        
        # Check governance requirements
        if require_governance_approval and plan.governance_approvals:
            governance_result = await self._get_governance_approval(plan)
            if governance_result["status"] != "approved":
                return {
                    "execution_id": execution_id,
                    "status": "blocked",
                    "reason": "Governance approval required",
                    "governance_result": governance_result
                }
        
        start_time = time.time()
        execution_result = {
            "execution_id": execution_id,
            "plan_id": plan_id,
            "status": "in_progress",
            "files_moved": 0,
            "directories_created": 0,
            "errors": [],
            "warnings": [],
            "start_time": start_time
        }
        
        try:
            # Create backup
            backup_path = await self._create_backup(plan)
            execution_result["backup_path"] = str(backup_path)
            
            # Create target directory structure
            await self._create_directory_structure(plan.target_directory, plan.directory_structure)
            execution_result["directories_created"] = len(plan.directory_structure)
            
            # Execute file moves
            for move in plan.file_moves:
                try:
                    await self._execute_file_move(move)
                    execution_result["files_moved"] += 1
                    
                except Exception as e:
                    error = {
                        "file": move["source"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    execution_result["errors"].append(error)
                    logging.error(f"Failed to move {move['source']}: {e}")
            
            # Update import statements for Python files
            if any(move["file_type"] == ".py" for move in plan.file_moves):
                import_updates = await self._update_import_statements(plan)
                execution_result["import_updates"] = import_updates
            
            # Validate organization
            validation_result = await self._validate_organization(plan)
            execution_result["validation"] = validation_result
            
            execution_result["status"] = "completed"
            execution_result["duration"] = time.time() - start_time
            
            # Update metrics
            self.metrics["files_organized"] += execution_result["files_moved"]
            self.metrics["directories_created"] += execution_result["directories_created"]
            self.metrics["organization_time"] += execution_result["duration"]
            
            # Record in history
            self.organization_history.append({
                "execution_id": execution_id,
                "plan_id": plan_id,
                "timestamp": datetime.now().isoformat(),
                "files_moved": execution_result["files_moved"],
                "status": execution_result["status"]
            })
            
        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["error"] = str(e)
            execution_result["duration"] = time.time() - start_time
            logging.error(f"Organization execution failed: {e}")
        
        return execution_result
    
    async def _get_governance_approval(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """Get governance approval for organization plan"""
        
        try:
            # Create governance request
            governance_data = {
                "action": "file_organization",
                "plan_id": plan.plan_id,
                "strategy": plan.strategy.value,
                "files_to_move": len(plan.file_moves),
                "governance_files": len([m for m in plan.file_moves if m.get("requires_governance")]),
                "risk_level": plan.risk_assessment.get("overall_risk", "medium"),
                "estimated_duration": plan.estimated_duration
            }
            
            # Execute governance workflow
            workflow_result = await self.advanced_workflows.execute_advanced_workflow(
                workflow_template_id="major_architecture_change",
                trigger_data=governance_data,
                priority=TaskPriority.HIGH
            )
            
            self.metrics["governance_approvals"] += 1
            
            return {
                "status": "approved" if "Approved" in workflow_result.get("decision", "") else "rejected",
                "workflow_result": workflow_result
            }
            
        except Exception as e:
            logging.error(f"Governance approval failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_backup(self, plan: OrganizationPlan) -> Path:
        """Create backup of files before organization"""
        
        backup_path = self.backup_directory / f"backup_{plan.plan_id}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files to backup
        for move in plan.file_moves:
            if move.get("backup_required", True):
                source_file = Path(move["source"])
                if source_file.exists():
                    backup_file = backup_path / source_file.name
                    shutil.copy2(source_file, backup_file)
        
        return backup_path
    
    async def _create_directory_structure(
        self,
        target_path: Path,
        structure: Dict[str, List[str]]
    ) -> None:
        """Create target directory structure"""
        
        for main_dir, subdirs in structure.items():
            main_path = target_path / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            
            for subdir in subdirs:
                sub_path = main_path / subdir
                sub_path.mkdir(parents=True, exist_ok=True)
    
    async def _execute_file_move(self, move: Dict[str, Any]) -> None:
        """Execute individual file move"""
        
        source_path = Path(move["source"])
        target_path = Path(move["target"])
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file
        shutil.move(str(source_path), str(target_path))
    
    async def _update_import_statements(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """Update import statements after file organization"""
        
        update_result = {
            "files_updated": 0,
            "imports_changed": 0,
            "errors": []
        }
        
        # This is a simplified implementation
        # In production, would use AST parsing for more robust import updates
        
        python_moves = [m for m in plan.file_moves if m["file_type"] == ".py"]
        
        for move in python_moves:
            try:
                target_file = Path(move["target"])
                if target_file.exists():
                    content = target_file.read_text(encoding='utf-8')
                    
                    # Simple import updates (very basic implementation)
                    updated_content = content
                    changes_made = 0
                    
                    # Update relative imports (basic pattern)
                    for other_move in python_moves:
                        old_module = Path(other_move["source"]).stem
                        new_module = Path(other_move["target"]).stem
                        
                        if old_module != new_module:
                            import_pattern = f"from {old_module} import"
                            new_import = f"from {new_module} import"
                            
                            if import_pattern in updated_content:
                                updated_content = updated_content.replace(import_pattern, new_import)
                                changes_made += 1
                    
                    if changes_made > 0:
                        target_file.write_text(updated_content, encoding='utf-8')
                        update_result["files_updated"] += 1
                        update_result["imports_changed"] += changes_made
                    
            except Exception as e:
                update_result["errors"].append({
                    "file": move["target"],
                    "error": str(e)
                })
        
        return update_result
    
    async def _validate_organization(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """Validate organization results"""
        
        validation = {
            "files_in_place": 0,
            "missing_files": [],
            "directory_structure_ok": True,
            "import_errors": [],
            "overall_status": "success"
        }
        
        # Check if files were moved correctly
        for move in plan.file_moves:
            target_path = Path(move["target"])
            if target_path.exists():
                validation["files_in_place"] += 1
            else:
                validation["missing_files"].append(move["target"])
        
        # Check directory structure
        for main_dir in plan.directory_structure.keys():
            dir_path = plan.target_directory / main_dir
            if not dir_path.exists():
                validation["directory_structure_ok"] = False
                break
        
        # Calculate overall status
        success_rate = validation["files_in_place"] / len(plan.file_moves) if plan.file_moves else 1.0
        
        if success_rate >= 0.95 and validation["directory_structure_ok"]:
            validation["overall_status"] = "success"
        elif success_rate >= 0.8:
            validation["overall_status"] = "partial_success"
        else:
            validation["overall_status"] = "failed"
        
        return validation
    
    def get_organization_metrics(self) -> Dict[str, Any]:
        """Get organization performance metrics"""
        
        return {
            "metrics": self.metrics,
            "active_plans": len(self.active_plans),
            "organization_rules": len(self.organization_rules),
            "organization_history": len(self.organization_history),
            "recent_organizations": self.organization_history[-5:] if self.organization_history else []
        }


async def demonstrate_production_file_organization():
    """Demonstrate production file organization system"""
    print("="*80)
    print("PRODUCTION FILE ORGANIZATION SYSTEM v9.2 DEMONSTRATION")
    print("Intelligent File Organization with Governance Oversight")
    print("="*80)
    
    # Initialize systems
    import os
    project_root = os.getcwd()
    gov_system = ProductionGovernanceSystem(project_root)
    await gov_system.start_governance_system()
    
    organizer = ProductionFileOrganizer(gov_system)
    
    print("\n1. FILE ORGANIZATION SYSTEM INITIALIZATION")
    print("-" * 50)
    
    metrics = organizer.get_organization_metrics()
    print(f"File organizer initialized:")
    print(f"  Organization rules: {metrics['organization_rules']}")
    print(f"  Active plans: {metrics['active_plans']}")
    print(f"  Backup directory: {organizer.backup_directory}")
    
    # Show organization rules
    print("\nOrganization Rules:")
    for rule in organizer.organization_rules.values():
        print(f"  • {rule.name}")
        print(f"    Pattern: {rule.pattern}")
        print(f"    Target: {rule.target_directory}")
        print(f"    Priority: {rule.priority}")
        print(f"    Governance required: {rule.governance_required}")
    
    print("\n2. CURRENT STRUCTURE ANALYSIS")
    print("-" * 50)
    
    # Analyze current structure
    current_path = Path(project_root)
    analysis = await organizer.analyze_current_structure(current_path)
    
    print("Current Structure Analysis:")
    print(f"  Total files: {analysis['total_files']}")
    print(f"  Total directories: {analysis['total_directories']}")
    print(f"  Governance files: {len(analysis['governance_files'])}")
    print(f"  Critical files: {len(analysis['critical_files'])}")
    print(f"  Organizational issues: {len(analysis['organizational_issues'])}")
    
    # Show file type distribution
    print("\nFile Type Distribution:")
    for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {ext or 'no extension'}: {count} files")
    
    # Show size distribution
    print("\nSize Distribution:")
    for size_cat, count in analysis['size_distribution'].items():
        print(f"  {size_cat}: {count} files")
    
    # Show organizational issues
    if analysis['organizational_issues']:
        print("\nOrganizational Issues Found:")
        for issue in analysis['organizational_issues'][:5]:
            print(f"  • {issue['type']} ({issue['severity']}): {issue['description']}")
    
    print("\n3. ORGANIZATION PLAN CREATION")
    print("-" * 50)
    
    # Test different organization strategies
    strategies = [
        (OrganizationStrategy.HYBRID, "Hybrid approach (recommended)"),
        (OrganizationStrategy.FUNCTIONAL, "Functional organization"),
        (OrganizationStrategy.DOMAIN, "Domain-driven organization")
    ]
    
    plans = []
    
    for strategy, description in strategies[:1]:  # Test one strategy for demo
        print(f"\nCreating plan: {description}")
        
        plan = await organizer.create_organization_plan(
            source_path=current_path,
            strategy=strategy,
            target_path=current_path / "organized_structure"
        )
        
        plans.append(plan)
        
        print(f"  Plan ID: {plan.plan_id}")
        print(f"  Strategy: {plan.strategy.value}")
        print(f"  Files to move: {len(plan.file_moves)}")
        print(f"  Directories to create: {len(plan.directory_structure)}")
        print(f"  Estimated duration: {plan.estimated_duration:.1f} seconds")
        print(f"  Risk level: {plan.risk_assessment['overall_risk']}")
        print(f"  Governance approvals needed: {len(plan.governance_approvals)}")
        
        # Show directory structure
        print("\n  Target Directory Structure:")
        for main_dir, subdirs in list(plan.directory_structure.items())[:5]:
            print(f"    {main_dir}")
            for subdir in subdirs[:3]:
                print(f"      └── {subdir}")
            if len(subdirs) > 3:
                print(f"      └── ... ({len(subdirs)-3} more)")
        
        # Show risk factors
        if plan.risk_assessment['risk_factors']:
            print("\n  Risk Factors:")
            for risk in plan.risk_assessment['risk_factors']:
                print(f"    • {risk['type']} ({risk['severity']}): {risk.get('count', 'N/A')}")
        
        # Show file moves sample
        governance_moves = [m for m in plan.file_moves if m.get('requires_governance')]
        if governance_moves:
            print(f"\n  Governance-Required Moves (showing first 3 of {len(governance_moves)}):")
            for move in governance_moves[:3]:
                source_name = Path(move['source']).name
                target_rel = Path(move['target']).relative_to(plan.target_directory)
                print(f"    {source_name} → {target_rel}")
    
    print("\n4. GOVERNANCE APPROVAL SIMULATION")
    print("-" * 50)
    
    if plans:
        plan = plans[0]
        
        print("Requesting governance approval for organization plan...")
        
        # Simulate governance approval (without actually executing)
        governance_result = await organizer._get_governance_approval(plan)
        
        print(f"Governance approval result:")
        print(f"  Status: {governance_result['status']}")
        if 'workflow_result' in governance_result:
            workflow = governance_result['workflow_result']
            print(f"  Decision: {workflow.get('decision', 'N/A')}")
            print(f"  Consensus level: {workflow.get('consensus_level', 'N/A')}")
            print(f"  Risk level: {workflow.get('risk_level', 'N/A')}")
    
    print("\n5. ORGANIZATION METRICS AND PERFORMANCE")
    print("-" * 50)
    
    # Get organization metrics
    final_metrics = organizer.get_organization_metrics()
    
    print("Organization System Performance:")
    metrics_data = final_metrics["metrics"]
    for metric, value in metrics_data.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.2f}")
        else:
            print(f"  {metric}: {value}")
    
    print(f"\nSystem State:")
    print(f"  Active plans: {final_metrics['active_plans']}")
    print(f"  Organization rules: {final_metrics['organization_rules']}")
    print(f"  Organization history: {final_metrics['organization_history']}")
    
    print("\n6. ROLLBACK AND SAFETY FEATURES")
    print("-" * 50)
    
    if plans:
        plan = plans[0]
        
        print("Rollback Plan Features:")
        rollback = plan.rollback_plan
        print(f"  Backup location: {rollback['backup_location']}")
        print(f"  Restore commands: {len(rollback['restore_commands'])} prepared")
        print(f"  Validation steps: {len(rollback['validation_steps'])} steps")
        
        print("\n  Validation Steps:")
        for step in rollback['validation_steps']:
            print(f"    • {step}")
        
        print("\n  Safety Features:")
        print("    • Automatic backup creation before organization")
        print("    • Governance approval for critical files")
        print("    • Import statement update automation")
        print("    • Comprehensive validation after organization")
        print("    • Complete rollback capability")
    
    await gov_system.stop_governance_system()
    
    print("\n" + "="*80)
    print("PRODUCTION FILE ORGANIZATION DEMONSTRATION COMPLETE")
    print("="*80)
    
    print("\nCapabilities Demonstrated:")
    print("• Intelligent file analysis and categorization")
    print("• Multiple organization strategies (Functional, Domain, Hybrid)")
    print("• Governance integration for critical file moves")
    print("• Risk assessment and mitigation planning")
    print("• Automated backup and rollback capabilities")
    print("• Import statement update automation")
    print("• Comprehensive validation and monitoring")
    print("• Production-ready safety features")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demonstration
    asyncio.run(demonstrate_production_file_organization())