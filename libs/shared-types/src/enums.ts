/**
 * @fileoverview Shared enums used across frontend and backend
 * @author Alex Novak & Dr. Sarah Chen - Enterprise Architects
 * @architecture Shared Types Library
 * @description Central enum definitions for type safety across the monorepo
 */

// ============== GOVERNANCE ENUMS ==============

export enum RuleSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  MEDIUM = 'MEDIUM',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export enum RuleStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  DISABLED = 'DISABLED',
  DEPRECATED = 'DEPRECATED'
}

// ============== TEMPLATE ENUMS ==============

export enum TemplateType {
  CODE = 'CODE',
  CONFIG = 'CONFIG',
  DOCUMENT = 'DOCUMENT',
  DOCUMENTATION = 'DOCUMENTATION',
  WORKFLOW = 'WORKFLOW',
  ANALYSIS = 'ANALYSIS',
  PROMPT = 'PROMPT',
  PERSONA = 'PERSONA'
}

// ============== SESSION ENUMS ==============

export enum SessionStatus {
  ACTIVE = 'active',
  WARNING = 'warning',
  EXPIRED = 'expired',
  ENDED = 'ended'
}

// ============== DECISION ENUMS ==============

export enum DecisionType {
  CODE_GENERATION = 'CODE_GENERATION',
  ARCHITECTURE = 'ARCHITECTURE',
  SECURITY = 'SECURITY',
  PERFORMANCE = 'PERFORMANCE',
  DOCUMENTATION = 'DOCUMENTATION',
  TESTING = 'TESTING',
  DEPLOYMENT = 'DEPLOYMENT'
}

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// ============== CACHE ENUMS ==============

export enum CacheLevel {
  L1_MEMORY = 'L1_MEMORY',
  L2_REDIS = 'L2_REDIS',
  L3_DATABASE = 'L3_DATABASE'
}

export enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

// ============== CONNECTION ENUMS ==============

export enum ConnectionStatus {
  CONNECTED = 'connected',
  CONNECTING = 'connecting',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  RECONNECTING = 'reconnecting'
}

export enum WebSocketState {
  CONNECTING = 0,
  OPEN = 1,
  CLOSING = 2,
  CLOSED = 3
}

// ============== AUDIT ENUMS ==============

export enum AuditEventType {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  ACCESS = 'ACCESS',
  VALIDATE = 'VALIDATE',
  ENFORCE = 'ENFORCE',
  APPROVE = 'APPROVE',
  REJECT = 'REJECT'
}

export enum EntityType {
  RULE = 'RULE',
  PRACTICE = 'PRACTICE',
  TEMPLATE = 'TEMPLATE',
  SESSION = 'SESSION',
  DECISION = 'DECISION',
  USER = 'USER',
  SYSTEM = 'SYSTEM'
}