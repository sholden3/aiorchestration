# Phase EIP-001: INTELLIGENCE_DISCOVERY Orchestration Prompt

**Target**: Claude Code Implementation  
**Duration**: 4 hours  
**Lead**: Multi-Persona Orchestration with Intelligence Integration  
**Phase Type**: Comprehensive Discovery with Intelligence Foundation  

---

## 🎯 **PHASE OBJECTIVE**

Implement comprehensive discovery system for **all 24 commands** with severity scoring (0-100), ROI calculation, cross-command intelligence foundation, and initial pattern detection capabilities.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Build Intelligence Foundation**
You MUST create the foundation for:
- All 24 command implementations
- Severity scoring system (0-100 points)
- ROI calculation framework
- Cross-command intelligence database
- Pattern detection initialization
- Metrics collection system

### **MULTI-COMMAND DISCOVERY**
- Not just code review - implement discovery for ALL commands
- Each command type has specific discovery patterns
- Intelligence sharing between commands from the start
- Pattern library initialization

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Universal Discovery Engine** (`libs/governance/core/intelligence_discovery.py`)

```python
class IntelligenceDiscoveryEngine:
    def __init__(self, governance_system, database_manager, cache_manager):
        # Use EXISTING systems
        self.governance = governance_system
        self.db = database_manager
        self.cache = cache_manager
        self.personas = PersonaManager()
        
        # Intelligence components
        self.severity_scorer = SeverityScorer()
        self.roi_calculator = ROICalculator()
        self.pattern_detector = PatternDetector()
        self.cross_intel = CrossCommandIntelligence()
        
        # Command registry for all 24 commands
        self.command_registry = self._initialize_all_commands()
    
    def _initialize_all_commands(self) -> dict:
        """Initialize all 24 command handlers"""
        return {
            # Core Analysis Commands
            'code-review': CodeReviewDiscovery(),
            'testing-review': TestingReviewDiscovery(),
            'security-review': SecurityReviewDiscovery(),
            'documentation-review': DocumentationReviewDiscovery(),
            'architecture-review': ArchitectureReviewDiscovery(),
            
            # Performance & Optimization
            'performance-review': PerformanceReviewDiscovery(),
            'dependency-analyze': DependencyAnalysisDiscovery(),
            'metrics-analyze': MetricsAnalysisDiscovery(),
            
            # Planning & Migration
            'architecture': ArchitecturePlanningDiscovery(),
            'migration-plan': MigrationPlanDiscovery(),
            'impact-check': ImpactCheckDiscovery(),
            'phase-review': PhaseReviewDiscovery(),
            
            # Intelligence & Analytics
            'knowledge-map': KnowledgeMapDiscovery(),
            'pattern-detect': PatternDetectDiscovery(),
            'feedback-analyze': FeedbackAnalysisDiscovery(),
            
            # Optimization
            'prompt-optimize': PromptOptimizationDiscovery(),
            'batch-review': BatchReviewDiscovery(),
            'progress-dashboard': DashboardDiscovery(),
            
            # Utility
            'bug-fix': BugFixDiscovery(),
            'copilot': CopilotDiscovery(),
            'research': ResearchDiscovery(),
            'help': HelpDiscovery()
        }
    
    async def discover_with_intelligence(self, command: str, target: str = None) -> IntelligenceResult:
        """
        Execute discovery with full intelligence integration:
        - Command-specific discovery
        - Severity scoring
        - ROI calculation
        - Pattern detection
        - Cross-command intelligence sharing
        """
        # Get command handler
        handler = self.command_registry[command]
        
        # Load cross-command intelligence
        related_findings = await self.cross_intel.get_related_findings(command)
        
        # Execute discovery with context
        raw_findings = await handler.discover(target, related_findings)
        
        # Apply severity scoring
        scored_findings = await self.apply_severity_scoring(raw_findings)
        
        # Calculate ROI for each finding
        prioritized_findings = await self.calculate_roi_scores(scored_findings)
        
        # Detect patterns
        patterns = await self.pattern_detector.detect_patterns(prioritized_findings)
        
        # Share findings with other commands
        await self.cross_intel.share_findings(command, prioritized_findings)
        
        # Store in intelligence database
        await self.store_intelligence_data(command, prioritized_findings, patterns)
        
        return IntelligenceResult(
            command=command,
            findings=prioritized_findings,
            patterns=patterns,
            cross_intelligence=related_findings
        )
```

### **2. Create Severity Scoring System** (`libs/governance/core/severity_scorer.py`)

