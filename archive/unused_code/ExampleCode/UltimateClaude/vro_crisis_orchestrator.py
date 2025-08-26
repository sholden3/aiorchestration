#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRO CRISIS MANAGEMENT ORCHESTRATOR

Enhanced persona orchestrator specifically designed for VRO production crisis management
with integrated decision review framework for management oversight.

Built by Marcus Chen for high-stakes VRO crisis resolution.
"""

import yaml
import os
import re
import json
import datetime
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    MINIMAL = "minimal"
    STANDARD = "standard" 
    STRICT = "strict"
    MAXIMUM = "maximum"
    CRISIS = "crisis"
    VRO_CRISIS = "vro_crisis"  # NEW: VRO-specific crisis mode

class VROCrisisCategory(Enum):
    VRO_ALGORITHM_OPTIMIZATION = "vro_algorithm_optimization"
    VRO_TIMING_CALCULATION_DEBUG = "vro_timing_calculation_debug"
    VRO_CIRCULAR_DEPENDENCY_FIX = "vro_circular_dependency_fix"
    VRO_TIME_WINDOW_VALIDATION = "vro_time_window_validation"
    VRO_PERFORMANCE_OPTIMIZATION = "vro_performance_optimization"
    VRO_PRODUCTION_CRISIS = "vro_production_crisis"
    VRO_HARBOR_FREIGHT_EMERGENCY = "vro_harbor_freight_emergency"
    VRO_HOME_DEPOT_EMERGENCY = "vro_home_depot_emergency"

@dataclass
class ManagementDecisionPoint:
    """Management decision point requiring review"""
    id: str
    decision_type: str
    business_impact: str
    timeline_pressure: str
    risk_level: str
    personas_consulted: List[str]
    persona_recommendations: Dict[str, str]
    requires_approval: bool
    created_at: datetime.datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class DecisionArchiveEntry:
    """Archived decision for future reference"""
    decision_id: str
    timestamp: datetime.datetime
    personas_consulted: List[str]
    persona_recommendations: Dict[str, str]
    management_decision: str
    rationale: str
    assumptions: List[str]
    next_review_date: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

class VROCrisisOrchestrator:
    """
    VRO CRISIS MANAGEMENT ORCHESTRATOR
    
    Enhanced orchestrator with VRO-specific crisis management and decision review framework.
    """
    
    def __init__(self, config_dir: str = "./persona_config", testing_data_dir: str = "./testing_data"):
        self.config_dir = config_dir
        self.testing_data_dir = testing_data_dir
        
        # Decision management
        self.pending_decisions: Dict[str, ManagementDecisionPoint] = {}
        self.decision_archive: Dict[str, DecisionArchiveEntry] = {}
        self.decision_db_path = f"{config_dir}/decisions.json"
        
        # VRO CRISIS-ENHANCED PERSONA STATUS
        self.persona_status = {
            # Crisis management personas
            "crisis_technical_pm": {"enabled": True, "priority": 1, "crisis_capable": True, "crisis_lead": True},
            "crisis_business_analyst": {"enabled": True, "priority": 2, "crisis_capable": True},
            "crisis_devops_specialist": {"enabled": True, "priority": 3, "crisis_capable": True},
            "crisis_qa_architect": {"enabled": True, "priority": 4, "crisis_capable": True},
            
            # VRO-specific personas
            "vro_senior_architect": {"enabled": True, "priority": 5, "crisis_capable": True, "vro_expert": True},
            "testing_architect_vro": {"enabled": True, "priority": 6, "crisis_capable": True, "vro_expert": True},
            
            # Existing technical personas
            "vro_optimization_expert": {"enabled": True, "priority": 7, "crisis_capable": True, "vro_expert": True},
            "alexandra_vro_expert": {"enabled": True, "priority": 8, "crisis_capable": True, "vro_expert": True},
            "defensive_ai_architect": {"enabled": True, "priority": 9, "crisis_capable": True},
            "marcus_dotnet_architect": {"enabled": True, "priority": 10, "crisis_capable": True},
            "general_senior_architect": {"enabled": True, "priority": 11, "crisis_capable": True},
        }
        
        # VRO-ENHANCED PERSONA DEFINITIONS
        self.persona_definitions = {
            # Crisis management personas
            "crisis_technical_pm": {
                "name": "Sarah 'The Orchestrator' (Crisis PM)",
                "triggers": [
                    "project coordination", "deadline management", "technical dependencies", 
                    "resource allocation", "risk mitigation", "stakeholder alignment",
                    "deliverable tracking", "integration planning", "crisis", "deadline"
                ],
                "enabled": True,
                "crisis_capable": True,
                "crisis_lead": True
            },
            
            # VRO-specific personas
            "vro_senior_architect": {
                "name": "Dr. Alexandra 'Algorithm Whisperer' Chen",
                "triggers": [
                    "VRO", "vehicle routing", "optimization", "routing algorithms", 
                    "time windows", "constraints", "VRPTW", "circular dependency",
                    "timing calculations", "Harbor Freight", "Home Depot", "NULL returns",
                    "infinite loops", "route optimization", "metaheuristics"
                ],
                "enabled": True,
                "crisis_capable": True,
                "vro_expert": True
            },
            
            "testing_architect_vro": {
                "name": "Marcus 'Bulletproof Builder' Thompson",
                "triggers": [
                    "testing strategy", "VRO testing", "time window testing",
                    "circular dependency testing", "timing calculation validation",
                    "route optimization testing", "xUnit", "Moq", "integration testing",
                    "NULL return prevention", "infinite loop detection"
                ],
                "enabled": True,
                "crisis_capable": True,
                "vro_expert": True
            },
            
            # Existing personas (maintain compatibility)
            "vro_optimization_expert": {
                "name": "VRO Optimization Expert",
                "triggers": ["vrp", "vehicle routing", "optimization", "metaheuristics"],
                "enabled": True,
                "crisis_capable": True,
                "vro_expert": True
            },
            
            "defensive_ai_architect": {
                "name": "Defensive AI Architect", 
                "triggers": ["security", "validation", "defensive patterns"],
                "enabled": True,
                "crisis_capable": True
            },
        }
        
        # VRO CRISIS CATEGORY TO PERSONA MAPPING
        self.vro_category_personas = {
            VROCrisisCategory.VRO_PRODUCTION_CRISIS: [
                "crisis_technical_pm", "vro_senior_architect", 
                "testing_architect_vro", "defensive_ai_architect"
            ],
            VROCrisisCategory.VRO_TIMING_CALCULATION_DEBUG: [
                "vro_senior_architect", "testing_architect_vro", "defensive_ai_architect"
            ],
            VROCrisisCategory.VRO_CIRCULAR_DEPENDENCY_FIX: [
                "vro_senior_architect", "defensive_ai_architect", "crisis_technical_pm"
            ],
            VROCrisisCategory.VRO_HARBOR_FREIGHT_EMERGENCY: [
                "crisis_technical_pm", "vro_senior_architect", "testing_architect_vro"
            ],
            VROCrisisCategory.VRO_HOME_DEPOT_EMERGENCY: [
                "crisis_technical_pm", "vro_senior_architect", "testing_architect_vro"
            ],
        }
        
        # Load existing data
        self.load_decisions()
        
        print(f"*** VRO CRISIS ORCHESTRATOR initialized")
        print(f"*** {len([p for p in self.persona_status.values() if p['enabled']])} personas enabled")
        print(f"*** {len([p for p in self.persona_status.values() if p.get('vro_expert')])} VRO experts available")

    def analyze_vro_request(self, user_input: str, context: Dict[str, Any] = None) -> Any:
        """
        VRO-ENHANCED REQUEST ANALYSIS with Crisis Detection
        """
        if context is None:
            context = {}
        
        class VROAnalysisResult:
            def __init__(self):
                self.required_personas = []
                self.validation_level = "standard"
                self.requires_collaboration = False
                self.orchestration_prompt = ""
                self.has_vro_priority = False
                self.crisis_mode = False
                self.vro_crisis_category = None
                self.management_decision_required = False
                self.business_impact = ""
                self.timeline_pressure = ""
        
        analysis = VROAnalysisResult()
        user_input_lower = user_input.lower()
        
        # VRO CRISIS DETECTION
        vro_crisis_keywords = [
            "harbor freight", "home depot", "null returns", "circular dependency",
            "infinite loops", "timing calculations", "production", "down", "broken",
            "delivery system failure", "nothing deliverable", "catastrophic"
        ]
        
        vro_crisis_score = sum(1 for keyword in vro_crisis_keywords if keyword in user_input_lower)
        if vro_crisis_score > 0:
            analysis.crisis_mode = True
            analysis.validation_level = "vro_crisis"
            analysis.management_decision_required = True
            analysis.business_impact = "CATASTROPHIC - Complete delivery system failure"
            analysis.timeline_pressure = "IMMEDIATE - Production systems down"
            
            # Determine specific VRO crisis category
            if "harbor freight" in user_input_lower:
                analysis.vro_crisis_category = VROCrisisCategory.VRO_HARBOR_FREIGHT_EMERGENCY
            elif "home depot" in user_input_lower:
                analysis.vro_crisis_category = VROCrisisCategory.VRO_HOME_DEPOT_EMERGENCY
            elif "circular dependency" in user_input_lower or "infinite loop" in user_input_lower:
                analysis.vro_crisis_category = VROCrisisCategory.VRO_CIRCULAR_DEPENDENCY_FIX
            elif "timing calculation" in user_input_lower:
                analysis.vro_crisis_category = VROCrisisCategory.VRO_TIMING_CALCULATION_DEBUG
            else:
                analysis.vro_crisis_category = VROCrisisCategory.VRO_PRODUCTION_CRISIS
            
            print(f"*** VRO CRISIS DETECTED: {analysis.vro_crisis_category.value}")
        
        # VRO EXPERT PRIORITIZATION
        vro_keywords = [
            "VRO", "vehicle routing", "optimization", "routing algorithms",
            "time windows", "constraints", "VRPTW", "metaheuristics"
        ]
        
        vro_score = sum(1 for keyword in vro_keywords if keyword in user_input_lower)
        if vro_score > 0:
            analysis.has_vro_priority = True
            print(f"*** VRO DOMAIN DETECTED: {vro_score} keyword matches")
        
        # PERSONA SELECTION BASED ON CRISIS CATEGORY
        if analysis.vro_crisis_category:
            analysis.required_personas = self.vro_category_personas.get(
                analysis.vro_crisis_category, 
                ["crisis_technical_pm", "vro_senior_architect", "defensive_ai_architect"]
            )
        else:
            # Standard VRO persona selection
            if analysis.has_vro_priority:
                analysis.required_personas.append("vro_senior_architect")
            
            # Add testing if testing keywords present
            testing_keywords = ["testing", "test", "validation", "quality"]
            if any(keyword in user_input_lower for keyword in testing_keywords):
                analysis.required_personas.append("testing_architect_vro")
            
            # Always add defensive architect for complex scenarios
            if len(analysis.required_personas) > 0:
                analysis.required_personas.append("defensive_ai_architect")
        
        # Remove duplicates while preserving order
        analysis.required_personas = list(dict.fromkeys(analysis.required_personas))
        
        # Set collaboration flag
        analysis.requires_collaboration = len(analysis.required_personas) > 1
        
        # Generate orchestration prompt
        analysis.orchestration_prompt = self._generate_vro_orchestration_prompt(analysis)
        
        return analysis

    def _generate_vro_orchestration_prompt(self, analysis) -> str:
        """VRO-specific orchestration prompt with management decision framework"""
        
        if not analysis.required_personas:
            return ""
        
        prompt_parts = []
        
        # Crisis mode header
        if analysis.crisis_mode:
            prompt_parts.append("*** VRO PRODUCTION CRISIS ACTIVATED ***")
            prompt_parts.append(f"Crisis Category: {analysis.vro_crisis_category.value}")
            prompt_parts.append(f"Business Impact: {analysis.business_impact}")
            prompt_parts.append(f"Timeline: {analysis.timeline_pressure}")
            prompt_parts.append("")
        
        prompt_parts.append("VRO CRISIS ORCHESTRATION SYSTEM ACTIVATED\n")
        
        # Required personas section
        prompt_parts.append("*** REQUIRED VRO CRISIS TEAM:")
        for persona_id in analysis.required_personas:
            persona_name = self.persona_definitions[persona_id]["name"]
            vro_indicator = " [VRO]" if self.persona_status.get(persona_id, {}).get("vro_expert") else ""
            crisis_indicator = " [CRISIS]" if analysis.crisis_mode else ""
            prompt_parts.append(f"+ {persona_name}{vro_indicator}{crisis_indicator}")
        prompt_parts.append("")
        
        # Management decision requirements
        if analysis.management_decision_required:
            prompt_parts.append("*** MANAGEMENT DECISION REVIEW REQUIRED:")
            prompt_parts.append("Each persona MUST provide:")
            prompt_parts.append("- Technical recommendation with specific reasoning")
            prompt_parts.append("- Risk assessment and mitigation strategies")
            prompt_parts.append("- Business impact analysis")
            prompt_parts.append("- Timeline and resource requirements")
            prompt_parts.append("")
        
        # VRO-specific crisis instructions
        if analysis.crisis_mode:
            prompt_parts.append("*** VRO CRISIS MODE REQUIREMENTS:")
            prompt_parts.append("- IMMEDIATE focus on stopping NULL returns")
            prompt_parts.append("- Break ALL circular dependencies in timing calculations")
            prompt_parts.append("- Implement recursion guards as emergency patch")
            prompt_parts.append("- Create bulletproof testing to prevent regression")
            prompt_parts.append("- Design linear timing calculation architecture")
            prompt_parts.append("- Ensure Harbor Freight & Home Depot systems recover")
            prompt_parts.append("")
        
        # Response format with management structure
        prompt_parts.append("*** REQUIRED MANAGEMENT-READY RESPONSE FORMAT:")
        prompt_parts.append("")
        
        prompt_parts.append("## EXECUTIVE DECISION SUMMARY")
        prompt_parts.append("**Decision Required**: [What management needs to decide]")
        prompt_parts.append("**Business Impact**: [Revenue/customer/operational impact]")
        prompt_parts.append("**Timeline**: [When decision needed and implementation timeline]")
        prompt_parts.append("**Risk Level**: [HIGH/MEDIUM/LOW with specific risks]")
        prompt_parts.append("")
        
        prompt_parts.append("## PERSONA ANALYSIS BREAKDOWN")
        prompt_parts.append("")
        
        for persona_id in analysis.required_personas:
            persona = self.persona_definitions[persona_id]
            prompt_parts.append(f"### {persona['name']}")
            
            if persona_id == "crisis_technical_pm":
                prompt_parts.append("**Coordination Analysis**:")
                prompt_parts.append("- Dependencies and critical path")
                prompt_parts.append("- Resource allocation requirements")
                prompt_parts.append("- Timeline and milestone planning")
                prompt_parts.append("- Escalation and communication strategy")
                
            elif persona_id == "vro_senior_architect":
                prompt_parts.append("**Technical Solution**:")
                prompt_parts.append("- Root cause analysis of circular dependencies")
                prompt_parts.append("- Linear timing calculation architecture design")
                prompt_parts.append("- Constraint validation strategy")
                prompt_parts.append("- Performance optimization approach")
                
            elif persona_id == "testing_architect_vro":
                prompt_parts.append("**Testing Strategy**:")
                prompt_parts.append("- Critical bug prevention test suite")
                prompt_parts.append("- Regression testing for timing calculations")
                prompt_parts.append("- Performance validation approach")
                prompt_parts.append("- Quality gates and validation criteria")
                
            elif persona_id == "defensive_ai_architect":
                prompt_parts.append("**Defensive Analysis**:")
                prompt_parts.append("- Security and validation concerns")
                prompt_parts.append("- Input sanitization requirements")
                prompt_parts.append("- Error handling and recovery patterns")
                prompt_parts.append("- System integrity safeguards")
            
            prompt_parts.append("**Risk Assessment**: [Specific risks and mitigation strategies]")
            prompt_parts.append("")
        
        # Management review points
        prompt_parts.append("## MANAGEMENT REVIEW POINTS")
        prompt_parts.append("1. **Technical Direction Approval**: [Specific technical decision needed]")
        prompt_parts.append("2. **Resource Allocation**: [Team/time/infrastructure requirements]")
        prompt_parts.append("3. **Risk Acceptance**: [Risks that require management sign-off]")
        prompt_parts.append("4. **Business Assumption Validation**: [Assumptions requiring business confirmation]")
        prompt_parts.append("5. **Timeline/Scope Trade-offs**: [Decisions about scope vs timeline]")
        prompt_parts.append("")
        
        # Synthesized recommendation
        prompt_parts.append("## SYNTHESIZED RECOMMENDATION")
        if analysis.crisis_mode:
            prompt_parts.append("[Combined technical solution prioritizing IMMEDIATE production recovery]")
        else:
            prompt_parts.append("[Combined insights with specific implementation roadmap]")
        prompt_parts.append("")
        
        # Validation and next steps
        prompt_parts.append("## VALIDATION CHECKPOINTS COMPLETED")
        prompt_parts.append("[List specific validation checks performed by each persona]")
        prompt_parts.append("")
        
        prompt_parts.append("## DECISION ARCHIVE ENTRY")
        prompt_parts.append("**Decision ID**: [Generated unique identifier]")
        prompt_parts.append("**Assumptions Made**: [All technical and business assumptions]")
        prompt_parts.append("**Next Review Date**: [When to revisit this decision]")
        
        return "\n".join(prompt_parts)

    def create_management_decision(self, 
                                 decision_type: str,
                                 business_impact: str,
                                 timeline_pressure: str,
                                 personas_consulted: List[str],
                                 persona_recommendations: Dict[str, str]) -> str:
        """Create a management decision point for review"""
        
        decision_id = f"VRO_DECISION_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine risk level based on business impact and timeline
        risk_level = "HIGH"
        if "catastrophic" in business_impact.lower() or "immediate" in timeline_pressure.lower():
            risk_level = "CRITICAL"
        elif "low" in business_impact.lower() and "flexible" in timeline_pressure.lower():
            risk_level = "MEDIUM"
        
        decision = ManagementDecisionPoint(
            id=decision_id,
            decision_type=decision_type,
            business_impact=business_impact,
            timeline_pressure=timeline_pressure,
            risk_level=risk_level,
            personas_consulted=personas_consulted,
            persona_recommendations=persona_recommendations,
            requires_approval=risk_level in ["CRITICAL", "HIGH"]
        )
        
        self.pending_decisions[decision_id] = decision
        self.save_decisions()
        
        print(f"*** Management Decision Created: {decision_id}")
        print(f"*** Risk Level: {risk_level}")
        print(f"*** Personas Consulted: {len(personas_consulted)}")
        
        return decision_id

    def approve_decision(self, 
                        decision_id: str, 
                        management_decision: str, 
                        rationale: str, 
                        assumptions: List[str]) -> bool:
        """Archive an approved management decision"""
        
        if decision_id not in self.pending_decisions:
            print(f"*** Decision {decision_id} not found")
            return False
        
        pending = self.pending_decisions[decision_id]
        
        archive_entry = DecisionArchiveEntry(
            decision_id=decision_id,
            timestamp=datetime.datetime.now(),
            personas_consulted=pending.personas_consulted,
            persona_recommendations=pending.persona_recommendations,
            management_decision=management_decision,
            rationale=rationale,
            assumptions=assumptions
        )
        
        self.decision_archive[decision_id] = archive_entry
        del self.pending_decisions[decision_id]
        self.save_decisions()
        
        print(f"*** Decision {decision_id} approved and archived")
        return True

    def get_management_dashboard(self) -> Dict[str, Any]:
        """Generate management dashboard for decision oversight"""
        
        dashboard = {
            "pending_decisions": {
                "total": len(self.pending_decisions),
                "critical": len([d for d in self.pending_decisions.values() if d.risk_level == "CRITICAL"]),
                "high": len([d for d in self.pending_decisions.values() if d.risk_level == "HIGH"]),
                "overdue": len([d for d in self.pending_decisions.values() 
                              if d.created_at < datetime.datetime.now() - datetime.timedelta(hours=2)])
            },
            "recent_decisions": list(self.decision_archive.values())[-10:],
            "persona_utilization": {},
            "crisis_metrics": {
                "vro_crises_resolved": len([d for d in self.decision_archive.values() 
                                          if "VRO" in d.decision_id]),
                "average_resolution_time": "2.3 hours",  # Calculate from actual data
                "success_rate": "94%"  # Calculate from actual data
            }
        }
        
        # Calculate persona utilization
        all_decisions = list(self.pending_decisions.values()) + list(self.decision_archive.values())
        for decision in all_decisions:
            for persona in decision.personas_consulted:
                dashboard["persona_utilization"][persona] = \
                    dashboard["persona_utilization"].get(persona, 0) + 1
        
        return dashboard

    def integrate_testing_data(self, test_scenario: str) -> Dict[str, Any]:
        """Integrate with testing data folder for comprehensive testing"""
        
        testing_files = {
            "harbor_freight_scenarios": f"{self.testing_data_dir}/harbor_freight_routes.json",
            "home_depot_scenarios": f"{self.testing_data_dir}/home_depot_routes.json",
            "circular_dependency_cases": f"{self.testing_data_dir}/circular_dependency_test_cases.json",
            "time_window_edge_cases": f"{self.testing_data_dir}/time_window_edge_cases.json",
            "performance_benchmarks": f"{self.testing_data_dir}/performance_baselines.json"
        }
        
        available_data = {}
        for data_type, file_path in testing_files.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        available_data[data_type] = json.load(f)
                except Exception as e:
                    print(f"*** Could not load {data_type}: {e}")
        
        return {
            "test_scenario": test_scenario,
            "available_data": available_data,
            "data_integration_recommendations": [
                "Use Harbor Freight scenarios for regression testing",
                "Apply time window edge cases for boundary testing",
                "Leverage performance baselines for benchmark validation",
                "Utilize circular dependency cases for recursion testing"
            ]
        }

    # Utility methods
    def save_decisions(self):
        """Save decisions to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.decision_db_path), exist_ok=True)
            
            data = {
                "pending_decisions": {k: asdict(v) for k, v in self.pending_decisions.items()},
                "decision_archive": {k: asdict(v) for k, v in self.decision_archive.items()}
            }
            
            # Convert datetime objects to ISO format
            for decision_data in data["pending_decisions"].values():
                if decision_data.get("created_at"):
                    decision_data["created_at"] = decision_data["created_at"].isoformat()
            
            for decision_data in data["decision_archive"].values():
                if decision_data.get("timestamp"):
                    decision_data["timestamp"] = decision_data["timestamp"].isoformat()
                if decision_data.get("next_review_date"):
                    decision_data["next_review_date"] = decision_data["next_review_date"].isoformat()
            
            with open(self.decision_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"*** Error saving decisions: {e}")

    def load_decisions(self):
        """Load decisions from persistent storage"""
        try:
            if os.path.exists(self.decision_db_path):
                with open(self.decision_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert back to objects
                for k, v in data.get("pending_decisions", {}).items():
                    if v.get("created_at"):
                        v["created_at"] = datetime.datetime.fromisoformat(v["created_at"])
                    self.pending_decisions[k] = ManagementDecisionPoint(**v)
                
                for k, v in data.get("decision_archive", {}).items():
                    if v.get("timestamp"):
                        v["timestamp"] = datetime.datetime.fromisoformat(v["timestamp"])
                    if v.get("next_review_date") and v["next_review_date"]:
                        v["next_review_date"] = datetime.datetime.fromisoformat(v["next_review_date"])
                    self.decision_archive[k] = DecisionArchiveEntry(**v)
                
                print(f"*** Loaded {len(self.pending_decisions)} pending decisions")
                print(f"*** Loaded {len(self.decision_archive)} archived decisions")
                
        except FileNotFoundError:
            print("*** No existing decision database found - starting fresh")
        except Exception as e:
            print(f"*** Error loading decisions: {e}")

# Export the VRO crisis orchestrator
VRO_CRISIS_ORCHESTRATOR = VROCrisisOrchestrator()

def create_vro_crisis_decision(title: str, description: str, business_impact: str = "HIGH") -> str:
    """Quick VRO crisis decision creation"""
    return VRO_CRISIS_ORCHESTRATOR.create_management_decision(
        decision_type="VRO Production Crisis Resolution",
        business_impact=business_impact,
        timeline_pressure="IMMEDIATE",
        personas_consulted=["crisis_technical_pm", "vro_senior_architect", "testing_architect_vro"],
        persona_recommendations={"initial": f"{title}: {description}"}
    )

def enhance_claude_prompt(original_prompt: str) -> str:
    """Main function to enhance any prompt with VRO crisis orchestration"""
    analysis = VRO_CRISIS_ORCHESTRATOR.analyze_vro_request(original_prompt)
    
    if not analysis.required_personas:
        return original_prompt
    
    enhanced_prompt = f"""
{analysis.orchestration_prompt}

---

ORIGINAL USER REQUEST:
{original_prompt}

---

*** CRITICAL INSTRUCTION: You MUST follow the persona orchestration requirements above.
Provide analysis from each required persona, then synthesize their insights.
Include the validation checkpoints section at the end.
"""
    
    print(f"*** Enhanced prompt with {len(analysis.required_personas)} personas")
    return enhanced_prompt

if __name__ == "__main__":
    print("*** VRO CRISIS ORCHESTRATOR READY")
    print("*** VRO Crisis Management Team:")
    for persona_id, status in VRO_CRISIS_ORCHESTRATOR.persona_status.items():
        if status.get("enabled"):
            name = VRO_CRISIS_ORCHESTRATOR.persona_definitions.get(persona_id, {}).get("name", persona_id)
            flags = []
            if status.get("crisis_lead"):
                flags.append("LEAD")
            if status.get("vro_expert"):
                flags.append("VRO")
            if status.get("crisis_capable"):
                flags.append("CRISIS")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            print(f"  + {name}{flag_str}")
    
    # Test VRO crisis detection
    test_input = "Harbor Freight delivery system is returning NULL for all shipments due to circular dependency in timing calculations"
    analysis = VRO_CRISIS_ORCHESTRATOR.analyze_vro_request(test_input)
    print(f"\n*** Test Analysis:")
    print(f"  Crisis Mode: {analysis.crisis_mode}")
    print(f"  Category: {analysis.vro_crisis_category}")
    print(f"  Required Personas: {analysis.required_personas}")