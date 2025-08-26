import { Component, OnInit } from '@angular/core';
import { RulesService } from '../../services/rules.service';
import { MatSnackBar } from '@angular/material/snack-bar';

interface Rule {
  id: string;
  name: string;
  description: string;
  condition: string;
  action: string;
  priority: number;
  enabled: boolean;
  category: string;
  tags: string[];
  lastModified: Date;
  executionCount: number;
}

@Component({
  selector: 'app-rules',
  templateUrl: './rules.component.html',
  styleUrls: ['./rules.component.scss']
})
export class RulesComponent implements OnInit {
  rules: Rule[] = [];
  categories = ['Validation', 'Transformation', 'Security', 'Performance', 'Business Logic'];
  displayedColumns: string[] = ['enabled', 'name', 'category', 'priority', 'executionCount', 'actions'];
  selectedRule: Rule | null = null;
  searchQuery = '';
  selectedCategory = '';

  constructor(
    private rulesService: RulesService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadRules();
  }

  loadRules(): void {
    // Load rules from service
    this.rules = [
      {
        id: '1',
        name: 'No Assumptions Rule',
        description: 'Prevents any assumptions without evidence',
        condition: 'if (!evidence) { reject() }',
        action: 'RequestEvidence()',
        priority: 1,
        enabled: true,
        category: 'Validation',
        tags: ['critical', 'evidence-based'],
        lastModified: new Date(),
        executionCount: 245
      },
      {
        id: '2',
        name: 'Token Optimization',
        description: 'Optimizes token usage for Claude API calls',
        condition: 'if (tokens > threshold)',
        action: 'CompressContext()',
        priority: 2,
        enabled: true,
        category: 'Performance',
        tags: ['optimization', 'cost-reduction'],
        lastModified: new Date(),
        executionCount: 1823
      },
      {
        id: '3',
        name: 'Cross-Persona Validation',
        description: 'Ensures all three personas validate critical decisions',
        condition: 'if (decision.critical)',
        action: 'RequireThreePersonaConsensus()',
        priority: 1,
        enabled: true,
        category: 'Business Logic',
        tags: ['governance', 'validation'],
        lastModified: new Date(),
        executionCount: 89
      },
      {
        id: '4',
        name: 'Cache Hit Optimization',
        description: 'Prioritizes cache usage for frequent queries',
        condition: 'if (query.frequency > 10)',
        action: 'MoveToHotCache()',
        priority: 3,
        enabled: true,
        category: 'Performance',
        tags: ['cache', 'optimization'],
        lastModified: new Date(),
        executionCount: 3421
      },
      {
        id: '5',
        name: 'Security Audit Trail',
        description: 'Logs all sensitive operations',
        condition: 'if (operation.sensitive)',
        action: 'LogToAuditTrail()',
        priority: 1,
        enabled: true,
        category: 'Security',
        tags: ['audit', 'compliance'],
        lastModified: new Date(),
        executionCount: 567
      }
    ];
  }

  toggleRule(rule: Rule): void {
    rule.enabled = !rule.enabled;
    this.snackBar.open(`Rule "${rule.name}" ${rule.enabled ? 'enabled' : 'disabled'}`, 'OK', {
      duration: 2000
    });
  }

  editRule(rule: Rule): void {
    this.selectedRule = rule;
  }

  deleteRule(rule: Rule): void {
    const index = this.rules.indexOf(rule);
    if (index > -1) {
      this.rules.splice(index, 1);
      this.snackBar.open(`Rule "${rule.name}" deleted`, 'OK', {
        duration: 2000
      });
    }
  }

  addNewRule(): void {
    const newRule: Rule = {
      id: Date.now().toString(),
      name: 'New Rule',
      description: 'Rule description',
      condition: '',
      action: '',
      priority: 5,
      enabled: false,
      category: 'Validation',
      tags: [],
      lastModified: new Date(),
      executionCount: 0
    };
    this.rules.push(newRule);
    this.selectedRule = newRule;
  }

  saveRule(): void {
    if (this.selectedRule) {
      this.selectedRule.lastModified = new Date();
      this.snackBar.open(`Rule "${this.selectedRule.name}" saved`, 'OK', {
        duration: 2000
      });
      this.selectedRule = null;
    }
  }

  cancelEdit(): void {
    this.selectedRule = null;
  }

  get filteredRules(): Rule[] {
    return this.rules.filter(rule => {
      const matchesSearch = !this.searchQuery || 
        rule.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        rule.description.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      const matchesCategory = !this.selectedCategory || 
        rule.category === this.selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }

  testRule(rule: Rule): void {
    this.snackBar.open(`Testing rule "${rule.name}"...`, 'OK', {
      duration: 2000
    });
    // Simulate rule execution
    setTimeout(() => {
      rule.executionCount++;
      this.snackBar.open(`Rule "${rule.name}" executed successfully`, 'OK', {
        duration: 2000
      });
    }, 1000);
  }
}