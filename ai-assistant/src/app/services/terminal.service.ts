import { Injectable, NgZone, OnDestroy } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { TerminalManagerService } from './terminal-manager.service';

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
 * FIX C1: Terminal Service - Refactored to component-scoped pattern
 * Removed 'providedIn: root' to allow proper lifecycle management
 * Now properly cleans up IPC listeners when component is destroyed
 * 
 * Architecture: Alex Novak
 * Memory Management: Explicit cleanup on destroy
 */
@Injectable()  // FIX C1: REMOVED providedIn: 'root' - now component-scoped
export class TerminalService implements OnDestroy {
  private outputSubject = new Subject<TerminalOutput>();
  private sessionsSubject = new Subject<TerminalSession[]>();
  private exitSubject = new Subject<any>();
  private cleanupFunctions: Array<() => void> = [];
  private isDestroyed = false;  // FIX C1: Track destruction state
  
  public output$ = this.outputSubject.asObservable();
  public sessions$ = this.sessionsSubject.asObservable();
  public exit$ = this.exitSubject.asObservable();

  constructor(
    private ngZone: NgZone,
    private terminalManager: TerminalManagerService  // FIX C1: Inject manager
  ) {
    // Register with manager for lifecycle tracking
    this.terminalManager.register(this);
    
    console.log('TerminalService initializing...');
    console.log('Is Electron?', this.isElectron());
    console.log('electronAPI available?', typeof window !== 'undefined' ? window.electronAPI : 'window not defined');
    
    if (this.isElectron()) {
      this.initializeListeners();
    }
  }

  private isElectron(): boolean {
    return typeof window !== 'undefined' && window.electronAPI !== undefined;
  }

  private initializeListeners(): void {
    if (!this.isElectron() || !window.electronAPI) {
      console.warn('Cannot initialize terminal listeners - not in Electron environment');
      return;
    }

    console.log('Initializing terminal IPC listeners...');

    // Listen for terminal output
    const outputCleanup = window.electronAPI.onTerminalOutput((data: TerminalOutput) => {
      console.log('Received terminal output:', data);
      this.ngZone.run(() => {
        this.outputSubject.next(data);
      });
    });
    this.cleanupFunctions.push(outputCleanup);

    // Listen for terminal exit
    const exitCleanup = window.electronAPI.onTerminalExit((data: any) => {
      console.log('Terminal exited:', data);
      this.ngZone.run(() => {
        this.exitSubject.next(data);
      });
    });
    this.cleanupFunctions.push(exitCleanup);

    // Listen for session updates
    const sessionsCleanup = window.electronAPI.onTerminalSessions((sessions: TerminalSession[]) => {
      console.log('Sessions updated:', sessions);
      this.ngZone.run(() => {
        this.sessionsSubject.next(sessions);
      });
    });
    this.cleanupFunctions.push(sessionsCleanup);

    console.log('Terminal IPC listeners initialized');
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
    
    console.log('Creating terminal session:', { sessionId, shell, cwd });
    
    try {
      const result = await window.electronAPI.createTerminalSession({
        sessionId,
        shell,
        cwd
      });
      console.log('Terminal session created successfully:', result);
      return result;
    } catch (error) {
      console.error('Failed to create terminal session:', error);
      throw error;
    }
  }

  writeToSession(sessionId: string, data: string): void {
    console.log('Writing to terminal session:', { sessionId, data });
    
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
    
    if (!window.electronAPI) {
      console.error('electronAPI not available for writeToSession');
      return;
    }
    
    window.electronAPI.writeToTerminal(sessionId, data);
  }

  resizeSession(sessionId: string, cols: number, rows: number): void {
    if (!this.isElectron()) {
      console.log('Mock terminal resize:', { cols, rows });
      return;
    }
    
    if (!window.electronAPI) {
      console.error('electronAPI not available for resizeSession');
      return;
    }
    
    console.log('Resizing terminal:', { sessionId, cols, rows });
    window.electronAPI.resizeTerminal(sessionId, cols, rows);
  }

  killSession(sessionId: string): void {
    if (!this.isElectron()) {
      console.log('Mock terminal kill:', sessionId);
      this.exitSubject.next({ sessionId, exitCode: 0 });
      return;
    }
    
    if (!window.electronAPI) {
      console.error('electronAPI not available for killSession');
      return;
    }
    
    console.log('Killing terminal session:', sessionId);
    window.electronAPI.killTerminal(sessionId);
  }

  async getActiveSessions(): Promise<TerminalSession[]> {
    if (!this.isElectron() || !window.electronAPI) {
      return Promise.resolve([]);
    }
    
    try {
      const sessions = await window.electronAPI.getTerminalSessions();
      console.log('Active sessions:', sessions);
      return sessions;
    } catch (error) {
      console.error('Failed to get terminal sessions:', error);
      return [];
    }
  }

  async getSessionOutput(sessionId: string, fromIndex: number = 0): Promise<any[]> {
    if (!this.isElectron() || !window.electronAPI) {
      return Promise.resolve([]);
    }
    
    try {
      const output = await window.electronAPI.getTerminalOutput(sessionId, fromIndex);
      console.log('Session output:', output);
      return output;
    } catch (error) {
      console.error('Failed to get terminal output:', error);
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
   */
  forceCleanup(): void {
    if (this.isDestroyed) return;
    
    console.log('Terminal service cleanup initiated');
    this.isDestroyed = true;
    
    // Clean up all IPC listeners
    this.cleanupFunctions.forEach(cleanup => {
      try {
        cleanup();
      } catch (error) {
        console.error('Cleanup error:', error);
      }
    });
    this.cleanupFunctions = [];
    
    // Complete all observables to prevent memory leaks
    this.outputSubject.complete();
    this.sessionsSubject.complete();
    this.exitSubject.complete();
    
    // Unregister from manager
    if (this.terminalManager) {
      this.terminalManager.unregister(this);
    }
    
    console.log('Terminal service cleanup complete');
  }
}