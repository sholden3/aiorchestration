/**
 * Windows Shell Detector Utility
 * Detects and validates available shells on Windows systems
 * Following single responsibility principle
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import { WindowsShellType, WindowsShellInfo, ShellFeatures } from '../types/pty.types';

const execAsync = promisify(exec);

export class WindowsShellDetector {
  private shellCache: Map<WindowsShellType, WindowsShellInfo> = new Map();
  private detectionComplete: boolean = false;

  /**
   * Common shell paths on Windows
   */
  private readonly SHELL_PATHS: Record<WindowsShellType, string[]> = {
    [WindowsShellType.POWERSHELL]: [
      'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
      'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe',
      'powershell.exe'
    ],
    [WindowsShellType.POWERSHELL_CORE]: [
      'C:\\Program Files\\PowerShell\\7\\pwsh.exe',
      'C:\\Program Files\\PowerShell\\6\\pwsh.exe',
      path.join(os.homedir(), 'AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe'),
      'pwsh.exe'
    ],
    [WindowsShellType.CMD]: [
      'C:\\Windows\\System32\\cmd.exe',
      'C:\\Windows\\SysWOW64\\cmd.exe',
      'cmd.exe'
    ],
    [WindowsShellType.WSL]: [
      'C:\\Windows\\System32\\wsl.exe',
      'wsl.exe'
    ],
    [WindowsShellType.GIT_BASH]: [
      'C:\\Program Files\\Git\\bin\\bash.exe',
      'C:\\Program Files (x86)\\Git\\bin\\bash.exe',
      path.join(os.homedir(), 'AppData\\Local\\Programs\\Git\\bin\\bash.exe'),
      'C:\\Users\\' + os.userInfo().username + '\\scoop\\apps\\git\\current\\usr\\bin\\bash.exe'
    ],
    [WindowsShellType.CYGWIN]: [
      'C:\\cygwin64\\bin\\bash.exe',
      'C:\\cygwin\\bin\\bash.exe'
    ]
  };

  /**
   * Detect optimal shell based on availability and features
   */
  public detectOptimalShell(): string {
    if (!this.detectionComplete) {
      this.detectAvailableShells();
    }

    // Priority order for optimal shell
    const priorityOrder: WindowsShellType[] = [
      WindowsShellType.POWERSHELL_CORE,
      WindowsShellType.POWERSHELL,
      WindowsShellType.GIT_BASH,
      WindowsShellType.WSL,
      WindowsShellType.CMD
    ];

    for (const shellType of priorityOrder) {
      const shellInfo = this.shellCache.get(shellType);
      if (shellInfo?.isAvailable) {
        return shellInfo.path;
      }
    }

    // Fallback to CMD as it's always available on Windows
    return 'cmd.exe';
  }

  /**
   * Detect all available shells on the system
   */
  public detectAvailableShells(): WindowsShellInfo[] {
    const availableShells: WindowsShellInfo[] = [];

    for (const [shellType, paths] of Object.entries(this.SHELL_PATHS)) {
      const shellInfo = this.detectShell(shellType as WindowsShellType, paths);
      if (shellInfo) {
        this.shellCache.set(shellType as WindowsShellType, shellInfo);
        if (shellInfo.isAvailable) {
          availableShells.push(shellInfo);
        }
      }
    }

    this.detectionComplete = true;
    return availableShells.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Detect a specific shell type
   */
  private detectShell(type: WindowsShellType, paths: string[]): WindowsShellInfo | null {
    for (const shellPath of paths) {
      if (this.isExecutableAvailable(shellPath)) {
        return {
          type,
          name: this.getShellName(type),
          path: shellPath,
          version: this.getShellVersion(shellPath, type),
          architecture: this.getArchitecture(),
          isAvailable: true,
          isDefault: false,
          priority: this.getShellPriority(type),
          features: this.getShellFeatures(type)
        };
      }
    }

    return {
      type,
      name: this.getShellName(type),
      path: '',
      isAvailable: false,
      isDefault: false,
      priority: 999,
      features: this.getShellFeatures(type)
    };
  }

  /**
   * Check if an executable exists and is accessible
   */
  private isExecutableAvailable(execPath: string): boolean {
    try {
      // Handle both absolute and PATH-based executables
      if (path.isAbsolute(execPath)) {
        return fs.existsSync(execPath) && fs.statSync(execPath).isFile();
      } else {
        // Check if it's in PATH
        const pathEnv = process.env.PATH || '';
        const pathDirs = pathEnv.split(path.delimiter);
        
        for (const dir of pathDirs) {
          const fullPath = path.join(dir, execPath);
          if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
            return true;
          }
        }
      }
    } catch (error) {
      // File doesn't exist or isn't accessible
    }
    return false;
  }

  /**
   * Get shell version synchronously (best effort)
   */
  private getShellVersion(shellPath: string, type: WindowsShellType): string | undefined {
    try {
      const versionCommands: Record<WindowsShellType, string> = {
        [WindowsShellType.POWERSHELL]: '$PSVersionTable.PSVersion.ToString()',
        [WindowsShellType.POWERSHELL_CORE]: '$PSVersionTable.PSVersion.ToString()',
        [WindowsShellType.CMD]: 'ver',
        [WindowsShellType.WSL]: '--version',
        [WindowsShellType.GIT_BASH]: '--version',
        [WindowsShellType.CYGWIN]: '--version'
      };

      // This would ideally be async, but for initialization we'll skip version detection
      // Version can be detected lazily when needed
      return undefined;
    } catch {
      return undefined;
    }
  }

  /**
   * Get shell display name
   */
  private getShellName(type: WindowsShellType): string {
    const names: Record<WindowsShellType, string> = {
      [WindowsShellType.POWERSHELL]: 'Windows PowerShell',
      [WindowsShellType.POWERSHELL_CORE]: 'PowerShell Core',
      [WindowsShellType.CMD]: 'Command Prompt',
      [WindowsShellType.WSL]: 'Windows Subsystem for Linux',
      [WindowsShellType.GIT_BASH]: 'Git Bash',
      [WindowsShellType.CYGWIN]: 'Cygwin'
    };
    return names[type] || type;
  }

  /**
   * Get shell priority (lower is better)
   */
  private getShellPriority(type: WindowsShellType): number {
    const priorities: Record<WindowsShellType, number> = {
      [WindowsShellType.POWERSHELL_CORE]: 1,
      [WindowsShellType.POWERSHELL]: 2,
      [WindowsShellType.GIT_BASH]: 3,
      [WindowsShellType.WSL]: 4,
      [WindowsShellType.CMD]: 5,
      [WindowsShellType.CYGWIN]: 6
    };
    return priorities[type] || 999;
  }

  /**
   * Get shell features and capabilities
   */
  private getShellFeatures(type: WindowsShellType): ShellFeatures {
    const features: Record<WindowsShellType, ShellFeatures> = {
      [WindowsShellType.POWERSHELL]: {
        supportsPowerShell: true,
        supportsAnsiColors: true,
        supportsUnicode: true,
        supportsConPTY: true,
        supportsResize: true
      },
      [WindowsShellType.POWERSHELL_CORE]: {
        supportsPowerShell: true,
        supportsAnsiColors: true,
        supportsUnicode: true,
        supportsConPTY: true,
        supportsResize: true
      },
      [WindowsShellType.CMD]: {
        supportsPowerShell: false,
        supportsAnsiColors: false,
        supportsUnicode: false,
        supportsConPTY: true,
        supportsResize: true
      },
      [WindowsShellType.WSL]: {
        supportsPowerShell: false,
        supportsAnsiColors: true,
        supportsUnicode: true,
        supportsConPTY: true,
        supportsResize: true
      },
      [WindowsShellType.GIT_BASH]: {
        supportsPowerShell: false,
        supportsAnsiColors: true,
        supportsUnicode: true,
        supportsConPTY: false,
        supportsResize: true
      },
      [WindowsShellType.CYGWIN]: {
        supportsPowerShell: false,
        supportsAnsiColors: true,
        supportsUnicode: true,
        supportsConPTY: false,
        supportsResize: true
      }
    };
    return features[type];
  }

  /**
   * Get system architecture
   */
  private getArchitecture(): string {
    return os.arch();
  }

  /**
   * Async version to get detailed shell version
   */
  public async getShellVersionAsync(shellPath: string, type: WindowsShellType): Promise<string> {
    try {
      let command: string;
      
      switch (type) {
        case WindowsShellType.POWERSHELL:
        case WindowsShellType.POWERSHELL_CORE:
          command = `"${shellPath}" -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"`;
          break;
        case WindowsShellType.CMD:
          command = `"${shellPath}" /c ver`;
          break;
        case WindowsShellType.WSL:
          command = `"${shellPath}" --version`;
          break;
        case WindowsShellType.GIT_BASH:
        case WindowsShellType.CYGWIN:
          command = `"${shellPath}" --version`;
          break;
        default:
          return 'unknown';
      }

      const { stdout } = await execAsync(command);
      return stdout.trim();
    } catch (error) {
      return 'unknown';
    }
  }

  /**
   * Validate if a shell path is valid and executable
   */
  public validateShell(shellPath: string): boolean {
    return this.isExecutableAvailable(shellPath);
  }

  /**
   * Get cached shell info
   */
  public getShellInfo(type: WindowsShellType): WindowsShellInfo | undefined {
    if (!this.detectionComplete) {
      this.detectAvailableShells();
    }
    return this.shellCache.get(type);
  }

  /**
   * Clear shell cache (useful for re-detection)
   */
  public clearCache(): void {
    this.shellCache.clear();
    this.detectionComplete = false;
  }
}