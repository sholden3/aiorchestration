#!/usr/bin/env python3
"""
🔥 SIMPLE PERSONA ORCHESTRATOR SCRIPT 🔥

This script integrates with your existing Claude AI hook system to automatically
apply persona orchestration and defensive validation to every Claude interaction.

Usage:
    - Place this in your Claude AI hook directory
    - Configure persona_config.json
    - The script will automatically intercept and enhance Claude responses
"""

import yaml
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# 🔥 ADD THESE NEW IMPORTS for TODO functionality
import json
import datetime
from dataclasses import asdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    MINIMAL = "minimal"
    STANDARD = "standard" 
    STRICT = "strict"
    MAXIMUM = "maximum"

@dataclass
class PersonaConfig:
    """Simple persona configuration"""
    persona_id: str
    name: str
    enabled: bool
    validation_level: ValidationLevel
    triggers: List[str]
    mandatory_checks: List[str]
    prohibited_actions: List[str]
    system_prompt: str

class TODOPriority(Enum):
    CRITICAL = "critical"      # 🚨 Production blockers, security issues
    HIGH = "high"             # 🔥 Performance issues, architectural debt
    MEDIUM = "medium"         # 🎯 Feature enhancements, optimizations  
    LOW = "low"               # 📋 Documentation, minor improvements

class TODOStatus(Enum):
    CREATED = "created"           # 📝 Just created, needs analysis
    ANALYZED = "analyzed"         # 🔍 Persona consultation completed
    IN_PROGRESS = "in_progress"   # 🚧 Work started
    REVIEW = "review"            # 👀 Code review needed
    TESTING = "testing"          # 🧪 Testing phase
    COMPLETED = "completed"      # ✅ Done and verified
    BLOCKED = "blocked"          # 🚫 Cannot proceed

class TODOCategory(Enum):
    VRO_OPTIMIZATION = "vro_optimization"      # 🚀 VRO algorithm improvements
    SECURITY = "security"                      # 🛡️ Security enhancements
    PERFORMANCE = "performance"                # ⚡ Performance optimizations
    ARCHITECTURE = "architecture"              # 🏗️ Architectural improvements
    BUG_FIX = "bug_fix"                       # 🐛 Bug fixes
    FEATURE = "feature"                       # ✨ New features
    DOCUMENTATION = "documentation"            # 📚 Documentation tasks
    TECHNICAL_DEBT = "technical_debt"         # 🔧 Code cleanup/refactoring
    ML_OPTIMIZATION = "ml_optimization"  # 🧠 ML-powered optimizations
    CACHE_OPTIMIZATION = "cache_optimization"  # 🚀 Caching strategies