```python
class SeverityScorer:
    def __init__(self):
        self.scoring_rules = {
            'security_impact': {'weight': 40, 'factors': [
                'data_exposure', 'authentication', 'authorization', 
                'injection', 'cryptography'
            ]},
            'user_impact': {'weight': 30, 'factors': [
                'availability', 'data_integrity', 'user_experience', 
                'functionality'
            ]},
            'technical_debt': {'weight': 20, 'factors': [
                'maintainability', 'complexity', 'duplication', 'coupling'
            ]},
            'maintenance_burden': {'weight': 10, 'factors': [
                'documentation', 'test_coverage', 'code_clarity'
            ]}
        }
    
    async def calculate_severity_score(self, finding: dict) -> int:
        """
        Calculate 0-100 severity score for any finding
        """
        total_score = 0
        
        # Security Impact (0-40)
        security_score = self._calculate_security_impact(finding)
        total_score += min(40, security_score)
        
        # User Impact (0-30)
        user_score = self._calculate_user_impact(finding)
        total_score += min(30, user_score)
        
        # Technical Debt (0-20)
        debt_score = self._calculate_technical_debt(finding)
        total_score += min(20, debt_score)
        
        # Maintenance Burden (0-10)
        maintenance_score = self._calculate_maintenance_burden(finding)
        total_score += min(10, maintenance_score)
        
        return min(100, total_score)
    
    def get_severity_level(self, score: int) -> str:
        """Map score to severity level"""
        if score >= 90:
            return "CRITICAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
```

### **3. Create ROI Calculator** (`libs/governance/core/roi_calculator.py`)

```python
class ROICalculator:
    def __init__(self):
        self.effort_estimator = EffortEstimator()
        self.value_calculator = ValueCalculator()
    
    async def calculate_roi(self, finding: dict) -> float:
        """
        Calculate ROI score for prioritization
        ROI = (Risk Reduction + Performance Gain) / Implementation Effort
        """
        # Calculate risk reduction (0-100)
        risk_reduction = await self._calculate_risk_reduction(finding)
        
        # Calculate performance gain (0-100)
        performance_gain = await self._calculate_performance_gain(finding)
        
        # Estimate implementation effort (1-100 story points)
        effort = await self.effort_estimator.estimate(finding)
        
        # Calculate ROI
        roi = (risk_reduction + performance_gain) / max(effort, 1)
        
        return round(roi, 2)
    
    async def _calculate_risk_reduction(self, finding: dict) -> float:
        """Calculate risk reduction value"""
        base_risk = finding.get('severity_score', 50)
        mitigation_factor = finding.get('mitigation_effectiveness', 0.8)
        return base_risk * mitigation_factor
    
    async def _calculate_performance_gain(self, finding: dict) -> float:
        """Calculate performance improvement value"""
        current_performance = finding.get('current_performance', 50)
        expected_improvement = finding.get('expected_improvement', 0.3)
        return current_performance * expected_improvement
    
    def get_priority_from_roi(self, roi: float) -> str:
        """Map ROI to priority level"""
        if roi > 5.0:
            return "IMMEDIATE"
        elif roi >= 2.0:
            return "CURRENT_SPRINT"
        elif roi >= 1.0:
            return "NEXT_QUARTER"
        else:
            return "BACKLOG"
```

### **4. Create Cross-Command Intelligence System** (`libs/governance/core/cross_command_intelligence.py`)

```python
class CrossCommandIntelligence:
    def __init__(self, database_manager, cache_manager):
        self.db = database_manager
        self.cache = cache_manager
        self.command_graph = self._build_command_graph()
    
    def _build_command_graph(self) -> dict:
        """Define relationships between all 24 commands"""
        return {
            'code-review': {
                'produces': ['code_quality_issues', 'refactoring_needs', 'complexity_metrics'],
                'consumes': ['architecture_decisions', 'performance_bottlenecks'],
                'feeds_into': ['testing-review', 'documentation-review', 'performance-review']
            },
            'security-review': {
                'produces': ['security_vulnerabilities', 'compliance_gaps', 'risk_assessment'],
                'consumes': ['dependency_vulnerabilities', 'code_quality_issues'],
                'feeds_into': ['bug-fix', 'migration-plan', 'dependency-analyze']
            },
            'performance-review': {
                'produces': ['performance_bottlenecks', 'optimization_opportunities'],
                'consumes': ['architecture_decisions', 'code_quality_issues'],
                'feeds_into': ['code-review', 'architecture-review', 'prompt-optimize']
            },
            'pattern-detect': {
                'produces': ['recurring_patterns', 'systemic_issues', 'improvement_trends'],
                'consumes': ['all_command_outputs'],
                'feeds_into': ['all_commands']
            },
            # ... define all 24 command relationships
        }
    
    async def share_findings(self, source_command: str, findings: list):
        """Share findings with dependent commands"""
        targets = self.command_graph[source_command]['feeds_into']
        
        for target in targets:
            cache_key = f"cross_intel:{target}:{source_command}"
            await self.cache.set_hot(cache_key, findings, ttl=3600)
            
        # Store in database for persistence
        await self._store_shared_findings(source_command, findings)
    
    async def get_related_findings(self, command: str) -> list:
        """Get findings from commands this one depends on"""
        dependencies = self.command_graph[command]['consumes']
        related_findings = []
        
        for dependency in dependencies:
            # Try cache first
            cache_key = f"cross_intel:{command}:{dependency}"
            cached = await self.cache.get_hot(cache_key)
            
            if cached:
                related_findings.extend(cached)
            else:
                # Fall back to database
                db_findings = await self._load_shared_findings(dependency)
                related_findings.extend(db_findings)
        
        return related_findings
```

