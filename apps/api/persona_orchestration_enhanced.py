"""
Enhanced Persona Orchestration System
Implements full AI persona collaboration with assumption challenging
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

from unified_governance_orchestrator import (
    UnifiedGovernanceOrchestrator,
    PersonaContribution,
    ValidationResult,
    CollaborationResult,
    ConsensusLevel,
    EvidenceType
)
from ai_orchestration_engine import AITask, TaskStatus, TaskPriority


class AssumptionType(Enum):
    """Types of assumptions that can be made"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_STATE = "system_state"
    DATA_QUALITY = "data_quality"


class ValidationStrength(Enum):
    """Strength of validation for assumptions"""
    PROVEN = "proven"  # Backed by concrete evidence
    LIKELY = "likely"  # Supported by data
    POSSIBLE = "possible"  # Reasonable but unverified
    UNLIKELY = "unlikely"  # Contradicted by some evidence
    DISPROVEN = "disproven"  # Contradicted by strong evidence


@dataclass
class Assumption:
    """Represents an assumption made by a persona"""
    assumption_id: str
    persona_name: str
    assumption_type: AssumptionType
    statement: str
    confidence: float
    evidence: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)
    validation_status: ValidationStrength = ValidationStrength.POSSIBLE
    challenges: List['Challenge'] = field(default_factory=list)
    supporting_personas: List[str] = field(default_factory=list)
    opposing_personas: List[str] = field(default_factory=list)


