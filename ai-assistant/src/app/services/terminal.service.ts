import { Injectable, NgZone, OnDestroy } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { TerminalManagerService } from './terminal-manager.service';
import { IPCService } from './ipc.service';

export interface TerminalSession {
  id: string;
  shell: string;
  cwd: string;
  created: number;
  lastActivity: number;
  outputLines: number;
  implementation?: string;
}

export interface TerminalOutput {
  sessionId: string;
  data: string;
  timestamp: number;
}

// Type declaration for the electronAPI exposed by preload script
declare global {
  interface Window {
    electronAPI?: {
      createTerminalSession: (options: any) => Promise<string>;
      writeToTerminal: (sessionId: string, data: string) => void;
      resizeTerminal: (sessionId: string, cols: number, rows: number) => void;
      killTerminal: (sessionId: string) => void;
      getTerminalSessions: () => Promise<TerminalSession[]>;
      getTerminalOutput: (sessionId: string, fromIndex: number) => Promise<any[]>;
      onTerminalOutput: (callback: (data: TerminalOutput) => void) => () => void;
      onTerminalExit: (callback: (data: any) => void) => () => void;
      onTerminalSessions: (callback: (sessions: TerminalSession[]) => void) => () => void;
    }
  }
}

/**
 * @fileoverview Terminal service with PTY management and IPC communication
 * @author Alex Novak v3.0 - 2025-01-27
 * @fixes C1: Terminal Service Memory Leak
 * @architecture Frontend Service Layer
 * @references docs/fixes/C1-terminal-service-memory-leak.md
 * @testing_strategy Memory leak detection, cleanup verification
 * @governance Alex's 3AM Test - full debugging capability
 * @assumptions 
 *   - IPC listeners must be explicitly cleaned up
 *   - Angular doesn't auto-cleanup root services
 * @hook_points
 *   - Terminal lifecycle monitoring
 *   - Resource cleanup verification
 * 
 * FIX C1: Terminal Service - Refactored to component-scoped pattern
 * Removed 'providedIn: root' to allow proper lifecycle management
 * Now properly cleans up IPC listeners when component is destroyed
 * 
 * Architecture: Alex Novak v3.0
 * Memory Management: Explicit cleanup on destroy with monitoring
 * 3AM Test: Full debugging with correlation IDs and cleanup verification
 */
@Injectable()  // FIX C1: REMOVED providedIn: 'root' - now component-scoped
export class TerminalService implements OnDestroy {
  private outputSubject = new Subject<TerminalOutput>();
  private sessionsSubject = new Subject<TerminalSession[]>();
  private exitSubject = new Subject<any>();
  private cleanupFunctions: Array<() => void> = [];
  private isDestroyed = false;  // FIX C1: Track destruction state
  private instanceId: string;  // FIX C1: Unique instance ID for debugging
  private createdAt: number;   // FIX C1: Creation timestamp for leak tracking
  
  public output$ = this.outputSubject.asObservable();
  public sessions$ = this.sessionsSubject.asObservable();
  public exit$ = this.exitSubject.asObservable();

  constructor(
    private ngZone: NgZone,
    private terminalManager: TerminalManagerService,  // FIX C1: Inject manager
    private ipcService: IPCService  // SECURITY: Inject IPC security service
  ) {
    // FIX C1: Initialize debugging properties
    this.instanceId = `terminal-service-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.createdAt = Date.now();
    
    // Register with manager for lifecycle tracking
    this.terminalManager.register(this);
    
    console.log(`[${this.instanceId}] TerminalService initializing...`);
    console.log(`[${this.instanceId}] Is Electron?`, this.isElectron());
    console.log(`[${this.instanceId}] electronAPI available?`, typeof window !== 'undefined' ? window.electronAPI : 'window not defined');
    
    if (this.isElectron()) {
      this.initializeListeners();
    }
    
    // FIX C1: 3AM Debug Hook - Log successful initialization
    console.log(`[${this.instanceId}] Terminal service initialized successfully at ${new Date(this.createdAt).toISOString()}`);
  }

  private isElectron(): boolean {
    return typeof window !== 'undefined' && window.electronAPI !== undefined;
  }

  private initializeListeners(): void {
    if (!this.isElectron() || !window.electronAPI) {
      console.warn(`[${this.instanceId}] Cannot initialize terminal listeners - not in Electron environment`);
      return;
    }

    console.log(`[${this.instanceId}] Initializing terminal IPC listeners...`);

    // Listen for terminal output
    const outputCleanup = window.electronAPI.onTerminalOutput((data: TerminalOutput) => {
      console.log(`[${this.instanceId}] Received terminal output:`, data);
      
      // FIX C1: Prevent processing if service is destroyed
      if (this.isDestroyed) {
        console.warn(`[${this.instanceId}] Ignoring output - service destroyed`);
        return;
      }
      
      this.ngZone.run(() => {
        this.outputSubject.next(data);
      });
    });
    this.cleanupFunctions.push(outputCleanup);
    console.log(`[${this.instanceId}] Output listener registered (${this.cleanupFunctions.length} total)`);

    // Listen for terminal exit
    const exitCleanup = window.electronAPI.onTerminalExit((data: any) => {
      console.log(`[${this.instanceId}] Terminal exited:`, data);
      
      // FIX C1: Prevent processing if service is destroyed
      if (this.isDestroyed) {
        console.warn(`[${this.instanceId}] Ignoring exit - service destroyed`);
        return;
      }
      
      this.ngZone.run(() => {
        this.exitSubject.next(data);
      });
    });
    this.cleanupFunctions.push(exitCleanup);
    console.log(`[${this.instanceId}] Exit listener registered (${this.cleanupFunctions.length} total)`);

    // Listen for session updates
    const sessionsCleanup = window.electronAPI.onTerminalSessions((sessions: TerminalSession[]) => {
      console.log(`[${this.instanceId}] Sessions updated:`, sessions);
      
      // FIX C1: Prevent processing if service is destroyed
      if (this.isDestroyed) {
        console.warn(`[${this.instanceId}] Ignoring sessions - service destroyed`);
        return;
      }
      
      this.ngZone.run(() => {
        this.sessionsSubject.next(sessions);
      });
    });
    this.cleanupFunctions.push(sessionsCleanup);
    console.log(`[${this.instanceId}] Sessions listener registered (${this.cleanupFunctions.length} total)`);

    console.log(`[${this.instanceId}] Terminal IPC listeners initialized - ${this.cleanupFunctions.length} listeners tracked`);
  }

  async createSession(shell?: string, cwd?: string): Promise<string> {
    const sessionId = `session-${Date.now()}`;
    return this.createSessionWithId(sessionId, shell, cwd);
  }

  async createSessionWithId(sessionId: string, shell?: string, cwd?: string): Promise<string> {
    if (!this.isElectron()) {
      // Mock session for development without Electron
      console.log('Created mock terminal session:', sessionId);
      
      // Simulate terminal output for development
      setTimeout(() => {
        this.outputSubject.next({
          sessionId: sessionId,
          data: 'Welcome to AI Development Assistant Terminal (Mock Mode)\r\n> ',
          timestamp: Date.now()
        });
      }, 100);
      
      return Promise.resolve(sessionId);
    }
    
    if (!window.electronAPI) {
      throw new Error('electronAPI not available');
    }
    
    console.log(`[${this.instanceId}] Creating terminal session:`, { sessionId, shell, cwd });
    
    try {
      // Use IPC security service instead of direct electronAPI access
      const result = await this.ipcService.safeInvoke<string>('create-terminal-session', {
        sessionId,
        shell,
        cwd
      }, {
        timeout: 10000,  // 10 second timeout for session creation
        retries: 1
      });
      
      console.log(`[${this.instanceId}] Terminal session created successfully:`, result);
      return result || sessionId;
    } catch (error) {
      console.error(`[${this.instanceId}] Failed to create terminal session:`, error);
      throw error;
    }
  }

  writeToSession(sessionId: string, data: string): void {
    console.log(`[${this.instanceId}] Writing to terminal session:`, { sessionId, data: data.substring(0, 100) });
    
    if (!this.isElectron()) {
      // Mock echo for development
      console.log('Mock terminal write:', data);
      this.outputSubject.next({
        sessionId,
        data: data,
        timestamp: Date.now()
      });
      
      // Simulate command output
      if (data.trim() && !data.startsWith('\x1b')) {
        setTimeout(() => {
          this.outputSubject.next({
            sessionId,
            data: `Mock output for: ${data}> `,
            timestamp: Date.now()
          });
        }, 100);
      }
      return;
    }
    
    // Use IPC security service for terminal writes
    this.ipcService.safeInvoke('terminal-write', {
      sessionId,
      data
    }).catch(error => {
      console.error(`[${this.instanceId}] Failed to write to terminal:`, error);
    });
  }

  resizeSession(sessionId: string, cols: number, rows: number): void {
    if (!this.isElectron()) {
      console.log('Mock terminal resize:', { cols, rows });
      return;
    }
    
    console.log(`[${this.instanceId}] Resizing terminal:`, { sessionId, cols, rows });
    
    // Use IPC security service for terminal resize
    this.ipcService.safeInvoke('terminal-resize', {
      sessionId,
      cols,
      rows
    }).catch(error => {
      console.error(`[${this.instanceId}] Failed to resize terminal:`, error);
    });
  }

  killSession(sessionId: string): void {
    if (!this.isElectron()) {
      console.log('Mock terminal kill:', sessionId);
      this.exitSubject.next({ sessionId, exitCode: 0 });
      return;
    }
    
    console.log(`[${this.instanceId}] Killing terminal session:`, sessionId);
    
    // Use IPC security service for terminal kill
    this.ipcService.safeInvoke('terminal-kill', {
      sessionId
    }).catch(error => {
      console.error(`[${this.instanceId}] Failed to kill terminal:`, error);
    });
  }

  async getActiveSessions(): Promise<TerminalSession[]> {
    if (!this.isElectron()) {
      return Promise.resolve([]);
    }
    
    try {
      const sessions = await this.ipcService.safeInvoke<TerminalSession[]>('get-terminal-sessions', {}, {
        timeout: 5000,
        fallbackValue: []
      });
      
      console.log(`[${this.instanceId}] Active sessions:`, sessions);
      return sessions || [];
    } catch (error) {
      console.error(`[${this.instanceId}] Failed to get terminal sessions:`, error);
      return [];
    }
  }

  async getSessionOutput(sessionId: string, fromIndex: number = 0): Promise<any[]> {
    if (!this.isElectron()) {
      return Promise.resolve([]);
    }
    
    try {
      const output = await this.ipcService.safeInvoke<any[]>('get-terminal-output', {
        sessionId,
        fromIndex
      }, {
        timeout: 5000,
        fallbackValue: []
      });
      
      console.log(`[${this.instanceId}] Session output:`, output);
      return output || [];
    } catch (error) {
      console.error(`[${this.instanceId}] Failed to get terminal output:`, error);
      return [];
    }
  }
  
  /**
   * FIX C1: Proper cleanup implementation
   * This will be called when the component using this service is destroyed
   */
  ngOnDestroy(): void {
    this.forceCleanup();
  }
  
  /**
   * FIX C1: Force cleanup method - can be called directly or via manager
   * Ensures all resources are properly released
   * 3AM Test: Comprehensive logging for debugging memory leaks
   */
  forceCleanup(): void {
    if (this.isDestroyed) {
      console.warn(`[${this.instanceId}] Cleanup already executed - ignoring duplicate call`);
      return;
    }
    
    const cleanupStartTime = Date.now();
    const serviceLifetime = cleanupStartTime - this.createdAt;
    
    console.log(`[${this.instanceId}] Terminal service cleanup initiated`);
    console.log(`[${this.instanceId}] Service lifetime: ${serviceLifetime}ms (${Math.round(serviceLifetime/1000)}s)`);
    console.log(`[${this.instanceId}] IPC listeners to cleanup: ${this.cleanupFunctions.length}`);
    
    this.isDestroyed = true;
    
    // Clean up all IPC listeners with individual tracking
    let cleanupErrors = 0;
    this.cleanupFunctions.forEach((cleanup, index) => {
      try {
        console.log(`[${this.instanceId}] Cleaning up listener ${index + 1}/${this.cleanupFunctions.length}`);
        cleanup();
      } catch (error) {
        cleanupErrors++;
        console.error(`[${this.instanceId}] Cleanup error for listener ${index + 1}:`, error);
      }
    });
    this.cleanupFunctions = [];
    
    // Complete all observables to prevent memory leaks
    try {
      this.outputSubject.complete();
      this.sessionsSubject.complete();
      this.exitSubject.complete();
      console.log(`[${this.instanceId}] All observables completed successfully`);
    } catch (error) {
      console.error(`[${this.instanceId}] Error completing observables:`, error);
    }
    
    // Unregister from manager
    if (this.terminalManager) {
      try {
        this.terminalManager.unregister(this);
        console.log(`[${this.instanceId}] Unregistered from terminal manager`);
      } catch (error) {
        console.error(`[${this.instanceId}] Error unregistering from manager:`, error);
      }
    }
    
    const cleanupDuration = Date.now() - cleanupStartTime;
    console.log(`[${this.instanceId}] Terminal service cleanup complete in ${cleanupDuration}ms`);
    console.log(`[${this.instanceId}] Cleanup summary: ${cleanupErrors} errors, ${this.cleanupFunctions.length} remaining listeners`);
    
    // FIX C1: 3AM Debug Hook - Final verification
    if (cleanupErrors > 0 || this.cleanupFunctions.length > 0) {
      console.error(`[${this.instanceId}] ⚠️  CLEANUP INCOMPLETE - May cause memory leak!`);
    } else {
      console.log(`[${this.instanceId}] ✅ Cleanup verified - No memory leak risk`);
    }
  }
  
  /**
   * FIX C1: 3AM Debugging Utilities
   * Provides runtime inspection capabilities for memory leak investigation
   */
  getDebugInfo(): any {
    return {
      instanceId: this.instanceId,
      createdAt: this.createdAt,
      createdAtISO: new Date(this.createdAt).toISOString(),
      lifeTimeMs: Date.now() - this.createdAt,
      isDestroyed: this.isDestroyed,
      activeListeners: this.cleanupFunctions.length,
      hasOutputSubscribers: this.outputSubject.observers.length,
      hasSessionsSubscribers: this.sessionsSubject.observers.length,
      hasExitSubscribers: this.exitSubject.observers.length,
      memoryRisk: this.isDestroyed ? 'NO_RISK' : 
                  this.cleanupFunctions.length > 0 ? 'POTENTIAL_LEAK' : 'LOW_RISK'
    };
  }
  
  /**
   * FIX C1: Global debug hook - accessible from browser console
   * Usage in DevTools: window.getTerminalDebugInfo()
   */
  static attachGlobalDebugHook(terminalManager: TerminalManagerService): void {
    if (typeof window !== 'undefined') {
      (window as any).getTerminalDebugInfo = () => {
        const debugInfo: any[] = [];
        (terminalManager as any).activeServices.forEach((service: TerminalService) => {
          if (service.getDebugInfo) {
            debugInfo.push(service.getDebugInfo());
          }
        });
        
        return {
          totalServices: debugInfo.length,
          activeServices: debugInfo.filter(info => !info.isDestroyed).length,
          destroyedServices: debugInfo.filter(info => info.isDestroyed).length,
          potentialLeaks: debugInfo.filter(info => info.memoryRisk === 'POTENTIAL_LEAK').length,
          services: debugInfo
        };
      };
      
      console.log('🔧 Terminal debug utilities attached to window.getTerminalDebugInfo()');
    }
  }
}