import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { PracticesApiService } from '../../services/api/practices-api.service';
import { PracticeResponse, PracticeCreate, PracticeUpdate } from '../../models/backend-api.models';

@Component({
  selector: 'app-practices',
  templateUrl: './practices.component.html',
  styleUrls: ['./practices.component.scss']
})
export class PracticesComponent implements OnInit {
  title = 'Best Practices Management';
  practices: PracticeResponse[] = [];
  filteredPractices: PracticeResponse[] = [];
  categories = ['architecture', 'testing', 'security', 'performance', 'documentation', 'governance'];
  loading = false;
  searchQuery = '';
  selectedCategory = '';
  selectedPractice: PracticeResponse | null = null;
  displayedColumns = ['name', 'category', 'votes', 'adoption_rate', 'actions'];
  
  // For creating/editing
  editMode = false;
  practiceForm: Partial<PracticeCreate> = {};

  constructor(
    private practicesApi: PracticesApiService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadPractices();
  }

  loadPractices(): void {
    this.loading = true;
    this.practicesApi.getPractices({ limit: 100 }).subscribe({
      next: (response) => {
        this.practices = response.practices;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading practices:', error);
        this.snackBar.open('Failed to load best practices', 'OK', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.filteredPractices = this.practices.filter(practice => {
      const matchesSearch = !this.searchQuery || 
        practice.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (practice.description?.toLowerCase().includes(this.searchQuery.toLowerCase()) || false);
      
      const matchesCategory = !this.selectedCategory || 
        practice.category === this.selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onCategoryChange(): void {
    this.applyFilters();
  }

  viewPractice(practice: PracticeResponse): void {
    this.selectedPractice = practice;
    this.editMode = false;
  }

  editPractice(practice: PracticeResponse): void {
    this.selectedPractice = practice;
    this.practiceForm = { ...practice };
    this.editMode = true;
  }

  createPractice(): void {
    this.practiceForm = {
      name: '',
      description: '',
      category: 'architecture',
      implementation_guide: '',
      benefits: [],
      challenges: [],
      examples: [],
      tags: []
    };
    this.editMode = true;
    this.selectedPractice = null;
  }

  savePractice(): void {
    if (!this.practiceForm.name || !this.practiceForm.description) {
      this.snackBar.open('Name and description are required', 'OK', { duration: 3000 });
      return;
    }

    if (this.selectedPractice?.id) {
      // Update existing practice
      this.practicesApi.updatePractice(this.selectedPractice.id, this.practiceForm as PracticeUpdate).subscribe({
        next: (updated) => {
          const index = this.practices.findIndex(p => p.id === updated.id);
          if (index > -1) {
            this.practices[index] = updated;
          }
          this.applyFilters();
          this.snackBar.open('Practice updated successfully', 'OK', { duration: 3000 });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error updating practice:', error);
          this.snackBar.open('Failed to update practice', 'OK', { duration: 3000 });
        }
      });
    } else {
      // Create new practice
      this.practicesApi.createPractice(this.practiceForm as PracticeCreate).subscribe({
        next: (created) => {
          this.practices.push(created);
          this.applyFilters();
          this.snackBar.open('Practice created successfully', 'OK', { duration: 3000 });
          this.cancelEdit();
        },
        error: (error) => {
          console.error('Error creating practice:', error);
          this.snackBar.open('Failed to create practice', 'OK', { duration: 3000 });
        }
      });
    }
  }

  deletePractice(practice: PracticeResponse): void {
    if (confirm(`Are you sure you want to delete "${practice.name}"?`)) {
      this.practicesApi.deletePractice(practice.id).subscribe({
        next: () => {
          this.practices = this.practices.filter(p => p.id !== practice.id);
          this.applyFilters();
          this.snackBar.open('Practice deleted successfully', 'OK', { duration: 3000 });
        },
        error: (error) => {
          console.error('Error deleting practice:', error);
          this.snackBar.open('Failed to delete practice', 'OK', { duration: 3000 });
        }
      });
    }
  }

  votePractice(practice: PracticeResponse, vote: 'up' | 'down'): void {
    this.practicesApi.votePractice(practice.id, { vote_type: vote }).subscribe({
      next: (result) => {
        if (vote === 'up') {
          practice.votes_up = (practice.votes_up || 0) + 1;
        } else {
          practice.votes_down = (practice.votes_down || 0) + 1;
        }
        this.snackBar.open(`Vote recorded`, 'OK', { duration: 2000 });
      },
      error: (error) => {
        console.error('Error voting:', error);
        this.snackBar.open('Failed to record vote', 'OK', { duration: 3000 });
      }
    });
  }

  applyPractice(practice: PracticeResponse): void {
    this.practicesApi.applyPractice(practice.id, {
      project_id: 'current-project',
      notes: 'Applied from UI'
    }).subscribe({
      next: (result) => {
        practice.adoption_rate = (practice.adoption_rate || 0) + 0.01;
        this.snackBar.open(`Practice applied successfully`, 'OK', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error applying practice:', error);
        this.snackBar.open('Failed to apply practice', 'OK', { duration: 3000 });
      }
    });
  }

  cancelEdit(): void {
    this.editMode = false;
    this.selectedPractice = null;
    this.practiceForm = {};
  }

  addTag(event: any): void {
    const value = event.value || event;
    if (value && this.practiceForm.tags) {
      this.practiceForm.tags.push(value.trim());
    }
  }

  removeTag(tag: string): void {
    if (this.practiceForm.tags) {
      const index = this.practiceForm.tags.indexOf(tag);
      if (index >= 0) {
        this.practiceForm.tags.splice(index, 1);
      }
    }
  }
}