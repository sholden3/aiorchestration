import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from '../../services/config.service';

interface Template {
  template_id: string;
  name: string;
  description: string;
  category: string;
  template_content: string;
  variables: string[];
  tags: string[];
  created_by: string;
  usage_count?: number;
}

@Component({
  selector: 'app-templates',
  templateUrl: './templates.component.html',
  styleUrls: ['./templates.component.scss']
})
export class TemplatesComponent implements OnInit {
  title = 'Templates Library';
  templates: Template[] = [];
  filteredTemplates: Template[] = [];
  categories: string[] = ['all', 'general', 'architecture', 'testing', 'security', 'performance'];
  selectedCategory = 'all';
  searchTerm = '';
  selectedTemplate: Template | null = null;
  isLoading = false;
  error = '';

  // Hardcoded templates for immediate use
  defaultTemplates: Template[] = [
    {
      template_id: 'TMPL-001',
      name: 'AI Agent Template',
      description: 'Template for creating new AI agents with persona integration',
      category: 'architecture',
      template_content: `class AIAgent:
    """AI Agent with multi-persona support"""
    
    def __init__(self, name: str, personas: List[Persona]):
        self.name = name
        self.personas = personas[:3]  # Maximum 3 personas
        self.tasks_completed = 0
        self.status = 'ready'
    
    async def execute_task(self, task: str):
        # Consult all personas for consensus
        decisions = await self.gather_persona_decisions(task)
        result = await self.reach_consensus(decisions)
        return result`,
      variables: ['name', 'personas', 'task'],
      tags: ['ai', 'agent', 'persona', 'architecture'],
      created_by: 'system',
      usage_count: 15
    },
    {
      template_id: 'TMPL-002',
      name: 'PTY Terminal Handler',
      description: 'Template for PTY terminal session management',
      category: 'general',
      template_content: `import pty
import os
import subprocess

class PTYTerminal:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.master, self.slave = pty.openpty()
        self.process = None
    
    def start_shell(self, shell='/bin/bash'):
        self.process = subprocess.Popen(
            [shell],
            stdin=self.slave,
            stdout=self.slave,
            stderr=self.slave,
            preexec_fn=os.setsid
        )`,
      variables: ['session_id', 'shell'],
      tags: ['terminal', 'pty', 'system'],
      created_by: 'system',
      usage_count: 8
    },
    {
      template_id: 'TMPL-003',
      name: 'Three-Persona Consensus',
      description: 'Template for implementing three-persona decision making',
      category: 'architecture',
      template_content: `async def reach_consensus(self, decisions: Dict[str, Any]):
    """Three-persona consensus algorithm"""
    
    # Dr. Sarah Chen - AI/Technical perspective
    sarah_vote = decisions.get('sarah_chen', {})
    
    # Marcus Rodriguez - Performance/Systems perspective  
    marcus_vote = decisions.get('marcus_rodriguez', {})
    
    # Emily Watson - UX/User perspective
    emily_vote = decisions.get('emily_watson', {})
    
    # Weighted consensus based on task type
    if self.is_technical_task():
        weights = {'sarah': 0.5, 'marcus': 0.3, 'emily': 0.2}
    elif self.is_performance_task():
        weights = {'sarah': 0.2, 'marcus': 0.6, 'emily': 0.2}
    else:  # UX/User task
        weights = {'sarah': 0.2, 'marcus': 0.2, 'emily': 0.6}
    
    return self.calculate_weighted_consensus(votes, weights)`,
      variables: ['decisions', 'weights'],
      tags: ['persona', 'consensus', 'governance'],
      created_by: 'system',
      usage_count: 12
    }
  ];

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.isLoading = true;
    this.error = '';
    
    // Try to load from backend
    const apiUrl = this.config.getApiUrl();
    this.http.get<{templates: Template[]}>(`${apiUrl}/templates`).subscribe({
      next: (response) => {
        this.templates = response.templates || this.defaultTemplates;
        this.filterTemplates();
        this.isLoading = false;
      },
      error: (error) => {
        // Fall back to default templates
        console.warn('Failed to load templates from backend, using defaults', error);
        this.templates = this.defaultTemplates;
        this.filterTemplates();
        this.isLoading = false;
      }
    });
  }

  filterTemplates(): void {
    this.filteredTemplates = this.templates.filter(template => {
      const matchesCategory = this.selectedCategory === 'all' || template.category === this.selectedCategory;
      const matchesSearch = !this.searchTerm || 
        template.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        template.description.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        template.tags.some(tag => tag.toLowerCase().includes(this.searchTerm.toLowerCase()));
      
      return matchesCategory && matchesSearch;
    });
  }

  selectTemplate(template: Template): void {
    this.selectedTemplate = template;
  }

  copyToClipboard(content: string): void {
    navigator.clipboard.writeText(content).then(() => {
      // Show success message
      console.log('Template copied to clipboard');
    });
  }

  onCategoryChange(): void {
    this.filterTemplates();
  }

  onSearchChange(): void {
    this.filterTemplates();
  }

  useTemplate(template: Template): void {
    // Increment usage count
    if (template.usage_count !== undefined) {
      template.usage_count++;
    }
    
    // Copy to clipboard
    this.copyToClipboard(template.template_content);
    
    // Could also emit event or navigate to code editor
    console.log('Using template:', template.name);
  }
}