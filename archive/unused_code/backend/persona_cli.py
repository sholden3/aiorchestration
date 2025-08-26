#!/usr/bin/env python
"""
Simple CLI interface to use the AI Orchestration System immediately
Run: python persona_cli.py
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Optional

# Set environment variables for immediate use
os.environ['MAX_HOT_CACHE_ITEMS'] = '100'
os.environ['DB_HOST'] = 'localhost'  # Will fallback to mock if not available

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from persona_manager import PersonaManager, PersonaType
from cache_manager import IntelligentCache
from database_manager import DatabaseManager
from claude_unified_integration import ClaudeUnifiedIntegration
from orchestrator import MultiTenantOrchestrator

class PersonaCLI:
    """Simple CLI for using AI personas immediately"""
    
    def __init__(self):
        """Initialize the system components"""
        print("[INIT] Initializing AI Orchestration System...")
        self.config = Config()
        self.cache = IntelligentCache()
        self.database = DatabaseManager(self.config)
        self.persona_manager = PersonaManager()  # No config parameter
        self.claude = ClaudeUnifiedIntegration(self.config)
        self._initialized = False
        
    async def _init_async(self):
        """Async initialization"""
        if not self._initialized:
            # Cache doesn't need async init, database does
            await self.database.initialize()
            self._initialized = True
            print("[OK] System ready!\n")
        
    def show_personas(self):
        """Display available personas"""
        print("\n[PERSONAS] Available AI Personas:")
        print("-" * 50)
        personas = {
            "1": ("Dr. Sarah Chen", PersonaType.SARAH_CHEN, "AI Integration & Claude Optimization"),
            "2": ("Marcus Rodriguez", PersonaType.MARCUS_RODRIGUEZ, "Systems Performance & Architecture"),
            "3": ("Emily Watson", PersonaType.EMILY_WATSON, "UX/Frontend & User Experience")
        }
        
        for key, (name, persona_type, description) in personas.items():
            print(f"{key}. {name}")
            print(f"   Specialty: {description}")
            print(f"   Keywords: {', '.join(self.persona_manager.persona_keywords.get(persona_type, [])[:5])}")
            print()
        
        return personas
    
    async def process_request(self, user_input: str, persona_type: Optional[PersonaType] = None):
        """Process a user request with the appropriate persona"""
        
        # Ensure initialization
        await self._init_async()
        
        # Auto-select persona if not specified
        if not persona_type:
            suggested = self.persona_manager.suggest_persona(user_input)
            if suggested:
                persona_type = suggested[0]
                print(f"[AUTO] Auto-selected: {persona_type.value}")
        
        # Check cache first
        cache_key = self.cache.generate_key(user_input, persona_type.value if persona_type else "general")
        cached_response = await self.cache.get(cache_key)
        
        if cached_response:
            print("[CACHE HIT] Using cached response.")
            return cached_response
        
        # Format prompt with persona
        if persona_type:
            prompt = self.persona_manager.format_prompt_for_persona(user_input, persona_type)
            # Ensure prompt is a string
            if not isinstance(prompt, str):
                prompt = str(prompt)
        else:
            prompt = user_input
        
        print(f"[PROCESSING] Using {persona_type.value if persona_type else 'general'} persona...")
        
        # For demo purposes, create a simulated response
        # In production, this would call Claude API
        response = {
            "persona": persona_type.value if persona_type else "general",
            "request": user_input,
            "response": f"[{persona_type.value if persona_type else 'General'}] Analysis of your request:\n\n"
                       f"Based on my expertise, here's my response to '{user_input[:50]}...'\n\n"
                       f"[This is a demo response. In production, this would use Claude API]",
            "confidence": 0.95,
            "tokens_used": len(str(prompt).split()) if prompt else 0
        }
        
        # Cache the response
        await self.cache.set(cache_key, response, ttl=3600)
        
        return response
    
    async def run_interactive(self):
        """Run interactive CLI session"""
        print("=" * 60)
        print("AI ORCHESTRATION SYSTEM - INTERACTIVE MODE")
        print("=" * 60)
        
        while True:
            self.show_personas()
            print("\nOptions:")
            print("  1-3: Select a specific persona")
            print("  a:   Auto-select persona based on request")
            print("  q:   Quit")
            print()
            
            choice = input("Select option: ").strip().lower()
            
            if choice == 'q':
                print("\n[EXIT] Goodbye!")
                break
            
            # Get user request
            user_input = input("\n[INPUT] Enter your request: ").strip()
            if not user_input:
                continue
            
            # Select persona
            persona_type = None
            if choice in ['1', '2', '3']:
                persona_map = {
                    '1': PersonaType.SARAH_CHEN,
                    '2': PersonaType.MARCUS_RODRIGUEZ,
                    '3': PersonaType.EMILY_WATSON
                }
                persona_type = persona_map[choice]
            
            # Process request
            try:
                response = await self.process_request(user_input, persona_type)
                
                print("\n" + "=" * 60)
                print("[RESPONSE]:")
                print("=" * 60)
                print(response['response'])
                print("\n" + "-" * 60)
                print(f"[METRICS] Confidence: {response['confidence']:.2%}, Tokens: {response['tokens_used']}")
                print("=" * 60)
                
            except Exception as e:
                print(f"\n[ERROR] {e}")
            
            print("\n" + "=" * 60)
            input("\nPress Enter to continue...")
            print("\033[2J\033[H")  # Clear screen
    
    async def run_batch(self, requests_file: str):
        """Process batch requests from a file"""
        print(f"[BATCH] Processing file: {requests_file}")
        
        if not Path(requests_file).exists():
            print(f"[ERROR] File not found: {requests_file}")
            return
        
        with open(requests_file, 'r') as f:
            requests = json.load(f)
        
        results = []
        for i, req in enumerate(requests, 1):
            print(f"\n[{i}/{len(requests)}] Processing: {req.get('request', '')[:50]}...")
            
            persona_type = None
            if 'persona' in req:
                persona_map = {
                    'sarah': PersonaType.SARAH_CHEN,
                    'marcus': PersonaType.MARCUS_RODRIGUEZ,
                    'emily': PersonaType.EMILY_WATSON
                }
                persona_type = persona_map.get(req['persona'].lower())
            
            response = await self.process_request(req['request'], persona_type)
            results.append(response)
        
        # Save results
        output_file = requests_file.replace('.json', '_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[SAVED] Results: {output_file}")
        
        # Show summary
        print("\n[SUMMARY]:")
        print(f"  Total requests: {len(requests)}")
        print(f"  Cache hits: {sum(1 for r in results if 'cache_hit' in r and r['cache_hit'])}")
        print(f"  Total tokens: {sum(r.get('tokens_used', 0) for r in results)}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Orchestration System CLI')
    parser.add_argument('--batch', help='Process batch requests from JSON file')
    parser.add_argument('--request', help='Single request to process')
    parser.add_argument('--persona', choices=['sarah', 'marcus', 'emily', 'auto'], 
                       default='auto', help='Select persona')
    
    args = parser.parse_args()
    
    cli = PersonaCLI()
    
    if args.batch:
        asyncio.run(cli.run_batch(args.batch))
    elif args.request:
        persona_map = {
            'sarah': PersonaType.SARAH_CHEN,
            'marcus': PersonaType.MARCUS_RODRIGUEZ,
            'emily': PersonaType.EMILY_WATSON
        }
        persona = persona_map.get(args.persona) if args.persona != 'auto' else None
        
        result = asyncio.run(cli.process_request(args.request, persona))
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        asyncio.run(cli.run_interactive())

if __name__ == "__main__":
    main()