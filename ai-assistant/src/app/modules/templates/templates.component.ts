import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TemplatesApiService } from '../../services/api/templates-api.service';
import { Template, TemplateType } from '../../models/backend-api.models';

@Component({
  selector: 'app-templates',
  templateUrl: './templates.component.html',
  styleUrls: ['./templates.component.scss']
})
export class TemplatesComponent implements OnInit {
  title = 'Templates Library';
  templates: Template[] = [];
  filteredTemplates: Template[] = [];
  templateTypes = Object.values(TemplateType);
  categories: string[] = ['code', 'documentation', 'configuration', 'testing', 'deployment'];
  selectedCategory = '';
  selectedType: TemplateType | '' = '';
  searchTerm = '';
  selectedTemplate: Template | null = null;
  isLoading = false;
  editMode = false;
  templateForm: Partial<Template> = {};
  renderVariables: Record<string, string> = {};
  renderedContent = '';

  constructor(
    private templatesApi: TemplatesApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.isLoading = true;
    
    this.templatesApi.getTemplates({ limit: 100 }).subscribe({
      next: (response) => {
        this.templates = response.templates;
        this.filterTemplates();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Failed to load templates:', error);
        this.snackBar.open('Failed to load templates', 'OK', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  filterTemplates(): void {
    this.filteredTemplates = this.templates.filter(template => {
      const matchesCategory = !this.selectedCategory || template.category === this.selectedCategory;
      const matchesType = !this.selectedType || template.type === this.selectedType;
      const matchesSearch = !this.searchTerm || 
        template.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        template.description.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        template.tags.some(tag => tag.toLowerCase().includes(this.searchTerm.toLowerCase()));
      
      return matchesCategory && matchesType && matchesSearch;
    });
  }

  selectTemplate(template: Template): void {
    this.selectedTemplate = template;
    this.editMode = false;
    this.renderedContent = '';
    // Initialize render variables
    this.renderVariables = {};
    template.variables.forEach(v => {
      this.renderVariables[v] = '';
    });
  }

  editTemplate(template: Template): void {
    this.selectedTemplate = template;
    this.templateForm = { ...template };
    this.editMode = true;
  }

  createTemplate(): void {
    this.templateForm = {
      name: '',
      description: '',
      type: TemplateType.CODE,
      category: 'code',
      content: '',
      variables: [],
      tags: []
    };
    this.editMode = true;
    this.selectedTemplate = null;
  }

  saveTemplate(): void {
    if (!this.templateForm.name || !this.templateForm.content) {
      this.snackBar.open('Name and content are required', 'OK', { duration: 3000 });
      return;
    }

    if (this.selectedTemplate?.id) {
      // Update existing
      this.templatesApi.updateTemplate(this.selectedTemplate.id, this.templateForm).subscribe({
        next: (updated) => {
          const index = this.templates.findIndex(t => t.id === updated.id);
          if (index > -1) {
            this.templates[index] = updated;
          }
          this.filterTemplates();
          this.snackBar.open('Template updated successfully', 'OK', { duration: 3000 });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error updating template:', error);
          this.snackBar.open('Failed to update template', 'OK', { duration: 3000 });
        }
      });
    } else {
      // Create new
      this.templatesApi.createTemplate(this.templateForm).subscribe({
        next: (created) => {
          this.templates.push(created);
          this.filterTemplates();
          this.snackBar.open('Template created successfully', 'OK', { duration: 3000 });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error creating template:', error);
          this.snackBar.open('Failed to create template', 'OK', { duration: 3000 });
        }
      });
    }
  }

  deleteTemplate(template: Template): void {
    if (confirm(`Are you sure you want to delete "${template.name}"?`)) {
      this.templatesApi.deleteTemplate(template.id).subscribe({
        next: () => {
          this.templates = this.templates.filter(t => t.id !== template.id);
          this.filterTemplates();
          this.snackBar.open('Template deleted successfully', 'OK', { duration: 3000 });
          this.selectedTemplate = null;
        },
        error: (error) => {
          console.error('Error deleting template:', error);
          this.snackBar.open('Failed to delete template', 'OK', { duration: 3000 });
        }
      });
    }
  }

  renderTemplate(): void {
    if (!this.selectedTemplate) return;
    
    this.templatesApi.renderTemplate(this.selectedTemplate.id, {
      variables: this.renderVariables
    }).subscribe({
      next: (result) => {
        this.renderedContent = result.rendered_content;
        this.snackBar.open('Template rendered successfully', 'OK', { duration: 2000 });
      },
      error: (error) => {
        console.error('Error rendering template:', error);
        this.snackBar.open('Failed to render template', 'OK', { duration: 3000 });
      }
    });
  }

  cloneTemplate(template: Template): void {
    this.templatesApi.cloneTemplate(template.id, {
      new_name: `${template.name} (Copy)`
    }).subscribe({
      next: (cloned) => {
        this.templates.push(cloned);
        this.filterTemplates();
        this.snackBar.open('Template cloned successfully', 'OK', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error cloning template:', error);
        this.snackBar.open('Failed to clone template', 'OK', { duration: 3000 });
      }
    });
  }

  copyToClipboard(content: string): void {
    navigator.clipboard.writeText(content).then(() => {
      this.snackBar.open('Copied to clipboard', 'OK', { duration: 2000 });
    });
  }

  cancelEdit(): void {
    this.editMode = false;
    this.templateForm = {};
    if (!this.selectedTemplate) {
      this.selectedTemplate = null;
    }
  }

  onCategoryChange(): void {
    this.filterTemplates();
  }

  onTypeChange(): void {
    this.filterTemplates();
  }

  onSearchChange(): void {
    this.filterTemplates();
  }
}