import { Injectable } from '@angular/core';

/**
 * FIX C1: Terminal Manager Service - Singleton to manage component-scoped terminal services
 * This service tracks and manages cleanup of all active terminal service instances
 * to prevent memory leaks from accumulated IPC listeners.
 * 
 * Architecture: Alex Novak
 * Pattern: Registry pattern for lifecycle management
 */
@Injectable({
  providedIn: 'root'  // This SHOULD be root - it's the manager, not the service
})
export class TerminalManagerService {
  private activeServices = new Set<any>();
  private cleanupCallbacks = new Map<any, () => void>();
  
  /**
   * Register a terminal service instance
   * @param service The terminal service instance to track
   */
  register(service: any): void {
    this.activeServices.add(service);
    console.log(`Terminal service registered. Active count: ${this.activeServices.size}`);
  }
  
  /**
   * Unregister a terminal service instance
   * @param service The terminal service instance to remove
   */
  unregister(service: any): void {
    this.activeServices.delete(service);
    this.cleanupCallbacks.delete(service);
    console.log(`Terminal service unregistered. Active count: ${this.activeServices.size}`);
  }
  
  /**
   * Register a cleanup callback for a service
   * @param service The service instance
   * @param callback The cleanup function to call
   */
  registerCleanup(service: any, callback: () => void): void {
    this.cleanupCallbacks.set(service, callback);
  }
  
  /**
   * Emergency cleanup - callable from global context or on app shutdown
   * This ensures all IPC listeners are properly removed
   */
  cleanup(): void {
    console.log(`Emergency cleanup initiated for ${this.activeServices.size} services`);
    
    this.activeServices.forEach(service => {
      try {
        // Call the service's cleanup method if it exists
        if (service.forceCleanup && typeof service.forceCleanup === 'function') {
          service.forceCleanup();
        }
        
        // Call any registered cleanup callback
        const callback = this.cleanupCallbacks.get(service);
        if (callback) {
          callback();
        }
      } catch (error) {
        console.error('Cleanup failed for service:', error);
      }
    });
    
    // Clear all tracking
    this.activeServices.clear();
    this.cleanupCallbacks.clear();
  }
  
  /**
   * Get count of active terminal services
   * Used for monitoring and debugging memory leaks
   */
  getActiveCount(): number {
    return this.activeServices.size;
  }
  
  /**
   * Get memory usage estimate
   * Each service with IPC listeners uses approximately 2-5MB
   */
  getMemoryEstimate(): string {
    const count = this.activeServices.size;
    const minMemory = count * 2;
    const maxMemory = count * 5;
    return `${minMemory}-${maxMemory} MB`;
  }
}