# Specialist Invocation Guide - Practical Usage Instructions

**Framework Version**: 2.2  
**Last Updated**: January 27, 2025  
**Purpose**: Step-by-step guide for invoking specialists in the Dynamic Persona Framework  

---

## 🎯 Quick Decision Tree

```
Is the issue domain-specific and complex?
├── NO → Alex & Sarah handle it
└── YES → Continue ↓

Does it match a specialist domain?
├── NO → Alex & Sarah collaborate
└── YES → Continue ↓

Is it HIGH severity or above?
├── NO → Consider if specialist needed
└── YES → INVOKE SPECIALIST
```

---

## 📋 Specialist Domain Mapping

### Performance Issues → Taylor Williams v1.1
**Invoke When You See:**
- Memory usage growing unbounded
- Bundle size > 5MB
- Page load time > 3 seconds
- Memory leaks detected
- Cache hit rate < 80%

**Example Invocation:**
```
[SPECIALIST INVOCATION REQUEST]
Issue: Bundle size has grown to 8.2MB, initial load taking 7 seconds
Domain: Performance Engineering
Severity: HIGH
Metrics: Bundle analysis shows 3MB of unused dependencies
Request: Invoke Taylor Williams for bundle optimization expertise
```

### WebSocket/Real-time Issues → Jordan Lee v3.2
**Invoke When You See:**
- WebSocket connections > 10,000
- Connection storms during deployments
- "Too many connections" errors
- Real-time features failing
- Message queue backlogs

**Example Invocation:**
```
[SPECIALIST INVOCATION REQUEST]
Issue: WebSocket connections climbing rapidly, 42K connections, memory at 7.8GB
Domain: Real-time Systems
Severity: CRITICAL
Metrics: Connection rate exceeding cleanup by 300%
Request: Invoke Jordan Lee for WebSocket crisis management
```

### Database Performance → Dr. Jamie Rodriguez v3.2
**Invoke When You See:**
- Query response > 1 second
- Connection pool exhaustion
- Database initialization failures
- Race conditions in startup
- Deadlock warnings

**Example Invocation:**
```
[SPECIALIST INVOCATION REQUEST]
Issue: API returning 500 errors for first 30 seconds after deployment
Domain: Database Performance
Severity: HIGH
Metrics: Connection pool not ready errors in logs
Request: Invoke Dr. Jamie Rodriguez for initialization sequence expertise
```

### Security Vulnerabilities → Morgan Hayes v2.0
**Invoke When You See:**
- Authentication bypasses
- IPC security concerns
- Data exposure in errors
- Privilege escalation attempts
- Suspicious access patterns

**Example Invocation:**
```
[SPECIALIST INVOCATION REQUEST]
Issue: IPC errors exposing database connection strings in renderer
Domain: Security Architecture
Severity: CRITICAL
Metrics: 15 privilege escalation attempts detected
Request: Invoke Morgan Hayes for security boundary hardening
```

### UI/UX Performance → Maya Patel v3.0
**Invoke When You See:**
- FPS drops below 30
- Accessibility violations
- Animation jank
- Material Design issues
- Responsive design breaks

**Example Invocation:**
```
[SPECIALIST INVOCATION REQUEST]
Issue: Terminal UI freezing during memory warnings, FPS at 8
Domain: UI/UX Performance
Severity: HIGH
Metrics: 12fps during critical operations, users complaining
Request: Invoke Maya Patel for motion design optimization
```

---

## 🔄 The Invocation Process

### Step 1: Core Architects Identify Need
**Alex**: "This WebSocket issue is beyond standard patterns. We're seeing connection storms."
**Sarah**: "Agreed. Connection cleanup rate is 300% behind establishment. We need Jordan."

### Step 2: Formal Invocation
```
**[INVOKING: Jordan Lee - Real-time Systems Specialist]**
```

### Step 3: Specialist Entry
**Jordan v3.2**: *immediately reviewing metrics* "I need three things:
1. Current connection pool configuration
2. Reconnection logic implementation  
3. Client-side cleanup handlers"

### Step 4: Specialist Intervention
- Provides immediate stabilization code
- Implements long-term architectural fixes
- Makes binding technical decisions
- Documents patterns and solutions

### Step 5: Knowledge Transfer
**Jordan v3.2**: "Here's my connection storm detection pattern..."
```javascript
// Jordan's pattern documentation
class ConnectionStormDetector {
  // Implementation details
}
```

### Step 6: Specialist Exit
```
**[EXITING: Jordan Lee]**
```

