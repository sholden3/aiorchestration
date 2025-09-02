#!/bin/bash
# File: validate-project-structure.sh

echo "🔍 PROJECT STRUCTURE VALIDATION"

# Check mandatory directories
REQUIRED_DIRS=(
    "ai-assistant/backend/tests"
    "ai-assistant/backend/docs/api"
    "ai-assistant/backend/docs/architecture" 
    "ai-assistant/backend/docs/runbooks"
    "ai-assistant/src/app/testing"
    "ai-assistant/src/e2e"
    "ai-assistant/electron/tests"
    "docs/fixes/critical"
    "docs/fixes/high"
    "docs/architecture"
    "docs/processes"
    "docs/runbooks"
    "tests/integration"
    "tests/performance"
    "tests/failure-scenarios"
)

missing_dirs=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing required directory: $dir"
        missing_dirs=$((missing_dirs + 1))
    fi
done

# Check test files exist for all implementation files
echo ""
echo "🧪 TEST FILE VALIDATION"

# Backend test validation
backend_files=$(find ai-assistant/backend -name "*.py" -not -path "*/tests/*" -not -name "__*" 2>/dev/null | wc -l)
backend_tests=$(find ai-assistant/backend/tests -name "test_*.py" 2>/dev/null | wc -l)
echo "Backend: $backend_files implementation files, $backend_tests test files"

# Frontend test validation  
component_files=$(find ai-assistant/src/app/components -name "*.component.ts" 2>/dev/null | wc -l)
component_tests=$(find ai-assistant/src/app/components -name "*.component.spec.ts" 2>/dev/null | wc -l)
echo "Components: $component_files components, $component_tests tests"

service_files=$(find ai-assistant/src/app/services -name "*.service.ts" 2>/dev/null | wc -l)
service_tests=$(find ai-assistant/src/app/services -name "*.service.spec.ts" 2>/dev/null | wc -l)
echo "Services: $service_files services, $service_tests tests"

# Documentation validation
echo ""
echo "📚 DOCUMENTATION VALIDATION"
[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md exists" || echo "❌ CLAUDE.md missing"
[ -f "docs/fixes/fixes-implementation-plan.md" ] && echo "✅ Fix plan exists" || echo "❌ Fix plan missing"

if [ $missing_dirs -eq 0 ]; then
    echo ""
    echo "✅ PROJECT STRUCTURE VALID"
    exit 0
else
    echo ""
    echo "❌ PROJECT STRUCTURE INVALID - $missing_dirs missing directories"
    exit 1
fi