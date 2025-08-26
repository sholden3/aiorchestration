# AI Development Assistant - Setup Guide
## Complete Installation and Configuration Instructions

---

## 📋 Prerequisites

### Required Software
1. **Node.js** (v18+ recommended)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **Python** (3.10+ required)
   - Download from: https://python.org/
   - Verify: `python --version`

3. **PostgreSQL** (14+ recommended)
   - Download from: https://www.postgresql.org/download/windows/
   - Default installation with:
     - Username: `postgres`
     - Password: `postgres` (you can change this)
     - Port: `5432`

4. **Git** (for Bash support on Windows)
   - Download from: https://git-scm.com/
   - This provides Git Bash for terminal emulation

5. **Claude Code** (already configured)
   - You mentioned this is already set up
   - The app will use your existing configuration

---

## 🚀 Installation Steps

### Step 1: Clone/Extract Project
```bash
# Navigate to your project directory
cd C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\ClaudeResearchAndDevelopment\ai-assistant
```

### Step 2: Install Node Dependencies
```bash
# Install Node.js dependencies
npm install

# If you encounter node-pty issues on Windows:
npm install --global windows-build-tools
npm rebuild node-pty
```

### Step 3: Set Up Python Backend
```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Step 4: Configure PostgreSQL Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE ai_assistant;

-- Exit psql
\q
```

### Step 5: Initialize Angular Project
```bash
# Install Angular CLI globally if not already installed
npm install -g @angular/cli

# Generate Angular application
ng new frontend --routing --style=scss
cd frontend

# Add Angular Material
ng add @angular/material

# Copy the provided components to src/app/
# (Components are provided in the implementation)
```

---

## 🔧 Configuration

### Database Configuration
If using different PostgreSQL credentials, update `backend/database_manager.py`:

```python
def _get_default_connection(self) -> str:
    return "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/ai_assistant"
```

### Claude Code Path
The system will auto-detect Claude Code. If it's not in PATH, update `backend/claude_integration.py`:

```python
possible_commands = [
    "C:\\path\\to\\your\\claude.exe",  # Add your Claude Code path
    # ... other paths
]
```

---

## 🏃 Running the Application

### Development Mode (Recommended for Setup)

#### Terminal 1: Start Backend
```bash
# Activate Python virtual environment
venv\Scripts\activate

# Start FastAPI backend
cd backend
python main.py
```
The backend will start on `http://localhost:8000`

#### Terminal 2: Start Frontend
```bash
# Start Angular development server
npm run watch
```
Angular will compile and watch for changes

#### Terminal 3: Start Electron
```bash
# Start Electron app
npm run electron:dev
```
The desktop application will open

### Production Mode
```bash
# Build and run everything
npm run build
npm start
```

---

## ✅ Verification Steps

### 1. Backend Health Check
Open browser and navigate to:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T...",
  "cache_enabled": true,
  "personas_available": 3
}
```

### 2. Database Connection
Check PostgreSQL connection:
```bash
psql -U postgres -d ai_assistant -c "SELECT 1;"
```

### 3. Claude Code Integration
Test Claude Code is accessible:
```bash
claude --version
```

### 4. PTY Terminal Test
In the Electron app:
1. Click "New Terminal"
2. Select PowerShell/Bash/CMD
3. Type `echo "Hello AI Assistant"`

---

## 🐛 Troubleshooting

### Issue: node-pty build fails on Windows
**Solution:**
```bash
npm install --global node-gyp
npm install --global windows-build-tools
npm rebuild node-pty --runtime=electron --target=28.0.0 --dist-url=https://atom.io/download/electron
```

### Issue: PostgreSQL connection refused
**Solution:**
1. Check PostgreSQL service is running:
```bash
# Windows Services
services.msc
# Look for "postgresql-x64-14" or similar
```

2. Verify connection:
```bash
psql -U postgres -h localhost -p 5432
```

### Issue: Backend won't start
**Solution:**
1. Check Python version: `python --version` (needs 3.10+)
2. Reinstall dependencies: `pip install -r backend/requirements.txt --force-reinstall`
3. Check port 8000 is not in use: `netstat -an | findstr :8000`

### Issue: Claude Code not found
**Solution:**
1. Add Claude to PATH, or
2. Update the path in `backend/claude_integration.py`
3. Verify with: `where claude` or `which claude`

### Issue: Angular compilation errors
**Solution:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

## 📊 Initial Configuration

### Setting Performance Targets
The system targets:
- **Cache Hit Rate**: 90%
- **Token Savings**: 65%
- **Response Time**: <500ms

These are monitored in the dashboard automatically.

### Persona Configuration
Three personas are pre-configured:
1. **Dr. Sarah Chen**: AI/Claude integration
2. **Marcus Rodriguez**: Systems/Performance
3. **Emily Watson**: UX/Frontend

No additional configuration needed.

---

## 🎯 Quick Test

After setup, test the system:

1. **Open the application**
2. **Type a test prompt**: "How do I optimize Python code for performance?"
3. **Check the dashboard** for:
   - Token usage
   - Cache hit rate
   - Response time
4. **Open a terminal** and verify PTY works

---

## 📝 Next Steps

1. **Familiarize with the UI**: Explore the dashboard and terminal
2. **Test personas**: Try different types of questions
3. **Monitor metrics**: Watch token savings increase with cache hits
4. **Customize**: Adjust cache sizes, TTLs, etc. as needed

---

## 🆘 Support

For issues:
1. Check the logs:
   - Backend: Terminal running `python main.py`
   - Frontend: Browser DevTools console
   - Electron: DevTools in the app

2. Verify all services running:
   - PostgreSQL on port 5432
   - Backend on port 8000
   - Angular on port 4200

3. Review error messages in the application's monitoring dashboard

---

**The system is designed to work locally on your Windows machine as a personal development tool. All data stays local, and the tool integrates with your existing Claude Code setup.**