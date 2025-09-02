# Round Table Discussion: Mandatory Living Documents System
**Date**: 2025-08-29
**Correlation ID**: ARCH-DOCS-001
**Facilitator**: Dr. Sarah Chen
**Status**: Active Discussion

## Participants
- Dr. Sarah Chen (Backend Architecture & Systems)
- Alex Novak (Frontend & Integration)
- Lisa Anderson (Documentation & Technical Writing)
- Priya Sharma (Testing & Quality)
- David Kim (Database & Performance)
- Riley Thompson (DevOps & Infrastructure)
- Jordan Chen (Security)
- Michael Torres (AI/ML Systems)

---

## Agenda Items

### 1. Mandatory Living Documents Structure
### 2. Correlation ID Tracking System
### 3. File Touch Documentation Update Policy

---

## Discussion: Mandatory Living Documents

### Opening Statement - Dr. Sarah Chen
"We need a system of mandatory documents that are automatically validated and updated with each commit. These documents should serve as the single source of truth for our system state, architecture, and roadmap."

### Lisa Anderson (Documentation Lead)
"I strongly support this. Here's my proposed structure for mandatory documents:

```
docs/
├── living/                          # Always current documents
│   ├── CURRENT_ARCHITECTURE.md      # What's actually built
│   ├── IMPLEMENTED_FEATURES.md      # What's working now
│   ├── UPCOMING_FEATURES.md         # Next sprint/phase items
│   ├── ACTIVE_MOCKS.md             # Current mock implementations
│   └── PHASE_PLAN.md               # Current phase work
├── phases/                          # Phase group organization
│   ├── active/                      # Current phase group
│   │   └── PHOENIX_RISING/          # Named phase group
│   │       ├── phase_1.md
│   │       ├── phase_2.md (current)
│   │       └── README.md
│   └── archived/                    # Completed phase groups
│       └── FOUNDATION_ALPHA/        # Previous phase group
└── decisions/                       # Round table decisions
```

Each document must have:
1. Correlation ID header
2. Last updated timestamp
3. Update frequency requirement
4. Validation schema"

### Alex Novak (Frontend Integration)
"From an integration perspective, we need these documents to be machine-readable as well as human-readable. I propose a YAML frontmatter approach:

```yaml
---
correlation_id: 4018e185-d0ad-4382-91cf-3224b61fcdfd
last_updated: 2025-08-29T15:35:33Z
update_frequency: per_commit
validation_schema: v1.0
phase_group: PHOENIX_RISING
phase_number: 2
---
```

This allows our governance hooks to automatically validate and update these fields."

### Priya Sharma (Testing & Quality)
"We need validation rules for each document type:

**CURRENT_ARCHITECTURE.md**:
- Must list all active components
- Must indicate which are mocked vs real
- Must include integration points
- Must have performance baselines

**IMPLEMENTED_FEATURES.md**:
- Must correlate to test coverage
- Must include feature flags if applicable
- Must indicate stability status
- Must link to relevant code

**UPCOMING_FEATURES.md**:
- Must have acceptance criteria
- Must have estimated complexity
- Must have dependencies listed
- Must have risk assessment"

### David Kim (Database & Performance)
"For the ACTIVE_MOCKS.md file, we need to track:
- Which systems are mocked
- Mock fidelity level (how realistic)
- Performance differences (mock vs real)
- Migration path to real implementation
- Test coverage using mocks

This is critical for understanding our technical debt."

### Riley Thompson (DevOps)
"Phase naming is crucial for deployment tracking. I propose:

**Phase Group Naming Convention**:
- Mythological themes for major versions: PHOENIX_RISING, ATLAS_FOUNDATION
- Each group has phases 1-N
- Clear completion criteria for phase groups
- Automatic archival on completion

**Benefits**:
- Easy to reference in commits
- Clear deployment boundaries
- Better change tracking
- Memorable milestone names"

### Jordan Chen (Security)
"Security consideration: These documents could expose system vulnerabilities if too detailed. I propose:

1. Public versions (in repo) with general information
2. Private versions (in secure storage) with sensitive details
3. Governance validates both exist and are in sync
4. Correlation IDs link both versions"

### Michael Torres (AI/ML)
"For AI governance, we need these documents to feed into our decision-making:
- Current architecture informs risk assessment
- Implemented features define capability boundaries
- Upcoming features trigger preparatory governance
- Phase plans allow proactive rule creation"

---

## Discussion: Correlation ID Tracking

### Dr. Sarah Chen
"Every document needs to track the last correlation ID that touched it. This creates an audit trail and ensures currency."

### Alex Novak
"I propose a three-tier correlation system:

```python
class CorrelationTracking:
    document_correlation: str  # Last update to this doc
    section_correlations: Dict[str, str]  # Per-section tracking
    reference_correlations: List[str]  # Related correlations
```

This allows fine-grained tracking while maintaining document-level currency."

### Lisa Anderson
"For readability, I suggest a standardized header format:

