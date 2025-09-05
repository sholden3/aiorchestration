import { Component, OnInit } from '@angular/core';

export interface LayoutPanel {
  id: string;
  title: string;
  type: 'terminal' | 'dashboard' | 'editor' | 'chat' | 'logs';
  visible: boolean;
  minimized: boolean;
  position: 'main' | 'bottom' | 'right' | 'left';
  size?: number; // percentage or pixels
}

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent implements OnInit {
  panels: LayoutPanel[] = [
    {
      id: 'main-dashboard',
      title: 'AI Orchestration Dashboard',
      type: 'dashboard',
      visible: true,
      minimized: false,
      position: 'main'
    },
    {
      id: 'terminal-1',
      title: 'Terminal',
      type: 'terminal',
      visible: true,
      minimized: false,
      position: 'bottom',
      size: 30 // 30% of height
    },
    {
      id: 'chat-assistant',
      title: 'AI Assistant',
      type: 'chat',
      visible: true,
      minimized: false,
      position: 'right',
      size: 350 // 350px width
    }
  ];

  activePanel: string = 'main-dashboard';
  resizing: boolean = false;
  
  constructor() {}

  ngOnInit(): void {
    this.loadLayoutPreferences();
  }

  togglePanel(panelId: string): void {
    const panel = this.panels.find(p => p.id === panelId);
    if (panel) {
      panel.visible = !panel.visible;
      this.saveLayoutPreferences();
    }
  }

  minimizePanel(panelId: string): void {
    const panel = this.panels.find(p => p.id === panelId);
    if (panel) {
      panel.minimized = !panel.minimized;
      this.saveLayoutPreferences();
    }
  }

  setActivePanel(panelId: string): void {
    this.activePanel = panelId;
  }

  onResize(panelId: string, newSize: number): void {
    const panel = this.panels.find(p => p.id === panelId);
    if (panel) {
      panel.size = newSize;
      this.saveLayoutPreferences();
    }
  }

  private loadLayoutPreferences(): void {
    const saved = localStorage.getItem('ai-assistant-layout');
    if (saved) {
      try {
        const savedPanels = JSON.parse(saved);
        this.panels = savedPanels;
      } catch (e) {
        console.error('Failed to load layout preferences', e);
      }
    }
  }

  private saveLayoutPreferences(): void {
    localStorage.setItem('ai-assistant-layout', JSON.stringify(this.panels));
  }

  // Quick access methods
  showTerminal(): void {
    const terminal = this.panels.find(p => p.type === 'terminal');
    if (terminal) {
      terminal.visible = true;
      terminal.minimized = false;
      this.activePanel = terminal.id;
    }
  }

  showDashboard(): void {
    const dashboard = this.panels.find(p => p.type === 'dashboard');
    if (dashboard) {
      dashboard.visible = true;
      dashboard.minimized = false;
      this.activePanel = dashboard.id;
    }
  }

  createNewTerminal(): void {
    const terminalCount = this.panels.filter(p => p.type === 'terminal').length;
    this.panels.push({
      id: `terminal-${terminalCount + 1}`,
      title: `Terminal ${terminalCount + 1}`,
      type: 'terminal',
      visible: true,
      minimized: false,
      position: 'bottom',
      size: 30
    });
  }

  // Helper methods for template
  hasLeftPanel(): boolean {
    return this.panels.some(p => p.position === 'left' && p.visible);
  }

  hasBottomPanel(): boolean {
    return this.panels.some(p => p.position === 'bottom' && p.visible);
  }

  hasRightPanel(): boolean {
    return this.panels.some(p => p.position === 'right' && p.visible);
  }

  getBottomPanelSize(): number {
    const panel = this.panels.find(p => p.position === 'bottom');
    return panel?.size || 30;
  }

  getRightPanelSize(): number {
    const panel = this.panels.find(p => p.position === 'right');
    return panel?.size || 350;
  }

  getMainPanels(): LayoutPanel[] {
    return this.panels.filter(p => p.position === 'main' && p.visible && !p.minimized);
  }

  getTerminalPanels(): LayoutPanel[] {
    return this.panels.filter(p => p.type === 'terminal');
  }

  isActiveTerminal(panel: LayoutPanel): boolean {
    return panel.type === 'terminal' && panel.visible && this.activePanel === panel.id;
  }
}