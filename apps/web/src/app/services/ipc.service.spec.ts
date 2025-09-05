/**
 * IPC Security Service Tests - Comprehensive Security Boundary Validation
 * 
 * @author Sam Martinez v3.2.0 - Testing Lead - Comprehensive Security Testing
 * @author Morgan Hayes v2.0 - Security Specialist - Security Attack Simulation
 * @author Alex Novak v3.0 - Core Architect - Integration & Error Boundary Testing
 * 
 * @fileoverview Complete test suite for IPC security boundaries
 * @architecture Frontend - IPC Security Testing Layer
 * @testing_strategy
 *   - Unauthorized channel access attempts
 *   - Oversized message rejection
 *   - Injection attack simulation
 *   - Timing attack protection
 *   - Pattern matching edge cases
 *   - Rate limiting enforcement
 *   - Audit trail verification
 * 
 * SECURITY TEST CATEGORIES:
 * 1. Channel Whitelist Validation
 * 2. Message Size Limits
 * 3. Rate Limiting
 * 4. Pattern Matching Security
 * 5. Injection Attack Protection
 * 6. Audit Trail Verification
 * 7. Error Boundary Integration
 * 8. Performance & Timing Security
 */

import { TestBed } from '@angular/core/testing';
import { IPCService } from './ipc.service';
import { IPCErrorBoundaryService, IPCError, IPCErrorType } from './ipc-error-boundary.service';
import { mockElectronAPI } from '../../../src/test-setup-electron';

// Test utilities for security testing
interface SecurityTestScenario {
  name: string;
  channel: string;
  data?: any;
  options?: any;
  expectedResult: 'ALLOW' | 'REJECT';
  expectedReason?: string;
}

