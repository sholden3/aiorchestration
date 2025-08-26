# PTY FOR REFERENCE

/**
 * PTY Migration Types and Interfaces
 * File: src/main/types/index.ts
 * 
 * Comprehensive TypeScript interfaces and types for PTY migration architecture
 * in Electron + Angular desktop application with Windows optimization.
 */

import { IPty } from 'node-pty';

// ============================================================================
// Core PTY Types
// ============================================================================

/**
 * Configuration interface for PTY instances with Windows-optimized settings
 */
export interface PTYConfig {
  shell?: string;
  args?: string[];
  cwd?: string;
  env?: NodeJS.ProcessEnv;
  cols?: number;
  rows?: number;
  encoding?: BufferEncoding;
  killTimeout?: number;
  useConpty?: boolean;
  experimentalUseConpty?: boolean;
}

/**
 * Enumeration of possible PTY states for lifecycle management
 */
export enum PTYStatus {
  INITIALIZING = 'initializing',
  ACTIVE = 'active',
  IDLE = 'idle',
  ERROR = 'error',
  TERMINATED = 'terminated'
}

/**
 * Represents a complete PTY instance with metadata and lifecycle tracking
 */
export interface PTYInstance {
  id: string;
  pty: IPty;
  config: PTYConfig;
  status: PTYStatus;
  createdAt: Date;
  lastActivity: Date;
}

/**
 * Data structures for PTY communication
 */
export interface PTYData {
  instanceId: string;
  data: string;
  timestamp: Date;
}

/**
 * PTY termination event information
 */
export interface PTYExitInfo {
  instanceId: string;
  exitCode: number;
  signal?: string;
  timestamp: Date;
}

// ============================================================================
// Windows-Specific Types
// ============================================================================

/**
 * Supported shell types with prioritization for Windows environments
 */
export enum WindowsShellType {
  POWERSHELL = 'powershell',
  POWERSHELL_CORE = 'pwsh',
  CMD = 'cmd',
  WSL = 'wsl',
  GIT_BASH = 'git-bash'
}

/**
 * Comprehensive shell detection and metadata for Windows environments
 */
export interface WindowsShellInfo {
  name: string;
  path: string;
  version?: string;
  architecture?: string;
  isAvailable: boolean;
  priority: number;
}

/**
 * Process management information for Windows
 */
export interface WindowsProcessInfo {
  pid: number;
  name: string;
  commandLine?: string;
  workingDirectory?: string;
  parentPid?: number;
  creationTime: Date;
}

/**
 * System environment detection for Windows
 */
export interface WindowsEnvironmentInfo {
  platform: string;
  release: string;
  architecture: string;
  availableShells: WindowsShellInfo[];
  defaultShell: WindowsShellInfo;
}

// ============================================================================
// Claude Code Service Types
// ============================================================================

/**
 * Configuration for Claude Code CLI integration with PTY support
 */
export interface ClaudeCodeConfig {
  executable?: string;
  workingDirectory?: string;
  timeout?: number;
  retryAttempts?: number;
  environmentVariables?: Record<string, string>;
  ptyConfig?: Partial<PTYConfig>;
}

/**
 * Command execution status tracking
 */
