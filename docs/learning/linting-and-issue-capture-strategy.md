# Linting and Automatic Issue Capture Strategy

**Date**: 2025-01-27  
**Version**: 1.0  
**Purpose**: Establish comprehensive linting and issue detection before proceeding  
**Specialists**: All participating in strategy discussion  

---

## 🎯 Strategic Overview

### Why Linters and Issue Capture Now?

**Dr. Sarah Chen**: "Better to catch issues automatically than discover them at 3 AM. What breaks first? Code without linting. How do we know? When production fails. What's Plan B? Automated detection."

**Alex Novak**: "Every issue caught by a linter is one less 3 AM debugging session. We need defense in depth."

---

## 🛠️ Recommended Tool Stack

### Python (Backend)

#### 1. **Linting & Code Quality**
```bash
# Core linters
pip install pylint         # Comprehensive linting
pip install flake8         # Style guide enforcement
pip install black          # Code formatter
pip install isort          # Import sorting
pip install mypy           # Static type checking

# Security
pip install bandit         # Security issue scanner
pip install safety         # Dependency vulnerability scanner

# Code complexity
pip install radon          # Complexity metrics
pip install xenon          # Complexity monitoring

# Documentation
pip install pydocstyle     # Docstring linting
pip install interrogate    # Documentation coverage
```

#### 2. **Configuration Files**

**.pylintrc**:
```ini
[MESSAGES CONTROL]
# Phase 2.5: Relaxed for now
disable=
    missing-module-docstring,  # Will fix in Week 2
    missing-class-docstring,   # Will fix in Week 2
    too-few-public-methods,    # Sometimes okay
    fixme,                      # Allow TODO/FIXME for now

[FORMAT]
max-line-length=120
indent-string='    '

[BASIC]
good-names=i,j,k,ex,_,df,id

[DESIGN]
max-args=7
max-attributes=10
```

**pyproject.toml** (for black and isort):
```toml
[tool.black]
line-length = 120
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true  # Relaxed for Phase 2.5
```

### TypeScript/JavaScript (Frontend)

#### 1. **Linting & Code Quality**
```bash
# Core linters
npm install -D eslint
npm install -D @typescript-eslint/parser
npm install -D @typescript-eslint/eslint-plugin
npm install -D prettier
npm install -D eslint-config-prettier
npm install -D eslint-plugin-prettier

# Angular specific
npm install -D @angular-eslint/eslint-plugin
npm install -D @angular-eslint/eslint-plugin-template
npm install -D @angular-eslint/schematics

# Security
npm install -D eslint-plugin-security
npm install -D eslint-plugin-sonarjs

# Code quality
npm install -D eslint-plugin-import
npm install -D eslint-plugin-jsdoc
npm install -D eslint-plugin-prefer-arrow
```

#### 2. **Configuration Files**

**.eslintrc.json**:
```json
{
  "root": true,
  "ignorePatterns": ["projects/**/*"],
  "overrides": [
    {
      "files": ["*.ts"],
      "parserOptions": {
        "project": ["tsconfig.json"],
        "createDefaultProgram": true
      },
      "extends": [
        "plugin:@angular-eslint/recommended",
        "plugin:@angular-eslint/template/process-inline-templates",
        "plugin:prettier/recommended"
      ],
      "rules": {
        // Phase 2.5: Relaxed rules
        "@angular-eslint/directive-selector": [
          "error",
          {
            "type": "attribute",
            "prefix": "app",
            "style": "camelCase"
          }
        ],
        "@typescript-eslint/no-explicit-any": "warn",  // Warning only for now
        "@typescript-eslint/no-unused-vars": "warn",   // Warning only
        "no-console": "warn",                           // Warning only
        "jsdoc/require-jsdoc": "warn"                  // Warning only
      }
    }
  ]
}
```

### Shell Scripts

#### 1. **Linting Tools**
```bash
# Shell script linting
sudo apt-get install shellcheck  # Or brew install shellcheck on Mac

# YAML linting
npm install -g yaml-lint

# Markdown linting
npm install -g markdownlint-cli
```

---

## 🔍 Automatic Issue Capture Tools

### 1. **SonarQube / SonarLint** (Comprehensive)
```yaml
# sonar-project.properties
sonar.projectKey=ai-assistant
sonar.sources=ai-assistant/src,ai-assistant/backend
sonar.exclusions=**/*.spec.ts,**/node_modules/**
sonar.tests=ai-assistant/src,ai-assistant/backend/tests
sonar.test.inclusions=**/*.spec.ts,**/test_*.py
sonar.python.coverage.reportPaths=coverage.xml
sonar.javascript.lcov.reportPaths=coverage/lcov.info
```

