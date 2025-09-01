"""
@fileoverview Database seed data
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - Database Layer
@business_logic Initial data for system bootstrapping
"""

from datetime import datetime
from typing import List
import json

from sqlalchemy.orm import Session
from .models import Rule, Practice, Template, RuleSeverity, RuleStatus, TemplateType

def seed_rules(db: Session):
    """Seed initial governance rules"""
    rules = [
        {
            "name": "docstring_required",
            "description": "All functions must have docstrings",
            "category": "documentation",
            "severity": RuleSeverity.ERROR,
            "status": RuleStatus.ACTIVE,
            "condition": "function.docstring is not None",
            "action": "block",
            "parameters": {"min_length": 10},
            "author": "Dr. Sarah Chen"
        },
        {
            "name": "test_coverage_minimum",
            "description": "Code coverage must be at least 80%",
            "category": "testing",
            "severity": RuleSeverity.WARNING,
            "status": RuleStatus.ACTIVE,
            "condition": "coverage >= 80",
            "action": "warn",
            "parameters": {"threshold": 80},
            "author": "Maya Patel"
        },
        {
            "name": "security_no_hardcoded_secrets",
            "description": "No hardcoded secrets in code",
            "category": "security",
            "severity": RuleSeverity.CRITICAL,
            "status": RuleStatus.ACTIVE,
            "condition": "not contains_secrets(code)",
            "action": "block",
            "parameters": {"patterns": ["api_key", "password", "secret"]},
            "author": "Marcus Rivera"
        },
        {
            "name": "complexity_limit",
            "description": "Cyclomatic complexity should not exceed 10",
            "category": "quality",
            "severity": RuleSeverity.WARNING,
            "status": RuleStatus.ACTIVE,
            "condition": "complexity <= 10",
            "action": "warn",
            "parameters": {"max_complexity": 10},
            "author": "Alex Novak"
        },
        {
            "name": "naming_convention",
            "description": "Follow PEP8 naming conventions",
            "category": "style",
            "severity": RuleSeverity.INFO,
            "status": RuleStatus.ACTIVE,
            "condition": "is_pep8_compliant(name)",
            "action": "suggest",
            "parameters": {"style_guide": "PEP8"},
            "author": "Dr. Sarah Chen"
        }
    ]
    
    for rule_data in rules:
        rule = Rule(**rule_data)
        db.add(rule)
    
    db.commit()
    print(f"Seeded {len(rules)} rules")

def seed_practices(db: Session):
    """Seed initial best practices"""
    practices = [
        {
            "name": "Test-Driven Development",
            "category": "development",
            "description": "Write tests before implementation",
            "rationale": "Ensures code meets requirements and catches bugs early",
            "examples": [
                "Write failing test",
                "Implement minimal code to pass",
                "Refactor while keeping tests green"
            ],
            "anti_patterns": [
                "Writing tests after implementation",
                "Skipping tests for 'simple' functions",
                "Not maintaining tests"
            ],
            "score_weight": 1.5,
            "author": "Maya Patel"
        },
        {
            "name": "Code Review Before Merge",
            "category": "collaboration",
            "description": "All code must be reviewed before merging",
            "rationale": "Catches bugs, shares knowledge, maintains quality",
            "examples": [
                "Create pull request with clear description",
                "Request review from relevant team members",
                "Address all feedback before merging"
            ],
            "anti_patterns": [
                "Merging without review",
                "Rubber-stamp approvals",
                "Ignoring reviewer feedback"
            ],
            "score_weight": 1.2,
            "author": "Alex Novak"
        },
        {
            "name": "Dependency Injection",
            "category": "architecture",
            "description": "Use dependency injection for better testability",
            "rationale": "Makes code more modular, testable, and maintainable",
            "examples": [
                "Pass dependencies as constructor parameters",
                "Use interfaces for dependencies",
                "Configure dependencies in IoC container"
            ],
            "anti_patterns": [
                "Hard-coding dependencies",
                "Creating dependencies inside classes",
                "Using global singletons"
            ],
            "score_weight": 1.3,
            "author": "Dr. Sarah Chen"
        },
        {
            "name": "Error Handling Strategy",
            "category": "reliability",
            "description": "Implement comprehensive error handling",
            "rationale": "Prevents crashes and provides better user experience",
            "examples": [
                "Use try-catch blocks appropriately",
                "Log errors with context",
                "Provide meaningful error messages"
            ],
            "anti_patterns": [
                "Catching and ignoring exceptions",
                "Generic error messages",
                "Not logging errors"
            ],
            "score_weight": 1.4,
            "author": "Marcus Rivera"
        }
    ]
    
    for practice_data in practices:
        practice = Practice(**practice_data)
        db.add(practice)
    
    db.commit()
    print(f"Seeded {len(practices)} practices")

