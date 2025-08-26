import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Input, AfterViewInit } from '@angular/core';
import { TerminalService, TerminalOutput } from '../../services/terminal.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-terminal',
  templateUrl: './terminal.component.html',
  styleUrls: ['./terminal.component.scss']
})
export class TerminalComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('terminalContainer', { static: false }) terminalContainer!: ElementRef;
  @Input() sessionId?: string;
  @Input() shell?: string;
  @Input() cwd?: string;
  
  private outputSubscription?: Subscription;
  private exitSubscription?: Subscription;
  private currentSessionId?: string;
  private commandHistory: string[] = [];
  private historyIndex: number = -1;
  
  terminalOutput: string = '';
  terminalInput: string = '';
  isSessionActive: boolean = false;

  constructor(private terminalService: TerminalService) {}

  ngOnInit(): void {
    console.log('Terminal component initializing...');
    
    // Subscribe to terminal events
    this.outputSubscription = this.terminalService.output$.subscribe(output => {
      console.log('Terminal output received:', output);
      if (output.sessionId === this.currentSessionId) {
        this.handleTerminalOutput(output);
      }
    });

    this.exitSubscription = this.terminalService.exit$.subscribe(exitData => {
      console.log('Terminal exit received:', exitData);
      if (exitData.sessionId === this.currentSessionId) {
        this.handleSessionExit(exitData);
      }
    });
  }

  ngAfterViewInit(): void {
    this.createSession();
  }

  ngOnDestroy(): void {
    this.cleanup();
  }

  private async createSession(): Promise<void> {
    console.log('Creating terminal session with:', { 
      sessionId: this.sessionId, 
      shell: this.shell, 
      cwd: this.cwd 
    });
    
    try {
      if (this.sessionId) {
        // Use the provided session ID
        this.currentSessionId = this.sessionId;
        // Still need to create the actual session with this ID
        await this.terminalService.createSessionWithId(this.sessionId, this.shell, this.cwd);
      } else {
        // Generate a new session ID
        this.currentSessionId = await this.terminalService.createSession(this.shell, this.cwd);
      }

      console.log('Session created with ID:', this.currentSessionId);

      // Get any existing output
      const existingOutput = await this.terminalService.getSessionOutput(this.currentSessionId);
      console.log('Existing output:', existingOutput);
      
      existingOutput.forEach(output => {
        this.terminalOutput += output.data;
      });
      
      this.isSessionActive = true;
      this.scrollToBottom();
      
      // Show initial prompt if no output
      if (!this.terminalOutput) {
        const shellName = this.shell || 'Terminal';
        this.terminalOutput = `${shellName} session started\r\n`;
      }
    } catch (error) {
      console.error('Failed to create terminal session:', error);
      this.terminalOutput = `Failed to create terminal session: ${error}\r\n`;
      this.isSessionActive = false;
    }
  }

  private handleTerminalOutput(output: TerminalOutput): void {
    // Process the output data (which may contain ANSI codes)
    const processedData = this.processAnsiCodes(output.data);
    this.terminalOutput += processedData;
    this.scrollToBottom();
  }

  private handleSessionExit(exitData: any): void {
    this.terminalOutput += `\r\nSession terminated with exit code: ${exitData.exitCode}\r\n`;
    this.isSessionActive = false;
    this.scrollToBottom();
  }

  private processAnsiCodes(data: string): string {
    // Basic ANSI code processing - remove for now, can enhance later
    // This is a simplified version that strips ANSI codes
    return data.replace(/\x1b\[[0-9;]*m/g, '');
  }

  onKeyPress(event: KeyboardEvent): void {
    if (!this.isSessionActive) return;

    switch(event.key) {
      case 'Enter':
        this.sendCommand();
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.navigateHistory(-1);
        break;
      case 'ArrowDown':
        event.preventDefault();
        this.navigateHistory(1);
        break;
      case 'Tab':
        event.preventDefault();
        // Could implement tab completion here
        break;
    }
  }

  sendCommand(): void {
    if (this.currentSessionId && this.terminalInput) {
      // Add to command history
      this.commandHistory.push(this.terminalInput);
      this.historyIndex = this.commandHistory.length;
      
      // Send command with newline
      this.terminalService.writeToSession(this.currentSessionId, this.terminalInput + '\r\n');
      
      // Clear input
      this.terminalInput = '';
      this.scrollToBottom();
    }
  }

  private navigateHistory(direction: number): void {
    const newIndex = this.historyIndex + direction;
    
    if (newIndex >= 0 && newIndex < this.commandHistory.length) {
      this.historyIndex = newIndex;
      this.terminalInput = this.commandHistory[this.historyIndex];
    } else if (newIndex >= this.commandHistory.length) {
      this.historyIndex = this.commandHistory.length;
      this.terminalInput = '';
    }
  }

  private scrollToBottom(): void {
    if (this.terminalContainer) {
      setTimeout(() => {
        const element = this.terminalContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }, 0);
    }
  }

  private cleanup(): void {
    this.outputSubscription?.unsubscribe();
    this.exitSubscription?.unsubscribe();
    
    if (this.currentSessionId && !this.sessionId) {
      // Only kill session if we created it (not passed in)
      this.terminalService.killSession(this.currentSessionId);
    }
  }

  public clear(): void {
    this.terminalOutput = '';
    
    // Send clear command to terminal
    if (this.currentSessionId && this.isSessionActive) {
      const clearCommand = this.shell?.includes('powershell') ? 'cls' : 'clear';
      this.terminalService.writeToSession(this.currentSessionId, clearCommand + '\r\n');
    }
  }

  public focus(): void {
    // Focus on the input element
    const inputElement = this.terminalContainer?.nativeElement.querySelector('.terminal-input');
    if (inputElement) {
      inputElement.focus();
    }
  }

  public fit(): void {
    // Calculate terminal dimensions and resize
    if (this.currentSessionId && this.terminalContainer) {
      const element = this.terminalContainer.nativeElement;
      const charWidth = 8; // Approximate character width in pixels
      const charHeight = 17; // Approximate character height in pixels
      
      const cols = Math.floor(element.clientWidth / charWidth);
      const rows = Math.floor(element.clientHeight / charHeight);
      
      this.terminalService.resizeSession(this.currentSessionId, cols, rows);
    }
  }

  public getShellIcon(): string {
    if (!this.shell) return 'terminal';
    
    if (this.shell.includes('powershell')) return 'terminal';
    if (this.shell.includes('cmd')) return 'computer';
    if (this.shell.includes('bash')) return 'code';
    
    return 'terminal';
  }
}