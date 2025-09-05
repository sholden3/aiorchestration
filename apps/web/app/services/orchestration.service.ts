import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ConfigService } from './config.service';

export interface OrchestrationStatus {
  is_running: boolean;
  agents: {
    total: number;
    active: number;
    idle: number;
    busy: number;
  };
  tasks: {
    queued: number;
    active: number;
    completed: number;
    failed: number;
  };
  performance: {
    total_tokens_used: number;
    average_response_time: number;
    overall_success_rate: number;
  };
  governance_active: boolean;
  persona_orchestration_active: boolean;
}

export interface TaskRequest {
  prompt: string;
  persona?: string;
  context: any;
  use_cache: boolean;
}

export interface TaskResponse {
  success: boolean;
  response: string;
  cached: boolean;
  tokens_saved: number;
  persona_used: string;
  execution_time_ms: number;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class OrchestrationService {
  private endpoints: any;
  private statusSubject = new BehaviorSubject<OrchestrationStatus | null>(null);
  public status$ = this.statusSubject.asObservable();

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {
    this.endpoints = this.config.getEndpoints();
  }

  getStatus(): Observable<OrchestrationStatus> {
    return this.http.get<OrchestrationStatus>(this.endpoints.orchestration.status)
      .pipe(tap(status => this.statusSubject.next(status)));
  }

  executeOrchestrated(request: TaskRequest): Observable<TaskResponse> {
    return this.http.post<TaskResponse>(this.endpoints.orchestration.execute, request);
  }

  executeSimple(request: TaskRequest): Observable<TaskResponse> {
    return this.http.post<TaskResponse>(this.endpoints.orchestration.simple, request);
  }

  getHealth(): Observable<any> {
    return this.http.get(this.endpoints.health);
  }

  getCacheMetrics(): Observable<any> {
    return this.http.get(this.endpoints.cache.metrics);
  }

  clearCache(): Observable<any> {
    return this.http.post(this.endpoints.cache.clear, {});
  }

  getPerformanceMetrics(): Observable<any> {
    return this.http.get(this.endpoints.metrics.performance);
  }
}