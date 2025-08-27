#!/bin/bash
# File: .git/hooks/pre-commit

echo "🔒 PRE-COMMIT VALIDATION"
echo "Orchestrated Quality Gate - Alex Novak & Dr. Sarah Chen"

# Run the task completion validation
if ./validate-task-completion.sh; then
    echo ""
    echo "✅ PRE-COMMIT VALIDATION PASSED"
    echo "Proceeding with commit..."
    exit 0
else
    echo ""
    echo "❌ PRE-COMMIT VALIDATION FAILED"
    echo ""
    echo "Sarah's Analysis: Fix failure modes before committing"
    echo "Alex's Analysis: Resolve integration issues before committing"
    echo ""
    echo "Run './validate-task-completion.sh' to see detailed failures"
    exit 1
fi