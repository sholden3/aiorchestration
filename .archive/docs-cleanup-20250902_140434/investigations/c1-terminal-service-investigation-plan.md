# C1 Terminal Service Architecture Investigation Plan

**Date**: 2025-01-27  
**Severity**: CRITICAL BLOCKER  
**Lead Investigators**: Alex Novak v3.0 & Dr. Sarah Chen v1.2  
**Status**: MUST COMPLETE BEFORE ANY FURTHER WORK

---

## 🔴 CRITICAL ISSUE STATEMENT

**Discovery**: Test reveals TerminalService might still be singleton despite C1 "fix"  
**Impact**: If true, memory leak is NOT fixed - all our testing is invalid  
**Risk**: Proceeding without resolution could cascade failures through entire system

---

## 📋 COMPREHENSIVE INVESTIGATION PLAN

### Phase 1: Component Usage Analysis (IMMEDIATE)

#### 1.1 Find All Components Using TerminalService
```bash
# Search for components that import TerminalService
grep -r "TerminalService" --include="*.component.ts" ai-assistant/src/

# Search for components that inject TerminalService in constructor
grep -r "private.*[Tt]erminal.*Service\|public.*[Tt]erminal.*Service" --include="*.ts" ai-assistant/src/

# Search for providers arrays mentioning TerminalService
grep -r "providers.*TerminalService" --include="*.ts" ai-assistant/src/
```

#### 1.2 Check Module Declarations
```bash
# Search modules for TerminalService in providers
grep -r "TerminalService" --include="*.module.ts" ai-assistant/src/

# Check if service is provided at module level
grep -r "providers.*\[.*TerminalService.*\]" --include="*.module.ts" ai-assistant/src/
```

#### 1.3 Document Each Usage Pattern
For each component found, document:
- Component name and path
- How it declares/injects TerminalService
- Whether it has `providers: [TerminalService]`
- Lifecycle hooks implemented (ngOnDestroy?)

---

### Phase 2: Service Configuration Analysis

#### 2.1 Verify Current Service Declaration
```typescript
// Check current @Injectable decorator
// File: terminal.service.ts
// Expected: @Injectable() with no providedIn
// Document actual finding
```

#### 2.2 Check Service Lifecycle Implementation
- Verify ngOnDestroy implementation
- Check cleanup function tracking
- Verify TerminalManagerService integration
- Document isDestroyed flag usage

#### 2.3 Analyze Injection Scope
```typescript
// Create test to verify actual scope
// 1. Create two test components with providers: [TerminalService]
// 2. Create two test components without providers
// 3. Compare instances received
// 4. Document behavior
```

---

### Phase 3: Memory Leak Verification

#### 3.1 Create Memory Leak Test Scenarios
```typescript
// Scenario 1: Multiple components, same instance (current suspected state)
// - Create 5 components without providers
// - Check if they share same TerminalService instance
// - Monitor IPC listener count

// Scenario 2: Multiple components, different instances (desired state)
// - Create 5 components with providers: [TerminalService]
// - Verify each has unique instance
// - Verify cleanup on component destroy
```

#### 3.2 IPC Listener Tracking
```typescript
// Track actual IPC listeners
// 1. Count before component creation
// 2. Count after 5 components created
// 3. Count after components destroyed
// 4. Verify listener cleanup
```

---

### Phase 4: Root Cause Analysis

#### 4.1 Architecture Decision Tree
```
Is TerminalService @Injectable() only?
├─ YES: Is it provided in any module?
│   ├─ YES: It's module singleton (not component-scoped!)
│   └─ NO: Are components using providers: [TerminalService]?
│       ├─ YES: True component scope achieved
│       └─ NO: PROBLEM - Unclear scope, likely singleton
└─ NO: Check for providedIn value
    ├─ 'root': Application singleton
    └─ Other: Document scope
```

#### 4.2 Impact Assessment Matrix
| Component | Current Scope | Expected Scope | Memory Leak Risk | Action Required |
|-----------|--------------|----------------|------------------|-----------------|
| (To be filled during investigation) |

---

### Phase 5: Testing Current Behavior

#### 5.1 Instance Identity Test
```typescript
describe('TerminalService Instance Scope Verification', () => {
  it('should verify actual scope in TestBed', () => {
    // Test 1: Direct injection
    const service1 = TestBed.inject(TerminalService);
    const service2 = TestBed.inject(TerminalService);
    
    // Document: Are these same or different?
    console.log('Direct injection same instance?', service1 === service2);
  });
  
  it('should verify scope with component providers', () => {
    @Component({
      template: '',
      providers: [TerminalService]
    })
    class TestComp {}
    
    const fixture1 = TestBed.createComponent(TestComp);
    const fixture2 = TestBed.createComponent(TestComp);
    
    const service1 = fixture1.debugElement.injector.get(TerminalService);
    const service2 = fixture2.debugElement.injector.get(TerminalService);
    
    // Document: Are these same or different?
    console.log('Component-provided same instance?', service1 === service2);
  });
});
```

