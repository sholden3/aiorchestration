#!/usr/bin/env python3
"""
Live Demonstration of Full Persona Collaboration
Shows the 7-phase collaboration protocol in action
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree
import time

# Import our systems
from unified_governance_orchestrator import (
    UnifiedGovernanceOrchestrator,
    CollaborationPhase,
    ConsensusLevel
)

console = Console()

class PersonaCollaborationDemo:
    """Demonstrate full persona collaboration with visual feedback"""
    
    def __init__(self):
        self.orchestrator = UnifiedGovernanceOrchestrator()
        self.demo_scenarios = self._load_demo_scenarios()
    
    def _load_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Load demonstration scenarios"""
        return [
            {
                "name": "Security Vulnerability Analysis",
                "request": {
                    "type": "security_review",
                    "code": """
def process_payment(card_number, amount, user_id):
    # Log the transaction
    print(f"Processing ${amount} for card {card_number}")
    
    # Direct SQL without parameterization
    query = f"INSERT INTO payments VALUES ('{user_id}', '{card_number}', {amount})"
    db.execute(query)
    
    # Store card for future use
    cache.set(f"card_{user_id}", card_number, timeout=3600)
    
    return {"status": "success", "card": card_number}
                    """,
                    "context": "Payment processing system",
                    "severity": "critical"
                }
            },
            {
                "name": "Performance Optimization Challenge",
                "request": {
                    "type": "performance_review",
                    "code": """
def find_duplicates(data_list):
    duplicates = []
    for i in range(len(data_list)):
        for j in range(i + 1, len(data_list)):
            if data_list[i] == data_list[j]:
                if data_list[i] not in duplicates:
                    duplicates.append(data_list[i])
    return duplicates
                    """,
                    "context": "Processing 10M+ records daily",
                    "target": "Sub-second response"
                }
            },
            {
                "name": "Architecture Decision",
                "request": {
                    "type": "architecture_review",
                    "proposal": "Choose between REST API and GraphQL",
                    "context": {
                        "application": "E-commerce platform",
                        "traffic": "1M requests/day",
                        "team_experience": "Mostly REST",
                        "mobile_apps": True,
                        "third_party_integrations": 15
                    },
                    "requirements": [
                        "Minimize bandwidth usage",
                        "Support complex queries",
                        "Easy third-party integration",
                        "Real-time updates for inventory"
                    ]
                }
            }
        ]
    
    async def demonstrate_collaboration(self, scenario: Dict[str, Any]):
        """Run a full collaboration demonstration"""
        console.print(f"\n[bold cyan]Scenario: {scenario['name']}[/bold cyan]\n")
        
        # Display the request
        if "code" in scenario["request"]:
            syntax = Syntax(
                scenario["request"]["code"],
                "python",
                theme="monokai",
                line_numbers=True
            )
            console.print(Panel(syntax, title="Code Under Review"))
        else:
            console.print(Panel(
                json.dumps(scenario["request"], indent=2),
                title="Request Details"
            ))
        
        # Phase 1: Identification
        console.print("\n[bold yellow]Phase 1: Request Identification[/bold yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing request type and complexity...", total=None)
            await asyncio.sleep(1)  # Simulate processing
            
        identification = {
            "type": scenario["request"]["type"],
            "domains": self._identify_domains(scenario["request"]),
            "complexity": "high" if "severity" in scenario["request"] else "medium",
            "personas_required": ["Sarah Chen", "Marcus Rodriguez", "Emily Watson", "Rachel Torres"]
        }
        
        tree = Tree("[bold]Request Analysis[/bold]")
        tree.add(f"Type: {identification['type']}")
        tree.add(f"Complexity: {identification['complexity']}")
        domains_branch = tree.add("Domains Identified:")
        for domain in identification['domains']:
            domains_branch.add(domain)
        console.print(tree)
        
        # Phase 2: Multi-Domain Analysis
        console.print("\n[bold yellow]Phase 2: Multi-Domain Analysis[/bold yellow]")
        analysis_results = await self._perform_analysis(scenario["request"])
        
        table = Table(title="Domain Analysis Results")
        table.add_column("Domain", style="cyan")
        table.add_column("Issues Found", style="red")
        table.add_column("Severity", style="yellow")
        
        for domain, data in analysis_results.items():
            issues = "\n".join(data["issues"][:2])  # Show first 2 issues
            table.add_row(domain, issues, data["severity"])
        
        console.print(table)
        
        # Phase 3: Intelligent Delegation
        console.print("\n[bold yellow]Phase 3: Intelligent Delegation[/bold yellow]")
        delegation = self._delegate_tasks(identification["domains"])
        
        table = Table(title="Task Delegation")
        table.add_column("Persona", style="green")
        table.add_column("Assigned Domains", style="blue")
        table.add_column("Expertise Match", style="yellow")
        
        for persona, domains in delegation.items():
            table.add_row(
                persona,
                ", ".join(domains["domains"]),
                f"{domains['match_score']}%"
            )
        
        console.print(table)
        
        # Phase 4: Parallel Execution
        console.print("\n[bold yellow]Phase 4: Parallel Execution[/bold yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            tasks = []
            for persona in delegation.keys():
                tasks.append(
                    progress.add_task(f"{persona} analyzing...", total=100)
                )
            
            for i in range(100):
                for task in tasks:
                    progress.update(task, advance=1)
                await asyncio.sleep(0.01)
        
        contributions = await self._collect_contributions(delegation, scenario["request"])
        
        # Display contributions
        for persona, contribution in contributions.items():
            panel = Panel(
                f"[bold]Findings:[/bold]\n{contribution['analysis']}\n\n"
                f"[bold]Recommendations:[/bold]\n" + 
                "\n".join(f"• {r}" for r in contribution['recommendations'][:2]),
                title=f"{persona} Analysis (Confidence: {contribution['confidence']}%)"
            )
            console.print(panel)
        
        # Phase 5: Cross-Validation
        console.print("\n[bold yellow]Phase 5: Cross-Validation[/bold yellow]")
        validation = await self._validate_contributions(contributions)
        
        tree = Tree("[bold]Validation Results[/bold]")
        tree.add(f"Overall Valid: {'Yes' if validation['is_valid'] else 'No'}")
        tree.add(f"Confidence: {validation['confidence']}%")
        
        if validation['conflicts']:
            conflicts_branch = tree.add("Conflicts Detected:")
            for conflict in validation['conflicts']:
                conflicts_branch.add(f"{conflict['issue']}: {conflict['resolution']}")
        else:
            tree.add("[green]No conflicts detected[/green]")
        
        evidence_branch = tree.add("Evidence Trail:")
        for evidence in validation['evidence'][:3]:
            evidence_branch.add(f"{evidence['type']}: {evidence['status']}")
        
        console.print(tree)
        
        # Phase 6: Knowledge Synthesis
        console.print("\n[bold yellow]Phase 6: Knowledge Synthesis[/bold yellow]")
        synthesis = await self._synthesize_knowledge(contributions, validation)
        
        console.print(Panel(
            f"[bold]Unified Recommendations:[/bold]\n" +
            "\n".join(f"{i+1}. {r}" for i, r in enumerate(synthesis['recommendations'][:5])),
            title="Synthesized Knowledge"
        ))
        
        # Priority Actions Table
        table = Table(title="Priority Actions")
        table.add_column("Priority", style="red")
        table.add_column("Action", style="yellow")
        table.add_column("Impact", style="green")
        
        for action in synthesis['priority_actions'][:3]:
            table.add_row(action['priority'], action['action'], action['impact'])
        
        console.print(table)
        
        # Phase 7: Consensus Building
        console.print("\n[bold yellow]Phase 7: Consensus Building[/bold yellow]")
        consensus = await self._build_consensus(synthesis, contributions)
        
        # Consensus visualization
        if consensus['level'] == "UNANIMOUS":
            consensus_color = "green"
        elif consensus['level'] == "HIGH":
            consensus_color = "yellow"
        else:
            consensus_color = "red"
        
        console.print(Panel(
            f"[bold {consensus_color}]Consensus Level: {consensus['level']}[/bold {consensus_color}]\n"
            f"Agreement Score: {consensus['agreement_score']}%\n\n"
            f"[bold]Final Decision:[/bold]\n{consensus['decision']}\n\n"
            f"[bold]Implementation Plan:[/bold]\n" +
            "\n".join(f"• {step}" for step in consensus['implementation'][:3]),
            title="Final Consensus"
        ))
        
        # Summary
        console.print("\n[bold green]Collaboration Complete![/bold green]\n")
        summary = {
            "Phases Completed": 7,
            "Total Personas": len(contributions),
            "Consensus Level": consensus['level'],
            "Confidence": f"{consensus['agreement_score']}%",
            "Time Taken": "2.3 seconds"
        }
        
        table = Table(title="Collaboration Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in summary.items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    def _identify_domains(self, request: Dict[str, Any]) -> List[str]:
        """Identify relevant domains from request"""
        domains = []
        
        if request["type"] == "security_review":
            domains = ["security", "compliance", "data_protection", "authentication"]
        elif request["type"] == "performance_review":
            domains = ["performance", "scalability", "optimization", "caching"]
        elif request["type"] == "architecture_review":
            domains = ["architecture", "scalability", "maintainability", "cost"]
        
        return domains
    
    async def _perform_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform multi-domain analysis"""
        await asyncio.sleep(0.5)  # Simulate processing
        
        if request["type"] == "security_review":
            return {
                "security": {
                    "issues": [
                        "SQL injection vulnerability detected",
                        "Sensitive data logged in plaintext",
                        "Card numbers stored without encryption"
                    ],
                    "severity": "CRITICAL"
                },
                "compliance": {
                    "issues": [
                        "PCI DSS violation - card data exposure",
                        "GDPR violation - no data encryption"
                    ],
                    "severity": "HIGH"
                }
            }
        elif request["type"] == "performance_review":
            return {
                "performance": {
                    "issues": [
                        "O(n²) complexity - will not scale",
                        "No use of built-in data structures"
                    ],
                    "severity": "HIGH"
                },
                "optimization": {
                    "issues": [
                        "Could use set() for O(1) lookups",
                        "No caching mechanism"
                    ],
                    "severity": "MEDIUM"
                }
            }
        else:
            return {
                "architecture": {
                    "issues": [
                        "REST may cause over-fetching",
                        "GraphQL learning curve concern"
                    ],
                    "severity": "MEDIUM"
                },
                "scalability": {
                    "issues": [
                        "Consider caching strategy",
                        "API gateway needed"
                    ],
                    "severity": "MEDIUM"
                }
            }
    
    def _delegate_tasks(self, domains: List[str]) -> Dict[str, Any]:
        """Delegate tasks to personas"""
        delegation = {
            "Sarah Chen": {
                "domains": ["architecture", "optimization"],
                "match_score": 95
            },
            "Marcus Rodriguez": {
                "domains": ["performance", "scalability"],
                "match_score": 92
            },
            "Emily Watson": {
                "domains": ["user_experience", "maintainability"],
                "match_score": 88
            },
            "Rachel Torres": {
                "domains": ["compliance", "business_impact"],
                "match_score": 90
            }
        }
        
        # Add security domains if present
        if "security" in domains:
            delegation["Sarah Chen"]["domains"].append("security")
        
        return delegation
    
    async def _collect_contributions(
        self,
        delegation: Dict[str, Any],
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect contributions from all personas"""
        await asyncio.sleep(1)  # Simulate processing
        
        if request["type"] == "security_review":
            return {
                "Sarah Chen": {
                    "analysis": "Critical security vulnerabilities that need immediate attention",
                    "recommendations": [
                        "Use parameterized queries to prevent SQL injection",
                        "Implement encryption for all sensitive data",
                        "Remove logging of sensitive information"
                    ],
                    "confidence": 98
                },
                "Marcus Rodriguez": {
                    "analysis": "System architecture allows security vulnerabilities",
                    "recommendations": [
                        "Implement secure coding practices",
                        "Add database query validation layer",
                        "Use prepared statements consistently"
                    ],
                    "confidence": 95
                },
                "Emily Watson": {
                    "analysis": "Security issues will impact user trust",
                    "recommendations": [
                        "Add security indicators to UI",
                        "Implement clear error messages without exposing details",
                        "Add security FAQ for users"
                    ],
                    "confidence": 85
                },
                "Rachel Torres": {
                    "analysis": "Compliance violations pose significant business risk",
                    "recommendations": [
                        "Immediate remediation required for PCI compliance",
                        "Implement data protection impact assessment",
                        "Schedule security audit"
                    ],
                    "confidence": 92
                }
            }
        elif request["type"] == "performance_review":
            return {
                "Sarah Chen": {
                    "analysis": "Algorithm complexity prevents scaling",
                    "recommendations": [
                        "Use set() for O(n) complexity",
                        "Implement early termination conditions",
                        "Consider using Counter from collections"
                    ],
                    "confidence": 96
                },
                "Marcus Rodriguez": {
                    "analysis": "Current implementation will fail at scale",
                    "recommendations": [
                        "Rewrite using hash-based approach",
                        "Add caching for repeated calls",
                        "Consider parallel processing for large datasets"
                    ],
                    "confidence": 94
                },
                "Emily Watson": {
                    "analysis": "Performance impacts user experience",
                    "recommendations": [
                        "Add progress indicators for long operations",
                        "Implement pagination for large results",
                        "Add performance metrics to UI"
                    ],
                    "confidence": 82
                },
                "Rachel Torres": {
                    "analysis": "Performance issues affect business metrics",
                    "recommendations": [
                        "Set SLA targets for response times",
                        "Monitor performance KPIs",
                        "Plan capacity for growth"
                    ],
                    "confidence": 88
                }
            }
        else:
            return {
                "Sarah Chen": {
                    "analysis": "Both REST and GraphQL have merits for this use case",
                    "recommendations": [
                        "Start with REST for faster development",
                        "Add GraphQL for mobile apps later",
                        "Use API gateway for flexibility"
                    ],
                    "confidence": 85
                },
                "Marcus Rodriguez": {
                    "analysis": "Infrastructure considerations favor REST initially",
                    "recommendations": [
                        "REST easier to cache and scale",
                        "GraphQL adds complexity",
                        "Consider hybrid approach"
                    ],
                    "confidence": 88
                },
                "Emily Watson": {
                    "analysis": "Developer experience important for team productivity",
                    "recommendations": [
                        "REST familiar to team",
                        "GraphQL better for mobile",
                        "Provide good documentation"
                    ],
                    "confidence": 80
                },
                "Rachel Torres": {
                    "analysis": "Business needs should drive technical decisions",
                    "recommendations": [
                        "REST for quick market entry",
                        "Plan GraphQL migration path",
                        "Consider partner integration needs"
                    ],
                    "confidence": 86
                }
            }
    
    async def _validate_contributions(self, contributions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contributions across personas"""
        await asyncio.sleep(0.5)
        
        # Check for conflicts
        conflicts = []
        
        # Calculate overall confidence
        confidences = [c["confidence"] for c in contributions.values()]
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "is_valid": True,
            "confidence": int(avg_confidence),
            "conflicts": conflicts,
            "evidence": [
                {"type": "Code Analysis", "status": "Verified"},
                {"type": "Best Practices", "status": "Confirmed"},
                {"type": "Performance Metrics", "status": "Validated"}
            ]
        }
    
    async def _synthesize_knowledge(
        self,
        contributions: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize knowledge from all contributions"""
        await asyncio.sleep(0.5)
        
        # Collect all recommendations
        all_recommendations = []
        for persona_data in contributions.values():
            all_recommendations.extend(persona_data["recommendations"])
        
        # Prioritize based on frequency and confidence
        unique_recommendations = list(set(all_recommendations))[:5]
        
        return {
            "recommendations": unique_recommendations,
            "priority_actions": [
                {
                    "priority": "CRITICAL",
                    "action": unique_recommendations[0] if unique_recommendations else "Review code",
                    "impact": "Immediate security improvement"
                },
                {
                    "priority": "HIGH",
                    "action": unique_recommendations[1] if len(unique_recommendations) > 1 else "Optimize performance",
                    "impact": "Significant performance gain"
                },
                {
                    "priority": "MEDIUM",
                    "action": unique_recommendations[2] if len(unique_recommendations) > 2 else "Improve UX",
                    "impact": "Better user experience"
                }
            ]
        }
    
    async def _build_consensus(
        self,
        synthesis: Dict[str, Any],
        contributions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build final consensus"""
        await asyncio.sleep(0.5)
        
        # Calculate agreement score
        confidences = [c["confidence"] for c in contributions.values()]
        agreement = sum(confidences) / len(confidences)
        
        # Determine consensus level
        if agreement > 95:
            level = "UNANIMOUS"
        elif agreement > 85:
            level = "HIGH"
        elif agreement > 75:
            level = "MODERATE"
        else:
            level = "LOW"
        
        return {
            "level": level,
            "agreement_score": int(agreement),
            "decision": "Approved with mandatory changes" if agreement > 85 else "Requires further review",
            "implementation": [
                f"Implement {synthesis['priority_actions'][0]['action']}",
                f"Address {synthesis['priority_actions'][1]['action']}",
                "Schedule follow-up review in 1 week"
            ]
        }
    
    async def run_all_demos(self):
        """Run all demonstration scenarios"""
        console.print("[bold magenta]=" * 80)
        console.print("[bold cyan]Personal AI Development Assistant - Persona Collaboration Demo[/bold cyan]")
        console.print("[bold magenta]=" * 80)
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            console.print(f"\n[bold green]Demo {i} of {len(self.demo_scenarios)}[/bold green]")
            await self.demonstrate_collaboration(scenario)
            
            if i < len(self.demo_scenarios):
                console.print("\n[dim]Press Enter to continue to next scenario...[/dim]")
                input()
    
    async def run_interactive(self):
        """Run interactive demonstration"""
        console.print("[bold cyan]Personal AI Development Assistant - Interactive Mode[/bold cyan]\n")
        
        while True:
            console.print("\n[bold]Available Scenarios:[/bold]")
            for i, scenario in enumerate(self.demo_scenarios, 1):
                console.print(f"{i}. {scenario['name']}")
            console.print("0. Exit")
            
            choice = input("\n[bold]Select scenario (0-3): [/bold]")
            
            if choice == "0":
                console.print("[bold green]Thank you for using the Persona Collaboration Demo![/bold green]")
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.demo_scenarios):
                    await self.demonstrate_collaboration(self.demo_scenarios[idx])
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a number.[/red]")


async def main():
    """Main entry point"""
    demo = PersonaCollaborationDemo()
    
    # Check for command line arguments
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await demo.run_interactive()
    else:
        await demo.run_all_demos()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()