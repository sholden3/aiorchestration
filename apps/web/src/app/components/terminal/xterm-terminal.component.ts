/**
 * @fileoverview XTerm Terminal Component - Real PTY integration with xterm.js
 * @author Alex Novak v1.0 - 2025-08-29
 * @architecture Frontend - Terminal UI component with xterm.js
 * @responsibility Render terminal UI, handle user input, connect to PTY via IPC
 * @dependencies xterm.js, TerminalService, Angular core
 * @integration_points IPC bridge, PTY manager, terminal service
 * @testing_strategy Component tests, PTY integration tests
 * @governance Alex's 3AM Test - Full terminal debugging
 * 
 * Business Logic Summary:
 * - Create xterm.js terminal UI
 * - Connect to real PTY via IPC
 * - Handle terminal input/output
 * - Manage terminal lifecycle
 * 
 * Architecture Integration:
 * - Uses component-scoped TerminalService (C1 fix)
 * - Connects to main process PTY via IPC
 * - Full ANSI color support via xterm.js
 */

import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Input, AfterViewInit } from '@angular/core';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { TerminalService, TerminalOutput } from '../../services/terminal.service';
import { Subscription } from 'rxjs';

/**
 * @class XtermTerminalComponent
 * @description Terminal component using xterm.js for full terminal emulation
 * @architecture_role Terminal UI with real PTY connection
 * @business_logic Full terminal emulation with PTY backend
 * @failure_modes PTY spawn failure, IPC disconnection
 * @debugging_info Session ID, PTY PID, connection state
 * 
 * Defensive Programming Patterns:
 * - Proper cleanup on destroy
 * - IPC error handling
 * - Session lifecycle management
 * 
 * Integration Boundaries:
 * - xterm.js for rendering
 * - IPC for PTY communication
 * - Component-scoped service
 */
