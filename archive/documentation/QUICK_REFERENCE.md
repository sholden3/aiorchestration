# AI Assistant - Quick Reference Card

## 🚀 Start Everything
```bash
# Terminal 1 - Backend
cd ai-assistant\backend
python main.py --port 8001

# Terminal 2 - Frontend  
cd ai-assistant
npm start

# Terminal 3 - Testing
# Keep this for running test commands
```

## ✅ Quick Health Check
```bash
curl http://localhost:8001/health
```

## 🧪 Test Commands (Copy & Paste)

### Basic AI Request
```bash
curl -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Write a hello world function\", \"use_cache\": true}"
```

### Governed AI Request (Three Personas)
```bash
curl -X POST "http://localhost:8001/ai/orchestrated" -H "Content-Type: application/json" -d "{\"prompt\": \"Design a database schema\", \"context\": {\"type\": \"postgres\"}}"
```

### Check Cache Performance
```bash
curl http://localhost:8001/metrics/cache
```

### Check Orchestration Status
```bash
curl http://localhost:8001/orchestration/status
```

### Test WebSocket
```bash
curl http://localhost:8001/ws/status
```

### Clear Cache
```bash
curl -X POST http://localhost:8001/cache/clear
```

## 📊 What to Look For

### In Backend Terminal:
- `INFO: Orchestration complete. Consensus: UNANIMOUS`
- `INFO: Assumptions validated: 8`
- `INFO: marcus_rodriguez challenges assumption`

### In Dashboard:
- Green "Running" status
- Cache hit rate increasing
- Real-time updates showing
- Tasks incrementing

### In API Responses:
- `"cached": true` = Cache working
- `"tokens_saved": >0` = Saving money
- `"execution_time_ms": 0` = Fast cache hit
- `"persona_used": "orchestrated_consensus"` = Governance active

## 🎯 Testing Sequence

1. **First Request** - Creates cache entry
```bash
curl -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Test prompt 1\", \"use_cache\": true}"
```

2. **Same Request** - Should hit cache (fast)
```bash
curl -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Test prompt 1\", \"use_cache\": true}"
```

3. **Governed Request** - Three personas validate
```bash
curl -X POST "http://localhost:8001/ai/orchestrated" -H "Content-Type: application/json" -d "{\"prompt\": \"Test prompt 1\", \"context\": {}}"
```

4. **Check Metrics** - See improvement
```bash
curl http://localhost:8001/metrics/cache
```

## 🔍 Dashboard Navigation

1. **Dashboard** - Main metrics view
2. **AI Orchestration** - Agent management
3. **Rules** - Governance rules
4. **Terminal** - Built-in terminal

## ⚡ Keyboard Shortcuts

- `F5` - Refresh dashboard
- `F12` - Developer tools
- `Ctrl+T` - New terminal tab (in app)
- `Ctrl+K` - Clear terminal

## 🛠️ Troubleshooting

### Backend Issues:
```bash
# Check if running
curl http://localhost:8001/health

# Restart backend
Ctrl+C (in backend terminal)
python main.py --port 8001
```

### Frontend Issues:
```bash
# Restart Electron
Ctrl+C (in frontend terminal)
npm start

# Check console
F12 in Electron window
```

### Cache Issues:
```bash
# Clear and restart
curl -X POST http://localhost:8001/cache/clear
```

## 📈 Success Metrics

- ✅ Cache hit rate > 50%
- ✅ Response time < 500ms (new), < 10ms (cached)
- ✅ All 3 personas active
- ✅ WebSocket connected
- ✅ Assumptions validated > 75%

## 💡 Pro Tips

1. **Same prompt = Cache hit** - Use identical text
2. **Watch backend terminal** - See governance in action
3. **F12 console** - See WebSocket messages
4. **Multiple requests** - Build cache hit rate
5. **Context matters** - Different context = different cache key

---

Keep this open while testing. Copy commands directly from here!