/**
 * @fileoverview TypeScript interfaces matching backend Pydantic schemas
 * @author Alex Novak - Frontend/Integration Architect
 * @description Strongly typed models for backend API integration
 */

// ============== ENUMS ==============

// Import shared enums from monorepo shared types library
import { 
  RuleSeverity, 
  RuleStatus, 
  TemplateType, 
  SessionStatus,
  DecisionType,
  RiskLevel,
  AuditEventType,
  EntityType
} from '../../../../libs/shared-types/src';

// Re-export all enums for backward compatibility
export { 
  RuleSeverity, 
  RuleStatus, 
  TemplateType, 
  SessionStatus,
  DecisionType,
  RiskLevel,
  AuditEventType,
  EntityType
};

// ============== RULES ==============

export interface RuleBase {
  name: string;
  description?: string;
  category?: string;
  severity?: RuleSeverity;
  status?: RuleStatus;
  condition: string;
  action: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface RuleCreate extends RuleBase {}

export interface RuleUpdate {
  name?: string;
  description?: string;
  category?: string;
  severity?: RuleSeverity;
  status?: RuleStatus;
  condition?: string;
  action?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface RuleResponse extends RuleBase {
  id: string;
  author?: string;
  version?: number;
  enforcement_count?: number;
  violation_count?: number;
  effectiveness_score?: number;
  created_at: string;
  updated_at: string;
}

export interface RuleListResponse {
  rules: RuleResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface RuleStats {
  total_rules: number;
  active_rules: number;
  average_effectiveness: number;
  severity_distribution: Record<string, number>;
  last_updated: string;
}

export interface RuleEnforcementResult {
  rule_id: string;
  rule_name: string;
  passed: boolean;
  severity: RuleSeverity;
  message: string;
  action?: string;
  context: Record<string, any>;
  violations_found?: number;
}

// Additional Rule types
export interface Rule extends RuleResponse {
  title: string;
  conditions?: any[];
  actions?: any[];
  exceptions?: any[];
  violations_count?: number;
}

// ============== PRACTICES ==============

export interface PracticeBase {
  name: string;
  description?: string;
  category?: string;
  implementation_guide?: string;
  benefits?: string[];
  challenges?: string[];
  examples?: string[];
  metrics?: Record<string, any>;
  tags?: string[];
}

export interface PracticeCreate extends PracticeBase {}

export interface PracticeUpdate {
  name?: string;
  description?: string;
  category?: string;
  implementation_guide?: string;
  benefits?: string[];
  challenges?: string[];
  examples?: string[];
  metrics?: Record<string, any>;
  tags?: string[];
}

export interface PracticeResponse extends PracticeBase {
  id: string;
  author?: string;
  effectiveness_score?: number;
  adoption_rate?: number;
  votes_up?: number;
  votes_down?: number;
  created_at: string;
  updated_at: string;
}

export interface PracticeListResponse {
  practices: PracticeResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface PracticeVote {
  vote_type: 'up' | 'down';
  comment?: string;
}

export interface PracticeApplication {
  applied_to?: string;
  project_id?: string;
  effectiveness_rating?: number;
  notes?: string;
}

// Additional Practice types
export interface BestPractice extends PracticeResponse {
  title: string;
  risks?: string[];
  references?: string[];
  vote_score?: number;
  adoption_count?: number;
  adoption_rate?: number;
}

// ============== TEMPLATES ==============

export interface TemplateBase {
  name: string;
  type: TemplateType;
  category?: string;
  template_content?: string;
  content?: string;
  description?: string;
  example_usage?: Record<string, any>;
  variables?: string[] | Record<string, any>;
  validation_rules?: Record<string, any>;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface TemplateCreate extends TemplateBase {}

export interface TemplateUpdate {
  name?: string;
  type?: TemplateType;
  category?: string;
  template_content?: string;
  description?: string;
  example_usage?: Record<string, any>;
  variables?: Record<string, any>;
  validation_rules?: Record<string, any>;
  metadata?: Record<string, any>;
  tags?: string[];
}

export interface TemplateResponse {
  id: string;
  name: string;
  type: TemplateType;
  category?: string;
  template_content: string;
  description?: string;
  example_usage?: Record<string, any>;
  variables?: Record<string, any>;
  validation_rules?: Record<string, any>;
  tags?: string[];
  author?: string;
  version: number;
  parent_id?: string;
  usage_count: number;
  success_rate?: number;
  created_at: string;
  updated_at: string;
}

export interface TemplateListResponse {
  templates: TemplateResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface TemplateRender {
  variables: Record<string, any>;
}

export interface TemplateRenderResponse {
  rendered_content: string;
  validation_errors?: string[];
  metadata?: Record<string, any>;
}

// Additional Template types
export interface Template extends TemplateResponse {
  content?: string;
  variables: string[];
}

// ============== SESSIONS ==============

export interface SessionBase {
  session_id: string;
  architects: string[];
  status?: SessionStatus;
  environment?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface SessionCreate extends SessionBase {}

export interface SessionUpdate {
  architects?: string[];
  status?: SessionStatus;
  environment?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface SessionResponse {
  id: string;
  session_id: string;
  architects: string[];
  status: SessionStatus;
  environment?: Record<string, any>;
  metadata?: Record<string, any>;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
  metrics?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SessionListResponse {
  sessions: SessionResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface SessionEnd {
  end_time?: string;
  metrics?: Record<string, any>;
  summary?: string;
}

export interface SessionMetrics {
  total_sessions: number;
  active_sessions: number;
  average_duration_minutes: number;
  total_decisions: number;
  total_audit_logs: number;
  sessions_by_status: Record<string, number>;
}

// ============== AUDIT LOGS ==============

export interface AuditLog {
  id: string;
  event_type: string;
  entity_type: string;
  entity_id?: string;
  action: string;
  actor: string;
  session_id?: string;
  before_state?: Record<string, any>;
  after_state?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

// ============== AI DECISIONS ==============

export interface AIDecision {
  id: string;
  session_id?: string;
  decision_type: string;
  context: Record<string, any>;
  decision: Record<string, any>;
  reasoning?: string;
  confidence?: number;
  alternatives?: Record<string, any>[];
  applied_rules?: string[];
  outcome?: string;
  feedback?: string;
  created_at: string;
}

// ============== COMMON RESPONSE TYPES ==============

export interface ApiError {
  detail: string;
}

export interface SuccessResponse {
  message: string;
  id?: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ActiveSessionsResponse {
  active_sessions: SessionResponse[];
  count: number;
}

export interface TemplateTypesResponse {
  types: Array<{
    value: string;
    name: string;
    description: string;
  }>;
}