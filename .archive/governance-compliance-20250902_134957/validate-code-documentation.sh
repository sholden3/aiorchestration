#!/bin/bash

# Code Documentation Validation Script
# Enforces comprehensive documentation standards for all source files
# Author: Alex Novak v3.0 & Dr. Sarah Chen v1.2
# Framework: Mandatory code documentation requirements

set -e

echo "=== CODE DOCUMENTATION VALIDATION ==="
echo "Enforcing comprehensive documentation standards..."
echo "Standards Reference: CLAUDE.md#code-documentation-requirements"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation counters
TOTAL_FILES=0
VALID_FILES=0
ERROR_COUNT=0

# Function to check file header requirements
check_file_header() {
    local file="$1"
    local errors=0
    
    echo "  Checking file header: $file"
    
    # Required header fields
    local required_fields=(
        "@fileoverview"
        "@author"
        "@architecture"
        "@responsibility"
        "@dependencies"
        "@integration_points"
        "@testing_strategy"
        "@governance"
    )
    
    for field in "${required_fields[@]}"; do
        if ! grep -q "$field" "$file"; then
            echo -e "    ${RED}ERROR: Missing $field in file header${NC}"
            ((errors++))
        fi
    done
    
    # Check for business logic summary
    if ! grep -A 10 "@fileoverview" "$file" | grep -q "Business Logic Summary:"; then
        echo -e "    ${RED}ERROR: Missing Business Logic Summary${NC}"
        ((errors++))
    fi
    
    # Check for architecture integration
    if ! grep -A 15 "@fileoverview" "$file" | grep -q "Architecture Integration:"; then
        echo -e "    ${RED}ERROR: Missing Architecture Integration section${NC}"
        ((errors++))
    fi
    
    return $errors
}

# Function to check class documentation
check_class_documentation() {
    local file="$1"
    local errors=0
    
    # Find all class declarations
    local class_lines=$(grep -n "^export class\|^class" "$file" || true)
    
    if [[ -n "$class_lines" ]]; then
        echo "  Checking class documentation: $file"
        
        while IFS= read -r line; do
            local line_num=$(echo "$line" | cut -d: -f1)
            local class_name=$(echo "$line" | sed 's/.*class \([A-Za-z0-9_]*\).*/\1/')
            
            echo "    Validating class: $class_name (line $line_num)"
            
            # Check if there's documentation before the class
            local doc_start=$((line_num - 20))
            if [[ $doc_start -lt 1 ]]; then doc_start=1; fi
            
            local doc_section=$(sed -n "${doc_start},${line_num}p" "$file")
            
            # Required class documentation fields
            local class_fields=(
                "@class"
                "@description"
                "@architecture_role"
                "@business_logic"
                "@failure_modes"
                "@debugging_info"
            )
            
            for field in "${class_fields[@]}"; do
                if ! echo "$doc_section" | grep -q "$field"; then
                    echo -e "      ${RED}ERROR: Class $class_name missing $field${NC}"
                    ((errors++))
                fi
            done
            
            # Check for defensive programming patterns
            if ! echo "$doc_section" | grep -q "Defensive Programming Patterns:"; then
                echo -e "      ${RED}ERROR: Class $class_name missing defensive programming patterns${NC}"
                ((errors++))
            fi
            
            # Check for integration boundaries
            if ! echo "$doc_section" | grep -q "Integration Boundaries:"; then
                echo -e "      ${RED}ERROR: Class $class_name missing integration boundaries${NC}"
                ((errors++))
            fi
            
        done <<< "$class_lines"
    fi
    
    return $errors
}

# Function to check method documentation
check_method_documentation() {
    local file="$1"
    local errors=0
    
    # Find public methods (simplified check)
    local method_lines=$(grep -n "public\|async.*(" "$file" | grep -v "constructor" | head -5 || true)
    
    if [[ -n "$method_lines" ]]; then
        echo "  Checking method documentation: $file"
        
        while IFS= read -r line; do
            local line_num=$(echo "$line" | cut -d: -f1)
            local method_info=$(echo "$line" | cut -d: -f2-)
            
            echo "    Validating method at line $line_num"
            
            # Check if there's documentation before the method
            local doc_start=$((line_num - 25))
            if [[ $doc_start -lt 1 ]]; then doc_start=1; fi
            
            local doc_section=$(sed -n "${doc_start},${line_num}p" "$file")
            
            # Required method documentation fields
            local method_fields=(
                "@method"
                "@description"
                "@business_rule"
                "@validation"
                "@error_handling"
                "@testing_requirements"
            )
            
            local missing_fields=0
            for field in "${method_fields[@]}"; do
                if ! echo "$doc_section" | grep -q "$field"; then
                    ((missing_fields++))
                fi
            done
            
            # Allow some methods to have minimal documentation if not business critical
            if [[ $missing_fields -gt 2 ]]; then
                echo -e "      ${YELLOW}WARNING: Method missing $missing_fields critical documentation fields${NC}"
            fi
            
            # Check for Sarah's framework
            if echo "$doc_section" | grep -q "@business_rule" && ! echo "$doc_section" | grep -q "Sarah's Framework Check:"; then
                echo -e "      ${RED}ERROR: Business method missing Sarah's Framework validation${NC}"
                ((errors++))
            fi
            
        done <<< "$method_lines"
    fi
    
    return $errors
}

