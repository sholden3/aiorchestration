/**
 * @fileoverview Test suite for C3 Process Coordination Fix
 * @author Sam Martinez v3.2.0 - Test Architecture
 * @testing_strategy Unit tests for backend coordination with retry logic
 * @references docs/fixes/C3-process-coordination-config.md
 * 
 * FIX C3: Process Coordination Tests
 * Tests the comprehensive backend startup coordination including:
 * - Retry logic with exponential backoff
 * - Already-running detection
 * - Correlation ID tracking
 * - Error handling and user notification
 */

const { describe, it, beforeEach, afterEach } = require('mocha');
const { expect } = require('chai');
const sinon = require('sinon');
const proxyquire = require('proxyquire');

describe('C3: Process Coordination Fix', () => {
    let AIAssistantApp;
    let app;
    let fetchStub;
    let spawnStub;
    let dialogStub;
    let consoleStub;
    
    beforeEach(() => {
        // Mock Electron modules
        const electronMock = {
            app: {
                requestSingleInstanceLock: sinon.stub().returns(true),
                whenReady: sinon.stub().resolves(),
                on: sinon.stub(),
                quit: sinon.stub()
            },
            BrowserWindow: sinon.stub().returns({
                loadURL: sinon.stub(),
                loadFile: sinon.stub(),
                show: sinon.stub(),
                on: sinon.stub(),
                once: sinon.stub(),
                webContents: {
                    send: sinon.stub(),
                    openDevTools: sinon.stub()
                },
                isDestroyed: sinon.stub().returns(false)
            }),
            ipcMain: {
                handle: sinon.stub(),
                on: sinon.stub()
            },
            dialog: {
                showErrorBox: sinon.stub()
            },
            shell: {
                openExternal: sinon.stub()
            }
        };
        
        // Mock child_process spawn
        spawnStub = sinon.stub();
        const childProcessMock = {
            spawn: spawnStub
        };
        
        // Mock fetch for health checks
        fetchStub = sinon.stub(global, 'fetch');
        
        // Mock console for correlation ID tracking
        consoleStub = {
            log: sinon.spy(),
            error: sinon.spy(),
            warn: sinon.spy()
        };
        
        dialogStub = electronMock.dialog;
        
        // Mock config
        const configMock = {
            backend: {
                port: 8000,
                host: '127.0.0.1',
                startup: {
                    maxRetries: 3,
                    retryDelay: 100, // Faster for tests
                    healthCheckTimeout: 200,
                    startupTimeout: 500
                }
            }
        };
        
        // Load the module with mocks
        const mainModule = proxyquire('../main.js', {
            'electron': electronMock,
            'child_process': childProcessMock,
            './config': configMock,
            './pty-fallback-system': sinon.stub().returns({
                createSession: sinon.stub(),
                writeToSession: sinon.stub(),
                killSession: sinon.stub(),
                getActiveSessions: sinon.stub().returns([])
            })
        });
        
        // Replace console with spy
        global.console = consoleStub;
    });
    
    afterEach(() => {
        // Restore stubs
        sinon.restore();
        if (global.fetch.restore) {
            global.fetch.restore();
        }
    });
    
    describe('Backend Already Running Detection', () => {
        it('should detect and connect to already-running backend', async function() {
            this.timeout(5000);
            
            // Mock successful health check
            fetchStub.resolves({
                ok: true,
                json: async () => ({ status: 'healthy' })
            });
            
            // Create app instance
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            
            // Trigger startup
            await app.startPythonBackend();
            
            // Verify correlation ID was generated
            const correlationIdCalls = consoleStub.log.getCalls()
                .filter(call => call.args[0].includes('startup-'));
            expect(correlationIdCalls).to.have.length.greaterThan(0);
            
            // Verify it detected already-running backend
            const alreadyRunningLog = consoleStub.log.getCalls()
                .find(call => call.args[0].includes('Backend already running'));
            expect(alreadyRunningLog).to.exist;
            
            // Verify spawn was NOT called
            expect(spawnStub.called).to.be.false;
            
            // Verify notification was sent
            const notificationLog = consoleStub.log.getCalls()
                .find(call => call.args[0].includes('connected'));
            expect(notificationLog).to.exist;
        });
        
        it('should use correlation IDs for all operations', async function() {
            fetchStub.resolves({
                ok: true,
                json: async () => ({ status: 'healthy' })
            });
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            await app.startPythonBackend();
            
            // Extract correlation ID from logs
            const correlationMatch = consoleStub.log.getCalls()
                .find(call => call.args[0].match(/\[startup-\d+\]/));
            expect(correlationMatch).to.exist;
            
            const correlationId = correlationMatch.args[0].match(/\[(startup-\d+)\]/)[1];
            
            // Verify same correlation ID used throughout
            const correlatedLogs = consoleStub.log.getCalls()
                .filter(call => call.args[0].includes(correlationId));
            expect(correlatedLogs.length).to.be.greaterThan(1);
        });
    });
    
    describe('Retry Logic with Exponential Backoff', () => {
        it('should retry 3 times with exponential backoff on failure', async function() {
            this.timeout(10000);
            
            // Mock spawn to fail
            const mockProcess = {
                stdout: { on: sinon.stub() },
                stderr: { on: sinon.stub() },
                on: sinon.stub(),
                kill: sinon.stub()
            };
            spawnStub.returns(mockProcess);
            
            // Mock health check to fail
            fetchStub.rejects(new Error('Connection refused'));
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            
            const startTime = Date.now();
            const result = await app.startPythonBackend();
            const duration = Date.now() - startTime;
            
            // Should have tried 3 times
            expect(spawnStub.callCount).to.equal(3);
            
            // Verify exponential backoff (100ms, 200ms, 400ms)
            // Total minimum time should be around 700ms
            expect(duration).to.be.greaterThan(600);
            
            // Verify process was killed after each attempt
            expect(mockProcess.kill.callCount).to.equal(3);
            
            // Should show error dialog
            expect(dialogStub.showErrorBox.called).to.be.true;
            
            // Should return false
            expect(result).to.be.false;
        });
        
        it('should succeed on second attempt and stop retrying', async function() {
            this.timeout(5000);
            
            const mockProcess = {
                stdout: { on: sinon.stub() },
                stderr: { on: sinon.stub() },
                on: sinon.stub(),
                kill: sinon.stub()
            };
            spawnStub.returns(mockProcess);
            
            // Fail first health check, succeed on second
            fetchStub.onFirstCall().rejects(new Error('Not ready'));
            fetchStub.onSecondCall().rejects(new Error('Still not ready'));
            fetchStub.resolves({
                ok: true,
                json: async () => ({ status: 'healthy' })
            });
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            
            const result = await app.startPythonBackend();
            
            // Should have succeeded
            expect(result).to.be.true;
            
            // Should have tried spawning twice
            expect(spawnStub.callCount).to.equal(2);
            
            // Should NOT show error dialog
            expect(dialogStub.showErrorBox.called).to.be.false;
        });
    });
    
    describe('Python Command Fallback', () => {
        it('should try multiple Python commands until one works', async function() {
            this.timeout(5000);
            
            const mockProcess = {
                stdout: { on: sinon.stub() },
                stderr: { on: sinon.stub() },
                on: sinon.stub(),
                kill: sinon.stub()
            };
            
            // First two commands fail, third succeeds
            spawnStub.onCall(0).throws(new Error('python not found'));
            spawnStub.onCall(1).throws(new Error('python3 not found'));
            spawnStub.onCall(2).returns(mockProcess);
            
            // Mock successful health check after spawn
            fetchStub.resolves({
                ok: true,
                json: async () => ({ status: 'healthy' })
            });
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            
            const result = await app.startPythonBackend();
            
            expect(result).to.be.true;
            expect(spawnStub.callCount).to.equal(3);
            
            // Verify it tried correct commands
            expect(spawnStub.getCall(0).args[0]).to.equal('python');
            expect(spawnStub.getCall(1).args[0]).to.equal('python3');
            expect(spawnStub.getCall(2).args[0]).to.equal('py');
        });
    });
    
    describe('Error Dialog and User Communication', () => {
        it('should show detailed error dialog on complete failure', async function() {
            this.timeout(5000);
            
            fetchStub.rejects(new Error('Connection failed'));
            spawnStub.returns({
                stdout: { on: sinon.stub() },
                stderr: { on: sinon.stub() },
                on: sinon.stub(),
                kill: sinon.stub()
            });
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            
            await app.startPythonBackend();
            
            expect(dialogStub.showErrorBox.called).to.be.true;
            
            const errorCall = dialogStub.showErrorBox.getCall(0);
            expect(errorCall.args[0]).to.equal('Backend Startup Failed');
            
            // Should include correlation ID
            expect(errorCall.args[1]).to.include('Correlation ID: startup-');
            
            // Should include possible causes
            expect(errorCall.args[1]).to.include('Python 3.10+ not installed');
            expect(errorCall.args[1]).to.include('Port 8000 already in use');
        });
    });
    
    describe('Backend Status Notifications', () => {
        it('should notify renderer of backend status changes', async function() {
            this.timeout(5000);
            
            // Create mock window
            const mockWindow = {
                webContents: {
                    send: sinon.stub()
                },
                isDestroyed: sinon.stub().returns(false)
            };
            
            fetchStub.resolves({
                ok: true,
                json: async () => ({ status: 'healthy' })
            });
            
            const { AIAssistantApp } = require('../main.js');
            app = new AIAssistantApp();
            app.mainWindow = mockWindow;
            
            await app.startPythonBackend();
            
            // Should have sent status update
            expect(mockWindow.webContents.send.called).to.be.true;
            
            const statusCall = mockWindow.webContents.send.getCall(0);
            expect(statusCall.args[0]).to.equal('backend-status');
            expect(statusCall.args[1]).to.deep.include({
                status: 'connected',
                port: 8000
            });
        });
    });
});

describe('C3: Configuration Management', () => {
    it('should use centralized configuration', () => {
        const config = require('../config');
        
        expect(config.backend.port).to.equal(8000);
        expect(config.backend.host).to.equal('127.0.0.1');
        expect(config.backend.startup.maxRetries).to.equal(3);
        expect(config.backend.startup.retryDelay).to.equal(2000);
    });
    
    it('should respect environment variable overrides', () => {
        process.env.BACKEND_PORT = '9000';
        
        // Clear require cache to reload config
        delete require.cache[require.resolve('../config')];
        const config = require('../config');
        
        expect(config.backend.port).to.equal('9000');
        
        // Cleanup
        delete process.env.BACKEND_PORT;
    });
});