### 2. **Pre-commit Framework** (Git Integration)
```yaml
# .pre-commit-config.yaml
repos:
  # Python
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--ignore=E203,W503']
        
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ['-ll', '--skip=B101']  # Relaxed for Phase 2.5
        
  # TypeScript/JavaScript
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.35.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        
  # Shell
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.2
    hooks:
      - id: shellcheck
        
  # Security
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### 3. **VS Code Settings** (Developer Experience)
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "typescript.updateImportsOnFileMove.enabled": "always",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## 📊 Progressive Linting Strategy

### Week 1: Detection Only
```javascript
// All linters in warning mode
{
  "rules": {
    "all-rules": "warn"  // Nothing blocks, everything warns
  }
}
```

### Week 2: Critical Rules Block
```javascript
{
  "rules": {
    "no-unused-vars": "error",      // Now blocking
    "no-explicit-any": "warn",      // Still warning
    "complexity": ["warn", 10]      // Warning only
  }
}
```

### Week 3: Most Rules Block
```javascript
{
  "rules": {
    "no-unused-vars": "error",
    "no-explicit-any": "error",     // Now blocking
    "complexity": ["error", 10],    // Now blocking
    "jsdoc/require-jsdoc": "warn"   // Still warning
  }
}
```

### Week 4: Full Enforcement
```javascript
{
  "rules": {
    // All rules at error level
  }
}
```

---

## 🎯 Implementation Priority

### Immediate (Before Any More Code)

1. **Install Core Linters**
```bash
# Backend
cd ai-assistant/backend
pip install pylint flake8 black isort mypy bandit

# Frontend
cd ai-assistant
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier

# Global
npm install -g markdownlint-cli
```

2. **Create Configuration Files**
- Copy configurations from above
- Set all rules to "warn" initially
- Commit configurations

3. **Run Baseline Scan**
```bash
# Capture current state
pylint ai-assistant/backend > linting-baseline-python.txt
eslint ai-assistant/src > linting-baseline-typescript.txt
```

4. **Setup IDE Integration**
- Install VS Code extensions
- Copy settings.json
- Test auto-formatting works

### This Week

1. **Fix Critical Issues Only**
- Security vulnerabilities
- Obvious bugs
- Syntax errors

2. **Track Everything Else**
```markdown
## Linting Debt
- Python: 234 warnings
- TypeScript: 567 warnings
- Target: Reduce by 50% each week
```

### Next Week

1. **Enable Blocking for Critical Rules**
2. **Fix 50% of warnings**
3. **Add pre-commit hooks**

---

## 🚨 Critical Linting Rules to Enable NOW

### Python - Security Critical
```python
# These should error immediately:
- B104: hardcoded_bind_all_interfaces
- B105: hardcoded_password_string
- B106: hardcoded_password_funcarg
- B107: hardcoded_password_default
- B108: hardcoded_tmp_directory
- B601: shell_injection
- B602: subprocess_popen_with_shell_equals_true
```

### TypeScript - Security Critical
```javascript
// These should error immediately:
- "no-eval": "error"
- "no-implied-eval": "error"
- "security/detect-non-literal-regexp": "error"
- "security/detect-unsafe-regex": "error"
- "security/detect-buffer-noassert": "error"
- "security/detect-child-process": "error"
- "security/detect-disable-mustache-escape": "error"
```

---

## 🎓 Team Consensus

### Sam Martinez v3.2.0
"Linting is like testing - start with detection, then enforcement. Track everything, fix progressively."

### Dr. Sarah Chen v1.2
"Every linter warning is a future 3 AM call prevented. But don't let perfect linting block progress."

### Alex Novak v3.0
"Auto-formatting on save is non-negotiable. Consistent code is debuggable code."

### Riley Thompson v1.1
"Integrate linting into CI/CD from Day 1, but as warnings initially. Graduate to errors."

### Quinn Roberts v1.1
"Document why we disable rules. Every suppression needs justification."

---

## ✅ Decision

**Unanimous Agreement**: Implement linting with progressive enforcement

1. **Install all linters TODAY**
2. **Configure in warning mode**
3. **Track all issues found**
4. **Fix security issues immediately**
5. **Progressive enforcement per week**
6. **Full enforcement by Week 4**

---

**This gives us automatic issue detection without blocking progress.**