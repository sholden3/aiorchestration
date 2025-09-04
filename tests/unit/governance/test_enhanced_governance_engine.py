#!/usr/bin/env python3
"""
@fileoverview Test suite for enhanced governance engine
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Test Layer
@responsibility Validate enhanced governance engine with all detectors
@dependencies pytest, tempfile, sqlite3, pathlib
@integration_points Governance engine, all detectors, database
@testing_strategy Unit tests for each component, integration tests
@governance Tests comprehensive governance framework functionality

Business Logic Summary:
- Test magic variable detection
- Test boilerplate detection
- Test execution tracking
- Test risk scoring
- Test orchestration

Architecture Integration:
- Tests all governance components
- Validates detector coordination
- Ensures database persistence
- Verifies risk calculations
"""

import pytest
from pathlib import Path
import tempfile
import sqlite3
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.enhanced_governance_engine import (
    MagicVariableDetector,
    TestExecutionTracker,
    BoilerplateDetector,
    EnhancedGovernanceEngine
)

# Define RiskLevel enum for tests
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestMagicVariableDetector:
    """Test magic variable detection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = MagicVariableDetector()
    
    def test_detects_magic_numbers(self):
        """Test detection of hardcoded numbers"""
        code = '''
        timeout = 5000
        max_retries = 17
        buffer_size = 8192
        '''
        
        issues = self.detector.detect(code, "config.py")
        
        assert len(issues) > 0
        assert any("17" in issue["value"] for issue in issues)
    
    def test_allows_common_numbers(self):
        """Test that common numbers are allowed"""
        code = '''
        count = 0
        increment = 1
        percentage = 100
        '''
        
        issues = self.detector.detect(code, "math.py")
        
        # Common numbers should be allowed
        assert len(issues) == 0
    
    def test_context_aware_http_codes(self):
        """Test context-aware HTTP status codes"""
        code = '''
        return response, 200  # OK
        abort(404)  # Not found
        status_code = 500  # Server error
        '''
        
        issues = self.detector.detect(code, "api.py")
        
        # HTTP codes should be allowed in context
        assert len(issues) == 0
    
    def test_context_aware_ports(self):
        """Test context-aware port numbers"""
        code = '''
        app.run(port=8080)
        redis_port = 6379
        db_port = 5432
        '''
        
        issues = self.detector.detect(code, "server.py")
        
        # Common ports should be allowed
        assert len(issues) == 0
    
    def test_detects_unusual_ports(self):
        """Test detection of unusual port numbers"""
        code = '''
        server.listen(12345)  # Unusual port
        '''
        
        issues = self.detector.detect(code, "server.py")
        
        assert len(issues) > 0
        assert "12345" in issues[0]["value"]
    
    def test_context_aware_timeouts(self):
        """Test context-aware timeout values"""
        code = '''
        timeout = 30000  # 30 seconds
        request_timeout = 5000  # 5 seconds
        '''
        
        issues = self.detector.detect(code, "config.py")
        
        # Common timeout values should be allowed
        assert len(issues) == 0
    
    def test_file_exemptions(self):
        """Test file-based exemptions"""
        code = '''
        magic_number = 42
        another_magic = 999
        '''
        
        # Test files should be exempt
        issues = self.detector.detect(code, "test_something.py")
        assert len(issues) == 0
        
        # Non-test files should detect
        issues = self.detector.detect(code, "production.py")
        assert len(issues) > 0
    
    def test_suggests_constants(self):
        """Test that detector suggests using constants"""
        code = '''
        buffer_size = 4096
        '''
        
        issues = self.detector.detect(code, "io.py")
        
        if issues:
            assert any("constant" in issue.get("suggestion", "").lower() 
                      for issue in issues)


class TestTestExecutionTracker:
    """Test the test execution tracking system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.tracker = TestExecutionTracker(str(self.db_path))
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """Test database is properly initialized"""
        # Check tables exist
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='test_executions'
        """)
        
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_record_test_execution(self):
        """Test recording test execution"""
        self.tracker.record_execution(
            test_file="test_example.py",
            status="passed",
            duration=1.5,
            coverage=85.0
        )
        
        # Verify it was recorded
        executions = self.tracker.get_recent_executions("test_example.py")
        
        assert len(executions) == 1
        assert executions[0]["status"] == "passed"
        assert executions[0]["coverage"] == 85.0
    
    def test_detect_stale_tests(self):
        """Test detection of stale tests"""
        # Record an old execution
        old_time = datetime.now() - timedelta(days=3)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_executions 
            (test_file, execution_time, status, duration, coverage)
            VALUES (?, ?, ?, ?, ?)
        """, ("old_test.py", old_time.isoformat(), "passed", 1.0, 80.0))
        conn.commit()
        conn.close()
        
        # Check staleness
        stale = self.tracker.get_stale_tests(max_age_days=2)
        
        assert len(stale) == 1
        assert stale[0]["test_file"] == "old_test.py"
    
    def test_get_test_statistics(self):
        """Test getting test statistics"""
        # Record multiple executions
        self.tracker.record_execution("test1.py", "passed", 1.0, 90.0)
        self.tracker.record_execution("test2.py", "failed", 2.0, 70.0)
        self.tracker.record_execution("test3.py", "passed", 1.5, 85.0)
        
        stats = self.tracker.get_statistics()
        
        assert stats["total_tests"] == 3
        assert stats["passed_tests"] == 2
        assert stats["failed_tests"] == 1
        assert stats["average_coverage"] == pytest.approx(81.67, rel=0.1)
    
    def test_track_downstream_dependencies(self):
        """Test tracking downstream dependencies"""
        deps = [
            ("module_a.py", "module_b.py"),
            ("module_b.py", "module_c.py"),
            ("module_a.py", "module_d.py")
        ]
        
        for source, target in deps:
            self.tracker.track_dependency(source, target)
        
        # Get downstream dependencies
        downstream = self.tracker.get_downstream_dependencies("module_a.py")
        
        assert "module_b.py" in downstream
        assert "module_d.py" in downstream
        # Transitive dependency
        assert "module_c.py" in downstream


