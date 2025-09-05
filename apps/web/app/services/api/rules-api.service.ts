/**
 * @fileoverview Rules API Service
 * @author Alex Novak - Frontend/Integration Architect
 * @description Service for interacting with backend Rules API
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry, map } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import {
  RuleBase,
  RuleCreate,
  RuleUpdate,
  RuleResponse,
  RuleListResponse,
  RuleStats,
  RuleEnforcementResult,
  RuleSeverity,
  RuleStatus,
  ApiError,
  PaginationParams
} from '../../models/backend-api.models';

@Injectable({
  providedIn: 'root'
})
export class RulesApiService {
  private apiUrl: string = '';
  
  constructor(
    private http: HttpClient,
    private appConfig: AppConfigService
  ) {
    // Initialize API URL from config
    this.apiUrl = this.appConfig.getEndpointUrl('/rules');
  }
  
  /**
   * Get list of rules with optional filtering
   */
  getRules(params?: {
    skip?: number;
    limit?: number;
    status?: RuleStatus;
    severity?: RuleSeverity;
    category?: string;
  }): Observable<RuleListResponse> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.status) httpParams = httpParams.set('status', params.status);
      if (params.severity) httpParams = httpParams.set('severity', params.severity);
      if (params.category) httpParams = httpParams.set('category', params.category);
    }
    
    return this.http.get<RuleListResponse>(`${this.apiUrl}/`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get rule statistics
   */
  getRuleStats(): Observable<RuleStats> {
    return this.http.get<RuleStats>(`${this.apiUrl}/stats`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get a specific rule by ID
   */
  getRule(ruleId: string): Observable<RuleResponse> {
    return this.http.get<RuleResponse>(`${this.apiUrl}/${ruleId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Create a new rule
   */
  createRule(rule: RuleCreate): Observable<RuleResponse> {
    return this.http.post<RuleResponse>(`${this.apiUrl}/`, rule)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Update an existing rule
   */
  updateRule(ruleId: string, update: RuleUpdate): Observable<RuleResponse> {
    return this.http.put<RuleResponse>(`${this.apiUrl}/${ruleId}`, update)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Delete a rule (soft delete - sets status to DEPRECATED)
   */
  deleteRule(ruleId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${ruleId}`)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Enforce a rule against given context
   */
  enforceRule(ruleId: string, context: Record<string, any>): Observable<RuleEnforcementResult> {
    return this.http.post<RuleEnforcementResult>(`${this.apiUrl}/${ruleId}/enforce`, context)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Get all unique categories from rules
   */
  getCategories(): Observable<string[]> {
    return this.getRules({ limit: 1000 }).pipe(
      map(response => {
        const categories = new Set<string>();
        response.rules.forEach(rule => {
          if (rule.category) {
            categories.add(rule.category);
          }
        });
        return Array.from(categories).sort();
      })
    );
  }
  
  /**
   * Search rules by text
   */
  searchRules(searchText: string): Observable<RuleResponse[]> {
    return this.getRules({ limit: 1000 }).pipe(
      map(response => {
        const lowerSearch = searchText.toLowerCase();
        return response.rules.filter(rule => 
          rule.name.toLowerCase().includes(lowerSearch) ||
          rule.description?.toLowerCase().includes(lowerSearch) ||
          rule.category?.toLowerCase().includes(lowerSearch)
        );
      })
    );
  }
  
  /**
   * Get active rules only
   */
  getActiveRules(): Observable<RuleResponse[]> {
    return this.getRules({ status: RuleStatus.ACTIVE, limit: 1000 }).pipe(
      map(response => response.rules)
    );
  }
  
  /**
   * Batch enforce multiple rules
   */
  batchEnforceRules(ruleIds: string[], context: Record<string, any>): Observable<RuleEnforcementResult[]> {
    const requests = ruleIds.map(id => this.enforceRule(id, context));
    return new Observable(observer => {
      Promise.all(requests.map(req => req.toPromise()))
        .then(results => {
          observer.next(results);
          observer.complete();
        })
        .catch(error => observer.error(error));
    });
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
    
    console.error('RulesApiService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}