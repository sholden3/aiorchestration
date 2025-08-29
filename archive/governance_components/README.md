# Governance Components Archive

## Archival Log

### 2025-01-28: smart_rules.py v1 → v2
**File**: `2025-01-28_smart_rules_v1_phase1-baseline.py`  
**Approved By**: Dr. Sarah Chen & Alex Novak  
**Related Issue**: Phase 1.5 - Cross-Language Exemption Architecture  
**Reason for Replacement**: 
- Implement context-aware pattern detection to eliminate false positives
- Add exemption system support for multi-language governance
- Separate safe operations (re.compile) from dangerous patterns (eval, exec)

**Key Changes**:
- Added ExemptionManager class for handling exemptions.yml
- Enhanced pattern detection with semantic analysis
- Backward compatibility wrapper for existing imports
- Support for file, class, and context-based exemptions

**Performance Metrics**:
- Before: 100% of patterns flagged (including false positives)
- After: Only truly dangerous patterns flagged, safe operations exempted
- Exemption lookup: <1ms with caching

**Rollback Instructions**:
1. Copy archived file back: `cp archive/governance_components/2025-01-28_smart_rules_v1_phase1-baseline.py governance/rules/smart_rules.py`
2. Remove exemptions.yml dependency from integrated_pre_commit_hook.py
3. Run tests: `python -m pytest governance/tests/test_smart_rules.py`

**Dependencies Affected**:
- governance/scripts/integrated_pre_commit_hook.py (imports SmartRules)
- governance/rules/rule_enhancer.py (if exists)
- Any custom validation scripts using SmartRules

**Testing**:
- Ensure all governance tests pass after replacement
- Verify exemptions.yml is loaded correctly
- Test with known false positive cases (re.compile, setattr in dataclasses)