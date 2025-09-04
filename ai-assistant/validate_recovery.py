#!/usr/bin/env python3
"""
Dependency Recovery Validation Script
Validates that all recovery phases completed successfully
Recovery: Created 2025-09-03 (DEC-2025-010)
"""

import sys
import os
from pathlib import Path
import importlib.util
import json

class RecoveryValidator:
    """Validates recovery was successful"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def check(self, condition, description):
        """Check a condition and record result"""
        if condition:
            print(f"[PASS] {description}")
            self.passed += 1
            self.results.append({"test": description, "result": "PASS"})
            return True
        else:
            print(f"[FAIL] {description}")
            self.failed += 1
            self.results.append({"test": description, "result": "FAIL"})
            return False
    
    def validate_phase_1_backend_structure(self):
        """Validate Phase 1: Backend Structure"""
        print("\n=== PHASE 1: Backend Structure ===")
        
        # Check directories exist
        self.check(Path("backend/core").exists(), "Core directory exists")
        self.check(Path("backend/api").exists(), "API directory exists")
        self.check(Path("backend/cache").exists(), "Cache directory exists")
        self.check(Path("backend/database").exists(), "Database directory exists")
        self.check(Path("backend/schemas").exists(), "Schemas directory exists")
        
        # Check __init__.py files
        self.check(Path("backend/__init__.py").exists(), "Backend __init__.py exists")
        self.check(Path("backend/core/__init__.py").exists(), "Core __init__.py exists")
        self.check(Path("backend/api/__init__.py").exists(), "API __init__.py exists")
        
        # Check critical files
        self.check(Path("backend/core/config.py").exists(), "Config in core directory")
        self.check(Path("backend/core/auth.py").exists(), "Auth module exists")
        self.check(Path("backend/core/port_discovery.py").exists(), "Port discovery exists")
        
    def validate_phase_2_frontend_assets(self):
        """Validate Phase 2: Frontend Assets"""
        print("\n=== PHASE 2: Frontend Assets ===")
        
        # Check assets directory
        self.check(Path("src/assets").exists(), "Assets directory exists")
        self.check(Path("src/assets/icons").exists(), "Icons directory exists")
        self.check(Path("src/assets/images").exists(), "Images directory exists")
        self.check(Path("src/assets/fonts").exists(), "Fonts directory exists")
        
        # Check recovered files
        self.check(Path("check-pty.js").exists(), "check-pty.js recovered")
        self.check(Path("src/assets/icons/favicon.ico").exists(), "Favicon placeholder exists")
        
    def validate_phase_3_database_models(self):
        """Validate Phase 3: Database Models"""
        print("\n=== PHASE 3: Database Models ===")
        
        # Check database files
        self.check(Path("backend/database/models.py").exists(), "SQLAlchemy models exist")
        self.check(Path("backend/database/database.py").exists(), "Database module exists")
        self.check(Path("backend/database_schema.sql").exists(), "SQL schema exists")
        self.check(Path("backend/init_database.py").exists(), "Database init script exists")
        self.check(Path("backend/migrations").exists(), "Migrations directory exists")
        
    def validate_phase_4_startup(self):
        """Validate Phase 4: Startup Configuration"""
        print("\n=== PHASE 4: Startup Configuration ===")
        
        # Check package.json scripts
        if Path("package.json").exists():
            with open("package.json", "r") as f:
                package = json.load(f)
                scripts = package.get("scripts", {})
                
                self.check("backend" in scripts, "Backend script in package.json")
                self.check("dev" in scripts, "Dev script in package.json")
                self.check(scripts.get("backend") == "python backend/main.py", 
                          "Backend script configured correctly")
        
        # Check Electron backend manager
        self.check(Path("electron/backend-manager.js").exists(), 
                  "Electron backend manager exists")
        
    def validate_imports(self):
        """Validate Python imports work"""
        print("\n=== IMPORT VALIDATION ===")
        
        # Set Python path
        sys.path.insert(0, str(Path.cwd() / "backend"))
        
        try:
            from core.config import get_config, get_backend_url, is_development
            self.check(True, "Core config imports successfully")
        except ImportError as e:
            self.check(False, f"Core config import failed: {e}")
            
        try:
            from core.auth import get_current_user, verify_token
            self.check(True, "Auth module imports successfully")
        except ImportError as e:
            self.check(False, f"Auth import failed: {e}")
            
        try:
            from core.port_discovery import discover_backend_port
            self.check(True, "Port discovery imports successfully")
        except ImportError as e:
            self.check(False, f"Port discovery import failed: {e}")
            
        try:
            from database.models import Base
            self.check(True, "Database models import successfully")
        except ImportError as e:
            self.check(False, f"Database models import failed: {e}")
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("DEPENDENCY RECOVERY VALIDATION REPORT")
        print("=" * 60)
        
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            
            print(f"\nTests Passed: {self.passed}/{total} ({success_rate:.1f}%)")
            
            if self.failed > 0:
                print("\nFailed Tests:")
                for result in self.results:
                    if result["result"] == "FAIL":
                        print(f"  - {result['test']}")
            
            print("\n" + "=" * 60)
            
            if success_rate == 100:
                print("[SUCCESS] RECOVERY COMPLETE: All validations passed!")
                print("The application should now be functional.")
                return 0
            elif success_rate >= 80:
                print("[WARNING] RECOVERY PARTIAL: Most validations passed")
                print("Some issues remain but application may be functional.")
                return 1
            else:
                print("[ERROR] RECOVERY INCOMPLETE: Significant issues remain")
                print("Application is likely not functional.")
                return 2
        else:
            print("No tests executed")
            return 3

def main():
    """Run validation"""
    print("AI Assistant Dependency Recovery Validation")
    print("=" * 60)
    
    # Change to ai-assistant directory
    os.chdir(Path(__file__).parent)
    
    validator = RecoveryValidator()
    
    # Run all validations
    validator.validate_phase_1_backend_structure()
    validator.validate_phase_2_frontend_assets()
    validator.validate_phase_3_database_models()
    validator.validate_phase_4_startup()
    validator.validate_imports()
    
    # Generate report
    exit_code = validator.generate_report()
    
    # Save report to temp
    report_path = Path("../temp/recovery_validation.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump({
            "timestamp": "2025-09-03T23:00:00Z",
            "passed": validator.passed,
            "failed": validator.failed,
            "results": validator.results,
            "exit_code": exit_code
        }, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())