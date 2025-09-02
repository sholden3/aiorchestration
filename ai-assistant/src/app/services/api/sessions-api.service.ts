/**
 * @fileoverview Sessions API Service
 * @author Alex Novak - Frontend/Integration Architect
 * @description Service for interacting with backend Sessions API
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, interval } from 'rxjs';
import { catchError, retry, map, switchMap } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import {
  SessionBase,
  SessionCreate,
  SessionUpdate,
  SessionResponse,
  SessionListResponse,
  SessionEnd,
  SessionMetrics,
  SessionStatus,
  ActiveSessionsResponse,
  AuditLog,
  AIDecision,
  ApiError
} from '../../models/backend-api.models';

@Injectable({
  providedIn: 'root'
})
export class SessionsApiService {
  private apiUrl: string = '';
  
  constructor(
    private http: HttpClient,
    private appConfig: AppConfigService
  ) {
    this.apiUrl = this.appConfig.getEndpointUrl('/sessions');
  }
  
  /**
   * Get list of sessions with optional filtering
   */
  getSessions(params?: {
    skip?: number;
    limit?: number;
    status?: SessionStatus;
    architect?: string;
  }): Observable<SessionListResponse> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.status) httpParams = httpParams.set('status', params.status);
      if (params.architect) httpParams = httpParams.set('architect', params.architect);
    }
    
    return this.http.get<SessionListResponse>(`${this.apiUrl}/`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get all currently active sessions
   */
  getActiveSessions(): Observable<ActiveSessionsResponse> {
    return this.http.get<ActiveSessionsResponse>(`${this.apiUrl}/active`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get session metrics and statistics
   */
  getSessionMetrics(): Observable<SessionMetrics> {
    return this.http.get<SessionMetrics>(`${this.apiUrl}/metrics`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get a specific session by ID
   */
  getSession(sessionId: string): Observable<SessionResponse> {
    return this.http.get<SessionResponse>(`${this.apiUrl}/${sessionId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Create a new development session
   */
  createSession(session: SessionCreate): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.apiUrl}/`, session)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Update an existing session
   */
  updateSession(sessionId: string, update: SessionUpdate): Observable<SessionResponse> {
    return this.http.put<SessionResponse>(`${this.apiUrl}/${sessionId}`, update)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * End a development session
   */
  endSession(sessionId: string, endData: SessionEnd): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.apiUrl}/${sessionId}/end`, endData)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Delete a session (soft delete - sets status to EXPIRED)
   */
  deleteSession(sessionId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${sessionId}`)
      .pipe(
        catchError(this.handleError)
      );
  }
  
  /**
   * Get all audit logs for a session
   */
  getSessionAuditLogs(sessionId: string, params?: {
    skip?: number;
    limit?: number;
  }): Observable<{
    session_id: string;
    logs: AuditLog[];
    total: number;
    skip: number;
    limit: number;
  }> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/${sessionId}/audit-logs`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Get all AI decisions for a session
   */
  getSessionDecisions(sessionId: string, params?: {
    skip?: number;
    limit?: number;
  }): Observable<{
    session_id: string;
    decisions: AIDecision[];
    total: number;
    skip: number;
    limit: number;
  }> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.skip !== undefined) httpParams = httpParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/${sessionId}/decisions`, { params: httpParams })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }
  
  /**
   * Start a new development session with auto-generated ID
   */
  startQuickSession(architects: string[]): Observable<SessionResponse> {
    const session: SessionCreate = {
      session_id: `session-${Date.now()}`,
      architects: architects,
      status: SessionStatus.ACTIVE,
      environment: {
        platform: navigator.platform,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      },
      metadata: {
        source: 'frontend',
        version: this.appConfig.getConfigSync()?.app.version
      }
    };
    
    return this.createSession(session);
  }
  
  /**
   * Get recent sessions (last 7 days)
   */
  getRecentSessions(days: number = 7): Observable<SessionResponse[]> {
    return this.getSessions({ limit: 100 }).pipe(
      map(response => {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        
        return response.sessions.filter(session => {
          const sessionDate = new Date(session.created_at);
          return sessionDate > cutoffDate;
        });
      })
    );
  }
  
  /**
   * Get sessions by architect
   */
  getSessionsByArchitect(architect: string): Observable<SessionResponse[]> {
    return this.getSessions({ architect, limit: 100 }).pipe(
      map(response => response.sessions)
    );
  }
  
  /**
   * Calculate total development time
   */
  getTotalDevelopmentTime(): Observable<number> {
    return this.getSessions({ limit: 1000 }).pipe(
      map(response => {
        return response.sessions.reduce((total, session) => {
          return total + (session.duration_minutes || 0);
        }, 0);
      })
    );
  }
  
  /**
   * Monitor active sessions (polling)
   */
  monitorActiveSessions(intervalMs: number = 30000): Observable<ActiveSessionsResponse> {
    return interval(intervalMs).pipe(
      switchMap(() => this.getActiveSessions())
    );
  }
  
  /**
   * Get session activity timeline
   */
  getSessionTimeline(sessionId: string): Observable<any[]> {
    // Combine audit logs and decisions into a timeline
    return new Observable(observer => {
      Promise.all([
        this.getSessionAuditLogs(sessionId, { limit: 100 }).toPromise(),
        this.getSessionDecisions(sessionId, { limit: 100 }).toPromise()
      ]).then(([auditData, decisionData]) => {
        const timeline: any[] = [];
        
        // Add audit logs to timeline
        if (auditData?.logs) {
          auditData.logs.forEach(log => {
            timeline.push({
              type: 'audit',
              timestamp: log.created_at,
              event: log.event_type,
              data: log
            });
          });
        }
        
        // Add decisions to timeline
        if (decisionData?.decisions) {
          decisionData.decisions.forEach(decision => {
            timeline.push({
              type: 'decision',
              timestamp: decision.created_at,
              event: decision.decision_type,
              data: decision
            });
          });
        }
        
        // Sort by timestamp
        timeline.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        
        observer.next(timeline);
        observer.complete();
      }).catch(error => observer.error(error));
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
    
    console.error('SessionsApiService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}