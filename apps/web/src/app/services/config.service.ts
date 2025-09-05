import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { AppConfigService } from './app-config.service';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  
  constructor(private appConfig: AppConfigService) {}
  
  // Get API URL from centralized config
  getApiUrl(): string {
    // Use centralized config service
    return this.appConfig.getApiUrl();
  }
  
  // Check if running in Electron
  private isElectron(): boolean {
    return this.appConfig.isElectron();
  }
  
  // Get WebSocket URL for real-time connections
  getWebSocketUrl(): string {
    return this.appConfig.getWebSocketUrl();
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