#!/usr/bin/env python
"""
Dynamic Multi-Persona Governance System v6.0
Intelligent Delegation with Universal Quality Standards
Works with any number of expert personas without prior knowledge
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from pathlib import Path

class ValidationLevel(Enum):
    """Validation requirement levels"""
    CRITICAL = "critical"  # Must pass all validations
    HIGH = "high"  # Must pass most validations
    MEDIUM = "medium"  # Should pass key validations
    LOW = "low"  # Basic validation only

@dataclass
class PersonaExpertise:
    """Dynamic persona expertise declaration"""
    name: str
    primary_domain: str
    secondary_domains: List[str] = field(default_factory=list)
    analysis_strengths: List[str] = field(default_factory=list)
    evidence_capabilities: List[str] = field(default_factory=list)
    cross_domain_knowledge: List[str] = field(default_factory=list)
    blind_spots: List[str] = field(default_factory=list)
    validation_methods: Dict[str, List[str]] = field(default_factory=dict)
    
    def get_expertise_score(self, domain: str) -> float:
        """Calculate expertise score for a domain"""
        if domain == self.primary_domain:
            return 1.0
        elif domain in self.secondary_domains:
            return 0.7
        elif domain in self.cross_domain_knowledge:
            return 0.4
        else:
            return 0.1  # Minimal score for cross-validation purposes

@dataclass
class ValidationChallenge:
    """Cross-validation challenge assignment"""
    claim_id: str
    claim_text: str
    primary_analyst: str
    evidence_validator: str
    assumption_challenger: str
    implementation_validator: str
    status: str = "pending"
    challenges: List[Dict[str, Any]] = field(default_factory=list)
    resolution: Optional[str] = None

@dataclass
class DelegationAssignment:
    """Task delegation assignment"""
    task_id: str
    task_description: str
    primary_owner: str
    supporting_personas: List[str] = field(default_factory=list)
    validators: List[str] = field(default_factory=list)
    evidence_required: List[str] = field(default_factory=list)
    status: str = "assigned"

class DynamicPersonaGovernance:
    """Adaptive governance for unknown personas"""
    
    def __init__(self):
        self.personas: Dict[str, PersonaExpertise] = {}
        self.domains_discovered: Set[str] = set()
        self.delegation_matrix: Dict[str, DelegationAssignment] = {}
        self.validation_challenges: List[ValidationChallenge] = []
        self.universal_standards = self._initialize_universal_standards()
        self.quality_violations: List[Dict[str, Any]] = []
        
    def _initialize_universal_standards(self) -> Dict[str, Any]:
        """Initialize domain-agnostic quality standards"""
        return {
            "evidence_requirements": {
                "code_inspection": {
                    "enabled": True,
                    "require_line_numbers": True,
                    "require_file_paths": True
                },
                "command_execution": {
                    "enabled": True,
                    "require_actual_output": True,
                    "no_theoretical_results": True
                },
                "metrics_measurement": {
                    "enabled": True,
                    "require_tools": True,
                    "no_estimates": True
                },
                "assumption_validation": {
                    "enabled": True,
                    "require_peer_review": True,
                    "cross_domain_challenge": True
                }
            },
            "forbidden_behaviors": [
                "magic_variables",
                "fake_metrics",
                "theoretical_claims",
                "unchallenged_assumptions",
                "domain_isolation"
            ],
            "violation_patterns": {
                "magic_variables": [r"localhost", r"127\.0\.0\.1", r"hardcoded", r"TODO", r"FIXME"],
                "fake_metrics": [r"should\s+be", r"approximately", r"estimated", r"theoretical"],
                "assumptions": [r"assume", r"probably", r"should\s+work", r"likely", r"expect"]
            }
        }
    
    async def register_persona(self, expertise_declaration: Dict[str, Any]) -> PersonaExpertise:
        """Register a new persona with their expertise"""
        persona = PersonaExpertise(
            name=expertise_declaration['name'],
            primary_domain=expertise_declaration['primary_domain'],
            secondary_domains=expertise_declaration.get('secondary_domains', []),
            analysis_strengths=expertise_declaration.get('analysis_strengths', []),
            evidence_capabilities=expertise_declaration.get('evidence_capabilities', []),
            cross_domain_knowledge=expertise_declaration.get('cross_domain_knowledge', []),
            blind_spots=expertise_declaration.get('blind_spots', []),
            validation_methods=expertise_declaration.get('validation_methods', {})
        )
        
        # Register persona
        self.personas[persona.name] = persona
        
        # Discover domains
        self.domains_discovered.add(persona.primary_domain)
        self.domains_discovered.update(persona.secondary_domains)
        
        print(f"[REGISTERED] {persona.name} - Primary: {persona.primary_domain}")
        
        return persona
    
    def generate_delegation_matrix(self) -> Dict[str, Any]:
        """Generate intelligent delegation matrix based on registered personas"""
        matrix = {
            "domains": {},
            "cross_validation": {},
            "delegation_rules": {}
        }
        
        # Map domains to experts
        for domain in self.domains_discovered:
            experts = []
            for persona_name, persona in self.personas.items():
                score = persona.get_expertise_score(domain)
                if score > 0:
                    experts.append({
                        "name": persona_name,
                        "score": score,
                        "role": self._determine_role(score)
                    })
            
            # Sort by expertise score
            experts.sort(key=lambda x: x['score'], reverse=True)
            
            if experts:
                matrix["domains"][domain] = {
                    "primary_expert": experts[0]['name'] if experts else None,
                    "secondary_support": [e['name'] for e in experts[1:3] if e['score'] > 0.3],
                    "validators": [e['name'] for e in experts if e['score'] <= 0.5]
                }
        
        # Generate cross-validation assignments
        for persona_name, persona in self.personas.items():
            validators = self._find_cross_domain_validators(persona)
            matrix["cross_validation"][persona_name] = {
                "must_validate": self._find_validation_targets(persona),
                "validated_by": validators,
                "evidence_required": persona.blind_spots
            }
        
        # Create delegation rules
        matrix["delegation_rules"] = self._generate_delegation_rules()
        
        return matrix
    
    def _determine_role(self, expertise_score: float) -> str:
        """Determine role based on expertise score"""
        if expertise_score >= 0.9:
            return "primary_expert"
        elif expertise_score >= 0.6:
            return "supporting_expert"
        elif expertise_score >= 0.3:
            return "contributor"
        else:
            return "validator"
    
    def _find_cross_domain_validators(self, persona: PersonaExpertise) -> List[str]:
        """Find personas from different domains for validation"""
        validators = []
        for other_name, other_persona in self.personas.items():
            if other_name != persona.name:
                # Prefer validators from completely different domains
                if other_persona.primary_domain not in [persona.primary_domain] + persona.secondary_domains:
                    validators.append(other_name)
        
        # If not enough different-domain validators, add some from secondary domains
        if len(validators) < 2:
            for other_name, other_persona in self.personas.items():
                if other_name != persona.name and other_name not in validators:
                    validators.append(other_name)
                    if len(validators) >= 2:
                        break
        
        return validators[:3]  # Return up to 3 validators
    
    def _find_validation_targets(self, persona: PersonaExpertise) -> List[str]:
        """Find what domains this persona should validate"""
        targets = []
        
        # Validate in areas where they have some knowledge but aren't experts
        for domain in self.domains_discovered:
            score = persona.get_expertise_score(domain)
            if 0.1 < score < 0.7:  # Not primary expert but has some knowledge
                targets.append(domain)
        
        return targets
    
    def _generate_delegation_rules(self) -> Dict[str, Any]:
        """Generate intelligent delegation rules"""
        return {
            "task_assignment": {
                "primary_owner": "Highest expertise score in relevant domain",
                "supporting_team": "Personas with score > 0.5 in domain",
                "validators": "Personas from different primary domains",
                "evidence_providers": "Personas with measurement capabilities"
            },
            "validation_requirements": {
                "all_claims": "Must be validated by at least one cross-domain persona",
                "performance_claims": "Must include actual measurements",
                "implementation_claims": "Must include executed code/commands",
                "assumption_statements": "Must be challenged by 2+ personas"
            },
            "escalation_path": {
                "disagreement": "Require evidence from all parties",
                "unresolved": "Aggregate votes weighted by expertise",
                "critical_decisions": "Require unanimous agreement"
            }
        }
    
    async def delegate_task(self, task_description: str, context: Dict[str, Any] = None) -> DelegationAssignment:
        """Intelligently delegate a task based on expertise"""
        # Analyze task to determine required domains
        required_domains = self._analyze_task_domains(task_description, context)
        
        # Find best personas for the task
        primary_owner = None
        supporting_personas = []
        validators = []
        
        for domain in required_domains:
            domain_experts = []
            for persona_name, persona in self.personas.items():
                score = persona.get_expertise_score(domain)
                if score > 0:
                    domain_experts.append((persona_name, score))
            
            domain_experts.sort(key=lambda x: x[1], reverse=True)
            
            if domain_experts and not primary_owner:
                primary_owner = domain_experts[0][0]
            
            for expert, score in domain_experts[1:]:
                if score > 0.5 and expert not in supporting_personas:
                    supporting_personas.append(expert)
        
        # Add cross-domain validators
        if primary_owner:
            validators = self._find_cross_domain_validators(self.personas[primary_owner])
        
        # Create assignment
        assignment = DelegationAssignment(
            task_id=f"task_{datetime.now().timestamp()}",
            task_description=task_description,
            primary_owner=primary_owner or "unassigned",
            supporting_personas=supporting_personas,
            validators=validators,
            evidence_required=self._determine_evidence_requirements(task_description)
        )
        
        self.delegation_matrix[assignment.task_id] = assignment
        
        return assignment
    
    def _analyze_task_domains(self, task_description: str, context: Optional[Dict] = None) -> List[str]:
        """Analyze task to determine required domains"""
        detected_domains = []
        task_lower = task_description.lower()
        
        # Check each persona's keywords
        for persona in self.personas.values():
            # Check primary domain keywords
            domain_keywords = persona.primary_domain.lower().split()
            for keyword in domain_keywords:
                if keyword in task_lower:
                    if persona.primary_domain not in detected_domains:
                        detected_domains.append(persona.primary_domain)
            
            # Check analysis strengths
            for strength in persona.analysis_strengths:
                if any(word in task_lower for word in strength.lower().split()):
                    if persona.primary_domain not in detected_domains:
                        detected_domains.append(persona.primary_domain)
        
        # If no domains detected, include all for comprehensive analysis
        if not detected_domains:
            detected_domains = list(self.domains_discovered)
        
        return detected_domains
    
    def _determine_evidence_requirements(self, task_description: str) -> List[str]:
        """Determine what evidence is required for the task"""
        requirements = []
        task_lower = task_description.lower()
        
        evidence_keywords = {
            "performance": ["benchmark", "measurement", "metrics"],
            "implementation": ["code", "actual output", "execution results"],
            "testing": ["test results", "validation output", "coverage report"],
            "security": ["vulnerability scan", "security audit", "compliance check"],
            "ui": ["screenshots", "user feedback", "accessibility report"]
        }
        
        for evidence_type, keywords in evidence_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                requirements.append(evidence_type)
        
        # Always require basic evidence
        if not requirements:
            requirements = ["code inspection", "execution results", "validation"]
        
        return requirements
    
    async def create_validation_challenge(self, claim: str, claimant: str) -> ValidationChallenge:
        """Create cross-validation challenge for a claim"""
        # Find validators
        claimant_persona = self.personas.get(claimant)
        if not claimant_persona:
            raise ValueError(f"Unknown persona: {claimant}")
        
        validators = self._find_cross_domain_validators(claimant_persona)
        
        # Assign validation roles
        challenge = ValidationChallenge(
            claim_id=f"claim_{datetime.now().timestamp()}",
            claim_text=claim,
            primary_analyst=claimant,
            evidence_validator=validators[0] if validators else "none",
            assumption_challenger=validators[1] if len(validators) > 1 else "none",
            implementation_validator=validators[2] if len(validators) > 2 else validators[0] if validators else "none"
        )
        
        # Add mandatory challenge questions
        challenge.challenges = [
            {"type": "evidence", "question": "What actual evidence supports this claim?"},
            {"type": "assumption", "question": "What assumptions are you making here?"},
            {"type": "alternative", "question": "What other explanations could account for this?"},
            {"type": "implementation", "question": "How would you actually verify this?"},
            {"type": "impact", "question": "What happens if this assumption is wrong?"}
        ]
        
        self.validation_challenges.append(challenge)
        
        return challenge
    
    async def validate_quality(self, content: str, author: str) -> Dict[str, Any]:
        """Validate content against universal quality standards"""
        violations = []
        
        # Check for forbidden patterns
        for behavior, patterns in self.universal_standards['violation_patterns'].items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append({
                        "type": behavior,
                        "pattern": pattern,
                        "matches": matches[:5],  # First 5 matches
                        "author": author,
                        "severity": "high" if behavior in ["magic_variables", "fake_metrics"] else "medium"
                    })
        
        # Check for evidence
        has_code_reference = bool(re.search(r'\w+\.\w+:\d+', content))  # file:line format
        has_command_output = bool(re.search(r'(\$|>)\s*\w+.*\n.*', content))  # command with output
        has_metrics = bool(re.search(r'\d+(\.\d+)?\s*(ms|%|MB|GB|ops)', content))  # metrics with units
        
        evidence_score = sum([has_code_reference, has_command_output, has_metrics]) / 3
        
        # Store violations
        if violations:
            self.quality_violations.extend(violations)
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "evidence_score": evidence_score,
            "requires_validation": evidence_score < 0.5,
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_collaboration_protocol(self) -> Dict[str, Any]:
        """Generate collaborative analysis protocol"""
        return {
            "phases": {
                "1_identification": {
                    "action": "All personas complete expertise identification",
                    "output": "PersonaExpertise declarations",
                    "validation": "System confirms all personas registered"
                },
                "2_matrix_creation": {
                    "action": "System generates delegation matrix",
                    "output": "Domain expertise mapping and cross-validation assignments",
                    "validation": "All domains have assigned experts"
                },
                "3_task_analysis": {
                    "action": "All personas analyze task for their domain relevance",
                    "output": "Domain-specific analysis points",
                    "validation": "Each persona identifies their contribution areas"
                },
                "4_delegation": {
                    "action": "System assigns primary and supporting roles",
                    "output": "DelegationAssignment with clear responsibilities",
                    "validation": "All personas acknowledge their roles"
                },
                "5_execution": {
                    "action": "Personas execute assigned analyses",
                    "output": "Domain-specific findings with evidence",
                    "validation": "Quality standards met, evidence provided"
                },
                "6_cross_validation": {
                    "action": "Cross-domain validation challenges",
                    "output": "Validated or challenged claims",
                    "validation": "All claims have been reviewed"
                },
                "7_synthesis": {
                    "action": "Collaborative synthesis of findings",
                    "output": "Consensus report with evidence",
                    "validation": "All personas agree or dissent documented"
                }
            },
            "checkpoints": {
                "before_analysis": "Expertise registered, matrix created",
                "during_analysis": "Evidence being collected, assumptions documented",
                "after_analysis": "Cross-validation complete, consensus achieved"
            }
        }
    
    def get_governance_status(self) -> Dict[str, Any]:
        """Get current governance system status"""
        return {
            "registered_personas": len(self.personas),
            "discovered_domains": list(self.domains_discovered),
            "active_delegations": len(self.delegation_matrix),
            "pending_challenges": len([c for c in self.validation_challenges if c.status == "pending"]),
            "quality_violations": len(self.quality_violations),
            "delegation_matrix": self.generate_delegation_matrix(),
            "collaboration_protocol": self.generate_collaboration_protocol()
        }

# Demonstration
async def demonstrate_dynamic_governance():
    """Demonstrate the dynamic governance system"""
    print("="*60)
    print("DYNAMIC MULTI-PERSONA GOVERNANCE SYSTEM v6.0")
    print("="*60)
    
    governance = DynamicPersonaGovernance()
    
    # Phase 1: Register unknown personas
    print("\nPHASE 1: PERSONA REGISTRATION")
    print("-"*40)
    
    # Simulate various expert personas registering
    personas_to_register = [
        {
            "name": "Dr. Neural Network",
            "primary_domain": "Deep Learning",
            "secondary_domains": ["Computer Vision", "NLP"],
            "analysis_strengths": ["model architecture", "training optimization"],
            "evidence_capabilities": ["tensorboard metrics", "confusion matrices"],
            "blind_spots": ["frontend", "deployment"]
        },
        {
            "name": "Captain Database",
            "primary_domain": "Data Engineering",
            "secondary_domains": ["ETL", "Data Warehousing"],
            "analysis_strengths": ["query optimization", "schema design"],
            "evidence_capabilities": ["query plans", "performance benchmarks"],
            "blind_spots": ["UI/UX", "machine learning"]
        },
        {
            "name": "Security Sentinel",
            "primary_domain": "Cybersecurity",
            "secondary_domains": ["Compliance", "Cryptography"],
            "analysis_strengths": ["vulnerability assessment", "threat modeling"],
            "evidence_capabilities": ["penetration testing", "security scans"],
            "blind_spots": ["user experience", "performance optimization"]
        }
    ]
    
    for persona_data in personas_to_register:
        await governance.register_persona(persona_data)
    
    # Phase 2: Generate delegation matrix
    print("\nPHASE 2: DELEGATION MATRIX GENERATION")
    print("-"*40)
    
    matrix = governance.generate_delegation_matrix()
    print(f"Domains discovered: {matrix['domains'].keys()}")
    
    for domain, experts in matrix['domains'].items():
        print(f"\n{domain}:")
        print(f"  Primary: {experts['primary_expert']}")
        print(f"  Support: {experts['secondary_support']}")
        print(f"  Validators: {experts['validators']}")
    
    # Phase 3: Delegate a task
    print("\nPHASE 3: TASK DELEGATION")
    print("-"*40)
    
    task = "Implement a secure machine learning pipeline with real-time data processing"
    assignment = await governance.delegate_task(task)
    
    print(f"Task: {task}")
    print(f"Primary Owner: {assignment.primary_owner}")
    print(f"Supporting Team: {assignment.supporting_personas}")
    print(f"Validators: {assignment.validators}")
    print(f"Evidence Required: {assignment.evidence_required}")
    
    # Phase 4: Create validation challenge
    print("\nPHASE 4: VALIDATION CHALLENGE")
    print("-"*40)
    
    claim = "The neural network achieves 95% accuracy on test data"
    challenge = await governance.create_validation_challenge(claim, "Dr. Neural Network")
    
    print(f"Claim: {claim}")
    print(f"Evidence Validator: {challenge.evidence_validator}")
    print(f"Assumption Challenger: {challenge.assumption_challenger}")
    print(f"Implementation Validator: {challenge.implementation_validator}")
    
    # Phase 5: Quality validation
    print("\nPHASE 5: QUALITY VALIDATION")
    print("-"*40)
    
    content_samples = [
        "The model should work with approximately 90% accuracy",  # Fake metric
        "Set learning_rate = 0.001 # hardcoded for now",  # Magic variable
        "Based on file model.py:42, the accuracy is 94.3%",  # Good evidence
    ]
    
    for content in content_samples:
        result = await governance.validate_quality(content, "Dr. Neural Network")
        print(f"\nContent: '{content[:50]}...'")
        print(f"Valid: {result['valid']}")
        print(f"Evidence Score: {result['evidence_score']:.1%}")
        if result['violations']:
            print(f"Violations: {[v['type'] for v in result['violations']]}")
    
    # Final status
    print("\n" + "="*60)
    print("GOVERNANCE STATUS")
    print("="*60)
    
    status = governance.get_governance_status()
    print(f"Registered Personas: {status['registered_personas']}")
    print(f"Discovered Domains: {len(status['discovered_domains'])}")
    print(f"Active Delegations: {status['active_delegations']}")
    print(f"Pending Challenges: {status['pending_challenges']}")
    print(f"Quality Violations: {status['quality_violations']}")

if __name__ == "__main__":
    asyncio.run(demonstrate_dynamic_governance())