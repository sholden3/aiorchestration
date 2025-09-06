/**
 * @fileoverview Shared logging utilities
 * @author Alex Novak - Frontend Architect
 * @architecture Shared Utils Library
 * @description Centralized logging with correlation tracking
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  CRITICAL = 4
}

export interface LogContext {
  correlationId?: string;
  sessionId?: string;
  userId?: string;
  component?: string;
  metadata?: Record<string, any>;
}

export class Logger {
  private static instance: Logger;
  private logLevel: LogLevel = LogLevel.INFO;
  private context: LogContext = {};

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  setLevel(level: LogLevel): void {
    this.logLevel = level;
  }

  setContext(context: LogContext): void {
    this.context = { ...this.context, ...context };
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.logLevel;
  }

  private formatMessage(level: string, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const mergedContext = { ...this.context, ...context };
    const contextStr = mergedContext.correlationId 
      ? `[${mergedContext.correlationId}]` 
      : '';
    
    return `${timestamp} [${level}]${contextStr} ${message}`;
  }

  debug(message: string, context?: LogContext): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.formatMessage('DEBUG', message, context));
    }
  }

  info(message: string, context?: LogContext): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage('INFO', message, context));
    }
  }

  warn(message: string, context?: LogContext): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.formatMessage('WARN', message, context));
    }
  }

  error(message: string, error?: Error, context?: LogContext): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      const errorMessage = error ? `${message}: ${error.message}` : message;
      console.error(this.formatMessage('ERROR', errorMessage, context));
      if (error?.stack) {
        console.error(error.stack);
      }
    }
  }

  critical(message: string, error?: Error, context?: LogContext): void {
    if (this.shouldLog(LogLevel.CRITICAL)) {
      const errorMessage = error ? `${message}: ${error.message}` : message;
      console.error(this.formatMessage('CRITICAL', errorMessage, context));
      if (error?.stack) {
        console.error(error.stack);
      }
    }
  }
}

export const logger = Logger.getInstance();