/**
 * Windows Process Manager Utility
 * Manages process lifecycle and monitoring on Windows
 * Following single responsibility and dependency inversion principles
 */

import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import * as os from 'os';

const execAsync = promisify(exec);

export interface ProcessInfo {
  pid: number;
  name: string;
  ppid?: number;
  memory?: number;
  cpu?: number;
  startTime?: Date;
  commandLine?: string;
}

export interface ProcessTreeNode {
  process: ProcessInfo;
  children: ProcessTreeNode[];
}

export class WindowsProcessManager {
  private monitoringIntervals: Map<string, NodeJS.Timeout> = new Map();
  private processCache: Map<number, ProcessInfo> = new Map();

  /**
   * Terminate a process and all its children (process tree)
   */
  public async terminateProcessTree(pid: number, force: boolean = false): Promise<boolean> {
    try {
      if (os.platform() !== 'win32') {
        // Non-Windows fallback
        process.kill(pid, force ? 'SIGKILL' : 'SIGTERM');
        return true;
      }

      // Windows-specific: Use taskkill to terminate process tree
      const flag = force ? '/F' : '';
      const command = `taskkill /PID ${pid} /T ${flag}`.trim();
      
      await execAsync(command);
      this.processCache.delete(pid);
      return true;
    } catch (error) {
      console.error(`Failed to terminate process ${pid}:`, error);
      return false;
    }
  }

  /**
   * Get information about a specific process
   */
  public async getProcessInfo(pid: number): Promise<ProcessInfo | null> {
    try {
      // Check cache first
      if (this.processCache.has(pid)) {
        return this.processCache.get(pid)!;
      }

      if (os.platform() !== 'win32') {
        // Non-Windows: Basic process info
        return {
          pid,
          name: 'unknown'
        };
      }

      // Windows: Use WMIC to get detailed process info
      const command = `wmic process where ProcessId=${pid} get Name,ParentProcessId,WorkingSetSize,CommandLine,CreationDate /format:csv`;
      const { stdout } = await execAsync(command);
      
      const lines = stdout.trim().split('\n').filter(line => line.trim());
      if (lines.length < 2) {
        return null;
      }

      // Parse CSV output
      const headers = lines[lines.length - 2].split(',');
      const values = lines[lines.length - 1].split(',');
      
      const info: ProcessInfo = {
        pid,
        name: this.getCSVValue(headers, values, 'Name') || 'unknown',
        ppid: parseInt(this.getCSVValue(headers, values, 'ParentProcessId') || '0'),
        memory: parseInt(this.getCSVValue(headers, values, 'WorkingSetSize') || '0'),
        commandLine: this.getCSVValue(headers, values, 'CommandLine')
      };

      // Cache the result
      this.processCache.set(pid, info);
      return info;
    } catch (error) {
      console.error(`Failed to get process info for PID ${pid}:`, error);
      return null;
    }
  }