export enum CommandStatus {
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * Command execution tracking with comprehensive status management
 */
export interface ClaudeCodeCommand {
  id: string;
  command: string;
  args: string[];
  workingDirectory?: string;
  environment?: Record<string, string>;
  timestamp: Date;
  status: CommandStatus;
}

/**
 * Result tracking for command execution
 */
export interface ClaudeCodeResult {
  commandId: string;
  exitCode: number;
  stdout: string;
  stderr: string;
  duration: number;
  timestamp: Date;
}

/**
 * Session management for persistent CLI interactions
 */
export interface ClaudeCodeSession {
  id: string;
  ptyInstanceId: string;
  workingDirectory: string;
  startTime: Date;
  endTime?: Date;
  commands: ClaudeCodeCommand[];
  isActive: boolean;
}

// ============================================================================
// File System Types
// ============================================================================

/**
 * File system operations configuration
 */
export interface FileSystemConfig {
  watchedDirectories?: string[];
  allowedExtensions?: string[];
  maxFileSize?: number;
  encoding?: BufferEncoding;
}

/**
 * File permissions interface
 */
export interface FilePermissions {
  readable: boolean;
  writable: boolean;
  executable: boolean;
  mode: number;
}

/**
 * File metadata tracking
 */
export interface FileInfo {
  path: string;
  name: string;
  extension: string;
  size: number;
  isDirectory: boolean;
  lastModified: Date;
  permissions?: FilePermissions;
}

/**
 * Directory structure analysis
 */
export interface DirectoryInfo {
  path: string;
  name: string;
  files: FileInfo[];
  subdirectories: DirectoryInfo[];
  totalSize: number;
  fileCount: number;
}

/**
 * File system monitoring events
 */
export interface FileWatchEvent {
  type: 'add' | 'change' | 'unlink' | 'addDir' | 'unlinkDir';
  path: string;
  timestamp: Date;
  stats?: FileInfo;
}

// ============================================================================
// Event System Types
// ============================================================================

/**
 * Event callback function type
 */
export type EventCallback<T = any> = (event: ServiceEvent<T>) => void | Promise<void>;

/**
 * Event-driven architecture for service communication
 */
export interface ServiceEvent<T = any> {
  type: string;
  payload: T;
  timestamp: Date;
  source: string;
  target?: string;
}

/**
 * Event subscription management
 */
export interface EventSubscription {
  id: string;
  eventType: string;
  callback: EventCallback;
  once?: boolean;
  priority?: number;
}

// ============================================================================
// Service Container Types
// ============================================================================

/**
 * Service lifecycle management configuration
 */
export interface ServiceConfig {
  enabled: boolean;
  autoStart?: boolean;
  dependencies?: string[];
  configuration?: Record<string, any>;
}

/**
 * Service dependency tracking
 */
export interface ServiceDependency {
  name: string;
  required: boolean;
  available: boolean;
  version?: string;
}

/**
 * Service health monitoring
 */
export interface ServiceStatus {
  name: string;
  running: boolean;
  healthy: boolean;
  startTime?: Date;
  lastError?: ServiceError;
  dependencies: ServiceDependency[];
}

/**
 * Performance monitoring for services
 */
export interface ServiceMetrics {
  name: string;
  uptime: number;
  requestCount: number;
  errorCount: number;
  lastActivity: Date;
  memoryUsage?: number;
}

/**
 * Service error tracking
 */
export interface ServiceError {
  message: string;
  code?: string;
  timestamp: Date;
  stack?: string;
  context?: Record<string, any>;
}

// ============================================================================
// IPC Communication Types
// ============================================================================

/**
 * IPC error information
 */
export interface IPCError {
  code: string;
  message: string;
  details?: any;
}

/**
 * Structured communication between main and renderer processes
 */
export interface IPCMessage<T = any> {
  id: string;
  type: string;
  payload: T;
  timestamp: Date;
  source: 'main' | 'renderer';
  target?: string;
}

/**
 * IPC response structure
 */
export interface IPCResponse<T = any> {
  id: string;
  success: boolean;
  data?: T;
  error?: IPCError;
  timestamp: Date;
}

// ============================================================================
// Application Configuration Types
// ============================================================================

/**
 * Windows-specific settings
 */
export interface WindowsConfig {
  preferredShell?: WindowsShellType;
  shellPaths?: Record<WindowsShellType, string>;
  environmentSetup?: string[];
  processMonitoring?: boolean;
}

/**
 * Application logging configuration
 */
export interface LoggingConfig {
  level: 'debug' | 'info' | 'warn' | 'error';
  file?: string;
  maxSize?: number;
  rotateFiles?: number;
  console?: boolean;
}

/**
 * Master configuration interface bringing together all service configurations
 */
export interface ApplicationConfig {
  pty: PTYConfig;
  claudeCode: ClaudeCodeConfig;
  fileSystem: FileSystemConfig;
  services: Record<string, ServiceConfig>;
  windows: WindowsConfig;
  logging: LoggingConfig;
}

// ============================================================================
// Error Handling Strategy
// ============================================================================

/**
 * Application error severity levels
 */
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

/**
 * Base error with context and severity
 */
export interface ApplicationError {
  code: string;
  message: string;
  severity: ErrorSeverity;
  timestamp: Date;
  context?: Record<string, any>;
  stack?: string;
  cause?: Error;
}

/**
 * PTY-specific errors with instance details
 */
export interface PTYError extends ApplicationError {
  instanceId?: string;
  ptyConfig?: PTYConfig;
  operationType: 'create' | 'write' | 'resize' | 'destroy' | 'read';
}

/**
 * Service startup failures
 */
export interface ServiceInitializationError extends ApplicationError {
  serviceName: string;
  dependencies?: string[];
  configuration?: Record<string, any>;
}

/**
 * Consistent error handling across all services using the Result pattern
 */
export interface Result<T> {
  success: boolean;
  data?: T;
  error?: ApplicationError;
}

// ============================================================================
// Service Interface Definitions
// ============================================================================

/**
 * Core PTY management interface defining all PTY operations
 */
export interface IPTYService {
  createPTY(config?: Partial<PTYConfig>): Promise<Result<PTYInstance>>;
  destroyPTY(instanceId: string): Promise<Result<void>>;
  writeToPTY(instanceId: string, data: string): Promise<Result<void>>;
  resizePTY(instanceId: string, cols: number, rows: number): Promise<Result<void>>;
  getPTYStatus(instanceId: string): Promise<Result<PTYStatus>>;
  getAllPTYInstances(): Promise<Result<PTYInstance[]>>;
  onData(instanceId: string, callback: (data: PTYData) => void): Promise<Result<void>>;
  onExit(instanceId: string, callback: (exitInfo: PTYExitInfo) => void): Promise<Result<void>>;
}

/**
 * Claude Code CLI integration interface with session management
 */
export interface IClaudeCodeService {
  executeCommand(command: string, args: string[], options?: Partial<ClaudeCodeConfig>): Promise<Result<ClaudeCodeResult>>;
  startSession(workingDirectory?: string): Promise<Result<ClaudeCodeSession>>;
  endSession(sessionId: string): Promise<Result<void>>;
  getSessionStatus(sessionId: string): Promise<Result<ClaudeCodeSession>>;
  getAllSessions(): Promise<Result<ClaudeCodeSession[]>>;
  executeInSession(sessionId: string, command: string, args: string[]): Promise<Result<ClaudeCodeResult>>;
}

/**
 * File system operations with watching capabilities
 */
export interface IFileSystemService {
  readFile(path: string, encoding?: BufferEncoding): Promise<Result<string>>;
  writeFile(path: string, content: string, encoding?: BufferEncoding): Promise<Result<void>>;
  getFileInfo(path: string): Promise<Result<FileInfo>>;
  getDirectoryInfo(path: string): Promise<Result<DirectoryInfo>>;
  watchDirectory(path: string, callback: (event: FileWatchEvent) => void): Promise<Result<void>>;
  unwatchDirectory(path: string): Promise<Result<void>>;
  ensureDirectory(path: string): Promise<Result<void>>;
  deleteFile(path: string): Promise<Result<void>>;
}

/**
 * Windows shell detection and validation
 */
export interface IWindowsShellDetector {
  detectAvailableShells(): Promise<Result<WindowsShellInfo[]>>;
  getDefaultShell(): Promise<Result<WindowsShellInfo>>;
  getShellInfo(shellType: WindowsShellType): Promise<Result<WindowsShellInfo>>;
  validateShellPath(path: string): Promise<Result<boolean>>;
  getEnvironmentInfo(): Promise<Result<WindowsEnvironmentInfo>>;
}

/**
 * Process monitoring and management for Windows
 */
export interface IWindowsProcessManager {
  getProcessInfo(pid: number): Promise<Result<WindowsProcessInfo>>;
  getProcessChildren(pid: number): Promise<Result<WindowsProcessInfo[]>>;
  killProcess(pid: number, force?: boolean): Promise<Result<void>>;
  isProcessRunning(pid: number): Promise<Result<boolean>>;
  monitorProcess(pid: number, callback: (info: WindowsProcessInfo) => void): Promise<Result<void>>;
  stopMonitoring(pid: number): Promise<Result<void>>;
}

/**
 * Event-driven service communication
 */
export interface IEventBus {
  emit<T>(event: ServiceEvent<T>): Promise<void>;
  subscribe<T>(eventType: string, callback: EventCallback<T>, options?: Partial<EventSubscription>): Promise<string>;
  unsubscribe(subscriptionId: string): Promise<void>;
  once<T>(eventType: string, callback: EventCallback<T>): Promise<void>;
  removeAllListeners(eventType?: string): Promise<void>;
  getSubscriptions(eventType?: string): EventSubscription[];
}

/**
 * Service lifecycle and dependency management
 */
export interface IServiceContainer {
  registerService<T>(name: string, service: T, config?: ServiceConfig): Promise<Result<void>>;
  getService<T>(name: string): Promise<Result<T>>;
  startService(name: string): Promise<Result<void>>;
  stopService(name: string): Promise<Result<void>>;
  getServiceStatus(name: string): Promise<Result<ServiceStatus>>;
  getAllServices(): Promise<Result<ServiceStatus[]>>;
  getServiceMetrics(name: string): Promise<Result<ServiceMetrics>>;
  isServiceHealthy(name: string): Promise<Result<boolean>>;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Runtime type checking utilities for safe type assertions
 */
export const isResult = <T>(obj: any): obj is Result<T> => {
  return obj && typeof obj === 'object' && typeof obj.success === 'boolean';
};

export const isPTYInstance = (obj: any): obj is PTYInstance => {
  return obj && 
    typeof obj === 'object' && 
    typeof obj.id === 'string' &&
    obj.pty &&
    obj.config &&
    Object.values(PTYStatus).includes(obj.status) &&
    obj.createdAt instanceof Date &&
    obj.lastActivity instanceof Date;
};

export const isServiceEvent = <T>(obj: any): obj is ServiceEvent<T> => {
  return obj && 
    typeof obj === 'object' && 
    typeof obj.type === 'string' &&
    obj.timestamp instanceof Date &&
    typeof obj.source === 'string';
};

export const isApplicationError = (obj: any): obj is ApplicationError => {
  return obj && 
    typeof obj === 'object' && 
    typeof obj.code === 'string' &&
    typeof obj.message === 'string' &&
    Object.values(ErrorSeverity).includes(obj.severity) &&
    obj.timestamp instanceof Date;
};

export const isPTYError = (obj: any): obj is PTYError => {
  return isApplicationError(obj) && 
    typeof obj.operationType === 'string' &&
    ['create', 'write', 'resize', 'destroy', 'read'].includes(obj.operationType);
};

export const isWindowsShellInfo = (obj: any): obj is WindowsShellInfo => {
  return obj && 
    typeof obj === 'object' && 
    typeof obj.name === 'string' &&
    typeof obj.path === 'string' &&
    typeof obj.isAvailable === 'boolean' &&
    typeof obj.priority === 'number';
};

export const isClaudeCodeSession = (obj: any): obj is ClaudeCodeSession => {
  return obj && 
    typeof obj === 'object' && 
    typeof obj.id === 'string' &&
    typeof obj.ptyInstanceId === 'string' &&
    typeof obj.workingDirectory === 'string' &&
    obj.startTime instanceof Date &&
    Array.isArray(obj.commands) &&
    typeof obj.isActive === 'boolean';
};

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Utility type for creating partial configurations
 */
export type PartialConfig<T> = {
  [P in keyof T]?: T[P] extends object ? PartialConfig<T[P]> : T[P];
};

/**
 * Utility type for event handler maps
 */
export type EventHandlerMap = {
  [eventType: string]: EventCallback[];
};

/**
 * Utility type for service registry
 */
export type ServiceRegistry = {
  [serviceName: string]: {
    instance: any;
    config: ServiceConfig;
    status: ServiceStatus;
    metrics: ServiceMetrics;
  };
};

/**
 * Utility type for async operation results
 */
export type AsyncResult<T> = Promise<Result<T>>;

// ============================================================================
// Constants
// ============================================================================

/**
 * Default PTY configuration optimized for Windows
 */
export const DEFAULT_PTY_CONFIG: PTYConfig = {
  cols: 80,
  rows: 30,
  encoding: 'utf8',
  killTimeout: 5000,
  useConpty: true,
  experimentalUseConpty: true,
};

/**
 * Default Claude Code configuration
 */
export const DEFAULT_CLAUDE_CODE_CONFIG: ClaudeCodeConfig = {
  executable: 'claude-code',
  timeout: 30000,
  retryAttempts: 3,
  environmentVariables: {},
};

/**
 * Windows shell priorities (higher number = higher priority)
 */
export const WINDOWS_SHELL_PRIORITIES: Record<WindowsShellType, number> = {
  [WindowsShellType.POWERSHELL_CORE]: 100,
  [WindowsShellType.POWERSHELL]: 90,
  [WindowsShellType.CMD]: 50,
  [WindowsShellType.WSL]: 80,
  [WindowsShellType.GIT_BASH]: 70,
};

/**
 * Default logging configuration
 */
export const DEFAULT_LOGGING_CONFIG: LoggingConfig = {
  level: 'info',
  console: true,
  maxSize: 10 * 1024 * 1024, // 10MB
  rotateFiles: 5,
};


## Next Steps PTY

**When we are ready, we need to look at the following:

Option 1: Windows Utility Classes

WindowsShellDetector - Shell detection and validation
WindowsProcessManager - Process monitoring and management

Option 2: Core Services

ClaudeCodeService - CLI integration with session management
FileSystemService - File operations with watching capabilities
EventBus - Event-driven service communication

Option 3: Infrastructure Services

ServiceContainer - Dependency management and lifecycle
Updated Angular services for PTY integration
