/**
 * @fileoverview Centralized configuration service for frontend
 * @author Alex Novak - Frontend/Integration Architect
 * @description Loads and manages application configuration from centralized JSON files
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';

export interface AppConfig {
  app: {
    name: string;
    version: string;
    environment: string;
  };
  backend: {
    host: string;
    port: number;
    protocol: string;
    api_prefix: string;
    health_check_path: string;
    websocket?: {
      enabled: boolean;
      ping_interval: number;
      ping_timeout: number;
    };
  };
  frontend: {
    dev_server?: {
      host: string;
      port: number;
    };
    electron?: {
      window: {
        width: number;
        height: number;
        minWidth: number;
        minHeight: number;
      };
      dev_tools: boolean;
    };
    api?: {
      timeout: number;
      retry_attempts: number;
      retry_delay: number;
    };
  };
  ipc?: {
    max_message_size: number;
    rate_limit: {
      window: number;
      max_calls: number;
    };
    channels: {
      whitelist_enabled: boolean;
      audit_enabled: boolean;
    };
  };
  terminal?: {
    shell: {
      windows: string;
      linux: string;
      darwin: string;
    };
    pty: {
      cols: number;
      rows: number;
      cwd?: string;
    };
  };
  logging?: {
    level: string;
    format: string;
    console: {
      enabled: boolean;
      colorize: boolean;
    };
  };
  security?: {
    auth: {
      enabled: boolean;
      jwt_secret?: string;
      token_expiry: number;
    };
    rate_limiting: {
      enabled: boolean;
      requests_per_minute: number;
    };
  };
  features?: {
    ai_integration: {
      enabled: boolean;
      provider: string;
      model?: string;
      max_tokens?: number;
    };
    governance: {
      enabled: boolean;
      audit_all_operations: boolean;
      enforce_rules: boolean;
    };
    templates: {
      enabled: boolean;
      cache_rendered: boolean;
    };
    practices: {
      enabled: boolean;
      voting_enabled: boolean;
    };
  };
}

@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
  private config$ = new BehaviorSubject<AppConfig | null>(null);
  private configUrl = '/config/app.config.json';
  private environment = this.detectEnvironment();
  
  constructor(private http: HttpClient) {
    this.loadConfiguration();
  }
  
  /**
   * Detect the current environment
   */
  private detectEnvironment(): string {
    // Check if running in Electron
    if (this.isElectron()) {
      // In Electron, check for development mode
      return (window as any).electronAPI?.isDevelopment ? 'development' : 'production';
    }
    
    // Check Angular environment
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'development';
    }
    
    return 'production';
  }
  
  /**
   * Load configuration from JSON files
   */
  private loadConfiguration(): void {
    // Try to load config from local file first (for Electron)
    if (this.isElectron()) {
      this.loadElectronConfig();
    } else {
      this.loadWebConfig();
    }
  }
  
  /**
   * Load configuration for Electron app
   */
  private loadElectronConfig(): void {
    // In Electron, config should be loaded via IPC from main process
    if ((window as any).electronAPI?.getConfig) {
      (window as any).electronAPI.getConfig().then((config: AppConfig) => {
        this.config$.next(config);
      }).catch((error: any) => {
        console.error('Failed to load Electron config:', error);
        this.loadDefaultConfig();
      });
    } else {
      this.loadDefaultConfig();
    }
  }
  
  /**
   * Load configuration for web app
   */
  private loadWebConfig(): void {
    // First try to load environment-specific config
    const envConfigUrl = `/config/app.config.${this.environment}.json`;
    
    this.http.get<AppConfig>(envConfigUrl).pipe(
      catchError(() => {
        // Fallback to base config
        return this.http.get<AppConfig>(this.configUrl);
      }),
      catchError(() => {
        // Fallback to default config
        console.warn('No config file found, using defaults');
        return of(this.getDefaultConfig());
      }),
      tap(config => this.config$.next(config))
    ).subscribe();
  }
  
  /**
   * Load default configuration
   */
  private loadDefaultConfig(): void {
    this.config$.next(this.getDefaultConfig());
  }
  
  /**
   * Get default configuration
   */
  private getDefaultConfig(): AppConfig {
    return {
      app: {
        name: 'AI Development Assistant',
        version: '2.0.0',
        environment: this.environment
      },
      backend: {
        host: '127.0.0.1',
        port: 8000,
        protocol: 'http',
        api_prefix: '/api',
        health_check_path: '/health',
        websocket: {
          enabled: true,
          ping_interval: 30,
          ping_timeout: 10
        }
      },
      frontend: {
        api: {
          timeout: 30000,
          retry_attempts: 3,
          retry_delay: 1000
        }
      },
      features: {
        ai_integration: {
          enabled: false,
          provider: 'mock'
        },
        governance: {
          enabled: true,
          audit_all_operations: true,
          enforce_rules: true
        },
        templates: {
          enabled: true,
          cache_rendered: true
        },
        practices: {
          enabled: true,
          voting_enabled: true
        }
      }
    };
  }
  
  /**
   * Get current configuration
   */
  getConfig(): Observable<AppConfig | null> {
    return this.config$.asObservable();
  }
  
  /**
   * Get current configuration synchronously
   */
  getConfigSync(): AppConfig | null {
    return this.config$.value;
  }
  
  /**
   * Get API URL
   */
  getApiUrl(): string {
    const config = this.config$.value;
    if (!config) {
      // Return default if config not loaded yet
      return 'http://127.0.0.1:8000';
    }
    
    const { protocol, host, port } = config.backend;
    return `${protocol}://${host}:${port}`;
  }
  
  /**
   * Get WebSocket URL
   */
  getWebSocketUrl(): string {
    const apiUrl = this.getApiUrl();
    return apiUrl.replace(/^http/, 'ws');
  }
  
  /**
   * Get specific endpoint URL
   */
  getEndpointUrl(path: string): string {
    const config = this.config$.value;
    const apiUrl = this.getApiUrl();
    const apiPrefix = config?.backend.api_prefix || '/api';
    
    // Ensure path starts with /
    if (!path.startsWith('/')) {
      path = '/' + path;
    }
    
    // If path already includes api prefix, don't add it again
    if (path.startsWith(apiPrefix)) {
      return apiUrl + path;
    }
    
    return apiUrl + apiPrefix + path;
  }
  
  /**
   * Check if running in Electron
   */
  isElectron(): boolean {
    return typeof window !== 'undefined' && 
           typeof (window as any).electronAPI !== 'undefined';
  }
  
  /**
   * Check if running in development mode
   */
  isDevelopment(): boolean {
    return this.environment === 'development';
  }
  
  /**
   * Check if running in production mode
   */
  isProduction(): boolean {
    return this.environment === 'production';
  }
  
  /**
   * Get feature flag
   */
  isFeatureEnabled(feature: string): boolean {
    const config = this.config$.value;
    if (!config?.features) return false;
    
    switch (feature) {
      case 'ai':
        return config.features.ai_integration?.enabled || false;
      case 'governance':
        return config.features.governance?.enabled || false;
      case 'templates':
        return config.features.templates?.enabled || false;
      case 'practices':
        return config.features.practices?.enabled || false;
      default:
        return false;
    }
  }
  
  /**
   * Reload configuration
   */
  reloadConfig(): void {
    this.loadConfiguration();
  }
}