@dataclass
class TODOItem:
    """Enhanced TODO item with persona integration"""
    id: str
    title: str
    description: str
    category: TODOCategory
    priority: TODOPriority
    status: TODOStatus
    
    # Persona consultation
    required_personas: List[str]
    persona_analysis: Dict[str, str]
    persona_recommendations: List[str]
    
    # Context and tracking
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    created_by: str = "claude_code"
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    
    # Dependencies and verification
    dependencies: List[str] = None
    verification_criteria: List[str] = None
    completion_evidence: List[str] = None
    
    # Business rules
    estimated_effort: Optional[str] = None  # "1h", "1d", "1w"
    deadline: Optional[datetime.datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.dependencies is None:
            self.dependencies = []
        if self.verification_criteria is None:
            self.verification_criteria = []
        if self.completion_evidence is None:
            self.completion_evidence = []
        if self.tags is None:
            self.tags = []
        if self.persona_recommendations is None:
            self.persona_recommendations = []


class SimplePersonaOrchestrator:
    """
    🛡️ LIGHTWEIGHT PERSONA ORCHESTRATION ENGINE
    
    Integrates with your existing Claude AI hook system to provide:
    - Automatic persona selection based on content triggers
    - Defensive validation protocol enforcement  
    - Multi-persona collaboration when needed
    - Rule enforcement for business logic preservation
    """
    
    def __init__(self, config_dir: str = "./persona_config"):
        self.config_dir = config_dir
        self.personas: Dict[str, PersonaConfig] = {}
        self.validation_rules: Dict[str, Any] = {}
        self.collaboration_rules: Dict[str, Any] = {}
        
        self._load_configurations()
    
    def _load_configurations(self):
        """🔧 Load persona configurations from YAML files"""
        try:
            # Load persona status
            status_file = os.path.join(self.config_dir, "persona_status.yaml")
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    self.persona_status = yaml.safe_load(f)
            
            # Load validation rules
            rules_file = os.path.join(self.config_dir, "validation_rules.yaml") 
            if os.path.exists(rules_file):
                with open(rules_file, 'r') as f:
                    self.validation_rules = yaml.safe_load(f)
            
            # Load collaboration rules
            collab_file = os.path.join(self.config_dir, "collaboration_rules.yaml")
            if os.path.exists(collab_file):
                with open(collab_file, 'r') as f:
                    self.collaboration_rules = yaml.safe_load(f)
            
            # Load individual persona configs
            self._load_persona_configs()
            
            logger.info(f"✅ Loaded {len(self.personas)} persona configurations")
            
        except Exception as e:
            logger.error(f"🚨 Configuration loading failed: {e}")
            raise

    def _load_persona_configs(self):
        """🔧 Load individual persona configuration files"""
        persona_files = [
            "persona_vro_optimization_expert.yaml",       # 🎯 TOP PRIORITY VRO expert
            "persona_alexandra_vro_expert.yaml",          # 🎯 Secondary VRO expert  
            "persona_defensive_ai_architect.yaml",
            "persona_marcus_dotnet_architect.yaml", 
            "persona_general_senior_architect.yaml",      # 🆕 New general architect
        ]
        
        for file_name in persona_files:
            file_path = os.path.join(self.config_dir, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    # Check if persona is enabled
                    persona_id = config_data['persona_id']
                    status = self.persona_status.get('persona_status', {}).get(persona_id, {})
                    
                    if status.get('enabled', False):
                        persona = PersonaConfig(
                            persona_id=persona_id,
                            name=config_data['name'],
                            enabled=True,
                            validation_level=ValidationLevel(status.get('validation_level', 'standard')),
                            triggers=config_data.get('triggers', []),
                            mandatory_checks=config_data.get('mandatory_checks', []),
                            prohibited_actions=config_data.get('prohibited_actions', []),
                            system_prompt=config_data.get('system_prompt', '')
                        )
                        
                        self.personas[persona_id] = persona
                        logger.info(f"✅ Loaded persona: {persona.name} (Priority: {status.get('priority', 999)})")
                    
                except Exception as e:
                    logger.error(f"🚨 Failed to load {file_name}: {e}")

    def analyze_request(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🔍 ANALYZE USER REQUEST and determine required personas with VRO PRIORITY
        
        Returns orchestration plan with VRO optimization expert prioritized
        """
        if context is None:
            context = {}
        
        analysis = {
            "required_personas": [],
            "validation_level": ValidationLevel.STANDARD,
            "requires_collaboration": False,
            "rule_violations": [],
            "orchestration_prompt": "",
            "primary_persona": None
        }
        
        # 🎯 VRO PRIORITY TRIGGER ANALYSIS - Check VRO keywords first!
        user_input_lower = user_input.lower()
        
        # 🔥 PRIORITY CHECK: VRO optimization keywords get TOP PRIORITY
        vro_optimization_keywords = [
            "vrp", "vehicle routing", "optimization", "metaheuristics", "routing algorithms", 
            "tsp", "cvrp", "vrptw", "genetic algorithms", "simulated annealing",
            "performance metrics", "algorithmic", "cache hit rate", "complexity analysis",
            "logistics", "delivery", "pickup", "depot", "capacity", "fuel consumption"
        ]
        
        vro_triggers = sum(1 for keyword in vro_optimization_keywords if keyword in user_input_lower)
        
        if vro_triggers > 0:
            # 🎯 VRO OPTIMIZATION EXPERT GETS TOP PRIORITY!
            if "vro_optimization_expert" in self.personas:
                analysis["required_personas"].append("vro_optimization_expert")
                analysis["primary_persona"] = "vro_optimization_expert"
                analysis["validation_level"] = ValidationLevel.MAXIMUM
                logger.info(f"🎯 VRO OPTIMIZATION EXPERT activated with {vro_triggers} trigger matches!")
        
        # 🔍 REGULAR PERSONA TRIGGER ANALYSIS (sorted by priority)
        persona_scores = {}
        
        for persona_id, persona in self.personas.items():
            if persona_id == "vro_optimization_expert" and persona_id in analysis["required_personas"]:
                continue  # Already handled above
                
            score = 0
            for trigger in persona.triggers:
                if trigger.lower() in user_input_lower:
                    score += 1
            
            if score > 0:
                # Get priority from status config
                priority = self.persona_status.get('persona_status', {}).get(persona_id, {}).get('priority', 999)
                persona_scores[persona_id] = (score, priority)
        
        # 🏆 SORT BY TRIGGER SCORE, THEN BY PRIORITY (lower priority number = higher priority)
        sorted_personas = sorted(persona_scores.items(), key=lambda x: (-x[1][0], x[1][1]))
        
        # Add top scoring personas
        for persona_id, (score, priority) in sorted_personas:
            if len(analysis["required_personas"]) < 4:  # Max 4 personas
                analysis["required_personas"].append(persona_id)
                logger.info(f"🎯 Triggered persona: {self.personas[persona_id].name} (score: {score}, priority: {priority})")
        
        # 🔥 DETERMINE VALIDATION LEVEL based on content
        if any(keyword in user_input_lower for keyword in ["critical", "production", "security", "validation", "optimization"]):
            analysis["validation_level"] = ValidationLevel.MAXIMUM
        elif any(keyword in user_input_lower for keyword in ["architecture", "review", "performance", "algorithm"]):
            analysis["validation_level"] = ValidationLevel.STRICT
        
        # 🤝 COLLABORATION REQUIREMENTS
        if len(analysis["required_personas"]) > 1:
            analysis["requires_collaboration"] = True
        
        # 🛡️ SPECIAL VRO COLLABORATION RULES
        collaboration_rules = self.collaboration_rules.get('collaboration_rules', {})
        
        # Check priority triggers first
        priority_triggers = collaboration_rules.get('priority_triggers', {})
        for trigger_name, trigger_config in priority_triggers.items():
            if any(keyword in user_input_lower for keyword in trigger_config.get('keywords', [])):
                # VRO optimization detected - apply priority rules
                primary = trigger_config.get('primary_persona')
                if primary and primary in self.personas:
                    if primary not in analysis["required_personas"]:
                        analysis["required_personas"].insert(0, primary)
                    analysis["primary_persona"] = primary
                    
                # Add secondary personas
                for secondary in trigger_config.get('secondary_personas', []):
                    if secondary in self.personas and secondary not in analysis["required_personas"]:
                        analysis["required_personas"].append(secondary)
                
                analysis["validation_level"] = ValidationLevel(trigger_config.get('validation_level', 'strict'))
                analysis["requires_collaboration"] = True
                break
        
        # Check other collaboration rules
        for rule_name, rule_config in collaboration_rules.get('required_collaborations', {}).items():
            if self._matches_collaboration_rule(user_input_lower, rule_name, rule_config):
                # Update personas if not already set by priority triggers
                if not analysis.get("primary_persona"):
                    analysis["required_personas"] = rule_config['required_personas']
                    analysis["validation_level"] = ValidationLevel(rule_config['validation_level'])
                    analysis["requires_collaboration"] = True
                break
        
        # 📋 GENERATE ORCHESTRATION PROMPT with VRO priority
        analysis["orchestration_prompt"] = self._generate_orchestration_prompt(analysis)
        
        return analysis

    def _matches_collaboration_rule(self, user_input: str, rule_name: str, rule_config: Dict = None) -> bool:
        """🔍 Check if user input matches specific collaboration rules"""
        
        if rule_config and 'triggers' in rule_config:
            # Use triggers from rule config if available
            triggers = rule_config['triggers']
            return any(trigger in user_input for trigger in triggers)
        
        # Fallback to hardcoded rule keywords for backward compatibility
        rule_keywords = {
            "vro_optimization_analysis": ["optimization", "metaheuristics", "algorithm", "performance"],
            "vro_architecture_review": ["vro", "routing", "architecture", "review"],
            "dotnet_performance_optimization": [".net", "performance", "optimization", "c#"],
            "comprehensive_system_review": ["system", "comprehensive", "review", "architecture"],
            "angular_architecture_review": ["angular", "frontend", "spa", "typescript"]
        }
        
        keywords = rule_keywords.get(rule_name, [])
        return any(keyword in user_input for keyword in keywords)

    def _generate_orchestration_prompt(self, analysis: Dict[str, Any]) -> str:
        """📋 Generate the prompt injection for Claude"""
        
        if not analysis["required_personas"]:
            return ""
        
        prompt_parts = []
        prompt_parts.append("🔥 PERSONA ORCHESTRATION SYSTEM ACTIVATED 🔥\n")
        
        # 🎯 REQUIRED PERSONAS SECTION
        prompt_parts.append("🎯 REQUIRED PERSONAS FOR THIS REQUEST:")
        for persona_id in analysis["required_personas"]:
            persona = self.personas[persona_id]
            prompt_parts.append(f"✅ {persona.name} ({persona_id})")
        
        prompt_parts.append("")
        
        # 🛡️ VALIDATION REQUIREMENTS
        prompt_parts.append(f"🛡️ VALIDATION LEVEL: {analysis['validation_level'].value.upper()}")
        prompt_parts.append("")
        
        # 📋 MANDATORY VALIDATION CHECKS
        prompt_parts.append("📋 MANDATORY VALIDATION CHECKS:")
        all_checks = set()
        for persona_id in analysis["required_personas"]:
            persona = self.personas[persona_id]
            all_checks.update(persona.mandatory_checks)
        
        for check in sorted(all_checks):
            prompt_parts.append(f"□ {check}")
        prompt_parts.append("")
        
        # 🚨 PROHIBITED ACTIONS
        prompt_parts.append("🚨 PROHIBITED ACTIONS:")
        all_prohibited = set()
        for persona_id in analysis["required_personas"]:
            persona = self.personas[persona_id]
            all_prohibited.update(persona.prohibited_actions)
        
        for action in sorted(all_prohibited):
            prompt_parts.append(f"❌ {action}")
        prompt_parts.append("")
        
        # 🤝 COLLABORATION INSTRUCTIONS
        if analysis["requires_collaboration"]:
            prompt_parts.append("🤝 COLLABORATION REQUIRED:")
            prompt_parts.append("You MUST provide analysis from EACH required persona, then synthesize their insights.")
            prompt_parts.append("")
        
        # 📝 RESPONSE FORMAT REQUIREMENTS
        prompt_parts.append("📝 REQUIRED RESPONSE FORMAT:")
        prompt_parts.append("")
        
        for persona_id in analysis["required_personas"]:
            persona = self.personas[persona_id]
            icon = self._get_persona_icon(persona_id)
            prompt_parts.append(f"{icon} {persona.name.upper()} ANALYSIS:")
            prompt_parts.append(f"[Provide {persona.name}'s specialized analysis here]")
            prompt_parts.append("")
        
        if analysis["requires_collaboration"]:
            prompt_parts.append("🚀 SYNTHESIZED RECOMMENDATION:")
            prompt_parts.append("[Combined insights from all consulted personas]")
            prompt_parts.append("")
        
        prompt_parts.append("✅ VALIDATION CHECKPOINTS COMPLETED:")
        prompt_parts.append("[List the validation checks you performed]")
        
        return "\n".join(prompt_parts)

    def _get_persona_icon(self, persona_id: str) -> str:
        """🎨 Get emoji icon for persona"""
        icons = {
            "vro_optimization_expert": "🚀",      # 🎯 TOP PRIORITY VRO expert
            "alexandra_vro_expert": "🎯",         # 🎯 Secondary VRO expert
            "defensive_ai_architect": "🛡️",
            "marcus_dotnet_architect": "🏗️", 
            "general_senior_architect": "🏛️",    # 🆕 General architect
            "alex_angular_architect": "🎨"
        }
        return icons.get(persona_id, "🤖")

    def validate_response(self, response: str, required_personas: List[str]) -> Dict[str, Any]:
        """🛡️ Validate Claude's response against persona requirements"""
        
        validation_result = {
            "is_valid": True,
            "missing_personas": [],
            "validation_errors": [],
            "recommendations": []
        }
        
        # 🔍 CHECK FOR REQUIRED PERSONA SECTIONS
        for persona_id in required_personas:
            persona = self.personas[persona_id]
            persona_name = persona.name.upper()
            
            if persona_name not in response.upper():
                validation_result["missing_personas"].append(persona.name)
                validation_result["is_valid"] = False
        
        # 🛡️ CHECK FOR PROHIBITED CONTENT
        prohibited_patterns = [
            r"magic\s+number",
            r"magic\s+variable", 
            r"hardcoded",
            r"TODO.*without.*explanation"
        ]
        
        for pattern in prohibited_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                validation_result["validation_errors"].append(f"Prohibited pattern detected: {pattern}")
                validation_result["is_valid"] = False
        
        # 📋 CHECK FOR VALIDATION CHECKLIST
        if "VALIDATION CHECKPOINTS" not in response.upper():
            validation_result["validation_errors"].append("Missing validation checkpoints section")
            validation_result["is_valid"] = False
        
        return validation_result

    def enhance_claude_prompt(self, original_prompt: str, context: Dict[str, Any] = None) -> str:
        """
        🚀 MAIN HOOK FUNCTION: Enhance Claude prompt with persona orchestration
        
        This is the function your existing Claude AI hook should call.
        """
        
        # 🔍 ANALYZE THE REQUEST
        analysis = self.analyze_request(original_prompt, context)
        
        if not analysis["required_personas"]:
            # No personas required, return original prompt
            return original_prompt
        
        # 🔥 INJECT ORCHESTRATION SYSTEM
        enhanced_prompt = f"""
{analysis['orchestration_prompt']}

---

ORIGINAL USER REQUEST:
{original_prompt}

---

🚨 CRITICAL INSTRUCTION: You MUST follow the persona orchestration requirements above.
Provide analysis from each required persona, then synthesize their insights.
Include the validation checkpoints section at the end.
"""
        
        logger.info(f"🔥 Enhanced prompt with {len(analysis['required_personas'])} personas")
        return enhanced_prompt

    def process_claude_response(self, response: str, original_request: str) -> Dict[str, Any]:
        """
        🛡️ POST-PROCESS CLAUDE RESPONSE: Validate and enhance if needed
        
        Call this after getting Claude's response to ensure quality.
        """
        
        analysis = self.analyze_request(original_request)
        validation = self.validate_response(response, analysis["required_personas"])
        
        result = {
            "original_response": response,
            "enhanced_response": response,
            "validation_result": validation,
            "personas_consulted": analysis["required_personas"],
            "recommendations": []
        }
        
        # 🚨 IF VALIDATION FAILS, PROVIDE ENHANCEMENT SUGGESTIONS
        if not validation["is_valid"]:
            enhancement_suggestions = []
            
            if validation["missing_personas"]:
                enhancement_suggestions.append(
                    f"Missing analysis from: {', '.join(validation['missing_personas'])}"
                )
            
            if validation["validation_errors"]:
                enhancement_suggestions.extend(validation["validation_errors"])
            
            result["recommendations"] = enhancement_suggestions
            
            logger.warning(f"🚨 Response validation failed: {validation['validation_errors']}")
        
        return result

# ================================================================================
# 🔥 ADD THIS CLASS TO YOUR SimplePersonaOrchestrator CLASS
# ================================================================================

class TODOIntegratedPersonaOrchestrator:
    """
    🛡️ SELF-CONTAINED TODO + PERSONA ORCHESTRATOR
    
    This fixes the inheritance issue by being self-contained
    """
    
    def __init__(self, config_dir: str = "./persona_config"):
        self.config_dir = config_dir
        
        # Initialize your existing persona system attributes
        self.personas: Dict[str, Any] = {}
        self.validation_rules: Dict[str, Any] = {}
        self.collaboration_rules: Dict[str, Any] = {}
        
        # TODO management
        self.todos: Dict[str, TODOItem] = {}
        self.todo_db_path = f"{config_dir}/todos.json"
        
        # 🎯 SIMPLE PERSONA STATUS TRACKING (self-contained)
        self.persona_status = {
            "vro_optimization_expert": {"enabled": True, "priority": 1},
            "performance_optimization_expert": {"enabled": True, "priority": 2},
            "alexandra_vro_expert": {"enabled": True, "priority": 2},
            "defensive_ai_architect": {"enabled": True, "priority": 3},
            "marcus_dotnet_architect": {"enabled": True, "priority": 4},
            "general_senior_architect": {"enabled": True, "priority": 5},
            "alex_angular_architect": {"enabled": False, "priority": 6}
        }
        
        # 🎯 SIMPLE PERSONA DEFINITIONS (self-contained)
        self.persona_definitions = {
            "vro_optimization_expert": {
                "name": "🚀 VRO Optimization Expert",
                "triggers": ["vrp", "vehicle routing", "optimization", "metaheuristics", "routing algorithms", 
                           "tsp", "cvrp", "vrptw", "genetic algorithms", "simulated annealing",
                           "performance metrics", "algorithmic", "cache hit rate", "complexity analysis"],
                "enabled": True
            },
            "alexandra_vro_expert": {
                "name": "🎯 Dr. Alexandra (VRO Expert)",
                "triggers": ["vro", "routing", "time windows", "constraints", "delivery", "pickup", "depot"],
                "enabled": True
            },
            "defensive_ai_architect": {
                "name": "🛡️ Defensive AI Architect", 
                "triggers": ["security", "validation", "defensive patterns", "input validation", "ai architecture"],
                "enabled": True
            },
            "marcus_dotnet_architect": {
                "name": "🏗️ Marcus (.NET Expert)",
                "triggers": [".net", "c#", "performance", "solid principles", "memory allocation"],
                "enabled": True
            },
            "general_senior_architect": {
                "name": "🏛️ Senior Architect",
                "triggers": ["architecture", "system design", "enterprise", "scalability", "maintainability"],
                "enabled": True
            },
            "performance_optimization_expert": {
                "name": "🚀 Performance & Caching Expert",
                "triggers": [
                    "cache", "caching", "performance", "optimization", "ml caching", 
                    "predictive caching", "token reduction", "compression", "batching",
                    "l1 cache", "l2 cache", "memory optimization", "cpu cache",
                    "machine learning cache", "prefetching", "hit rate"
                ],
                "enabled": True
            },
        }
        
        # 🎯 CATEGORY TO PERSONA MAPPING
        self.category_personas = {
            TODOCategory.VRO_OPTIMIZATION: ["vro_optimization_expert", "alexandra_vro_expert", "defensive_ai_architect"],
            TODOCategory.SECURITY: ["defensive_ai_architect", "general_senior_architect"],
            TODOCategory.PERFORMANCE: ["vro_optimization_expert", "marcus_dotnet_architect", "defensive_ai_architect"],
            TODOCategory.ARCHITECTURE: ["general_senior_architect", "defensive_ai_architect", "marcus_dotnet_architect"],
            TODOCategory.BUG_FIX: ["defensive_ai_architect", "marcus_dotnet_architect"],
            TODOCategory.FEATURE: ["general_senior_architect", "defensive_ai_architect"],
            TODOCategory.DOCUMENTATION: ["general_senior_architect", "defensive_ai_architect"],
            TODOCategory.TECHNICAL_DEBT: ["defensive_ai_architect", "marcus_dotnet_architect", "general_senior_architect"],
            TODOCategory.PERFORMANCE: ["performance_optimization_expert", "vro_optimization_expert", "defensive_ai_architect"],
            TODOCategory.ML_OPTIMIZATION: ["performance_optimization_expert", "vro_optimization_expert", "defensive_ai_architect"],
            TODOCategory.CACHE_OPTIMIZATION: ["performance_optimization_expert", "defensive_ai_architect"]
        }
        
        # Load TODOs
        self.load_todos()
        
        print(f"✅ TODO-Integrated Persona Orchestrator initialized")
        print(f"📊 {len([p for p in self.persona_status.values() if p['enabled']])} personas enabled")

    def analyze_request(self, user_input: str, context: Dict[str, Any] = None) -> Any:
        """
        🔍 ANALYZE USER REQUEST and determine required personas with VRO PRIORITY
        
        This replicates your existing persona analysis functionality
        """
        if context is None:
            context = {}
        
        # Create a simple analysis result object
        class AnalysisResult:
            def __init__(self):
                self.required_personas = []
                self.validation_level = "standard"
                self.requires_collaboration = False
                self.orchestration_prompt = ""
                self.has_vro_priority = False
        
        analysis = AnalysisResult()
        user_input_lower = user_input.lower()
        
        # 🚀 VRO PRIORITY TRIGGER ANALYSIS
        vro_optimization_triggers = self.persona_definitions["vro_optimization_expert"]["triggers"]
        vro_score = sum(1 for trigger in vro_optimization_triggers if trigger in user_input_lower)
        
        if vro_score > 0:
            analysis.required_personas.append("vro_optimization_expert")
            analysis.has_vro_priority = True
            print(f"🎯 VRO OPTIMIZATION EXPERT activated! ({vro_score} triggers matched)")
        
        # Check other personas
        persona_scores = []
        for persona_id, persona_config in self.persona_definitions.items():
            if persona_id == "vro_optimization_expert":
                continue  # Already handled
                
            if not self.persona_status.get(persona_id, {}).get("enabled", False):
                continue
                
            score = sum(1 for trigger in persona_config["triggers"] if trigger in user_input_lower)
            if score > 0:
                priority = self.persona_status.get(persona_id, {}).get("priority", 999)
                persona_scores.append((persona_id, score, priority))
        
        # Sort by score (desc) then priority (asc)
        persona_scores.sort(key=lambda x: (-x[1], x[2]))
        
        # Add top personas (max 4 total)
        for persona_id, score, priority in persona_scores:
            if len(analysis.required_personas) < 4:
                analysis.required_personas.append(persona_id)
                print(f"✅ Activated: {self.persona_definitions[persona_id]['name']} (score: {score})")
        
        # Determine validation level
        if any(word in user_input_lower for word in ["critical", "production", "security", "optimization"]):
            analysis.validation_level = "maximum"
        elif any(word in user_input_lower for word in ["architecture", "performance", "algorithm"]):
            analysis.validation_level = "strict"
        
        # Set collaboration flag
        if len(analysis.required_personas) > 1:
            analysis.requires_collaboration = True
        
        # Generate orchestration prompt
        analysis.orchestration_prompt = self._generate_orchestration_prompt(analysis)
        
        return analysis

    def _generate_orchestration_prompt(self, analysis) -> str:
        """Generate the persona orchestration prompt"""
        
        if not analysis.required_personas:
            return ""
        
        prompt_parts = []
        prompt_parts.append("🔥 PERSONA ORCHESTRATION SYSTEM ACTIVATED 🔥\n")
        
        if analysis.has_vro_priority:
            prompt_parts.append("🚀 VRO OPTIMIZATION EXPERT HAS TOP PRIORITY FOR THIS REQUEST!\n")
        
        # Required personas section
        prompt_parts.append("🎯 REQUIRED PERSONAS FOR THIS REQUEST:")
        for persona_id in analysis.required_personas:
            persona_name = self.persona_definitions[persona_id]["name"]
            prompt_parts.append(f"✅ {persona_name}")
        prompt_parts.append("")
        
        # Validation requirements
        prompt_parts.append(f"🛡️ VALIDATION LEVEL: {analysis.validation_level.upper()}")
        prompt_parts.append("")
        
        # Response format
        prompt_parts.append("📝 REQUIRED RESPONSE FORMAT:")
        prompt_parts.append("")
        
        for persona_id in analysis.required_personas:
            persona = self.persona_definitions[persona_id]
            prompt_parts.append(f"{persona['name']} ANALYSIS:")
            
            if persona_id == "vro_optimization_expert":
                prompt_parts.append("[Performance metrics, algorithmic analysis, optimization opportunities, metaheuristic recommendations]")
            elif persona_id == "alexandra_vro_expert":
                prompt_parts.append("[VRO domain expertise, constraint analysis, routing optimization, time window considerations]")
            elif persona_id == "defensive_ai_architect":
                prompt_parts.append("[Defensive patterns, validation concerns, security implications, input sanitization]")
            elif persona_id == "marcus_dotnet_architect":
                prompt_parts.append("[.NET performance, SOLID principles, memory optimization, async patterns]")
            elif persona_id == "general_senior_architect":
                prompt_parts.append("[System design, enterprise patterns, scalability, architectural guidance]")
            
            prompt_parts.append("")
        
        if len(analysis.required_personas) > 1:
            prompt_parts.append("🚀 SYNTHESIZED RECOMMENDATION:")
            if analysis.has_vro_priority:
                prompt_parts.append("[Combined insights with VRO optimization expert guidance prioritized]")
            else:
                prompt_parts.append("[Combined insights from all consulted personas]")
            prompt_parts.append("")
        
        prompt_parts.append("✅ VALIDATION CHECKPOINTS COMPLETED:")
        prompt_parts.append("[List the validation checks you performed]")
        
        return "\n".join(prompt_parts)

    def create_todo_with_personas(self, 
                                 title: str, 
                                 description: str, 
                                 category: TODOCategory,
                                 priority: TODOPriority = TODOPriority.MEDIUM,
                                 file_path: Optional[str] = None,
                                 line_number: Optional[int] = None,
                                 auto_analyze: bool = True) -> str:
        """
        📝 CREATE TODO with automatic persona consultation
        """
        
        # Generate unique ID
        todo_id = self._generate_todo_id(title, description)
        
        # Determine required personas based on category
        required_personas = self.category_personas.get(category, ["general_senior_architect", "defensive_ai_architect"])
        
        # Create TODO item
        todo = TODOItem(
            id=todo_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=TODOStatus.CREATED,
            required_personas=required_personas,
            persona_analysis={},
            persona_recommendations=[],
            file_path=file_path,
            line_number=line_number
        )
        
        # Add verification criteria
        todo.verification_criteria = self._generate_verification_criteria(category, priority)
        
        # Store TODO
        self.todos[todo_id] = todo
        self.save_todos()
        
        print(f"📝 Created TODO: {todo_id}")
        print(f"🎯 Category: {category.value}")
        print(f"🔥 Priority: {priority.value}")
        print(f"👥 Required personas: {required_personas}")
        
        # Automatic persona analysis
        if auto_analyze:
            self.analyze_todo_with_personas(todo_id)
        
        return todo_id

    def analyze_todo_with_personas(self, todo_id: str) -> Dict[str, str]:
        """
        🔍 PERSONA ANALYSIS of TODO item
        """
        
        if todo_id not in self.todos:
            raise ValueError(f"TODO {todo_id} not found")
        
        todo = self.todos[todo_id]
        
        print(f"🔍 Analyzing TODO {todo_id} with {len(todo.required_personas)} personas...")
        
        # Create analysis prompt
        analysis_prompt = f"""
        TODO ANALYSIS REQUEST:
        
        Title: {todo.title}
        Description: {todo.description}
        Category: {todo.category.value}
        Priority: {todo.priority.value}
        File: {todo.file_path or 'N/A'}
        
        Required Analysis:
        1. Implementation approach and best practices
        2. Potential risks and defensive considerations
        3. Performance implications and optimization opportunities
        4. Testing strategy and verification criteria
        5. Completion criteria and success metrics
        6. Estimated effort and timeline recommendations
        """
        
        try:
            # Use the persona analysis system
            analysis = self.analyze_request(analysis_prompt)
            
            if analysis.required_personas:
                # Store the analysis results
                todo.persona_analysis["analysis_prompt"] = analysis.orchestration_prompt
                todo.persona_analysis["required_personas"] = analysis.required_personas
                todo.persona_analysis["validation_level"] = analysis.validation_level
                todo.persona_analysis["has_vro_priority"] = analysis.has_vro_priority
                
                # Extract recommendations
                recommendations = self._extract_todo_recommendations(todo)
                todo.persona_recommendations.extend(recommendations)
                
                todo.status = TODOStatus.ANALYZED
                todo.updated_at = datetime.datetime.now()
                
                self.save_todos()
                
                print(f"✅ TODO analysis completed for {todo_id}")
                print(f"🎯 Personas involved: {', '.join(analysis.required_personas)}")
                print(f"🛡️ Validation level: {analysis.validation_level}")
                
                return todo.persona_analysis
            else:
                print(f"⚠️ No personas triggered for TODO {todo_id}")
                return {}
                
        except Exception as e:
            print(f"🚨 TODO analysis failed: {e}")
            return {}

    def get_todo_dashboard(self) -> Dict[str, Any]:
        """📊 TODO DASHBOARD with persona utilization metrics"""
        
        dashboard = {
            "summary": {
                "total": len(self.todos),
                "by_status": {},
                "by_priority": {},
                "by_category": {}
            },
            "active_todos": [],
            "persona_utilization": {},
            "recent_analysis": [],
            "metrics": {
                "completion_rate": 0.0,
                "persona_effectiveness": {}
            }
        }
        
        # Calculate metrics
        now = datetime.datetime.now()
        completed_todos = []
        
        for todo in self.todos.values():
            # Status counts
            status_key = todo.status.value
            dashboard["summary"]["by_status"][status_key] = dashboard["summary"]["by_status"].get(status_key, 0) + 1
            
            # Priority counts
            priority_key = todo.priority.value
            dashboard["summary"]["by_priority"][priority_key] = dashboard["summary"]["by_priority"].get(priority_key, 0) + 1
            
            # Category counts
            category_key = todo.category.value
            dashboard["summary"]["by_category"][category_key] = dashboard["summary"]["by_category"].get(category_key, 0) + 1
            
            # Persona utilization tracking
            for persona in todo.required_personas:
                if persona not in dashboard["persona_utilization"]:
                    dashboard["persona_utilization"][persona] = 0
                dashboard["persona_utilization"][persona] += 1
            
            # Active TODOs
            if todo.status == TODOStatus.IN_PROGRESS:
                dashboard["active_todos"].append({
                    "id": todo.id,
                    "title": todo.title,
                    "priority": todo.priority.value,
                    "category": todo.category.value,
                    "personas": todo.required_personas
                })
            
            # Completed todos
            if todo.status == TODOStatus.COMPLETED:
                completed_todos.append(todo)
        
        # Completion rate
        if len(self.todos) > 0:
            dashboard["metrics"]["completion_rate"] = len(completed_todos) / len(self.todos) * 100
        
        return dashboard

    def complete_todo(self, todo_id: str, evidence: List[str] = None) -> bool:
        """✅ COMPLETE TODO with verification"""
        
        if todo_id not in self.todos:
            print(f"❌ TODO {todo_id} not found")
            return False
        
        todo = self.todos[todo_id]
        
        if evidence:
            todo.completion_evidence.extend(evidence)
        
        # Simple verification - check if we have evidence
        verification_passed = len(todo.completion_evidence) > 0
        
        if verification_passed:
            todo.status = TODOStatus.COMPLETED
            todo.updated_at = datetime.datetime.now()
            
            print(f"✅ TODO {todo_id} completed successfully!")
            print(f"👥 Consulted personas: {', '.join(todo.required_personas)}")
            
        else:
            print(f"⚠️ TODO {todo_id} needs completion evidence")
        
        self.save_todos()
        return verification_passed

    # Helper methods
    def _generate_todo_id(self, title: str, description: str) -> str:
        """Generate unique TODO ID"""
        content = f"{title}{description}{datetime.datetime.now().isoformat()}"
        return f"TODO_{hashlib.md5(content.encode()).hexdigest()[:8]}"

    def _generate_verification_criteria(self, category: TODOCategory, priority: TODOPriority) -> List[str]:
        """Generate verification criteria"""
        
        base_criteria = [
            "Code compiles without errors",
            "All existing unit tests pass",
            "No new security vulnerabilities introduced",
            "Performance impact assessed and documented"
        ]
        
        category_criteria = {
            TODOCategory.VRO_OPTIMIZATION: [
                "Algorithm complexity analysis completed",
                "Performance benchmarks show improvement",
                "Time window constraints validated",
                "Route optimization metrics measured"
            ],
            TODOCategory.SECURITY: [
                "Security review completed",
                "Input validation implemented",
                "Error handling covers edge cases",
                "No sensitive data exposed"
            ]
        }
        
        criteria = base_criteria.copy()
        criteria.extend(category_criteria.get(category, []))
        
        return criteria

    def _extract_todo_recommendations(self, todo: TODOItem) -> List[str]:
        """Extract recommendations from persona analysis"""
        
        recommendations = []
        
        if TODOCategory.VRO_OPTIMIZATION == todo.category:
            recommendations.extend([
                "Consider algorithmic complexity implications",
                "Benchmark performance before and after changes",
                "Validate time window constraints",
                "Document optimization rationale"
            ])
        
        if "defensive_ai_architect" in todo.required_personas:
            recommendations.extend([
                "Implement comprehensive input validation",
                "Add proper error handling and logging",
                "Consider security implications",
                "Follow defensive programming patterns"
            ])
        
        return recommendations

    def save_todos(self):
        """Save TODOs to persistent storage"""
        
        try:
            os.makedirs(os.path.dirname(self.todo_db_path), exist_ok=True)
            
            data = []
            for todo in self.todos.values():
                todo_dict = asdict(todo)
                
                # Convert enums to strings
                todo_dict['category'] = todo.category.value
                todo_dict['priority'] = todo.priority.value
                todo_dict['status'] = todo.status.value
                
                # Convert datetime to ISO format
                todo_dict['created_at'] = todo.created_at.isoformat()
                todo_dict['updated_at'] = todo.updated_at.isoformat()
                
                if todo.deadline:
                    todo_dict['deadline'] = todo.deadline.isoformat()
                
                data.append(todo_dict)
            
            with open(self.todo_db_path, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"🚨 Error saving TODOs: {e}")

    def load_todos(self):
        """Load TODOs from persistent storage"""
        
        try:
            with open(self.todo_db_path, 'r') as f:
                data = json.load(f)
            
            for todo_data in data:
                # Convert back to enums
                todo_data['category'] = TODOCategory(todo_data['category'])
                todo_data['priority'] = TODOPriority(todo_data['priority'])
                todo_data['status'] = TODOStatus(todo_data['status'])
                
                # Parse datetime fields
                todo_data['created_at'] = datetime.datetime.fromisoformat(todo_data['created_at'])
                todo_data['updated_at'] = datetime.datetime.fromisoformat(todo_data['updated_at'])
                
                if todo_data.get('deadline'):
                    todo_data['deadline'] = datetime.datetime.fromisoformat(todo_data['deadline'])
                
                todo = TODOItem(**todo_data)
                self.todos[todo.id] = todo
            
            print(f"📥 Loaded {len(self.todos)} TODOs from {self.todo_db_path}")
            
        except FileNotFoundError:
            print("📝 No existing TODO database found - starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading TODOs: {e}")

    # Compatibility methods to match your existing interface
    def enhance_claude_prompt(self, original_prompt: str) -> str:
        """🚀 ENHANCED CLAUDE PROMPT with persona orchestration"""
        
        analysis = self.analyze_request(original_prompt)
        
        if not analysis.required_personas:
            return original_prompt
        
        enhanced_prompt = f"""
{analysis.orchestration_prompt}

---

ORIGINAL USER REQUEST:
{original_prompt}

---

🚨 CRITICAL INSTRUCTION: You MUST follow the persona orchestration requirements above.
Provide analysis from each required persona, then synthesize their insights.
Include the validation checkpoints section at the end.
"""
        
        print(f"🔥 Enhanced prompt with {len(analysis.required_personas)} personas")
        return enhanced_prompt

    def is_persona_enabled(self, persona_id: str) -> bool:
        """🔍 Check if a specific persona is enabled"""
        return self.persona_status.get(persona_id, {}).get("enabled", False)

    def get_enabled_personas(self) -> List[str]:
        """📋 Get list of currently enabled personas"""
        return [pid for pid, status in self.persona_status.items() if status.get("enabled", False)]

# ====================================================================================================
# 🔧 INTEGRATION HELPERS FOR YOUR EXISTING HOOK SYSTEM
# ====================================================================================================

class ClaudePersonaHook:
    """
    🔌 SIMPLE INTEGRATION CLASS
    
    Use this class to integrate with your existing Claude AI hook system.
    """
    
    def __init__(self, config_dir: str = "./persona_config"):
        self.orchestrator = TODOIntegratedPersonaOrchestrator(config_dir)
    
    def pre_claude_hook(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        🚀 PRE-CLAUDE HOOK: Call this before sending request to Claude
        
        Returns enhanced prompt with persona orchestration instructions.
        """
        return self.orchestrator.enhance_claude_prompt(user_input, context)
    
    def post_claude_hook(self, claude_response: str, original_request: str) -> Dict[str, Any]:
        """
        🛡️ POST-CLAUDE HOOK: Call this after getting response from Claude
        
        Returns validation results and enhancement recommendations.
        """
        return self.orchestrator.process_claude_response(claude_response, original_request)
    
    def is_persona_enabled(self, persona_id: str) -> bool:
        """🔍 Check if a specific persona is enabled"""
        return persona_id in self.orchestrator.personas
    
    def get_enabled_personas(self) -> List[str]:
        """📋 Get list of currently enabled personas"""
        return list(self.orchestrator.personas.keys())

# ====================================================================================================
# 🚀 SIMPLE COMMAND LINE INTERFACE
# ====================================================================================================

PERSONA_SYSTEM = TODOIntegratedPersonaOrchestrator()

# ================================================================================
# 🚀 CONVENIENCE FUNCTIONS FOR YOUR EXISTING WORKFLOW
# ================================================================================

# 🔥 ADD THESE CONVENIENCE FUNCTIONS at the end of your file

def create_vro_todo(title: str, description: str, priority: str = "medium") -> str:
    """🚀 Quick VRO optimization TODO creation"""
    
    orchestrator = PERSONA_SYSTEM  # Use your PERSONA_SYSTEM
    priority_enum = TODOPriority(priority.lower()) 
    
    return orchestrator.create_todo_with_personas(
        title=title,
        description=description,
        category=TODOCategory.VRO_OPTIMIZATION,
        priority=priority_enum,
        auto_analyze=True
    )

def create_security_todo(title: str, description: str, priority: str = "high") -> str:
    """🛡️ Quick security TODO creation"""
    
    orchestrator = PERSONA_SYSTEM
    priority_enum = TODOPriority(priority.lower())
    
    return orchestrator.create_todo_with_personas(
        title=title,
        description=description,
        category=TODOCategory.SECURITY,
        priority=priority_enum,
        auto_analyze=True
    )

def create_ml_optimization_todo(title: str, description: str, priority: str = "high") -> str:
    """🧠 Quick ML optimization TODO creation"""
    
    orchestrator = PERSONA_SYSTEM
    priority_enum = TODOPriority(priority.lower())
    
    return orchestrator.create_todo_with_personas(
        title=title,
        description=description,
        category=TODOCategory.ML_OPTIMIZATION,  # You'll need to add this enum
        priority=priority_enum,
        auto_analyze=True
    )

def show_todo_dashboard():
    """📊 Show comprehensive TODO dashboard"""
    
    orchestrator = PERSONA_SYSTEM
    dashboard = orchestrator.get_todo_dashboard()
    
    print("🔥 TODO DASHBOARD WITH PERSONA INSIGHTS 🔥")
    print("=" * 60)
    
    # Summary
    print(f"📊 Total TODOs: {dashboard['summary']['total']}")
    print(f"📋 By Status: {dashboard['summary']['by_status']}")
    print(f"🎯 By Priority: {dashboard['summary']['by_priority']}")
    print(f"🏷️ By Category: {dashboard['summary']['by_category']}")
    
    # Persona utilization
    if dashboard['persona_utilization']:
        print(f"\n👥 Persona Utilization:")
        for persona, count in dashboard['persona_utilization'].items():
            print(f"   {persona}: {count} TODOs")
    
    # Active TODOs
    if dashboard['active_todos']:
        print(f"\n🚧 Active TODOs ({len(dashboard['active_todos'])}):")
        for todo in dashboard['active_todos']:
            print(f"   📝 {todo['id']}: {todo['title']}")
            print(f"      Priority: {todo['priority']} | Category: {todo['category']}")
            print(f"      Personas: {', '.join(todo['personas'])}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🔥 Persona Orchestration CLI")
    parser.add_argument("command", choices=["analyze", "enhance", "status", "test"])
    parser.add_argument("--input", "-i", help="Input text or file")
    parser.add_argument("--config", "-c", default="./persona_config", help="Config directory")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    hook = ClaudePersonaHook(args.config)
    
    if args.command == "status":
        print("📊 PERSONA STATUS:")
        for persona_id in hook.get_enabled_personas():
            persona = hook.orchestrator.personas[persona_id]
            print(f"✅ {persona.name} ({persona_id})")
    
    elif args.command == "analyze":
        if not args.input:
            print("❌ Please provide input with --input")
            exit(1)
        
        # Read input from file or use directly
        if os.path.exists(args.input):
            with open(args.input, 'r') as f:
                user_input = f.read()
        else:
            user_input = args.input
        
        analysis = hook.orchestrator.analyze_request(user_input)
        print("🔍 ANALYSIS RESULT:")
        print(f"Required personas: {analysis['required_personas']}")
        print(f"Validation level: {analysis['validation_level'].value}")
        print(f"Requires collaboration: {analysis['requires_collaboration']}")
    
    elif args.command == "enhance":
        if not args.input:
            print("❌ Please provide input with --input")
            exit(1)
        
        if os.path.exists(args.input):
            with open(args.input, 'r') as f:
                user_input = f.read()
        else:
            user_input = args.input
        
        enhanced = hook.pre_claude_hook(user_input)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(enhanced)
            print(f"✅ Enhanced prompt saved to {args.output}")
        else:
            print("🔥 ENHANCED PROMPT:")
            print(enhanced)
    
    elif args.command == "test":
        # Simple test
        test_input = "How do I optimize this VRO algorithm for better performance?"
        enhanced = hook.pre_claude_hook(test_input)
        print("🧪 TEST ENHANCEMENT:")
        print(enhanced)

