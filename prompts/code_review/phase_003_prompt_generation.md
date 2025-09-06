# Phase CRA-003: COPILOT_PROMPT_ENGINE Orchestration Prompt

**Target**: GitHub Copilot Implementation with Claude Code Orchestration  
**Duration**: 6 hours  
**Lead**: GitHub Copilot (Implementation) + Dr. Sarah Chen (Governance Oversight)  
**Phase Type**: Prompt Generation & Implementation Guidance  

---

## 🎯 **PHASE OBJECTIVE**

Generate detailed, persona-specific GitHub Copilot prompts based on hook analysis results, with comprehensive governance rule integration and safety mechanisms for code implementation.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Use Analysis Results from CRA-002**
You MUST use data from previous phases:
- Hook execution results from `hook_execution_log` table
- Plugin analysis results from `plugin_execution_log` table  
- Issue classifications from `discovered_issues` table
- Persona consultations from existing `PersonaManager` results

### **PROMPT GENERATION REQUIREMENTS**
- Persona-specific expertise integration
- Governance rule embedding in prompts
- Safety checks and rollback procedures
- Database-driven prompt customization

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Copilot Prompt Generator** (`libs/governance/core/copilot_prompt_generator.py`)

```python
# Template structure - integrate with existing systems
class CopilotPromptGenerator:
    def __init__(self, database_manager, persona_manager, governance_system):
        # Use EXISTING systems
        self.db = database_manager
        self.personas = persona_manager  
        self.governance = governance_system
        self.prompt_templates = {}
        self.safety_rules = {}
    
    async def generate_prompts_for_session(self, session_id: str) -> GeneratedPrompts:
        """
        Generate all Copilot prompts for a completed analysis session:
        - Load analysis results from database
        - Route issues to appropriate personas
        - Generate persona-specific prompts
        - Embed governance rules and safety checks
        """
        pass
    
    async def generate_persona_prompt(self, issue: Issue, persona: str, context: dict) -> CopilotPrompt:
        """Generate prompt specific to persona expertise"""
        pass
    
    async def embed_governance_rules(self, prompt: CopilotPrompt, issue: Issue) -> CopilotPrompt:
        """Embed relevant governance rules into prompt"""
        pass
```

**Requirements**:
- [ ] Load analysis results from CRA-002 database tables
- [ ] Generate prompts for each persona based on their expertise
- [ ] Embed governance rules from existing `config.yaml`
- [ ] Include safety checks and rollback procedures
- [ ] Store generated prompts in database for tracking
- [ ] Support prompt customization via database configuration

### **2. Create Persona-Specific Prompt Templates** (`prompts/copilot_templates/`)

#### **Sarah Chen - Architecture Prompts** (`prompts/copilot_templates/architecture_refactoring.md`)

```markdown
You are Dr. Sarah Chen, Senior Backend & Infrastructure Architect with 12+ years experience in Python, FastAPI, database optimization, and system architecture.

EXPERTISE AREAS:
- Python backend development and optimization
- FastAPI design patterns and best practices
- Database schema design and query optimization
- System architecture and scalability planning
- Infrastructure patterns and deployment strategies

ANALYSIS CONTEXT:
- Session ID: {{session_id}}
- Issue Type: {{issue.type}}
- Severity: {{issue.severity}}
- File Path: {{issue.file_path}}
- Lines: {{issue.line_numbers}}

GOVERNANCE REQUIREMENTS:
{{governance_rules}}

SAFETY PROTOCOLS:
{{safety_checks}}

TASK: {{issue.description}}

SPECIFIC REQUIREMENTS:
1. {{requirement_1}}
2. {{requirement_2}}
3. {{requirement_3}}

CONSTRAINTS:
- Maintain backward compatibility with existing APIs
- Follow existing database patterns in {{database_patterns}}
- Use current caching strategies from {{cache_patterns}}
- Preserve all existing tests and add comprehensive new tests
- Update documentation following governance standards

IMPLEMENTATION APPROACH:
1. Analysis Phase: Review current implementation and identify architectural issues
2. Design Phase: Create improved architecture following SOLID principles
3. Implementation Phase: Refactor incrementally with comprehensive testing
4. Validation Phase: Ensure all governance requirements are met

ROLLBACK PLAN:
{{rollback_procedures}}

FOCUS: Create maintainable, scalable, and testable architecture while maintaining system reliability and following all governance protocols.
```

