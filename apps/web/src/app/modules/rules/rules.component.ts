import { Component, OnInit } from '@angular/core';
import { RulesApiService } from '../../services/api/rules-api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RuleResponse, RuleCreate, RuleUpdate, RuleSeverity, RuleStatus } from '../../models/backend-api.models';

@Component({
  selector: 'app-rules',
  templateUrl: './rules.component.html',
  styleUrls: ['./rules.component.scss']
})
export class RulesComponent implements OnInit {
  title = 'Rules Management';
  rules: RuleResponse[] = [];
  categories = ['security', 'performance', 'governance', 'validation', 'documentation'];
  severities = Object.values(RuleSeverity);
  displayedColumns: string[] = ['status', 'name', 'category', 'severity', 'violation_count', 'actions'];
  selectedRule: RuleResponse | null = null;
  searchQuery = '';
  selectedCategory = '';
  loading = false;
  editMode = false;
  ruleForm: Partial<RuleCreate> = {};

  constructor(
    private rulesApi: RulesApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadRules();
  }

  loadRules(): void {
    this.loading = true;
    this.rulesApi.getRules({ limit: 100 }).subscribe({
      next: (response) => {
        this.rules = response.rules;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading rules:', error);
        this.snackBar.open('Failed to load rules', 'OK', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  toggleRule(rule: RuleResponse): void {
    const newStatus = rule.status === RuleStatus.ACTIVE ? RuleStatus.INACTIVE : RuleStatus.ACTIVE;
    const update = { status: newStatus };
    
    this.rulesApi.updateRule(rule.id, update).subscribe({
      next: (updatedRule) => {
        rule.status = updatedRule.status;
        this.snackBar.open(`Rule "${rule.name}" ${rule.status}`, 'OK', {
          duration: 2000
        });
      },
      error: (error) => {
        console.error('Error updating rule:', error);
        this.snackBar.open('Failed to update rule', 'OK', { duration: 3000 });
      }
    });
  }

  editRule(rule: RuleResponse): void {
    this.selectedRule = { ...rule }; // Create a copy for editing
  }

  deleteRule(rule: RuleResponse): void {
    if (confirm(`Are you sure you want to delete rule "${rule.name}"?`)) {
      this.rulesApi.deleteRule(rule.id).subscribe({
        next: () => {
          const index = this.rules.findIndex(r => r.id === rule.id);
          if (index > -1) {
            this.rules.splice(index, 1);
          }
          this.snackBar.open(`Rule "${rule.name}" deleted`, 'OK', {
            duration: 2000
          });
        },
        error: (error) => {
          console.error('Error deleting rule:', error);
          this.snackBar.open('Failed to delete rule', 'OK', { duration: 3000 });
        }
      });
    }
  }

  addNewRule(): void {
    this.ruleForm = {
      name: 'New Rule',
      description: 'Rule description',
      category: 'governance',
      severity: RuleSeverity.MEDIUM,
      status: RuleStatus.DRAFT,
      condition: 'true',
      action: 'log',
      tags: []
    };
    this.editMode = true;
    this.selectedRule = null;
  }

  saveRule(): void {
    if (this.selectedRule?.id) {
      // Update existing rule
      this.rulesApi.updateRule(this.selectedRule.id, this.ruleForm as RuleUpdate).subscribe({
        next: (updatedRule) => {
          const index = this.rules.findIndex(r => r.id === updatedRule.id);
          if (index > -1) {
            this.rules[index] = updatedRule;
          }
          this.snackBar.open(`Rule "${updatedRule.name}" updated`, 'OK', {
            duration: 2000
          });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error updating rule:', error);
          this.snackBar.open('Failed to update rule', 'OK', { duration: 3000 });
        }
      });
    } else {
      // Create new rule
      this.rulesApi.createRule(this.ruleForm as RuleCreate).subscribe({
        next: (createdRule) => {
          this.rules.push(createdRule);
          this.snackBar.open(`Rule "${createdRule.name}" created`, 'OK', {
            duration: 2000
          });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error creating rule:', error);
          this.snackBar.open('Failed to create rule', 'OK', { duration: 3000 });
        }
      });
    }
  }

  cancelEdit(): void {
    this.selectedRule = null;
    this.editMode = false;
    this.ruleForm = {};
  }

  get filteredRules(): RuleResponse[] {
    return this.rules.filter(rule => {
      const matchesSearch = !this.searchQuery || 
        rule.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (rule.description?.toLowerCase().includes(this.searchQuery.toLowerCase()) || false);
      
      const matchesCategory = !this.selectedCategory || 
        rule.category === this.selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }

  enforceRule(rule: RuleResponse): void {
    this.snackBar.open(`Enforcing rule "${rule.name}"...`, 'OK', {
      duration: 2000
    });
    
    const context = { ruleId: rule.id, timestamp: new Date().toISOString() };
    this.rulesApi.enforceRule(rule.id, context).subscribe({
      next: (result) => {
        const violations = result.violations_found || 0;
        this.snackBar.open(
          `Rule "${rule.name}" enforced. Violations: ${violations}`, 
          'OK', 
          { duration: 3000 }
        );
        // Update violations count
        rule.violation_count = (rule.violation_count || 0) + violations;
      },
      error: (error) => {
        console.error('Error enforcing rule:', error);
        this.snackBar.open('Failed to enforce rule', 'OK', { duration: 3000 });
      }
    });
  }

  testRule(rule: RuleResponse): void {
    this.rulesApi.enforceRule(rule.id, {}).subscribe({
      next: (result) => {
        const message = result.passed ? 
          `Rule "${rule.name}" passed validation` : 
          `Rule "${rule.name}" failed: ${result.message}`;
        this.snackBar.open(message, 'OK', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error testing rule:', error);
        this.snackBar.open('Failed to test rule', 'OK', { duration: 3000 });
      }
    });
  }

  viewRule(rule: RuleResponse): void {
    this.selectedRule = rule;
    this.editMode = false;
  }

  getSeverityColor(severity?: RuleSeverity): string {
    if (!severity) return 'primary';
    switch (severity) {
      case RuleSeverity.CRITICAL:
      case RuleSeverity.ERROR:
        return 'warn';
      case RuleSeverity.MEDIUM:
        return 'accent';
      case RuleSeverity.WARNING:
        return 'accent';
      default:
        return 'primary';
    }
  }

  isRuleActive(rule: RuleResponse): boolean {
    return rule.status === RuleStatus.ACTIVE;
  }
}