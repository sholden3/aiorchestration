# AI Development Assistant - Complete Use Guide & Testing Walkthrough

## Table of Contents
1. [Starting the System](#1-starting-the-system)
2. [First-Time Setup Verification](#2-first-time-setup-verification)
3. [Testing Core Features](#3-testing-core-features)
4. [Real Development Scenarios](#4-real-development-scenarios)
5. [Monitoring & Metrics](#5-monitoring--metrics)
6. [Troubleshooting Guide](#6-troubleshooting-guide)

---

## 1. Starting the System

### Step 1.1: Start Backend Service

Open Terminal 1:
```bash
cd C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\ClaudeResearchAndDevelopment\ai-assistant\backend
python main.py --port 8001
```

**Expected Output:**
```
INFO: Claude integration initialized in MOCK mode (Claude CLI not found)
INFO: Starting AI Backend Service on port 8001
INFO: Uvicorn running on http://127.0.0.1:8001
```

✅ **Check**: Backend is running when you see "Application startup complete"

### Step 1.2: Launch Frontend Application

Open Terminal 2:
```bash
cd C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\ClaudeResearchAndDevelopment\ai-assistant
npm start
```

**Expected Output:**
```
> ai-assistant@0.0.0 start
> electron .
```

✅ **Check**: Electron window opens with the AI Development Assistant

### Step 1.3: Verify All Services

Open Terminal 3 for testing:
```bash
# Test backend health
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-08-25T...",
  "cache_enabled": true,
  "personas_available": 3
}
```

---

## 2. First-Time Setup Verification

### Test 2.1: Dashboard Components

In the Electron app, verify you can see:

1. **Left Sidebar** with menu items:
   - [ ] Dashboard
   - [ ] Reporting  
   - [ ] AI Orchestration
   - [ ] Projects
   - [ ] Templates
   - [ ] Best Practices
   - [ ] Rules
   - [ ] Governance
   - [ ] Plugins

2. **Main Dashboard** showing:
   - [ ] Latest Updates cards
   - [ ] Current Projects with progress bars
   - [ ] AI Orchestration Status (if backend connected)
   - [ ] Cache Performance metrics

3. **Bottom Terminal** panel:
   - [ ] Terminal tabs (Terminal 1, AI Logs)
   - [ ] Input field for commands
   - [ ] Clear and expand buttons

### Test 2.2: Terminal Functionality

Click on the terminal area and test:

```bash
# Type these commands:
dir
echo "Testing terminal"
cd ..
dir
```

✅ **Check**: Commands execute and show output

---

## 3. Testing Core Features

### Test 3.1: Basic AI Task Execution

Open Terminal 3 and run:

```bash
# Test basic AI execution
curl -X POST "http://localhost:8001/ai/execute" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Write a Python function to calculate fibonacci\", \"use_cache\": false}"
```

**Expected Response:**
```json
{
  "success": true,
  "response": "```python\n# Mock code generation response...",
  "cached": false,
  "persona_used": "ai_integration",
  "execution_time_ms": ~500
}
```

📝 **Note**: Response is mocked since Claude CLI isn't installed

### Test 3.2: Cache System

Run the same request twice:

```bash
# First request (will be cached)
curl -X POST "http://localhost:8001/ai/execute" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Optimize database query\", \"use_cache\": true}"

# Second request (should hit cache)
curl -X POST "http://localhost:8001/ai/execute" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Optimize database query\", \"use_cache\": true}"
```

✅ **Check Second Response**:
- `"cached": true`
- `"tokens_saved": >0`
- `"execution_time_ms": 0 or very low`

### Test 3.3: Three-Persona Governance

Test the orchestrated endpoint with governance:

```bash
curl -X POST "http://localhost:8001/ai/orchestrated" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Design a scalable API architecture\", \"context\": {\"requirements\": \"high availability\"}}"
```

**Watch the Backend Terminal** for:
```
INFO: Starting full orchestration for task api_task_XXX
INFO: Extracted 9 assumptions for validation
INFO: marcus_rodriguez challenges assumption 'AI models will maintain consistent performance'
INFO: Orchestration complete. Consensus: UNANIMOUS
INFO: Assumptions validated: 8
```

### Test 3.4: WebSocket Real-Time Updates

1. **In the Dashboard**, look at the top-right corner for connection status
2. **Open Developer Tools** (F12 in Electron)
3. **Go to Console tab**
4. You should see:
   ```
   WebSocket connected - stopping polling
   ```

5. **Make an AI request** and watch for:
   ```
   Task update: {type: 'task_update', task_id: '...', status: 'started'}
   Persona decision: {persona: 'marcus_rodriguez', decision: '...'}
   ```

### Test 3.5: Cache Metrics

Check current cache performance:

```bash
curl http://localhost:8001/metrics/cache
```

**Expected Fields:**
```json
{
  "hit_rate": 0.5,  // Should increase with use
  "tokens_saved": 111,
  "hot_cache_size_mb": 0.0,
  "warm_cache_files": 62,
  "total_requests": 2,
  "cache_hits": 1,
  "cache_misses": 1
}
```

---

## 4. Real Development Scenarios

### Scenario 4.1: Code Review Request

Simulate a code review workflow:

```bash
# Step 1: Submit code for review
curl -X POST "http://localhost:8001/ai/orchestrated" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Review this code: def calc(x,y): return x+y*2/x if x!=0 else 0\", \"context\": {\"type\": \"code_review\"}}"
```

**Observe in Dashboard:**
- AI Orchestration Status shows active task
- Governance shield icon turns green
- Task count increments

### Scenario 4.2: Architecture Design

```bash
# Step 2: Request architecture design
curl -X POST "http://localhost:8001/ai/execute" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Design microservices for e-commerce platform\", \"persona\": \"systems_performance\"}"
```

**Note the persona**: Marcus Rodriguez (Systems) will take lead

### Scenario 4.3: Performance Optimization

```bash
# Step 3: Ask for optimization
curl -X POST "http://localhost:8001/ai/orchestrated" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Optimize React component rendering\", \"context\": {\"framework\": \"React 18\"}}"
```

**Check Cache**: Run same request again - should be instant

### Scenario 4.4: Bug Investigation

```bash
# Step 4: Debug assistance
curl -X POST "http://localhost:8001/ai/execute" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Debug: API returns 500 on POST /users\", \"context\": {\"error\": \"Internal Server Error\"}}"
```

---

## 5. Monitoring & Metrics

### 5.1: Dashboard Monitoring

**In the Electron App Dashboard:**

1. **AI Orchestration Status Card**
   - [ ] Shows "Running" status
   - [ ] Displays agent count (0/3 initially)
   - [ ] Shows active tasks
   - [ ] Governance Active indicator

2. **Cache Performance Card**
   - [ ] Hit Rate percentage
   - [ ] Tokens Saved count
   - [ ] Hot Cache size in MB
   - [ ] Warm Files count

3. **Live Updates Section**
   - [ ] Updates change to "Real-time" when WebSocket connected
   - [ ] Metrics update automatically every 5-10 seconds

### 5.2: Terminal Monitoring

In the **AI Logs** terminal tab:
- Switch to "AI Logs" tab
- Should show orchestration decisions
- Displays cache hits/misses

### 5.3: WebSocket Status

Check WebSocket connections:

```bash
curl http://localhost:8001/ws/status
```

Should show active connections if dashboard is open

### 5.4: Performance Testing

Run multiple requests to see cache improvement:

```bash
# Run this 5 times with the same prompt
for /L %i in (1,1,5) do curl -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Generate unit tests\", \"use_cache\": true}"
```

Check cache metrics after:
```bash
curl http://localhost:8001/metrics/cache
```

✅ **Cache hit rate should increase** toward 80%+

---

## 6. Troubleshooting Guide

### Issue 6.1: Backend Won't Start

**Symptom**: Error when running `python main.py`

**Fix**:
```bash
# Install dependencies
pip install fastapi uvicorn asyncpg pydantic

# Check Python version (needs 3.8+)
python --version
```

### Issue 6.2: Frontend Won't Start

**Symptom**: `npm start` fails

**Fix**:
```bash
# Install dependencies
npm install

# If Electron issues:
npm install electron --save-dev

# Clear cache and retry
npm cache clean --force
npm install
```

### Issue 6.3: WebSocket Not Connecting

**Symptom**: Dashboard shows "Disconnected"

**Checks**:
1. Backend running on port 8001?
2. No firewall blocking WebSocket?
3. Check browser console for errors

**Test WebSocket directly**:
```bash
cd ai-assistant\backend
python test_websocket.py
```

### Issue 6.4: Terminal Not Working

**Symptom**: No output in terminal panel

**Fix**:
- Windows: Should fallback to cmd.exe automatically
- Check Electron dev tools console for errors
- Try typing `echo test` and pressing Enter

### Issue 6.5: Cache Not Working

**Symptom**: Every request shows `"cached": false`

**Fix**:
1. Ensure `use_cache: true` in request
2. Use exact same prompt for cache hit
3. Check cache metrics endpoint
4. Clear cache and restart:
   ```bash
   curl -X POST http://localhost:8001/cache/clear
   ```

---

## Quick Test Checklist

Use this checklist to verify everything is working:

### Backend Tests
- [ ] Health endpoint returns 200 OK
- [ ] AI execute endpoint returns mock response
- [ ] AI orchestrated endpoint shows governance
- [ ] Cache metrics endpoint shows data
- [ ] WebSocket status shows connections

### Frontend Tests  
- [ ] Electron app launches
- [ ] Dashboard loads with cards
- [ ] Terminal accepts commands
- [ ] Sidebar navigation works
- [ ] Real-time updates appear

### Integration Tests
- [ ] Cache hit on repeated request
- [ ] WebSocket connects from dashboard
- [ ] Governance decisions in backend log
- [ ] Metrics update in real-time
- [ ] Terminal shows command output

---

## Notes Section (Your Testing Notes)

Use this section to record your observations:

### What Works Well:
```
- 
- 
- 
```

### Issues Found:
```
- 
- 
- 
```

### Improvement Ideas:
```
- 
- 
- 
```

### Performance Observations:
```
- Cache hit rate after 10 requests: ____%
- Average response time (cached): ____ms
- Average response time (new): ____ms
- Token savings after session: ____
```

---

## Next Steps After Testing

1. **If everything works**: Ready to use with your Claude Code workflow
2. **If issues found**: Check troubleshooting section
3. **To use with real Claude**: Install Claude CLI and restart backend
4. **To customize**: Modify personas in `persona_manager.py`
5. **To enhance**: Add more mock responses in `claude_integration.py`

---

## Support Commands Reference

```bash
# Backend
cd ai-assistant\backend
python main.py --port 8001

# Frontend
cd ai-assistant
npm start

# Test health
curl http://localhost:8001/health

# Test AI
curl -X POST http://localhost:8001/ai/execute -H "Content-Type: application/json" -d "{\"prompt\": \"test\"}"

# Check cache
curl http://localhost:8001/metrics/cache

# WebSocket test
python backend\test_websocket.py

# Clear cache
curl -X POST http://localhost:8001/cache/clear
```

---

This guide should help you thoroughly test the AI Development Assistant. Take notes in the provided sections as you go through each test!