/**
 * PTY Types and Interfaces
 * Following SOLID principles and clean architecture
 */

import { IPty } from 'node-pty';

// ============================================================================
// Core PTY Types
// ============================================================================

export interface PTYSessionOptions {
  shell?: string;
  args?: string[];
  cwd: string;
  env?: Record<string, string>;
  cols?: number;
  rows?: number;
  command?: string;
  enhancedPrompt?: string;
  template?: string;
  bestPractices?: string[];
  metadata?: Record<string, any>;
}

export interface PTYSession {
  id: string;
  pty: IPty;
  isActive: boolean;
  createdAt: Date;
  workingDirectory: string;
  metadata: PTYMetadata;
  windowsSpecific?: WindowsPTYInfo;
  history: CommandHistory[];
  performance: SessionPerformance;
}

export interface PTYMetadata {
  originalCommand: string;
  bestPractices: string[];
  template?: string;
  shell: string;
  lastActivity?: Date;
  tags?: string[];
  projectContext?: ProjectContext;
}

export interface WindowsPTYInfo {
  processId: number;
  useConpty: boolean;
  codepage: string;
  shellType?: WindowsShellType;
  processTree?: number[];
}

export interface CommandHistory {
  command: string;
  timestamp: Date;
  exitCode?: number;
  duration?: number;
  output?: string;
}

export interface SessionPerformance {
  startTime: Date;
  totalCommands: number;
  totalOutputBytes: number;
  averageResponseTime: number;
  errors: number;
}

// ============================================================================
// PTY Events
// ============================================================================

export interface PTYSessionData {
  sessionId: string;
  data: string;
  timestamp: string;
  type: 'stdout' | 'stderr';
}

export interface PTYSessionExit {
  sessionId: string;
  exitCode: number;
  signal?: string;
  timestamp: string;
  reason?: string;
}

export interface PTYSessionError {
  sessionId: string;
  error: string;
  code?: string;
  recoverable: boolean;
  timestamp: string;
}

// ============================================================================
// Windows Shell Types
// ============================================================================

export enum WindowsShellType {
  POWERSHELL = 'powershell',
  POWERSHELL_CORE = 'pwsh',
  CMD = 'cmd',
  WSL = 'wsl',
  GIT_BASH = 'git-bash',
  CYGWIN = 'cygwin'
}

export interface WindowsShellInfo {
  type: WindowsShellType;
  name: string;
  path: string;
  version?: string;
  architecture?: string;
  isAvailable: boolean;
  isDefault: boolean;
  priority: number;
  features: ShellFeatures;
}

export interface ShellFeatures {
  supportsPowerShell: boolean;
  supportsAnsiColors: boolean;
  supportsUnicode: boolean;
  supportsConPTY: boolean;
  supportsResize: boolean;
}

// ============================================================================
// Project Context
// ============================================================================

export interface ProjectContext {
  type?: 'node' | 'python' | 'java' | 'dotnet' | 'go' | 'rust' | 'other';
  framework?: string;
  language?: string;
  dependencies?: string[];
  configuration?: Record<string, any>;
  gitInfo?: GitContext;
}

export interface GitContext {
  branch: string;
  remote?: string;
  isDirty: boolean;
  lastCommit?: string;
}

// ============================================================================
// Service Interfaces
// ============================================================================

export interface IPTYService {
  // Session Management
  createSession(options: PTYSessionOptions): Promise<string>;
  terminateSession(sessionId: string): boolean;
  getSession(sessionId: string): PTYSession | undefined;
  getAllSessions(): PTYSession[];
  getActiveSessions(): string[];
  
  // Session Operations
  writeToSession(sessionId: string, data: string): boolean;
  resizeSession(sessionId: string, cols: number, rows: number): boolean;
  clearSession(sessionId: string): boolean;
  
  // History & Context
  getSessionHistory(sessionId: string): CommandHistory[];
  setProjectContext(sessionId: string, context: ProjectContext): void;
  
  // Lifecycle
  cleanup(): void;
}

// ============================================================================
// Configuration
// ============================================================================

export interface PTYConfiguration {
  maxSessions: number;
  defaultShell?: string;
  shellPaths?: Record<WindowsShellType, string>;
  sessionTimeout?: number;
  encoding?: BufferEncoding;
  environmentVariables?: Record<string, string>;
  conptySettings?: ConPTYSettings;
}

export interface ConPTYSettings {
  enabled: boolean;
  inheritCursor: boolean;
  rows: number;
  cols: number;
}

// ============================================================================
// Error Types
// ============================================================================

export class PTYError extends Error {
  constructor(
    message: string,
    public code: string,
    public sessionId?: string,
    public recoverable: boolean = false
  ) {
    super(message);
    this.name = 'PTYError';
  }
}

export class PTYSessionNotFoundError extends PTYError {
  constructor(sessionId: string) {
    super(`PTY session ${sessionId} not found`, 'SESSION_NOT_FOUND', sessionId, true);
  }
}

export class PTYMaxSessionsError extends PTYError {
  constructor(max: number) {
    super(`Maximum number of PTY sessions (${max}) reached`, 'MAX_SESSIONS', undefined, true);
  }
}

// ============================================================================
// Type Guards
// ============================================================================

export function isPTYSession(obj: any): obj is PTYSession {
  return obj && 
    typeof obj.id === 'string' &&
    obj.pty &&
    typeof obj.isActive === 'boolean';
}

export function isPTYSessionData(obj: any): obj is PTYSessionData {
  return obj &&
    typeof obj.sessionId === 'string' &&
    typeof obj.data === 'string' &&
    typeof obj.timestamp === 'string';
}

export function isWindowsShellType(value: string): value is WindowsShellType {
  return Object.values(WindowsShellType).includes(value as WindowsShellType);
}