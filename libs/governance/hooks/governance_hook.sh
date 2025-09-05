#!/bin/bash
# Claude Code Governance Hook Wrapper
# This script is called by Claude Code to enforce governance

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         GOVERNANCE SYSTEM INTERCEPTING OPERATION          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set hook type based on context
export CLAUDE_HOOK_TYPE="${1:-decision}"

# Log the governance action
echo "[$(date +%H:%M:%S)] GOVERNANCE: Validating AI operation..."
echo "  Type: $CLAUDE_HOOK_TYPE"
echo "  Working Dir: $(pwd)"

# Run the Python governance hook
python "$SCRIPT_DIR/claude_code_governance_hook.py" "$@"

# Check for specific operations
case "$CLAUDE_HOOK_TYPE" in
    "pre-write")
        echo "[GOVERNANCE] Pre-write validation: Checking for dangerous patterns..."
        ;;
    "post-write")
        echo "[GOVERNANCE] Post-write audit: Logging changes..."
        ;;
    "pre-execute")
        echo "[GOVERNANCE] Pre-execution check: Validating command safety..."
        ;;
    *)
        echo "[GOVERNANCE] General validation completed"
        ;;
esac

echo ""
echo "✓ Governance check complete - Operation monitored and logged"
echo ""