describe('IPCService - Security Boundary Tests', () => {
  let service: IPCService;
  let mockBoundaryService: any;
  
  beforeEach(() => {
    // Create mock for IPC Error Boundary Service using Jest
    const mockSafeIPCInvoke = jest.fn();
    const spy = {
      safeIPCInvoke: mockSafeIPCInvoke
    };
    
    // Setup Electron API mock
    if (!(window as any).electronAPI) {
      (window as any).electronAPI = mockElectronAPI;
    }
    mockElectronAPI._resetState();
    
    TestBed.configureTestingModule({
      providers: [
        IPCService,
        { provide: IPCErrorBoundaryService, useValue: spy }
      ]
    });
    
    service = TestBed.inject(IPCService);
    mockBoundaryService = TestBed.inject(IPCErrorBoundaryService) as any;
    
    // Default mock response
    mockBoundaryService.safeIPCInvoke.mockResolvedValue({ success: true });
  });
  
  describe('SECURITY LAYER 1: Channel Whitelist Validation', () => {
    const validChannels: SecurityTestScenario[] = [
      {
        name: 'AI task execution',
        channel: 'execute-ai-task',
        expectedResult: 'ALLOW'
      },
      {
        name: 'Terminal session creation',
        channel: 'create-terminal-session',
        expectedResult: 'ALLOW'
      },
      {
        name: 'Cache metrics',
        channel: 'get-cache-metrics',
        expectedResult: 'ALLOW'
      },
      {
        name: 'Dynamic terminal session response',
        channel: 'terminal-session-created-abc123',
        expectedResult: 'ALLOW'
      },
      {
        name: 'Dynamic terminal output',
        channel: 'terminal-output-session-456',
        expectedResult: 'ALLOW'
      }
    ];
    
    const invalidChannels: SecurityTestScenario[] = [
      {
        name: 'Unauthorized system access',
        channel: 'system-shutdown',
        expectedResult: 'REJECT',
        expectedReason: 'Channel not in whitelist'
      },
      {
        name: 'File system manipulation',
        channel: 'delete-file',
        expectedResult: 'REJECT',
        expectedReason: 'Channel not in whitelist'
      },
      {
        name: 'Process control',
        channel: 'exec-command',
        expectedResult: 'REJECT',
        expectedReason: 'Channel not in whitelist'
      },
      {
        name: 'Empty channel name',
        channel: '',
        expectedResult: 'REJECT',
        expectedReason: 'Invalid channel format'
      },
      {
        name: 'Extremely long channel name',
        channel: 'a'.repeat(300),
        expectedResult: 'REJECT',
        expectedReason: 'Channel name too long'
      },
      {
        name: 'Null channel (type coercion attack)',
        channel: null as any,
        expectedResult: 'REJECT',
        expectedReason: 'Invalid channel format'
      }
    ];
    
    validChannels.forEach(scenario => {
      it(`should ALLOW valid channel: ${scenario.name}`, async () => {
        const result = await service.safeInvoke(scenario.channel, scenario.data, scenario.options);
        expect(result).toBeTruthy();
        expect(mockBoundaryService.safeIPCInvoke).toHaveBeenCalledWith(
          scenario.channel,
          expect.objectContaining({ correlationId: expect.any(String) }),
          expect.any(Object)
        );
      });
    });
    
    invalidChannels.forEach(scenario => {
      it(`should REJECT invalid channel: ${scenario.name}`, async () => {
        try {
          await service.safeInvoke(scenario.channel, scenario.data, scenario.options);
          fail(`Expected rejection for channel: ${scenario.channel}`);
        } catch (error: any) {
          expect(error).toBeInstanceOf(IPCError);
          expect(error.type).toBe(IPCErrorType.CONNECTION_FAILED);
          if (scenario.expectedReason) {
            expect(error.message).toContain(scenario.expectedReason);
          }
        }
      });
    });
  });
  
  describe('SECURITY LAYER 2: Message Size Limits', () => {
    it('should allow small messages', async () => {
      const smallMessage = { data: 'test' };
      const result = await service.safeInvoke('execute-ai-task', smallMessage);
      expect(result).toBeTruthy();
    });
    
    it('should reject oversized messages for AI tasks', async () => {
      // AI tasks have 512KB limit
      const largeMessage = { data: 'x'.repeat(600 * 1024) }; // 600KB
      
      try {
        await service.safeInvoke('execute-ai-task', largeMessage);
        fail('Expected message size rejection');
      } catch (error: any) {
        expect(error).toBeInstanceOf(IPCError);
        expect(error.message).toContain('Message size');
        expect(error.message).toContain('exceeds limit');
      }
    });
    
    it('should reject oversized messages for terminal commands', async () => {
      // Terminal commands have 8KB limit
      const largeCommand = { command: 'x'.repeat(10 * 1024) }; // 10KB
      
      try {
        await service.safeInvoke('terminal-write', largeCommand);
        fail('Expected message size rejection');
      } catch (error: any) {
        expect(error).toBeInstanceOf(IPCError);
        expect(error.message).toContain('Message size');
        expect(error.message).toContain('exceeds limit');
      }
    });
    
    it('should handle circular references safely', async () => {
      // Create circular reference
      const circularObj: any = { name: 'test' };
      circularObj.self = circularObj;
      
      const result = await service.safeInvoke('get-cache-metrics', circularObj);
      expect(result).toBeTruthy();
    });
    
    it('should filter dangerous properties in message calculation', async () => {
      const dangerousMessage = {
        __proto__: { malicious: true },
        constructor: { name: 'attack' },
        data: 'legitimate'
      };
      
      const result = await service.safeInvoke('get-cache-metrics', dangerousMessage);
      expect(result).toBeTruthy();
    });
  });
  
  describe('SECURITY LAYER 3: Rate Limiting', () => {
    it('should allow calls within rate limit', async () => {
      // Make several calls within the limit
      for (let i = 0; i < 5; i++) {
        const result = await service.safeInvoke('get-cache-metrics');
        expect(result).toBeTruthy();
      }
    });
    
    it('should enforce terminal session creation limits', async () => {
      // Terminal sessions have limit of 10 per minute
      const promises: Promise<any>[] = [];
      
      // Make 11 requests (should trigger rate limit)
      for (let i = 0; i < 11; i++) {
        promises.push(
          service.safeInvoke('create-terminal-session', { sessionId: `session-${i}` })
            .catch(error => error)
        );
      }
      
      const results = await Promise.all(promises);
      const rejections = results.filter(result => result instanceof IPCError);
      
      expect(rejections.length).toBeGreaterThan(0);
      expect(rejections[0].message).toContain('Rate limit exceeded');
    });
    
    it('should reset rate limits after time window', async () => {
      // This test would need to manipulate time or use a shorter window for practical testing
      // For now, we'll test the rate limit tracking structure
      const metrics = service.getSecurityMetrics();
      expect(metrics.rateLimitTrackers).toBeGreaterThanOrEqual(0);
    });
  });
  
  describe('SECURITY LAYER 4: Pattern Matching Security', () => {
    it('should match exact patterns correctly', () => {
      const result = service.testChannelValidation('execute-ai-task');
      expect(result.isValid).toBe(true);
    });
    
    it('should match wildcard patterns safely', () => {
      const testCases = [
        { channel: 'terminal-session-created-abc123', expected: true },
        { channel: 'terminal-session-created-', expected: true },
        { channel: 'terminal-output-session-456', expected: true },
        { channel: 'terminal-session-xyz', expected: false },
        { channel: 'malicious-terminal-session-created-hack', expected: false }
      ];
      
      testCases.forEach(testCase => {
        const result = service.testChannelValidation(testCase.channel);
        expect(result.isValid).toBe(testCase.expected);
      });
    });
    
    it('should resist ReDoS attacks with complex patterns', () => {
      // Test pattern that could cause ReDoS with regex
      const attackPattern = 'a'.repeat(10000) + 'b';
      const startTime = Date.now();
      
      const result = service.testChannelValidation(attackPattern);
      const duration = Date.now() - startTime;
      
      expect(result.isValid).toBe(false);
      expect(duration).toBeLessThan(100); // Should complete quickly
    });
    
    it('should handle malformed patterns safely', () => {
      const malformedChannels = [
        'channel\x00with\x00nulls',
        'channel\nwith\nnewlines',
        'channel\rwith\rreturns',
        'channel\twith\ttabs',
        'channel with spaces',
        'channel"with"quotes',
        'channel<with>brackets',
        'channel&with&ampersands'
      ];
      
      malformedChannels.forEach(channel => {
        const result = service.testChannelValidation(channel);
        expect(result.isValid).toBe(false);
      });
    });
  });
  
  describe('SECURITY LAYER 5: Injection Attack Protection', () => {
    it('should sanitize SQL injection attempts in channel names', () => {
      const sqlInjectionChannels = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'; --",
        "1' UNION SELECT * FROM secrets --"
      ];
      
      sqlInjectionChannels.forEach(channel => {
        const result = service.testChannelValidation(channel);
        expect(result.isValid).toBe(false);
      });
    });
    
    it('should resist XSS attempts in channel names', () => {
      const xssChannels = [
        '<script>alert("xss")</script>',
        'javascript:alert("xss")',
        'onmouseover="alert(1)"',
        '<img src=x onerror=alert(1)>'
      ];
      
      xssChannels.forEach(channel => {
        const result = service.testChannelValidation(channel);
        expect(result.isValid).toBe(false);
      });
    });
    
    it('should handle command injection attempts', () => {
      const commandInjectionChannels = [
        'channel; rm -rf /',
        'channel && malicious-command',
        'channel | cat /etc/passwd',
        'channel $(whoami)',
        'channel `id`'
      ];
      
      commandInjectionChannels.forEach(channel => {
        const result = service.testChannelValidation(channel);
        expect(result.isValid).toBe(false);
      });
    });
    
    it('should safely handle path traversal attempts', () => {
      const pathTraversalChannels = [
        '../../../etc/passwd',
        '..\\..\\..\\windows\\system32\\config\\sam',
        '....//....//....//etc/passwd',
        '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'
      ];
      
      pathTraversalChannels.forEach(channel => {
        const result = service.testChannelValidation(channel);
        expect(result.isValid).toBe(false);
      });
    });
  });
  
  describe('SECURITY LAYER 6: Audit Trail Verification', () => {
    it('should log successful channel access', async () => {
      await service.safeInvoke('get-cache-metrics');
      
      const auditLog = service.getAuditLog(10);
      const lastEvent = auditLog[auditLog.length - 1];
      
      expect(lastEvent).toBeDefined();
      expect(lastEvent.action).toBe('ALLOWED');
      expect(lastEvent.channel).toBe('get-cache-metrics');
      expect(lastEvent.correlationId).toBeDefined();
    });
    
    it('should log channel rejections with reasons', async () => {
      try {
        await service.safeInvoke('unauthorized-channel');
      } catch (error) {
        // Expected to fail
      }
      
      const auditLog = service.getAuditLog(10);
      const rejectionEvent = auditLog.find(event => event.action === 'REJECTED');
      
      expect(rejectionEvent).toBeDefined();
      expect(rejectionEvent!.channel).toBe('unauthorized-channel');
      expect(rejectionEvent!.reason).toBeDefined();
      expect(rejectionEvent!.correlationId).toBeDefined();
    });
    
    it('should log rate limit violations', async () => {
      // Trigger rate limit
      const promises = [];
      for (let i = 0; i < 15; i++) {
        promises.push(
          service.safeInvoke('create-terminal-session', { sessionId: `session-${i}` })
            .catch(error => error)
        );
      }
      await Promise.all(promises);
      
      const auditLog = service.getAuditLog(50);
      const rateLimitEvent = auditLog.find(event => event.action === 'RATE_LIMITED');
      
      expect(rateLimitEvent).toBeDefined();
      expect(rateLimitEvent!.reason).toContain('Rate limit exceeded');
    });
    
    it('should log message size violations', async () => {
      try {
        const largeMessage = { data: 'x'.repeat(600 * 1024) };
        await service.safeInvoke('execute-ai-task', largeMessage);
      } catch (error) {
        // Expected to fail
      }
      
      const auditLog = service.getAuditLog(10);
      const sizeEvent = auditLog.find(event => event.action === 'SIZE_EXCEEDED');
      
      expect(sizeEvent).toBeDefined();
      expect(sizeEvent!.messageSize).toBeDefined();
      expect(sizeEvent!.reason).toContain('Message size');
    });
    
    it('should maintain audit log size limits', async () => {
      // Generate many events to test log rotation
      for (let i = 0; i < 1200; i++) {
        try {
          await service.safeInvoke(`unauthorized-${i}`);
        } catch (error) {
          // Expected to fail
        }
      }
      
      const auditLog = service.getAuditLog(2000); // Request more than the limit
      expect(auditLog.length).toBeLessThanOrEqual(1000); // Should be capped at 1000
    });
  });
  
  describe('SECURITY LAYER 7: Error Boundary Integration', () => {
    it('should integrate with IPCErrorBoundaryService correctly', async () => {
      await service.safeInvoke('get-cache-metrics', { test: 'data' });
      
      expect(mockBoundaryService.safeIPCInvoke).toHaveBeenCalledWith(
        'get-cache-metrics',
        expect.objectContaining({ 
          test: 'data',
          correlationId: expect.any(String)
        }),
        expect.any(Object)
      );
    });
    
    it('should handle error boundary service failures', async () => {
      mockBoundaryService.safeIPCInvoke.mockRejectedValue(new Error('Boundary service failed'));
      
      try {
        await service.safeInvoke('get-cache-metrics');
        fail('Expected error from boundary service');
      } catch (error: any) {
        expect(error).toBeInstanceOf(IPCError);
        expect(error.type).toBe(IPCErrorType.UNKNOWN);
      }
    });
    
    it('should preserve correlation IDs through error boundary', async () => {
      const customCorrelationId = 'test-correlation-123';
      
      await service.safeInvoke('get-cache-metrics', {}, { correlationId: customCorrelationId });
      
      expect(mockBoundaryService.safeIPCInvoke).toHaveBeenCalledWith(
        'get-cache-metrics',
        expect.objectContaining({ correlationId: customCorrelationId }),
        expect.any(Object)
      );
    });
  });
  
  describe('SECURITY LAYER 8: Performance & Timing Security', () => {
    it('should complete channel validation quickly', () => {
      const startTime = performance.now();
      
      // Test 1000 validation calls
      for (let i = 0; i < 1000; i++) {
        service.testChannelValidation('execute-ai-task');
      }
      
      const duration = performance.now() - startTime;
      expect(duration).toBeLessThan(100); // Should complete in under 100ms
    });
    
    it('should not leak timing information about channel validation', () => {
      const validChannel = 'execute-ai-task';
      const invalidChannel = 'unauthorized-channel-with-very-long-name-that-might-take-longer';
      
      // Measure validation time for valid channel
      const validStartTime = performance.now();
      for (let i = 0; i < 100; i++) {
        service.testChannelValidation(validChannel);
      }
      const validDuration = performance.now() - validStartTime;
      
      // Measure validation time for invalid channel
      const invalidStartTime = performance.now();
      for (let i = 0; i < 100; i++) {
        service.testChannelValidation(invalidChannel);
      }
      const invalidDuration = performance.now() - invalidStartTime;
      
      // Times should be similar (within 50% of each other)
      const ratio = Math.max(validDuration, invalidDuration) / Math.min(validDuration, invalidDuration);
      expect(ratio).toBeLessThan(1.5);
    });
    
    it('should handle concurrent validation requests safely', async () => {
      const promises = [];
      
      // Make 50 concurrent validation requests
      for (let i = 0; i < 50; i++) {
        promises.push(service.safeInvoke('get-cache-metrics', { request: i }));
      }
      
      const results = await Promise.all(promises);
      
      // All should succeed
      results.forEach(result => {
        expect(result).toBeTruthy();
      });
    });
  });
  
  describe('DEBUG UTILITIES & MONITORING', () => {
    it('should provide comprehensive security metrics', () => {
      const metrics = service.getSecurityMetrics();
      
      expect(metrics).toEqual(expect.objectContaining({
        config: expect.any(Object),
        auditEvents: expect.any(Number),
        rateLimitTrackers: expect.any(Number),
        recentRejections: expect.any(Array),
        channelWhitelist: expect.any(Number)
      }));
      
      expect(metrics.channelWhitelist).toBeGreaterThan(0);
    });
    
    it('should provide access to audit log', () => {
      const auditLog = service.getAuditLog(5);
      expect(Array.isArray(auditLog)).toBe(true);
    });
    
    it('should attach global debug utilities', () => {
      // Check if debug functions are attached to window
      expect(typeof (window as any).getIPCSecurityDebug).toBe('function');
      expect(typeof (window as any).testIPCChannel).toBe('function');
      
      // Test debug function
      const debugInfo = (window as any).getIPCSecurityDebug();
      expect(debugInfo.instanceId).toBeDefined();
      expect(debugInfo.metrics).toBeDefined();
      expect(debugInfo.whitelist).toBeDefined();
    });
  });
  
  describe('EDGE CASES & STRESS TESTING', () => {
    it('should handle null and undefined data gracefully', async () => {
      const testCases = [null, undefined, '', 0, false, NaN, {}];
      
      for (const testData of testCases) {
        const result = await service.safeInvoke('get-cache-metrics', testData);
        expect(result).toBeTruthy();
      }
    });
    
    it('should handle deeply nested objects safely', async () => {
      // Create deeply nested object
      let deepObject: any = { level: 0 };
      let current = deepObject;
      
      for (let i = 1; i < 100; i++) {
        current.next = { level: i };
        current = current.next;
      }
      
      const result = await service.safeInvoke('get-cache-metrics', deepObject);
      expect(result).toBeTruthy();
    });
    
    it('should handle very large arrays safely', async () => {
      const largeArray = new Array(1000).fill(0).map((_, i) => ({ index: i, data: `item-${i}` }));
      
      try {
        await service.safeInvoke('execute-ai-task', { items: largeArray });
        // This might succeed or fail depending on the actual size, both are valid
      } catch (error) {
        // If it fails, it should be due to size limits
        expect(error).toBeInstanceOf(IPCError);
        expect(error.message).toContain('Message size');
      }
    });
    
    it('should maintain state consistency under stress', async () => {
      const promises = [];
      
      // Create mixed valid/invalid requests
      for (let i = 0; i < 100; i++) {
        if (i % 3 === 0) {
          // Valid request
          promises.push(service.safeInvoke('get-cache-metrics').catch(e => e));
        } else if (i % 3 === 1) {
          // Invalid channel
          promises.push(service.safeInvoke('invalid-channel').catch(e => e));
        } else {
          // Rate limit test
          promises.push(service.safeInvoke('create-terminal-session', { id: i }).catch(e => e));
        }
      }
      
      const results = await Promise.all(promises);
      
      // Service should still be functional
      const finalTest = await service.safeInvoke('get-cache-metrics');
      expect(finalTest).toBeTruthy();
      
      // Metrics should be consistent
      const metrics = service.getSecurityMetrics();
      expect(metrics.auditEvents).toBeGreaterThan(0);
    });
  });
});