"""
Quick WebSocket test to verify real-time monitoring
Run this while the backend is running to see live updates
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:8001/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[OK] Connected to WebSocket at {uri}")
            print("=" * 50)
            
            # Subscribe to all events
            await websocket.send(json.dumps({
                "type": "subscribe",
                "events": [
                    "orchestration_status",
                    "cache_metrics",
                    "task_update",
                    "persona_decision",
                    "assumption_validation"
                ]
            }))
            
            # Send a ping
            await websocket.send(json.dumps({
                "type": "ping"
            }))
            
            # Request status
            await websocket.send(json.dumps({
                "type": "request_status"
            }))
            
            print("Listening for updates...")
            print("(Press Ctrl+C to stop)")
            print("=" * 50)
            
            # Listen for messages
            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(message)
                    message_count += 1
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] Message #{message_count}")
                    print(f"Type: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'orchestration_status':
                        status = data.get('data', {})
                        print(f"  Orchestration: {'Running' if status.get('is_running') else 'Stopped'}")
                        print(f"  Agents: {status.get('agents', {})}")
                        print(f"  Tasks: {status.get('tasks', {})}")
                    
                    elif data.get('type') == 'cache_metrics':
                        metrics = data.get('data', {})
                        hit_rate = metrics.get('hit_rate', 0) * 100
                        print(f"  Cache Hit Rate: {hit_rate:.1f}%")
                        print(f"  Tokens Saved: {metrics.get('tokens_saved', 0)}")
                        print(f"  Cache Hits: {metrics.get('cache_hits', 0)}")
                    
                    elif data.get('type') == 'task_update':
                        print(f"  Task ID: {data.get('task_id')}")
                        print(f"  Status: {data.get('status')}")
                        print(f"  Details: {data.get('details')}")
                    
                    elif data.get('type') == 'persona_decision':
                        print(f"  Persona: {data.get('persona')}")
                        print(f"  Decision: {data.get('decision')[:50]}...")
                        print(f"  Confidence: {data.get('confidence')}")
                    
                    elif data.get('type') == 'assumption_validation':
                        print(f"  Assumption: {data.get('assumption')}")
                        print(f"  Validated: {data.get('validated')}")
                        print(f"  Challenger: {data.get('challenger', 'N/A')}")
                    
                    else:
                        print(f"  Data: {json.dumps(data, indent=2)}")
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)  # Show we're still listening
                    
    except websockets.exceptions.WebSocketException as e:
        print(f"[ERROR] WebSocket error: {e}")
    except KeyboardInterrupt:
        print("\n\nDisconnecting...")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    print("WebSocket Test Client")
    print("=" * 50)
    asyncio.run(test_websocket())