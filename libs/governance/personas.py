"""
Data-Driven Persona Management System

Loads persona definitions from YAML configuration and provides
intelligent consultation capabilities for governance decisions.

Author: Alex Novak & Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import yaml
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PersonaProfile:
    """Data structure for a persona profile."""
    name: str
    version: str
    role: str
    persona_type: str  # 'core' or 'specialist'
    domain: Optional[str] = None
    always_present: bool = False
    expertise: Dict[str, List[str]] = field(default_factory=dict)
    trigger_keywords: List[str] = field(default_factory=list)
    consultation_patterns: List[Dict] = field(default_factory=list)
    crisis_experience: List[Dict] = field(default_factory=list)
    decision_framework: Dict[str, Any] = field(default_factory=dict)
    invocation_triggers: List[str] = field(default_factory=list)


class PersonaManager:
    """
    Manages persona consultations for governance intelligence.
    
    Loads persona definitions from YAML configuration and provides
    methods to consult personas based on context and triggers.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the PersonaManager with configuration.
        
        Args:
            config_path: Path to personas.yaml configuration file
        """
        self.config_path = config_path or Path("libs/governance/personas.yaml")
        self.config: Dict = {}
        self.personas: Dict[str, PersonaProfile] = {}
        self.core_personas: List[str] = []
        self.specialist_personas: List[str] = []
        self.invocation_rules: Dict = {}
        self.consultation_history: List[Dict] = []
        
        self._load_configuration()
    
    def _load_configuration(self):
        """Load persona configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Personas config not found at {self.config_path}")
                self._use_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Parse core personas
            for persona_id, persona_data in self.config.get('core_personas', {}).items():
                profile = self._create_persona_profile(persona_data, 'core')
                self.personas[profile.name] = profile
                self.core_personas.append(profile.name)
            
            # Parse specialist personas
            for persona_id, persona_data in self.config.get('specialist_personas', {}).items():
                profile = self._create_persona_profile(persona_data, 'specialist')
                self.personas[profile.name] = profile
                self.specialist_personas.append(profile.name)
            
            # Load invocation rules
            self.invocation_rules = self.config.get('invocation_rules', {})
            
            logger.info(f"Loaded {len(self.personas)} personas from configuration")
            
        except Exception as e:
            logger.error(f"Error loading persona configuration: {e}")
            self._use_default_config()
    
    def _create_persona_profile(self, data: Dict, persona_type: str) -> PersonaProfile:
        """Create a PersonaProfile from configuration data."""
        return PersonaProfile(
            name=data.get('name', 'Unknown'),
            version=data.get('version', '1.0'),
            role=data.get('role', 'Specialist'),
            persona_type=persona_type,
            domain=data.get('domain'),
            always_present=data.get('always_present', False),
            expertise=data.get('expertise', {}),
            trigger_keywords=data.get('trigger_keywords', []),
            consultation_patterns=data.get('consultation_patterns', []),
            crisis_experience=data.get('crisis_experience', []),
            decision_framework=data.get('decision_framework', {}),
            invocation_triggers=data.get('invocation_triggers', [])
        )
    
    def _use_default_config(self):
        """Use minimal default configuration if file not found."""
        logger.info("Using default persona configuration")
        
        # Create minimal core personas
        self.personas['Alex Novak'] = PersonaProfile(
            name='Alex Novak',
            version='3.0',
            role='Frontend Architect',
            persona_type='core',
            always_present=True,
            expertise={'primary': ['Frontend', 'Electron', 'Angular']},
            trigger_keywords=['frontend', 'ui', 'electron']
        )
        
        self.personas['Dr. Sarah Chen'] = PersonaProfile(
            name='Dr. Sarah Chen',
            version='1.2',
            role='Backend Architect',
            persona_type='core',
            always_present=True,
            expertise={'primary': ['Backend', 'Python', 'Database']},
            trigger_keywords=['backend', 'api', 'database']
        )
        
        self.core_personas = ['Alex Novak', 'Dr. Sarah Chen']
    
    async def consult(
        self,
        persona_name: str,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Consult a specific persona for guidance.
        
        Args:
            persona_name: Name of the persona to consult
            question: Question for the persona
            context: Context information for the consultation
            
        Returns:
            Persona's guidance as a formatted string
        """
        if persona_name not in self.personas:
            return f"Persona '{persona_name}' not found. Available: {', '.join(self.personas.keys())}"
        
        persona = self.personas[persona_name]
        
        # Record consultation
        self._record_consultation(persona_name, question, context)
        
        # Generate response based on persona's expertise and patterns
        response = self._generate_persona_response(persona, question, context)
        
        return response
    
    def _generate_persona_response(
        self,
        persona: PersonaProfile,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate a response based on persona's profile and expertise."""
        
        # Check if question matches any expertise areas
        relevance_score = self._calculate_relevance(persona, question, context)
        
        if relevance_score < 0.3:
            return (f"{persona.name}: This is outside my primary expertise. "
                   f"Consider consulting a specialist in this area.")
        
        # Build response based on persona's profile
        response_parts = []
        
        # Add greeting based on persona style
        response_parts.append(f"{persona.name} ({persona.role}):")
        
        # Check against decision framework
        if persona.decision_framework:
            for key, principle in persona.decision_framework.items():
                if any(keyword in question.lower() or keyword in str(context).lower() 
                      for keyword in key.lower().split('_')):
                    response_parts.append(f"\n[CHECK] {principle}")
        
        # Check against crisis experience
        relevant_experience = self._find_relevant_experience(persona, question, context)
        if relevant_experience:
            response_parts.append(f"\n[EXPERIENCE] From past incidents: {relevant_experience}")
        
        # Add specific recommendations based on patterns
        recommendations = self._generate_recommendations(persona, question, context)
        if recommendations:
            response_parts.append(f"\n[RECOMMENDATIONS]:")
            for rec in recommendations:
                response_parts.append(f"  - {rec}")
        
        # Add confidence level
        response_parts.append(f"\n[CONFIDENCE]: {relevance_score:.0%}")
        
        return "\n".join(response_parts)
    
    def _calculate_relevance(
        self,
        persona: PersonaProfile,
        question: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate how relevant this persona is to the question."""
        score = 0.0
        total_checks = 0
        
        # Check trigger keywords
        question_lower = question.lower()
        context_str = str(context).lower()
        
        for keyword in persona.trigger_keywords:
            total_checks += 1
            if keyword.lower() in question_lower or keyword.lower() in context_str:
                score += 1.0
        
        # Check consultation patterns
        if 'file_path' in context:
            file_path = context['file_path']
            for pattern in persona.consultation_patterns:
                total_checks += 1
                if self._matches_pattern(file_path, pattern.get('pattern', '')):
                    score += pattern.get('confidence', 0.5)
        
        # Check invocation triggers
        for trigger in persona.invocation_triggers:
            total_checks += 1
            if trigger.lower() in question_lower:
                score += 0.8
        
        # Calculate final score
        if total_checks == 0:
            return 0.5  # Default medium relevance if no checks
        
        return min(score / total_checks, 1.0)
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a glob-like pattern."""
        # Convert glob pattern to regex
        pattern_regex = pattern.replace('*', '.*').replace('?', '.')
        try:
            return bool(re.match(pattern_regex, text))
        except:
            return False
    
    def _find_relevant_experience(
        self,
        persona: PersonaProfile,
        question: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Find relevant crisis experience from persona's history."""
        for experience in persona.crisis_experience:
            incident = experience.get('incident', '').lower()
            lesson = experience.get('lesson', '')
            practice = experience.get('applied_practice', '')
            
            # Check if incident keywords appear in question/context
            if any(word in question.lower() or word in str(context).lower() 
                  for word in incident.split()):
                return f"{lesson} -- Applied: {practice}" if practice else lesson
        
        return None
    
    def _generate_recommendations(
        self,
        persona: PersonaProfile,
        question: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate specific recommendations based on persona expertise."""
        recommendations = []
        
        # Security persona specific checks
        if persona.name == "Morgan Hayes" and 'security_patterns' in persona.__dict__:
            if 'command' in context:
                cmd = context['command']
                # Check for dangerous patterns
                for pattern in persona.security_patterns.get('dangerous_commands', []):
                    if pattern in cmd:
                        recommendations.append(f"[DANGER] Command contains '{pattern}'")
                        recommendations.append("Use safer alternative or add validation")
        
        # Database persona specific checks
        if persona.name == "Dr. Jamie Rodriguez":
            if 'query' in context or 'database' in question.lower():
                recommendations.append("Always use parameterized queries")
                recommendations.append("Check execution plan with EXPLAIN")
                recommendations.append("Monitor connection pool usage")
        
        # Performance persona specific checks
        if persona.name == "Taylor Williams":
            if 'performance' in question.lower() or 'memory' in question.lower():
                recommendations.append("Profile before optimizing")
                recommendations.append("Measure baseline metrics first")
                recommendations.append("Consider caching strategy")
        
        # Real-time persona specific checks
        if persona.name == "Jordan Lee":
            if 'websocket' in question.lower() or 'realtime' in context:
                recommendations.append("Implement exponential backoff for reconnection")
                recommendations.append("Add connection pooling with limits")
                recommendations.append("Monitor backpressure indicators")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def determine_relevant_personas(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """
        Determine which personas are relevant for an operation.
        
        Args:
            operation: Type of operation being performed
            context: Context of the operation
            
        Returns:
            List of (persona_name, confidence_score) tuples
        """
        relevant = []
        
        # Always include core personas for major decisions
        if 'architecture' in operation.lower() or 'critical' in str(context).lower():
            for persona_name in self.core_personas:
                relevant.append((persona_name, 0.9))
        
        # Check automatic triggers from configuration
        for trigger in self.invocation_rules.get('automatic_triggers', []):
            condition = trigger.get('condition', '')
            personas = trigger.get('personas', [])
            confidence = trigger.get('confidence', 0.8)
            
            # Evaluate condition (simplified evaluation)
            if self._evaluate_condition(condition, operation, context):
                for persona_name in personas:
                    if persona_name in self.personas:
                        relevant.append((persona_name, confidence))
        
        # Check each persona's relevance
        for persona_name, persona in self.personas.items():
            if persona_name not in [r[0] for r in relevant]:  # Not already added
                relevance = self._calculate_relevance(persona, operation, context)
                if relevance > 0.5:  # Threshold for inclusion
                    relevant.append((persona_name, relevance))
        
        # Sort by confidence and limit to max concurrent
        relevant.sort(key=lambda x: x[1], reverse=True)
        max_concurrent = self.config.get('metadata', {}).get('max_concurrent_personas', 3)
        
        return relevant[:max_concurrent]
    
    def _evaluate_condition(self, condition: str, operation: str, context: Dict) -> bool:
        """Simple condition evaluator for invocation rules."""
        try:
            # Create safe evaluation context
            safe_context = {
                'operation': operation,
                'context': context,
                'file_path': context.get('file_path', ''),
            }
            
            # Simple string matching for now (can be enhanced)
            if ' in ' in condition:
                parts = condition.split(' in ')
                if len(parts) == 2:
                    needle = parts[0].strip().strip("'\"")
                    haystack = parts[1].strip()
                    if haystack in safe_context:
                        return needle in str(safe_context[haystack])
            
            if '.endswith(' in condition:
                # Handle file_path.endswith() checks
                if 'file_path' in context:
                    match = re.search(r"\.endswith\(['\"](.+?)['\"]\)", condition)
                    if match:
                        suffix = match.group(1)
                        return context['file_path'].endswith(suffix)
            
            if ' == ' in condition:
                parts = condition.split(' == ')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    if left in safe_context:
                        return str(safe_context[left]) == right
            
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
        
        return False
    
    def _record_consultation(self, persona_name: str, question: str, context: Dict):
        """Record a consultation for audit purposes."""
        self.consultation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'persona': persona_name,
            'question': question,
            'context_summary': {k: str(v)[:100] for k, v in context.items()}
        })
        
        # Keep only last 1000 consultations in memory
        if len(self.consultation_history) > 1000:
            self.consultation_history = self.consultation_history[-1000:]
    
    async def initialize(self):
        """Initialize the persona manager (async for compatibility)."""
        # Reload configuration if needed
        self._load_configuration()
        logger.info(f"PersonaManager initialized with {len(self.personas)} personas")
    
    def get_all_personas(self) -> Dict[str, Dict]:
        """Get all persona profiles as dictionary."""
        return {
            name: {
                'name': p.name,
                'version': p.version,
                'role': p.role,
                'type': p.persona_type,
                'domain': p.domain,
                'expertise': p.expertise,
                'always_present': p.always_present
            }
            for name, p in self.personas.items()
        }
    
    def get_consultation_history(self, limit: int = 100) -> List[Dict]:
        """Get recent consultation history."""
        return self.consultation_history[-limit:]