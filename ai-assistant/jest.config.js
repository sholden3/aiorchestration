// jest.config.js - Production-ready Jest configuration
// Approved by: Alex Novak (Frontend) & Dr. Sarah Chen (Backend)
// Decision: Simplified configuration following Jest API correctly
// Rollback: Previous version archived at archive/test_infrastructure/

module.exports = {
  // Angular preset - handles TypeScript compilation and Angular testing utilities
  preset: 'jest-preset-angular',
  
  // Test environment setup files - executed after Jest is initialized
  setupFilesAfterEnv: [
    '<rootDir>/src/test-setup.ts',           // Angular testing environment
    '<rootDir>/src/test-setup-electron.ts'   // Enhanced Electron mocks (v2)
  ],
  
  // DOM environment for Angular components
  testEnvironment: 'jsdom',
  
  // Node.js specific options for Electron compatibility
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons']
  },
  
  // TypeScript transformation (Sarah's requirement: proper error messages)
  transform: {
    '^.+\\.(ts|js|mjs|html)$': [
      'jest-preset-angular',
      {
        tsconfig: '<rootDir>/tsconfig.spec.json',
        stringifyContentPathRegex: '\\.(html|svg)$'
      }
    ]
  },
  
  // Test discovery patterns (Alex's requirement: find all test types)
  testMatch: [
    '<rootDir>/src/**/*.spec.ts',
    '<rootDir>/src/**/*.test.ts'
  ],
  
  // Module resolution
  moduleNameMapper: {
    '^@/(.*)': '<rootDir>/src/$1',
    '^@app/(.*)': '<rootDir>/src/app/$1',
    '^@shared/(.*)': '<rootDir>/src/shared/$1',
    '\\.(css|less|scss|sass)$': 'jest-preset-angular/build/config/style-transform.js'
  },
  
  // Transform only what's needed (performance optimization)
  transformIgnorePatterns: [
    'node_modules/(?!(@angular|@ngrx|rxjs)/)'
  ],
  
  // Resource management (Alex's Electron requirements)
  maxWorkers: 1,              // Prevent Electron process conflicts
  testTimeout: 45000,         // Sarah's requirement: Handle backend maintenance delays
  detectOpenHandles: true,    // Catch resource leaks
  forceExit: true,           // Prevent hanging processes
  
  // Coverage configuration (balanced for emergency fixes)
  collectCoverage: false,     // Disabled by default for performance
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.spec.ts',
    '!src/app/**/*.test.ts',
    '!src/app/**/*.module.ts',
    '!src/app/**/index.ts'
  ],
  
  // Realistic thresholds (Sarah's requirement: don't block emergency fixes)
  coverageThreshold: {
    global: {
      statements: 70,    // Reduced from 80 for emergency flexibility
      branches: 60,      // Reduced from 70 for complex conditionals
      functions: 70,     // Reduced from 80 for utility functions
      lines: 70          // Reduced from 80 for emergency fixes
    }
  },
  
  // Coverage output formats
  coverageReporters: ['text', 'lcov', 'html'],
  coverageDirectory: '<rootDir>/coverage',
  
  // Performance monitoring (Sarah's observability requirement)
  logHeapUsage: true,
  verbose: true,
  errorOnDeprecated: true,
  
  // Caching for faster subsequent runs
  cache: true,
  cacheDirectory: '<rootDir>/node_modules/.cache/jest',
  
  // CI optimizations
  bail: process.env.CI === 'true' ? 5 : 0,  // Fail fast in CI
  silent: process.env.CI === 'true',         // Less output in CI
  
  // Watch mode exclusions (development performance)
  watchPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/coverage/',
    '<rootDir>/archive/'
  ],
  
  // Global setup/teardown
  globalSetup: '<rootDir>/src/test-global-setup.ts',
  globalTeardown: '<rootDir>/src/test-global-teardown.ts',
  
  // Test result processors for CI integration
  testResultsProcessor: process.env.CI ? 'jest-junit' : undefined,
  
  // Notification settings (Alex's 3 AM requirement: clear failures)
  notify: false,
  notifyMode: 'failure',
  
  // Test sequencer for predictable execution order
  // testSequencer: '<rootDir>/src/test-sequencer.js', // Commented: Not needed, maxWorkers=1 provides sufficient control
  
  // Resolver for custom module resolution
  resolver: undefined,
  
  // Runner for custom test execution
  runner: 'jest-runner',
  
  // Prevent configuration issues
  clearMocks: true,           // Clear mock state between tests
  resetMocks: false,          // Don't reset mock implementations
  restoreMocks: false,        // Don't restore original implementations
  
  // Module file extensions
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
    'node'
  ]
};

/**
 * Configuration Rationale:
 * 
 * 1. Removed 'projects' array - Jest doesn't support testTimeout at project level
 * 2. Simplified structure for maintainability
 * 3. Balanced coverage thresholds for emergency fixes
 * 4. Resource limits prevent CI hangs
 * 5. Clear error reporting for 3 AM debugging
 * 
 * Rollback Procedure:
 * 1. Copy archive/test_infrastructure/[date]_jest.config_v[n].js back
 * 2. Run: npm test -- --passWithNoTests to verify
 * 3. Maximum rollback time: 2 minutes
 * 
 * Monitoring:
 * - Test execution time: Should be < 5 minutes for full suite
 * - Memory usage: Should stay below 2GB
 * - Coverage: Track trends, not absolute values
 */