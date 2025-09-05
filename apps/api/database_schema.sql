-- Database Schema for AI Assistant
-- PostgreSQL schema with best practices and templates storage

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS rule_violations CASCADE;
DROP TABLE IF EXISTS template_variables CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS best_practices CASCADE;
DROP TABLE IF EXISTS rules CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- Categories table (shared by rules, best practices, and templates)
CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('rule', 'practice', 'template', 'all')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rules table
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) REFERENCES categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    enforcement VARCHAR(20) NOT NULL CHECK (enforcement IN ('mandatory', 'recommended', 'optional')),
    examples JSONB DEFAULT '[]'::jsonb,
    anti_patterns JSONB DEFAULT '[]'::jsonb,
    violations_consequence TEXT,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0 CHECK (priority >= 0)
);

-- Best Practices table
CREATE TABLE best_practices (
    practice_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) REFERENCES categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    benefits JSONB DEFAULT '[]'::jsonb,
    implementation_guide TEXT,
    anti_patterns JSONB DEFAULT '[]'::jsonb,
    references JSONB DEFAULT '[]'::jsonb,
    examples JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT true,
    is_required BOOLEAN DEFAULT false,
    priority VARCHAR(20) CHECK (priority IN ('P0-CRITICAL', 'P1-HIGH', 'P2-MEDIUM', 'P3-LOW')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates table
CREATE TABLE templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) REFERENCES categories(id),
    template_content TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);

-- Template Variables table (for complex variable definitions)
CREATE TABLE template_variables (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) REFERENCES templates(template_id) ON DELETE CASCADE,
    variable_name VARCHAR(100) NOT NULL,
    variable_type VARCHAR(50) NOT NULL CHECK (variable_type IN ('text', 'multiline', 'select', 'multiselect', 'boolean', 'number')),
    default_value TEXT,
    options JSONB DEFAULT '[]'::jsonb,
    is_required BOOLEAN DEFAULT false,
    description TEXT,
    validation_regex TEXT,
    UNIQUE(template_id, variable_name)
);

-- Rule Violations tracking table
CREATE TABLE rule_violations (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(50) REFERENCES rules(rule_id),
    file_path TEXT,
    line_number INTEGER,
    violation_description TEXT,
    severity VARCHAR(20),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Indexes for performance
CREATE INDEX idx_rules_category ON rules(category);
CREATE INDEX idx_rules_active ON rules(active);
CREATE INDEX idx_rules_severity ON rules(severity);
CREATE INDEX idx_best_practices_category ON best_practices(category);
CREATE INDEX idx_best_practices_active ON best_practices(is_active);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_active ON templates(is_active);
CREATE INDEX idx_violations_unresolved ON rule_violations(resolved) WHERE resolved = false;

-- Insert default categories
INSERT INTO categories (id, name, description, type) VALUES
    ('file-operations', 'File Operations', 'File system operations and management', 'all'),
    ('general', 'General', 'General development practices', 'all'),
    ('prompt-engineering', 'Prompt Engineering', 'Claude and AI prompt best practices', 'all'),
    ('security', 'Security', 'Security best practices and rules', 'all'),
    ('performance', 'Performance', 'Performance optimization practices', 'all'),
    ('testing', 'Testing', 'Testing strategies and requirements', 'all'),
    ('requirements-gathering', 'Requirements', 'Requirements gathering and anti-boilerplate', 'all'),
    ('documentation', 'Documentation', 'Code and project documentation', 'template'),
    ('git-workflow', 'Git Workflow', 'Git commits and pull requests', 'template'),
    ('analysis', 'Analysis', 'Code analysis and review', 'template'),
    ('debugging', 'Debugging', 'Debugging and troubleshooting', 'template'),
    ('code-generation', 'Code Generation', 'Code generation templates', 'template'),
    ('project-management', 'Project Management', 'Project planning and management', 'template'),
    ('database', 'Database', 'Database design and operations', 'template'),
    ('operations', 'Operations', 'Deployment and operations', 'template');

-- Create update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_best_practices_updated_at BEFORE UPDATE ON best_practices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Create view for active rules with category names
CREATE VIEW active_rules_view AS
SELECT 
    r.rule_id,
    r.title,
    r.description,
    c.name as category_name,
    r.severity,
    r.enforcement,
    r.examples,
    r.anti_patterns,
    r.created_at,
    r.updated_at
FROM rules r
JOIN categories c ON r.category = c.id
WHERE r.active = true;

-- Create view for active best practices with category names
CREATE VIEW active_best_practices_view AS
SELECT 
    bp.practice_id,
    bp.title,
    bp.description,
    c.name as category_name,
    bp.is_required,
    bp.priority,
    bp.examples,
    bp.anti_patterns,
    bp.created_at,
    bp.updated_at
FROM best_practices bp
JOIN categories c ON bp.category = c.id
WHERE bp.is_active = true;

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;