#### **Marcus Rodriguez - Performance Prompts** (`prompts/copilot_templates/performance_optimization.md`)

```markdown
You are Marcus Rodriguez, Senior Performance Engineer with expertise in optimization, profiling, and scalable system design.

EXPERTISE AREAS:
- Performance profiling and bottleneck identification
- Database query optimization and indexing strategies
- Caching implementations and cache invalidation
- Memory management and resource optimization
- Load testing and capacity planning

ANALYSIS CONTEXT:
- Session ID: {{session_id}}
- Performance Issue: {{issue.type}}
- Impact Level: {{issue.severity}}
- File Path: {{issue.file_path}}
- Performance Metrics: {{performance_data}}

GOVERNANCE REQUIREMENTS:
{{governance_rules}}

CURRENT PERFORMANCE BASELINE:
{{current_metrics}}

TASK: {{issue.description}}

OPTIMIZATION REQUIREMENTS:
1. Target performance improvement: {{target_improvement}}
2. Memory usage constraints: {{memory_limits}}
3. Response time requirements: {{response_time_targets}}

CONSTRAINTS:
- Must maintain existing functionality
- Cannot break current API contracts
- Must preserve data consistency
- Follow existing error handling patterns

IMPLEMENTATION STRATEGY:
1. Profile and Measure: Identify specific bottlenecks
2. Optimize Critical Path: Focus on highest impact improvements  
3. Test Performance: Validate improvements with benchmarks
4. Monitor Regression: Ensure no performance degradation

ROLLBACK PLAN:
{{rollback_procedures}}

FOCUS: Achieve measurable performance improvements while maintaining system stability and functionality.
```

#### **Emily Watson - Testing Prompts** (`prompts/copilot_templates/testing_enhancement.md`)

```markdown
You are Emily Watson, QA Lead and Testing Architect specializing in comprehensive test strategy design and implementation.

EXPERTISE AREAS:
- Test strategy design and implementation
- Unit, integration, and end-to-end testing
- Test automation and CI/CD integration
- Coverage analysis and quality metrics
- Flaky test identification and resolution

ANALYSIS CONTEXT:
- Session ID: {{session_id}}
- Testing Issue: {{issue.type}}
- Priority: {{issue.severity}}
- Component: {{issue.file_path}}
- Current Coverage: {{coverage_data}}

GOVERNANCE REQUIREMENTS:
{{governance_rules}}

TESTING REQUIREMENTS:
- Minimum unit test coverage: 85%
- Integration test coverage: 80%
- All tests must pass in CI/CD pipeline
- No flaky tests allowed in production
- Performance tests for critical paths

TASK: {{issue.description}}

TESTING STRATEGY:
1. {{testing_requirement_1}}
2. {{testing_requirement_2}}
3. {{testing_requirement_3}}

CONSTRAINTS:
- Use existing testing frameworks and patterns
- Follow current test organization structure
- Maintain test execution speed <2 minutes
- Integrate with existing CI/CD pipeline

IMPLEMENTATION APPROACH:
1. Analyze Current Coverage: Identify gaps in test coverage
2. Design Test Cases: Create comprehensive test scenarios
3. Implement Tests: Write tests following existing patterns
4. Validate Quality: Ensure tests are reliable and maintainable

ROLLBACK PLAN:
{{rollback_procedures}}

FOCUS: Create comprehensive, reliable, and maintainable test coverage that ensures system quality and prevents regressions.
```

