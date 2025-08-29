# 🔄 DEVELOPMENT GOVERNANCE PROTOCOL

## Mandatory Session Management
Every development session MUST follow this protocol:

### Decision Approval Protocol (CRITICAL)
**⚠️ NEVER proceed with architectural decisions without explicit approval:**
1. Present the decision with all persona perspectives
2. Wait for user to read and respond
3. Only proceed after receiving explicit approval
4. Document the approval in decision logs

**Examples requiring approval:**
- Changing testing strategies
- Simplifying complex processes
- Modifying architectural patterns
- Altering established workflows
- Deviating from documented standards

### Session Start (REQUIRED)
```bash
# Before any development work
echo "=== SESSION INITIALIZATION ==="
./validate-session-start.sh
echo "Core Architects: Alex Novak & Dr. Sarah Chen active"
echo "Specialist Pool: Available per PERSONAS.md"
echo "Decision Log: DECISIONS.md ready for updates"
echo "Ready for orchestrated development"
```

### Session End (REQUIRED)  
```bash
# Before committing any changes
echo "=== SESSION VALIDATION ==="
./validate-task-completion.sh
echo "Both architects must approve before commit"
```

### Task Completion Verification
Every task requires both architects' explicit sign-off:
- **Sarah**: "Does this pass the Three Questions framework?" (What breaks first? How do we know? What's Plan B?)
- **Alex**: "Does this pass the 3 AM Test?" (Debuggable under pressure? Integration points documented? Cleanup verified?)

## Standardized Prompt Protocols
Use these templates for all development requests:

### Task Request Template
```
[ORCHESTRATED TASK REQUEST]
Architects: Request both Alex Novak and Dr. Sarah Chen
Task: [specific description]
Requirements:
- Sarah: Analyze failure modes and backend implications  
- Alex: Evaluate frontend integration and process coordination
- Both: Cross-validate assumptions and provide verification
Success Criteria: [specific, measurable outcomes]
```

### Emergency Fix Template
```
[EMERGENCY FIX REQUEST]
CRITICAL ISSUE DETECTED
Severity: [CRITICAL/HIGH/MEDIUM]
Immediate Actions Needed:
- Sarah: Identify blast radius and containment
- Alex: Determine process coordination impact  
- Both: Provide emergency mitigation steps
```

## Mandatory Archival Rules (ENFORCED)
Every file replacement MUST follow these archival procedures:

### Pre-Archival Requirements
1. **Approval**: Both Alex and Sarah must approve before archiving
2. **Documentation**: Create README.md in archive directory explaining:
   - Why the file is being replaced
   - Performance comparison (old vs new)
   - Rollback procedure
   - Dependencies affected

### Archive Structure
```
archive/
├── test_infrastructure/     # Test-related files
├── backend_components/      # Backend service files
├── frontend_components/     # Frontend/Angular files
└── configuration/          # Config files
```

### Naming Convention
```
YYYY-MM-DD_original-filename_v{version}_{reason}.ext
Example: 2025-08-26_test-setup-electron_v1_baseline.ts
```

### Rollback Procedure
1. Locate archived file in appropriate directory
2. Copy back to original location
3. Run validation tests
4. Document rollback reason

**Enforcement**: No file replacements without archival. Violations require architecture review.

## 🚀 ORCHESTRATED DEVELOPMENT WORKFLOW

### Pre-Development Validation (Both Architects)
```bash
# Sarah's Backend Validation
cd ai-assistant/backend
python -m pytest -v                    # Verify tests pass
python -c "import main; print('OK')"   # Check imports work

# Alex's Frontend Validation  
cd ai-assistant
npm run build                          # Verify Angular compiles
npm run electron:dev                   # Check Electron launches
```

### Cross-Validation Requirements
Every change must pass both architects' validation:

**Sarah's Checklist**:
- [ ] What breaks first? (Failure mode analysis)
- [ ] How do we know? (Monitoring and observability)
- [ ] What's Plan B? (Fallback and recovery)
- [ ] Circuit breakers implemented where needed
- [ ] Resource limits enforced

**Alex's Checklist**:
- [ ] Passes 3 AM test (debuggable under pressure)
- [ ] IPC error boundaries in place
- [ ] Memory cleanup verified  
- [ ] Process coordination tested
- [ ] Angular change detection optimized

### Implementation Standards
```typescript
// Alex's Defensive Pattern Template
class DefensiveService {
  async safeOperation<T>(operation: () => Promise<T>): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      this.logError(error);
      throw new ApplicationError('Operation failed', { originalError: error });
    }
  }
}

// Sarah's Circuit Breaker Pattern Template  
class CircuitBreaker {
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.isOpen()) {
      throw new CircuitBreakerOpenError('Service unavailable');
    }
    
    try {
      const result = await operation();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }
}
```

## Comprehensive Governance Framework
For complete governance procedures, see: `docs/processes/governance-framework.md`

**Key Framework Components:**
- **Session Management**: Mandatory start/end validation protocols
- **Quality Gates**: Automated testing and validation requirements  
- **Documentation Standards**: Currency requirements and templates
- **Emergency Procedures**: Critical issue response protocols
- **Process Enforcement**: Git hooks and automated validation

**Implementation Commands:**
```bash
# Install governance framework
curl -O docs/processes/governance-framework.md
chmod +x validate-*.sh

# Daily workflow integration
alias start-work='./validate-session-start.sh'
alias finish-work='./validate-task-completion.sh'  
alias check-ready='./validate-project-structure.sh'
```

**Enforcement Level**: MANDATORY - No exceptions for production commits