### **5. Create Pattern Detection Engine** (`libs/governance/core/pattern_detector.py`)

```python
class PatternDetector:
    def __init__(self, database_manager):
        self.db = database_manager
        self.pattern_threshold = 3
        self.pattern_library = {}
    
    async def detect_patterns(self, findings: list) -> list:
        """
        Detect recurring patterns across findings
        """
        patterns = []
        
        # Group findings by similarity
        grouped = self._group_by_similarity(findings)
        
        for group_key, group_findings in grouped.items():
            if len(group_findings) >= self.pattern_threshold:
                pattern = await self._create_pattern(group_key, group_findings)
                patterns.append(pattern)
                
                # Store in pattern library
                await self._store_pattern(pattern)
        
        return patterns
    
    def _group_by_similarity(self, findings: list) -> dict:
        """Group findings by similarity metrics"""
        groups = {}
        
        for finding in findings:
            # Create similarity key based on multiple factors
            key = self._generate_similarity_key(finding)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(finding)
        
        return groups
    
    async def _create_pattern(self, key: str, findings: list) -> dict:
        """Create pattern object from grouped findings"""
        return {
            'pattern_id': f"PAT-{hash(key)}",
            'pattern_type': self._determine_pattern_type(findings),
            'occurrences': len(findings),
            'affected_files': list(set(f['file_path'] for f in findings)),
            'severity_average': sum(f['severity_score'] for f in findings) / len(findings),
            'recommended_systemic_fix': await self._generate_systemic_fix(findings),
            'first_seen': min(f.get('discovered_at') for f in findings),
            'last_seen': max(f.get('discovered_at') for f in findings)
        }
```

---

## 🗄️ **DATABASE SCHEMA - INTELLIGENCE FOUNDATION**

```sql
-- Intelligence foundation tables
CREATE TABLE IF NOT EXISTS intelligence_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    command VARCHAR(50) NOT NULL,
    target_path TEXT,
    total_findings INTEGER DEFAULT 0,
    patterns_detected INTEGER DEFAULT 0,
    cross_intel_used BOOLEAN DEFAULT false,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'in_progress'
);

CREATE TABLE IF NOT EXISTS intelligence_findings (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES intelligence_sessions(session_id),
    command_source VARCHAR(50) NOT NULL,
    finding_type VARCHAR(100) NOT NULL,
    severity_score INTEGER CHECK (severity_score >= 0 AND severity_score <= 100),
    severity_level VARCHAR(20),
    roi_score DECIMAL(5,2),
    priority VARCHAR(20),
    file_path TEXT,
    line_numbers INTEGER[],
    description TEXT,
    pattern_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pattern_library (
    pattern_id VARCHAR(100) PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(200),
    occurrences INTEGER DEFAULT 1,
    affected_files TEXT[],
    severity_average DECIMAL(5,2),
    recommended_fix TEXT,
    success_rate DECIMAL(3,2),
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS cross_command_intelligence (
    id SERIAL PRIMARY KEY,
    source_command VARCHAR(50) NOT NULL,
    target_command VARCHAR(50) NOT NULL,
    finding_type VARCHAR(100),
    shared_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics_tracking (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    command_source VARCHAR(50),
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_intelligence_findings_severity ON intelligence_findings(severity_score);
CREATE INDEX idx_intelligence_findings_roi ON intelligence_findings(roi_score);
CREATE INDEX idx_pattern_library_occurrences ON pattern_library(occurrences);
CREATE INDEX idx_cross_command_source ON cross_command_intelligence(source_command);
CREATE INDEX idx_cross_command_target ON cross_command_intelligence(target_command);
```

---

## 👥 **PERSONA INTEGRATION**

### **Dynamic Persona Selection for Each Command**

```python
class PersonaOrchestrator:
    def __init__(self, persona_manager):
        self.personas = persona_manager
        self.persona_templates = PERSONA_TEMPLATES
        self.effectiveness_scores = {}
    
    async def select_personas_for_command(self, command: str, context: dict) -> list:
        """
        Select optimal 3 personas for any command based on:
        - Command type and requirements
        - Historical effectiveness scores
        - Current patterns detected
        - Project phase and context
        """
        # Get default personas for command type
        defaults = self._get_default_personas(command)
        
        # Load effectiveness scores
        scores = await self._load_effectiveness_scores(command)
        
        # Consider current patterns
        patterns = context.get('patterns', [])
        
        # Optimize selection
        selected = self._optimize_selection(defaults, scores, patterns)
        
        return selected[:3]  # Always return exactly 3 personas
    
    def _get_default_personas(self, command: str) -> list:
        """Get default persona assignments by command"""
        defaults = {
            'code-review': ['architect', 'optimizer', 'guardian'],
            'security-review': ['guardian', 'auditor', 'integration_specialist'],
            'performance-review': ['optimizer', 'data_scientist', 'architect'],
            'testing-review': ['guardian', 'auditor', 'user_advocate'],
            'documentation-review': ['user_advocate', 'auditor', 'architect'],
            'pattern-detect': ['data_scientist', 'architect', 'optimizer'],
            # ... all 24 commands
        }
        return defaults.get(command, ['auditor', 'architect', 'guardian'])
```

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Discovery Performance**
- [ ] Full codebase discovery: <2 minutes
- [ ] Severity scoring: <50ms per finding
- [ ] ROI calculation: <100ms per finding
- [ ] Pattern detection: <30 seconds for 1000 findings
- [ ] Cross-command intelligence lookup: <100ms

### **Database Performance**
- [ ] Finding storage: <10ms per record
- [ ] Pattern library updates: <50ms
- [ ] Cross-intelligence queries: <100ms
- [ ] Metrics tracking: <5ms per metric

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Intelligence Governance**
- [ ] All severity scores follow governance formula
- [ ] ROI calculations use approved methodology
- [ ] Pattern detection respects privacy rules
- [ ] Cross-command sharing follows security guidelines
- [ ] Metrics collection complies with regulations

---

## 📊 **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] All 24 commands have discovery handlers
- [ ] Severity scoring functional for all finding types
- [ ] ROI calculation working accurately
- [ ] Pattern detection identifying recurring issues
- [ ] Cross-command intelligence sharing operational

### **Intelligence Requirements**
- [ ] >90% of findings have severity scores
- [ ] 100% of findings have ROI calculations
- [ ] Pattern detection accuracy >80%
- [ ] Cross-command data available within 100ms
- [ ] Metrics tracking all key indicators

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Core Intelligence Engine** (1.5 hours)
1. Implement `IntelligenceDiscoveryEngine` with all 24 commands
2. Create severity scoring system
3. Implement ROI calculator
4. Test with sample data

### **Step 2: Cross-Command Intelligence** (1 hour)
1. Build command relationship graph
2. Implement intelligence sharing mechanism
3. Create intelligence retrieval system
4. Test cross-command data flow

### **Step 3: Pattern Detection** (1 hour)
1. Implement pattern detection engine
2. Create pattern library management
3. Test pattern identification
4. Validate systemic fix recommendations

### **Step 4: Database & Integration** (30 minutes)
1. Create all database tables
2. Test data storage and retrieval
3. Validate cache integration
4. Performance testing

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/intelligence_discovery.py` - Main discovery engine
- [ ] `libs/governance/core/severity_scorer.py` - Severity scoring system
- [ ] `libs/governance/core/roi_calculator.py` - ROI calculation
- [ ] `libs/governance/core/cross_command_intelligence.py` - Intelligence sharing
- [ ] `libs/governance/core/pattern_detector.py` - Pattern detection
- [ ] `libs/governance/core/persona_orchestrator.py` - Persona selection
- [ ] Database schema with all intelligence tables

### **Documentation Updates**
- [ ] Update `TRACKER.md` with EIP-001 completion
- [ ] Update `STATUS.md` with intelligence capabilities
- [ ] Add entries to `DECISIONS.md` for intelligence architecture
- [ ] Document command relationships and data flow

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **ALL 24 COMMANDS**: Not just code review - implement full platform
2. **INTELLIGENCE FIRST**: Every finding scored and prioritized
3. **CROSS-COMMAND**: Data flows between related commands
4. **PATTERN DETECTION**: Identify systemic issues from day one
5. **METRICS FOUNDATION**: Track everything for continuous improvement

---

**Remember**: This phase creates the intelligence foundation for ALL 24 commands, not just code review. Every finding gets severity scoring, ROI calculation, and contributes to pattern detection and cross-command intelligence.