#### **Rachel Torres - Documentation Prompts** (`prompts/copilot_templates/documentation_improvement.md`)

```markdown
You are Rachel Torres, Technical Documentation Lead with expertise in creating clear, comprehensive, and maintainable technical documentation.

EXPERTISE AREAS:
- Technical documentation architecture and strategy
- API documentation and developer guides
- Documentation automation and tooling
- Information architecture and user experience
- Documentation maintenance and governance

ANALYSIS CONTEXT:
- Session ID: {{session_id}}
- Documentation Issue: {{issue.type}}
- Priority: {{issue.severity}}
- Component: {{issue.file_path}}
- Documentation Gap: {{documentation_analysis}}

GOVERNANCE REQUIREMENTS:
{{governance_rules}}

DOCUMENTATION STANDARDS:
{{documentation_standards}}

TASK: {{issue.description}}

DOCUMENTATION REQUIREMENTS:
1. {{doc_requirement_1}}
2. {{doc_requirement_2}}
3. {{doc_requirement_3}}

CONSTRAINTS:
- Follow existing documentation structure and patterns
- Use established templates and formatting
- Ensure documentation passes governance validation
- Integrate with existing documentation tools

IMPLEMENTATION APPROACH:
1. Gap Analysis: Identify specific documentation deficiencies
2. Content Strategy: Plan comprehensive documentation coverage
3. Content Creation: Write clear, accurate, and maintainable documentation
4. Quality Validation: Ensure documentation meets governance standards

ROLLBACK PLAN:
{{rollback_procedures}}

FOCUS: Create clear, comprehensive, and maintainable documentation that enhances developer productivity and system understanding.
```

### **3. Create Prompt Customization System** (`libs/governance/core/prompt_customizer.py`)

```python
class PromptCustomizer:
    def __init__(self, database_manager, config_manager):
        # Use EXISTING systems
        pass
    
    async def customize_prompt_for_issue(self, base_prompt: str, issue: Issue, context: dict) -> str:
        """
        Customize prompt with:
        - Issue-specific details
        - Current governance rules
        - Safety protocols
        - Rollback procedures
        """
        pass
    
    async def load_governance_rules_for_issue(self, issue: Issue) -> dict:
        """Load relevant governance rules from existing config"""
        pass
    
    async def generate_safety_checks(self, issue: Issue) -> list:
        """Generate safety checks based on issue type and severity"""
        pass
    
    async def create_rollback_procedures(self, issue: Issue) -> dict:
        """Create rollback procedures for the specific change"""
        pass
```

### **4. Create Prompt Execution Orchestrator** (`libs/governance/core/prompt_orchestrator.py`)

```python
class PromptOrchestrator:
    def __init__(self, prompt_generator, database_manager, governance_system):
        # Use EXISTING systems
        pass
    
    async def orchestrate_copilot_implementation(self, session_id: str) -> OrchestrationResult:
        """
        Orchestrate the complete Copilot implementation process:
        1. Generate prompts for all issues in session
        2. Execute prompts in priority order
        3. Validate implementations against governance
        4. Handle errors and rollbacks
        5. Update database with results
        """
        pass
    
    async def execute_prompt_sequence(self, prompts: List[CopilotPrompt]) -> ExecutionResults:
        """Execute prompts in proper sequence with validation"""
        pass
    
    async def validate_implementation(self, implementation: CodeChange) -> ValidationResult:
        """Validate Copilot implementation against governance rules"""
        pass
```

---

## 🗄️ **DATABASE SCHEMA EXTENSIONS**

### **Prompt Management Tables** (Extend existing database)