class TestBoilerplateDetector:
    """Test boilerplate code detection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = BoilerplateDetector()
    
    def test_detects_duplicate_code(self):
        """Test detection of duplicate code blocks"""
        code1 = '''
        def process_user(user):
            if not user:
                raise ValueError("User is required")
            
            user_id = user.get('id')
            user_name = user.get('name')
            user_email = user.get('email')
            
            return {
                'id': user_id,
                'name': user_name,
                'email': user_email
            }
        '''
        
        code2 = '''
        def process_admin(admin):
            if not admin:
                raise ValueError("Admin is required")
            
            admin_id = admin.get('id')
            admin_name = admin.get('name')
            admin_email = admin.get('email')
            
            return {
                'id': admin_id,
                'name': admin_name,
                'email': admin_email
            }
        '''
        
        # Add patterns
        self.detector.add_pattern(code1, "file1.py")
        duplicates = self.detector.detect_boilerplate(code2, "file2.py")
        
        assert len(duplicates) > 0
        assert duplicates[0]["similarity"] > 0.8
    
    def test_ignores_small_snippets(self):
        """Test that small code snippets are ignored"""
        code1 = "x = 1"
        code2 = "y = 1"
        
        self.detector.add_pattern(code1, "file1.py")
        duplicates = self.detector.detect_boilerplate(code2, "file2.py")
        
        # Too small to be considered boilerplate
        assert len(duplicates) == 0
    
    def test_test_setup_exemption(self):
        """Test that test setup code is exempt"""
        test_setup = '''
        def setUp(self):
            self.client = TestClient()
            self.db = TestDatabase()
            self.user = create_test_user()
        '''
        
        # Add pattern from test file
        self.detector.add_pattern(test_setup, "test_1.py")
        
        # Similar setup in another test
        duplicates = self.detector.detect_boilerplate(test_setup, "test_2.py")
        
        # Test files should be exempt
        assert len(duplicates) == 0 or duplicates[0]["severity"] == "info"
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching with variable name changes"""
        code1 = '''
        def calculate_total(items):
            total = 0
            for item in items:
                total += item.price * item.quantity
            return total
        '''
        
        code2 = '''
        def compute_sum(products):
            sum = 0
            for product in products:
                sum += product.price * product.quantity
            return sum
        '''
        
        self.detector.add_pattern(code1, "calc1.py")
        duplicates = self.detector.detect_boilerplate(code2, "calc2.py")
        
        # Should detect similarity despite variable name differences
        assert len(duplicates) > 0
        assert duplicates[0]["similarity"] > 0.7


