# Folder Structure Guidelines

## Clean Architecture for AI Orchestration System

### Required Folder Structure

```
ai-assistant/
├── backend/
│   ├── api/                    # API endpoints and REST interfaces
│   │   ├── governance_api.py
│   │   └── main.py
│   │
│   ├── config/                 # Configuration files
│   │   ├── governance_config.json
│   │   ├── config.py
│   │   └── settings.json
│   │
│   ├── governance/             # Governance and validation modules
│   │   ├── governance_enforcer.py
│   │   ├── data_driven_governance.py
│   │   ├── development_enforcer.py
│   │   ├── rules_enforcement.py
│   │   └── validate_unicode_and_structure.py
│   │
│   ├── personas/               # AI Persona modules
│   │   ├── persona_manager.py
│   │   └── persona_cli.py
│   │
│   ├── cache/                  # Caching modules
│   │   ├── cache_manager.py
│   │   ├── cache_abstraction.py
│   │   ├── enhanced_cache_abstraction.py
│   │   └── three_tier_cache.py
│   │
│   ├── database/               # Database modules
│   │   ├── database_manager.py
│   │   ├── specialized_databases.py
│   │   └── test_db_mock.py
│   │
│   ├── core/                   # Core business logic
│   │   ├── orchestrator.py
│   │   ├── base_patterns.py
│   │   ├── metrics_collector.py
│   │   └── pty_manager.py
│   │
│   ├── integrations/           # External integrations
│   │   ├── claude_integration.py
│   │   ├── claude_unified_integration.py
│   │   └── auto_injection.py
│   │
│   ├── tests/                  # All test files
│   │   ├── test_orchestration.py
│   │   ├── test_governance.py
│   │   ├── test_cache/
│   │   ├── test_database/
│   │   └── test_personas/
│   │
│   ├── scripts/                # Utility scripts
│   │   ├── install_hooks.bat
│   │   ├── daily_governance.bat
│   │   └── quickstart.bat
│   │
│   └── docs/                   # Documentation
│       ├── CLAUDE.md
│       ├── QUICKSTART_GUIDE.md
│       └── GOVERNANCE_INTEGRATION.md
│
└── frontend/                   # Frontend application
    └── [frontend structure]
```

## Naming Conventions

### File Naming Rules

1. **Test Files**: `test_*.py`
   - Must start with `test_`
   - Should be in `tests/` folder
   - Example: `test_governance.py`

2. **Configuration Files**: `*_config.json` or `config_*.json`
   - Should be in `config/` folder
   - Example: `governance_config.json`

3. **API Files**: `*_api.py` or `api_*.py`
   - Should be in `api/` folder
   - Example: `governance_api.py`

4. **Module Files**: descriptive snake_case
   - Group by functionality
   - Example: `cache_manager.py`

## Organization Rules

### Maximum Files Per Folder
- **Limit**: 20 Python files per folder
- **Action**: Split into submodules when exceeded
- **Example**: Split tests into `test_cache/`, `test_database/`, etc.

### Separation of Concerns
1. **No mixing**: Don't mix test files with implementation
2. **Clear boundaries**: Each folder has a single responsibility
3. **Dependencies**: Core modules should not depend on integrations

### Import Structure
```python
# Good - organized imports
from cache.cache_manager import IntelligentCache
from personas.persona_manager import PersonaManager
from governance.rules_enforcement import RulesEngine

# Bad - scattered imports
from cache_manager import IntelligentCache
from persona_manager import PersonaManager
from rules_enforcement import RulesEngine
```

## Benefits of This Structure

1. **Clarity**: Easy to find files by function
2. **Scalability**: Can grow without becoming messy
3. **Testability**: Clear test organization
4. **Maintainability**: Related files grouped together
5. **Portability**: Easy to move modules to other projects

## Migration Plan

### Phase 1: Create Folders
```bash
mkdir api config governance personas cache database core integrations tests scripts docs
```

### Phase 2: Move Files
```bash
# Move test files
mv test_*.py tests/

# Move config files
mv *_config.json config/
mv config.py config/

# Move governance files
mv *governance*.py governance/
mv *enforcer*.py governance/
mv rules_enforcement.py governance/

# Move cache files
mv *cache*.py cache/

# Move database files
mv *database*.py database/
mv test_db_mock.py database/

# Move persona files
mv persona*.py personas/

# Move API files
mv *_api.py api/
mv main.py api/

# Move integration files
mv claude*.py integrations/
mv auto_injection.py integrations/

# Move core files
mv orchestrator.py core/
mv base_patterns.py core/
mv metrics_collector.py core/
mv pty_manager.py core/

# Move scripts
mv *.bat scripts/

# Move documentation
mv *.md docs/
```

### Phase 3: Update Imports
Update all Python files to use the new import paths:
```python
# Before
from cache_manager import IntelligentCache

# After  
from cache.cache_manager import IntelligentCache
```

### Phase 4: Update Configuration
Update paths in configuration files and scripts to reflect new structure.

## Validation

Run the folder structure validator to ensure compliance:
```bash
python governance/validate_unicode_and_structure.py
```

## Enforcement

The governance system will automatically:
1. Detect violations of folder structure rules
2. Suggest file movements
3. Prevent commits with structure violations (when hooks enabled)
4. Generate reports on structure health

## Exceptions

Some files may remain in the root for special purposes:
- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration
- `.pre-commit-config.yaml` - Hook configuration
- `README.md` - Project documentation

These are standard project files that tools expect in the root directory.