```sql
-- Add to existing database schema
CREATE TABLE IF NOT EXISTS copilot_prompts (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    issue_id INTEGER REFERENCES discovered_issues(id),
    persona VARCHAR(50) NOT NULL,
    prompt_template VARCHAR(100) NOT NULL,
    generated_prompt TEXT NOT NULL,
    governance_rules JSONB,
    safety_checks JSONB,
    rollback_procedures JSONB,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS copilot_executions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER REFERENCES copilot_prompts(id),
    execution_start TIMESTAMP DEFAULT NOW(),
    execution_end TIMESTAMP,
    success BOOLEAN,
    implementation_summary TEXT,
    files_changed TEXT[],
    governance_validation_result JSONB,
    error_message TEXT,
    rollback_executed BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS implementation_tracking (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    total_prompts INTEGER,
    completed_prompts INTEGER,
    failed_prompts INTEGER,
    overall_success_rate DECIMAL(5,2),
    total_files_changed INTEGER,
    governance_compliance_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

---

## ⚙️ **GOVERNANCE RULE INTEGRATION**

### **5. Governance Rule Embedder** (`libs/governance/core/governance_embedder.py`)

```python
class GovernanceRuleEmbedder:
    def __init__(self, governance_system, config_manager):
        # Use EXISTING governance system
        pass
    
    async def get_rules_for_issue(self, issue: Issue) -> GovernanceRules:
        """
        Extract relevant governance rules for specific issue:
        - File creation restrictions
        - Naming conventions
        - Testing requirements
        - Documentation standards
        - Security patterns
        """
        pass
    
    async def embed_rules_in_prompt(self, prompt: str, rules: GovernanceRules) -> str:
        """Embed governance rules into Copilot prompt"""
        pass
    
    async def generate_validation_criteria(self, issue: Issue) -> ValidationCriteria:
        """Generate validation criteria based on governance rules"""
        pass
```

### **6. Safety Protocol Generator** (`libs/governance/core/safety_protocol_generator.py`)

```python
class SafetyProtocolGenerator:
    def __init__(self, governance_system, database_manager):
        # Use EXISTING systems
        pass
    
    async def generate_safety_checks(self, issue: Issue) -> SafetyChecks:
        """
        Generate safety checks based on:
        - Issue severity and type
        - Files being modified
        - Potential impact scope
        - Existing governance rules
        """
        pass
    
    async def create_rollback_procedures(self, issue: Issue) -> RollbackProcedures:
        """Create detailed rollback procedures"""
        pass
    
    async def validate_safety_compliance(self, implementation: CodeChange) -> SafetyValidation:
        """Validate implementation against safety protocols"""
        pass
