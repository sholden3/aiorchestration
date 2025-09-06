# Phase EIP-002: MODULAR_INTELLIGENCE_HOOKS Orchestration Prompt

**Target**: Claude Code Implementation  
**Duration**: 6 hours  
**Lead**: Intelligence Hook Architecture with Learning Integration  
**Phase Type**: Intelligent Hook System with Cross-Command Learning  

---

## 🎯 **PHASE OBJECTIVE**

Implement intelligent, modular analysis hooks that enable all 24 commands to share intelligence, learn from execution patterns, and continuously improve through feedback loops.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Build Upon Intelligence Foundation**
You MUST extend Phase EIP-001 with:
- Intelligent hooks for all 24 commands
- Learning mechanisms in each hook
- Cross-command data flow pipelines
- Pattern-based hook optimization
- Real-time metrics collection

### **LEARNING HOOK ARCHITECTURE**
- Hooks that adapt based on success rates
- Pattern-aware execution paths
- Cross-command intelligence consumption
- Continuous improvement mechanisms

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Intelligent Hook Registry** (`libs/governance/core/intelligent_hook_registry.py`)

```python
class IntelligentHookRegistry:
    def __init__(self, governance_system, database_manager, config_manager):
        self.governance = governance_system
        self.db = database_manager
        self.config = config_manager
        
        # Intelligence components
        self.learning_system = ContinuousLearningSystem()
        self.cross_intel = CrossCommandIntelligence()
        self.pattern_engine = PatternDetectionEngine()
        self.metrics_collector = MetricsCollector()
        
        # Hook registrations for all 24 commands
        self.command_hooks = self._register_all_command_hooks()
        
    def _register_all_command_hooks(self) -> dict:
        """Register hooks for all 24 commands"""
        return {
            # Analysis hooks
            'code-review': [CodeQualityHook(), ComplexityHook(), RefactoringHook()],
            'testing-review': [CoverageHook(), TestQualityHook(), FlakynessHook()],
            'security-review': [VulnerabilityHook(), ComplianceHook(), ThreatModelHook()],
            'documentation-review': [CompletenessHook(), ClarityHook(), MaintenanceHook()],
            'architecture-review': [PatternHook(), CouplingHook(), ScalabilityHook()],
            
            # Performance hooks
            'performance-review': [BottleneckHook(), OptimizationHook(), ResourceHook()],
            'dependency-analyze': [VersionHook(), VulnerabilityHook(), LicenseHook()],
            
            # Intelligence hooks
            'pattern-detect': [RecurrenceHook(), SystemicHook(), TrendHook()],
            'metrics-analyze': [TrendAnalysisHook(), AnomalyHook(), PredictionHook()],
            'feedback-analyze': [SuccessRateHook(), ImprovementHook(), LearningHook()],
            
            # ... hooks for all 24 commands
        }
    
    async def execute_intelligent_hooks(self, command: str, context: dict) -> HookResults:
        """
        Execute hooks with intelligence integration:
        - Load relevant cross-command intelligence
        - Apply learned optimizations
        - Collect metrics during execution
        - Update learning system with results
        """
        # Get hooks for command
        hooks = self.command_hooks[command]
        
        # Load intelligence context
        intel_context = await self._load_intelligence_context(command)
        context.update(intel_context)
        
        # Execute hooks with learning
        results = []
        for hook in hooks:
            # Apply learned optimizations
            optimized_hook = await self.learning_system.optimize_hook(hook, context)
            
            # Execute with metrics collection
            start_time = time.time()
            result = await optimized_hook.execute(context)
            execution_time = time.time() - start_time
            
            # Collect metrics
            await self.metrics_collector.collect_hook_metrics(
                command, hook.__class__.__name__, execution_time, result
            )
            
            # Update learning system
            await self.learning_system.update_from_execution(hook, result)
            
            results.append(result)
        
        # Share results with other commands
        await self.cross_intel.share_hook_results(command, results)
        
        return HookResults(command=command, results=results, metrics=await self.metrics_collector.get_summary())
```

### **2. Create Learning-Enabled Base Hook** (`libs/governance/hooks/intelligent_base_hook.py`)

```python
class IntelligentBaseHook(ABC):
    def __init__(self):
        self.execution_history = []
        self.success_rate = 1.0
        self.optimization_suggestions = []
        self.pattern_awareness = {}
    
    async def execute(self, context: dict) -> HookResult:
        """
        Execute hook with intelligence features:
        - Pattern-aware execution
        - Success tracking
        - Learning from failures
        """
        try:
            # Check for known patterns
            patterns = context.get('detected_patterns', [])
            if patterns:
                context = await self._apply_pattern_optimizations(context, patterns)
            
            # Execute core logic
            result = await self._execute_core(context)
            
            # Track success
            self._track_execution(True, result)
            
            # Learn from execution
            await self._learn_from_execution(result)
            
            return result
            
        except Exception as e:
            # Track failure
            self._track_execution(False, str(e))
            
            # Learn from failure
            await self._learn_from_failure(e, context)
            
            # Apply fallback strategy
            return await self._fallback_execution(context)
    
    @abstractmethod
    async def _execute_core(self, context: dict) -> HookResult:
        """Core hook logic - override in subclasses"""
        pass
    
    async def _apply_pattern_optimizations(self, context: dict, patterns: list) -> dict:
        """Apply optimizations based on detected patterns"""
        for pattern in patterns:
            if pattern['type'] in self.pattern_awareness:
                optimization = self.pattern_awareness[pattern['type']]
                context = await optimization(context)
        return context
    
    def _track_execution(self, success: bool, data: any):
        """Track execution for learning"""
        self.execution_history.append({
            'timestamp': datetime.now(),
            'success': success,
            'data': data
        })
        
        # Update success rate
        recent = self.execution_history[-100:]  # Last 100 executions
        successes = sum(1 for e in recent if e['success'])
        self.success_rate = successes / len(recent)
    
    async def _learn_from_execution(self, result: HookResult):
        """Learn from successful execution"""
        # Identify what worked well
        if result.performance_gain > 0:
            self.optimization_suggestions.append({
                'type': 'performance',
                'suggestion': result.optimization_used,
                'gain': result.performance_gain
            })
    
    async def _learn_from_failure(self, error: Exception, context: dict):
        """Learn from failed execution"""
        # Identify failure pattern
        failure_pattern = self._identify_failure_pattern(error)
        
        # Add to pattern awareness
        if failure_pattern not in self.pattern_awareness:
            self.pattern_awareness[failure_pattern] = self._create_mitigation_strategy(failure_pattern)
```

### **3. Create Cross-Command Learning Pipeline** (`libs/governance/core/learning_pipeline.py`)

```python
class CrossCommandLearningPipeline:
    def __init__(self, database_manager, cache_manager):
        self.db = database_manager
        self.cache = cache_manager
        self.learning_queue = asyncio.Queue()
        self.learning_models = {}
    
    async def process_learning_events(self):
        """
        Continuous learning pipeline:
        - Process execution results from all commands
        - Update learning models
        - Share learnings across commands
        - Improve hook effectiveness
        """
        while True:
            event = await self.learning_queue.get()
            
            # Extract learning data
            command = event['command']
            hook_name = event['hook']
            result = event['result']
            
            # Update command-specific model
            model = self._get_or_create_model(command)
            await model.update(hook_name, result)
            
            # Identify cross-command learnings
            cross_learnings = await self._extract_cross_learnings(event)
            
            # Share with related commands
            for target_command, learning in cross_learnings.items():
                await self._share_learning(target_command, learning)
            
            # Update global effectiveness metrics
            await self._update_global_metrics(event)
    
    async def _extract_cross_learnings(self, event: dict) -> dict:
        """Extract learnings applicable to other commands"""
        learnings = {}
        
        # Pattern-based learnings
        if 'pattern' in event['result']:
            pattern = event['result']['pattern']
            # All commands can benefit from pattern knowledge
            for cmd in self._get_related_commands(event['command']):
                learnings[cmd] = {'pattern': pattern, 'mitigation': event['result'].get('mitigation')}
        
        # Performance optimizations
        if 'optimization' in event['result']:
            optimization = event['result']['optimization']
            # Share with performance-sensitive commands
            for cmd in ['performance-review', 'prompt-optimize', 'metrics-analyze']:
                learnings[cmd] = {'optimization': optimization}
        
        return learnings
```

### **4. Create Metrics Collection System** (`libs/governance/core/metrics_collector.py`)

```python
class MetricsCollector:
    def __init__(self, database_manager):
        self.db = database_manager
        self.metrics_buffer = []
        self.aggregations = {}
    
    async def collect_hook_metrics(self, command: str, hook: str, execution_time: float, result: any):
        """Collect detailed metrics from hook execution"""
        metrics = {
            'command': command,
            'hook': hook,
            'execution_time': execution_time,
            'timestamp': datetime.now(),
            'success': result.success if hasattr(result, 'success') else True,
            'findings_count': len(result.findings) if hasattr(result, 'findings') else 0,
            'severity_average': self._calculate_severity_average(result),
            'roi_average': self._calculate_roi_average(result),
            'patterns_detected': len(result.patterns) if hasattr(result, 'patterns') else 0
        }
        
        # Buffer for batch insertion
        self.metrics_buffer.append(metrics)
        
        # Flush if buffer is full
        if len(self.metrics_buffer) >= 100:
            await self._flush_metrics()
        
        # Update real-time aggregations
        await self._update_aggregations(metrics)
    
    async def get_command_effectiveness(self, command: str) -> dict:
        """Get effectiveness metrics for a command"""
        return {
            'success_rate': self.aggregations.get(f'{command}:success_rate', 0),
            'average_execution_time': self.aggregations.get(f'{command}:avg_time', 0),
            'findings_per_execution': self.aggregations.get(f'{command}:avg_findings', 0),
            'pattern_detection_rate': self.aggregations.get(f'{command}:pattern_rate', 0)
        }
```

### **5. Create Pattern-Aware Hooks** (`libs/governance/hooks/pattern_aware_hooks.py`)

```python
class PatternAwareHook(IntelligentBaseHook):
    def __init__(self):
        super().__init__()
        self.known_patterns = {}
        self.pattern_mitigations = {}
    
    async def _execute_core(self, context: dict) -> HookResult:
        """Execute with pattern awareness"""
        # Check for known patterns
        detected_patterns = await self._detect_known_patterns(context)
        
        if detected_patterns:
            # Apply pattern-specific analysis
            results = await self._analyze_with_patterns(context, detected_patterns)
            
            # Suggest systemic fixes
            systemic_fixes = await self._generate_systemic_fixes(detected_patterns)
            results['systemic_fixes'] = systemic_fixes
        else:
            # Standard analysis
            results = await self._standard_analysis(context)
        
        # Check if new patterns emerging
        potential_patterns = await self._identify_potential_patterns(results)
        if potential_patterns:
            await self._register_new_patterns(potential_patterns)
        
        return HookResult(
            findings=results.get('findings', []),
            patterns=detected_patterns,
            systemic_fixes=results.get('systemic_fixes', []),
            metadata={'pattern_aware': True}
        )
    
    async def _detect_known_patterns(self, context: dict) -> list:
        """Detect known patterns in the context"""
        patterns = []
        
        for pattern_id, pattern_def in self.known_patterns.items():
            if await self._matches_pattern(context, pattern_def):
                patterns.append({
                    'id': pattern_id,
                    'type': pattern_def['type'],
                    'confidence': await self._calculate_confidence(context, pattern_def),
                    'mitigation': self.pattern_mitigations.get(pattern_id)
                })
        
        return patterns
```

---

## 🗄️ **DATABASE SCHEMA EXTENSIONS**

```sql
-- Learning and metrics tables
CREATE TABLE IF NOT EXISTS hook_execution_metrics (
    id SERIAL PRIMARY KEY,
    command VARCHAR(50) NOT NULL,
    hook_name VARCHAR(100) NOT NULL,
    execution_time_ms INTEGER,
    success BOOLEAN,
    findings_count INTEGER,
    severity_average DECIMAL(5,2),
    roi_average DECIMAL(5,2),
    patterns_detected INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_events (
    id SERIAL PRIMARY KEY,
    command VARCHAR(50) NOT NULL,
    hook_name VARCHAR(100),
    event_type VARCHAR(50), -- 'success', 'failure', 'pattern', 'optimization'
    event_data JSONB,
    learning_applied BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hook_effectiveness (
    command VARCHAR(50),
    hook_name VARCHAR(100),
    success_rate DECIMAL(3,2),
    avg_execution_time_ms INTEGER,
    total_executions INTEGER,
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (command, hook_name)
);

CREATE TABLE IF NOT EXISTS cross_command_learnings (
    id SERIAL PRIMARY KEY,
    source_command VARCHAR(50) NOT NULL,
    target_command VARCHAR(50) NOT NULL,
    learning_type VARCHAR(50),
    learning_data JSONB,
    effectiveness_score DECIMAL(3,2),
    applied_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_hook_metrics_command ON hook_execution_metrics(command);
CREATE INDEX idx_hook_metrics_timestamp ON hook_execution_metrics(timestamp);
CREATE INDEX idx_learning_events_command ON learning_events(command);
CREATE INDEX idx_cross_learnings_target ON cross_command_learnings(target_command);
```

---

## 🔗 **INTELLIGENCE INTEGRATION POINTS**

### **Cross-Command Data Flow**
```python
COMMAND_DATA_FLOW = {
    'code-review': {
        'consumes_from': ['architecture-review', 'performance-review'],
        'provides_to': ['testing-review', 'documentation-review'],
        'learning_share': ['bug-fix', 'prompt-optimize']
    },
    'pattern-detect': {
        'consumes_from': ['all_commands'],  # Special case - consumes from all
        'provides_to': ['all_commands'],     # Provides patterns to all
        'learning_share': ['all_commands']
    },
    'metrics-analyze': {
        'consumes_from': ['all_commands'],
        'provides_to': ['progress-dashboard', 'feedback-analyze'],
        'learning_share': ['prompt-optimize', 'batch-review']
    }
    # ... define for all 24 commands
}
```

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Hook Execution Performance**
- [ ] Individual hook execution: <500ms
- [ ] Command total hook time: <5 seconds
- [ ] Learning updates: <100ms
- [ ] Cross-command data retrieval: <50ms

### **Learning System Performance**
- [ ] Pattern matching: <200ms
- [ ] Learning model updates: <500ms
- [ ] Cross-command sharing: <100ms
- [ ] Metrics aggregation: <1 second

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Learning System Governance**
- [ ] Learning bounded to prevent drift
- [ ] Pattern detection validated against rules
- [ ] Cross-command sharing follows security policies
- [ ] Metrics collection respects privacy

---

## 📊 **SUCCESS CRITERIA**

### **Hook System Requirements**
- [ ] All 24 commands have intelligent hooks
- [ ] Hooks share data across commands
- [ ] Learning system improving effectiveness
- [ ] Pattern detection integrated in hooks

### **Intelligence Requirements**
- [ ] Hook success rate >85%
- [ ] Cross-command data available <100ms
- [ ] Learning improvements measurable
- [ ] Pattern detection accuracy >80%

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Intelligent Hook Infrastructure** (2 hours)
1. Implement `IntelligentHookRegistry`
2. Create `IntelligentBaseHook`
3. Build hook implementations for all commands
4. Test hook execution

### **Step 2: Learning System** (2 hours)
1. Implement `CrossCommandLearningPipeline`
2. Create learning models
3. Build learning event processing
4. Test learning updates

### **Step 3: Metrics and Pattern Integration** (1.5 hours)
1. Implement `MetricsCollector`
2. Create pattern-aware hooks
3. Test pattern detection in hooks
4. Validate metrics collection

### **Step 4: Integration Testing** (30 minutes)
1. Test cross-command data flow
2. Validate learning improvements
3. Verify performance requirements
4. Test complete hook system

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/intelligent_hook_registry.py` - Hook registry with learning
- [ ] `libs/governance/hooks/intelligent_base_hook.py` - Learning-enabled base hook
- [ ] `libs/governance/core/learning_pipeline.py` - Cross-command learning
- [ ] `libs/governance/core/metrics_collector.py` - Metrics collection system
- [ ] `libs/governance/hooks/pattern_aware_hooks.py` - Pattern-aware hooks
- [ ] Hook implementations for all 24 commands
- [ ] Database schema extensions

### **Documentation Updates**
- [ ] Update `TRACKER.md` with EIP-002 completion
- [ ] Update `STATUS.md` with hook intelligence capabilities
- [ ] Document learning system architecture
- [ ] Create hook development guide

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **INTELLIGENT HOOKS**: Every hook learns and improves
2. **CROSS-COMMAND FLOW**: Data flows between all related commands
3. **PATTERN INTEGRATION**: Hooks detect and respond to patterns
4. **CONTINUOUS LEARNING**: System gets smarter with each execution
5. **METRICS DRIVEN**: Every execution tracked and analyzed

---

**Remember**: This phase creates intelligent hooks that not only execute analysis but learn from every execution, share intelligence across commands, and continuously improve the platform's effectiveness.