def seed_templates(db: Session):
    """Seed initial templates"""
    templates = [
        {
            "name": "Service Class Template",
            "type": TemplateType.CODE,
            "category": "backend/services",
            "template_content": '''/**
 * @fileoverview {{description}}
 * @author {{author}} v{{version}}
 * @architecture {{layer}}
 * @business_logic {{business_logic}}
 */

import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class {{className}}Service {
  constructor(
    {{#each dependencies}}
    private readonly {{this.name}}: {{this.type}},
    {{/each}}
  ) {}

  {{#each methods}}
  {{this.name}}({{this.params}}): {{this.returnType}} {
    // {{this.description}}
    {{this.implementation}}
  }
  {{/each}}
}''',
            "variables": {
                "description": {"type": "string", "required": True},
                "author": {"type": "string", "required": True},
                "version": {"type": "string", "default": "1.0"},
                "layer": {"type": "string", "required": True},
                "business_logic": {"type": "string", "required": True},
                "className": {"type": "string", "required": True},
                "dependencies": {"type": "array", "required": False},
                "methods": {"type": "array", "required": True}
            },
            "author": "Alex Novak"
        },
        {
            "name": "Phase Documentation Template",
            "type": TemplateType.DOCUMENTATION,
            "category": "project/phases",
            "template_content": '''# Phase {{phaseNumber}}: {{phaseName}}

## Duration
**Start Date**: {{startDate}}  
**End Date**: {{endDate}}  
**Total Days**: {{duration}}

## Objectives
{{#each objectives}}
- {{this}}
{{/each}}

## Deliverables
{{#each deliverables}}
### {{this.name}}
{{this.description}}
- **Status**: {{this.status}}
- **Owner**: {{this.owner}}
{{/each}}

## Success Criteria
{{#each criteria}}
- [ ] {{this}}
{{/each}}

## Risks & Mitigations
{{#each risks}}
| Risk | Impact | Mitigation |
|------|--------|------------|
| {{this.risk}} | {{this.impact}} | {{this.mitigation}} |
{{/each}}

## Team
{{#each team}}
- **{{this.name}}** ({{this.role}}): {{this.responsibilities}}
{{/each}}''',
            "variables": {
                "phaseNumber": {"type": "number", "required": True},
                "phaseName": {"type": "string", "required": True},
                "startDate": {"type": "string", "required": True},
                "endDate": {"type": "string", "required": True},
                "duration": {"type": "number", "required": True},
                "objectives": {"type": "array", "required": True},
                "deliverables": {"type": "array", "required": True},
                "criteria": {"type": "array", "required": True},
                "risks": {"type": "array", "required": False},
                "team": {"type": "array", "required": True}
            },
            "author": "Jordan Kim"
        },
        {
            "name": "Bug Fix Prompt Template",
            "type": TemplateType.PROMPT,
            "category": "ai/prompts",
            "template_content": '''As {{persona}}, please analyze and fix this bug:

## Context
**Component**: {{component}}
**Severity**: {{severity}}
**Reported By**: {{reporter}}

## Bug Description
{{description}}

## Error Details
```
{{errorMessage}}
```

## Stack Trace
```
{{stackTrace}}
```

## Steps to Reproduce
{{#each steps}}
{{@index}}. {{this}}
{{/each}}

## Constraints
{{#each constraints}}
- {{this}}
{{/each}}

Please provide:
1. Root cause analysis
2. Proposed fix with code
3. Test cases to prevent regression
4. Impact assessment''',
            "variables": {
                "persona": {"type": "string", "default": "Senior Developer"},
                "component": {"type": "string", "required": True},
                "severity": {"type": "string", "required": True},
                "reporter": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "errorMessage": {"type": "string", "required": True},
                "stackTrace": {"type": "string", "required": False},
                "steps": {"type": "array", "required": True},
                "constraints": {"type": "array", "required": False}
            },
            "author": "David Park"
        }
    ]
    
    for template_data in templates:
        # Convert variables dict to JSON
        if 'variables' in template_data:
            template_data['variables'] = json.dumps(template_data['variables'])
        template = Template(**template_data)
        db.add(template)
    
    db.commit()
    print(f"Seeded {len(templates)} templates")

def seed_all(db: Session):
    """Seed all data"""
    seed_rules(db)
    seed_practices(db)
    seed_templates(db)
    print("All seed data loaded successfully")