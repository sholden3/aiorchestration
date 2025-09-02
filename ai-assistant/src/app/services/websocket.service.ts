import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { AppConfigService } from './app-config.service';

export interface WebSocketMessage {
  event?: string;
  type?: string;
  data: any;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messagesSubject = new Subject<WebSocketMessage>();
  public messages$ = this.messagesSubject.asObservable();
  
  private connectionStatusSubject = new Subject<boolean>();
  public connectionStatus$ = this.connectionStatusSubject.asObservable();
  
  private reconnectInterval = 5000; // 5 seconds
  private reconnectTimer: any;
  
  // Legacy observables for backward compatibility
  public orchestrationUpdates$ = new Subject<any>();
  public cacheMetricsUpdates$ = new Subject<any>();
  public taskUpdates$ = new Subject<any>();
  public personaDecisions$ = new Subject<any>();
  public assumptionValidations$ = new Subject<any>();

  constructor(private configService: AppConfigService) {
    // Auto-connect when service is created
    this.connect();
    
    // Map new messages to legacy observables
    this.messages$.subscribe(msg => {
      if (msg.event === 'orchestration.update') this.orchestrationUpdates$.next(msg.data);
      if (msg.event === 'cache.metrics') this.cacheMetricsUpdates$.next(msg.data);
      if (msg.event === 'task.update') this.taskUpdates$.next(msg.data);
      if (msg.event === 'persona.decision') this.personaDecisions$.next(msg.data);
      if (msg.event === 'assumption.validation') this.assumptionValidations$.next(msg.data);
    });
  }

  connect(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.configService.config$.subscribe(config => {
      const wsProtocol = config.backend.protocol === 'https' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://${config.backend.host}:${config.backend.port}/ws`;
      this.connectToWebSocket(wsUrl);
    });
  }

  private connectToWebSocket(wsUrl: string): void {
    console.log('Connecting to WebSocket:', wsUrl);
    
    try {
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.connectionStatusSubject.next(true);
        this.clearReconnectTimer();
      };
      
      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.messagesSubject.next(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.connectionStatusSubject.next(false);
        this.socket = null;
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.clearReconnectTimer();
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(event: string, data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = {
        event,
        data,
        timestamp: new Date().toISOString()
      };
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', event);
    }
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    console.log(`Scheduling reconnect in ${this.reconnectInterval}ms`);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  // Subscribe to specific event types
  onEvent(eventType: string): Observable<any> {
    return new Observable(observer => {
      const subscription = this.messages$.subscribe(message => {
        if (message.event === eventType) {
          observer.next(message.data);
        }
      });
      return () => subscription.unsubscribe();
    });
  }

  // Common event subscriptions
  onRuleUpdate(): Observable<any> {
    return this.onEvent('rule.updated');
  }

  onPracticeUpdate(): Observable<any> {
    return this.onEvent('practice.updated');
  }

  onTemplateUpdate(): Observable<any> {
    return this.onEvent('template.updated');
  }

  onCacheMetrics(): Observable<any> {
    return this.onEvent('cache.metrics');
  }

  onOrchestrationStatus(): Observable<any> {
    return this.onEvent('orchestration.status');
  }

  onGovernanceEvent(): Observable<any> {
    return this.onEvent('governance.event');
  }

  onNotification(): Observable<any> {
    return this.onEvent('notification');
  }
}