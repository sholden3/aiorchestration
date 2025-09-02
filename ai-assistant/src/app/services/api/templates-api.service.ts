/**
 * @fileoverview Templates API Service
 * @author Alex Novak - Frontend/Integration Architect
 * @description Service for interacting with backend Templates API
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, retry, map } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import {
  TemplateBase,
  TemplateCreate,
  TemplateUpdate,
  TemplateResponse,
  TemplateListResponse,
  TemplateRender,
  TemplateRenderResponse,
  TemplateType,
  TemplateTypesResponse,
  ApiError
} from '../../models/backend-api.models';

@Injectable({
  providedIn: 'root'
})
export class TemplatesApiService {
  private apiUrl: string = '';
  private renderCache = new Map<string, TemplateRenderResponse>();
  
  constructor(
    private http: HttpClient,
    private appConfig: AppConfigService
  ) {
    this.apiUrl = this.appConfig.getEndpointUrl('/templates');
  }
  
  /**
   * Get list of templates with optional filtering
   */
  getTemplates(params?: {
    skip?: number;
    limit?: number;
    type?: TemplateType;
    category?: string;
  }): Observable<TemplateListResponse> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.type) httpParams = httpParams.set('type', params.type);
      if (params.category) httpParams = httpParams.set('category', params.category);
    }
    
    return this.http.get<TemplateListResponse>(`${this.apiUrl}/`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get all available template types
   */
  getTemplateTypes(): Observable<TemplateTypesResponse> {
    return this.http.get<TemplateTypesResponse>(`${this.apiUrl}/types`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get a specific template by ID
   */
  getTemplate(templateId: string): Observable<TemplateResponse> {
    return this.http.get<TemplateResponse>(`${this.apiUrl}/${templateId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Create a new template
   */
  createTemplate(template: TemplateCreate): Observable<TemplateResponse> {
    return this.http.post<TemplateResponse>(`${this.apiUrl}/`, template)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Update an existing template
   */
  updateTemplate(templateId: string, update: TemplateUpdate): Observable<TemplateResponse> {
    // Clear render cache for this template
    this.clearRenderCache(templateId);
    
    return this.http.put<TemplateResponse>(`${this.apiUrl}/${templateId}`, update)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Delete a template
   */
  deleteTemplate(templateId: string): Observable<any> {
    // Clear render cache for this template
    this.clearRenderCache(templateId);
    
    return this.http.delete<any>(`${this.apiUrl}/${templateId}`)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Render a template with provided variables
   */
  renderTemplate(templateId: string, variables: Record<string, any>): Observable<TemplateRenderResponse> {
    // Check cache first
    const cacheKey = this.getCacheKey(templateId, variables);
    if (this.renderCache.has(cacheKey)) {
      return of(this.renderCache.get(cacheKey)!);
    }
    
    const renderRequest: TemplateRender = { variables };
    
    return this.http.post<TemplateRenderResponse>(
      `${this.apiUrl}/${templateId}/render`,
      renderRequest
    ).pipe(
      map(response => {
        // Cache successful renders
        if (response.validation_errors?.length === 0) {
          this.renderCache.set(cacheKey, response);
        }
        return response;
      }),
      catchError(this.handleError)
    );
  }
  
  /**
   * Clone an existing template
   */
  cloneTemplate(templateId: string, data: { new_name: string } | string): Observable<TemplateResponse> {
    const newName = typeof data === 'string' ? data : data.new_name;
    const params = new HttpParams().set('new_name', newName);
    
    return this.http.post<TemplateResponse>(
      `${this.apiUrl}/${templateId}/clone`,
      {},
      { params }
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  /**
   * Get templates by type
   */
  getTemplatesByType(type: TemplateType): Observable<TemplateResponse[]> {
    return this.getTemplates({ type, limit: 100 }).pipe(
      map(response => response.templates)
    );
  }
  
  /**
   * Get most used templates
   */
  getMostUsedTemplates(limit: number = 10): Observable<TemplateResponse[]> {
    return this.getTemplates({ limit: 100 }).pipe(
      map(response => {
        return response.templates
          .sort((a, b) => b.usage_count - a.usage_count)
          .slice(0, limit);
      })
    );
  }
  
  /**
   * Search templates by text
   */
  searchTemplates(searchText: string): Observable<TemplateResponse[]> {
    return this.getTemplates({ limit: 1000 }).pipe(
      map(response => {
        const lowerSearch = searchText.toLowerCase();
        return response.templates.filter(template => 
          template.name.toLowerCase().includes(lowerSearch) ||
          template.description?.toLowerCase().includes(lowerSearch) ||
          template.category?.toLowerCase().includes(lowerSearch) ||
          template.tags?.some(tag => tag.toLowerCase().includes(lowerSearch))
        );
      })
    );
  }
  
  /**
   * Get all unique categories
   */
  getCategories(): Observable<string[]> {
    return this.getTemplates({ limit: 1000 }).pipe(
      map(response => {
        const categories = new Set<string>();
        response.templates.forEach(template => {
          if (template.category) {
            categories.add(template.category);
          }
        });
        return Array.from(categories).sort();
      })
    );
  }
  
  /**
   * Validate template variables
   */
  validateVariables(template: TemplateResponse, variables: Record<string, any>): string[] {
    const errors: string[] = [];
    const requiredVars = Object.keys(template.variables || {});
    const providedVars = Object.keys(variables);
    
    // Check for missing required variables
    requiredVars.forEach(reqVar => {
      if (!providedVars.includes(reqVar)) {
        errors.push(`Missing required variable: ${reqVar}`);
      }
    });
    
    // Check for extra variables
    providedVars.forEach(provVar => {
      if (!requiredVars.includes(provVar)) {
        errors.push(`Unknown variable: ${provVar}`);
      }
    });
    
    return errors;
  }
  
  /**
   * Get template history (versions)
   */
  getTemplateHistory(templateId: string): Observable<TemplateResponse[]> {
    return this.getTemplates({ limit: 1000 }).pipe(
      map(response => {
        return response.templates.filter(t => 
          t.parent_id === templateId || t.id === templateId
        ).sort((a, b) => b.version - a.version);
      })
    );
  }
  
  /**
   * Generate cache key for render results
   */
  private getCacheKey(templateId: string, variables: Record<string, any>): string {
    return `${templateId}:${JSON.stringify(variables)}`;
  }
  
  /**
   * Clear render cache for a template
   */
  private clearRenderCache(templateId?: string): void {
    if (templateId) {
      // Clear specific template cache
      const keysToDelete: string[] = [];
      this.renderCache.forEach((_, key) => {
        if (key.startsWith(templateId + ':')) {
          keysToDelete.push(key);
        }
      });
      keysToDelete.forEach(key => this.renderCache.delete(key));
    } else {
      // Clear all cache
      this.renderCache.clear();
    }
  }
  
  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.error && error.error.detail) {
        errorMessage = error.error.detail;
      } else {
        errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      }
    }
    
    console.error('TemplatesApiService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}