```

---

## 🔗 **INTEGRATION POINTS**

### **Analysis Results Integration**
- [ ] Load hook execution results from CRA-002
- [ ] Use plugin analysis data for prompt context
- [ ] Integrate persona consultation results
- [ ] Access issue classifications and priorities

### **Governance Integration**
- [ ] Embed existing governance rules from `config.yaml`
- [ ] Use existing validation patterns
- [ ] Follow current safety protocols
- [ ] Maintain existing audit logging

### **Database Integration**
- [ ] Store all prompts in database for tracking
- [ ] Log execution results and outcomes
- [ ] Track implementation success rates
- [ ] Maintain comprehensive audit trail

### **Cache Integration**  
- [ ] Cache generated prompts for reuse
- [ ] Cache governance rule lookups
- [ ] Cache persona consultation results
- [ ] Optimize prompt generation performance

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Prompt Generation Performance**
- [ ] Prompt generation: <30 seconds per issue
- [ ] Governance rule embedding: <5 seconds per prompt
- [ ] Safety protocol generation: <10 seconds per issue
- [ ] Database storage: <100ms per prompt

### **Execution Orchestration Performance**
- [ ] Prompt sequence planning: <60 seconds
- [ ] Execution monitoring: Real-time updates
- [ ] Validation processing: <30 seconds per implementation
- [ ] Rollback execution: <2 minutes if needed

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Safety Requirements**
- [ ] All prompts include comprehensive safety checks
- [ ] Rollback procedures defined for every change
- [ ] Governance rule validation before implementation
- [ ] Error handling with graceful degradation

### **Quality Requirements**
- [ ] Prompts tested with sample implementations
- [ ] Governance rule accuracy verified
- [ ] Safety protocol effectiveness validated
- [ ] Database integrity maintained

### **Audit Requirements**
- [ ] All prompt generation logged
- [ ] Execution results tracked
- [ ] Implementation outcomes recorded
- [ ] Compliance scores calculated

---

## 📊 **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] Prompts generated for all analysis issues
- [ ] Persona expertise properly integrated
- [ ] Governance rules accurately embedded
- [ ] Safety protocols comprehensive and effective

### **Quality Requirements**
- [ ] >90% of generated prompts result in successful implementations
- [ ] 100% governance rule compliance in prompts
- [ ] All safety checks functional and tested
- [ ] Rollback procedures validated

### **Performance Requirements**
- [ ] All generation times within specified limits
- [ ] Database operations meet latency requirements
- [ ] Cache utilization optimizes performance
- [ ] Memory usage within acceptable bounds

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Prompt Generator Core** (2 hours)
1. Implement `CopilotPromptGenerator` with database integration
2. Create persona-specific prompt templates
3. Test prompt generation with sample data
4. Validate database storage and retrieval

### **Step 2: Governance Integration** (2 hours)
1. Implement `GovernanceRuleEmbedder`
2. Create `SafetyProtocolGenerator`
3. Test governance rule embedding
4. Validate safety protocol generation

### **Step 3: Customization and Orchestration** (1.5 hours)
1. Implement `PromptCustomizer`
2. Create `PromptOrchestrator` 
3. Test end-to-end prompt generation
4. Validate orchestration workflow

### **Step 4: Validation and Testing** (30 minutes)
1. Test all components with CRA-002 results
2. Verify governance compliance
3. Validate safety protocols
4. Test database integration

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/copilot_prompt_generator.py` - Main prompt generator
- [ ] `prompts/copilot_templates/` - Persona-specific prompt templates
- [ ] `libs/governance/core/prompt_customizer.py` - Prompt customization
- [ ] `libs/governance/core/prompt_orchestrator.py` - Execution orchestration
- [ ] `libs/governance/core/governance_embedder.py` - Rule integration
- [ ] `libs/governance/core/safety_protocol_generator.py` - Safety protocols
- [ ] Database schema extensions for prompt management

### **Documentation Updates**
- [ ] Update `TRACKER.md` with CRA-003 completion
- [ ] Update `STATUS.md` with prompt generation capabilities
- [ ] Add entries to `DECISIONS.md` for prompt design choices
- [ ] Document prompt templates and customization options

### **Validation Outputs**
- [ ] Sample prompts generated for each persona
- [ ] Governance rule embedding verification
- [ ] Safety protocol validation results
- [ ] Performance benchmark results

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **PERSONA ACCURACY**: Prompts must accurately reflect each persona's expertise
2. **GOVERNANCE INTEGRATION**: All relevant governance rules must be embedded
3. **SAFETY FIRST**: Comprehensive safety checks and rollback procedures required
4. **DATABASE DRIVEN**: All prompts and results stored for tracking and analysis
5. **PERFORMANCE OPTIMIZED**: Meet all generation and execution time requirements

---

## 🎯 **NEXT PHASE PREPARATION**

Upon successful completion of CRA-003:
- [ ] Validate all prompts generate correctly
- [ ] Confirm governance rules properly embedded
- [ ] Test safety protocols and rollback procedures
- [ ] Verify database storage and retrieval
- [ ] Prepare prompts for CRA-004 configuration integration

**Phase CRA-004 Input**: Generated prompts and execution tracking data will be used for database-driven configuration management and UI preparation.

---

**Remember**: This phase creates the intelligence that guides GitHub Copilot implementations. Focus on creating prompts that are comprehensive, safe, and aligned with each persona's expertise while embedding all necessary governance rules.