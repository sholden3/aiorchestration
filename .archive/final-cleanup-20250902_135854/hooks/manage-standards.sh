#!/bin/bash

###############################################################################
# Standards Management Script
# 
# Purpose: Manage pre-commit hook versions and progression
# Author: Quinn Roberts v1.1
# Date: 2025-01-27
# 
# Usage:
#   ./manage-standards.sh status     - Show current standards version
#   ./manage-standards.sh upgrade    - Upgrade to next version
#   ./manage-standards.sh downgrade  - Downgrade to previous version
#   ./manage-standards.sh set <ver>  - Set specific version
#   ./manage-standards.sh restore   - Restore strict standards (v1.0)
###############################################################################

HOOKS_DIR="hooks/versions"
GIT_HOOKS_DIR=".git/hooks"
CURRENT_VERSION_FILE=".git/standards-version.txt"
FEATURE_FLAGS_FILE="config/feature-flags.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get current version
get_current_version() {
    if [ -f "$CURRENT_VERSION_FILE" ]; then
        cat "$CURRENT_VERSION_FILE"
    else
        echo "0.1"  # Default to minimal if not set
    fi
}

# Set version
set_version() {
    local version=$1
    local hook_file="$HOOKS_DIR/pre-commit-v${version}-*.sh"
    
    # Find the hook file for this version
    local hook_path=$(ls $hook_file 2>/dev/null | head -1)
    
    if [ -z "$hook_path" ]; then
        echo -e "${RED}Error: No hook found for version $version${NC}"
        return 1
    fi
    
    # Backup current hook
    if [ -f "$GIT_HOOKS_DIR/pre-commit" ]; then
        cp "$GIT_HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit.backup"
    fi
    
    # Install new hook
    cp "$hook_path" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    
    # Update version file
    echo "$version" > "$CURRENT_VERSION_FILE"
    
    # Update feature flags
    if [ -f "$FEATURE_FLAGS_FILE" ]; then
        # Update week number based on version
        local week=1
        case $version in
            "0.1") week=1 ;;
            "0.4") week=2 ;;
            "0.8") week=3 ;;
            "1.0") week=4 ;;
        esac
        
        # Use temporary file for JSON update
        jq ".enforcement.preCommitVersion = \"$version\" | .week = $week" "$FEATURE_FLAGS_FILE" > "${FEATURE_FLAGS_FILE}.tmp"
        mv "${FEATURE_FLAGS_FILE}.tmp" "$FEATURE_FLAGS_FILE"
    fi
    
    echo -e "${GREEN}✓ Standards updated to version $version${NC}"
    echo -e "  Hook: $(basename $hook_path)"
    
    # Show what this version enforces
    case $version in
        "0.1")
            echo -e "${YELLOW}  Week 1 - Minimal Standards:${NC}"
            echo "    • Blocks: Syntax errors, secrets"
            echo "    • Warns: Documentation, coverage"
            echo "    • Coverage target: 0% (tracking only)"
            ;;
        "0.4")
            echo -e "${YELLOW}  Week 2 - Progressive Standards:${NC}"
            echo "    • Blocks: Syntax, secrets, documentation"
            echo "    • Warns: Coverage <40%, linting"
            echo "    • Coverage target: 40%"
            ;;
        "0.8")
            echo -e "${YELLOW}  Week 3 - Maturing Standards:${NC}"
            echo "    • Blocks: Syntax, secrets, docs, coverage <40%"
            echo "    • Warns: Coverage <80%"
            echo "    • Coverage target: 80%"
            ;;
        "1.0")
            echo -e "${YELLOW}  Week 4 - Full Standards:${NC}"
            echo "    • All standards enforced"
            echo "    • Coverage required: 80%"
            echo "    • No technical debt allowed"
            ;;
    esac
}

