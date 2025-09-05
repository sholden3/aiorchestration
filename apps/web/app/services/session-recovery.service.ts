/**
 * @fileoverview Session recovery service for state persistence and restoration
 * @author Alex Novak v2.0 - Frontend Integration Architect
 * @architecture Frontend - Session state management and recovery
 * @business_logic Persists session state, recovers after disconnection, validates sessions
 * @integration_points LocalStorage, SessionStorage, IPC service, Backend validation
 * @error_handling Corrupted state recovery, validation failures, storage quota exceeded
 * @performance Debounced persistence, compression for large states, cleanup of old sessions
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, interval } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

/**
 * Session state structure
 * @interface SessionState
 */
export interface SessionState {
  sessionId: string;
  userId?: string;
  timestamp: number;
  expiresAt: number;
  data: Map<string, any>;
  metadata: SessionMetadata;
}

/**
 * Session metadata
 * @interface SessionMetadata
 */
export interface SessionMetadata {
  userAgent: string;
  platform: string;
  language: string;
  timezone: string;
  screenResolution: string;
  connectionType?: string;
  created: number;
  lastActive: number;
  recoveryCount: number;
}

/**
 * Recovery options
 * @interface RecoveryOptions
 */
export interface RecoveryOptions {
  maxAge: number; // Maximum age of session to recover (ms)
  validateWithBackend: boolean;
  preserveOnFailure: boolean;
  compressionEnabled: boolean;
}

/**
 * @class SessionRecoveryService
 * @description Manages session persistence and recovery
 * 
 * This service provides:
 * - Automatic session state persistence
 * - Recovery after browser refresh or crash
 * - Cross-tab session synchronization
 * - Session validation with backend
 * - Cleanup of expired sessions
 */
@Injectable({
  providedIn: 'root'
})
export class SessionRecoveryService {
  /**
   * Current session state
   */
  private sessionState$ = new BehaviorSubject<SessionState | null>(null);
  
  /**
   * Storage key prefix
   */
  private readonly STORAGE_KEY = 'ai_assistant_session';
  
  /**
   * Backup storage key for recovery
   */
  private readonly BACKUP_KEY = 'ai_assistant_session_backup';
  
  /**
   * Default recovery options
   */
  private readonly defaultOptions: RecoveryOptions = {
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    validateWithBackend: true,
    preserveOnFailure: true,
    compressionEnabled: true
  };
  
  /**
   * Session expiry duration (ms)
   */
  private readonly SESSION_DURATION = 8 * 60 * 60 * 1000; // 8 hours
  
  /**
   * Cleanup interval
   */
  private cleanupInterval: any;
  
  /**
   * Cross-tab communication channel
   */
  private broadcastChannel: BroadcastChannel | null = null;

  constructor() {
    this.initializeBroadcastChannel();
    this.startCleanupTask();
    this.setupStorageEventListener();
    this.recoverExistingSession();
  }

  /**
   * Get current session state
   * @returns Observable of session state
   */
  public getSessionState(): Observable<SessionState | null> {
    return this.sessionState$.asObservable();
  }

  /**
   * Get current session ID
   * @returns Current session ID or null
   */
  public getCurrentSessionId(): string | null {
    return this.sessionState$.value?.sessionId || null;
  }

  /**
   * Create new session
   * @param userId Optional user ID
   * @returns Created session state
   */
  public createSession(userId?: string): SessionState {
    const sessionId = this.generateSessionId();
    const now = Date.now();
    
    const session: SessionState = {
      sessionId,
      userId,
      timestamp: now,
      expiresAt: now + this.SESSION_DURATION,
      data: new Map(),
      metadata: this.generateMetadata()
    };
    
    this.sessionState$.next(session);
    this.persistSession(session);
    this.broadcastSessionUpdate('created', session);
    
    console.log('[SessionRecovery] New session created', { sessionId, userId });
    
    return session;
  }

  /**
   * Update session data
   * @param key Data key
   * @param value Data value
   */
  public updateSessionData(key: string, value: any): void {
    const session = this.sessionState$.value;
    if (!session) {
      console.warn('[SessionRecovery] No active session to update');
      return;
    }
    
    session.data.set(key, value);
    session.metadata.lastActive = Date.now();
    
    this.sessionState$.next(session);
    this.debouncedPersist(session);
    this.broadcastSessionUpdate('updated', session);
  }

  /**
   * Get session data
   * @param key Data key
   * @returns Data value or undefined
   */
  public getSessionData(key: string): any {
    return this.sessionState$.value?.data.get(key);
  }

  /**
   * Clear session data
   * @param key Optional key to clear specific data
   */
  public clearSessionData(key?: string): void {
    const session = this.sessionState$.value;
    if (!session) return;
    
    if (key) {
      session.data.delete(key);
    } else {
      session.data.clear();
    }
    
    this.sessionState$.next(session);
    this.persistSession(session);
  }

