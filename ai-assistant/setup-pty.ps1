# PowerShell script to setup PTY support for AI Development Assistant
# Run as Administrator for best results

Write-Host "AI Development Assistant - PTY Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠ Not running as Administrator. Some features may not install correctly." -ForegroundColor Yellow
    Write-Host ""
}

# Function to test if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "Checking prerequisites..." -ForegroundColor Green

# Check Python
Write-Host -NoNewline "  Python: "
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Not found" -ForegroundColor Red
    Write-Host "    Please install Python from https://python.org" -ForegroundColor Yellow
}

# Check Node.js
Write-Host -NoNewline "  Node.js: "
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "✓ $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Not found" -ForegroundColor Red
    Write-Host "    Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
}

# Check Visual Studio or Build Tools
Write-Host -NoNewline "  C++ Build Tools: "
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    $vsInstall = & $vsWhere -latest -property installationPath
    if ($vsInstall) {
        Write-Host "✓ Visual Studio found" -ForegroundColor Green
    } else {
        Write-Host "⚠ Visual Studio found but no installation detected" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ Not found" -ForegroundColor Red
    Write-Host "    Installing Windows Build Tools..." -ForegroundColor Yellow
    
    if ($isAdmin) {
        # Try to install build tools
        Write-Host "    Downloading build tools..." -ForegroundColor Cyan
        $buildToolsUrl = "https://aka.ms/vs/17/release/vs_buildtools.exe"
        $installerPath = "$env:TEMP\vs_buildtools.exe"
        
        try {
            Invoke-WebRequest -Uri $buildToolsUrl -OutFile $installerPath
            Write-Host "    Starting installation (this may take several minutes)..." -ForegroundColor Cyan
            Start-Process -FilePath $installerPath -ArgumentList "--quiet", "--wait", "--add", "Microsoft.VisualStudio.Workload.VCTools", "--includeRecommended" -Wait
            Write-Host "    ✓ Build tools installed" -ForegroundColor Green
        } catch {
            Write-Host "    ✗ Failed to install build tools: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "    Run this script as Administrator to auto-install build tools" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Attempting to install node-pty..." -ForegroundColor Green

# Set Python path for node-gyp
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if ($pythonPath) {
    $env:PYTHON = $pythonPath
    Write-Host "  Set PYTHON environment variable to: $pythonPath" -ForegroundColor Cyan
}

# Try to install node-pty
Set-Location -Path $PSScriptRoot
Write-Host "  Running: npm install node-pty" -ForegroundColor Cyan
npm install node-pty 2>&1 | ForEach-Object {
    if ($_ -match "error") {
        Write-Host "  $_" -ForegroundColor Red
    } elseif ($_ -match "warn") {
        Write-Host "  $_" -ForegroundColor Yellow
    } else {
        Write-Host "  $_" -ForegroundColor Gray
    }
}

# Check if installation succeeded
Write-Host ""
Write-Host "Checking installation status..." -ForegroundColor Green

if (Test-Path "node_modules\node-pty") {
    Write-Host "✓ node-pty installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "PTY support is now available. The app will use full terminal functionality." -ForegroundColor Green
} else {
    Write-Host "⚠ node-pty installation failed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The app will use fallback terminal implementation with limited features." -ForegroundColor Yellow
    Write-Host "This is sufficient for most development tasks." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete. You can now run:" -ForegroundColor Cyan
Write-Host "  npm run build:electron" -ForegroundColor White
Write-Host "  npm run electron" -ForegroundColor White
Write-Host ""

# Pause if not running in a script
if (-not $PSCommandPath) {
    Read-Host "Press Enter to continue"
}