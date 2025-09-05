import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';

export interface Rule {
  rule_id: string;
  category: string;
  title: string;
  description: string;
  severity: string;
  examples?: string[];
  anti_patterns?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface BestPractice {
  practice_id: string;
  category: string;
  title: string;
  description: string;
  benefits?: string[];
  implementation_guide?: string;
  anti_patterns?: string[];
  references?: string[];
  examples?: string[];
  is_active: boolean;
  is_required: boolean;
  priority?: string;
}

export interface Template {
  template_id: string;
  name: string;
  description: string;
  category: string;
  template_content: string;
  variables?: string[];
  tags?: string[];
  is_active: boolean;
  created_by?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  rules?: Rule[];
  practices?: BestPractice[];
  templates?: Template[];
  count?: number;
  error?: string;
}

export interface Statistics {
  total: number;
  by_category: { [key: string]: number };
  by_severity?: { [key: string]: number };
  by_priority?: { [key: string]: number };
  active?: number;
  required?: number;
}

@Injectable({
  providedIn: 'root'
})
export class RulesService {
  private baseUrl: string;

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {
    const endpoints = this.config.getEndpoints();
    this.baseUrl = endpoints.rules.base;
  }

  // Rules endpoints
  getRules(category?: string, severity?: string): Observable<ApiResponse<Rule[]>> {
    let params = new HttpParams();
    if (category) params = params.append('category', category);
    if (severity) params = params.append('severity', severity);
    
    return this.http.get<ApiResponse<Rule[]>>(`${this.baseUrl}/`, { params });
  }

  getRuleById(ruleId: string): Observable<ApiResponse<Rule>> {
    return this.http.get<ApiResponse<Rule>>(`${this.baseUrl}/${ruleId}`);
  }

  getRulesStats(): Observable<ApiResponse<Statistics>> {
    return this.http.get<ApiResponse<Statistics>>(`${this.baseUrl}/stats`);
  }

  // Best Practices endpoints
  getBestPractices(category?: string, priority?: string, isRequired?: boolean): Observable<ApiResponse<BestPractice[]>> {
    let params = new HttpParams();
    if (category) params = params.append('category', category);
    if (priority) params = params.append('priority', priority);
    if (isRequired !== undefined) params = params.append('is_required', isRequired.toString());
    
    // Use the parent API URL for practices
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<BestPractice[]>>(`${apiUrl}/practices/`, { params });
  }

  getPracticeById(practiceId: string): Observable<ApiResponse<BestPractice>> {
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<BestPractice>>(`${apiUrl}/practices/${practiceId}`);
  }

  getPracticesStats(): Observable<ApiResponse<Statistics>> {
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<Statistics>>(`${apiUrl}/practices/stats`);
  }

  // Templates endpoints  
  getTemplates(category?: string, tag?: string): Observable<ApiResponse<Template[]>> {
    let params = new HttpParams();
    if (category) params = params.append('category', category);
    if (tag) params = params.append('tag', tag);
    
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<Template[]>>(`${apiUrl}/templates/`, { params });
  }

  getTemplateById(templateId: string): Observable<ApiResponse<Template>> {
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<Template>>(`${apiUrl}/templates/${templateId}`);
  }

  getTemplatesStats(): Observable<ApiResponse<Statistics>> {
    const apiUrl = this.baseUrl.replace('/rules', '');
    return this.http.get<ApiResponse<Statistics>>(`${apiUrl}/templates/stats`);
  }

  // Utility method to get all categories
  getCategories(): Observable<string[]> {
    // Extract unique categories from practices
    return new Observable(observer => {
      this.getBestPractices().subscribe(response => {
        if (response.success && response.practices) {
          const categories = [...new Set(response.practices.map(p => p.category))];
          observer.next(categories);
          observer.complete();
        } else {
          observer.error('Failed to fetch categories');
        }
      });
    });
  }
}