```markdown
<!-- 
GOVERNANCE TRACKING
Last Update: 2025-08-29T15:35:33Z
Correlation: 4018e185-d0ad-4382-91cf-3224b61fcdfd
Auto-Update: ENABLED
-->
```

This is human-readable but also parseable."

### Priya Sharma
"We need validation rules:
- Correlation ID must exist in audit log
- Timestamp must be within last N days (based on update_frequency)
- If stale, governance hook warns/blocks
- Manual override requires justification"

---

## Discussion: File Touch Documentation Update

### Dr. Sarah Chen
"If we modify a file, its documentation must be updated. This prevents documentation drift."

### Lisa Anderson
"I propose a 'documentation shadow' system:
- Every source file has a corresponding .doc.md file
- When file is touched, .doc.md must be updated
- If only refactoring, note 'REFACTOR_ONLY' in doc
- Governance validates both are updated together"

### Alex Novak
"That could get unwieldy. Alternative proposal:
- Inline documentation must be updated (mandatory)
- If significant change, update living documents
- Governance tracks 'documentation debt' score
- Periodic documentation sprints to pay down debt"

### Priya Sharma
"Compromise proposal:
1. Inline docs MUST be updated (enforced)
2. Living documents get AUTO-UPDATED sections
3. Manual sections marked for review
4. Governance tracks what needs human review

Example:
```markdown
## Component Status
<!-- AUTO-GENERATED - DO NOT EDIT -->
Last touched: 2025-08-29
Files modified: 15
Test coverage: 87%
<!-- END AUTO-GENERATED -->

## Architecture Notes
<!-- MANUAL - NEEDS REVIEW -->
Last reviewed: 2025-08-01 ⚠️ STALE
```"

### David Kim
"For database schema changes, this is critical. Proposal:
- Schema changes require migration document
- Document includes rollback procedure
- Performance impact assessment required
- All in version-controlled migrations/ folder"

### Riley Thompson
"From DevOps perspective:
- Deploy requires all docs current
- Stale docs block deployment
- Emergency override requires C-level approval
- All overrides logged for audit"

---

## Consensus Decisions

### 1. Mandatory Living Documents ✅ APPROVED

**Structure**:
```
docs/living/
├── CURRENT_ARCHITECTURE.md
├── IMPLEMENTED_FEATURES.md  
├── UPCOMING_FEATURES.md
├── ACTIVE_MOCKS.md
├── PHASE_PLAN.md
└── .governance/
    └── validation_schemas/
```

**Update Requirements**:
- CURRENT_ARCHITECTURE.md - Weekly or on architectural change
- IMPLEMENTED_FEATURES.md - Per feature completion
- UPCOMING_FEATURES.md - Per sprint planning
- ACTIVE_MOCKS.md - When mocks change
- PHASE_PLAN.md - Per phase transition

### 2. Phase Group Naming ✅ APPROVED

**Convention**: `{MYTHOLOGICAL_NAME}_{PURPOSE}`
- Examples: PHOENIX_RISING, ATLAS_FOUNDATION, HERMES_MESSAGING
- Each group contains phases 1-N
- Clear completion criteria required
- Automatic archival on completion

### 3. Correlation ID System ✅ APPROVED

**Implementation**:
```yaml
# Document header
---
governance:
  correlation_id: xxx-xxx-xxx
  last_updated: ISO-8601
  update_required_by: ISO-8601
  validation_schema: v1.0
  auto_sections: [status, metrics]
  manual_sections: [architecture, decisions]
---
```

### 4. Touch Update Policy ✅ APPROVED WITH CONDITIONS

**Rules**:
1. File modification requires inline doc update (ENFORCED)
2. Significant changes require living doc update (TRACKED)
3. Refactor-only changes marked as such (ALLOWED)
4. Documentation debt score tracked (MONITORED)
5. Quarterly documentation review required (SCHEDULED)

---

## Implementation Plan

### Phase 1: Templates and Schemas (Immediate)
- Create document templates
- Define validation schemas
- Implement correlation tracking

### Phase 2: Governance Integration (This Week)
- Add document validation to pre-commit hook
- Implement correlation ID injection
- Create update tracking system

### Phase 3: Automation (Next Week)
- Auto-update sections in documents
- Generate documentation debt reports
- Create documentation dashboard

### Phase 4: Enforcement (Two Weeks)
- Block commits with stale critical docs
- Require justification for overrides
- Generate compliance reports

---

## Action Items

1. **Lisa Anderson**: Create document templates with validation schemas
2. **Alex Novak**: Implement correlation ID tracking in governance
3. **Dr. Sarah Chen**: Update governance rules for document validation
4. **Priya Sharma**: Create test cases for document validation
5. **Riley Thompson**: Integrate with CI/CD pipeline
6. **All**: Review and approve templates before implementation

---

## Next Review
- Date: 2025-09-05
- Purpose: Review implementation progress
- Success Criteria: All templates created, validation working

---

**Consensus Status**: ✅ APPROVED BY ALL PARTICIPANTS

*This decision is binding and requires unanimous approval to modify.*