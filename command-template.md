# Enhanced Command Template

## Command Structure Template

This template demonstrates how to implement any of the enhanced commands with all features integrated.

```python
# Example: performance-review command implementation

class PerformanceReviewCommand:
    """
    Enhanced performance review with cross-command intelligence,
    pattern detection, and automated prompt generation.
    """
    
    def __init__(self):
        self.metrics_config = load_json('metrics.json')
        self.personas_config = load_json('personas.json')
        self.cross_intel = load_json('cross-intelligence.json')
        self.previous_findings = self.load_previous_findings()
        
    def execute(self, target_path=None):
        """Main execution flow following enhanced process"""
        
        # Phase 0: Intelligence Gathering
        intelligence = self.gather_intelligence()
        
        # Phase 1: Initial Analysis
        governance = self.read_governance('CLAUDE.md')
        files = self.scan_codebase(target_path)
        
        # Phase 2: Expert Persona Activation
        personas = self.select_personas('performance-review')
        
        # Phase 3: Collaborative Review
        findings = self.collaborative_review(files, personas, intelligence)
        
        # Phase 4: Severity Scoring
        scored_findings = self.apply_severity_scoring(findings)
        
        # Phase 5: Cost-Benefit Analysis
        prioritized_findings = self.calculate_roi(scored_findings)
        
        # Phase 6: GitHub Copilot Prompt Generation
        prompts = self.generate_prompts(prioritized_findings, personas)
        
        # Phase 7: Cross-Command Intelligence Update
        self.update_intelligence(findings)
        
        # Phase 8: Report Generation
        report = self.generate_report(prioritized_findings, prompts)
        
        # Phase 9: Metrics Collection
        self.collect_metrics(findings, prompts)
        
        return report, prompts
    
    def gather_intelligence(self):
        """Load cross-command intelligence data"""
        intelligence = {
            'previous_issues': self.load_issues_database(),
            'patterns': self.load_patterns_database(),
            'prompt_success': self.load_prompt_success_rates(),
            'related_findings': self.get_related_findings([
                'code-review',
                'architecture-review'
            ])
        }
        return intelligence
    
    def select_personas(self, command_name):
        """Select optimal persona combination"""
        default_personas = self.personas_config['selection_rules'][command_name]
        
        # Adjust based on previous success rates
        success_rates = self.get_persona_success_rates(command_name)
        
        # Select top 3 performing personas for this command type
        selected = self.optimize_persona_selection(default_personas, success_rates)
        
        return [self.personas_config['personas'][p] for p in selected]
    
    def collaborative_review(self, files, personas, intelligence):
        """Three personas review and reach consensus"""
        findings = []
        
        for file in files:
            # Each persona analyzes independently
            persona_findings = []
            for persona in personas:
                analysis = self.analyze_with_persona(file, persona, intelligence)
                persona_findings.append(analysis)
            
            # Reach consensus
            consensus = self.reach_consensus(persona_findings)
            findings.extend(consensus)
            
        # Apply pattern detection
        patterns = self.detect_patterns(findings, intelligence['patterns'])
        
        return {'issues': findings, 'patterns': patterns}
    
    def apply_severity_scoring(self, findings):
        """Quantitative severity scoring"""
        scored = []
        
        for finding in findings['issues']:
            score = 0
            
            # Security Impact (0-40)
            score += self.calculate_security_impact(finding) * 40
            
            # User Impact (0-30)
            score += self.calculate_user_impact(finding) * 30
            
            # Technical Debt (0-20)
            score += self.calculate_technical_debt(finding) * 20
            
            # Maintenance Burden (0-10)
            score += self.calculate_maintenance_burden(finding) * 10
            
            finding['severity_score'] = score
            finding['severity_level'] = self.get_severity_level(score)
            scored.append(finding)
            
        return scored
    
    def calculate_roi(self, findings):
        """Calculate ROI for prioritization"""
        for finding in findings:
            risk_reduction = finding.get('risk_reduction', 50)
            performance_gain = finding.get('performance_gain', 30)
            implementation_effort = finding.get('effort_points', 10)
            
            roi = (risk_reduction + performance_gain) / max(implementation_effort, 1)
            finding['roi_score'] = roi
            finding['priority'] = self.get_priority_from_roi(roi)
            
        return sorted(findings, key=lambda x: x['roi_score'], reverse=True)
    
    def generate_prompts(self, findings, personas):
        """Generate enhanced GitHub Copilot prompts"""
        prompts = []
        
        for finding in findings[:10]:  # Top 10 priorities
            prompt = self.create_enhanced_prompt(finding, personas)
            prompts.append(prompt)
            
            # Save to prompts folder
            self.save_prompt(prompt, finding['id'])
            
        return prompts
    
    def create_enhanced_prompt(self, finding, personas):
        """Create structured GitHub Copilot prompt"""
        return f"""
You are a {personas[0]['name']} with expertise in {', '.join(personas[0]['expertise'])}.

CONTEXT: {finding['description']} with severity score {finding['severity_score']}/100

INTELLIGENCE:
- Previous similar issues: {self.get_similar_issues_count(finding)}
- Success rate of similar fixes: {self.get_similar_fix_success_rate(finding)}%
- Estimated effort: {finding.get('effort_points', 'Unknown')} story points

TASK: {finding['recommended_action']}

REQUIREMENTS:
1. {finding['requirement_1']}
2. {finding['requirement_2']}
3. {finding['requirement_3']}

CONSTRAINTS:
- Dependencies: {finding.get('dependencies', 'None identified')}
- Performance: {finding.get('performance_constraints', 'Standard requirements')}
- Compatibility: {finding.get('compatibility', 'Current stack')}

GOVERNANCE:
- Follow coding standards in CLAUDE.md
- Severity score: {finding['severity_score']}/100
- Priority: {finding['priority']}

VALIDATION:
- Unit tests: {finding.get('test_scenarios', 'Standard coverage')}
- Integration tests: {finding.get('integration_tests', 'API validation')}
- Performance benchmarks: {finding.get('benchmarks', 'Baseline metrics')}
- Security checks: {finding.get('security_checks', 'OWASP standards')}

SUCCESS METRICS:
- {finding.get('success_metric_1', 'Issue resolved')}
- {finding.get('success_metric_2', 'Tests passing')}
- {finding.get('success_metric_3', 'Performance maintained')}
"""
```

## Usage Pattern

```python
# Initialize command with cross-intelligence
command = PerformanceReviewCommand()

# Execute with intelligence gathering
report, prompts = command.execute('src/api/')

# Results are automatically:
# - Saved to reports/ folder
# - Prompts saved to prompts/ folder
# - Metrics updated in metrics/ folder
# - Intelligence shared with other commands
```

## Key Features Demonstrated

1. **Intelligence Gathering**: Loads previous findings and patterns
2. **Persona Selection**: Dynamically selects best personas based on success rates
3. **Collaborative Review**: Multiple personas reach consensus
4. **Severity Scoring**: Quantitative 0-100 scoring system
5. **ROI Calculation**: Prioritizes based on value/effort ratio
6. **Pattern Detection**: Identifies recurring issues
7. **Cross-Command Updates**: Shares findings with other commands
8. **Metrics Collection**: Tracks success rates and improvements
9. **Enhanced Prompts**: Includes context, intelligence, and success metrics
10. **Continuous Learning**: Adjusts based on feedback

## Integration Points

- **Reads**: `CLAUDE.md`, previous findings, patterns, success rates
- **Writes**: Reports, prompts, metrics, updated intelligence
- **Shares**: Findings with related commands
- **Learns**: From prompt success rates and user feedback