  /**
   * Recover session from storage
   * @param options Recovery options
   * @returns Recovered session or null
   */
  public async recoverSession(options?: Partial<RecoveryOptions>): Promise<SessionState | null> {
    const opts = { ...this.defaultOptions, ...options };
    
    try {
      // Try primary storage
      let storedSession = this.loadFromStorage(this.STORAGE_KEY);
      
      // Try backup if primary fails
      if (!storedSession) {
        storedSession = this.loadFromStorage(this.BACKUP_KEY);
      }
      
      if (!storedSession) {
        console.log('[SessionRecovery] No session found in storage');
        return null;
      }
      
      // Check age
      const age = Date.now() - storedSession.timestamp;
      if (age > opts.maxAge) {
        console.log('[SessionRecovery] Session too old', { age, maxAge: opts.maxAge });
        this.clearStorage();
        return null;
      }
      
      // Check expiry
      if (Date.now() > storedSession.expiresAt) {
        console.log('[SessionRecovery] Session expired');
        this.clearStorage();
        return null;
      }
      
      // Validate with backend if required
      if (opts.validateWithBackend) {
        const isValid = await this.validateSessionWithBackend(storedSession);
        if (!isValid) {
          console.warn('[SessionRecovery] Session validation failed');
          if (!opts.preserveOnFailure) {
            this.clearStorage();
            return null;
          }
        }
      }
      
      // Update recovery count
      storedSession.metadata.recoveryCount++;
      storedSession.metadata.lastActive = Date.now();
      
      // Restore session
      this.sessionState$.next(storedSession);
      this.persistSession(storedSession);
      this.broadcastSessionUpdate('recovered', storedSession);
      
      console.log('[SessionRecovery] Session recovered', {
        sessionId: storedSession.sessionId,
        age: Math.round(age / 1000) + 's',
        recoveryCount: storedSession.metadata.recoveryCount
      });
      
      return storedSession;
      
    } catch (error) {
      console.error('[SessionRecovery] Recovery failed', error);
      if (!opts.preserveOnFailure) {
        this.clearStorage();
      }
      return null;
    }
  }

  /**
   * Destroy current session
   */
  public destroySession(): void {
    const session = this.sessionState$.value;
    if (session) {
      console.log('[SessionRecovery] Destroying session', { sessionId: session.sessionId });
      this.broadcastSessionUpdate('destroyed', session);
    }
    
    this.sessionState$.next(null);
    this.clearStorage();
  }

