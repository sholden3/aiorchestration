-- MCP Governance Server Database Schema (SQLite Version)
-- Version: 1.0.0
-- Author: Dr. Sarah Chen
-- Phase: MCP-001 PHOENIX_RISE_FOUNDATION
-- Purpose: Track MCP sessions, consultations, and metrics

-- ============================================================================
-- MCP Sessions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_sessions (
    session_id TEXT PRIMARY KEY,
    connection_id TEXT NOT NULL,
    client_identifier TEXT,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'active',
    port INTEGER NOT NULL,
    client_metadata TEXT, -- JSON stored as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mcp_sessions_status ON mcp_sessions(status);
CREATE INDEX IF NOT EXISTS idx_mcp_sessions_connection ON mcp_sessions(connection_id);
CREATE INDEX IF NOT EXISTS idx_mcp_sessions_time ON mcp_sessions(start_time, end_time);

-- ============================================================================
-- Persona Consultations Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS persona_consultations (
    consultation_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES mcp_sessions(session_id) ON DELETE CASCADE,
    persona_name TEXT NOT NULL,
    persona_version TEXT,
    operation TEXT NOT NULL,
    question TEXT NOT NULL,
    context TEXT NOT NULL, -- JSON stored as TEXT
    response TEXT NOT NULL,
    confidence_score REAL,
    response_time_ms INTEGER,
    cache_hit INTEGER DEFAULT 0, -- Boolean as INTEGER (0/1)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_consultations_session ON persona_consultations(session_id);
CREATE INDEX IF NOT EXISTS idx_consultations_persona ON persona_consultations(persona_name);
CREATE INDEX IF NOT EXISTS idx_consultations_operation ON persona_consultations(operation);
CREATE INDEX IF NOT EXISTS idx_consultations_timestamp ON persona_consultations(timestamp);

-- ============================================================================
-- Governance Decisions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS governance_decisions (
    decision_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    operation TEXT NOT NULL,
    context TEXT NOT NULL, -- JSON stored as TEXT
    approved INTEGER NOT NULL, -- Boolean as INTEGER
    confidence REAL,
    personas_consulted TEXT, -- JSON stored as TEXT
    recommendations TEXT, -- JSON stored as TEXT
    warnings TEXT, -- JSON stored as TEXT
    outcome TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_decisions_session ON governance_decisions(session_id);
CREATE INDEX IF NOT EXISTS idx_decisions_operation ON governance_decisions(operation);
CREATE INDEX IF NOT EXISTS idx_decisions_outcome ON governance_decisions(outcome);
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON governance_decisions(timestamp);

-- ============================================================================
-- MCP Metrics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_metrics (
    metric_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_requests INTEGER NOT NULL DEFAULT 0,
    cache_hits INTEGER NOT NULL DEFAULT 0,
    cache_misses INTEGER NOT NULL DEFAULT 0,
    avg_response_time REAL,
    errors INTEGER NOT NULL DEFAULT 0,
    active_sessions INTEGER,
    period_start TIMESTAMP,
    period_end TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_session ON mcp_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON mcp_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_period ON mcp_metrics(period_start, period_end);

-- ============================================================================
-- Audit Log Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_audit_log (
    audit_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    event_data TEXT, -- JSON stored as TEXT
    user_identifier TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_session ON mcp_audit_log(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON mcp_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON mcp_audit_log(timestamp);

-- ============================================================================
-- Configuration History Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_config_history (
    config_id TEXT PRIMARY KEY,
    config_type TEXT NOT NULL, -- 'personas', 'rules', 'thresholds'
    config_version TEXT NOT NULL,
    config_data TEXT NOT NULL, -- JSON stored as TEXT
    changed_by TEXT,
    change_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_config_type ON mcp_config_history(config_type);
CREATE INDEX IF NOT EXISTS idx_config_version ON mcp_config_history(config_version);
CREATE INDEX IF NOT EXISTS idx_config_timestamp ON mcp_config_history(timestamp);

-- ============================================================================
-- Views
-- ============================================================================

-- Active sessions view
CREATE VIEW IF NOT EXISTS active_mcp_sessions AS
SELECT 
    session_id,
    connection_id,
    client_identifier,
    start_time,
    CAST((julianday('now') - julianday(start_time)) * 24 * 60 * 60 AS INTEGER) as duration_seconds,
    port,
    client_metadata
FROM mcp_sessions
WHERE status = 'active';

-- Session summary view
CREATE VIEW IF NOT EXISTS mcp_session_summary AS
SELECT 
    s.session_id,
    s.connection_id,
    s.start_time,
    s.end_time,
    s.status,
    COUNT(DISTINCT pc.consultation_id) as total_consultations,
    COUNT(DISTINCT pc.persona_name) as unique_personas,
    AVG(pc.confidence_score) as avg_confidence,
    AVG(pc.response_time_ms) as avg_response_time
FROM mcp_sessions s
LEFT JOIN persona_consultations pc ON s.session_id = pc.session_id
GROUP BY s.session_id, s.connection_id, s.start_time, s.end_time, s.status;

-- ============================================================================
-- Triggers (SQLite version)
-- ============================================================================

-- Update timestamp trigger
CREATE TRIGGER IF NOT EXISTS update_mcp_sessions_updated_at
    AFTER UPDATE ON mcp_sessions
    FOR EACH ROW
BEGIN
    UPDATE mcp_sessions 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
END;

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert test session
-- INSERT INTO mcp_sessions (session_id, connection_id, client_identifier, port, client_metadata)
-- VALUES ('test-session-001', 'test-connection-001', 'claude-code-test', 8001, 
--         '{"version": "1.0", "environment": "development"}');