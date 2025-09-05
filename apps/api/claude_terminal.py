"""
Claude Terminal Integration
Provides a terminal interface to interact with Claude directly
"""

import asyncio
import subprocess
import os
from typing import Optional, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeTerminal:
    """
    Terminal interface for Claude interaction
    Allows direct conversation with Claude through PTY
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_connected = False
        self.session_id = f"claude_{datetime.now().timestamp()}"
        self.output_callback: Optional[Callable] = None
        
    async def connect(self, output_callback: Callable = None):
        """
        Connect to Claude via terminal
        This would normally launch claude CLI in interactive mode
        """
        self.output_callback = output_callback
        
        # Check if Claude CLI exists
        claude_cmd = self._find_claude_command()
        
        if claude_cmd:
            try:
                # Start Claude in interactive mode
                self.process = subprocess.Popen(
                    [claude_cmd, '--interactive'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.is_connected = True
                logger.info(f"Connected to Claude CLI: {self.session_id}")
                
                # Start output reader
                asyncio.create_task(self._read_output())
                
                return {
                    'success': True,
                    'session_id': self.session_id,
                    'message': 'Connected to Claude'
                }
            except Exception as e:
                logger.error(f"Failed to start Claude CLI: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'message': 'Claude CLI not available, using mock mode'
                }
        else:
            # Mock mode
            self.is_connected = True
            logger.info("Claude Terminal in mock mode")
            
            if self.output_callback:
                await self.output_callback({
                    'session_id': self.session_id,
                    'output': 'Claude Terminal (Simulation Mode - Claude CLI not found in PATH)\n\nNote: To use real Claude integration, ensure Claude Code CLI is in your PATH.\nCurrently using advanced simulation for testing.\n\n> Ready for input\n',
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'success': True,
                'session_id': self.session_id,
                'message': 'Claude Terminal connected (Simulation mode - CLI not in PATH)'
            }
    
    def _find_claude_command(self) -> Optional[str]:
        """Find Claude CLI executable"""
        possible_commands = [
            'claude',
            'claude.bat',
            'claude-code',
            'claude-code.bat',
            os.path.expanduser('~/claude/claude'),
            r'C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\cache_optimizer_project\ClaudeInterceptor\claude.bat',
        ]
        
        # On Windows, also check if claude is available via where command
        if os.name == 'nt':
            try:
                result = subprocess.run(['where', 'claude'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    claude_path = result.stdout.strip().split('\n')[0]
                    if claude_path and os.path.exists(claude_path):
                        logger.info(f"Found Claude at: {claude_path}")
                        return claude_path
            except:
                pass
        
        for cmd in possible_commands:
            try:
                # Try running with --version or --help
                test_args = ['--version'] if 'bat' not in cmd else ['--help']
                result = subprocess.run(
                    [cmd] + test_args,
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0 or 'claude' in result.stdout.decode('utf-8', errors='ignore').lower():
                    logger.info(f"Found working Claude command: {cmd}")
                    return cmd
            except Exception as e:
                continue
        
        logger.warning("Claude CLI not found, will use mock mode")
        return None
    
    async def _read_output(self):
        """Read output from Claude process"""
        if not self.process:
            return
        
        while self.is_connected and self.process:
            try:
                line = self.process.stdout.readline()
                if line and self.output_callback:
                    await self.output_callback({
                        'session_id': self.session_id,
                        'output': line,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error reading Claude output: {e}")
                break
    
    async def send_message(self, message: str):
        """Send message to Claude"""
        if not self.is_connected:
            return {
                'success': False,
                'error': 'Not connected to Claude'
            }
        
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(message + '\n')
                self.process.stdin.flush()
                
                return {
                    'success': True,
                    'message_sent': message
                }
            except Exception as e:
                logger.error(f"Failed to send message to Claude: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        else:
            # Mock mode response
            mock_response = self._generate_mock_response(message)
            
            if self.output_callback:
                await self.output_callback({
                    'session_id': self.session_id,
                    'output': f"\nYou: {message}\n\nClaude: {mock_response}\n\n> ",
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'success': True,
                'message_sent': message,
                'mock_response': mock_response
            }
    
    def _generate_mock_response(self, message: str) -> str:
        """Generate mock Claude response (simulating real Claude)"""
        message_lower = message.lower()
        
        # More realistic mock responses based on common queries
        if 'hello' in message_lower or 'hi' in message_lower:
            return "Hello! I'm Claude, your AI assistant. I can help with coding, analysis, debugging, and answering questions. What would you like to work on today?"
        
        elif 'help' in message_lower:
            return """I can assist you with:
• Writing and reviewing code in multiple languages
• Debugging and troubleshooting issues
• Explaining complex concepts
• Designing system architectures
• Optimizing performance
• Writing documentation
• And much more! What specific task can I help you with?"""
        
        elif 'test' in message_lower:
            return "The terminal connection is working properly. I'm ready to assist you with any programming or technical questions you have."
        
        elif 'code' in message_lower or 'write' in message_lower or 'create' in message_lower:
            return f"I understand you want help with coding related to: '{message[:100]}'. While I'm in simulation mode, in production I would provide detailed code examples, explanations, and best practices for your specific request."
        
        elif 'explain' in message_lower or 'what' in message_lower or 'how' in message_lower:
            return f"Great question about '{message[:100]}'. In production mode, I would provide a comprehensive explanation with examples and clarifications. Currently running in simulation mode for testing."
        
        elif 'fix' in message_lower or 'error' in message_lower or 'bug' in message_lower:
            return f"I see you need help debugging: '{message[:100]}'. In production, I would analyze the error, identify the root cause, and provide a solution with explanation."
        
        # Default response with context
        return f"""I received your message: "{message[:150]}{'...' if len(message) > 150 else ''}"

In production mode with full Claude integration, I would provide a detailed, thoughtful response to your query. Currently operating in simulation mode for testing the terminal interface.

The system is configured correctly and ready for full Claude CLI integration once the path is properly set."""
    
    async def disconnect(self):
        """Disconnect from Claude"""
        self.is_connected = False
        
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass
            finally:
                self.process = None
        
        logger.info(f"Disconnected Claude terminal: {self.session_id}")
        return {'success': True}
    
    def get_status(self):
        """Get terminal status"""
        return {
            'session_id': self.session_id,
            'is_connected': self.is_connected,
            'mode': 'cli' if self.process else 'mock'
        }

# Global Claude terminal instance
claude_terminal = ClaudeTerminal()