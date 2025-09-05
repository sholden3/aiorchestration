# Claude Code Native Hooks: Complete Implementation Guide

A comprehensive implementation guide for all 9 native Claude Code hooks, their available tools, pain points, and Python integration patterns.

## Quick Reference: All Native Hooks

| Hook | Execution Point | Can Block? | Primary Use Case |
|------|----------------|------------|------------------|
| `PreToolUse` | Before tool execution | ✅ Yes (exit 2) | Security validation, input sanitization |
| `PostToolUse` | After tool completion | ❌ No (feedback only) | Code formatting, testing, documentation |
| `UserPromptSubmit` | When user submits prompt | ❌ No (context only) | Context injection, prompt enhancement |
| `SessionStart` | Session begin/resume | ❌ No (setup only) | Environment setup, context loading |
| `SessionEnd` | Session termination | ❌ No (cleanup only) | Cleanup, logging, state persistence |
| `Notification` | When Claude needs permission | ❌ No (alert only) | External notifications, approval workflows |
| `Stop` | When Claude stops working | ✅ Yes (exit 2 forces continue) | Workflow management, completion validation |
| `SubagentStop` | When subagents stop | ✅ Yes (exit 2 forces continue) | Multi-agent orchestration |
| `PreCompact` | Before context compaction | ❌ No (backup only) | Context preservation, transcript archival |

---

## Hook 1: PreToolUse - The Security Gatekeeper

**Execution Point**: After Claude creates tool parameters but before tool execution  
**Can Block Execution**: ✅ Yes (exit code 2)  
**Primary Purpose**: Security validation and input sanitization

### Available Tool Types
- `Task` - High-level task execution
- `Bash` - Shell command execution
- `Read` - File reading operations
- `Edit` - File editing operations
- `Write` - File writing operations
- `mcp__server__tool` - MCP tool calls (pattern: `mcp__servername__toolname`)

### JSON Input Structure
```json
{
  "session_id": "sess_12345",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "tool_name": "Write",
  "tool_input": {
    "path": "example.py",
    "content": "print('hello world')"
  },
  "stop_hook_active": false
}
```

