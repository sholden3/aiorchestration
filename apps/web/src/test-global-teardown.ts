// src/test-global-teardown.ts - Enhanced with environment restoration
export default async (): Promise<void> => {
  console.log('\n🧹 Jest Global Teardown - Cleaning up test environment');
  
  // Restore original environment (Sarah's defensive pattern)
  if ((global as any).__ORIGINAL_ENV__) {
    process.env = (global as any).__ORIGINAL_ENV__;
    delete (global as any).__ORIGINAL_ENV__;
    console.log('✅ Original environment restored');
  }
  
  // Clean up any test artifacts
  // This would disconnect from test database, clean temp files, etc.
  
  // Report memory usage (Alex's 3 AM debugging feature)
  if (process.memoryUsage) {
    const usage = process.memoryUsage();
    console.log(`📊 Final memory usage: ${Math.round(usage.heapUsed / 1024 / 1024)}MB`);
  }
  
  console.log('✅ Test environment cleaned up\n');
};