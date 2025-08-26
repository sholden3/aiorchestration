"""
Business Context: AI Persona management for specialized assistance
Architecture Pattern: Strategy pattern for persona-specific behaviors
Business Logic: Three personas (Sarah, Marcus, Emily) with voting-based conflict resolution
Performance Requirements: Instant persona selection, conflict resolution <100ms
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)

class PersonaType(Enum):
    """Available persona types"""
    SARAH_CHEN = "ai_integration"
    MARCUS_RODRIGUEZ = "systems_performance"  
    EMILY_WATSON = "ux_frontend"

@dataclass
class Persona:
    """Configuration for a single persona"""
    type: PersonaType
    name: str
    expertise: List[str]
    trigger_keywords: List[str]
    system_prompt: str
    priority: int = 1  # For conflict resolution

@dataclass
class PersonaResponse:
    """Response from a persona with confidence"""
    persona: PersonaType
    response: str
    confidence: float
    reasoning: str = ""

class PersonaManager:
    """
    Manages AI personas for specialized assistance
    Business Logic: Auto-suggest based on context, voting for conflicts
    """
    
    def __init__(self):
        """Initialize with three expert personas"""
        self.personas = self._initialize_personas()
        self.active_personas: List[PersonaType] = []
        self.conflict_history: List[Dict] = []
        
        logger.info(f"Initialized {len(self.personas)} personas")
    
    def _initialize_personas(self) -> Dict[PersonaType, Persona]:
        """
        Create the three expert personas with their specializations
        """
        return {
            PersonaType.SARAH_CHEN: Persona(
                type=PersonaType.SARAH_CHEN,
                name="Dr. Sarah Chen",
                expertise=[
                    "Claude API integration",
                    "Token optimization",
                    "AI prompt engineering",
                    "Agent orchestration",
                    "Error handling patterns",
                    "Fallback strategies"
                ],
                trigger_keywords=[
                    "claude", "ai", "token", "prompt", "api", "llm",
                    "optimization", "agent", "orchestration", "gpt",
                    "completion", "embedding", "model", "inference"
                ],
                system_prompt="""You are Dr. Sarah Chen, an AI integration specialist with deep expertise in Claude API optimization.
                
Your focus areas:
- Token usage optimization (target: 65% reduction)
- Intelligent prompt engineering
- Multi-agent orchestration
- Defensive error handling
- API rate limit management
- Response caching strategies

Always:
- Validate assumptions before implementation
- Provide comprehensive error handling
- Optimize for token efficiency
- Document integration patterns
- Consider fallback scenarios""",
                priority=2
            ),
            
            PersonaType.MARCUS_RODRIGUEZ: Persona(
                type=PersonaType.MARCUS_RODRIGUEZ,
                name="Marcus Rodriguez",
                expertise=[
                    "System performance",
                    "Database optimization",
                    "Caching strategies",
                    "Python architecture",
                    "Async programming",
                    "Memory management"
                ],
                trigger_keywords=[
                    "performance", "cache", "database", "optimize", "speed",
                    "memory", "async", "sql", "postgresql", "redis",
                    "latency", "throughput", "scale", "benchmark"
                ],
                system_prompt="""You are Marcus Rodriguez, a systems performance architect specializing in high-performance Python systems.

Your focus areas:
- Cache optimization (target: 90% hit rate)
- Database query optimization
- Async/await patterns
- Memory management
- Performance profiling
- System scalability

Always:
- Measure performance impact
- Avoid premature optimization
- Consider cache invalidation carefully
- Profile before optimizing
- Document architectural decisions""",
                priority=2
            ),
            
            PersonaType.EMILY_WATSON: Persona(
                type=PersonaType.EMILY_WATSON,
                name="Emily Watson",
                expertise=[
                    "User experience",
                    "Angular development",
                    "Electron applications",
                    "UI/UX design",
                    "Terminal interfaces",
                    "Accessibility"
                ],
                trigger_keywords=[
                    "ui", "ux", "frontend", "angular", "electron",
                    "design", "user", "interface", "component", "terminal",
                    "pty", "accessibility", "material", "layout"
                ],
                system_prompt="""You are Emily Watson, a UX and frontend specialist with expertise in Angular and Electron applications.

Your focus areas:
- User experience optimization
- Angular best practices
- Electron desktop applications
- PTY terminal integration
- Material Design implementation
- Cognitive load management