### Step 7: Documentation Update
```markdown
### 2025-01-27 - Jordan Lee - WebSocket Resource Management
**Invoked By**: Sarah Chen & Alex Novak
**Decisions Made**: 
- Max 5 connections per client IP
- Exponential backoff with jitter required
- 60-second zombie connection cleanup
**Binding Constraints**: These limits cannot be exceeded
```

---

## 📝 Documentation Templates

### Invocation Request Template
```markdown
[SPECIALIST INVOCATION REQUEST]
Issue: [Specific technical problem]
Domain: [Performance/Security/Database/Real-time/UI-UX]
Severity: [CRITICAL/HIGH/MEDIUM]
Current Metrics:
- [Metric 1]: [Value]
- [Metric 2]: [Value]
Evidence:
- [Log excerpts or screenshots]
Failed Attempts:
- [What core team tried]
Request: Invoke [Specialist Name] for [specific expertise needed]
```

### During Intervention Template
```markdown
**[Specialist Name]**: *[initial action]* "[First response]"

[Shows their analysis approach]

**Critical Findings**:
1. [Finding 1]
2. [Finding 2]

**Immediate Actions**:
```[language]
// Emergency fix code
```

**Long-term Solution**:
```[language]
// Architectural improvement
```
```

### Exit Documentation Template
```markdown
### DECISIONS.md Entry
**Date**: [YYYY-MM-DD]
**Specialist**: [Name Version]
**Invoked By**: [Alex and/or Sarah]
**Issue**: [Brief description]

**Decisions Made**:
1. [Technical decision 1]
2. [Technical decision 2]

**Binding Constraints**:
- [Constraint that can't be changed]
- [Another binding limit]

**Success Metrics**:
- [Metric]: [Target value]
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T: Invoke Without Metrics
```markdown
WRONG:
"The app feels slow, let's get Taylor"

RIGHT:
"Memory usage at 3.2GB, growing 100MB/hour, heap snapshots show leaked listeners"
```

### ❌ DON'T: Invoke Multiple Specialists
```markdown
WRONG:
"We have database AND security issues, invoke Jamie and Morgan together"

RIGHT:
"Security issue is more critical, invoke Morgan first. Jamie can address database after."
```

### ❌ DON'T: Skip Documentation
```markdown
WRONG:
[Specialist provides solution]
"Thanks, implementing now!"

RIGHT:
[Specialist provides solution]
"Updating DECISIONS.md with binding constraints..."
```

### ❌ DON'T: Override Specialist Decisions
```markdown
WRONG:
"Jamie said 100 connections max, but let's do 200"

RIGHT:
"Jamie's 100 connection limit is binding. If we need more, we must re-invoke Jamie."
```

---

## 🎯 Invocation Triggers by Severity

### CRITICAL (Invoke Immediately)
- System down or failing
- Security breach detected
- Data loss occurring
- Revenue impact active
- User-facing catastrophic errors

### HIGH (Invoke Within 1 Hour)
- Performance degrading rapidly
- Errors affecting >10% of users
- Resource exhaustion trending
- Security vulnerability discovered
- Deployment failures

### MEDIUM (Consider Invocation)
- Performance below targets
- Technical debt mounting
- Architecture concerns
- Optimization opportunities
- Prevention planning needed

---

## 📊 Success Metrics for Invocations

### Good Invocation Indicators
✅ Issue resolved within specialist's session
✅ Clear documentation produced
✅ Prevention measures implemented
✅ Team learned new patterns
✅ No regression after implementation

### Poor Invocation Indicators
❌ Multiple specialists needed for same issue
❌ Issue returns after specialist exit
❌ Documentation incomplete
❌ Team confused by solution
❌ Decisions contradicting each other

---

## 💡 Pro Tips

1. **Prepare Before Invoking**
   - Gather all relevant metrics
   - Document what's been tried
   - Have code/logs ready to share

2. **During Intervention**
   - Let specialist lead
   - Ask clarifying questions
   - Take detailed notes
   - Test solutions immediately

3. **After Exit**
   - Update documentation immediately
   - Implement all recommendations
   - Set up monitoring for recurrence
   - Share learnings with team

4. **Emergency Protocol**
   - For CRITICAL issues, invoke immediately
   - Skip formal request template if system failing
   - Document retroactively once stable

---

## 🔗 Quick Links

- [PERSONAS.md](../PERSONAS.md) - Full specialist profiles
- [DECISIONS.md](../DECISIONS.md) - Binding decisions log
- [Crisis Scenarios](.) - Example interventions
- [Validation Script](../../validate-specialist-decisions.sh) - Enforcement tool

---

**Remember**: Specialists are experts brought in for their deep domain knowledge. Trust their expertise, document their decisions, and learn from their interventions.

*"The right expert at the right time with the right documentation transforms crisis into capability."*