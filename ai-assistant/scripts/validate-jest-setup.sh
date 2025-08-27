#!/bin/bash
# scripts/validate-jest-setup.sh - Sarah's comprehensive validation

set -e

echo "=== JEST SETUP VALIDATION ==="

# Test 1: Basic Jest functionality
echo "Testing basic Jest functionality..."
npm run test -- --testPathPattern=nonexistent --passWithNoTests
echo "✓ Basic Jest configuration valid"

# Test 2: Angular preset integration
echo "Testing Angular preset integration..."
if npm run test -- --listTests | grep -q "spec.ts"; then
    echo "✓ Angular test files detected"
else
    echo "✗ No Angular test files found"
    exit 1
fi

# Test 3: Electron mocks functionality
echo "Testing Electron mocks..."
cat > temp-electron-test.spec.ts << 'EOF'
import { mockElectronAPI } from '../src/test-setup-electron';

describe('Electron Mock Validation', () => {
  it('should provide working electron API mock', async () => {
    expect(window.electronAPI).toBeDefined();
    const result = await window.electronAPI.invoke('test-channel', { data: 'test' });
    expect(result.success).toBe(true);
  });
  
  it('should track PTY processes', () => {
    const ptyId = window.electronAPI.createPty();
    expect(ptyId).toBeDefined();
    expect(window.electronAPI._ptyCount).toBe(1);
    
    window.electronAPI.killPty(ptyId);
    expect(window.electronAPI._ptyCount).toBe(0);
  });
});
EOF

npm run test -- temp-electron-test.spec.ts
rm temp-electron-test.spec.ts
echo "✓ Electron mocks working correctly"

# Test 4: Memory leak detection
echo "Testing memory leak detection..."
npm run test:memory -- --testPathPattern=nonexistent --passWithNoTests > memory-test.log 2>&1
if grep -q "heap usage" memory-test.log; then
    echo "✓ Memory monitoring active"
else
    echo "✗ Memory monitoring not working"
    exit 1
fi
rm memory-test.log

# Test 5: Coverage reporting
echo "Testing coverage reporting..."
npm run test:coverage -- --testPathPattern=nonexistent --passWithNoTests
if [ -d "coverage" ]; then
    echo "✓ Coverage reporting working"
else
    echo "✗ Coverage reporting failed"
    exit 1
fi

echo "=== ALL JEST SETUP VALIDATIONS PASSED ==="