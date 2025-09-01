/**
 * @fileoverview Unit tests for SessionRecoveryService
 * @author Maya Patel v2.0 - QA & Testing Lead
 * @architecture Testing - Unit test suite for session recovery service
 * @business_logic Validates session persistence, recovery, cross-tab sync
 * @testing_strategy Mock storage APIs, simulate session lifecycle, test edge cases
 * @coverage_target 90% code coverage for SessionRecoveryService
 */

import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { SessionRecoveryService, SessionState } from './session-recovery.service';
import { take } from 'rxjs/operators';

describe('SessionRecoveryService', () => {
  let service: SessionRecoveryService;
  let mockBroadcastChannel: any;

  beforeEach(() => {
    // Clear storage
    localStorage.clear();
    sessionStorage.clear();

    // Mock BroadcastChannel
    mockBroadcastChannel = {
      postMessage: jest.fn(),
      close: jest.fn(),
      onmessage: null
    };

    jest.spyOn(window, 'BroadcastChannel' as any).mockReturnValue(mockBroadcastChannel);

    TestBed.configureTestingModule({
      providers: [SessionRecoveryService]
    });

    service = TestBed.inject(SessionRecoveryService);
  });

  afterEach(() => {
    service.destroy();
    localStorage.clear();
    sessionStorage.clear();
  });

  describe('Service Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should initialize broadcast channel', () => {
      expect(window.BroadcastChannel).toHaveBeenCalledWith('ai_assistant_session_sync');
    });

    it('should attempt to recover existing session on init', fakeAsync(() => {
      const existingSession = {
        sessionId: 'existing-session',
        timestamp: Date.now(),
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: {
          recoveryCount: 0
        }
      };

      localStorage.setItem('ai_assistant_session', JSON.stringify(existingSession));
      
      const newService = new SessionRecoveryService();
      tick(100);

      newService.getSessionState().pipe(take(1)).subscribe(state => {
        expect(state?.sessionId).toBe('existing-session');
      });
    }));

    it('should create new session if recovery fails', fakeAsync(() => {
      // No existing session in storage
      const newService = new SessionRecoveryService();
      tick(100);

      newService.getSessionState().pipe(take(1)).subscribe(state => {
        expect(state).toBeTruthy();
        expect(state?.sessionId).toMatch(/^sess_/);
      });
    }));
  });

  describe('Session Creation', () => {
    it('should create session with unique ID', () => {
      const session = service.createSession();
      
      expect(session.sessionId).toMatch(/^sess_[a-z0-9]+_[a-z0-9]+$/);
      expect(session.timestamp).toBeLessThanOrEqual(Date.now());
      expect(session.expiresAt).toBeGreaterThan(Date.now());
    });

    it('should create session with user ID', () => {
      const session = service.createSession('user123');
      
      expect(session.userId).toBe('user123');
    });

    it('should persist created session', () => {
      jest.spyOn(localStorage, 'setItem');
      
      service.createSession();
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'ai_assistant_session',
        expect.any(String)
      );
    });

    it('should broadcast session creation', () => {
      service.createSession();
      
      expect(mockBroadcastChannel.postMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'created',
          session: jasmine.any(String)
        })
      );
    });

    it('should update observable state', (done) => {
      service.getSessionState().pipe(take(1)).subscribe(state => {
        if (state) {
          expect(state.sessionId).toMatch(/^sess_/);
          done();
        }
      });

      service.createSession();
    });

    it('should generate correct metadata', () => {
      const session = service.createSession();
      
      expect(session.metadata.userAgent).toBe(navigator.userAgent);
      expect(session.metadata.platform).toBe(navigator.platform);
      expect(session.metadata.language).toBe(navigator.language);
      expect(session.metadata.recoveryCount).toBe(0);
      expect(session.metadata.created).toBeLessThanOrEqual(Date.now());
    });
  });

  describe('Session Data Management', () => {
    beforeEach(() => {
      service.createSession();
    });

    it('should update session data', () => {
      service.updateSessionData('key1', 'value1');
      
      const data = service.getSessionData('key1');
      expect(data).toBe('value1');
    });

    it('should handle complex data types', () => {
      const complexData = {
        array: [1, 2, 3],
        nested: { prop: 'value' }
      };
      
      service.updateSessionData('complex', complexData);
      
      const retrieved = service.getSessionData('complex');
      expect(retrieved).toEqual(complexData);
    });

    it('should update last active timestamp', fakeAsync(() => {
      const initialTime = Date.now();
      
      tick(100);
      service.updateSessionData('key', 'value');
      
      service.getSessionState().subscribe(state => {
        expect(state?.metadata.lastActive).toBeGreaterThan(initialTime);
      });
    }));

    it('should broadcast data updates', () => {
      mockBroadcastChannel.postMessage.calls.reset();
      
      service.updateSessionData('key', 'value');
      
      expect(mockBroadcastChannel.postMessage).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'updated' })
      );
    });

    it('should clear specific session data', () => {
      service.updateSessionData('key1', 'value1');
      service.updateSessionData('key2', 'value2');
      
      service.clearSessionData('key1');
      
      expect(service.getSessionData('key1')).toBeUndefined();
      expect(service.getSessionData('key2')).toBe('value2');
    });

    it('should clear all session data', () => {
      service.updateSessionData('key1', 'value1');
      service.updateSessionData('key2', 'value2');
      
      service.clearSessionData();
      
      expect(service.getSessionData('key1')).toBeUndefined();
      expect(service.getSessionData('key2')).toBeUndefined();
    });

    it('should handle updates with no active session', () => {
      service.destroySession();
      
      expect(() => service.updateSessionData('key', 'value')).not.toThrow();
    });
  });

  describe('Session Recovery', () => {
    it('should recover valid session from localStorage', async () => {
      const validSession = {
        sessionId: 'recovered-session',
        timestamp: Date.now() - 1000,
        expiresAt: Date.now() + 3600000,
        data: [['key', 'value']],
        metadata: {
          recoveryCount: 1,
          lastActive: Date.now()
        }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(validSession));
      
      const recovered = await service.recoverSession();
      
      expect(recovered?.sessionId).toBe('recovered-session');
      expect(recovered?.metadata.recoveryCount).toBe(2); // Incremented
    });

    it('should recover from backup storage if primary fails', async () => {
      const backupSession = {
        sessionId: 'backup-session',
        timestamp: Date.now() - 1000,
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      sessionStorage.setItem('ai_assistant_session_backup', JSON.stringify(backupSession));
      
      const recovered = await service.recoverSession();
      
      expect(recovered?.sessionId).toBe('backup-session');
    });

    it('should reject expired sessions', async () => {
      const expiredSession = {
        sessionId: 'expired-session',
        timestamp: Date.now() - 1000,
        expiresAt: Date.now() - 1000, // Expired
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(expiredSession));
      
      const recovered = await service.recoverSession();
      
      expect(recovered).toBeNull();
      expect(localStorage.getItem('ai_assistant_session')).toBeNull();
    });

    it('should reject sessions older than maxAge', async () => {
      const oldSession = {
        sessionId: 'old-session',
        timestamp: Date.now() - 25 * 60 * 60 * 1000, // 25 hours old
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(oldSession));
      
      const recovered = await service.recoverSession({ maxAge: 24 * 60 * 60 * 1000 });
      
      expect(recovered).toBeNull();
    });

    it('should validate with backend when required', async () => {
      const session = {
        sessionId: 'test-session',
        timestamp: Date.now(),
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(session));
      
      // Mock validation
      jest.spyOn(service as any, 'validateSessionWithBackend').mockResolvedValue(true);
      
      const recovered = await service.recoverSession({ validateWithBackend: true });
      
      expect((service as any).validateSessionWithBackend).toHaveBeenCalled();
      expect(recovered?.sessionId).toBe('test-session');
    });

    it('should handle validation failure based on preserveOnFailure', async () => {
      const session = {
        sessionId: 'invalid-session',
        timestamp: Date.now(),
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(session));
      
      jest.spyOn(service as any, 'validateSessionWithBackend').mockResolvedValue(false);
      
      // With preserveOnFailure = false
      const notPreserved = await service.recoverSession({
        validateWithBackend: true,
        preserveOnFailure: false
      });
      
      expect(notPreserved).toBeNull();
      expect(localStorage.getItem('ai_assistant_session')).toBeNull();
    });

    it('should handle corrupted session data', async () => {
      localStorage.setItem('ai_assistant_session', 'corrupted{data');
      
      const recovered = await service.recoverSession();
      
      expect(recovered).toBeNull();
    });

    it('should broadcast recovery', async () => {
      const session = {
        sessionId: 'test-session',
        timestamp: Date.now(),
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: { recoveryCount: 0 }
      };
      
      localStorage.setItem('ai_assistant_session', JSON.stringify(session));
      mockBroadcastChannel.postMessage.calls.reset();
      
      await service.recoverSession();
      
      expect(mockBroadcastChannel.postMessage).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'recovered' })
      );
    });
  });

  describe('Session Destruction', () => {
    it('should clear session state', () => {
      service.createSession();
      service.destroySession();
      
      expect(service.getCurrentSessionId()).toBeNull();
    });

    it('should clear storage', () => {
      service.createSession();
      
      jest.spyOn(localStorage, 'removeItem');
      jest.spyOn(sessionStorage, 'removeItem');
      
      service.destroySession();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('ai_assistant_session');
      expect(sessionStorage.removeItem).toHaveBeenCalledWith('ai_assistant_session_backup');
    });

    it('should broadcast destruction', () => {
      service.createSession();
      mockBroadcastChannel.postMessage.calls.reset();
      
      service.destroySession();
      
      expect(mockBroadcastChannel.postMessage).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'destroyed' })
      );
    });
  });

  describe('Storage Management', () => {
    it('should handle localStorage quota exceeded', () => {
      service.createSession();
      
      const mockError = new DOMException('QuotaExceededError', 'QuotaExceededError');
      
      jest.spyOn(localStorage, 'setItem').mockImplementation(() => { throw mockError; });
      jest.spyOn(service as any, 'cleanupOldSessions');
      
      service.updateSessionData('key', 'value');
      
      expect((service as any).cleanupOldSessions).toHaveBeenCalled();
    });

    it('should clean up expired sessions', () => {
      // Add expired sessions
      const expiredSession = {
        sessionId: 'expired',
        expiresAt: Date.now() - 1000
      };
      
      localStorage.setItem('ai_assistant_session_old', JSON.stringify(expiredSession));
      localStorage.setItem('ai_assistant_session_current', JSON.stringify({
        sessionId: 'current',
        expiresAt: Date.now() + 3600000
      }));
      
      jest.spyOn(localStorage, 'removeItem');
      
      (service as any).cleanupOldSessions();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('ai_assistant_session_old');
    });

    it('should remove corrupted session data during cleanup', () => {
      localStorage.setItem('ai_assistant_session_corrupted', 'invalid json');
      
      jest.spyOn(localStorage, 'removeItem');
      
      (service as any).cleanupOldSessions();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('ai_assistant_session_corrupted');
    });
  });

  describe('Cross-Tab Synchronization', () => {
    it('should handle broadcast messages from other tabs', () => {
      service.createSession('user1');
      
      const remoteSession = {
        sessionId: 'remote-session',
        userId: 'user2',
        timestamp: Date.now(),
        expiresAt: Date.now() + 3600000,
        data: [],
        metadata: {
          lastActive: Date.now() + 1000 // Newer
        }
      };
      
      mockBroadcastChannel.onmessage({
        data: {
          type: 'updated',
          session: JSON.stringify(remoteSession)
        }
      });
      
      service.getSessionState().subscribe(state => {
        expect(state?.sessionId).toBe('remote-session');
      });
    });

    it('should ignore older broadcast messages', () => {
      const currentSession = service.createSession();
      
      const olderSession = {
        ...currentSession,
        metadata: {
          ...currentSession.metadata,
          lastActive: currentSession.metadata.lastActive - 1000
        }
      };
      
      mockBroadcastChannel.onmessage({
        data: {
          type: 'updated',
          session: JSON.stringify(olderSession)
        }
      });
      
      service.getSessionState().subscribe(state => {
        expect(state?.sessionId).toBe(currentSession.sessionId);
      });
    });

    it('should handle destroyed session broadcast', () => {
      service.createSession();
      
      mockBroadcastChannel.onmessage({
        data: { type: 'destroyed' }
      });
      
      service.getSessionState().subscribe(state => {
        expect(state).toBeNull();
      });
    });

    it('should handle storage events for fallback sync', () => {
      const storageEvent = new StorageEvent('storage', {
        key: 'ai_assistant_session',
        newValue: JSON.stringify({
          sessionId: 'storage-sync',
          timestamp: Date.now(),
          data: []
        })
      });
      
      window.dispatchEvent(storageEvent);
      
      service.getSessionState().subscribe(state => {
        expect(state?.sessionId).toBe('storage-sync');
      });
    });
  });

  describe('Cleanup and Lifecycle', () => {
    it('should start cleanup interval', () => {
      jest.useFakeTimers();
      
      jest.spyOn(service as any, 'cleanupOldSessions');
      
      const newService = new SessionRecoveryService();
      
      jest.advanceTimersByTime(60 * 60 * 1000); // 1 hour
      
      expect((service as any).cleanupOldSessions).toHaveBeenCalled();
      
      jest.useRealTimers();
    });

    it('should clean up resources on destroy', () => {
      service.createSession();
      
      const cleanupInterval = (service as any).cleanupInterval;
      jest.spyOn(window, 'clearInterval');
      
      service.destroy();
      
      expect(window.clearInterval).toHaveBeenCalledWith(cleanupInterval);
      expect(mockBroadcastChannel.close).toHaveBeenCalled();
    });

    it('should persist session before destroy', () => {
      service.createSession();
      
      jest.spyOn(localStorage, 'setItem');
      
      service.destroy();
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'ai_assistant_session',
        expect.any(String)
      );
    });
  });

  describe('Utility Methods', () => {
    it('should generate unique session IDs', () => {
      const session1 = service.createSession();
      const session2 = service.createSession();
      
      expect(session1.sessionId).not.toBe(session2.sessionId);
    });

    it('should correctly serialize and deserialize sessions', () => {
      const original = service.createSession();
      original.data.set('key1', 'value1');
      original.data.set('key2', { nested: 'object' });
      
      const serialized = (service as any).serializeSession(original);
      const deserialized = (service as any).deserializeSession(serialized);
      
      expect(deserialized.sessionId).toBe(original.sessionId);
      expect(deserialized.data.get('key1')).toBe('value1');
      expect(deserialized.data.get('key2')).toEqual({ nested: 'object' });
    });

    it('should debounce persist operations', fakeAsync(() => {
      service.createSession();
      
      jest.spyOn(localStorage, 'setItem');
      
      // Multiple rapid updates
      service.updateSessionData('key1', 'value1');
      service.updateSessionData('key2', 'value2');
      service.updateSessionData('key3', 'value3');
      
      tick(500); // Less than debounce time
      expect(localStorage.setItem).not.toHaveBeenCalled();
      
      tick(600); // Complete debounce
      expect(localStorage.setItem).toHaveBeenCalledTimes(1);
    }));
  });
});