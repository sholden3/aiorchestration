import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainLayoutComponent } from './components/main-layout/main-layout.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { AgentManagerComponent } from './components/agent-manager/agent-manager.component';

const routes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'agents', component: AgentManagerComponent },
      { 
        path: 'reporting', 
        loadChildren: () => import('./modules/reporting/reporting.module').then(m => m.ReportingModule) 
      },
      { 
        path: 'orchestration', 
        loadChildren: () => import('./modules/orchestration/orchestration.module').then(m => m.OrchestrationModule) 
      },
      { 
        path: 'projects', 
        loadChildren: () => import('./modules/projects/projects.module').then(m => m.ProjectsModule) 
      },
      { 
        path: 'templates', 
        loadChildren: () => import('./modules/templates/templates.module').then(m => m.TemplatesModule) 
      },
      { 
        path: 'practices', 
        loadChildren: () => import('./modules/practices/practices.module').then(m => m.PracticesModule) 
      },
      { 
        path: 'rules', 
        loadChildren: () => import('./modules/rules/rules.module').then(m => m.RulesModule) 
      },
      { 
        path: 'governance', 
        loadChildren: () => import('./modules/governance/governance.module').then(m => m.GovernanceModule) 
      },
      { 
        path: 'plugins', 
        loadChildren: () => import('./modules/plugins/plugins.module').then(m => m.PluginsModule) 
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule]
})
export class AppRoutingModule { }