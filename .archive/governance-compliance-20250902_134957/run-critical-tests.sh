#!/bin/bash

# ================================================
# 🧪 CRITICAL FIX TEST RUNNER
# ================================================
# Runs tests for C3 and H3 critical fixes
# Author: Sam Martinez v3.2.0
# Date: 2025-01-27

echo "================================================"
echo "🧪 RUNNING CRITICAL FIX TESTS"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run Python tests
run_python_tests() {
    local test_file=$1
    local test_name=$2
    
    echo "📝 Running: $test_name"
    echo "----------------------------------------"
    
    cd ai-assistant/backend
    python -m pytest "$test_file" -v --color=yes 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        ((FAILED_TESTS++))
    fi
    
    cd ../..
    ((TOTAL_TESTS++))
    echo ""
}

# Function to run Node.js tests
run_node_tests() {
    local test_file=$1
    local test_name=$2
    
    echo "📝 Running: $test_name"
    echo "----------------------------------------"
    
    cd ai-assistant/electron
    
    # Check if test dependencies are installed
    if [ ! -f "node_modules/mocha/bin/mocha" ]; then
        echo -e "${YELLOW}⚠️  Installing test dependencies...${NC}"
        npm install --save-dev mocha chai sinon proxyquire
    fi
    
    npx mocha "$test_file" --reporter spec 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        ((FAILED_TESTS++))
    fi
    
    cd ../..
    ((TOTAL_TESTS++))
    echo ""
}

# H3: Database Initialization Race Condition Tests
echo "🔍 H3: Database Initialization Race Condition Tests"
echo "================================================"
run_python_tests "tests/test_h3_initialization_race.py" "H3 Database Initialization Tests"

# C3: Process Coordination Tests
echo "🔍 C3: Process Coordination Tests"
echo "================================================"
run_node_tests "main.test.js" "C3 Process Coordination Tests"

# Summary
echo "================================================"
echo "📊 TEST SUMMARY"
echo "================================================"
echo "Total Test Suites: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL CRITICAL FIX TESTS PASSED!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  SOME TESTS FAILED - Please review the output above${NC}"
    exit 1
fi