# Function to check business logic documentation
check_business_logic_comments() {
    local file="$1"
    local errors=0
    
    # Look for business logic indicators
    local business_indicators=$(grep -n "if.*business\|validate\|check.*rule\|enforce\|BUSINESS" "$file" || true)
    
    if [[ -n "$business_indicators" ]]; then
        echo "  Checking business logic comments: $file"
        
        while IFS= read -r line; do
            local line_num=$(echo "$line" | cut -d: -f1)
            
            # Check surrounding lines for documentation
            local context_start=$((line_num - 3))
            if [[ $context_start -lt 1 ]]; then context_start=1; fi
            local context_end=$((line_num + 3))
            
            local context=$(sed -n "${context_start},${context_end}p" "$file")
            
            # Check for required business logic comments
            if ! echo "$context" | grep -q "BUSINESS RULE:\|VALIDATION:\|ERROR HANDLING:"; then
                echo -e "    ${YELLOW}WARNING: Line $line_num may need business logic documentation${NC}"
            fi
            
        done <<< "$business_indicators"
    fi
    
    return $errors
}

# Function to calculate documentation score
calculate_documentation_score() {
    local file="$1"
    local score=0
    
    # File header score (25 points)
    if grep -q "@fileoverview\|@author\|@architecture\|@responsibility" "$file"; then
        score=$((score + 25))
    fi
    
    # Class documentation score (25 points)  
    if grep -q "@class\|@architecture_role\|@business_logic" "$file"; then
        score=$((score + 25))
    fi
    
    # Method documentation score (25 points)
    if grep -q "@method\|@description\|@business_rule" "$file"; then
        score=$((score + 25))
    fi
    
    # Business logic comments score (25 points)
    if grep -q "BUSINESS RULE:\|VALIDATION:\|ERROR HANDLING:" "$file"; then
        score=$((score + 25))
    fi
    
    echo $score
}

# Main validation function
validate_file() {
    local file="$1"
    local total_errors=0
    
    echo ""
    echo "=== Validating: $file ==="
    
    # Check file header
    check_file_header "$file"
    total_errors=$((total_errors + $?))
    
    # Check class documentation
    check_class_documentation "$file"
    total_errors=$((total_errors + $?))
    
    # Check method documentation
    check_method_documentation "$file"
    total_errors=$((total_errors + $?))
    
    # Check business logic comments
    check_business_logic_comments "$file"
    total_errors=$((total_errors + $?))
    
    # Calculate documentation score
    local score=$(calculate_documentation_score "$file")
    echo "  Documentation Score: $score/100"
    
    if [[ $score -lt 90 ]]; then
        echo -e "  ${RED}ERROR: Documentation score below minimum (90/100)${NC}"
        total_errors=$((total_errors + 1))
    fi
    
    if [[ $total_errors -eq 0 ]]; then
        echo -e "  ${GREEN}✅ PASSED: All documentation requirements met${NC}"
        ((VALID_FILES++))
    else
        echo -e "  ${RED}❌ FAILED: $total_errors documentation issues found${NC}"
    fi
    
    ((TOTAL_FILES++))
    ERROR_COUNT=$((ERROR_COUNT + total_errors))
    
    return $total_errors
}

# Main execution
echo ""
echo "Scanning TypeScript files..."

# Find all TypeScript files (excluding node_modules, dist, etc.)
typescript_files=$(find . -name "*.ts" -not -path "./node_modules/*" -not -path "./dist/*" -not -path "./coverage/*" || true)

if [[ -z "$typescript_files" ]]; then
    echo -e "${YELLOW}WARNING: No TypeScript files found to validate${NC}"
else
    for file in $typescript_files; do
        validate_file "$file"
    done
fi

echo ""
echo "Scanning Python files..."

# Find all Python files
python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" || true)

if [[ -n "$python_files" ]]; then
    for file in $python_files; do
        # Adapt validation for Python files (similar patterns)
        echo "  Checking Python file: $file (basic validation)"
        if ! grep -q "\"\"\".*@fileoverview\|'''.*@fileoverview" "$file"; then
            echo -e "    ${YELLOW}WARNING: Python file may need comprehensive documentation${NC}"
        fi
    done
fi

echo ""
echo "=== VALIDATION SUMMARY ==="
echo "Total files processed: $TOTAL_FILES"
echo "Files meeting standards: $VALID_FILES"
echo "Total errors found: $ERROR_COUNT"

if [[ $ERROR_COUNT -eq 0 ]]; then
    echo -e "${GREEN}✅ SUCCESS: All code documentation requirements met!${NC}"
    echo "Ready for commit with comprehensive documentation."
    exit 0
else
    echo -e "${RED}❌ FAILURE: $ERROR_COUNT documentation issues must be resolved${NC}"
    echo ""
    echo "REQUIRED ACTIONS:"
    echo "1. Add missing file headers with all required fields"
    echo "2. Document all classes with architecture integration"
    echo "3. Add comprehensive method documentation"
    echo "4. Include business logic comments with governance framework checks"
    echo "5. Ensure documentation score ≥ 90/100 for all files"
    echo ""
    echo "Reference: CLAUDE.md#code-documentation-requirements"
    exit 1
fi