@Component({
  selector: 'app-xterm-terminal',
  template: `
    <div class="xterm-container" #terminalContainer>
      <div class="terminal-header">
        <span class="terminal-title">{{ title || 'Terminal' }}</span>
        <span class="terminal-session" *ngIf="currentSessionId">
          Session: {{ currentSessionId }}
        </span>
        <div class="terminal-actions">
          <button (click)="clear()" title="Clear Terminal">
            <mat-icon>clear_all</mat-icon>
          </button>
          <button (click)="restart()" title="Restart Session">
            <mat-icon>refresh</mat-icon>
          </button>
          <button (click)="kill()" title="Kill Session">
            <mat-icon>close</mat-icon>
          </button>
        </div>
      </div>
      <div class="terminal-body" #terminalElement></div>
      <div class="terminal-status" *ngIf="!isSessionActive">
        <span class="status-message">{{ statusMessage }}</span>
      </div>
    </div>
  `,
  styles: [`
    .xterm-container {
      height: 100%;
      display: flex;
      flex-direction: column;
      background: #1e1e1e;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .terminal-header {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      background: #2d2d2d;
      border-bottom: 1px solid #3e3e3e;
      font-size: 14px;
      color: #cccccc;
    }
    
    .terminal-title {
      flex: 1;
      font-weight: 500;
    }
    
    .terminal-session {
      margin-right: 12px;
      font-size: 12px;
      color: #999;
    }
    
    .terminal-actions {
      display: flex;
      gap: 4px;
    }
    
    .terminal-actions button {
      background: transparent;
      border: none;
      color: #999;
      cursor: pointer;
      padding: 4px;
      display: flex;
      align-items: center;
      border-radius: 4px;
      transition: all 0.2s;
    }
    
    .terminal-actions button:hover {
      background: #3e3e3e;
      color: #fff;
    }
    
    .terminal-body {
      flex: 1;
      overflow: hidden;
    }
    
    .terminal-status {
      padding: 12px;
      background: #2d2d2d;
      border-top: 1px solid #3e3e3e;
      text-align: center;
      color: #999;
      font-size: 14px;
    }
    
    ::ng-deep .xterm {
      padding: 8px;
      height: 100%;
    }
    
    ::ng-deep .xterm-viewport {
      background-color: #1e1e1e !important;
    }
    
    ::ng-deep .xterm-screen {
      height: 100% !important;
    }
  `],
  providers: [TerminalService]  // Component-scoped service (C1 fix)
})
export class XtermTerminalComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('terminalElement', { static: false }) terminalElement!: ElementRef;
  @Input() sessionId?: string;
  @Input() shell?: string;
  @Input() cwd?: string;
  @Input() title?: string;
  @Input() fontSize: number = 14;
  @Input() theme: any = {
    background: '#1e1e1e',
    foreground: '#cccccc',
    cursor: '#ffffff',
    cursorAccent: '#000000',
    selection: 'rgba(255, 255, 255, 0.3)',
    black: '#000000',
    red: '#cd3131',
    green: '#0dbc79',
    yellow: '#e5e510',
    blue: '#2472c8',
    magenta: '#bc3fbc',
    cyan: '#11a8cd',
    white: '#e5e5e5',
    brightBlack: '#666666',
    brightRed: '#f14c4c',
    brightGreen: '#23d18b',
    brightYellow: '#f5f543',
    brightBlue: '#3b8eea',
    brightMagenta: '#d670d6',
    brightCyan: '#29b8db',
    brightWhite: '#e5e5e5'
  };
  
  private terminal?: Terminal;
  private fitAddon?: FitAddon;
  private webLinksAddon?: WebLinksAddon;
  private outputSubscription?: Subscription;
  private exitSubscription?: Subscription;
  private _currentSessionId?: string;
  private resizeObserver?: ResizeObserver;
  
  isSessionActive: boolean = false;
  statusMessage: string = 'Initializing...';
  
  /**
   * Public accessor for current session ID - used in template binding
   * @returns Current session ID or undefined if no active session
   */
  public get currentSessionId(): string | undefined {
    return this._currentSessionId;
  }
  
  /**
   * Updates current session with validation
   * @param sessionId - New session identifier
   * @business_rule Session ID must be non-empty string
   */
  private setSession(sessionId: string | undefined): void {
    if (sessionId && sessionId.trim().length === 0) {
      console.warn('[XTerm] Invalid session ID: empty string');
      return;
    }
    this._currentSessionId = sessionId;
  }
  
  constructor(private terminalService: TerminalService) {}
  
  /**
   * @method ngOnInit
   * @description Initialize terminal component and subscriptions
   * @business_rule Set up IPC listeners before creating terminal
   */
  ngOnInit(): void {
    console.log('[XTerm] Component initializing...');
    
    // Subscribe to terminal output from PTY
    this.outputSubscription = this.terminalService.output$.subscribe(output => {
      if (output.sessionId === this._currentSessionId) {
        this.handleTerminalOutput(output);
      }
    });
    
    // Subscribe to session exit events
    this.exitSubscription = this.terminalService.exit$.subscribe(exitData => {
      if (exitData.sessionId === this._currentSessionId) {
        this.handleSessionExit(exitData);
      }
    });
  }
  
  /**
   * @method ngAfterViewInit
   * @description Create xterm.js terminal after view initialization
   * @business_rule Terminal must be created after DOM is ready
   */
  ngAfterViewInit(): void {
    this.createTerminal();
    this.createSession();
  }
  
  /**
   * @method createTerminal
   * @description Create and configure xterm.js terminal instance
   * @business_rule Configure terminal with theme and addons
   */
  private createTerminal(): void {
    if (!this.terminalElement) {
      console.error('[XTerm] Terminal element not found');
      return;
    }
    
    // Create xterm.js terminal
    this.terminal = new Terminal({
      fontSize: this.fontSize,
      fontFamily: 'Consolas, "Courier New", monospace',
      theme: this.theme,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 10000,
      tabStopWidth: 4,
      windowsMode: process.platform === 'win32'
    });
    
    // Add fit addon for responsive sizing
    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    
    // Add web links addon for clickable URLs
    this.webLinksAddon = new WebLinksAddon();
    this.terminal.loadAddon(this.webLinksAddon);
    
    // Open terminal in DOM element
    this.terminal.open(this.terminalElement.nativeElement);
    
    // Initial fit
    this.fitAddon.fit();
    
    // Set up resize observer
    this.setupResizeObserver();
    
    // Handle terminal input
    this.terminal.onData((data: string) => {
      if (this._currentSessionId && this.isSessionActive) {
        // Send input to PTY via IPC
        this.terminalService.writeToSession(this._currentSessionId, data);
      }
    });
    
    // Handle terminal resize
    this.terminal.onResize((dimensions: { cols: number; rows: number }) => {
      if (this._currentSessionId && this.isSessionActive) {
        // Send resize to PTY
        this.terminalService.resizeSession(
          this._currentSessionId,
          dimensions.cols,
          dimensions.rows
        );
      }
    });
    
    console.log('[XTerm] Terminal created successfully');
  }
  
  /**
   * @method createSession
   * @description Create PTY session via IPC
   * @business_rule Request real PTY from main process
   * 
   * Sarah's Framework Check:
   * - What breaks first: PTY spawn failure
   * - How we know: Error from main process
   * - Plan B: Show error message, allow retry
   */
  private async createSession(): Promise<void> {
    this.statusMessage = 'Creating session...';
    
    try {
      // Create PTY session
      if (this.sessionId) {
        this.setSession(this.sessionId);
        await this.terminalService.createSessionWithId(this.sessionId, this.shell, this.cwd);
      } else {
        this.setSession(await this.terminalService.createSession(this.shell, this.cwd));
      }
      
      console.log('[XTerm] Session created:', this._currentSessionId);
      
      // Get any existing output
      const existingOutput = await this.terminalService.getSessionOutput(this._currentSessionId);
      existingOutput.forEach(output => {
        if (this.terminal && output.data) {
          this.terminal.write(output.data);
        }
      });
      
      this.isSessionActive = true;
      this.statusMessage = '';
      
      // Focus terminal
      this.terminal?.focus();
      
    } catch (error) {
      console.error('[XTerm] Failed to create session:', error);
      this.statusMessage = `Failed to create session: ${error}`;
      this.isSessionActive = false;
      
      // Show error in terminal
      if (this.terminal) {
        this.terminal.write(`\r\n\x1b[31mError: Failed to create terminal session\x1b[0m\r\n`);
        this.terminal.write(`${error}\r\n`);
      }
    }
  }
  
  /**
   * @method handleTerminalOutput
   * @description Handle output from PTY
   * @business_rule Write PTY output directly to xterm
   * @param {TerminalOutput} output - Output from PTY
   */
  private handleTerminalOutput(output: TerminalOutput): void {
    if (this.terminal && output.data) {
      // Write output to xterm (includes ANSI codes)
      this.terminal.write(output.data);
    }
  }
  
  /**
   * @method handleSessionExit
   * @description Handle PTY session exit
   * @business_rule Show exit message and disable input
   * @param {any} exitData - Exit data from PTY
   */
  private handleSessionExit(exitData: any): void {
    this.isSessionActive = false;
    this.statusMessage = `Session exited (code: ${exitData.exitCode})`;
    
    if (this.terminal) {
      this.terminal.write(`\r\n\x1b[33mSession terminated with exit code ${exitData.exitCode}\x1b[0m\r\n`);
      this.terminal.options.disableStdin = true;
    }
  }
  
  /**
   * @method setupResizeObserver
   * @description Set up resize observer for responsive terminal
   * @business_rule Terminal should resize with container
   */
  private setupResizeObserver(): void {
    if (!this.terminalElement) return;
    
    this.resizeObserver = new ResizeObserver(() => {
      if (this.fitAddon) {
        this.fitAddon.fit();
      }
    });
    
    this.resizeObserver.observe(this.terminalElement.nativeElement);
  }
  
  /**
   * @method clear
   * @description Clear terminal screen
   * @business_rule Send clear command to PTY
   */
  public clear(): void {
    if (this.terminal) {
      this.terminal.clear();
    }
    
    // Send clear command to PTY
    if (this._currentSessionId && this.isSessionActive) {
      const clearCommand = this.shell?.includes('powershell') ? 'cls' : 'clear';
      this.terminalService.writeToSession(this._currentSessionId, clearCommand + '\r');
    }
  }
  
  /**
   * @method restart
   * @description Restart terminal session
   * @business_rule Kill current session and create new one
   */
  public async restart(): Promise<void> {
    if (this._currentSessionId) {
      this.kill();
    }
    
    // Clear terminal
    if (this.terminal) {
      this.terminal.clear();
      this.terminal.reset();
      this.terminal.options.disableStdin = false;
    }
    
    // Create new session
    await this.createSession();
  }
  
  /**
   * @method kill
   * @description Kill terminal session
   * @business_rule Terminate PTY process
   */
  public kill(): void {
    if (this._currentSessionId) {
      this.terminalService.killSession(this._currentSessionId);
      this.setSession(undefined);
      this.isSessionActive = false;
      this.statusMessage = 'Session killed';
    }
  }
  
  /**
   * @method ngOnDestroy
   * @description Clean up terminal and subscriptions
   * @business_rule Ensure proper cleanup to prevent memory leaks
   */
  ngOnDestroy(): void {
    console.log('[XTerm] Component destroying...');
    
    // Clean up subscriptions
    this.outputSubscription?.unsubscribe();
    this.exitSubscription?.unsubscribe();
    
    // Clean up resize observer
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    
    // Kill session if we created it
    if (this._currentSessionId && !this.sessionId) {
      this.terminalService.killSession(this._currentSessionId);
    }
    
    // Dispose terminal
    if (this.terminal) {
      this.terminal.dispose();
    }
    
    console.log('[XTerm] Component destroyed');
  }
}

// Export for module
export { Terminal } from 'xterm';