import { Component, OnInit } from '@angular/core';
import { RulesApiService } from '../../services/api/rules-api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Rule, RuleSeverity, RuleStatus } from '../../models/backend-api.models';

@Component({
  selector: 'app-rules',
  templateUrl: './rules.component.html',
  styleUrls: ['./rules.component.scss']
})
export class RulesComponent implements OnInit {
  rules: Rule[] = [];
  categories = ['security', 'performance', 'governance', 'validation', 'documentation'];
  severities = Object.values(RuleSeverity);
  displayedColumns: string[] = ['status', 'title', 'category', 'severity', 'violations_count', 'actions'];
  selectedRule: Rule | null = null;
  searchQuery = '';
  selectedCategory = '';
  loading = false;

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

  toggleRule(rule: Rule): void {
    const newStatus = rule.status === RuleStatus.ACTIVE ? RuleStatus.INACTIVE : RuleStatus.ACTIVE;
    const update = { status: newStatus };
    
    this.rulesApi.updateRule(rule.id, update).subscribe({
      next: (updatedRule) => {
        rule.status = updatedRule.status;
        this.snackBar.open(`Rule "${rule.title}" ${rule.status}`, 'OK', {
          duration: 2000
        });
      },
      error: (error) => {
        console.error('Error updating rule:', error);
        this.snackBar.open('Failed to update rule', 'OK', { duration: 3000 });
      }
    });
  }

  editRule(rule: Rule): void {
    this.selectedRule = { ...rule }; // Create a copy for editing
  }

  deleteRule(rule: Rule): void {
    if (confirm(`Are you sure you want to delete rule "${rule.title}"?`)) {
      this.rulesApi.deleteRule(rule.id).subscribe({
        next: () => {
          const index = this.rules.findIndex(r => r.id === rule.id);
          if (index > -1) {
            this.rules.splice(index, 1);
          }
          this.snackBar.open(`Rule "${rule.title}" deleted`, 'OK', {
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
    const newRule: Partial<Rule> = {
      title: 'New Rule',
      description: 'Rule description',
      category: 'governance',
      severity: RuleSeverity.MEDIUM,
      status: RuleStatus.DRAFT,
      tags: [],
      conditions: [],
      actions: [],
      exceptions: []
    };
    this.selectedRule = newRule as Rule;
  }

  saveRule(): void {
    if (this.selectedRule) {
      if (this.selectedRule.id) {
        // Update existing rule
        this.rulesApi.updateRule(this.selectedRule.id, this.selectedRule).subscribe({
          next: (updatedRule) => {
            const index = this.rules.findIndex(r => r.id === updatedRule.id);
            if (index > -1) {
              this.rules[index] = updatedRule;
            }
            this.snackBar.open(`Rule "${updatedRule.title}" updated`, 'OK', {
              duration: 2000
            });
            this.selectedRule = null;
          },
          error: (error) => {
            console.error('Error updating rule:', error);
            this.snackBar.open('Failed to update rule', 'OK', { duration: 3000 });
          }
        });
      } else {
        // Create new rule
        this.rulesApi.createRule(this.selectedRule).subscribe({
          next: (createdRule) => {
            this.rules.push(createdRule);
            this.snackBar.open(`Rule "${createdRule.title}" created`, 'OK', {
              duration: 2000
            });
            this.selectedRule = null;
          },
          error: (error) => {
            console.error('Error creating rule:', error);
            this.snackBar.open('Failed to create rule', 'OK', { duration: 3000 });
          }
        });
      }
    }
  }

  cancelEdit(): void {
    this.selectedRule = null;
  }

  get filteredRules(): Rule[] {
    return this.rules.filter(rule => {
      const matchesSearch = !this.searchQuery || 
        rule.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        rule.description.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      const matchesCategory = !this.selectedCategory || 
        rule.category === this.selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }

  enforceRule(rule: Rule): void {
    this.snackBar.open(`Enforcing rule "${rule.title}"...`, 'OK', {
      duration: 2000
    });
    
    this.rulesApi.enforceRule(rule.id).subscribe({
      next: (result) => {
        this.snackBar.open(
          `Rule "${rule.title}" enforced. Violations: ${result.violations_found}`, 
          'OK', 
          { duration: 3000 }
        );
        // Update violations count
        rule.violations_count = (rule.violations_count || 0) + result.violations_found;
      },
      error: (error) => {
        console.error('Error enforcing rule:', error);
        this.snackBar.open('Failed to enforce rule', 'OK', { duration: 3000 });
      }
    });
  }
}