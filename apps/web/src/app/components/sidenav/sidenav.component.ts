import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

export interface MenuItem {
  icon: string;
  label: string;
  route: string;
}

@Component({
  selector: 'app-sidenav',
  standalone: true,
  imports: [
    CommonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule
  ],
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent {
  @Input() isOpen = true;
  @Input() activeMenuItem = 'dashboard';
  @Output() menuItemSelected = new EventEmitter<string>();
  
  menuItems: MenuItem[] = [
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

  constructor(private router: Router) {}

  selectMenuItem(route: string): void {
    this.menuItemSelected.emit(route);
    this.router.navigate([route]);
    
    // On mobile, close sidebar after selection
    if (window.innerWidth <= 768) {
      this.isOpen = false;
    }
  }
}