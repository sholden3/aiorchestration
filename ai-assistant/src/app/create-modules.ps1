# PowerShell script to create placeholder modules
$modules = @('reporting', 'projects', 'templates', 'practices', 'governance', 'plugins')

foreach ($module in $modules) {
    $modulePath = "modules/$module"
    
    # Module file
    $moduleContent = @"
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ${module.substring(0,1).toUpperCase()}${module.substring(1)}Component } from './$module.component';

const routes: Routes = [
  { path: '', component: ${module.substring(0,1).toUpperCase()}${module.substring(1)}Component }
];

@NgModule({
  declarations: [${module.substring(0,1).toUpperCase()}${module.substring(1)}Component],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ]
})
export class ${module.substring(0,1).toUpperCase()}${module.substring(1)}Module { }
"@
    
    # Component file
    $componentContent = @"
import { Component } from '@angular/core';

@Component({
  selector: 'app-$module',
  templateUrl: './$module.component.html',
  styleUrls: ['./$module.component.scss']
})
export class ${module.substring(0,1).toUpperCase()}${module.substring(1)}Component {
  title = '${module.substring(0,1).toUpperCase()}${module.substring(1)}';
}
"@
    
    # HTML file
    $htmlContent = @"
<div class="page-container">
  <mat-card>
    <mat-card-header>
      <mat-card-title>
        <mat-icon>dashboard</mat-icon>
        {{ title }}
      </mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <p>This section is under construction. Check back soon!</p>
    </mat-card-content>
  </mat-card>
</div>
"@
    
    # SCSS file
    $scssContent = @"
.page-container {
  padding: 24px;
  
  mat-card {
    max-width: 800px;
    margin: 0 auto;
    
    mat-card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      
      mat-icon {
        color: #667eea;
      }
    }
  }
}
"@
    
    # Write files
    Set-Content -Path "$modulePath/$module.module.ts" -Value $moduleContent
    Set-Content -Path "$modulePath/$module.component.ts" -Value $componentContent
    Set-Content -Path "$modulePath/$module.component.html" -Value $htmlContent
    Set-Content -Path "$modulePath/$module.component.scss" -Value $scssContent
    
    Write-Host "Created module: $module"
}

Write-Host "All modules created successfully!"