# Show status
show_status() {
    local current=$(get_current_version)
    echo -e "${BLUE}=== Standards Management Status ===${NC}"
    echo ""
    echo -e "Current Version: ${GREEN}$current${NC}"
    
    # Calculate days since start
    local start_date="2025-01-27"
    local current_date=$(date +%Y-%m-%d)
    local days_elapsed=$(( ($(date -d "$current_date" +%s) - $(date -d "$start_date" +%s)) / 86400 ))
    local current_week=$(( (days_elapsed / 7) + 1 ))
    
    echo -e "Days Since Start: $days_elapsed (Week $current_week)"
    echo ""
    
    # Show progression schedule
    echo "Progression Schedule:"
    echo -e "  Week 1 (Days 1-7):   v0.1 - Minimal ${current_week==1 && echo '← Current' || echo ''}"
    echo -e "  Week 2 (Days 8-14):  v0.4 - Progressive ${current_week==2 && echo '← Current' || echo ''}"
    echo -e "  Week 3 (Days 15-21): v0.8 - Maturing ${current_week==3 && echo '← Current' || echo ''}"
    echo -e "  Week 4 (Days 22+):   v1.0 - Full ${current_week>=4 && echo '← Current' || echo ''}"
    echo ""
    
    # Check if upgrade is recommended
    local recommended_version="0.1"
    case $current_week in
        1) recommended_version="0.1" ;;
        2) recommended_version="0.4" ;;
        3) recommended_version="0.8" ;;
        *) recommended_version="1.0" ;;
    esac
    
    if [ "$current" != "$recommended_version" ]; then
        echo -e "${YELLOW}⚠️  Recommendation: Upgrade to v$recommended_version for Week $current_week${NC}"
        echo -e "   Run: ./manage-standards.sh upgrade"
    else
        echo -e "${GREEN}✓ Using correct version for Week $current_week${NC}"
    fi
    
    # Show current technical debt
    if [ -f "TECHNICAL_DEBT.md" ]; then
        echo ""
        echo "Technical Debt Summary:"
        local debt_lines=$(grep -c "^- \[ \]" TECHNICAL_DEBT.md || echo "0")
        echo "  Unpaid debt items: $debt_lines"
    fi
}

# Upgrade to next version
upgrade_version() {
    local current=$(get_current_version)
    local next=""
    
    case $current in
        "0.1") next="0.4" ;;
        "0.4") next="0.8" ;;
        "0.8") next="1.0" ;;
        "1.0") 
            echo -e "${YELLOW}Already at maximum version (1.0)${NC}"
            return 0
            ;;
        *)
            echo -e "${RED}Unknown current version: $current${NC}"
            return 1
            ;;
    esac
    
    echo -e "${BLUE}Upgrading from v$current to v$next...${NC}"
    set_version "$next"
    
    # Log the upgrade
    echo "$(date): Upgraded standards from v$current to v$next" >> .git/progressive-standards.log
}

# Downgrade to previous version
downgrade_version() {
    local current=$(get_current_version)
    local prev=""
    
    case $current in
        "0.1")
            echo -e "${YELLOW}Already at minimum version (0.1)${NC}"
            return 0
            ;;
        "0.4") prev="0.1" ;;
        "0.8") prev="0.4" ;;
        "1.0") prev="0.8" ;;
        *)
            echo -e "${RED}Unknown current version: $current${NC}"
            return 1
            ;;
    esac
    
    echo -e "${YELLOW}⚠️  Downgrading from v$current to v$prev${NC}"
    echo -e "${YELLOW}   This should only be done if the higher standards are blocking critical work${NC}"
    read -p "Are you sure? (y/N): " confirm
    
    if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
        set_version "$prev"
        echo "$(date): Downgraded standards from v$current to v$prev (manual)" >> .git/progressive-standards.log
    else
        echo "Downgrade cancelled"
    fi
}

# Main command handling
case "$1" in
    status)
        show_status
        ;;
    upgrade)
        upgrade_version
        ;;
    downgrade)
        downgrade_version
        ;;
    set)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Version number required${NC}"
            echo "Usage: $0 set <version>"
            echo "Available versions: 0.1, 0.4, 0.8, 1.0"
            exit 1
        fi
        set_version "$2"
        ;;
    restore)
        echo -e "${BLUE}Restoring full standards (v1.0)...${NC}"
        set_version "1.0"
        ;;
    *)
        echo "Standards Management Script"
        echo ""
        echo "Usage:"
        echo "  $0 status     - Show current standards version"
        echo "  $0 upgrade    - Upgrade to next version"
        echo "  $0 downgrade  - Downgrade to previous version"  
        echo "  $0 set <ver>  - Set specific version (0.1, 0.4, 0.8, 1.0)"
        echo "  $0 restore    - Restore strict standards (v1.0)"
        echo ""
        echo "Current version: $(get_current_version)"
        ;;
esac