### Python Implementation Example
```python
#!/usr/bin/env python3
"""PreToolUse Hook - Security Validation"""
import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, List

class PreToolUseValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Dangerous delete
            r"sudo\s+",       # Privilege escalation
            r"curl.*\|\s*bash", # Pipe to bash
            r"eval\s*\(",     # Dynamic code execution
        ]
        
        self.restricted_paths = [
            "/etc/",
            "/var/",
            "/usr/bin/",
            "~/.ssh/",
        ]
    
    def validate_tool_call(self, hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool call and return decision"""
        tool_name = hook_data.get("tool_name")
        tool_input = hook_data.get("tool_input", {})
        
        # Route to appropriate validator
        if tool_name == "Bash":
            return self.validate_bash_command(tool_input)
        elif tool_name in ["Write", "Edit"]:
            return self.validate_file_operation(tool_input)
        elif tool_name == "Read":
            return self.validate_file_read(tool_input)
        elif tool_name.startswith("mcp__"):
            return self.validate_mcp_call(tool_name, tool_input)
        else:
            return {"allowed": True, "reason": "Tool type allowed"}
    
    def validate_bash_command(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bash command for security"""
        command = tool_input.get("command", "")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": f"Dangerous pattern detected: {pattern}",
                    "suggestion": "Use safer alternatives or contact admin"
                }
        
        # Check for network operations requiring approval
        if any(net in command.lower() for net in ["curl", "wget", "ssh"]):
            return {
                "allowed": False,
                "reason": "Network operations require approval",
                "suggestion": "Submit network request through approval process"
            }
        
        return {"allowed": True, "reason": "Command validated"}
    
    def validate_file_operation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file write/edit operations"""
        file_path = tool_input.get("path", "")
        
        # Check restricted paths
        for restricted in self.restricted_paths:
            if file_path.startswith(restricted):
                return {
                    "allowed": False,
                    "reason": f"Access denied to restricted path: {restricted}",
                    "suggestion": "Use project directory for file operations"
                }
        
        # Check file extensions
        dangerous_extensions = [".exe", ".bat", ".sh", ".ps1"]
        if any(file_path.endswith(ext) for ext in dangerous_extensions):
            return {
                "allowed": False,
                "reason": "Executable file creation requires approval",
                "suggestion": "Contact admin for executable creation"
            }
        
        return {"allowed": True, "reason": "File operation validated"}
    
    def validate_file_read(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file read operations"""
        file_path = tool_input.get("path", "")
        
        # Block sensitive file access
        sensitive_files = [".env", "config.ini", "secrets.json"]
        if any(sensitive in file_path.lower() for sensitive in sensitive_files):
            return {
                "allowed": False,
                "reason": "Access denied to sensitive configuration files",
                "suggestion": "Use environment variables instead"
            }
        
        return {"allowed": True, "reason": "File read validated"}
    
    def validate_mcp_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MCP tool calls"""
        # Extract server and tool from name: mcp__server__tool
        parts = tool_name.split("__")
        if len(parts) >= 3:
            server = parts[1]
            tool = parts[2]
            
            # Implement server-specific validation
            if server == "dangerous_server":
                return {
                    "allowed": False,
                    "reason": f"Server {server} is not approved for use",
                    "suggestion": "Use approved MCP servers only"
                }
        
        return {"allowed": True, "reason": "MCP call validated"}

def main():
    """Main hook execution"""
    try:
        # Read JSON input from stdin
        hook_data = json.loads(sys.stdin.read())
        
        validator = PreToolUseValidator()
        result = validator.validate_tool_call(hook_data)
        
        if result["allowed"]:
            # Allow execution
            print(f"✅ Tool call approved: {result['reason']}")
            sys.exit(0)
        else:
            # Block execution and provide feedback
            print(f"❌ Tool call blocked: {result['reason']}")
            if "suggestion" in result:
                print(f"💡 Suggestion: {result['suggestion']}")
            sys.exit(2)  # Exit code 2 blocks execution
            
    except json.JSONDecodeError:
        print("❌ Invalid JSON input")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Common Pain Points
1. **Timeout Issues**: 60-second default timeout can be insufficient for complex validation
2. **False Positives**: Overly restrictive patterns can block legitimate operations
3. **Performance**: Complex validation can slow down tool execution
4. **Context Loss**: Hook runs independently, can't access full Claude conversation context

### Configuration Example
```json
{
  "hooks": {
    "PreToolUse": {
      "command": ["python", "/path/to/pre_tool_use.py"],
      "timeout": 30,
      "parallel": false
    }
  }
}
```

---

## Hook 2: PostToolUse - Quality Enforcement

**Execution Point**: Immediately after successful tool completion  
**Can Block Execution**: ❌ No (provides feedback only)  
**Primary Purpose**: Code formatting, testing, and result validation

### JSON Input Structure
```json
{
  "session_id": "sess_12345",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "tool_name": "Write",
  "tool_input": {
    "path": "example.py",
    "content": "print('hello world')"
  },
  "tool_output": "File written successfully",
  "stop_hook_active": false
}
```

### Python Implementation Example
```python
#!/usr/bin/env python3
"""PostToolUse Hook - Quality Enforcement"""
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class PostToolUseProcessor:
    def __init__(self):
        self.formatters = {
            '.py': ['black', '--quiet'],
            '.js': ['prettier', '--write'],
            '.ts': ['prettier', '--write'],
            '.json': ['jq', '.']
        }
        
        self.test_commands = {
            '.py': ['python', '-m', 'pytest', '--tb=short'],
            '.js': ['npm', 'test'],
            '.ts': ['npm', 'run', 'typecheck']
        }
    
    def process_tool_result(self, hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process tool result and apply quality checks"""
        tool_name = hook_data.get("tool_name")
        tool_input = hook_data.get("tool_input", {})
        
        results = []
        
        if tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("path", "")
            if file_path:
                results.extend(self.format_file(file_path))
                results.extend(self.run_tests_if_applicable(file_path))
                results.extend(self.validate_code_quality(file_path))
        
        return {"results": results, "success": len([r for r in results if not r.get("success", True)]) == 0}
    
    def format_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Auto-format files using appropriate formatters"""
        results = []
        path = Path(file_path)
        
        if not path.exists():
            return [{"action": "format", "success": False, "message": f"File not found: {file_path}"}]
        
        formatter = self.formatters.get(path.suffix.lower())
        if formatter:
            try:
                result = subprocess.run(
                    formatter + [str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    results.append({
                        "action": "format",
                        "success": True,
                        "message": f"Formatted {file_path} with {formatter[0]}"
                    })
                else:
                    results.append({
                        "action": "format",
                        "success": False,
                        "message": f"Formatting failed: {result.stderr}",
                        "suggestion": "Check file syntax and formatter configuration"
                    })
            except subprocess.TimeoutExpired:
                results.append({
                    "action": "format",
                    "success": False,
                    "message": f"Formatting timeout for {file_path}"
                })
        
        return results
    
    def run_tests_if_applicable(self, file_path: str) -> List[Dict[str, Any]]:
        """Run tests for applicable files"""
        results = []
        path = Path(file_path)
        
        # Only run tests for test files or if test files exist
        if "test" in file_path.lower() or self.has_tests_for_file(path):
            test_cmd = self.test_commands.get(path.suffix.lower())
            if test_cmd:
                try:
                    result = subprocess.run(
                        test_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=path.parent
                    )
                    
                    if result.returncode == 0:
                        results.append({
                            "action": "test",
                            "success": True,
                            "message": "Tests passed"
                        })
                    else:
                        results.append({
                            "action": "test",
                            "success": False,
                            "message": f"Tests failed:\n{result.stdout}\n{result.stderr}",
                            "suggestion": "Fix failing tests before continuing"
                        })
                except subprocess.TimeoutExpired:
                    results.append({
                        "action": "test",
                        "success": False,
                        "message": "Test execution timeout"
                    })
        
        return results
    
    def validate_code_quality(self, file_path: str) -> List[Dict[str, Any]]:
        """Validate code quality metrics"""
        results = []
        path = Path(file_path)
        
        if path.suffix == '.py':
            # Run pylint or flake8
            try:
                result = subprocess.run(
                    ['flake8', '--max-line-length=88', str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    results.append({
                        "action": "lint",
                        "success": True,
                        "message": "Code quality checks passed"
                    })
                else:
                    results.append({
                        "action": "lint",
                        "success": False,
                        "message": f"Code quality issues:\n{result.stdout}",
                        "suggestion": "Address linting issues for better code quality"
                    })
            except subprocess.TimeoutExpired:
                results.append({
                    "action": "lint",
                    "success": False,
                    "message": "Linting timeout"
                })
        
        return results
    
    def has_tests_for_file(self, file_path: Path) -> bool:
        """Check if tests exist for the given file"""
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"tests/test_{file_path.stem}.py"
        ]
        
        return any((file_path.parent / pattern).exists() for pattern in test_patterns)

def main():
    """Main hook execution"""
    try:
        hook_data = json.loads(sys.stdin.read())
        
        processor = PostToolUseProcessor()
        result = processor.process_tool_result(hook_data)
        
        # Output results for Claude to see
        for res in result["results"]:
            if res["success"]:
                print(f"✅ {res['action']}: {res['message']}")
            else:
                print(f"❌ {res['action']}: {res['message']}")
                if "suggestion" in res:
                    print(f"💡 {res['suggestion']}")
        
        # Exit code 2 shows error to Claude but doesn't block (tool already executed)
        if not result["success"]:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Hook error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Common Pain Points
1. **Tool Already Executed**: Can't prevent bad code from being written
2. **Async Formatting**: File formatting can interfere with Claude's next actions
3. **Test Dependencies**: Tests might require setup that's not available
4. **Performance Impact**: Heavy processing can slow down development flow

---

## Hook 3: UserPromptSubmit - Context Injection

**Execution Point**: When user submits a prompt  
**Can Block Execution**: ❌ No (context injection only)  
**Primary Purpose**: Context enhancement and prompt preprocessing

### JSON Input Structure
```json
{
  "session_id": "sess_12345",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "user_prompt": "Fix the bug in the authentication system",
  "stop_hook_active": false
}
```

### Python Implementation Example
```python
#!/usr/bin/env python3
"""UserPromptSubmit Hook - Context Injection"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import subprocess

class ContextInjector:
    def __init__(self):
        self.context_sources = [
            self.get_git_context,
            self.get_project_structure,
            self.get_recent_changes,
            self.get_error_logs,
            self.get_coding_standards
        ]
    
    def inject_context(self, hook_data: Dict[str, Any]) -> str:
        """Inject relevant context for the user prompt"""
        user_prompt = hook_data.get("user_prompt", "")
        cwd = hook_data.get("cwd", "")
        
        context_parts = []
        
        # Add project context header
        context_parts.append("=== PROJECT CONTEXT ===")
        
        # Gather context from all sources
        for source in self.context_sources:
            try:
                context = source(user_prompt, cwd)
                if context:
                    context_parts.append(context)
            except Exception as e:
                context_parts.append(f"Context error ({source.__name__}): {e}")
        
        # Add prompt-specific context
        if "bug" in user_prompt.lower() or "fix" in user_prompt.lower():
            context_parts.append(self.get_debugging_context(cwd))
        
        if "test" in user_prompt.lower():
            context_parts.append(self.get_testing_context(cwd))
        
        context_parts.append("=== END CONTEXT ===")
        
        return "\n\n".join(context_parts)
    
    def get_git_context(self, user_prompt: str, cwd: str) -> str:
        """Get relevant git context"""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=cwd, timeout=5
            )
            
            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True, text=True, cwd=cwd, timeout=5
            )
            
            # Get current status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=cwd, timeout=5
            )
            
            context = "Git Context:\n"
            context += f"Branch: {branch_result.stdout.strip()}\n"
            context += f"Recent commits:\n{log_result.stdout}"
            
            if status_result.stdout.strip():
                context += f"Modified files:\n{status_result.stdout}"
            
            return context
        except Exception:
            return "Git Context: Not available"
    
    def get_project_structure(self, user_prompt: str, cwd: str) -> str:
        """Get relevant project structure"""
        try:
            important_files = []
            path = Path(cwd)
            
            # Look for important files
            for pattern in ["*.py", "*.js", "*.ts", "*.json", "*.md", "*.yml", "*.yaml"]:
                important_files.extend(path.glob(pattern))
                important_files.extend(path.glob(f"*/{pattern}"))
            
            # Limit to most relevant files
            important_files = sorted(important_files)[:20]
            
            context = "Project Structure:\n"
            for file in important_files:
                relative_path = file.relative_to(path)
                context += f"  {relative_path}\n"
            
            return context
        except Exception:
            return "Project Structure: Not available"
    
    def get_recent_changes(self, user_prompt: str, cwd: str) -> str:
        """Get recent file changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~3"],
                capture_output=True, text=True, cwd=cwd, timeout=5
            )
            
            if result.stdout.strip():
                return f"Recent Changes:\n{result.stdout}"
            else:
                return "Recent Changes: No recent changes"
        except Exception:
            return "Recent Changes: Not available"
    
    def get_error_logs(self, user_prompt: str, cwd: str) -> str:
        """Get recent error logs if debugging"""
        if "error" not in user_prompt.lower() and "bug" not in user_prompt.lower():
            return ""
        
        try:
            log_files = []
            path = Path(cwd)
            
            # Look for log files
            for pattern in ["*.log", "logs/*.log", "log/*.log"]:
                log_files.extend(path.glob(pattern))
            
            if not log_files:
                return "Error Logs: No log files found"
            
            # Get recent errors from most recent log
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-50:]  # Last 50 lines
                error_lines = [line for line in lines if 'error' in line.lower()]
                
                if error_lines:
                    return f"Recent Errors (from {latest_log.name}):\n" + "".join(error_lines)
                else:
                    return "Error Logs: No recent errors found"
        except Exception:
            return "Error Logs: Not available"
    
    def get_coding_standards(self, user_prompt: str, cwd: str) -> str:
        """Get project coding standards"""
        try:
            standards_files = [".eslintrc", "pyproject.toml", ".flake8", "tslint.json"]
            path = Path(cwd)
            
            found_standards = []
            for std_file in standards_files:
                if (path / std_file).exists():
                    found_standards.append(std_file)
            
            if found_standards:
                return f"Coding Standards: Found {', '.join(found_standards)}"
            else:
                return "Coding Standards: No configuration files found"
        except Exception:
            return "Coding Standards: Not available"
    
    def get_debugging_context(self, cwd: str) -> str:
        """Get debugging-specific context"""
        context = "Debugging Context:\n"
        
        # Check for test files
        try:
            path = Path(cwd)
            test_files = list(path.glob("**/test_*.py")) + list(path.glob("**/*_test.py"))
            if test_files:
                context += f"Found {len(test_files)} test files\n"
            else:
                context += "No test files found\n"
        except Exception:
            context += "Could not check for test files\n"
        
        return context
    
    def get_testing_context(self, cwd: str) -> str:
        """Get testing-specific context"""
        try:
            # Check for test configuration
            path = Path(cwd)
            test_configs = ["pytest.ini", "setup.cfg", "pyproject.toml", "jest.config.js"]
            
            found_configs = []
            for config in test_configs:
                if (path / config).exists():
                    found_configs.append(config)
            
            context = "Testing Context:\n"
            if found_configs:
                context += f"Test configs: {', '.join(found_configs)}\n"
            else:
                context += "No test configuration found\n"
            
            return context
        except Exception:
            return "Testing Context: Not available"

def main():
    """Main hook execution"""
    try:
        hook_data = json.loads(sys.stdin.read())
        
        injector = ContextInjector()
        context = injector.inject_context(hook_data)
        
        # Output context to be injected into prompt
        print(context)
        
        # Always exit 0 for context injection
        sys.exit(0)
        
    except Exception as e:
        print(f"Context Error: {e}")
        sys.exit(0)  # Don't fail the prompt submission

if __name__ == "__main__":
    main()
```

### Common Pain Points
1. **Context Overload**: Too much context can exceed token limits
2. **Irrelevant Context**: Injecting context that's not useful for the prompt
3. **Performance**: Context gathering can slow prompt processing
4. **Stale Context**: Context might be outdated by the time Claude processes it

---

## Hook 4: SessionStart - Environment Setup

**Execution Point**: When sessions begin or resume  
**Can Block Execution**: ❌ No (setup only)  
**Primary Purpose**: Environment initialization and context loading

### JSON Input Structure
```json
{
  "session_id": "sess_12345",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "is_resume": false,
  "stop_hook_active": false
}
```

### Python Implementation Example
```python
#!/usr/bin/env python3
"""SessionStart Hook - Environment Setup"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
import subprocess

class SessionSetup:
    def __init__(self):
        self.setup_tasks = [
            self.load_environment_variables,
            self.check_dependencies,
            self.setup_git_hooks,
            self.load_project_context,
            self.validate_workspace
        ]
    
    def setup_session(self, hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup the development session"""
        session_id = hook_data.get("session_id")
        cwd = hook_data.get("cwd", "")
        is_resume = hook_data.get("is_resume", False)
        
        results = []
        
        print(f"🚀 Setting up session {session_id}")
        if is_resume:
            print("📂 Resuming existing session")
        
        # Run all setup tasks
        for task in self.setup_tasks:
            try:
                result = task(cwd, is_resume)
                results.append(result)
                if result["success"]:
                    print(f"✅ {result['task']}: {result['message']}")
                else:
                    print(f"⚠️  {result['task']}: {result['message']}")
            except Exception as e:
                results.append({
                    "task": task.__name__,
                    "success": False,
                    "message": f"Setup error: {e}"
                })
                print(f"❌ {task.__name__}: {e}")
        
        # Summary
        successful = len([r for r in results if r["success"]])
        print(f"\n📊 Setup complete: {successful}/{len(results)} tasks successful")
        
        return {"results": results, "success": successful > 0}
    
    def load_environment_variables(self, cwd: str, is_resume: bool) -> Dict[str, Any]:
        """Load project-specific environment variables"""
        env_files = [".env", ".env.local", ".env.development"]
        
        loaded_files = []
        for env_file in env_files:
            env_path = Path(cwd) / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                os.environ[key] = value
                    loaded_files.append(env_file)
                except Exception as e:
                    return {
                        "task": "Environment Variables",
                        "success": False,
                        "message": f"Error loading {env_file}: {e}"
                    }
        
        if loaded_files:
            return {
                "task": "Environment Variables",
                "success": True,
                "message": f"Loaded {', '.join(loaded_files)}"
            }
        else:
            return {
                "task": "Environment Variables",
                "success": True,
                "message": "No environment files found"
            }
    
    def check_dependencies(self, cwd: str, is_resume: bool) -> Dict[str, Any]:
        """Check if project dependencies are installed"""
        dependency_files = {
            "package.json": ["npm", "install"],
            "requirements.txt": ["pip", "install", "-r", "requirements.txt"],
            "Pipfile": ["pipenv", "install"],
            "pyproject.toml": ["pip", "install", "-e", "."]
        }
        
        path = Path(cwd)
        missing_deps = []
        
        for dep_file, install_cmd in dependency_files.items():
            if (path / dep_file).exists():
                # Check if dependencies are installed
                if dep_file == "package.json":
                    if not (path / "node_modules").exists():
                        missing_deps.append(f"Run: {' '.join(install_cmd)}")
                elif dep_file in ["requirements.txt", "Pipfile", "pyproject.toml"]:
                    # For Python, this is more complex, so we'll just suggest
                    if not is_resume:  # Only suggest on new sessions
                        missing_deps.append(f"Consider: {' '.join(install_cmd)}")
        
        if missing_deps:
            return {
                "task": "Dependencies",
                "success": False,
                "message": f"Possible missing dependencies: {'; '.join(missing_deps)}"
            }
        else:
            return {
                "task": "Dependencies",
                "success": True,
                "message": "Dependencies appear to be installed"
            }
    
    def setup_git_hooks(self, cwd: str, is_resume: bool) -> Dict[str, Any]:
        """Setup git hooks if needed"""
        try:
            git_dir = Path(cwd) / ".git"
            if not git_dir.exists():
                return {
                    "task": "Git Hooks",
                    "success": True,
                    "message": "Not a git repository"
                }
            
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            
            # Check for pre-commit
            pre_commit_hook = hooks_dir / "pre-commit"
            if not pre_commit_hook.exists():
                # Create a basic pre-commit hook
                hook_content = """#!/bin/bash
# Basic pre-commit hook
echo "Running pre-commit checks..."
exit 0
"""
                with open(pre_commit_hook, 'w') as f:
                    f.write(hook_content)
                pre_commit_hook.chmod(0o755)
                
                return {
                    "task": "Git Hooks",
                    "success": True,
                    "message": "Created basic pre-commit hook"
                }
            else:
                return {
                    "task": "Git Hooks",
                    "success": True,
                    "message": "Git hooks already configured"
                }
        except Exception as e:
            return {
                "task": "Git Hooks",
                "success": False,
                "message": f"Error setting up git hooks: {e}"
            }
    
    def load_project_context(self, cwd: str, is_resume: bool) -> Dict[str, Any]:
        """Load project-specific context and preferences"""
        context_files = ["CLAUDE.md", ".claude_context", "README.md"]
        path = Path(cwd)
        
        found_files = []
        for context_file in context_files:
            if (path / context_file).exists():
                found_files.append(context_file)
        
        if found_files:
            return {
                "task": "Project Context",
                "success": True,
                "message": f"Found context files: {', '.join(found_files)}"
            }
        else:
            return {
                "task": "Project Context",
                "success": True,
                "message": "No specific context files found"
            }
    
    def validate_workspace(self, cwd: str, is_resume: bool) -> Dict[str, Any]:
        """Validate workspace permissions and structure"""
        path = Path(cwd)
        
        # Check write permissions
        if not os.access(cwd, os.W_OK):
            return {
                "task": "Workspace Validation",
                "success": False,
                "message": "No write permissions in workspace"
            }
        
        # Check for common project indicators
        project_indicators = [
            "package.json", "setup.py", "pyproject.toml", 
            "Cargo.toml", "go.mod", "pom.xml", ".git"
        ]
        
        found_indicators = []
        for indicator in project_indicators:
            if (path / indicator).exists():
                found_indicators.append(indicator)
        
        if found_indicators:
            return {
                "task": "Workspace Validation",
                "success": True,
                "message": f"Project type detected: {', '.join(found_indicators)}"
            }
        else:
            return {
                "task": "Workspace Validation",
                "success": True,
                "message": "Generic workspace (no project files detected)"
            }

def main():
    """Main hook execution"""
    try:
        hook_data = json.loads(sys.stdin.read())
        
        setup = SessionSetup()
        result = setup.setup_session(hook_data)
        
        # Always exit 0 for session setup
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Session setup error: {e}")
        sys.exit(0)  # Don't fail session start

if __name__ == "__main__":
    main()
```

### Common Pain Points
1. **Slow Startup**: Complex setup tasks can delay session start
2. **Permission Issues**: Setup might need permissions not available
3. **Environment Conflicts**: Loading environment variables might conflict
4. **Network Dependencies**: Setup might require internet access

---

## Hook 5: SessionEnd - Cleanup and Persistence

**Execution Point**: When sessions terminate  
**Can Block Execution**: ❌ No (cleanup only)  
**Primary Purpose**: State persistence and cleanup operations

### Python Implementation Example
```python
#!/usr/bin/env python3
"""SessionEnd Hook - Cleanup and Persistence"""
import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class SessionCleanup:
    def __init__(self):
        self.cleanup_tasks = [
            self.backup_session_state,
            self.clean_temporary_files,
            self.update_session_metrics,
            self.save_workspace_state,
            self.cleanup_processes
        ]
    
    def cleanup_session(self, hook_data: Dict[str, Any]) -> None:
        """Clean up session and save state"""
        session_id = hook_data.get("session_id")
        cwd = hook_data.get("cwd", "")
        
        print(f"🧹 Cleaning up session {session_id}")
        
        for task in self.cleanup_tasks:
            try:
                result = task(session_id, cwd)
                if result["success"]:
                    print(f"✅ {result['task']}: {result['message']}")
                else:
                    print(f"⚠️  {result['task']}: {result['message']}")
            except Exception as e:
                print(f"❌ {task.__name__}: {e}")
        
        print("👋 Session cleanup complete")
    
    def backup_session_state(self, session_id: str, cwd: str) -> Dict[str, Any]:
        """Backup important session state"""
        backup_dir = Path.home() / ".claude_sessions" / session_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save session metadata
            metadata = {
                "session_id": session_id,
                "cwd": cwd,
                "ended_at": datetime.now().isoformat(),
                "files_modified": self.get_modified_files(cwd)
            }
            
            with open(backup_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "task": "Session Backup",
                "success": True,
                "message": f"State saved to {backup_dir}"
            }
        except Exception as e:
            return {
                "task": "Session Backup",
                "success": False,
                "message": f"Backup failed: {e}"
            }
    
    def get_modified_files(self, cwd: str) -> list:
        """Get list of files modified in this session"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, cwd=cwd, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')
            else:
                return []
        except Exception:
            return []

# Remaining hooks follow similar patterns...
```

---

## Hook Integration with Your Custom Governance System

### Bridging Native and Custom Hooks

```python
#!/usr/bin/env python3
"""Bridge between native Claude Code hooks and custom governance system"""
import json
import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "ai-assistant" / "backend"))

from governance.core.runtime_governance import RuntimeGovernanceSystem, HookType
from governance.core.runtime_governance import AgentContext, DecisionContext

class NativeToCustomBridge:
    def __init__(self):
        self.governance = RuntimeGovernanceSystem()
    
    async def handle_pre_tool_use(self, hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Bridge PreToolUse to custom PRE_DECISION hook"""
        # Convert native hook data to custom governance context
        context = DecisionContext(
            decision_id=f"tool_{hook_data.get('session_id', 'unknown')}",
            agent_id="claude_code",
            decision_type="tool_execution",
            input_data=hook_data.get("tool_input", {}),
            proposed_output=hook_data.get("tool_name"),
            confidence_score=1.0,
            risk_score=self.calculate_risk_score(hook_data)
        )
        
        # Run custom governance
        result = await self.governance.validate_decision(context)
        
        return {
            "allowed": result.decision == "approved",
            "reason": result.reason,
            "risk_level": result.risk_level
        }
    
    def calculate_risk_score(self, hook_data: Dict[str, Any]) -> float:
        """Calculate risk score based on tool and parameters"""
        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})
        
        base_risk = {
            "Bash": 0.8,
            "Write": 0.4,
            "Read": 0.2,
            "Edit": 0.5
        }.get(tool_name, 0.3)
        
        # Increase risk for dangerous patterns
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if any(danger in command for danger in ["sudo", "rm -rf", "curl |"]):
                base_risk = 0.95
        
        return base_risk

async def main():
    """Main bridge execution"""
    try:
        hook_data = json.loads(sys.stdin.read())
        bridge = NativeToCustomBridge()
        
        # Route to appropriate handler based on environment variable
        hook_type = os.environ.get("CLAUDE_HOOK_TYPE", "unknown")
        
        if hook_type == "PreToolUse":
            result = await bridge.handle_pre_tool_use(hook_data)
            
            if result["allowed"]:
                print(f"✅ Tool approved: {result['reason']}")
                sys.exit(0)
            else:
                print(f"❌ Tool blocked: {result['reason']}")
                sys.exit(2)
        else:
            print(f"⚠️  Unknown hook type: {hook_type}")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Bridge error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Management

### Complete Hook Configuration Example

```json
{
  "hooks": {
    "PreToolUse": {
      "command": ["python", "/path/to/hooks/pre_tool_use.py"],
      "timeout": 30,
      "parallel": false,
      "env": {
        "CLAUDE_HOOK_TYPE": "PreToolUse",
        "GOVERNANCE_LEVEL": "strict"
      }
    },
    "PostToolUse": {
      "command": ["python", "/path/to/hooks/post_tool_use.py"],
      "timeout": 60,
      "parallel": true,
      "env": {
        "CLAUDE_HOOK_TYPE": "PostToolUse",
        "AUTO_FORMAT": "true"
      }
    },
    "UserPromptSubmit": {
      "command": ["python", "/path/to/hooks/context_injector.py"],
      "timeout": 10,
      "parallel": false,
      "env": {
        "CLAUDE_HOOK_TYPE": "UserPromptSubmit",
        "MAX_CONTEXT_SIZE": "5000"
      }
    },
    "SessionStart": {
      "command": ["python", "/path/to/hooks/session_setup.py"],
      "timeout": 30,
      "parallel": false,
      "env": {
        "CLAUDE_HOOK_TYPE": "SessionStart"
      }
    },
    "SessionEnd": {
      "command": ["python", "/path/to/hooks/session_cleanup.py"],
      "timeout": 15,
      "parallel": false,
      "env": {
        "CLAUDE_HOOK_TYPE": "SessionEnd"
      }
    }
  },
  "permissions": {
    "allowTools": ["Read", "Write", "Edit"],
    "denyTools": ["Bash"],
    "allowPaths": ["/workspace/**"],
    "denyPaths": ["/etc/**", "/var/**"]
  }
}
```

## Summary and Best Practices

### Hook Implementation Principles
1. **Single Responsibility**: Each hook should have one clear purpose
2. **Fail Safe**: Hooks should fail gracefully and not break Claude's flow
3. **Performance**: Keep hooks fast - they run on every operation
4. **Logging**: Always log hook execution for debugging
5. **Testing**: Test hooks thoroughly in isolation

### Common Patterns
- **PreToolUse**: Security validation, input sanitization, permission checking
- **PostToolUse**: Code formatting, testing, quality checks
- **Context Hooks**: Environment setup, context injection, state management
- **Lifecycle Hooks**: Setup, cleanup, monitoring

### Integration Strategy
1. Start with simple hooks for critical operations (PreToolUse for security)
2. Add quality enforcement hooks (PostToolUse for formatting)
3. Enhance with context injection (UserPromptSubmit, SessionStart)
4. Complete with lifecycle management (SessionEnd)
5. Bridge to your custom governance system for unified control

This comprehensive implementation guide provides the foundation for building sophisticated governance and automation around Claude Code's native hook system.