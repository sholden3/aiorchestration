import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  // Backend API configuration
  private readonly DEFAULT_API_HOST = '127.0.0.1';
  private readonly DEFAULT_API_PORT = 8001;
  private readonly DEFAULT_API_PROTOCOL = 'http';
  
  // Get API URL from environment or use defaults
  getApiUrl(): string {
    if (environment.production) {
      // In production, use relative URLs or configured endpoint
      return environment.apiUrl || '/api';
    }
    
    // In development, check if running in Electron
    if (this.isElectron()) {
      // Electron app connects to local backend
      return `${this.DEFAULT_API_PROTOCOL}://${this.DEFAULT_API_HOST}:${this.DEFAULT_API_PORT}`;
    }
    
    // Web development mode
    return environment.apiUrl || `${this.DEFAULT_API_PROTOCOL}://${this.DEFAULT_API_HOST}:${this.DEFAULT_API_PORT}`;
  }
  
  // Check if running in Electron
  private isElectron(): boolean {
    return typeof window !== 'undefined' && window.electronAPI !== undefined;
  }
  
  // Get WebSocket URL for real-time connections
  getWebSocketUrl(): string {
    const apiUrl = this.getApiUrl();
    return apiUrl.replace(/^http/, 'ws');
  }
  
  // Get specific service endpoints
  getEndpoints() {
    const baseUrl = this.getApiUrl();
    return {
      health: `${baseUrl}/health`,
      orchestration: {
        status: `${baseUrl}/orchestration/status`,
        execute: `${baseUrl}/ai/orchestrated`,
        simple: `${baseUrl}/ai/execute`
      },
      cache: {
        metrics: `${baseUrl}/metrics/cache`,
        clear: `${baseUrl}/cache/clear`
      },
      metrics: {
        performance: `${baseUrl}/metrics/performance`,
        cache: `${baseUrl}/metrics/cache`
      },
      rules: {
        base: `${baseUrl}/api/rules`,
        execute: `${baseUrl}/api/rules/execute`,
        validate: `${baseUrl}/api/rules/validate`
      },
      personas: {
        suggest: `${baseUrl}/persona/suggest`,
        list: `${baseUrl}/personas`
      }
    };
  }
  
  // Get configuration values
  getConfig() {
    return {
      apiUrl: this.getApiUrl(),
      wsUrl: this.getWebSocketUrl(),
      isElectron: this.isElectron(),
      isDevelopment: !environment.production,
      endpoints: this.getEndpoints()
    };
  }
}