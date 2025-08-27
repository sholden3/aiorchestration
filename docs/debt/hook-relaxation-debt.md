# Pre-Commit Hook Relaxation Debt Tracker

**Created**: 2025-01-27  
**Owner**: Quinn Roberts v1.1 - Standards Enforcement  
**Phase**: 2.5 Implementation - Week 1  
**Auto-Expires**: Week 4 (2025-02-17)  

---

## 🚨 Critical Relaxations That MUST Be Re-Enabled

### 1. TypeScript Syntax Checking (HIGH PRIORITY)
**Current State**: DISABLED  
**Files Affected**: 13+ TypeScript files currently unchecked  
**Reason**: `node -c` doesn't understand TypeScript syntax  
**Risk Level**: HIGH - Could have syntax errors in production  

**Files Currently Skipped**:
- ai-assistant/scripts/chaos-test-jest.spec.ts
- ai-assistant/src/app/components/terminal/terminal.component.ts
- ai-assistant/src/app/services/ipc-error-boundary.service.spec.ts
- ai-assistant/src/app/services/ipc-error-boundary.service.ts
- ai-assistant/src/app/services/terminal-manager.service.ts
- ai-assistant/src/app/services/terminal.service.spec.ts
- ai-assistant/src/app/services/terminal.service.ts
- ai-assistant/src/test-global-setup.ts
- ai-assistant/src/test-global-teardown.ts
- ai-assistant/src/test-setup-electron.ts
- ai-assistant/src/test-setup.ts
- tests/unit/frontend/services/ipc.service.spec.ts
- archive/test_infrastructure/2025-08-26_test-setup-electron_v1_baseline.ts

**Week 2 Fix Required**:
```bash
# Install TypeScript compiler
npm install -g typescript

# Update pre-commit hook to use tsc
for file in *.ts; do
    tsc --noEmit "$file"
done
```

**Debt Interest**: Every day without TS checking = potential runtime errors

---

### 2. Secret Detection Relaxations (MEDIUM PRIORITY)
**Current State**: OVERLY PERMISSIVE  
**Files Skipped**: All .md, .json, .sh, package-lock.json files  
**Reason**: Too many false positives in documentation  
**Risk Level**: MEDIUM - Could accidentally commit secrets in these files  

**What We're Not Checking**:
- Documentation files (*.md) - Could contain example secrets
- Configuration files (*.json) - Could contain API keys
- Shell scripts (*.sh) - Could contain credentials
- Lock files (package-lock.json) - Less risky but still possible

**Week 2 Improvement Required**:
- Implement smarter detection that looks for actual values
- Check JSON files for non-example keys
- Scan shell scripts for export statements with secrets

---

### 3. Test Coverage Checking (LOW PRIORITY)
**Current State**: NOT RUNNING  
**Reason**: Tests take too long in pre-commit  
**Risk Level**: LOW - Tracked in CI/CD instead  

**Current Approach**: Deferred to CI/CD pipeline
**Week 3 Enhancement**: Add quick coverage check without full test run

---

## 📊 Relaxation Metrics

### Week 1 Status (Current)
```yaml
typescript_checking: disabled
secret_detection: relaxed
coverage_checking: deferred
documentation_checking: warning_only
linting: not_integrated
```

### Week 2 Requirements
```yaml
typescript_checking: enabled  # MUST FIX
secret_detection: improved    # SHOULD FIX
coverage_checking: quick_check # NICE TO HAVE
documentation_checking: required # MUST FIX
linting: warning_mode         # SHOULD ADD
```

### Week 3 Requirements
```yaml
typescript_checking: strict
secret_detection: comprehensive
coverage_checking: enforced_40_percent
documentation_checking: strict
linting: error_mode
```

---

## 🔧 Implementation Plan

### Week 2 - Day 1 (Priority)
1. **Enable TypeScript Checking**
   ```bash
   # Add to pre-commit v0.4
   if command -v tsc &> /dev/null; then
       tsc --noEmit "$file"
   else
       npx tsc --noEmit "$file"
   fi
   ```

2. **Improve Secret Detection**
   ```bash
   # Check JSON files more carefully
   if [[ "$file" == *.json ]] && [[ "$file" != *package-lock.json ]]; then
       # Look for actual keys, not just the word "secret"
       check_json_secrets "$file"
   fi
   ```

### Week 3 - Day 1
1. **Add Coverage Threshold Check**
2. **Enable Linting Integration**
3. **Restore Full Secret Scanning**

---

## 📈 Risk Assessment

### Current Risks (Week 1)
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TypeScript syntax errors | HIGH | HIGH | Manual review before push |
| Secrets in .md files | LOW | HIGH | Manual review of docs |
| Secrets in .json config | MEDIUM | HIGH | Use .env files |
| Low test coverage | HIGH | MEDIUM | Track in CI/CD |

### Risk Reduction Timeline
- **Week 1**: Accept risks, track everything
- **Week 2**: Eliminate TypeScript risk
- **Week 3**: Eliminate secret risk
- **Week 4**: All risks mitigated

---

## ✅ Payback Checklist

### Week 2 Must-Do
- [ ] Enable TypeScript syntax checking
- [ ] Test all previously skipped TS files
- [ ] Improve secret detection for config files
- [ ] Document any new debt incurred

### Week 3 Must-Do
- [ ] Enforce 40% coverage minimum
- [ ] Enable all linting rules
- [ ] Restore comprehensive secret scanning
- [ ] Zero tolerance for new debt

### Week 4 Must-Do
- [ ] All relaxations removed
- [ ] Full standards enforced
- [ ] Delete this file (debt paid!)

---

## 🚨 Accountability

**If TypeScript checking is not enabled by Week 2**:
- All TS commits must be manually reviewed
- No production deployments allowed
- Team lead notification required

**If secret detection not improved by Week 2**:
- Security audit required
- All config files manually reviewed
- Credential rotation if any found

---

## 📝 Lessons for Future

### What We Learned
1. **Blocking on TypeScript syntax was wrong** - Should have had proper tooling first
2. **Secret detection needs intelligence** - Not just pattern matching
3. **Progressive standards work** - But need clear tracking

### Permanent Changes to Consider
1. Always skip package-lock.json for secrets (too many false positives)
2. TypeScript checking should use tsc, not node
3. Coverage checking belongs in CI/CD, not pre-commit

---

**Remember**: Every relaxation is a loan we must repay. Interest compounds daily.

*"Technical debt is not free. Every day we don't pay it back, it gets more expensive."* - Quinn Roberts v1.1