  /**
   * Get all child processes of a parent process
   */
  public async getChildProcesses(parentPid: number): Promise<ProcessInfo[]> {
    try {
      if (os.platform() !== 'win32') {
        // Non-Windows: Limited support
        return [];
      }

      const command = `wmic process where ParentProcessId=${parentPid} get ProcessId,Name /format:csv`;
      const { stdout } = await execAsync(command);
      
      const lines = stdout.trim().split('\n').filter(line => line.trim());
      if (lines.length < 2) {
        return [];
      }

      const children: ProcessInfo[] = [];
      const headers = lines[0].split(',');
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        if (values.length >= 2) {
          const pid = parseInt(this.getCSVValue(headers, values, 'ProcessId') || '0');
          const name = this.getCSVValue(headers, values, 'Name') || 'unknown';
          
          if (pid > 0) {
            children.push({
              pid,
              name,
              ppid: parentPid
            });
          }
        }
      }

      return children;
    } catch (error) {
      console.error(`Failed to get child processes for PID ${parentPid}:`, error);
      return [];
    }
  }

  /**
   * Build a complete process tree starting from a root PID
   */
  public async getProcessTree(rootPid: number): Promise<ProcessTreeNode | null> {
    const rootInfo = await this.getProcessInfo(rootPid);
    if (!rootInfo) {
      return null;
    }

    const node: ProcessTreeNode = {
      process: rootInfo,
      children: []
    };

    const children = await this.getChildProcesses(rootPid);
    for (const child of children) {
      const childNode = await this.getProcessTree(child.pid);
      if (childNode) {
        node.children.push(childNode);
      }
    }

    return node;
  }

  /**
   * Monitor a process and call callback when it exits
   */
  public monitorProcess(
    pid: number,
    callback: (exitCode: number | null) => void,
    pollInterval: number = 1000
  ): string {
    const monitorId = `monitor-${pid}-${Date.now()}`;
    
    const checkProcess = async () => {
      try {
        if (os.platform() === 'win32') {
          // Windows: Check if process exists
          const command = `tasklist /FI "PID eq ${pid}" /NH`;
          const { stdout } = await execAsync(command);
          
          if (!stdout.includes(pid.toString())) {
            // Process no longer exists
            this.stopMonitoring(monitorId);
            callback(null);
          }
        } else {
          // Non-Windows: Use process.kill with signal 0
          try {
            process.kill(pid, 0);
          } catch {
            // Process doesn't exist
            this.stopMonitoring(monitorId);
            callback(null);
          }
        }
      } catch (error) {
        console.error(`Error monitoring process ${pid}:`, error);
        this.stopMonitoring(monitorId);
        callback(null);
      }
    };

    const interval = setInterval(checkProcess, pollInterval);
    this.monitoringIntervals.set(monitorId, interval);
    
    // Initial check
    checkProcess();
    
    return monitorId;
  }

  /**
   * Stop monitoring a process
   */
  public stopMonitoring(monitorId: string): void {
    const interval = this.monitoringIntervals.get(monitorId);
    if (interval) {
      clearInterval(interval);
      this.monitoringIntervals.delete(monitorId);
    }
  }

  /**
   * Stop all monitoring
   */
  public stopAllMonitoring(): void {
    for (const interval of this.monitoringIntervals.values()) {
      clearInterval(interval);
    }
    this.monitoringIntervals.clear();
  }

  /**
   * Check if a process is running
   */
  public async isProcessRunning(pid: number): Promise<boolean> {
    try {
      if (os.platform() === 'win32') {
        const command = `tasklist /FI "PID eq ${pid}" /NH`;
        const { stdout } = await execAsync(command);
        return stdout.includes(pid.toString());
      } else {
        try {
          process.kill(pid, 0);
          return true;
        } catch {
          return false;
        }
      }
    } catch {
      return false;
    }
  }

  /**
   * Get memory usage of a process
   */
  public async getProcessMemory(pid: number): Promise<number> {
    try {
      const info = await this.getProcessInfo(pid);
      return info?.memory || 0;
    } catch {
      return 0;
    }
  }

  /**
   * Kill a single process
   */
  public async killProcess(pid: number, signal: string = 'SIGTERM'): Promise<boolean> {
    try {
      if (os.platform() === 'win32') {
        const force = signal === 'SIGKILL' ? '/F' : '';
        const command = `taskkill /PID ${pid} ${force}`.trim();
        await execAsync(command);
      } else {
        process.kill(pid, signal);
      }
      this.processCache.delete(pid);
      return true;
    } catch (error) {
      console.error(`Failed to kill process ${pid}:`, error);
      return false;
    }
  }

  /**
   * Clear process cache
   */
  public clearCache(): void {
    this.processCache.clear();
  }

  /**
   * Helper to parse CSV values from WMIC output
   */
  private getCSVValue(headers: string[], values: string[], headerName: string): string | undefined {
    const index = headers.findIndex(h => h.trim() === headerName);
    if (index >= 0 && index < values.length) {
      return values[index].trim();
    }
    return undefined;
  }

  /**
   * Cleanup resources
   */
  public cleanup(): void {
    this.stopAllMonitoring();
    this.clearCache();
  }
}