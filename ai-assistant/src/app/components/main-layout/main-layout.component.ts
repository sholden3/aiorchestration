import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { RulesService } from '../../services/rules.service';
import { TerminalService } from '../../services/terminal.service';
import { OrchestrationService } from '../../services/orchestration.service';
import { TerminalComponent } from '../terminal/terminal.component';

export interface Project {
  name: string;
  percentage: number;
  status: string;
  phase: string;
}

export interface Update {
  icon: string;
  title: string;
  description: string;
  time: string;
  color: string;
}

export interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.scss']
})
export class MainLayoutComponent implements OnInit {
  @ViewChild('chatInput') chatInput!: any;
  @ViewChild('terminalComponent') terminalComponent!: TerminalComponent;

  // Layout state
  sidebarOpen = true;
  aiAssistantOpen = false;
  terminalExpanded = false;
  currentPage = 'Dashboard';
  
  // Menu items
  menuItems = [
    { icon: 'dashboard', label: 'Dashboard', route: 'dashboard' },
    { icon: 'smart_toy', label: 'AI Agents', route: 'agents' },
    { icon: 'bar_chart', label: 'Reporting', route: 'reporting' },
    { icon: 'auto_awesome', label: 'AI Orchestration', route: 'orchestration' },
    { icon: 'work', label: 'Projects', route: 'projects' },
    { icon: 'library_books', label: 'Templates', route: 'templates' },
    { icon: 'lightbulb', label: 'Best Practices', route: 'practices' },
    { icon: 'gavel', label: 'Rules', route: 'rules' },
    { icon: 'shield', label: 'Governance', route: 'governance' },
    { icon: 'widgets', label: 'Plugins', route: 'plugins' }
  ];
  
  activeMenuItem = 'dashboard';
  
  // Projects data
  projects: Project[] = [
    { name: 'Customer Support AI', percentage: 78, status: 'Implementation Phase - Testing in progress', phase: 'implementation' },
    { name: 'Data Processing Pipeline', percentage: 45, status: 'Development Phase - API integration', phase: 'development' },
    { name: 'Predictive Analytics Model', percentage: 92, status: 'Deployment Phase - Final validation', phase: 'deployment' },
    { name: 'Voice Recognition System', percentage: 23, status: 'Planning Phase - Requirements gathering', phase: 'planning' }
  ];
  
  // Updates
  updates: Update[] = [
    { 
      icon: 'system_update', 
      title: 'Version 2.4.1 Available', 
      description: 'New AI model integration and improved performance monitoring capabilities.',
      time: '2 hours ago',
      color: '#4ecdc4'
    },
    { 
      icon: 'new_releases', 
      title: 'Enhanced Templates Released', 
      description: '10 new project templates for common AI orchestration patterns now available.',
      time: '1 day ago',
      color: '#667eea'
    },
    { 
      icon: 'security', 
      title: 'Security Patch Applied', 
      description: 'Enhanced governance controls and audit logging improvements.',
      time: '3 days ago',
      color: '#764ba2'
    }
  ];
  
  // Chat
  chatMessages: ChatMessage[] = [
    { type: 'ai', content: 'Hello! I\'m here to help you with your AI orchestration projects. What can I assist you with today?', timestamp: new Date() },
    { type: 'user', content: 'Can you help me optimize the Customer Support AI project?', timestamp: new Date() },
    { type: 'ai', content: 'Absolutely! I can see your Customer Support AI is at 78% completion. Let me analyze the current implementation and suggest optimizations for the testing phase.', timestamp: new Date() }
  ];
  
  chatInputValue = '';
  
  // Terminal
  terminals = [
    { id: 'terminal-1', name: 'Terminal 1', active: true },
    { id: 'ai-logs', name: 'AI Logs', active: false }
  ];
  
  activeTerminal = 'terminal-1';
  
  // Status indicators
  backendStatus = 'running';
  governanceActive = true;
  personasActive = true;
  
  // User info
  userName = 'John Smith';
  userInitials = 'JS';

  constructor(
    private router: Router,
    private rulesService: RulesService,
    private terminalService: TerminalService,
    private orchestrationService: OrchestrationService
  ) {}

  ngOnInit(): void {
    this.checkScreenSize();
    this.loadDashboardData();
  }
  
  checkScreenSize(): void {
    this.sidebarOpen = window.innerWidth > 768;
  }
  
  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }
  
  toggleAIAssistant(): void {
    this.aiAssistantOpen = !this.aiAssistantOpen;
  }
  
  toggleTerminalExpansion(): void {
    this.terminalExpanded = !this.terminalExpanded;
  }
  
  selectMenuItem(route: string): void {
    this.activeMenuItem = route;
    const item = this.menuItems.find(m => m.route === route);
    if (item) {
      this.currentPage = item.label;
    }
    
    // Navigate to the route
    this.router.navigate([route]);
    
    // On mobile, close sidebar after selection
    if (window.innerWidth <= 768) {
      this.sidebarOpen = false;
    }
  }
  
  sendChatMessage(): void {
    if (!this.chatInputValue.trim()) return;
    
    // Add user message
    this.chatMessages.push({
      type: 'user',
      content: this.chatInputValue,
      timestamp: new Date()
    });
    
    const userMessage = this.chatInputValue;
    this.chatInputValue = '';
    
    // Simulate AI response
    setTimeout(() => {
      this.chatMessages.push({
        type: 'ai',
        content: `I understand you're asking about "${userMessage}". Let me help you with that based on your current projects and system status.`,
        timestamp: new Date()
      });
      this.scrollChatToBottom();
    }, 1000);
    
    this.scrollChatToBottom();
  }
  
  executeTerminalCommand(): void {
    // Terminal component handles its own input
  }
  
  clearTerminal(): void {
    if (this.terminalComponent) {
      this.terminalComponent.clear();
    }
  }
  
  addTerminal(): void {
    const newId = `terminal-${this.terminals.length + 1}`;
    this.terminals.push({
      id: newId,
      name: `Terminal ${this.terminals.length + 1}`,
      active: false
    });
    this.selectTerminal(newId);
  }
  
  selectTerminal(id: string): void {
    this.terminals.forEach(t => t.active = false);
    const terminal = this.terminals.find(t => t.id === id);
    if (terminal) {
      terminal.active = true;
      this.activeTerminal = id;
    }
  }
  
  closeTerminal(id: string): void {
    if (this.terminals.length <= 1) return;
    
    const index = this.terminals.findIndex(t => t.id === id);
    if (index > -1) {
      this.terminals.splice(index, 1);
      if (this.activeTerminal === id && this.terminals.length > 0) {
        this.selectTerminal(this.terminals[0].id);
      }
    }
  }
  
  openSettings(): void {
    // TODO: Implement settings dialog
    console.log('Settings clicked');
  }
  
  onStatusClick(status: string): void {
    console.log(`Status clicked: ${status}`);
    // TODO: Implement status panel
  }
  
  private scrollChatToBottom(): void {
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 0);
  }
  
  private loadDashboardData(): void {
    // Load real data from services
    // This is where we'd connect to our backend
  }
  
  onChatKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendChatMessage();
    }
  }
}