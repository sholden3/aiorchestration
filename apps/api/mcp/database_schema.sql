-- MCP Governance Server Database Schema
-- Version: 1.0.0
-- Author: Dr. Sarah Chen
-- Phase: MCP-001 PHOENIX_RISE_FOUNDATION
-- Purpose: Track MCP sessions, consultations, and metrics

-- ============================================================================
-- MCP Sessions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id VARCHAR(255) NOT NULL,
    client_identifier VARCHAR(255),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    port INTEGER NOT NULL,
    client_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mcp_sessions_status ON mcp_sessions(status);
CREATE INDEX idx_mcp_sessions_connection ON mcp_sessions(connection_id);
CREATE INDEX idx_mcp_sessions_time ON mcp_sessions(start_time, end_time);

-- ============================================================================
-- Persona Consultations Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS persona_consultations (
    consultation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES mcp_sessions(session_id) ON DELETE CASCADE,
    persona_name VARCHAR(255) NOT NULL,
    persona_version VARCHAR(50),
    operation VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    context JSONB NOT NULL,
    response TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consultations_session ON persona_consultations(session_id);
CREATE INDEX idx_consultations_persona ON persona_consultations(persona_name);
CREATE INDEX idx_consultations_operation ON persona_consultations(operation);
CREATE INDEX idx_consultations_timestamp ON persona_consultations(timestamp);

-- ============================================================================
-- Governance Decisions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS governance_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    operation VARCHAR(255) NOT NULL,
    context JSONB NOT NULL,
    approved BOOLEAN NOT NULL,
    confidence DECIMAL(3,2),
    personas_consulted JSONB,
    recommendations JSONB,
    warnings JSONB,
    outcome VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_decisions_session ON governance_decisions(session_id);
CREATE INDEX idx_decisions_operation ON governance_decisions(operation);
CREATE INDEX idx_decisions_outcome ON governance_decisions(outcome);
CREATE INDEX idx_decisions_timestamp ON governance_decisions(timestamp);

-- ============================================================================
-- MCP Metrics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_requests INTEGER NOT NULL DEFAULT 0,
    cache_hits INTEGER NOT NULL DEFAULT 0,
    cache_misses INTEGER NOT NULL DEFAULT 0,
    avg_response_time DECIMAL(10,3),
    errors INTEGER NOT NULL DEFAULT 0,
    active_sessions INTEGER,
    period_start TIMESTAMP,
    period_end TIMESTAMP
);

CREATE INDEX idx_metrics_session ON mcp_metrics(session_id);
CREATE INDEX idx_metrics_timestamp ON mcp_metrics(timestamp);
CREATE INDEX idx_metrics_period ON mcp_metrics(period_start, period_end);

-- ============================================================================
-- Audit Log Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES mcp_sessions(session_id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    user_identifier VARCHAR(255),
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_session ON mcp_audit_log(session_id);
CREATE INDEX idx_audit_event_type ON mcp_audit_log(event_type);
CREATE INDEX idx_audit_timestamp ON mcp_audit_log(timestamp);

-- ============================================================================
-- Configuration History Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp_config_history (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_type VARCHAR(100) NOT NULL, -- 'personas', 'rules', 'thresholds'
    config_version VARCHAR(50) NOT NULL,
    config_data JSONB NOT NULL,
    changed_by VARCHAR(255),
    change_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_config_type ON mcp_config_history(config_type);
CREATE INDEX idx_config_version ON mcp_config_history(config_version);
CREATE INDEX idx_config_timestamp ON mcp_config_history(timestamp);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to update session end time
CREATE OR REPLACE FUNCTION end_mcp_session(p_session_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE mcp_sessions
    SET end_time = CURRENT_TIMESTAMP,
        status = 'completed',
        updated_at = CURRENT_TIMESTAMP
    WHERE session_id = p_session_id
      AND status = 'active';
END;
$$ LANGUAGE plpgsql;

-- Function to get session metrics
CREATE OR REPLACE FUNCTION get_session_metrics(p_session_id UUID)
RETURNS TABLE(
    total_consultations BIGINT,
    avg_confidence DECIMAL,
    avg_response_time_ms DECIMAL,
    cache_hit_rate DECIMAL,
    unique_personas BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_consultations,
        AVG(confidence_score) as avg_confidence,
        AVG(response_time_ms) as avg_response_time_ms,
        AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as cache_hit_rate,
        COUNT(DISTINCT persona_name) as unique_personas
    FROM persona_consultations
    WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_mcp_sessions_updated_at
    BEFORE UPDATE ON mcp_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- Views
-- ============================================================================

-- Active sessions view
CREATE OR REPLACE VIEW active_mcp_sessions AS
SELECT 
    session_id,
    connection_id,
    client_identifier,
    start_time,
    extract(epoch from (CURRENT_TIMESTAMP - start_time)) as duration_seconds,
    port,
    client_metadata
FROM mcp_sessions
WHERE status = 'active';

-- Session summary view
CREATE OR REPLACE VIEW mcp_session_summary AS
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
-- Sample Data (for testing)
-- ============================================================================

-- Insert test session
-- INSERT INTO mcp_sessions (connection_id, client_identifier, port, client_metadata)
-- VALUES ('test-connection-001', 'claude-code-test', 8001, 
--         '{"version": "1.0", "environment": "development"}');

-- ============================================================================
-- Cleanup Script
-- ============================================================================

-- To remove all tables (use with caution):
-- DROP TABLE IF EXISTS mcp_audit_log CASCADE;
-- DROP TABLE IF EXISTS mcp_metrics CASCADE;
-- DROP TABLE IF EXISTS governance_decisions CASCADE;
-- DROP TABLE IF EXISTS persona_consultations CASCADE;
-- DROP TABLE IF EXISTS mcp_sessions CASCADE;
-- DROP TABLE IF EXISTS mcp_config_history CASCADE;
-- DROP VIEW IF EXISTS active_mcp_sessions;
-- DROP VIEW IF EXISTS mcp_session_summary;
-- DROP FUNCTION IF EXISTS end_mcp_session;
-- DROP FUNCTION IF EXISTS get_session_metrics;
-- DROP FUNCTION IF EXISTS update_updated_at;