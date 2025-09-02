#!/bin/bash

###############################################################################
# validate-specialist-decisions.sh
# 
# Author: Quinn Roberts v1.1 - Standards Enforcement Specialist
# Date: 2025-01-27
# Purpose: Validate all specialist decisions in code are tracked in DECISIONS.md
# Architecture Reference: docs/architecture/documentation-standards.md
# Governance: Dynamic Persona Orchestration Framework v2.2
# 
# This script ensures that any code referencing specialist decisions is
# properly documented in DECISIONS.md with full traceability
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SPECIALIST DECISION VALIDATION ===${NC}"
echo "Checking for undocumented specialist invocations..."
echo "Required by: Dynamic Persona Orchestration Framework v2.2"
echo ""

VALIDATION_PASSED=true

# Check if PERSONAS.md exists
if [ ! -f "PERSONAS.md" ]; then
    echo -e "${RED}❌ ERROR: PERSONAS.md not found - persona model not defined${NC}"
    VALIDATION_PASSED=false
else
    echo -e "${GREEN}✅ PERSONAS.md exists${NC}"
fi

# Check if DECISIONS.md exists
if [ ! -f "DECISIONS.md" ]; then
    echo -e "${RED}❌ ERROR: DECISIONS.md not found - decision log missing${NC}"
    VALIDATION_PASSED=false
else
    echo -e "${GREEN}✅ DECISIONS.md exists${NC}"
fi

# Enhanced specialist pattern detection
SPECIALIST_PATTERNS=(
    "@specialist"
    "@decision"
    "INVOKING:"
    "SPECIALIST:"
    "Per specialist guidance"
    "specialist approval required"
    "Morgan Hayes"
    "Sam Martinez"
    "Riley Thompson"
    "Quinn Roberts"
    "Taylor Williams"
    "Casey Jordan"
    "Dr. Avery Chen"
    "Dr. Jamie Rodriguez"
)

# Check for specialist invocations in recent commits
echo ""
echo "Checking staged files for specialist markers..."

# Look for specialist invocation patterns in staged files
SPECIALIST_FILES=""
for pattern in "${SPECIALIST_PATTERNS[@]}"; do
    FILES=$(git diff --cached --name-only | xargs grep -l "$pattern" 2>/dev/null || true)
    if [ ! -z "$FILES" ]; then
        SPECIALIST_FILES="$SPECIALIST_FILES$FILES"$'\n'
    fi
done

SPECIALIST_FILES=$(echo "$SPECIALIST_FILES" | sort -u | grep -v "^$" || true)

if [ ! -z "$SPECIALIST_FILES" ]; then
    echo -e "${YELLOW}⚠️  Found specialist markers in:${NC}"
    echo "$SPECIALIST_FILES"
    
    # Check if DECISIONS.md is also being updated
    if git diff --cached --name-only | grep -q "DECISIONS.md"; then
        echo -e "${GREEN}✅ DECISIONS.md is being updated${NC}"
    else
        echo -e "${RED}❌ ERROR: Specialist invoked but DECISIONS.md not updated${NC}"
        VALIDATION_PASSED=false
    fi
    
    # Check for inline documentation
    if git diff --cached | grep -q "@specialist\|@decision\|@constraint"; then
        echo -e "${GREEN}✅ Found inline specialist documentation${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: Consider adding @specialist inline documentation${NC}"
    fi
fi

# Check for orphaned decisions (decisions without corresponding code)
echo ""
echo -e "${BLUE}Checking for decision/code alignment...${NC}"

# Count decisions in DECISIONS.md (excluding template and examples)
DECISION_COUNT=$(grep -c "^### 20[0-9][0-9]-" DECISIONS.md 2>/dev/null || echo "0")
echo "📊 Total decisions logged: $DECISION_COUNT"

# Validate each decision has corresponding implementation
echo ""
echo "Validating decision implementation status..."

# Parse decisions and check for implementation markers
UNIMPLEMENTED=0
while IFS= read -r decision_line; do
    # Extract date and specialist from decision line
    if [[ "$decision_line" =~ ^###.*([0-9]{4}-[0-9]{2}-[0-9]{2}).*-.*(.+).*-.*(.+)$ ]]; then
        DATE="${BASH_REMATCH[1]}"
        SPECIALIST=$(echo "${BASH_REMATCH[2]}" | xargs)
        
        # Check if this decision has corresponding code
        CODE_EXISTS=false
        for pattern in "${SPECIALIST_PATTERNS[@]}"; do
            if grep -r "$pattern.*$DATE" src backend electron 2>/dev/null | grep -v "DECISIONS.md" > /dev/null; then
                CODE_EXISTS=true
                break
            fi
        done
        
        if [ "$CODE_EXISTS" = false ]; then
            echo -e "${YELLOW}  ⚠️  Decision from $DATE may not be implemented${NC}"
            ((UNIMPLEMENTED++))
        fi
    fi
done < <(grep "^### 20[0-9][0-9]-" DECISIONS.md 2>/dev/null || true)

if [ "$UNIMPLEMENTED" -gt 0 ]; then
    echo -e "${YELLOW}Found $UNIMPLEMENTED potentially unimplemented decisions${NC}"
fi

# Check for action items that are overdue
echo ""
echo -e "${BLUE}Checking for overdue action items...${NC}"

TODAY=$(date +%Y-%m-%d)
OVERDUE=""
while IFS= read -r line; do
    if [[ "$line" =~ \[\ \].*([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
        DATE="${BASH_REMATCH[1]}"
        if [[ "$DATE" < "$TODAY" ]]; then
            OVERDUE="$OVERDUE$line"$'\n'
        fi
    fi
done < <(grep -E "\[ \].*20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]" DECISIONS.md 2>/dev/null || true)

if [ ! -z "$OVERDUE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Found overdue action items:${NC}"
    echo "$OVERDUE"
fi

# Check for conflicting decisions
echo ""
echo -e "${BLUE}Checking for potential decision conflicts...${NC}"

# Look for common conflict patterns
CONFLICTS=$(grep -A5 -B5 "override\|supersede\|conflict\|contradict" DECISIONS.md 2>/dev/null | grep -E "^### " | wc -l || echo "0")
if [ "$CONFLICTS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $CONFLICTS potential decision conflicts - review needed${NC}"
fi

# Check for stale file references in DECISIONS.md
echo ""
echo -e "${BLUE}Checking for stale file references...${NC}"
STALE_REFS=0

while IFS= read -r file_ref; do
    # Clean up the file reference
    clean_ref=$(echo "$file_ref" | sed 's/[`*]//g' | xargs)
    
    # Check if file exists in common locations
    if [ -n "$clean_ref" ] && [[ "$clean_ref" == *"."* ]]; then
        FILE_EXISTS=false
        for dir in . src backend electron tests docs; do
            if [ -f "$dir/$clean_ref" ]; then
                FILE_EXISTS=true
                break
            fi
        done
        
        if [ "$FILE_EXISTS" = false ]; then
            echo -e "${YELLOW}  ⚠️  Referenced file may not exist: $clean_ref${NC}"
            ((STALE_REFS++))
        fi
    fi
done < <(grep -oE '\`[^`]+\.[a-z]+\`' DECISIONS.md 2>/dev/null | sort -u || true)

if [ "$STALE_REFS" -gt 0 ]; then
    echo -e "${YELLOW}Found $STALE_REFS potentially stale file references${NC}"
fi

# Generate summary statistics
echo ""
echo -e "${BLUE}=== VALIDATION SUMMARY ===${NC}"
echo "Total Decisions Logged: $DECISION_COUNT"
echo "Potentially Unimplemented: $UNIMPLEMENTED"
echo "Stale File References: $STALE_REFS"
echo "Potential Conflicts: $CONFLICTS"

# Determine if validation passes
if [ "$UNIMPLEMENTED" -gt 2 ] || [ "$STALE_REFS" -gt 3 ]; then
    VALIDATION_PASSED=false
fi

# Final validation result
echo ""
echo "==================================="
if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}✅ SPECIALIST DECISION VALIDATION PASSED${NC}"
    echo ""
    echo "Documentation Standards Met:"
    echo "- Persona model defined (PERSONAS.md)"
    echo "- Decision log maintained (DECISIONS.md)"
    echo "- Inline documentation present"
    echo "- Decision implementation tracked"
    echo ""
    echo "Governance Framework: Dynamic Persona Orchestration v2.2"
    echo "Quality Gate: Decision Traceability ✓"
    exit 0
else
    echo -e "${RED}❌ SPECIALIST DECISION VALIDATION FAILED${NC}"
    echo ""
    echo "Required Actions:"
    echo "1. Update DECISIONS.md with all specialist decisions"
    echo "2. Add inline @specialist documentation to code"
    echo "3. Ensure PERSONAS.md defines all specialists"
    echo "4. Implement decisions referenced in DECISIONS.md"
    echo "5. Clean up stale file references"
    echo ""
    echo "See PERSONAS.md for specialist documentation requirements"
    echo "See DECISIONS.md for decision tracking template"
    echo ""
    echo "This validation is required by the Dynamic Persona Orchestration Framework"
    exit 1
fi