/**
 * @fileoverview Root Angular module for AI Assistant application
 * @author Alex Novak v2.0 - 2025-08-29
 * @architecture Frontend - Angular root module configuration
 * @responsibility Bootstrap Angular application with required modules and services
 * @dependencies Angular core, Material Design, HttpClient, Forms, routing
 * @integration_points All Angular components, services, backend API via HTTP
 * @testing_strategy Module testing with TestBed, component integration tests
 * @governance Frontend security boundaries, XSS protection, CORS handling
 * 
 * Business Logic Summary:
 * - Configure Angular application modules
 * - Register global services and providers
 * - Set up Material Design components
 * - Configure HTTP interceptors
 * - Bootstrap main application component
 * 
 * Architecture Integration:
 * - Entry point for Angular application
 * - Configures all UI components
 * - Sets up service injection
 * - Manages application-wide providers
 * - Integrates with Electron via services
 */
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';

// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatBadgeModule } from '@angular/material/badge';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';

// Components - Only existing ones
import { AppComponent } from './app.component';
import { ToolbarComponent } from './components/toolbar/toolbar.component';
import { StatusIndicatorsComponent } from './components/status-indicators/status-indicators.component';
import { TerminalComponent } from './components/terminal/terminal.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LayoutComponent } from './components/layout/layout.component';
import { MainLayoutComponent } from './components/main-layout/main-layout.component';
import { SidenavComponent } from './components/sidenav/sidenav.component';
import { AgentManagerComponent } from './components/agent-manager/agent-manager.component';

// Services
import { OrchestrationService } from './services/orchestration.service';
// TerminalService import removed - now component-scoped per C1 fix
import { RulesService } from './services/rules.service';
import { WebSocketService } from './services/websocket.service';

@NgModule({
  declarations: [
    AppComponent,
    ToolbarComponent,
    StatusIndicatorsComponent,
    TerminalComponent,
    DashboardComponent,
    LayoutComponent,
    MainLayoutComponent,
    AgentManagerComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    SidenavComponent,
    // Material Modules
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatTabsModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatBadgeModule,
    MatTooltipModule,
    MatExpansionModule,
    MatDialogModule,
    MatSnackBarModule,
    MatSlideToggleModule,
    MatGridListModule,
    MatDividerModule,
    MatTableModule
  ],
  providers: [
    OrchestrationService,
    // TerminalService removed - now component-scoped per C1 fix
    RulesService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }