#!/usr/bin/env python
"""
Data-Driven Governance Orchestrator v5.0
Flexible, configurable, UI-friendly governance system
Portable and easy to integrate into any project
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import copy
import re

class ExecutionMode(Enum):
    """Execution modes for agent/persona combinations"""
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT_SINGLE_PERSONA = "multi_agent_single_persona"
    MULTI_AGENT_MULTI_PERSONA = "multi_agent_multi_persona"
    FULL_ORCHESTRATION = "full_orchestration"

@dataclass
class Agent:
    """Agent configuration"""
    id: str
    name: str
    enabled: bool
    personas: List[str] = field(default_factory=list)
    execution_order: int = 0
    can_parallelize: bool = True
    intercepts: bool = False
    runs_after: List[str] = field(default_factory=list)
    mandatory: bool = False

@dataclass
class Persona:
    """Persona configuration"""
    id: str
    name: str
    role: str
    enabled: bool
    weight: float = 1.0
    keywords: List[str] = field(default_factory=list)
    validations: Dict[str, bool] = field(default_factory=dict)
    rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationRule:
    """Validation rule configuration"""
    name: str
    enabled: bool
    severity: str
    patterns: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    auto_fix: bool = False

@dataclass
class GovernanceResult:
    """Result of governance execution"""
    success: bool
    mode: str
    agents_executed: List[str]
    personas_executed: List[str]
    violations: List[Dict[str, Any]]
    audit_results: Dict[str, Any]
    prompt_transformations: Dict[str, str]
    execution_time_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class PromptInterceptor:
    """Intercepts and rewrites prompts using best practices"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.rules = config.get('rewriting_rules', {})
        self.distribution = config.get('distribution', {})
        self.transformations = []
    
    async def intercept_and_rewrite(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Intercept prompt and rewrite using best practices"""
        if not self.enabled:
            return {'original': prompt, 'rewritten': prompt, 'transformations': []}
        
        original = prompt
        rewritten = prompt
        transformations = []
        
        # Enhance clarity
        if self.rules.get('enhance_clarity', {}).get('enabled'):
            rewritten, clarity_transforms = self._enhance_clarity(rewritten)
            transformations.extend(clarity_transforms)
        
        # Add context
        if self.rules.get('add_context', {}).get('enabled'):
            rewritten, context_transforms = self._add_context(rewritten, context)
            transformations.extend(context_transforms)
        
        # Apply technical precision
        if self.rules.get('technical_precision', {}).get('enabled'):
            rewritten, precision_transforms = self._apply_precision(rewritten)
            transformations.extend(precision_transforms)
        
        # Apply best practice templates
        if self.rules.get('best_practices', {}).get('enabled'):
            rewritten, bp_transforms = self._apply_best_practices(rewritten)
            transformations.extend(bp_transforms)
        
        return {
            'original': original,
            'rewritten': rewritten,
            'transformations': transformations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _enhance_clarity(self, prompt: str) -> Tuple[str, List[str]]:
        """Enhance prompt clarity"""
        transformations = []
        patterns = self.rules['enhance_clarity'].get('patterns', {})
        
        for vague_term in patterns.get('vague_terms', []):
            if vague_term in prompt.lower():
                replacement = patterns['replacements'].get(vague_term, vague_term)
                prompt = re.sub(rf'\b{vague_term}\b', replacement, prompt, flags=re.IGNORECASE)
                transformations.append(f"Replaced '{vague_term}' with '{replacement}'")
        
        return prompt, transformations
    
    def _add_context(self, prompt: str, context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Add relevant context to prompt"""
        transformations = []
        auto_add = self.rules['add_context'].get('auto_add', [])
        
        context_additions = []
        if 'project_context' in auto_add and context:
            if 'project' in context:
                context_additions.append(f"Project: {context['project']}")
        
        if 'current_file' in auto_add and context:
            if 'file' in context:
                context_additions.append(f"Current file: {context['file']}")
        
        if 'recent_changes' in auto_add and context:
            if 'changes' in context:
                context_additions.append(f"Recent changes: {context['changes']}")
        
        if context_additions:
            context_str = "\n".join(context_additions)
            prompt = f"Context:\n{context_str}\n\n{prompt}"
            transformations.append(f"Added {len(context_additions)} context items")
        
        return prompt, transformations
    
    def _apply_precision(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply technical precision to prompt"""
        transformations = []
        
        # Add specificity markers
        if "fix" in prompt.lower() and "bug" not in prompt.lower():
            prompt = prompt.replace("fix", "identify and fix the specific bug where")
            transformations.append("Added specificity to 'fix' request")
        
        if "improve" in prompt.lower() and "performance" not in prompt.lower():
            prompt = prompt.replace("improve", "improve the performance/quality of")
            transformations.append("Clarified 'improve' request")
        
        return prompt, transformations
    
    def _apply_best_practices(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply best practice templates"""
        transformations = []
        templates = self.rules['best_practices'].get('templates', {})
        
        # Detect intent and apply template
        prompt_lower = prompt.lower()
        if "review" in prompt_lower and "code" in prompt_lower:
            if not any(quality in prompt_lower for quality in ['quality', 'performance', 'security']):
                prompt = f"Review the following code for quality, performance, and security:\n{prompt}"
                transformations.append("Applied code review best practice template")
        
        return prompt, transformations

class DataDrivenGovernanceOrchestrator:
    """Main orchestrator for data-driven governance"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        self.config_path = config_path or Path(__file__).parent / "governance_config.json"
        self.config = self._load_config()
        self.config_history = []
        self.agents = self._parse_agents()
        self.personas = self._parse_personas()
        self.validation_rules = self._parse_validation_rules()
        self.prompt_interceptor = PromptInterceptor(self.config.get('prompt_interception', {}))
        self.audit_results = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if isinstance(self.config_path, str):
            self.config_path = Path(self.config_path)
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": "5.0",
            "defaults": {
                "governance_level": "balanced",
                "enable_prompt_interceptor": True,
                "enable_business_auditor": True
            },
            "agents": {},
            "personas": {},
            "validation_rules": {},
            "execution_modes": {}
        }
    
    def _parse_agents(self) -> Dict[str, Agent]:
        """Parse agents from configuration"""
        agents = {}
        for agent_id, agent_config in self.config.get('agents', {}).items():
            if isinstance(agent_config, dict):
                agents[agent_id] = Agent(
                    id=agent_config.get('id', agent_id),
                    name=agent_config.get('name', agent_id),
                    enabled=agent_config.get('enabled', True),
                    personas=agent_config.get('personas_enabled', []),
                    execution_order=agent_config.get('execution_order', 0),
                    can_parallelize=agent_config.get('can_parallelize', True),
                    intercepts=agent_config.get('intercepts', False),
                    runs_after=agent_config.get('runs_after', []),
                    mandatory=agent_config.get('mandatory', False)
                )
        return agents
    
    def _parse_personas(self) -> Dict[str, Persona]:
        """Parse personas from configuration"""
        personas = {}
        for persona_id, persona_config in self.config.get('personas', {}).items():
            personas[persona_id] = Persona(
                id=persona_config.get('id', persona_id),
                name=persona_config.get('name', persona_id),
                role=persona_config.get('role', ''),
                enabled=persona_config.get('enabled', True),
                weight=persona_config.get('weight', 1.0),
                keywords=persona_config.get('keywords', []),
                validations=persona_config.get('validations', {}),
                rules=persona_config.get('rules', {})
            )
        return personas
    
    def _parse_validation_rules(self) -> Dict[str, ValidationRule]:
        """Parse validation rules from configuration"""
        rules = {}
        for rule_name, rule_config in self.config.get('validation_rules', {}).get('global', {}).items():
            rules[rule_name] = ValidationRule(
                name=rule_name,
                enabled=rule_config.get('enabled', True),
                severity=rule_config.get('severity', 'warning'),
                patterns=rule_config.get('patterns', []),
                exceptions=rule_config.get('exceptions', []),
                auto_fix=rule_config.get('auto_fix', False)
            )
        return rules
    
    async def execute(self, prompt: str, mode: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> GovernanceResult:
        """Execute governance with specified mode"""
        start_time = datetime.now()
        
        # Determine execution mode
        if not mode:
            mode = self._determine_execution_mode(prompt, context)
        
        # Intercept and rewrite prompt if enabled
        prompt_result = None
        if self.config['defaults'].get('enable_prompt_interceptor', True):
            prompt_result = await self.prompt_interceptor.intercept_and_rewrite(prompt, context)
            prompt = prompt_result['rewritten']
        
        # Execute based on mode
        if mode == ExecutionMode.SINGLE_AGENT.value:
            result = await self._execute_single_agent(prompt, context)
        elif mode == ExecutionMode.MULTI_AGENT_SINGLE_PERSONA.value:
            result = await self._execute_multi_agent_single_persona(prompt, context)
        elif mode == ExecutionMode.MULTI_AGENT_MULTI_PERSONA.value:
            result = await self._execute_multi_agent_multi_persona(prompt, context)
        else:  # FULL_ORCHESTRATION
            result = await self._execute_full_orchestration(prompt, context)
        
        # Run business auditor if enabled
        if self.config['defaults'].get('enable_business_auditor', True):
            audit_result = await self._run_business_auditor(result, prompt, context)
            result.audit_results = audit_result
        
        # Add prompt transformation info
        if prompt_result:
            result.prompt_transformations = prompt_result
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        result.execution_time_ms = execution_time
        
        return result
    
    def _determine_execution_mode(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Determine best execution mode based on prompt and context"""
        # Analyze prompt complexity
        complexity_indicators = ['multiple', 'all', 'comprehensive', 'full', 'complete']
        is_complex = any(indicator in prompt.lower() for indicator in complexity_indicators)
        
        # Check for specific persona keywords
        matching_personas = self._match_personas_to_prompt(prompt)
        
        if is_complex or len(matching_personas) > 2:
            return ExecutionMode.FULL_ORCHESTRATION.value
        elif len(matching_personas) > 1:
            return ExecutionMode.MULTI_AGENT_MULTI_PERSONA.value
        elif context and context.get('require_audit'):
            return ExecutionMode.MULTI_AGENT_SINGLE_PERSONA.value
        else:
            return ExecutionMode.SINGLE_AGENT.value
    
    def _match_personas_to_prompt(self, prompt: str) -> List[str]:
        """Match personas based on keywords in prompt"""
        matching = []
        prompt_lower = prompt.lower()
        
        for persona_id, persona in self.personas.items():
            if persona.enabled:
                for keyword in persona.keywords:
                    if keyword.lower() in prompt_lower:
                        matching.append(persona_id)
                        break
        
        return matching
    
    async def _execute_single_agent(self, prompt: str, context: Optional[Dict[str, Any]]) -> GovernanceResult:
        """Execute with single agent"""
        mode_config = self.config['execution_modes'].get('single_agent', {})
        agent_id = mode_config.get('agent', 'primary')
        persona_ids = mode_config.get('personas', ['sarah_chen'])
        
        violations = await self._run_validations(prompt, context)
        
        return GovernanceResult(
            success=len(violations) == 0,
            mode=ExecutionMode.SINGLE_AGENT.value,
            agents_executed=[agent_id],
            personas_executed=persona_ids,
            violations=violations,
            audit_results={},
            prompt_transformations={},
            execution_time_ms=0
        )
    
    async def _execute_multi_agent_single_persona(self, prompt: str, context: Optional[Dict[str, Any]]) -> GovernanceResult:
        """Execute with multiple agents, single persona each"""
        mode_config = self.config['execution_modes'].get('multi_agent_single_persona', {})
        agents = mode_config.get('agents', ['primary', 'business_auditor'])
        personas_per_agent = mode_config.get('personas_per_agent', {})
        
        all_personas = []
        for agent in agents:
            all_personas.extend(personas_per_agent.get(agent, []))
        
        violations = await self._run_validations(prompt, context)
        
        return GovernanceResult(
            success=len(violations) == 0,
            mode=ExecutionMode.MULTI_AGENT_SINGLE_PERSONA.value,
            agents_executed=agents,
            personas_executed=all_personas,
            violations=violations,
            audit_results={},
            prompt_transformations={},
            execution_time_ms=0
        )
    
    async def _execute_multi_agent_multi_persona(self, prompt: str, context: Optional[Dict[str, Any]]) -> GovernanceResult:
        """Execute with multiple agents and multiple personas"""
        mode_config = self.config['execution_modes'].get('multi_agent_multi_persona', {})
        agents = mode_config.get('agents', ['prompt_interceptor', 'primary', 'business_auditor'])
        personas_per_agent = mode_config.get('personas_per_agent', {})
        
        all_personas = []
        for agent in agents:
            all_personas.extend(personas_per_agent.get(agent, []))
        
        violations = await self._run_validations(prompt, context)
        
        # Execute personas in parallel if enabled
        if self.config['defaults'].get('parallel_execution', True):
            tasks = []
            for persona_id in all_personas:
                if persona_id in self.personas and self.personas[persona_id].enabled:
                    tasks.append(self._execute_persona(persona_id, prompt, context))
            
            if tasks:
                await asyncio.gather(*tasks)
        
        return GovernanceResult(
            success=len(violations) == 0,
            mode=ExecutionMode.MULTI_AGENT_MULTI_PERSONA.value,
            agents_executed=agents,
            personas_executed=all_personas,
            violations=violations,
            audit_results={},
            prompt_transformations={},
            execution_time_ms=0
        )
    
    async def _execute_full_orchestration(self, prompt: str, context: Optional[Dict[str, Any]]) -> GovernanceResult:
        """Execute full orchestration with all agents and personas"""
        all_agents = [a for a in self.agents.keys() if self.agents[a].enabled]
        all_personas = [p for p in self.personas.keys() if self.personas[p].enabled]
        
        violations = await self._run_validations(prompt, context)
        
        # Sort agents by execution order
        sorted_agents = sorted(all_agents, key=lambda a: self.agents[a].execution_order)
        
        # Execute agents in order
        for agent_id in sorted_agents:
            agent = self.agents[agent_id]
            
            # Check if agent should run after others
            if agent.runs_after:
                # This is handled by execution_order
                pass
            
            # Execute agent with its personas
            if agent.personas:
                for persona_id in agent.personas:
                    if persona_id in self.personas and self.personas[persona_id].enabled:
                        await self._execute_persona(persona_id, prompt, context)
        
        return GovernanceResult(
            success=len(violations) == 0,
            mode=ExecutionMode.FULL_ORCHESTRATION.value,
            agents_executed=sorted_agents,
            personas_executed=all_personas,
            violations=violations,
            audit_results={},
            prompt_transformations={},
            execution_time_ms=0
        )
    
    async def _execute_persona(self, persona_id: str, prompt: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a specific persona"""
        persona = self.personas[persona_id]
        
        # Run persona-specific validations
        validations = persona.validations
        results = {}
        
        for validation_name, enabled in validations.items():
            if enabled:
                results[validation_name] = await self._run_persona_validation(
                    persona_id, validation_name, prompt, context
                )
        
        return results
    
    async def _run_persona_validation(self, persona_id: str, validation_name: str, 
                                     prompt: str, context: Optional[Dict[str, Any]]) -> bool:
        """Run a specific validation for a persona"""
        # This would integrate with actual validation logic
        # For now, return success
        return True
    
    async def _run_validations(self, prompt: str, context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run global validation rules"""
        violations = []
        
        for rule_name, rule in self.validation_rules.items():
            if rule.enabled:
                # Check for pattern violations
                for pattern in rule.patterns:
                    if pattern in prompt:
                        # Check if in exceptions
                        skip = False
                        if context and 'file' in context:
                            for exception in rule.exceptions:
                                if exception in context['file']:
                                    skip = True
                                    break
                        
                        if not skip:
                            violations.append({
                                'rule': rule_name,
                                'severity': rule.severity,
                                'pattern': pattern,
                                'auto_fix': rule.auto_fix,
                                'location': 'prompt'
                            })
        
        return violations
    
    async def _run_business_auditor(self, result: GovernanceResult, prompt: str, 
                                   context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run Dr. Rachel Torres' business auditor"""
        audit_results = {
            'business_features_validated': False,
            'assumptions_destroyed': [],
            'gaps_found': [],
            'evidence_required': [],
            'aggressive_challenges': []
        }
        
        # Check if Rachel Torres is enabled
        if 'rachel_torres' not in self.personas or not self.personas['rachel_torres'].enabled:
            return audit_results
        
        rachel = self.personas['rachel_torres']
        
        # Aggressive assumption destruction
        if rachel.rules.get('reject_unvalidated_assumptions', True):
            assumptions = self._find_assumptions(prompt, context)
            audit_results['assumptions_destroyed'] = assumptions
        
        # Business feature gap analysis
        if rachel.validations.get('gap_analysis', True):
            gaps = self._find_business_gaps(prompt, context)
            audit_results['gaps_found'] = gaps
        
        # Generate aggressive challenges
        if rachel.rules.get('aggressive_challenging', True):
            for persona_id in result.personas_executed:
                if persona_id != 'rachel_torres':
                    challenge = self._generate_aggressive_challenge(persona_id, prompt)
                    audit_results['aggressive_challenges'].append({
                        'target': persona_id,
                        'challenge': challenge
                    })
        
        audit_results['business_features_validated'] = len(audit_results['gaps_found']) == 0
        
        return audit_results
    
    def _find_assumptions(self, prompt: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Find assumptions in prompt and context"""
        assumptions = []
        assumption_patterns = ['assume', 'should', 'probably', 'likely', 'expect', 'think']
        
        for pattern in assumption_patterns:
            if pattern in prompt.lower():
                assumptions.append(f"Assumption detected: '{pattern}' in prompt")
        
        return assumptions
    
    def _find_business_gaps(self, prompt: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Find business logic gaps"""
        gaps = []
        
        # Check for business keywords without implementation
        business_keywords = ['business', 'feature', 'requirement', 'user story', 'capability']
        implementation_keywords = ['implement', 'code', 'function', 'class', 'method']
        
        has_business = any(kw in prompt.lower() for kw in business_keywords)
        has_implementation = any(kw in prompt.lower() for kw in implementation_keywords)
        
        if has_business and not has_implementation:
            gaps.append("Business feature mentioned without implementation details")
        
        return gaps
    
    def _generate_aggressive_challenge(self, persona_id: str, prompt: str) -> str:
        """Generate aggressive challenge for a persona"""
        challenges = {
            'sarah_chen': "Where's the evidence that your AI integration delivers actual business value?",
            'marcus_rodriguez': "How does your performance optimization translate to user-perceived improvements?",
            'emily_watson': "What user research validates your UX decisions solve real problems?"
        }
        
        return challenges.get(persona_id, f"Validate your assumptions with evidence for: {prompt[:50]}...")
    
    # UI Integration Methods
    
    def update_config(self, updates: Dict[str, Any], source: str = 'ui') -> bool:
        """Update configuration from UI or API"""
        # Save current config to history
        self.config_history.append(copy.deepcopy(self.config))
        
        # Apply updates
        self._merge_config(self.config, updates)
        
        # Re-parse components
        self.agents = self._parse_agents()
        self.personas = self._parse_personas()
        self.validation_rules = self._parse_validation_rules()
        self.prompt_interceptor = PromptInterceptor(self.config.get('prompt_interception', {}))
        
        # Save to file if persistence enabled
        if self.config.get('persistence', {}).get('save_config_changes', True):
            self.save_config()
        
        return True
    
    def _merge_config(self, base: Dict, updates: Dict) -> None:
        """Recursively merge configuration updates"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def reset_config(self, to_defaults: bool = False) -> bool:
        """Reset configuration to defaults or previous state"""
        if to_defaults:
            self.config = self._get_default_config()
        elif self.config_history:
            self.config = self.config_history.pop()
        else:
            return False
        
        # Re-parse components
        self.agents = self._parse_agents()
        self.personas = self._parse_personas()
        self.validation_rules = self._parse_validation_rules()
        self.prompt_interceptor = PromptInterceptor(self.config.get('prompt_interception', {}))
        
        return True
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def export_config(self, format: str = 'json') -> str:
        """Export configuration in specified format"""
        if format == 'json':
            return json.dumps(self.config, indent=2)
        elif format == 'yaml':
            # Would require PyYAML
            import yaml
            return yaml.dump(self.config)
        elif format == 'python':
            return f"config = {repr(self.config)}"
        else:
            return json.dumps(self.config)
    
    def validate_config(self, config: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """Validate configuration"""
        config = config or self.config
        errors = []
        
        # Check required fields
        required = ['version', 'defaults', 'agents', 'personas', 'validation_rules']
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate agents
        for agent_id, agent in config.get('agents', {}).items():
            if isinstance(agent, dict):
                if 'id' not in agent:
                    errors.append(f"Agent {agent_id} missing id field")
        
        # Validate personas
        for persona_id, persona in config.get('personas', {}).items():
            if 'id' not in persona:
                errors.append(f"Persona {persona_id} missing id field")
        
        return len(errors) == 0, errors
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status for UI"""
        return {
            'version': self.config.get('version', '5.0'),
            'active_agents': [a for a in self.agents.keys() if self.agents[a].enabled],
            'active_personas': [p for p in self.personas.keys() if self.personas[p].enabled],
            'prompt_interceptor_enabled': self.config['defaults'].get('enable_prompt_interceptor', True),
            'business_auditor_enabled': self.config['defaults'].get('enable_business_auditor', True),
            'validation_rules_active': sum(1 for r in self.validation_rules.values() if r.enabled),
            'config_history_size': len(self.config_history)
        }

# Portable module exports
__all__ = [
    'DataDrivenGovernanceOrchestrator',
    'ExecutionMode',
    'Agent',
    'Persona',
    'ValidationRule',
    'GovernanceResult',
    'PromptInterceptor'
]

async def demo():
    """Demonstrate the data-driven governance system"""
    print("="*60)
    print("DATA-DRIVEN GOVERNANCE ORCHESTRATOR v5.0")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Get status
    status = orchestrator.get_status()
    print(f"\nStatus: {json.dumps(status, indent=2)}")
    
    # Test different execution modes
    test_prompts = [
        ("Fix the bug in the code", ExecutionMode.SINGLE_AGENT.value),
        ("Optimize the cache and improve UI performance", ExecutionMode.MULTI_AGENT_MULTI_PERSONA.value),
        ("Complete system review with all validations", ExecutionMode.FULL_ORCHESTRATION.value)
    ]
    
    for prompt, mode in test_prompts:
        print(f"\n{'='*40}")
        print(f"Prompt: {prompt}")
        print(f"Mode: {mode}")
        
        result = await orchestrator.execute(prompt, mode=mode)
        
        print(f"Success: {result.success}")
        print(f"Agents: {result.agents_executed}")
        print(f"Personas: {result.personas_executed}")
        print(f"Violations: {len(result.violations)}")
        if result.audit_results:
            print(f"Audit: {result.audit_results.get('business_features_validated')}")
        print(f"Time: {result.execution_time_ms}ms")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo())