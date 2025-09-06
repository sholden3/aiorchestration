# Phase EIP-003: INTELLIGENT_PROMPT_ENGINE Orchestration Prompt

**Target**: GitHub Copilot Implementation with Intelligence Integration  
**Duration**: 6 hours  
**Lead**: Intelligent Prompt Generation with Learning Optimization  
**Phase Type**: AI-Powered Prompt Generation with Continuous Improvement  

---

## 🎯 **PHASE OBJECTIVE**

Generate intelligent, context-aware GitHub Copilot prompts for all 24 commands with embedded intelligence data, success predictions, and continuous learning from implementation feedback.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Leverage Full Intelligence Stack**
You MUST integrate:
- Severity scores and ROI calculations in every prompt
- Pattern detection results and systemic fix recommendations
- Cross-command intelligence context
- Success rate predictions based on historical data
- Learning system feedback loops

### **INTELLIGENT PROMPT FEATURES**
- Dynamic persona selection based on effectiveness
- Pattern-aware implementation guidance
- Success probability scoring
- Automated prompt optimization
- Feedback collection mechanisms

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Intelligent Prompt Generator** (`libs/governance/core/intelligent_prompt_generator.py`)

```python
class IntelligentPromptGenerator:
    def __init__(self, database_manager, persona_manager, governance_system):
        self.db = database_manager
        self.personas = persona_manager
        self.governance = governance_system
        
        # Intelligence components
        self.learning_system = PromptLearningSystem()
        self.success_predictor = SuccessPredictor()
        self.pattern_integrator = PatternIntegrator()
        self.optimization_engine = PromptOptimizationEngine()
        
        # Command-specific generators
        self.command_generators = self._initialize_command_generators()
    
    def _initialize_command_generators(self) -> dict:
        """Initialize generators for all 24 commands"""
        return {
            'code-review': CodeReviewPromptGenerator(),
            'testing-review': TestingPromptGenerator(),
            'security-review': SecurityPromptGenerator(),
            'documentation-review': DocumentationPromptGenerator(),
            'architecture-review': ArchitecturePromptGenerator(),
            'performance-review': PerformancePromptGenerator(),
            'dependency-analyze': DependencyPromptGenerator(),
            'metrics-analyze': MetricsPromptGenerator(),
            'architecture': ArchitecturePlanPromptGenerator(),
            'migration-plan': MigrationPromptGenerator(),
            'impact-check': ImpactPromptGenerator(),
            'phase-review': PhaseReviewPromptGenerator(),
            'knowledge-map': KnowledgeMapPromptGenerator(),
            'pattern-detect': PatternDetectPromptGenerator(),
            'feedback-analyze': FeedbackPromptGenerator(),
            'prompt-optimize': PromptOptimizePromptGenerator(),
            'batch-review': BatchReviewPromptGenerator(),
            'progress-dashboard': DashboardPromptGenerator(),
            'bug-fix': BugFixPromptGenerator(),
            'copilot': DirectPromptGenerator(),
            'research': ResearchPromptGenerator(),
            'help': HelpPromptGenerator()
        }
    
    async def generate_intelligent_prompt(self, command: str, finding: dict) -> IntelligentPrompt:
        """
        Generate prompt with full intelligence integration:
        - Include severity and ROI scores
        - Add pattern context if applicable
        - Predict success probability
        - Optimize based on historical data
        - Include learning checkpoints
        """
        # Get command-specific generator
        generator = self.command_generators[command]
        
        # Select optimal personas based on effectiveness
        personas = await self._select_optimal_personas(command, finding)
        
        # Load cross-command intelligence
        cross_intel = await self._load_cross_intelligence(command, finding)
        
        # Check for pattern context
        pattern_context = await self.pattern_integrator.get_pattern_context(finding)
        
        # Predict success probability
        success_probability = await self.success_predictor.predict(command, finding, personas)
        
        # Generate base prompt
        base_prompt = await generator.generate(finding, personas, cross_intel)
        
        # Optimize based on learning
        optimized_prompt = await self.optimization_engine.optimize(base_prompt, success_probability)
        
        # Add intelligence metadata
        intelligent_prompt = await self._enhance_with_intelligence(
            optimized_prompt,
            finding,
            pattern_context,
            success_probability
        )
        
        # Store for tracking
        await self._store_prompt(intelligent_prompt)
        
        return intelligent_prompt
    
    async def _enhance_with_intelligence(self, prompt: str, finding: dict, 
                                        pattern: dict, success_prob: float) -> str:
        """Enhance prompt with intelligence data"""
        return f"""
{prompt}

## 📊 INTELLIGENCE CONTEXT

### Severity & Priority
- **Severity Score**: {finding['severity_score']}/100 ({finding['severity_level']})
- **ROI Score**: {finding['roi_score']} ({finding['priority']})
- **Success Probability**: {success_prob:.1%}

### Pattern Analysis
{self._format_pattern_context(pattern)}

### Cross-Command Intelligence
{await self._format_cross_intelligence(finding)}

### Historical Context
- Similar issues resolved: {await self._get_similar_resolved_count(finding)}
- Average resolution time: {await self._get_avg_resolution_time(finding)}
- Common pitfalls: {await self._get_common_pitfalls(finding)}

### Learning Checkpoints
□ Implementation started (auto-tracked)
□ Tests passing (validate before proceeding)
□ Performance benchmarks met (measure impact)
□ Documentation updated (maintain completeness)
□ Feedback collected (helps improve future prompts)

### Systemic Considerations
{await self._format_systemic_recommendations(pattern)}

### Success Metrics
- Expected outcome: {finding.get('expected_outcome', 'Issue resolved')}
- Performance target: {finding.get('performance_target', 'No degradation')}
- Quality gates: {finding.get('quality_gates', 'All tests passing')}
"""
```

### **2. Create Success Prediction System** (`libs/governance/core/success_predictor.py`)

```python
class SuccessPredictor:
    def __init__(self, database_manager):
        self.db = database_manager
        self.prediction_models = {}
        self.feature_extractors = {}
    
    async def predict(self, command: str, finding: dict, personas: list) -> float:
        """
        Predict success probability based on:
        - Historical success rates for similar issues
        - Persona effectiveness for this type
        - Pattern complexity
        - Current codebase state
        """
        # Extract features
        features = await self._extract_features(command, finding, personas)
        
        # Get or create prediction model
        model = await self._get_prediction_model(command)
        
        # Calculate base probability
        base_prob = await model.predict(features)
        
        # Adjust for contextual factors
        adjusted_prob = await self._apply_contextual_adjustments(
            base_prob, finding, personas
        )
        
        return min(1.0, max(0.0, adjusted_prob))
    
    async def _extract_features(self, command: str, finding: dict, personas: list) -> dict:
        """Extract features for prediction"""
        return {
            'severity_score': finding['severity_score'],
            'roi_score': finding['roi_score'],
            'pattern_match': finding.get('pattern_id') is not None,
            'personas_effectiveness': await self._get_personas_effectiveness(personas, command),
            'complexity_score': await self._calculate_complexity(finding),
            'historical_success': await self._get_historical_success_rate(command, finding['finding_type']),
            'codebase_health': await self._get_codebase_health_score()
        }
    
    async def update_model(self, command: str, prompt_id: str, actual_success: bool):
        """Update prediction model with actual outcome"""
        model = await self._get_prediction_model(command)
        
        # Get original prediction
        original = await self._get_original_prediction(prompt_id)
        
        # Calculate error
        error = abs(original - (1.0 if actual_success else 0.0))
        
        # Update model
        await model.update(prompt_id, actual_success, error)
        
        # Store learning event
        await self._store_learning_event(command, prompt_id, original, actual_success)
```

### **3. Create Prompt Optimization Engine** (`libs/governance/core/prompt_optimization_engine.py`)

```python
class PromptOptimizationEngine:
    def __init__(self, database_manager):
        self.db = database_manager
        self.optimization_rules = {}
        self.success_patterns = {}
    
    async def optimize(self, base_prompt: str, success_probability: float) -> str:
        """
        Optimize prompt based on:
        - Historical success patterns
        - Common failure points
        - Effective prompt structures
        - Clarity improvements
        """
        optimized = base_prompt
        
        # Apply structural optimizations
        optimized = await self._optimize_structure(optimized)
        
        # Add reinforcement for low success probability
        if success_probability < 0.7:
            optimized = await self._add_reinforcement(optimized, success_probability)
        
        # Apply learned improvements
        optimized = await self._apply_learned_improvements(optimized)
        
        # Enhance clarity
        optimized = await self._enhance_clarity(optimized)
        
        return optimized
    
    async def _optimize_structure(self, prompt: str) -> str:
        """Optimize prompt structure for better success"""
        # Add clear sections if missing
        sections = ['TASK', 'REQUIREMENTS', 'CONSTRAINTS', 'VALIDATION']
        for section in sections:
            if section not in prompt:
                prompt = await self._add_section(prompt, section)
        
        # Ensure numbered steps
        prompt = await self._ensure_numbered_steps(prompt)
        
        # Add success criteria if missing
        if 'SUCCESS CRITERIA' not in prompt:
            prompt = await self._add_success_criteria(prompt)
        
        return prompt
    
    async def _add_reinforcement(self, prompt: str, success_prob: float) -> str:
        """Add reinforcement for challenging tasks"""
        reinforcement = f"""
## ⚠️ COMPLEXITY NOTICE
This task has a predicted success rate of {success_prob:.1%}. Extra attention required:

### Common Challenges
{await self._get_common_challenges(prompt)}

### Recommended Approach
1. Start with the simplest implementation
2. Test each component independently
3. Integrate incrementally with validation
4. Use defensive programming techniques

### Validation Checkpoints
{await self._get_validation_checkpoints(prompt)}
"""
        return prompt + reinforcement
```

### **4. Create Pattern-Integrated Prompt Templates** (`prompts/intelligence_templates/`)

#### **Pattern-Aware Prompt Template** (`prompts/intelligence_templates/pattern_aware_template.md`)

```markdown
You are {{persona_combination}} working collaboratively to resolve a {{pattern_type}} pattern.

## 🎯 PATTERN CONTEXT

### Pattern Identification
- **Pattern ID**: {{pattern_id}}
- **Type**: {{pattern_type}}
- **Occurrences**: {{occurrences}} instances found
- **Affected Files**: {{affected_files_count}} files
- **Severity Average**: {{severity_avg}}/100

### Systemic Issue
{{systemic_description}}

## 📊 INTELLIGENCE DATA

### Severity & ROI
- **Severity Score**: {{severity_score}}/100 ({{severity_level}})
- **ROI Score**: {{roi_score}} ({{priority}})
- **Success Probability**: {{success_probability}}%

### Historical Context
- **Similar Patterns Resolved**: {{similar_resolved}}
- **Average Resolution Time**: {{avg_resolution_time}}
- **Success Rate**: {{historical_success_rate}}%

## 🎯 TASK

Implement a SYSTEMIC fix that addresses all {{occurrences}} instances of this pattern:

{{task_description}}

## ✅ REQUIREMENTS

1. **Systemic Solution**: Fix must address ALL occurrences, not individual instances
2. **Pattern Prevention**: Implementation should prevent future occurrences
3. **Backward Compatibility**: Maintain all existing functionality
4. **Test Coverage**: Add tests that detect this pattern
5. **Documentation**: Document the pattern and its solution

## 🔧 IMPLEMENTATION STRATEGY

### Phase 1: Pattern Analysis
1. Review all {{occurrences}} occurrences
2. Identify root cause
3. Design systemic solution

### Phase 2: Implementation
1. Create shared solution component
2. Refactor all occurrences to use solution
3. Add pattern detection tests

### Phase 3: Validation
1. Verify all occurrences resolved
2. Run pattern detection to confirm
3. Performance benchmark

## 🚫 CONSTRAINTS

- {{constraint_1}}
- {{constraint_2}}
- {{constraint_3}}

## 📈 SUCCESS METRICS

- Pattern occurrences reduced to 0
- No performance degradation
- All tests passing
- Pattern detection test prevents regression

## 🔄 LEARNING FEEDBACK

Please provide feedback after implementation:
- Was the pattern correctly identified? [Y/N]
- Did the systemic fix work? [Y/N]
- Time to implement: [hours]
- Challenges encountered: [text]
- Suggestions for improvement: [text]

This feedback improves future pattern detection and resolution.
```

### **5. Create Feedback Collection System** (`libs/governance/core/feedback_collector.py`)

```python
class FeedbackCollector:
    def __init__(self, database_manager, learning_system):
        self.db = database_manager
        self.learning = learning_system
        self.feedback_queue = asyncio.Queue()
    
    async def collect_prompt_feedback(self, prompt_id: str, feedback: dict):
        """
        Collect feedback on prompt execution:
        - Success/failure
        - Time to implement
        - Challenges faced
        - Improvements suggested
        """
        # Validate feedback
        validated = await self._validate_feedback(feedback)
        
        # Store in database
        await self._store_feedback(prompt_id, validated)
        
        # Queue for learning processing
        await self.feedback_queue.put({
            'prompt_id': prompt_id,
            'feedback': validated,
            'timestamp': datetime.now()
        })
        
        # Update success predictor
        await self._update_success_predictor(prompt_id, validated)
        
        # Update prompt optimization engine
        await self._update_optimization_engine(prompt_id, validated)
        
        # Share learnings with related commands
        await self._share_feedback_learnings(prompt_id, validated)
    
    async def process_feedback_queue(self):
        """Process feedback for continuous learning"""
        while True:
            item = await self.feedback_queue.get()
            
            # Extract learnings
            learnings = await self._extract_learnings(item)
            
            # Update learning models
            await self.learning.update_from_feedback(learnings)
            
            # Identify patterns in feedback
            patterns = await self._identify_feedback_patterns(item)
            
            # Update prompt templates if needed
            if patterns:
                await self._update_prompt_templates(patterns)
```

### **6. Create Persona Effectiveness Tracker** (`libs/governance/core/persona_effectiveness.py`)

```python
class PersonaEffectivenessTracker:
    def __init__(self, database_manager):
        self.db = database_manager
        self.effectiveness_scores = {}
        self.combination_synergies = {}
    
    async def track_persona_performance(self, command: str, personas: list, 
                                       prompt_id: str, success: bool):
        """Track how well personas perform for different commands"""
        # Update individual persona scores
        for persona in personas:
            key = f"{command}:{persona}"
            if key not in self.effectiveness_scores:
                self.effectiveness_scores[key] = {'success': 0, 'total': 0}
            
            self.effectiveness_scores[key]['total'] += 1
            if success:
                self.effectiveness_scores[key]['success'] += 1
        
        # Track combination synergies
        combo_key = f"{command}:{'-'.join(sorted(personas))}"
        if combo_key not in self.combination_synergies:
            self.combination_synergies[combo_key] = {'success': 0, 'total': 0}
        
        self.combination_synergies[combo_key]['total'] += 1
        if success:
            self.combination_synergies[combo_key]['success'] += 1
        
        # Store in database
        await self._store_effectiveness_data(command, personas, prompt_id, success)
    
    async def get_optimal_personas(self, command: str, context: dict) -> list:
        """Get optimal persona combination for command and context"""
        # Get base effectiveness scores
        scores = {}
        for persona in PERSONA_TEMPLATES.keys():
            key = f"{command}:{persona}"
            if key in self.effectiveness_scores:
                total = self.effectiveness_scores[key]['total']
                if total > 0:
                    scores[persona] = self.effectiveness_scores[key]['success'] / total
                else:
                    scores[persona] = 0.5  # Default score
            else:
                scores[persona] = 0.5
        
        # Adjust for context (patterns, severity, etc.)
        adjusted_scores = await self._adjust_for_context(scores, context)
        
        # Select top 3 personas
        sorted_personas = sorted(adjusted_scores.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_personas[:3]]
```

---

## 🗄️ **DATABASE SCHEMA EXTENSIONS**

```sql
-- Intelligent prompt tables
CREATE TABLE IF NOT EXISTS intelligent_prompts (
    id SERIAL PRIMARY KEY,
    prompt_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(100),
    command VARCHAR(50) NOT NULL,
    finding_id INTEGER,
    personas TEXT[],
    severity_score INTEGER,
    roi_score DECIMAL(5,2),
    success_probability DECIMAL(3,2),
    pattern_id VARCHAR(100),
    prompt_text TEXT,
    optimization_applied BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_feedback (
    id SERIAL PRIMARY KEY,
    prompt_id VARCHAR(100) REFERENCES intelligent_prompts(prompt_id),
    success BOOLEAN,
    implementation_time_hours DECIMAL(5,2),
    challenges TEXT,
    improvements_suggested TEXT,
    pattern_correctly_identified BOOLEAN,
    systemic_fix_worked BOOLEAN,
    feedback_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prompt_effectiveness (
    prompt_id VARCHAR(100) PRIMARY KEY,
    predicted_success DECIMAL(3,2),
    actual_success BOOLEAN,
    prediction_error DECIMAL(3,2),
    personas_used TEXT[],
    pattern_involved BOOLEAN,
    execution_time_hours DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS persona_effectiveness (
    command VARCHAR(50),
    persona VARCHAR(50),
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(3,2),
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (command, persona)
);

CREATE TABLE IF NOT EXISTS persona_combinations (
    command VARCHAR(50),
    combination TEXT,
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    synergy_score DECIMAL(3,2),
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (command, combination)
);

-- Indexes
CREATE INDEX idx_intelligent_prompts_command ON intelligent_prompts(command);
CREATE INDEX idx_intelligent_prompts_success_prob ON intelligent_prompts(success_probability);
CREATE INDEX idx_prompt_feedback_success ON prompt_feedback(success);
CREATE INDEX idx_persona_effectiveness_score ON persona_effectiveness(effectiveness_score);
```

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Prompt Generation Performance**
- [ ] Single prompt generation: <2 seconds
- [ ] Batch prompt generation: <30 seconds for 50 prompts
- [ ] Success prediction: <200ms
- [ ] Optimization: <500ms per prompt

### **Learning System Performance**
- [ ] Feedback processing: <1 second
- [ ] Model updates: <2 seconds
- [ ] Persona optimization: <500ms
- [ ] Pattern integration: <300ms

---

## 📊 **SUCCESS CRITERIA**

### **Prompt Quality Requirements**
- [ ] All prompts include intelligence context
- [ ] Success prediction accuracy >75%
- [ ] Pattern integration for applicable issues
- [ ] Feedback collection mechanism in every prompt

### **Learning Requirements**
- [ ] Prompt effectiveness improves over time
- [ ] Persona selection optimizes based on performance
- [ ] Pattern solutions become more effective
- [ ] Success predictions become more accurate

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Core Prompt Generation** (2 hours)
1. Implement `IntelligentPromptGenerator`
2. Create command-specific generators
3. Build prompt templates
4. Test generation for all commands

### **Step 2: Intelligence Integration** (2 hours)
1. Implement `SuccessPredictor`
2. Create `PromptOptimizationEngine`
3. Build pattern integration
4. Test intelligence enhancement

### **Step 3: Learning Systems** (1.5 hours)
1. Implement `FeedbackCollector`
2. Create `PersonaEffectivenessTracker`
3. Build learning pipelines
4. Test feedback processing

### **Step 4: Validation** (30 minutes)
1. Test all 24 command generators
2. Validate intelligence integration
3. Verify learning systems
4. Performance testing

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] Intelligent prompt generator for all 24 commands
- [ ] Success prediction system
- [ ] Prompt optimization engine
- [ ] Feedback collection system
- [ ] Persona effectiveness tracking
- [ ] Pattern-integrated templates
- [ ] Database schema extensions

### **Documentation Updates**
- [ ] Update `TRACKER.md` with EIP-003 completion
- [ ] Document prompt intelligence features
- [ ] Create feedback guide
- [ ] Update learning system documentation

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **INTELLIGENCE IN EVERY PROMPT**: All prompts include severity, ROI, and patterns
2. **CONTINUOUS LEARNING**: Every execution improves future prompts
3. **SUCCESS PREDICTION**: Accurate probability helps set expectations
4. **FEEDBACK LOOPS**: Systematic collection and processing of feedback
5. **PERSONA OPTIMIZATION**: Dynamic selection based on effectiveness

---

**Remember**: This phase creates prompts that are not just instructions but intelligent, context-aware guidance that learns and improves with every execution.