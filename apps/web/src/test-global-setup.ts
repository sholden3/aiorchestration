// src/test-global-setup.ts - Enhanced version with environment isolation
export default async (): Promise<void> => {
  console.log('\n🧪 Jest Global Setup - Initializing test environment');
  
  // Store original environment for restoration (Sarah's defensive pattern)
  (global as any).__ORIGINAL_ENV__ = { ...process.env };
  
  // Set test environment variables with explicit typing
  process.env['NODE_ENV'] = 'test';
  process.env['CI'] = process.env['CI'] || 'false';
  
  // Sarah's concern: Allow environment override for integration tests
  if (process.env['TEST_ENVIRONMENT_OVERRIDE']) {
    process.env['NODE_ENV'] = process.env['TEST_ENVIRONMENT_OVERRIDE'];
    console.log(`Environment override detected: NODE_ENV=${process.env['NODE_ENV']}`);
  }
  
  // Suppress console output in CI (fixed - no jest functions here)
  if (process.env['CI'] === 'true') {
    console.log = () => {};
    console.info = () => {};
  }
  
  console.log(`✅ Test environment initialized: NODE_ENV=${process.env['NODE_ENV']}\n`);
};