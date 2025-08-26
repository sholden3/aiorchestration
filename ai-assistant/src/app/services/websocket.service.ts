import { Injectable, NgZone } from '@angular/core';
import { Observable, Subject, BehaviorSubject, timer } from 'rxjs';
import { ConfigService } from './config.service';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
  event_type?: string;
}

export interface OrchestrationUpdate {
  type: 'orchestration_status';
  data: any;
}

export interface CacheMetricsUpdate {
  type: 'cache_metrics';
  data: any;
}

export interface TaskUpdate {
  type: 'task_update';
  task_id: string;
  status: string;
  details?: any;
}

export interface PersonaDecision {
  type: 'persona_decision';
  persona: string;
  decision: string;
  confidence: number;
}

export interface AssumptionValidation {
  type: 'assumption_validation';
  assumption: string;
  validated: boolean;
  challenger?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket?: WebSocket;
  private messagesSubject = new Subject<WebSocketMessage>();
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);
  private reconnectTimer?: any;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // Start with 2 seconds
  
  // Specific event subjects
  private orchestrationUpdates = new Subject<OrchestrationUpdate>();
  private cacheMetricsUpdates = new Subject<CacheMetricsUpdate>();
  private taskUpdates = new Subject<TaskUpdate>();
  private personaDecisions = new Subject<PersonaDecision>();
  private assumptionValidations = new Subject<AssumptionValidation>();
  
  // Public observables
  public messages$ = this.messagesSubject.asObservable();
  public connectionStatus$ = this.connectionStatusSubject.asObservable();
  public orchestrationUpdates$ = this.orchestrationUpdates.asObservable();
  public cacheMetricsUpdates$ = this.cacheMetricsUpdates.asObservable();
  public taskUpdates$ = this.taskUpdates.asObservable();
  public personaDecisions$ = this.personaDecisions.asObservable();
  public assumptionValidations$ = this.assumptionValidations.asObservable();

  constructor(
    private config: ConfigService,
    private ngZone: NgZone
  ) {}

  connect(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = this.getWebSocketUrl();
    console.log('Connecting to WebSocket:', wsUrl);

    try {
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = (event) => {
        console.log('WebSocket connected');
        this.ngZone.run(() => {
          this.connectionStatusSubject.next(true);
          this.reconnectAttempts = 0;
          this.reconnectDelay = 2000;
        });
        
        // Subscribe to all events
        this.sendMessage({
          type: 'subscribe',
          events: [
            'orchestration_status',
            'cache_metrics',
            'task_update',
            'persona_decision',
            'assumption_validation',
            'system_alert',
            'performance_metric'
          ]
        });
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.ngZone.run(() => {
            this.handleMessage(message);
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected');
        this.ngZone.run(() => {
          this.connectionStatusSubject.next(false);
          this.attemptReconnect();
        });
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    // Emit to general messages subject
    this.messagesSubject.next(message);
    
    // Route to specific subjects based on type
    switch (message.type) {
      case 'orchestration_status':
        this.orchestrationUpdates.next(message as OrchestrationUpdate);
        break;
      case 'cache_metrics':
        this.cacheMetricsUpdates.next(message as CacheMetricsUpdate);
        break;
      case 'task_update':
        this.taskUpdates.next(message as TaskUpdate);
        break;
      case 'persona_decision':
        this.personaDecisions.next(message as PersonaDecision);
        break;
      case 'assumption_validation':
        this.assumptionValidations.next(message as AssumptionValidation);
        break;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
      // Exponential backoff
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
    }, this.reconnectDelay);
  }

  sendMessage(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = undefined;
    }
  }

  private getWebSocketUrl(): string {
    const apiUrl = this.config.getApiUrl();
    // Convert http to ws, https to wss
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const baseUrl = apiUrl.replace(/^https?/, wsProtocol);
    return `${baseUrl}/ws`;
  }

  // Utility methods for common operations
  ping(): void {
    this.sendMessage({ type: 'ping' });
  }

  requestStatus(): void {
    this.sendMessage({ type: 'request_status' });
  }

  subscribeToEvents(events: string[]): void {
    this.sendMessage({
      type: 'subscribe',
      events: events
    });
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}