@dataclass
class Challenge:
    """Represents a challenge to an assumption"""
    challenge_id: str
    challenger_persona: str
    assumption_id: str
    challenge_type: str  # "evidence", "logic", "experience", "data"
    argument: str
    counter_evidence: List[Dict[str, Any]]
    strength: float  # 0-1, how strong is the challenge
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass 
class ConsensusDecision:
    """Final decision after personas debate"""
    decision_id: str
    task_id: str
    final_decision: str
    consensus_level: ConsensusLevel
    participating_personas: List[str]
    assumptions_validated: List[str]
    assumptions_rejected: List[str]
    evidence_used: List[Dict[str, Any]]
    dissenting_opinions: List[Dict[str, str]]
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class PersonaOrchestrationEnhanced:
    """Enhanced orchestration system where personas actively challenge each other"""
    
    def __init__(self, governance: UnifiedGovernanceOrchestrator):
        self.governance = governance
        self.assumptions: Dict[str, Assumption] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.decisions: Dict[str, ConsensusDecision] = {}
        self.active_debates: Dict[str, Dict[str, Any]] = {}
        
        # Persona specializations for targeted challenges
        self.persona_specializations = {
            "dr_sarah_chen": {
                "strengths": ["ai_integration", "prompt_engineering", "model_optimization"],
                "challenge_focus": ["performance_assumptions", "ai_behavior", "integration_complexity"]
            },
            "marcus_rodriguez": {
                "strengths": ["system_performance", "database_optimization", "caching"],
                "challenge_focus": ["performance_claims", "scalability_assumptions", "resource_usage"]
            },
            "emily_watson": {
                "strengths": ["user_experience", "interface_design", "accessibility"],
                "challenge_focus": ["user_behavior_assumptions", "usability_claims", "adoption_rates"]
            }
        }
        
        logging.info("Enhanced Persona Orchestration initialized with assumption challenging")
    
    async def process_task_with_full_orchestration(self, task: AITask) -> ConsensusDecision:
        """Process a task with full persona orchestration and assumption validation"""
        
        logging.info(f"Starting full orchestration for task {task.task_id}")
        
        # Phase 1: Initial Analysis - Each persona forms independent opinions
        initial_contributions = await self._gather_initial_opinions(task)
        
        # Phase 2: Assumption Extraction - Identify all assumptions made
        assumptions = await self._extract_assumptions(initial_contributions)
        
        # Phase 3: Challenge Phase - Personas challenge each other's assumptions
        challenges = await self._challenge_assumptions(assumptions)
        
        # Phase 4: Evidence Gathering - Collect evidence for/against assumptions
        evidence_results = await self._gather_evidence(assumptions, challenges)
        
        # Phase 5: Debate Resolution - Resolve conflicts through structured debate
        debate_results = await self._conduct_debate(task, assumptions, challenges, evidence_results)
        
        # Phase 6: Consensus Building - Build consensus or document dissent
        consensus = await self._build_consensus(task, debate_results)
        
        # Phase 7: Final Validation - Validate the decision against evidence
        validated_decision = await self._validate_final_decision(consensus)
        
        # Store the decision
        self.decisions[task.task_id] = validated_decision
        
        # Update task with results
        task.consensus_level = validated_decision.confidence_score
        task.assumptions = [a.statement for a in assumptions.values() if a.validation_status == ValidationStrength.PROVEN]
        task.conflicting_opinions = validated_decision.dissenting_opinions
        
        logging.info(f"Orchestration complete for task {task.task_id}. Consensus: {validated_decision.consensus_level}")
        
        return validated_decision
    
    async def _gather_initial_opinions(self, task: AITask) -> Dict[str, PersonaContribution]:
        """Each persona independently analyzes the task"""
        contributions = {}
        
        for persona_name in self.persona_specializations.keys():
            # Each persona analyzes based on their expertise
            contribution = PersonaContribution(
                persona_name=persona_name,
                contribution_type="initial_analysis",
                content={
                    "task_understanding": f"Analysis of {task.description} from {persona_name} perspective",
                    "proposed_approach": self._generate_approach(persona_name, task),
                    "concerns": self._identify_concerns(persona_name, task),
                    "assumptions": self._identify_initial_assumptions(persona_name, task)
                },
                confidence_score=0.7,  # Initial confidence before validation
                timestamp=datetime.now()
            )
            contributions[persona_name] = contribution
            
        return contributions
    
    async def _extract_assumptions(self, contributions: Dict[str, PersonaContribution]) -> Dict[str, Assumption]:
        """Extract all assumptions from persona contributions"""
        assumptions = {}
        assumption_counter = 0
        
        for persona_name, contribution in contributions.items():
            if isinstance(contribution.content, dict) and "assumptions" in contribution.content:
                for assumption_text in contribution.content["assumptions"]:
                    assumption_id = f"assumption_{assumption_counter}"
                    assumption = Assumption(
                        assumption_id=assumption_id,
                        persona_name=persona_name,
                        assumption_type=self._categorize_assumption(assumption_text),
                        statement=assumption_text,
                        confidence=contribution.confidence_score,
                        evidence=contribution.evidence
                    )
                    assumptions[assumption_id] = assumption
                    assumption_counter += 1
                    
        logging.info(f"Extracted {len(assumptions)} assumptions for validation")
        return assumptions
    
    async def _challenge_assumptions(self, assumptions: Dict[str, Assumption]) -> Dict[str, List[Challenge]]:
        """Each persona challenges others' assumptions"""
        all_challenges = {}
        challenge_counter = 0
        
        for assumption_id, assumption in assumptions.items():
            challenges_for_assumption = []
            
            # Each other persona can challenge
            for persona_name in self.persona_specializations.keys():
                if persona_name != assumption.persona_name:
                    # Check if this persona would challenge this assumption
                    if self._should_challenge(persona_name, assumption):
                        challenge = Challenge(
                            challenge_id=f"challenge_{challenge_counter}",
                            challenger_persona=persona_name,
                            assumption_id=assumption_id,
                            challenge_type=self._determine_challenge_type(persona_name, assumption),
                            argument=self._generate_challenge_argument(persona_name, assumption),
                            counter_evidence=self._find_counter_evidence(persona_name, assumption),
                            strength=self._calculate_challenge_strength(persona_name, assumption)
                        )
                        challenges_for_assumption.append(challenge)
                        challenge_counter += 1
                        
                        # Track the challenge
                        assumption.challenges.append(challenge)
                        assumption.opposing_personas.append(persona_name)
                        
                        logging.info(f"{persona_name} challenges assumption '{assumption.statement}' with strength {challenge.strength}")
            
            all_challenges[assumption_id] = challenges_for_assumption
        
        return all_challenges
    
    async def _gather_evidence(self, assumptions: Dict[str, Assumption], 
                             challenges: Dict[str, List[Challenge]]) -> Dict[str, ValidationResult]:
        """Gather evidence to validate or refute assumptions"""
        evidence_results = {}
        
        for assumption_id, assumption in assumptions.items():
            # Gather supporting evidence
            supporting_evidence = await self._find_supporting_evidence(assumption)
            
            # Gather refuting evidence from challenges
            refuting_evidence = []
            for challenge in challenges.get(assumption_id, []):
                refuting_evidence.extend(challenge.counter_evidence)
            
            # Validate the assumption
            validation = ValidationResult(
                is_valid=len(supporting_evidence) > len(refuting_evidence),
                confidence=self._calculate_evidence_confidence(supporting_evidence, refuting_evidence),
                evidence=supporting_evidence + refuting_evidence,
                issues_found=[c.argument for c in challenges.get(assumption_id, [])],
                persona_name=assumption.persona_name,
                validation_type="assumption_validation",
                confidence_score=self._calculate_evidence_confidence(supporting_evidence, refuting_evidence),
                evidence_quality_score=len(supporting_evidence) / max(1, len(supporting_evidence) + len(refuting_evidence))
            )
            
            # Update assumption validation status
            if validation.confidence > 0.8:
                assumption.validation_status = ValidationStrength.PROVEN
            elif validation.confidence > 0.6:
                assumption.validation_status = ValidationStrength.LIKELY
            elif validation.confidence > 0.4:
                assumption.validation_status = ValidationStrength.POSSIBLE
            elif validation.confidence > 0.2:
                assumption.validation_status = ValidationStrength.UNLIKELY
            else:
                assumption.validation_status = ValidationStrength.DISPROVEN
            
            evidence_results[assumption_id] = validation
            
        return evidence_results
    
    async def _conduct_debate(self, task: AITask, assumptions: Dict[str, Assumption],
                            challenges: Dict[str, List[Challenge]], 
                            evidence_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Conduct structured debate between personas"""
        debate_log = {
            "rounds": [],
            "key_points": [],
            "agreements": [],
            "disagreements": []
        }
        
        # Round 1: Present validated assumptions
        round1 = {
            "round": 1,
            "topic": "Validated Assumptions",
            "presentations": {}
        }
        
        for persona_name in self.persona_specializations.keys():
            persona_assumptions = [a for a in assumptions.values() if a.persona_name == persona_name]
            validated = [a for a in persona_assumptions if a.validation_status in [ValidationStrength.PROVEN, ValidationStrength.LIKELY]]
            round1["presentations"][persona_name] = {
                "validated_assumptions": [a.statement for a in validated],
                "confidence": sum(a.confidence for a in validated) / len(validated) if validated else 0
            }
        
        debate_log["rounds"].append(round1)
        
        # Round 2: Address challenges
        round2 = {
            "round": 2,
            "topic": "Addressing Challenges",
            "rebuttals": {}
        }
        
        for assumption_id, assumption in assumptions.items():
            if assumption.challenges:
                round2["rebuttals"][assumption_id] = {
                    "original_claim": assumption.statement,
                    "defender": assumption.persona_name,
                    "challenges": [
                        {
                            "challenger": c.challenger_persona,
                            "argument": c.argument,
                            "strength": c.strength
                        }
                        for c in assumption.challenges
                    ],
                    "defense": self._generate_defense(assumption, evidence_results.get(assumption_id))
                }
        
        debate_log["rounds"].append(round2)
        
        # Identify agreements and disagreements
        for assumption_id, assumption in assumptions.items():
            if len(assumption.opposing_personas) == 0:
                debate_log["agreements"].append({
                    "assumption": assumption.statement,
                    "agreed_by": list(self.persona_specializations.keys())
                })
            elif len(assumption.opposing_personas) == len(self.persona_specializations) - 1:
                debate_log["disagreements"].append({
                    "assumption": assumption.statement,
                    "proposed_by": assumption.persona_name,
                    "opposed_by": assumption.opposing_personas
                })
        
        return debate_log
    
    async def _build_consensus(self, task: AITask, debate_results: Dict[str, Any]) -> ConsensusDecision:
        """Build consensus from debate results"""
        
        # Calculate consensus level based on agreements
        total_points = len(debate_results.get("agreements", [])) + len(debate_results.get("disagreements", []))
        agreement_points = len(debate_results.get("agreements", []))
        
        if total_points > 0:
            consensus_ratio = agreement_points / total_points
        else:
            consensus_ratio = 0
        
        # Determine consensus level
        if consensus_ratio > 0.9:
            consensus_level = ConsensusLevel.UNANIMOUS
        elif consensus_ratio > 0.75:
            consensus_level = ConsensusLevel.HIGH
        elif consensus_ratio > 0.5:
            consensus_level = ConsensusLevel.MEDIUM
        elif consensus_ratio > 0.25:
            consensus_level = ConsensusLevel.MODERATE
        else:
            consensus_level = ConsensusLevel.LOW
        
        # Create decision
        decision = ConsensusDecision(
            decision_id=f"decision_{task.task_id}",
            task_id=task.task_id,
            final_decision=self._formulate_final_decision(task, debate_results),
            consensus_level=consensus_level,
            participating_personas=list(self.persona_specializations.keys()),
            assumptions_validated=[a["assumption"] for a in debate_results.get("agreements", [])],
            assumptions_rejected=[d["assumption"] for d in debate_results.get("disagreements", [])],
            evidence_used=self._collect_all_evidence(debate_results),
            dissenting_opinions=[
                {
                    "persona": d["proposed_by"],
                    "opinion": d["assumption"],
                    "opposed_by": d["opposed_by"]
                }
                for d in debate_results.get("disagreements", [])
            ],
            confidence_score=consensus_ratio
        )
        
        return decision
    
    async def _validate_final_decision(self, decision: ConsensusDecision) -> ConsensusDecision:
        """Final validation of the consensus decision"""
        
        # Check for critical disagreements
        critical_disagreements = [
            d for d in decision.dissenting_opinions 
            if self._is_critical_disagreement(d)
        ]
        
        if critical_disagreements:
            # Reduce confidence if there are critical disagreements
            decision.confidence_score *= 0.8
            logging.warning(f"Critical disagreements found in decision {decision.decision_id}")
        
        # Validate against evidence
        evidence_score = self._validate_against_evidence(decision)
        decision.confidence_score = (decision.confidence_score + evidence_score) / 2
        
        logging.info(f"Final decision validated with confidence {decision.confidence_score}")
        
        return decision
    
    # Helper methods
    def _generate_approach(self, persona_name: str, task: AITask) -> str:
        """Generate approach based on persona specialization"""
        specialization = self.persona_specializations[persona_name]
        return f"Approach using {specialization['strengths']} for {task.task_type}"
    
    def _identify_concerns(self, persona_name: str, task: AITask) -> List[str]:
        """Identify concerns based on persona focus"""
        specialization = self.persona_specializations[persona_name]
        concerns = []
        for focus in specialization["challenge_focus"]:
            if focus in task.description.lower() or focus in task.task_type.lower():
                concerns.append(f"Concern about {focus}")
        return concerns
    
    def _identify_initial_assumptions(self, persona_name: str, task: AITask) -> List[str]:
        """Generate initial assumptions based on persona perspective"""
        assumptions = []
        
        if persona_name == "dr_sarah_chen":
            assumptions.extend([
                "AI models will maintain consistent performance",
                "Token optimization can achieve 65% reduction",
                "Prompt engineering can improve response quality"
            ])
        elif persona_name == "marcus_rodriguez":
            assumptions.extend([
                "System can handle 1000 concurrent requests",
                "Cache hit rate will exceed 90%",
                "Database queries will complete within 100ms"
            ])
        elif persona_name == "emily_watson":
            assumptions.extend([
                "Users will adapt to new interface within 2 weeks",
                "Response time under 500ms is acceptable",
                "Error messages will be understood by users"
            ])
        
        return assumptions
    
    def _categorize_assumption(self, assumption_text: str) -> AssumptionType:
        """Categorize assumption by type"""
        text_lower = assumption_text.lower()
        
        if any(word in text_lower for word in ["performance", "speed", "latency", "throughput"]):
            return AssumptionType.PERFORMANCE
        elif any(word in text_lower for word in ["security", "vulnerability", "attack", "breach"]):
            return AssumptionType.SECURITY
        elif any(word in text_lower for word in ["user", "interface", "experience", "usability"]):
            return AssumptionType.USER_BEHAVIOR
        elif any(word in text_lower for word in ["technical", "architecture", "design", "implementation"]):
            return AssumptionType.TECHNICAL
        elif any(word in text_lower for word in ["business", "cost", "revenue", "roi"]):
            return AssumptionType.BUSINESS
        else:
            return AssumptionType.SYSTEM_STATE
    
    def _should_challenge(self, persona_name: str, assumption: Assumption) -> bool:
        """Determine if persona should challenge an assumption"""
        specialization = self.persona_specializations[persona_name]
        
        # Challenge if assumption is in persona's challenge focus
        for focus in specialization["challenge_focus"]:
            if focus in assumption.statement.lower():
                return True
        
        # Always challenge assumptions with low confidence
        if assumption.confidence < 0.5:
            return True
        
        # Marcus challenges performance claims
        if persona_name == "marcus_rodriguez" and assumption.assumption_type == AssumptionType.PERFORMANCE:
            return True
        
        # Emily challenges user behavior assumptions
        if persona_name == "emily_watson" and assumption.assumption_type == AssumptionType.USER_BEHAVIOR:
            return True
        
        # Sarah challenges technical assumptions
        if persona_name == "dr_sarah_chen" and assumption.assumption_type == AssumptionType.TECHNICAL:
            return True
        
        return False
    
    def _determine_challenge_type(self, persona_name: str, assumption: Assumption) -> str:
        """Determine type of challenge to make"""
        if assumption.evidence:
            return "evidence"
        elif assumption.assumption_type == AssumptionType.PERFORMANCE:
            return "data"
        elif assumption.assumption_type == AssumptionType.USER_BEHAVIOR:
            return "experience"
        else:
            return "logic"
    
    def _generate_challenge_argument(self, persona_name: str, assumption: Assumption) -> str:
        """Generate challenge argument based on persona expertise"""
        if persona_name == "marcus_rodriguez":
            return f"Based on system metrics, {assumption.statement} may not hold under load conditions"
        elif persona_name == "emily_watson":
            return f"User research suggests {assumption.statement} may not align with actual user behavior"
        elif persona_name == "dr_sarah_chen":
            return f"Technical analysis indicates {assumption.statement} requires additional validation"
        else:
            return f"Evidence suggests {assumption.statement} needs further verification"
    
    def _find_counter_evidence(self, persona_name: str, assumption: Assumption) -> List[Dict[str, Any]]:
        """Find evidence that contradicts the assumption"""
        counter_evidence = []
        
        # Simulate finding counter evidence based on persona expertise
        if assumption.assumption_type == AssumptionType.PERFORMANCE:
            counter_evidence.append({
                "type": "benchmark",
                "data": "Previous benchmarks show 20% lower performance",
                "source": persona_name
            })
        elif assumption.assumption_type == AssumptionType.USER_BEHAVIOR:
            counter_evidence.append({
                "type": "user_study",
                "data": "User studies indicate different behavior patterns",
                "source": persona_name
            })
        
        return counter_evidence
    
    def _calculate_challenge_strength(self, persona_name: str, assumption: Assumption) -> float:
        """Calculate how strong a challenge is"""
        base_strength = 0.5
        
        # Stronger if challenging within expertise
        specialization = self.persona_specializations[persona_name]
        if any(s in assumption.statement.lower() for s in specialization["strengths"]):
            base_strength += 0.3
        
        # Stronger if assumption has no evidence
        if not assumption.evidence:
            base_strength += 0.2
        
        return min(base_strength, 1.0)
    
    async def _find_supporting_evidence(self, assumption: Assumption) -> List[Dict[str, Any]]:
        """Find evidence supporting an assumption"""
        supporting_evidence = []
        
        # Simulate finding supporting evidence
        if assumption.evidence:
            supporting_evidence.extend(assumption.evidence)
        
        # Add mock evidence based on assumption type
        if assumption.assumption_type == AssumptionType.TECHNICAL:
            supporting_evidence.append({
                "type": "documentation",
                "data": "Technical documentation supports this approach",
                "confidence": 0.7
            })
        
        return supporting_evidence
    
    def _calculate_evidence_confidence(self, supporting: List[Dict], refuting: List[Dict]) -> float:
        """Calculate confidence based on evidence balance"""
        if not supporting and not refuting:
            return 0.5
        
        support_weight = len(supporting) * 0.6  # Supporting evidence slightly weighted
        refute_weight = len(refuting) * 0.4
        
        total_weight = support_weight + refute_weight
        if total_weight == 0:
            return 0.5
        
        return support_weight / total_weight
    
    def _generate_defense(self, assumption: Assumption, validation: Optional[ValidationResult]) -> str:
        """Generate defense for a challenged assumption"""
        if validation and validation.is_valid:
            return f"Evidence supports this assumption with {validation.confidence:.1%} confidence"
        else:
            return f"While challenged, this assumption is based on {assumption.persona_name}'s expertise"
    
    def _formulate_final_decision(self, task: AITask, debate_results: Dict[str, Any]) -> str:
        """Formulate the final decision based on debate results"""
        agreements = debate_results.get("agreements", [])
        if agreements:
            return f"Based on consensus, proceed with {task.task_type} using validated assumptions"
        else:
            return f"Proceed with caution on {task.task_type} due to unresolved disagreements"
    
    def _collect_all_evidence(self, debate_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect all evidence used in the debate"""
        all_evidence = []
        
        for round_data in debate_results.get("rounds", []):
            if "presentations" in round_data:
                for persona, data in round_data["presentations"].items():
                    if "evidence" in data:
                        all_evidence.extend(data["evidence"])
        
        return all_evidence
    
    def _is_critical_disagreement(self, disagreement: Dict[str, Any]) -> bool:
        """Determine if a disagreement is critical"""
        # Check if multiple personas oppose
        if isinstance(disagreement.get("opposed_by"), list) and len(disagreement["opposed_by"]) > 1:
            return True
        
        # Check for security or performance related disagreements
        opinion = disagreement.get("opinion", "").lower()
        if any(word in opinion for word in ["security", "performance", "critical", "failure"]):
            return True
        
        return False
    
    def _validate_against_evidence(self, decision: ConsensusDecision) -> float:
        """Validate decision against collected evidence"""
        if not decision.evidence_used:
            return 0.5
        
        # Calculate evidence quality score
        quality_score = sum(
            e.get("confidence", 0.5) 
            for e in decision.evidence_used
        ) / len(decision.evidence_used)
        
        return quality_score


async def demonstrate_enhanced_orchestration():
    """Demonstrate the enhanced persona orchestration with assumption fighting"""
    
    print("="*80)
    print("ENHANCED PERSONA ORCHESTRATION DEMONSTRATION")
    print("Showing how personas challenge each other's assumptions")
    print("="*80)
    
    # Initialize systems
    governance = UnifiedGovernanceOrchestrator()
    orchestrator = PersonaOrchestrationEnhanced(governance)
    
    # Create a complex task that will generate assumptions
    task = AITask(
        task_id="complex_task_001",
        task_type="system_optimization",
        description="Optimize the caching system to achieve 65% token reduction while maintaining <500ms response time",
        input_data={
            "current_metrics": {
                "token_usage": 100000,
                "response_time": 800,
                "cache_hit_rate": 0.6
            },
            "requirements": {
                "token_reduction": 0.65,
                "max_response_time": 500,
                "min_cache_hit_rate": 0.9
            }
        },
        priority=TaskPriority.CRITICAL,
        estimated_tokens=5000,
        requires_governance=True
    )
    
    print(f"\nTask: {task.description}")
    print(f"Priority: {task.priority.value}")
    print(f"Requires Governance: {task.requires_governance}")
    
    # Process with full orchestration
    print("\n" + "="*60)
    print("STARTING FULL ORCHESTRATION")
    print("="*60)
    
    decision = await orchestrator.process_task_with_full_orchestration(task)
    
    # Display results
    print("\n" + "="*60)
    print("ORCHESTRATION RESULTS")
    print("="*60)
    
    print(f"\nFinal Decision: {decision.final_decision}")
    print(f"Consensus Level: {decision.consensus_level.value}")
    print(f"Confidence Score: {decision.confidence_score:.1%}")
    
    print("\nValidated Assumptions:")
    for assumption in decision.assumptions_validated[:3]:
        print(f"  ✓ {assumption}")
    
    print("\nRejected Assumptions:")
    for assumption in decision.assumptions_rejected[:3]:
        print(f"  ✗ {assumption}")
    
    print("\nDissenting Opinions:")
    for opinion in decision.dissenting_opinions[:3]:
        print(f"  - {opinion['persona']}: {opinion['opinion'][:100]}...")
        print(f"    Opposed by: {', '.join(opinion['opposed_by'])}")
    
    print("\n" + "="*60)
    print("ASSUMPTION VALIDATION DETAILS")
    print("="*60)
    
    # Show some assumption challenges
    for assumption_id, assumption in list(orchestrator.assumptions.items())[:3]:
        print(f"\nAssumption: {assumption.statement}")
        print(f"  Proposed by: {assumption.persona_name}")
        print(f"  Validation Status: {assumption.validation_status.value}")
        print(f"  Challenges:")
        for challenge in assumption.challenges[:2]:
            print(f"    - {challenge.challenger_persona}: {challenge.argument[:100]}...")
            print(f"      Challenge Strength: {challenge.strength:.1%}")


if __name__ == "__main__":
    asyncio.run(demonstrate_enhanced_orchestration())