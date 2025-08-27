/**
 * @fileoverview Unit tests for IPC Service with comprehensive observability and defensive patterns
 * @author Alex Novak v3.0 & Sam Martinez v3.2.0 - 2025-01-27
 * @architecture Testing Layer 1 - Unit Test for IPC Service
 * @responsibility Validates IPC service functionality with security boundaries and performance monitoring
 * @dependencies Jest, Angular Testing Utilities, Custom Observability Framework, IPC Mocks
 * @integration_points Test observability system, performance monitoring, security validation
 * @testing_strategy Comprehensive unit testing with IPC security validation and circuit breaker testing
 * @governance Validates service against ipc-communication.md and security-boundaries.md specifications
 * 
 * Business Logic Summary:
 * - Tests secure IPC communication patterns with context isolation
 * - Validates channel whitelisting and payload size limits
 * - Ensures proper error handling and circuit breaker functionality
 * 
 * Architecture Integration:
 * - References ipc-communication.md#secure-ipc-patterns
 * - Validates security-boundaries.md#ipc-security-boundary
 * - Tests frontend-architecture.md#ipc-service-requirements
 * 
 * SPECIALIST DECISION: Alex Novak v3.0 - 2025-01-27
 * DECISION REFERENCE: DECISIONS.md#ipc-security-patterns
 * RATIONALE: IPC security is critical boundary - comprehensive testing required
 * CONSTRAINTS: All IPC channels must be whitelisted, all payloads validated
 * VALIDATION: Security violations logged, circuit breaker protects against abuse
 */

import { TestBed } from '@angular/core/testing';
import { NgZone } from '@angular/core';
import { of, throwError, Subject } from 'rxjs';

import { IPCService } from '../../../../ai-assistant/src/app/services/ipc.service';
import { TestObservabilityFramework } from '../../../utilities/test-framework/observability-framework';
import { PerformanceTestMonitor } from '../../../utilities/test-framework/performance-monitor';
import { SecurityTestValidator } from '../../../utilities/test-framework/security-validator';
import { ElectronMock } from '../../../utilities/mocks/electron-mocks';

/**
 * @class IPCServiceSpec
 * @description Comprehensive unit tests for IPCService with security and observability validation
 * @architecture_role Validates secure IPC communication patterns and defensive programming
 * @business_logic Tests IPC channel whitelisting, payload validation, circuit breaker patterns
 * @failure_modes Channel security bypass, payload size attacks, circuit breaker failure
 * @debugging_info Detailed IPC transaction logging with correlation IDs and security events
 * 
 * Defensive Programming Patterns:
 * - Channel whitelist validation testing
 * - Payload size limit enforcement testing  
 * - Circuit breaker activation and recovery testing
 * - Security violation detection and logging
 * 
 * Integration Boundaries:
 * - Electron IPC channel security validation
 * - Main process communication testing
 * - Error propagation and handling verification
 * - Performance monitoring integration
 * 
 * SECURITY BOUNDARY: IPC communication security testing
 * GOVERNANCE: All security controls must pass validation
 */
