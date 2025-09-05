/**
 * @fileoverview Practices API Service
 * @author Alex Novak - Frontend/Integration Architect
 * @description Service for interacting with backend Practices API
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry, map } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import {
  PracticeBase,
  PracticeCreate,
  PracticeUpdate,
  PracticeResponse,
  PracticeListResponse,
  PracticeVote,
  PracticeApplication,
  ApiError
} from '../../models/backend-api.models';

@Injectable({
  providedIn: 'root'
})
export class PracticesApiService {
  private apiUrl: string = '';
  
  constructor(
    private http: HttpClient,
    private appConfig: AppConfigService
  ) {
    this.apiUrl = this.appConfig.getEndpointUrl('/practices');
  }
  
  /**
   * Get list of practices with optional filtering
   */
  getPractices(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    min_effectiveness?: number;
  }): Observable<PracticeListResponse> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.category) httpParams = httpParams.set('category', params.category);
      if (params.min_effectiveness !== undefined) {
        httpParams = httpParams.set('min_effectiveness', params.min_effectiveness.toString());
      }
    }
    
    return this.http.get<PracticeListResponse>(`${this.apiUrl}/`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get a specific practice by ID
   */
  getPractice(practiceId: string): Observable<PracticeResponse> {
    return this.http.get<PracticeResponse>(`${this.apiUrl}/${practiceId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Create a new practice
   */
  createPractice(practice: PracticeCreate): Observable<PracticeResponse> {
    return this.http.post<PracticeResponse>(`${this.apiUrl}/`, practice)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Update an existing practice
   */
  updatePractice(practiceId: string, update: PracticeUpdate): Observable<PracticeResponse> {
    return this.http.put<PracticeResponse>(`${this.apiUrl}/${practiceId}`, update)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Delete a practice
   */
  deletePractice(practiceId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${practiceId}`)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Vote on a practice's effectiveness
   */
  votePractice(practiceId: string, vote: PracticeVote): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${practiceId}/vote`, vote)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Record an application of a practice
   */
  applyPractice(practiceId: string, application: PracticeApplication): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${practiceId}/apply`, application)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Get top practices by effectiveness
   */
  getTopPractices(limit: number = 10): Observable<PracticeResponse[]> {
    return this.getPractices({ limit: 100 }).pipe(
      map(response => {
        return response.practices
          .sort((a, b) => (b.effectiveness_score || 0) - (a.effectiveness_score || 0))
          .slice(0, limit);
      })
    );
  }
  
  /**
   * Get most adopted practices
   */
  getMostAdopted(limit: number = 10): Observable<PracticeResponse[]> {
    return this.getPractices({ limit: 100 }).pipe(
      map(response => {
        return response.practices
          .sort((a, b) => (b.adoption_rate || 0) - (a.adoption_rate || 0))
          .slice(0, limit);
      })
    );
  }
  
  /**
   * Get practices by category
   */
  getPracticesByCategory(category: string): Observable<PracticeResponse[]> {
    return this.getPractices({ category, limit: 100 }).pipe(
      map(response => response.practices)
    );
  }
  
  /**
   * Search practices by text
   */
  searchPractices(searchText: string): Observable<PracticeResponse[]> {
    return this.getPractices({ limit: 1000 }).pipe(
      map(response => {
        const lowerSearch = searchText.toLowerCase();
        return response.practices.filter(practice => 
          practice.name.toLowerCase().includes(lowerSearch) ||
          practice.description?.toLowerCase().includes(lowerSearch) ||
          practice.category?.toLowerCase().includes(lowerSearch) ||
          practice.implementation_guide?.toLowerCase().includes(lowerSearch)
        );
      })
    );
  }
  
  /**
   * Get all unique categories
   */
  getCategories(): Observable<string[]> {
    return this.getPractices({ limit: 1000 }).pipe(
      map(response => {
        const categories = new Set<string>();
        response.practices.forEach(practice => {
          if (practice.category) {
            categories.add(practice.category);
          }
        });
        return Array.from(categories).sort();
      })
    );
  }
  
  /**
   * Calculate ROI for a practice based on votes
   */
  calculateROI(practice: PracticeResponse): number {
    const votes_up = practice.votes_up || 0;
    const votes_down = practice.votes_down || 0;
    const total_votes = votes_up + votes_down;
    
    if (total_votes === 0) return 0;
    
    return (votes_up / total_votes) * 100;
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
    
    console.error('PracticesApiService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}