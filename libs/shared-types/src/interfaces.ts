/**
 * @fileoverview Shared interfaces for cross-cutting concerns
 * @author Alex Novak & Dr. Sarah Chen - Enterprise Architects
 * @architecture Shared Types Library
 * @description Base interfaces used throughout the monorepo
 */

import { 
  RuleSeverity, 
  RuleStatus, 
  TemplateType, 
  SessionStatus,
  AuditEventType,
  EntityType 
} from './enums';

// ============== BASE INTERFACES ==============

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at?: string;
}

export interface Timestamped {
  created_at: string;
  updated_at?: string;
}

export interface Authored {
  author?: string;
  version?: number;
}

export interface Taggable {
  tags?: string[];
  metadata?: Record<string, any>;
}

// ============== PAGINATION ==============

export interface PaginationParams {
  skip?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more?: boolean;
}

// ============== VALIDATION ==============

export interface ValidationResult {
  valid: boolean;
  score?: number;
  errors?: ValidationError[];
  warnings?: ValidationWarning[];
  metadata?: Record<string, any>;
}

export interface ValidationError {
  field?: string;
  message: string;
  code?: string;
  severity?: RuleSeverity;
}

export interface ValidationWarning {
  field?: string;
  message: string;
  code?: string;
  suggestion?: string;
}

// ============== API RESPONSES ==============

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: ResponseMetadata;
}

export interface ApiError {
  code?: string;
  message: string;
  detail?: string;
  field?: string;
  stack?: string;
}

export interface ResponseMetadata {
  request_id?: string;
  timestamp?: string;
  duration_ms?: number;
  version?: string;
}

// ============== AUDIT ==============

export interface AuditEntry {
  id: string;
  event_type: AuditEventType;
  entity_type: EntityType;
  entity_id?: string;
  action: string;
  actor: string;
  session_id?: string;
  before_state?: Record<string, any>;
  after_state?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

// ============== GOVERNANCE ==============

export interface GovernanceContext {
  session_id?: string;
  correlation_id?: string;
  agent_id?: string;
  user_id?: string;
  rules?: string[];
  compliance_level?: number;
  metadata?: Record<string, any>;
}

export interface ComplianceResult {
  compliant: boolean;
  score: number;
  violations?: RuleViolation[];
  warnings?: ComplianceWarning[];
  recommendations?: string[];
}

export interface RuleViolation {
  rule_id: string;
  rule_name: string;
  severity: RuleSeverity;
  message: string;
  context?: Record<string, any>;
  fix_suggestion?: string;
}

export interface ComplianceWarning {
  message: string;
  severity: RuleSeverity;
  context?: Record<string, any>;
}

// ============== METRICS ==============

export interface MetricPoint {
  name: string;
  value: number;
  timestamp: string;
  tags?: Record<string, string>;
}

export interface PerformanceMetrics {
  response_time_ms?: number;
  cpu_usage?: number;
  memory_usage_mb?: number;
  request_count?: number;
  error_count?: number;
  success_rate?: number;
}

// ============== CONFIGURATION ==============

export interface ConfigValue<T = any> {
  key: string;
  value: T;
  description?: string;
  type?: string;
  default?: T;
  required?: boolean;
  validation?: string;
}

export interface FeatureFlag {
  key: string;
  enabled: boolean;
  description?: string;
  rollout_percentage?: number;
  conditions?: Record<string, any>;
}

// ============== ERROR HANDLING ==============

export interface ErrorContext {
  error: Error;
  context?: Record<string, any>;
  timestamp?: string;
  stack?: string;
  recovery_attempted?: boolean;
  recovery_successful?: boolean;
}

export interface CircuitBreakerState {
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failure_count: number;
  last_failure_time?: string;
  next_attempt_time?: string;
  success_count?: number;
}