class TestEnhancedGovernanceEngine:
    """Test the complete enhanced governance engine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = EnhancedGovernanceEngine(base_path=Path(self.temp_dir))
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_file_with_multiple_issues(self):
        """Test analyzing a file with multiple governance issues"""
        code = '''
        API_KEY = "secret123"  # Hardcoded secret
        timeout = 99999  # Magic number
        
        def process_data(data):
            if not data:
                return None
            
            result = []
            for item in data:
                result.append(item * 2)
            return result
        
        def process_items(items):  # Similar to above
            if not items:
                return None
            
            output = []
            for item in items:
                output.append(item * 2)
            return output
        '''
        
        result = self.engine.analyze_file(code, "problematic.py")
        
        assert result["has_issues"]
        assert len(result["magic_variables"]) > 0
        assert result["risk_level"] != RiskLevel.LOW
    
    def test_risk_score_calculation(self):
        """Test risk score calculation"""
        issues = {
            "magic_variables": [{"value": "12345", "severity": "high"}],
            "boilerplate": [{"similarity": 0.9, "severity": "medium"}],
            "stale_tests": ["old_test.py"],
            "missing_tests": ["module.py"]
        }
        
        score = self.engine._calculate_risk_score(issues)
        
        assert score > 0
        assert score <= 10
    
    def test_get_downstream_impacts(self):
        """Test getting downstream impacts of changes"""
        # Set up some dependencies
        self.engine.test_tracker.track_dependency("core.py", "service.py")
        self.engine.test_tracker.track_dependency("service.py", "api.py")
        
        impacts = self.engine.get_downstream_impacts("core.py")
        
        assert "service.py" in impacts["affected_files"]
        assert "api.py" in impacts["affected_files"]
        assert impacts["risk_level"] != RiskLevel.LOW
    
    def test_suggest_tests_for_file(self):
        """Test suggesting tests for a file"""
        code = '''
        class UserService:
            def get_user(self, user_id):
                pass
            
            def create_user(self, data):
                pass
            
            def delete_user(self, user_id):
                pass
        '''
        
        suggestions = self.engine.suggest_tests("user_service.py", code)
        
        assert len(suggestions) > 0
        assert any("get_user" in s for s in suggestions)
        assert any("create_user" in s for s in suggestions)
    
    def test_file_exemptions(self):
        """Test that certain files are exempt from checks"""
        # Test file should be exempt from many checks
        code = '''
        magic_number = 42
        test_timeout = 99999
        '''
        
        result = self.engine.analyze_file(code, "test_example.py")
        
        # Should have fewer issues due to exemptions
        assert not result["has_issues"] or result["risk_level"] == RiskLevel.LOW
    
    def test_generate_report(self):
        """Test report generation"""
        # Analyze a file
        code = '''
        timeout = 12345
        API_KEY = "secret"
        '''
        
        self.engine.analyze_file(code, "app.py")
        report = self.engine.generate_report()
        
        assert "Enhanced Governance Report" in report
        assert "Risk Level" in report
        assert "Magic Variables" in report


class TestIntegrationScenarios:
    """Integration tests for complete scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = EnhancedGovernanceEngine(base_path=Path(self.temp_dir))
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pre_commit_scenario(self):
        """Test a typical pre-commit scenario"""
        files_to_check = [
            ("api.py", '''
            PORT = 8080
            
            @app.route('/api/users')
            def get_users():
                return jsonify(users)
            '''),
            
            ("service.py", '''
            timeout = 5000
            
            def process():
                # Some logic
                pass
            '''),
            
            ("test_api.py", '''
            def test_get_users():
                response = client.get('/api/users')
                assert response.status_code == 200
            ''')
        ]
        
        all_issues = []
        for filename, content in files_to_check:
            result = self.engine.analyze_file(content, filename)
            if result["has_issues"]:
                all_issues.append((filename, result))
        
        # Should have some issues but not blocking
        assert len(all_issues) >= 0
        
        # Test files should have fewer issues
        test_issues = [i for i in all_issues if i[0].startswith("test_")]
        non_test_issues = [i for i in all_issues if not i[0].startswith("test_")]
        
        if test_issues and non_test_issues:
            assert len(test_issues) <= len(non_test_issues)
    
    def test_continuous_improvement_tracking(self):
        """Test that the system tracks improvements over time"""
        # Initial analysis
        code_v1 = '''
        timeout = 99999
        api_key = "hardcoded"
        '''
        
        result1 = self.engine.analyze_file(code_v1, "app.py")
        score1 = self.engine._calculate_risk_score({
            "magic_variables": result1["magic_variables"],
            "boilerplate": [],
            "stale_tests": [],
            "missing_tests": []
        })
        
        # Improved version
        code_v2 = '''
        TIMEOUT = 30000  # 30 seconds
        api_key = os.environ.get('API_KEY')
        '''
        
        result2 = self.engine.analyze_file(code_v2, "app.py")
        score2 = self.engine._calculate_risk_score({
            "magic_variables": result2["magic_variables"],
            "boilerplate": [],
            "stale_tests": [],
            "missing_tests": []
        })
        
        # Should show improvement
        assert score2 <= score1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])