# Virtual Environment Automation Strategy

## Overview
Implement automatic virtual environment creation and management for the governance system to ensure isolation and reproducible environments.

## Implementation Plan

### Phase 1: Detection and Setup (Post Plugin Architecture)
```python
# libs/governance/environment/venv_manager.py

import os
import sys
import subprocess
import venv
from pathlib import Path
from typing import Optional, List

class VirtualEnvironmentManager:
    """Manages virtual environment lifecycle for the governance system."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / ".venv"
        self.requirements_file = project_root / "requirements.txt"
        self.python_executable = self._get_venv_python()
    
    def ensure_venv_exists(self) -> bool:
        """Create venv if it doesn't exist."""
        if not self.venv_path.exists():
            return self.create_venv()
        return True
    
    def create_venv(self) -> bool:
        """Create a new virtual environment."""
        try:
            venv.create(self.venv_path, with_pip=True, upgrade_deps=True)
            self._install_requirements()
            return True
        except Exception as e:
            print(f"Failed to create venv: {e}")
            return False
    
    def _get_venv_python(self) -> Path:
        """Get path to Python executable in venv."""
        if sys.platform == "win32":
            return self.venv_path / "Scripts" / "python.exe"
        return self.venv_path / "bin" / "python"
```

### Phase 2: Auto-Activation System
```python
# libs/governance/environment/auto_activate.py

def auto_activate_venv():
    """Automatically activate venv when running governance tools."""
    venv_manager = VirtualEnvironmentManager(Path.cwd())
    
    # Check if already in venv
    if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        return True
    
    # Ensure venv exists
    if not venv_manager.ensure_venv_exists():
        raise RuntimeError("Failed to setup virtual environment")
    
    # Restart script in venv
    if sys.executable != str(venv_manager.python_executable):
        os.execv(
            str(venv_manager.python_executable),
            [str(venv_manager.python_executable)] + sys.argv
        )
```

### Phase 3: Entry Point Wrapper
```python
# main.py (modified)

#!/usr/bin/env python
"""Main entry point with automatic venv activation."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from libs.governance.environment.auto_activate import auto_activate_venv

# Ensure we're running in venv
auto_activate_venv()

# Now import and run the actual application
from apps.api.main import main

if __name__ == "__main__":
    main()
```

### Phase 4: Platform-Specific Scripts

#### Windows (run.bat)
```batch
@echo off
setlocal

:: Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

:: Run the application
python main.py %*
```

#### Unix/Mac (run.sh)
```bash
#!/bin/bash

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Run the application
python main.py "$@"
```

## Integration Points

### 1. Git Hooks
```python
# .git/hooks/pre-commit (modified)
#!/usr/bin/env python

# Auto-activate venv before running validators
from libs.governance.environment.auto_activate import auto_activate_venv
auto_activate_venv()

# Continue with validation...
```

### 2. Plugin System
```python
# libs/governance/plugins/loader.py
class PluginLoader:
    def __init__(self):
        # Ensure venv is active
        auto_activate_venv()
        # Continue loading plugins...
```

### 3. Test Runner
```python
# run_tests.py
#!/usr/bin/env python

from libs.governance.environment.auto_activate import auto_activate_venv
auto_activate_venv()

import pytest
sys.exit(pytest.main())
```

## Requirements Management

### requirements.txt
```txt
# Core dependencies
pyyaml>=6.0
jsonschema>=4.0
watchdog>=3.0
msgpack>=1.0

# Testing
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21

# Development
black>=23.0
mypy>=1.0
ruff>=0.1
```

### requirements-dev.txt
```txt
-r requirements.txt

# Additional dev tools
ipython>=8.0
jupyter>=1.0
pre-commit>=3.0
```

## Benefits

1. **Isolation**: No global package pollution
2. **Reproducibility**: Consistent environments across machines
3. **Version Control**: Lock file for exact versions
4. **Easy Cleanup**: Just delete .venv folder
5. **CI/CD Ready**: Same process in pipelines

## Implementation Timeline

After completing the plugin architecture phases:

1. **Week 1**: Implement VirtualEnvironmentManager
2. **Week 1**: Add auto-activation to entry points
3. **Week 2**: Create platform-specific scripts
4. **Week 2**: Update all tools to use venv
5. **Week 3**: Test across platforms
6. **Week 3**: Update documentation
7. **Week 4**: CI/CD integration

## Configuration

### .env.config.yaml
```yaml
venv:
  auto_create: true
  auto_activate: true
  upgrade_pip: true
  install_dev_deps: false
  python_version: "3.10"
  
paths:
  venv_dir: ".venv"
  requirements: "requirements.txt"
  requirements_dev: "requirements-dev.txt"
  
behavior:
  check_updates: true
  update_frequency: "weekly"
  create_lockfile: true
```

## Error Handling

```python
class VenvError(Exception):
    """Base exception for venv-related errors."""
    pass

class VenvCreationError(VenvError):
    """Failed to create virtual environment."""
    pass

class VenvActivationError(VenvError):
    """Failed to activate virtual environment."""
    pass

class DependencyInstallError(VenvError):
    """Failed to install dependencies."""
    pass
```

## Testing Strategy

1. Test venv creation on all platforms
2. Test auto-activation logic
3. Test dependency installation
4. Test error recovery
5. Test CI/CD integration

## Notes

- Always use `.venv` as the standard venv directory name
- Add `.venv/` to `.gitignore`
- Document Python version requirements
- Consider using `pyproject.toml` for modern Python packaging
- Support both pip and poetry/pipenv as package managers

---

**Priority**: HIGH (implement after plugin architecture)
**Complexity**: MEDIUM
**Impact**: Improves isolation, reproducibility, and deployment