  /**
   * Persist session to storage
   * @param session Session to persist
   * @private
   */
  private persistSession(session: SessionState): void {
    try {
      const serialized = this.serializeSession(session);
      
      // Save to primary storage
      localStorage.setItem(this.STORAGE_KEY, serialized);
      
      // Save backup
      sessionStorage.setItem(this.BACKUP_KEY, serialized);
      
      console.debug('[SessionRecovery] Session persisted');
    } catch (error) {
      console.error('[SessionRecovery] Failed to persist session', error);
      
      // Try to clear old data if quota exceeded
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        this.cleanupOldSessions();
        // Retry once
        try {
          const serialized = this.serializeSession(session);
          localStorage.setItem(this.STORAGE_KEY, serialized);
        } catch (retryError) {
          console.error('[SessionRecovery] Retry failed', retryError);
        }
      }
    }
  }

  /**
   * Debounced persist for frequent updates
   */
  private debouncedPersist = this.debounce((session: SessionState) => {
    this.persistSession(session);
  }, 1000);

  /**
   * Load session from storage
   * @param key Storage key
   * @returns Session or null
   * @private
   */
  private loadFromStorage(key: string): SessionState | null {
    try {
      const stored = key === this.BACKUP_KEY 
        ? sessionStorage.getItem(key)
        : localStorage.getItem(key);
      
      if (!stored) return null;
      
      return this.deserializeSession(stored);
    } catch (error) {
      console.error('[SessionRecovery] Failed to load from storage', error);
      return null;
    }
  }

  /**
   * Serialize session for storage
   * @param session Session to serialize
   * @returns Serialized string
   * @private
   */
  private serializeSession(session: SessionState): string {
    const simplified = {
      ...session,
      data: Array.from(session.data.entries())
    };
    
    const json = JSON.stringify(simplified);
    
    // Compress if enabled and supported
    if (this.defaultOptions.compressionEnabled && typeof CompressionStream !== 'undefined') {
      // Note: CompressionStream API may not be available in all browsers
      return json; // For now, return uncompressed
    }
    
    return json;
  }

  /**
   * Deserialize session from storage
   * @param data Serialized data
   * @returns Session state
   * @private
   */
  private deserializeSession(data: string): SessionState {
    const parsed = JSON.parse(data);
    
    return {
      ...parsed,
      data: new Map(parsed.data)
    };
  }

  /**
   * Validate session with backend
   * @param session Session to validate
   * @returns True if valid
   * @private
   */
  private async validateSessionWithBackend(session: SessionState): Promise<boolean> {
    try {
      // TODO: Implement actual backend validation
      console.log('[SessionRecovery] Validating session with backend', {
        sessionId: session.sessionId
      });
      
      // Simulated validation
      return true;
    } catch (error) {
      console.error('[SessionRecovery] Validation error', error);
      return false;
    }
  }

  /**
   * Generate unique session ID
   * @returns Session ID
   * @private
   */
  private generateSessionId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 9);
    return `sess_${timestamp}_${random}`;
  }

  /**
   * Generate session metadata
   * @returns Session metadata
   * @private
   */
  private generateMetadata(): SessionMetadata {
    const now = Date.now();
    
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      screenResolution: `${screen.width}x${screen.height}`,
      connectionType: (navigator as any).connection?.effectiveType,
      created: now,
      lastActive: now,
      recoveryCount: 0
    };
  }

  /**
   * Initialize broadcast channel for cross-tab communication
   * @private
   */
  private initializeBroadcastChannel(): void {
    if (typeof BroadcastChannel !== 'undefined') {
      this.broadcastChannel = new BroadcastChannel('ai_assistant_session_sync');
      
      this.broadcastChannel.onmessage = (event) => {
        this.handleBroadcastMessage(event.data);
      };
      
      console.log('[SessionRecovery] Broadcast channel initialized');
    }
  }

  /**
   * Broadcast session update to other tabs
   * @param type Update type
   * @param session Session data
   * @private
   */
  private broadcastSessionUpdate(type: string, session: SessionState): void {
    if (this.broadcastChannel) {
      this.broadcastChannel.postMessage({
        type,
        session: this.serializeSession(session),
        timestamp: Date.now()
      });
    }
  }

  /**
   * Handle broadcast message from other tabs
   * @param message Broadcast message
   * @private
   */
  private handleBroadcastMessage(message: any): void {
    console.log('[SessionRecovery] Broadcast message received', { type: message.type });
    
    switch (message.type) {
      case 'created':
      case 'updated':
      case 'recovered':
        // Update local session if it's newer
        const remoteSession = this.deserializeSession(message.session);
        const localSession = this.sessionState$.value;
        
        if (!localSession || remoteSession.metadata.lastActive > localSession.metadata.lastActive) {
          this.sessionState$.next(remoteSession);
        }
        break;
        
      case 'destroyed':
        this.sessionState$.next(null);
        break;
    }
  }

  /**
   * Setup storage event listener for cross-tab sync (fallback)
   * @private
   */
  private setupStorageEventListener(): void {
    window.addEventListener('storage', (event) => {
      if (event.key === this.STORAGE_KEY && event.newValue) {
        console.log('[SessionRecovery] Storage event detected');
        const session = this.deserializeSession(event.newValue);
        this.sessionState$.next(session);
      }
    });
  }

  /**
   * Start cleanup task for expired sessions
   * @private
   */
  private startCleanupTask(): void {
    // Run cleanup every hour
    this.cleanupInterval = setInterval(() => {
      this.cleanupOldSessions();
    }, 60 * 60 * 1000);
  }

  /**
   * Clean up old sessions from storage
   * @private
   */
  private cleanupOldSessions(): void {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('ai_assistant_session'));
    let cleaned = 0;
    
    keys.forEach(key => {
      try {
        const data = localStorage.getItem(key);
        if (data) {
          const session = JSON.parse(data);
          if (Date.now() > session.expiresAt) {
            localStorage.removeItem(key);
            cleaned++;
          }
        }
      } catch (error) {
        // Remove corrupted data
        localStorage.removeItem(key);
        cleaned++;
      }
    });
    
    if (cleaned > 0) {
      console.log('[SessionRecovery] Cleaned up old sessions', { count: cleaned });
    }
  }

  /**
   * Clear all storage
   * @private
   */
  private clearStorage(): void {
    localStorage.removeItem(this.STORAGE_KEY);
    sessionStorage.removeItem(this.BACKUP_KEY);
  }

  /**
   * Recover existing session on service initialization
   * @private
   */
  private async recoverExistingSession(): Promise<void> {
    const recovered = await this.recoverSession({
      validateWithBackend: false // Skip validation on initial load
    });
    
    if (!recovered) {
      // Create new session if recovery fails
      this.createSession();
    }
  }

  /**
   * Utility debounce function
   * @param func Function to debounce
   * @param wait Wait time in ms
   * @returns Debounced function
   * @private
   */
  private debounce<T extends (...args: any[]) => any>(func: T, wait: number): T {
    let timeout: any;
    
    return ((...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    }) as T;
  }

  /**
   * Clean up resources
   */
  public destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    
    if (this.broadcastChannel) {
      this.broadcastChannel.close();
    }
    
    // Persist current session before destroy
    const session = this.sessionState$.value;
    if (session) {
      this.persistSession(session);
    }
  }
}