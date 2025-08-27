// src/test-setup.ts - Sarah's comprehensive test setup
import 'jest-preset-angular/setup-jest';
import { TestBed } from '@angular/core/testing';

// Global test timeout - prevent hanging tests
jest.setTimeout(30000);

// Mock console methods to reduce noise (but preserve errors)
const originalError = console.error;
const originalWarn = console.warn;

console.error = (...args: any[]) => {
  // Allow Angular testing errors through
  if (args[0]?.toString().includes('Angular')) {
    originalError(...args);
  }
};

console.warn = (...args: any[]) => {
  // Suppress common Angular warnings in tests
  if (!args[0]?.toString().includes('Angular is running in development mode')) {
    originalWarn(...args);
  }
};

// Global test cleanup - Sarah's defensive pattern
afterEach(() => {
  // Clear all mocks to prevent test interdependence
  jest.clearAllMocks();
  
  // Reset DOM to prevent memory leaks
  document.body.innerHTML = '';
  
  // Clear any timers that might be hanging
  jest.clearAllTimers();
  
  // Reset TestBed - prevents module caching issues
  TestBed.resetTestingModule();
});

// Global error handler for uncaught exceptions
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Fail the test suite on unhandled rejections
  process.exit(1);
});

// Zone.js configuration for Angular testing
import 'zone.js';
import 'zone.js/testing';

// Configure Angular testing environment
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

// Initialize Angular testing environment only if not already initialized
// Alex's defensive pattern: Prevent double initialization
try {
  getTestBed().initTestEnvironment(
    BrowserDynamicTestingModule,
    platformBrowserDynamicTesting(),
    {
      teardown: { destroyAfterEach: true } // Automatic cleanup
    }
  );
} catch (error: any) {
  // Sarah's pattern: Only re-throw if it's not the expected error
  if (!error?.message?.includes('Cannot set base providers')) {
    throw error;
  }
  // Already initialized, which is fine
}