describe('IPCService', () => {
    let service: IPCService;
    let ngZone: NgZone;
    let electronMock: ElectronMock;
    let observabilityFramework: TestObservabilityFramework;
    let performanceMonitor: PerformanceTestMonitor;
    let securityValidator: SecurityTestValidator;
    
    // BUSINESS RULE: All IPC tests must run in complete security isolation
    // VALIDATION: No actual IPC calls, all channels mocked, security boundaries enforced
    // ERROR HANDLING: IPC security violations must be detected and logged
    // AUDIT TRAIL: All IPC operations logged with correlation IDs for security analysis
    
    beforeEach(async () => {
        // Setup comprehensive test observability
        observabilityFramework = new TestObservabilityFramework();
        performanceMonitor = new PerformanceTestMonitor();
        securityValidator = new SecurityTestValidator();
        
        const correlationId = observabilityFramework.generateCorrelationId();
        
        // ALEX'S 3AM TEST: Setup detailed debugging context for IPC testing
        await observabilityFramework.setupTestContext({
            testSuite: 'IPCService',
            testType: 'security_critical',
            correlationId,
            testStartTime: Date.now(),
            debugLevel: 'VERBOSE'
        });
        
        // Setup secure Electron IPC mock
        electronMock = new ElectronMock();
        electronMock.setupSecureIPCMocks();
        
        // Configure test module with security-focused setup
        await TestBed.configureTestingModule({
            providers: [
                IPCService,
                { provide: NgZone, useClass: NgZone },
                { provide: 'electronAPI', useValue: electronMock.getElectronAPI() }
            ]
        }).compileComponents();
        
        service = TestBed.inject(IPCService);
        ngZone = TestBed.inject(NgZone);
        
        // SARAH'S FRAMEWORK: Validate test isolation and security setup
        await observabilityFramework.validateSecureTestIsolation();
        await securityValidator.validateTestEnvironmentSecurity();
        
        // Verify service is properly initialized with security controls
        expect(service).toBeTruthy();
        expect(service.isSecurelyInitialized()).toBe(true);
    });
    
    afterEach(async () => {
        // ALEX'S 3AM TEST: Comprehensive test completion logging
        const testResults = {
            testResults: expect.getState(),
            performanceMetrics: performanceMonitor.getMetrics(),
            securityEvents: securityValidator.getSecurityEvents(),
            ipcTransactions: electronMock.getTransactionLog(),
            memoryUsage: (performance as any).memory?.usedJSHeapSize || 0
        };
        
        await observabilityFramework.recordTestCompletion(testResults);
        
        // Verify no memory leaks from IPC operations
        const memoryUsage = (performance as any).memory?.usedJSHeapSize || 0;
        const memoryBaseline = observabilityFramework.getMemoryBaseline();
        if (memoryUsage > memoryBaseline * 1.15) {  // Allow 15% increase
            fail(`IPC service memory leak detected: ${memoryUsage} bytes > ${memoryBaseline * 1.15} bytes`);
        }
        
        // Cleanup IPC mock resources
        await electronMock.cleanup();
    });
    
    /**
     * SERVICE INITIALIZATION TESTS
     * Tests secure service initialization with proper error handling
     */
    describe('Service Initialization', () => {
        
        it('should initialize with secure IPC configuration', async () => {
            // BUSINESS RULE: IPC service must initialize with all security controls active
            const startTime = performance.now();
            
            expect(service).toBeTruthy();
            expect(service).toBeInstanceOf(IPCService);
            expect(service.isSecurelyInitialized()).toBe(true);
            
            // Performance validation - initialization should be immediate
            const initTime = performance.now() - startTime;
            expect(initTime).toBeLessThan(50); // <50ms initialization
            
            // SARAH'S FRAMEWORK: Validate security controls are active
            expect(service.getChannelWhitelist()).toBeDefined();
            expect(service.getChannelWhitelist().size).toBeGreaterThan(0);
            expect(service.getMaxPayloadSize()).toBe(1024 * 1024); // 1MB limit
            expect(service.getCircuitBreakerState()).toBe('CLOSED');
            
            // SECURITY BOUNDARY: Verify security configuration
            expect(service.isChannelWhitelistEnabled()).toBe(true);
            expect(service.isPayloadValidationEnabled()).toBe(true);
            expect(service.isSecurityLoggingEnabled()).toBe(true);
            
            // AUDIT TRAIL: Log secure initialization
            await observabilityFramework.logServiceEvent({
                eventType: 'IPC_SERVICE_INITIALIZATION',
                status: 'SUCCESS',
                securityControls: {
                    channelWhitelistEnabled: true,
                    payloadValidationEnabled: true,
                    circuitBreakerEnabled: true
                },
                initializationTimeMs: initTime,
                correlationId: service.getCorrelationId()
            });
        });
        
        it('should handle initialization with missing Electron API gracefully', async () => {
            // SARAH'S FRAMEWORK: Test what breaks first - missing Electron dependency
            const serviceWithoutElectron = TestBed.configureTestingModule({
                providers: [
                    IPCService,
                    NgZone,
                    { provide: 'electronAPI', useValue: null }
                ]
            });
            
            expect(() => {
                TestBed.inject(IPCService);
            }).toThrowError('Electron API not available - running in browser mode');
            
            // ALEX'S 3AM TEST: Ensure error provides debugging information
            try {
                TestBed.inject(IPCService);
            } catch (error: any) {
                expect(error.message).toContain('Electron API not available');
                expect(error.debugContext).toBeDefined();
                expect(error.debugContext.environment).toBe('browser');
                expect(error.correlationId).toBeDefined();
            }
        });
    });
    
    /**
     * CHANNEL SECURITY TESTS
     * Tests IPC channel whitelisting and security validation
     */
    describe('Channel Security Validation', () => {
        
        it('should allow communication through whitelisted channels', async () => {
            // BUSINESS RULE: Only whitelisted IPC channels are allowed for communication
            const whitelistedChannel = 'agent:create';
            const testPayload = { agentType: 'code_assistant', config: { model: 'claude-3-sonnet' } };
            const expectedResponse = { success: true, agentId: 'test-agent-123' };
            
            // Configure mock response for whitelisted channel
            electronMock.setupChannelResponse(whitelistedChannel, expectedResponse);
            
            const startTime = performance.now();
            const result = await service.invoke(whitelistedChannel, testPayload);
            const responseTime = performance.now() - startTime;
            
            // Validate successful communication
            expect(result).toEqual(expectedResponse);
            expect(responseTime).toBeLessThan(100); // <100ms response time
            
            // SECURITY BOUNDARY: Verify channel was validated
            const securityEvents = securityValidator.getSecurityEvents();
            const channelValidationEvent = securityEvents.find(e => e.type === 'CHANNEL_VALIDATION');
            expect(channelValidationEvent).toBeDefined();
            expect(channelValidationEvent?.result).toBe('ALLOWED');
            
            // AUDIT TRAIL: Log successful IPC communication
            await observabilityFramework.logIPCTransaction({
                channel: whitelistedChannel,
                payloadSize: JSON.stringify(testPayload).length,
                responseSize: JSON.stringify(result).length,
                responseTimeMs: responseTime,
                securityValidation: 'PASSED',
                correlationId: service.getCorrelationId()
            });
        });
        
        it('should block communication through non-whitelisted channels', async () => {
            // SECURITY BOUNDARY: Non-whitelisted channels must be blocked
            const maliciousChannel = 'system:delete_files';
            const maliciousPayload = { path: '/etc/passwd' };
            
            // BUSINESS RULE: Non-whitelisted channels must be rejected with security logging
            await expectAsync(service.invoke(maliciousChannel, maliciousPayload)).toBeRejected();
            
            // Verify security violation was logged
            const securityEvents = securityValidator.getSecurityEvents();
            const violationEvent = securityEvents.find(e => e.type === 'CHANNEL_SECURITY_VIOLATION');
            expect(violationEvent).toBeDefined();
            expect(violationEvent?.details.attemptedChannel).toBe(maliciousChannel);
            expect(violationEvent?.severity).toBe('HIGH');
            
            // ALEX'S 3AM TEST: Ensure violation is traceable
            expect(violationEvent?.correlationId).toBeDefined();
            expect(violationEvent?.timestamp).toBeDefined();
            expect(violationEvent?.sourceLocation).toContain('IPCService');
            
            // Verify service security counters
            expect(service.getSecurityViolationCount()).toBe(1);
            expect(service.getLastSecurityViolation()).toEqual({
                type: 'UNAUTHORIZED_CHANNEL',
                channel: maliciousChannel,
                timestamp: jasmine.any(Number),
                correlationId: jasmine.any(String)
            });
        });
        
        it('should enforce payload size limits to prevent DoS attacks', async () => {
            // SECURITY BOUNDARY: Payload size limits prevent resource exhaustion attacks
            const whitelistedChannel = 'cache:set';
            const oversizedPayload = {
                key: 'test',
                value: 'x'.repeat(2 * 1024 * 1024) // 2MB payload (exceeds 1MB limit)
            };
            
            // BUSINESS RULE: Oversized payloads must be rejected to prevent DoS
            await expectAsync(service.invoke(whitelistedChannel, oversizedPayload)).toBeRejectedWithError(
                jasmine.stringMatching(/Payload size.*exceeds maximum/)
            );
            
            // Verify DoS protection logging
            const securityEvents = securityValidator.getSecurityEvents();
            const dosProtectionEvent = securityEvents.find(e => e.type === 'DOS_PROTECTION_ACTIVATED');
            expect(dosProtectionEvent).toBeDefined();
            expect(dosProtectionEvent?.details.payloadSize).toBe(JSON.stringify(oversizedPayload).length);
            expect(dosProtectionEvent?.details.maxAllowedSize).toBe(1024 * 1024);
            
            // AUDIT TRAIL: Log DoS protection activation
            await observabilityFramework.logSecurityEvent({
                eventType: 'IPC_DOS_PROTECTION',
                channel: whitelistedChannel,
                payloadSize: JSON.stringify(oversizedPayload).length,
                action: 'BLOCKED',
                correlationId: service.getCorrelationId()
            });
        });
    });
    
    /**
     * CIRCUIT BREAKER TESTS
     * Tests circuit breaker pattern implementation for IPC resilience
     */
    describe('Circuit Breaker Pattern Validation', () => {
        
        it('should activate circuit breaker after repeated IPC failures', async () => {
            // SARAH'S FRAMEWORK: Test circuit breaker - what breaks first under repeated failures?
            const testChannel = 'agent:query';
            const testPayload = { agentId: 'test-agent' };
            
            // Configure mock to simulate repeated failures
            electronMock.setupChannelFailure(testChannel, new Error('IPC communication failed'));
            
            // Execute multiple failing operations to trigger circuit breaker
            const failureThreshold = service.getCircuitBreakerThreshold(); // Should be 5
            let circuitBreakerActivated = false;
            
            for (let i = 0; i < failureThreshold + 1; i++) {
                try {
                    await service.invoke(testChannel, testPayload);
                } catch (error: any) {
                    if (error.message.includes('Circuit breaker is open')) {
                        circuitBreakerActivated = true;
                        break;
                    }
                }
            }
            
            // Verify circuit breaker activation
            expect(circuitBreakerActivated).toBe(true);
            expect(service.getCircuitBreakerState()).toBe('OPEN');
            expect(service.getFailureCount()).toBe(failureThreshold);
            
            // BUSINESS RULE: Circuit breaker should prevent further IPC calls
            await expectAsync(service.invoke(testChannel, testPayload)).toBeRejectedWithError(
                jasmine.stringMatching(/Circuit breaker is open/)
            );
            
            // ALEX'S 3AM TEST: Ensure circuit breaker state is debuggable
            const circuitBreakerStatus = service.getCircuitBreakerStatus();
            expect(circuitBreakerStatus.state).toBe('OPEN');
            expect(circuitBreakerStatus.failureCount).toBe(failureThreshold);
            expect(circuitBreakerStatus.lastFailureTime).toBeDefined();
            expect(circuitBreakerStatus.nextRetryTime).toBeDefined();
        });
        
        it('should recover circuit breaker after successful health check', async () => {
            // SARAH'S FRAMEWORK: Test Plan B - circuit breaker recovery mechanism
            const testChannel = 'system:health';
            const healthResponse = { status: 'healthy', timestamp: Date.now() };
            
            // First, activate circuit breaker
            service.activateCircuitBreakerForTesting(); // Test utility method
            expect(service.getCircuitBreakerState()).toBe('OPEN');
            
            // Configure mock to succeed for health check
            electronMock.setupChannelResponse(testChannel, healthResponse);
            
            // Wait for circuit breaker half-open state (simulated)
            service.transitionToHalfOpenForTesting();
            expect(service.getCircuitBreakerState()).toBe('HALF_OPEN');
            
            // Execute successful health check
            const result = await service.invoke(testChannel, {});
            
            // Verify circuit breaker recovery
            expect(result).toEqual(healthResponse);
            expect(service.getCircuitBreakerState()).toBe('CLOSED');
            expect(service.getFailureCount()).toBe(0);
            
            // AUDIT TRAIL: Log circuit breaker recovery
            await observabilityFramework.logServiceEvent({
                eventType: 'IPC_CIRCUIT_BREAKER_RECOVERY',
                previousState: 'HALF_OPEN',
                newState: 'CLOSED',
                recoveryTrigger: 'SUCCESSFUL_HEALTH_CHECK',
                correlationId: service.getCorrelationId()
            });
        });
    });
    
    /**
     * PERFORMANCE VALIDATION TESTS
     * Tests IPC performance requirements and monitoring
     */
    describe('Performance Requirements Validation', () => {
        
        it('should meet performance baselines for IPC operations', async () => {
            // PERFORMANCE BASELINE: IPC operations must complete within performance requirements
            const testChannel = 'cache:get';
            const testPayload = { key: 'performance_test_key' };
            const mockResponse = { value: 'cached_data', hit: true };
            
            electronMock.setupChannelResponse(testChannel, mockResponse);
            
            // Execute multiple IPC operations to test consistency
            const operationCount = 100;
            const maxAcceptableLatency = 50; // 50ms per operation
            const operationTimes: number[] = [];
            
            for (let i = 0; i < operationCount; i++) {
                const startTime = performance.now();
                await service.invoke(testChannel, { ...testPayload, iteration: i });
                const operationTime = performance.now() - startTime;
                operationTimes.push(operationTime);
            }
            
            // Analyze performance metrics
            const averageLatency = operationTimes.reduce((sum, time) => sum + time, 0) / operationCount;
            const maxLatency = Math.max(...operationTimes);
            const p95Latency = operationTimes.sort((a, b) => a - b)[Math.floor(operationCount * 0.95)];
            
            // Validate performance requirements
            expect(averageLatency).toBeLessThan(maxAcceptableLatency);
            expect(maxLatency).toBeLessThan(maxAcceptableLatency * 2); // Allow 2x for outliers
            expect(p95Latency).toBeLessThan(maxAcceptableLatency * 1.5); // 95th percentile
            
            // Record detailed performance metrics
            await performanceMonitor.recordPerformanceMetrics({
                operation: 'ipc_invoke_performance_test',
                operationCount,
                averageLatencyMs: averageLatency,
                maxLatencyMs: maxLatency,
                p95LatencyMs: p95Latency,
                payloadSize: JSON.stringify(testPayload).length,
                responseSize: JSON.stringify(mockResponse).length
            });
            
            // BUSINESS RULE: Performance metrics must be within SLA requirements
            expect(averageLatency).toBeLessThan(25); // Stricter requirement: <25ms average
            expect(p95Latency).toBeLessThan(40); // <40ms for 95% of requests
        });
        
        it('should handle concurrent IPC operations efficiently', async () => {
            // PERFORMANCE BASELINE: Concurrent IPC operations must not degrade performance significantly
            const testChannel = 'terminal:execute';
            const concurrentOperations = 20;
            const basePayload = { command: 'ls -la', timeout: 5000 };
            
            // Setup mock responses for concurrent operations
            electronMock.setupChannelResponse(testChannel, { 
                output: 'file1.txt\nfile2.txt\nfile3.txt',
                exitCode: 0,
                executionTime: 45
            });
            
            // Execute concurrent IPC operations
            const startTime = performance.now();
            const concurrentPromises = Array.from({ length: concurrentOperations }, (_, i) => 
                service.invoke(testChannel, { ...basePayload, id: i })
            );
            
            const results = await Promise.all(concurrentPromises);
            const totalTime = performance.now() - startTime;
            
            // Validate concurrent operation results
            expect(results).toHaveSize(concurrentOperations);
            results.forEach(result => {
                expect(result.exitCode).toBe(0);
                expect(result.output).toContain('file');
            });
            
            // Performance validation for concurrency
            const averageTimePerOperation = totalTime / concurrentOperations;
            expect(averageTimePerOperation).toBeLessThan(100); // <100ms per operation under concurrency
            
            // Memory usage validation during concurrency
            const memoryUsed = (performance as any).memory?.usedJSHeapSize || 0;
            const memoryBaseline = observabilityFramework.getMemoryBaseline();
            expect(memoryUsed).toBeLessThan(memoryBaseline * 1.3); // <30% memory increase
            
            // AUDIT TRAIL: Log concurrency performance
            await performanceMonitor.recordConcurrencyMetrics({
                operation: 'ipc_concurrent_operations',
                concurrentCount: concurrentOperations,
                totalExecutionTimeMs: totalTime,
                averageTimePerOperationMs: averageTimePerOperation,
                memoryUsageBytes: memoryUsed,
                allOperationsSuccessful: true
            });
        });
    });
    
    /**
     * ERROR HANDLING AND RECOVERY TESTS
     * Tests comprehensive error handling and recovery mechanisms
     */
    describe('Error Handling and Recovery', () => {
        
        it('should handle IPC timeout errors gracefully', async () => {
            // SARAH'S FRAMEWORK: Test timeout handling - what breaks when operations take too long?
            const testChannel = 'agent:create';
            const testPayload = { agentType: 'slow_agent' };
            const timeoutMs = 1000;
            
            // Configure mock to simulate timeout
            electronMock.setupChannelTimeout(testChannel, timeoutMs + 500); // Exceed timeout
            
            // BUSINESS RULE: IPC timeouts must be handled with proper error reporting
            const startTime = performance.now();
            await expectAsync(service.invokeWithTimeout(testChannel, testPayload, timeoutMs))
                .toBeRejectedWithError(jasmine.stringMatching(/IPC operation timed out/));
            const actualTime = performance.now() - startTime;
            
            // Verify timeout was enforced (with small margin for execution overhead)
            expect(actualTime).toBeGreaterThan(timeoutMs - 50);
            expect(actualTime).toBeLessThan(timeoutMs + 200);
            
            // Verify error context for debugging
            try {
                await service.invokeWithTimeout(testChannel, testPayload, timeoutMs);
            } catch (error: any) {
                // ALEX'S 3AM TEST: Ensure timeout errors are debuggable
                expect(error.timeoutMs).toBe(timeoutMs);
                expect(error.channel).toBe(testChannel);
                expect(error.correlationId).toBeDefined();
                expect(error.startTime).toBeDefined();
            }
            
            // Verify service state after timeout
            expect(service.getTimeoutCount()).toBe(1);
            expect(service.getLastTimeoutChannel()).toBe(testChannel);
        });
        
        it('should recover from main process restart scenarios', async () => {
            // SARAH'S FRAMEWORK: Test Plan B - recovery from main process failure
            const testChannel = 'system:status';
            const testPayload = { check: 'connectivity' };
            
            // Simulate main process restart by resetting IPC
            electronMock.simulateMainProcessRestart();
            
            // First attempt should fail due to disconnected IPC
            await expectAsync(service.invoke(testChannel, testPayload))
                .toBeRejectedWithError(jasmine.stringMatching(/IPC connection lost/));
            
            // Service should detect disconnection and attempt reconnection
            await service.attemptReconnection();
            
            // Configure mock for successful reconnection
            electronMock.restoreIPCConnection();
            electronMock.setupChannelResponse(testChannel, { status: 'connected', pid: 12345 });
            
            // Retry operation should succeed after reconnection
            const result = await service.invoke(testChannel, testPayload);
            expect(result).toEqual({ status: 'connected', pid: 12345 });
            
            // Verify recovery metrics
            expect(service.getReconnectionCount()).toBe(1);
            expect(service.isConnected()).toBe(true);
            expect(service.getConnectionState()).toBe('CONNECTED');
            
            // AUDIT TRAIL: Log IPC recovery
            await observabilityFramework.logServiceEvent({
                eventType: 'IPC_CONNECTION_RECOVERY',
                disconnectionReason: 'MAIN_PROCESS_RESTART',
                reconnectionTime: jasmine.any(Number),
                operationsFailedDuringOutage: 1,
                correlationId: service.getCorrelationId()
            });
        });
    });
    
    /**
     * MEMORY MANAGEMENT TESTS
     * Tests proper resource cleanup and memory management
     */
    describe('Memory Management and Resource Cleanup', () => {
        
        it('should properly clean up IPC listeners and prevent memory leaks', async () => {
            // BUSINESS RULE: IPC service must not leak memory through accumulated listeners
            const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
            const testChannel = 'websocket:message';
            
            // Create multiple IPC listeners to simulate heavy usage
            const listenerCount = 100;
            const listeners: (() => void)[] = [];
            
            for (let i = 0; i < listenerCount; i++) {
                const cleanup = service.on(`${testChannel}_${i}`, (data) => {
                    // Listener implementation
                    console.log(`Received data on channel ${i}:`, data);
                });
                listeners.push(cleanup);
            }
            
            // Verify listeners are registered
            expect(service.getActiveListenerCount()).toBe(listenerCount);
            
            // Clean up all listeners
            listeners.forEach(cleanup => cleanup());
            
            // Force garbage collection and measure memory
            if (global.gc) {
                global.gc();
            }
            await new Promise(resolve => setTimeout(resolve, 100)); // Allow GC time
            
            const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
            const memoryIncrease = finalMemory - initialMemory;
            
            // Verify memory cleanup (allow small increase for test overhead)
            expect(memoryIncrease).toBeLessThan(1024 * 1024); // <1MB increase
            expect(service.getActiveListenerCount()).toBe(0);
            
            // AUDIT TRAIL: Log memory management validation
            await observabilityFramework.logServiceEvent({
                eventType: 'IPC_MEMORY_CLEANUP_TEST',
                listenersCreated: listenerCount,
                listenersCleanedUp: listenerCount,
                initialMemoryBytes: initialMemory,
                finalMemoryBytes: finalMemory,
                memoryIncreaseBytes: memoryIncrease,
                cleanupSuccessful: service.getActiveListenerCount() === 0
            });
        });
        
        it('should handle service shutdown gracefully', async () => {
            // BUSINESS RULE: Service shutdown must clean up all resources without errors
            const testChannel = 'agent:terminate';
            
            // Setup active operations and listeners
            const pendingOperations = 3;
            const activeListeners = 5;
            
            // Create pending operations
            const operationPromises: Promise<any>[] = [];
            for (let i = 0; i < pendingOperations; i++) {
                electronMock.setupChannelDelay(testChannel, 2000); // 2 second delay
                operationPromises.push(service.invoke(testChannel, { agentId: `agent-${i}` }));
            }
            
            // Create active listeners
            for (let i = 0; i < activeListeners; i++) {
                service.on(`test_channel_${i}`, () => {}); // Create but don't clean up
            }
            
            // Verify service has active resources
            expect(service.getPendingOperationCount()).toBe(pendingOperations);
            expect(service.getActiveListenerCount()).toBe(activeListeners);
            
            // Initiate graceful shutdown
            const shutdownPromise = service.shutdown();
            
            // Verify shutdown process
            await expectAsync(shutdownPromise).toBeResolved();
            
            // Verify all resources were cleaned up
            expect(service.getPendingOperationCount()).toBe(0);
            expect(service.getActiveListenerCount()).toBe(0);
            expect(service.isShutdown()).toBe(true);
            
            // Verify pending operations were cancelled gracefully
            await expectAsync(Promise.all(operationPromises)).toBeRejected();
            
            // ALEX'S 3AM TEST: Ensure shutdown state is clear for debugging
            const shutdownStatus = service.getShutdownStatus();
            expect(shutdownStatus.shutdownInitiated).toBe(true);
            expect(shutdownStatus.resourcesCleanedUp).toBe(true);
            expect(shutdownStatus.shutdownDuration).toBeGreaterThan(0);
        });
    });
});