Always:
- Consider user cognitive load
- Ensure intuitive interfaces
- Follow Angular best practices
- Implement responsive designs
- Document component interactions""",
                priority=1
            )
        }
    
    def suggest_persona(self, task_description: str) -> List[PersonaType]:
        """
        Auto-suggest best personas based on task description
        Business Logic: Match keywords, return up to 3 personas
        Performance: <10ms keyword matching
        """
        task_lower = task_description.lower()
        scores = {}
        
        for persona_type, persona in self.personas.items():
            score = 0
            
            # Check keyword matches
            for keyword in persona.trigger_keywords:
                if keyword in task_lower:
                    score += 10
                # Partial match
                elif any(keyword in word for word in task_lower.split()):
                    score += 5
            
            # Check expertise matches
            for expertise in persona.expertise:
                if expertise.lower() in task_lower:
                    score += 15
            
            if score > 0:
                scores[persona_type] = score
        
        # Sort by score and return top 3
        sorted_personas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        suggestions = [persona for persona, _ in sorted_personas[:3]]
        
        # Default to all if no matches
        if not suggestions:
            suggestions = list(self.personas.keys())
        
        logger.debug(f"Suggested personas for '{task_description[:50]}...': {[p.value for p in suggestions]}")
        return suggestions
    
    def resolve_conflict(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Resolve conflicts between multiple persona responses
        Business Logic: Voting based on confidence and priority
        Performance: <100ms resolution
        """
        if not responses:
            return {
                'selected': None,
                'method': 'no_responses',
                'error': 'No responses to resolve'
            }
        
        if len(responses) == 1:
            return {
                'selected': list(responses.values())[0],
                'method': 'single_response',
                'persona': list(responses.keys())[0]
            }
        
        # Calculate confidence for each response
        votes = {}
        
        for persona_str, response in responses.items():
            try:
                persona_type = PersonaType(persona_str)
                persona = self.personas.get(persona_type)
                
                if persona:
                    # Handle tuple responses (response_text, confidence) from tests
                    if isinstance(response, tuple):
                        response_text, confidence = response
                    else:
                        response_text = response
                        # Calculate confidence based on response quality
                        confidence = self._calculate_confidence(response_text, persona)
                    
                    # Apply priority weighting
                    weighted_confidence = confidence * persona.priority
                    
                    votes[persona_str] = {
                        'confidence': confidence,
                        'weighted': weighted_confidence,
                        'response': response_text
                    }
            except Exception as e:
                logger.error(f"Error processing persona {persona_str}: {e}")
        
        if not votes:
            return {
                'selected': list(responses.values())[0],
                'method': 'fallback',
                'error': 'Could not calculate confidence'
            }
        
        # Select winner
        winner = max(votes.items(), key=lambda x: x[1]['weighted'])
        
        # Record conflict for learning
        self.conflict_history.append({
            'responses': len(responses),
            'winner': winner[0],
            'votes': votes
        })
        
        return {
            'selected': winner[1]['response'],
            'method': 'voting',
            'persona': winner[0],
            'winner': winner[0],  # Add winner key for backward compatibility
            'confidence': winner[1]['confidence'],
            'votes': {k: v['weighted'] for k, v in votes.items()},
            'voting_details': votes,  # Add voting_details for test compatibility
            'all_responses': responses
        }
    
    def _calculate_confidence(self, response: str, persona: Persona) -> float:
        """
        Calculate confidence score for a response
        Factors: Response length, technical terms, completeness
        """
        confidence = 0.5  # Base confidence
        
        # Response length (optimal: 100-500 words)
        word_count = len(response.split())
        if 100 <= word_count <= 500:
            confidence += 0.2
        elif word_count > 500:
            confidence += 0.1
        
        # Technical terms from expertise
        technical_matches = sum(
            1 for term in persona.expertise
            if term.lower() in response.lower()
        )
        confidence += min(0.2, technical_matches * 0.05)
        
        # Code blocks or examples
        if "```" in response or "def " in response or "class " in response:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def format_prompt_for_persona(self, persona_type: PersonaType, user_prompt: str) -> str:
        """
        Format user prompt with persona context
        Business Logic: Inject persona expertise and guidelines
        """
        persona = self.personas.get(persona_type)
        if not persona:
            return user_prompt
        
        formatted = f"""{persona.system_prompt}

User Task: {user_prompt}

Please respond with your expertise in: {', '.join(persona.expertise[:3])}

Remember to:
- Focus on your area of specialization
- Provide practical, implementable solutions
- Consider the context of a local development tool
- Optimize for the specific requirements mentioned"""
        
        return formatted
    
    def get_active_personas(self) -> List[Dict[str, Any]]:
        """Get information about currently active personas"""
        return [
            {
                'type': p.value,
                'name': self.personas[p].name,
                'expertise': self.personas[p].expertise[:3]
            }
            for p in self.active_personas
        ]
    
    def activate_persona(self, persona_type: PersonaType):
        """Activate a persona for use"""
        if persona_type not in self.active_personas:
            if len(self.active_personas) >= 3:
                # Remove oldest if at max
                self.active_personas.pop(0)
            self.active_personas.append(persona_type)
            logger.info(f"Activated persona: {persona_type.value}")
    
    def deactivate_persona(self, persona_type: PersonaType):
        """Deactivate a persona"""
        if persona_type in self.active_personas:
            self.active_personas.remove(persona_type)
            logger.info(f"Deactivated persona: {persona_type.value}")