#### 5.2 Memory Leak Verification Test
```typescript
describe('Memory Leak Verification', () => {
  it('should track IPC listeners across component lifecycle', () => {
    // Get initial state
    const initialListeners = countIPCListeners();
    
    // Create components
    const components = createMultipleComponents(5);
    const afterCreateListeners = countIPCListeners();
    
    // Destroy components
    components.forEach(c => c.destroy());
    const afterDestroyListeners = countIPCListeners();
    
    // Document findings
    console.log('Listener counts:', {
      initial: initialListeners,
      afterCreate: afterCreateListeners,
      afterDestroy: afterDestroyListeners
    });
  });
});
```

---

### Phase 6: Solution Paths Based on Findings

#### Path A: If Components Don't Provide Service (Likely)
**Finding**: Components inject but don't provide TerminalService  
**Problem**: Still singleton, C1 not fixed  
**Solutions**:
1. Update all components to add `providers: [TerminalService]`
2. Switch to factory pattern
3. Implement reference counting on singleton

#### Path B: If Module Provides Service
**Finding**: Service in module providers array  
**Problem**: Module singleton, not component-scoped  
**Solutions**:
1. Remove from module providers
2. Add to each component's providers
3. Or switch to different pattern

#### Path C: If Mixed Usage (Worst Case)
**Finding**: Some components provide, others don't  
**Problem**: Inconsistent behavior, partial leak  
**Solutions**:
1. Standardize all components
2. Create two services (shared vs isolated)
3. Enforce via linting rules

---

## 🔍 INVESTIGATION CHECKLIST

### Immediate Actions (Must Complete First)
- [ ] Find all components using TerminalService
- [ ] Check how each component declares/injects the service
- [ ] Verify module-level providers
- [ ] Check current @Injectable configuration
- [ ] Run instance identity tests
- [ ] Count actual IPC listeners

### Analysis Actions
- [ ] Map component usage patterns
- [ ] Identify scope inconsistencies
- [ ] Measure memory leak risk
- [ ] Document actual vs expected behavior
- [ ] Determine root cause

### Decision Actions
- [ ] Choose solution path based on findings
- [ ] Assess breaking change impact
- [ ] Plan migration strategy
- [ ] Update test expectations
- [ ] Document final architecture

---

## 📊 INVESTIGATION TRACKING TEMPLATE

### Component Analysis Results
```markdown
| Component | Path | Has Providers? | Injection Pattern | Instance Scope | Risk Level |
|-----------|------|---------------|-------------------|----------------|------------|
| (To be filled) |
```

### Service Configuration Results
```markdown
- Current @Injectable: ____________
- Module providers: _______________
- Component providers count: ______
- Singleton behavior: ____________
```

### Memory Leak Test Results
```markdown
- Components tested: _____
- Shared instance: YES/NO
- IPC listeners cleaned: YES/NO
- Memory leak present: YES/NO
```

---

## ⚠️ CRITICAL SUCCESS CRITERIA

**Investigation is complete when we can answer**:
1. ✅ Is TerminalService actually component-scoped?
2. ✅ Do components properly provide the service?
3. ✅ Is the memory leak actually fixed?
4. ✅ What changes are needed to fix it properly?
5. ✅ What's the impact on existing code?

---

## 🚨 STOP CONDITIONS

**Stop all work if we find**:
1. ❌ Service is still singleton (C1 not fixed)
2. ❌ Inconsistent usage patterns (partial leak)
3. ❌ Module-level provision (wrong scope)
4. ❌ No component provides the service (definitely singleton)

---

## 📝 INVESTIGATION OUTPUT

### Required Deliverables
1. **Component Usage Report**: How each component uses TerminalService
2. **Scope Analysis**: Actual vs expected scope per component
3. **Memory Leak Assessment**: Is C1 actually fixed?
4. **Solution Recommendation**: How to properly fix the issue
5. **Migration Plan**: Steps to implement the fix
6. **Test Updates**: How to update tests to match reality

---

## 🎯 NEXT STEPS AFTER INVESTIGATION

Based on findings, we will:
1. **If C1 is not fixed**: Stop everything, implement proper fix
2. **If partially fixed**: Fix inconsistencies, update all components
3. **If actually fixed**: Update test to match actual pattern
4. **If different pattern needed**: Implement chosen solution

---

## 💡 KEY INVESTIGATION COMMANDS

```bash
# Quick scan for component usage
find ai-assistant/src -name "*.component.ts" -exec grep -l "TerminalService" {} \;

# Check for providers arrays
grep -r "providers:" ai-assistant/src --include="*.component.ts" -A 2 | grep -B1 -A1 "TerminalService"

# Find constructor injections
grep -r "constructor.*TerminalService" ai-assistant/src --include="*.ts"

# Module provider check
find ai-assistant/src -name "*.module.ts" -exec grep -l "TerminalService" {} \;
```

---

**Investigation Lead**: Alex Novak v3.0  
**Validation**: Dr. Sarah Chen v1.2  
**Timeline**: IMMEDIATE - Block all other work  

**Remember**: "A test that fails unexpectedly is often revealing a truth we didn't want to see." - Sam Martinez