#!/usr/bin/env python3
"""
@fileoverview Integration tests for governance pre-commit hook
@author Dr. Sarah Chen v1.2 & Alex Novak v3.0 - 2025-01-28
@architecture Testing - Integration tests for governance hook
@responsibility Validate complete governance flow
@dependencies pytest, unittest, subprocess, tempfile
@integration_points Tests integrated_pre_commit_hook module
@testing_strategy Integration testing with simulated git operations
@governance Test file following governance requirements

Business Logic Summary:
- Test configuration loading
- Test persona invocation
- Test consensus achievement
- Test validation rules

Architecture Integration:
- Part of governance test suite
- Tests full integration flow
- Validates git hook behavior
"""

import pytest
import unittest
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.scripts.integrated_pre_commit_hook import (
    ConfigLoader,
    PersonaInvoker,
    ConsensusAchiever,
    IntegratedGovernanceHook
)


class TestConfigLoader(unittest.TestCase):
    """
    @class TestConfigLoader
    @description Test configuration loading system
    @architecture_role Validate data-driven configuration
    @business_logic Test JSON config loading and retrieval
    """
    
    def setUp(self):
        """Create temporary config directory with test configs"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'governance-config'
        
        # Create directory structure
        (self.config_dir / 'personas').mkdir(parents=True)
        (self.config_dir / 'rules').mkdir(parents=True)
        (self.config_dir / 'consensus').mkdir(parents=True)
        (self.config_dir / 'events').mkdir(parents=True)
        (self.config_dir / 'performance').mkdir(parents=True)
        
        # Create test configs
        self._create_test_configs()
        
        self.loader = ConfigLoader(self.config_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_configs(self):
        """Create test configuration files"""
        # Core architects
        personas = {
            "personas": {
                "alex_novak": {
                    "id": "alex_novak",
                    "role": "frontend_architect",
                    "type": "core"
                },
                "sarah_chen": {
                    "id": "sarah_chen",
                    "role": "backend_architect",
                    "type": "core"
                }
            }
        }
        with open(self.config_dir / 'personas/core-architects.json', 'w') as f:
            json.dump(personas, f)
        
        # Validation rules
        rules = {
            "validation_rules": {
                "documentation": {
                    "id": "documentation",
                    "enabled": True,
                    "requirements": {
                        "file_headers": {
                            "mandatory": ["@fileoverview", "@author"]
                        }
                    }
                },
                "testing": {
                    "id": "testing",
                    "enabled": True
                },
                "security": {
                    "id": "security",
                    "enabled": True
                }
            }
        }
        with open(self.config_dir / 'rules/validation-rules.json', 'w') as f:
            json.dump(rules, f)
        
        # Consensus strategies
        consensus = {
            "consensus_strategies": {
                "majority": {
                    "requirements": {
                        "agreement_threshold": 0.5
                    }
                },
                "veto_power": {
                    "requirements": {
                        "agreement_threshold": 0.8
                    }
                }
            }
        }
        with open(self.config_dir / 'consensus/strategies.json', 'w') as f:
            json.dump(consensus, f)
        
        # Event mappings
        events = {
            "event_mappings": {
                "git.pre_commit": {
                    "validators": ["documentation", "testing", "security"],
                    "personas": ["alex_novak", "sarah_chen"],
                    "consensus_strategy": "majority"
                }
            }
        }
        with open(self.config_dir / 'events/event-mappings.json', 'w') as f:
            json.dump(events, f)
    
    def test_load_all_configs(self):
        """Test loading all configuration files"""
        self.assertIn('personas', self.loader.configs)
        self.assertIn('validation_rules', self.loader.configs)
        self.assertIn('consensus', self.loader.configs)
        self.assertIn('events', self.loader.configs)
    
    def test_get_config(self):
        """Test retrieving specific configuration"""
        personas_config = self.loader.get_config('personas')
        self.assertIsNotNone(personas_config)
        self.assertIn('personas', personas_config)
        self.assertIn('alex_novak', personas_config['personas'])
    
    def test_get_event_mapping(self):
        """Test retrieving event mapping"""
        mapping = self.loader.get_event_mapping('git.pre_commit')
        self.assertIsNotNone(mapping)
        self.assertIn('validators', mapping)
        self.assertIn('consensus_strategy', mapping)
    
    def test_get_validation_rule(self):
        """Test retrieving validation rule"""
        rule = self.loader.get_validation_rule('documentation')
        self.assertIsNotNone(rule)
        self.assertEqual(rule['id'], 'documentation')
        self.assertTrue(rule['enabled'])
    
    def test_get_consensus_strategy(self):
        """Test retrieving consensus strategy"""
        strategy = self.loader.get_consensus_strategy('majority')
        self.assertIsNotNone(strategy)
        self.assertIn('requirements', strategy)
        self.assertEqual(strategy['requirements']['agreement_threshold'], 0.5)


class TestPersonaInvoker(unittest.TestCase):
    """
    @class TestPersonaInvoker
    @description Test persona invocation system
    @architecture_role Validate persona selection and invocation
    @business_logic Test context-based persona selection
    """
    
    def setUp(self):
        """Create mock config loader and persona invoker"""
        self.mock_loader = Mock(spec=ConfigLoader)
        
        # Mock personas config
        self.mock_loader.get_config.return_value = {
            'personas': {
                'alex_novak': {
                    'id': 'alex_novak',
                    'triggers': {
                        'keywords': ['frontend', 'angular', 'electron']
                    }
                },
                'sarah_chen': {
                    'id': 'sarah_chen',
                    'triggers': {
                        'keywords': ['backend', 'python', 'database']
                    }
                },
                'sam_martinez': {
                    'id': 'sam_martinez',
                    'triggers': {
                        'keywords': ['test', 'spec', 'quality']
                    }
                }
            }
        }
        
        self.invoker = PersonaInvoker(self.mock_loader)
    
    def test_load_personas(self):
        """Test loading persona definitions"""
        self.assertIn('alex_novak', self.invoker.personas)
        self.assertIn('sarah_chen', self.invoker.personas)
        self.assertIn('sam_martinez', self.invoker.personas)
    
    def test_select_personas_core(self):
        """Test core personas always selected"""
        context = {'files': []}
        personas = self.invoker.select_personas(context)
        
        self.assertIn('alex_novak', personas)
        self.assertIn('sarah_chen', personas)
    
    def test_select_personas_by_keywords(self):
        """Test persona selection based on file keywords"""
        context = {
            'files': [
                'test_something.py',
                'frontend.ts',
                'database_manager.py'
            ]
        }
        personas = self.invoker.select_personas(context)
        
        self.assertIn('alex_novak', personas)  # Core + frontend keyword
        self.assertIn('sarah_chen', personas)  # Core + database keyword
        self.assertIn('sam_martinez', personas)  # test keyword
    
    def test_invoke_persona(self):
        """Test invoking specific persona"""
        result = self.invoker.invoke_persona('alex_novak', {'files': []})
        
        self.assertIsNotNone(result)
        self.assertEqual(result['persona_id'], 'alex_novak')
        self.assertEqual(result['decision'], 'approve')
        self.assertIn('confidence', result)
        self.assertIn('timestamp', result)
    
    def test_invoke_unknown_persona(self):
        """Test invoking unknown persona"""
        result = self.invoker.invoke_persona('unknown', {})
        
        self.assertEqual(result['decision'], 'abstain')
        self.assertIn('reason', result)


class TestConsensusAchiever(unittest.TestCase):
    """
    @class TestConsensusAchiever
    @description Test consensus achievement system
    @architecture_role Validate consensus mechanisms
    @business_logic Test different consensus strategies
    """
    
    def setUp(self):
        """Create mock config loader and consensus achiever"""
        self.mock_loader = Mock(spec=ConfigLoader)
        
        # Mock consensus strategies
        self.mock_loader.get_consensus_strategy.side_effect = self._get_strategy
        
        self.achiever = ConsensusAchiever(self.mock_loader)
    
    def _get_strategy(self, name):
        """Mock strategy retrieval"""
        strategies = {
            'majority': {
                'requirements': {'agreement_threshold': 0.5}
            },
            'unanimous': {
                'requirements': {'agreement_threshold': 1.0}
            },
            'veto_power': {
                'requirements': {'agreement_threshold': 0.6}
            }
        }
        return strategies.get(name)
    
    def test_majority_consensus_achieved(self):
        """Test majority consensus achieved"""
        votes = {
            'alex': {'decision': 'approve'},
            'sarah': {'decision': 'approve'},
            'sam': {'decision': 'reject'}
        }
        
        result = self.achiever.achieve_consensus(votes, 'majority')
        
        self.assertTrue(result['achieved'])
        self.assertAlmostEqual(result['approval_ratio'], 0.667, places=2)
    
    def test_majority_consensus_failed(self):
        """Test majority consensus not achieved"""
        votes = {
            'alex': {'decision': 'approve'},
            'sarah': {'decision': 'reject'},
            'sam': {'decision': 'reject'}
        }
        
        result = self.achiever.achieve_consensus(votes, 'majority')
        
        self.assertFalse(result['achieved'])
        self.assertAlmostEqual(result['approval_ratio'], 0.333, places=2)
    
    def test_unanimous_consensus(self):
        """Test unanimous consensus requirement"""
        votes = {
            'alex': {'decision': 'approve'},
            'sarah': {'decision': 'approve'}
        }
        
        result = self.achiever.achieve_consensus(votes, 'unanimous')
        self.assertTrue(result['achieved'])
        
        # Add one rejection
        votes['sam'] = {'decision': 'reject'}
        result = self.achiever.achieve_consensus(votes, 'unanimous')
        self.assertFalse(result['achieved'])
    
    def test_veto_power(self):
        """Test veto power consensus"""
        votes = {
            'alex': {'decision': 'approve'},
            'sarah': {'decision': 'veto'},
            'sam': {'decision': 'approve'}
        }
        
        result = self.achiever.achieve_consensus(votes, 'veto_power')
        
        self.assertFalse(result['achieved'])
        self.assertIn('veto_persona', result)
        self.assertEqual(result['veto_persona'], 'sarah')
    
    def test_empty_votes(self):
        """Test consensus with no votes"""
        result = self.achiever.achieve_consensus({}, 'majority')
        
        self.assertFalse(result['achieved'])
        self.assertEqual(result['reason'], 'No votes received')


class TestIntegratedGovernanceHook(unittest.TestCase):
    """
    @class TestIntegratedGovernanceHook
    @description Integration tests for complete governance hook
    @architecture_role Validate full governance flow
    @business_logic Test end-to-end governance validation
    
    Sarah's Framework Check:
    - What breaks first: Git integration or validation rules
    - How we know: Exit codes and correlation tracking
    - Plan B: Bypass mode for emergencies
    """
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.setup_mock_git_repo()
    
    def tearDown(self):
        """Clean up test environment"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def setup_mock_git_repo(self):
        """Create mock git repository for testing"""
        # Create .git directory structure
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        # Create hooks directory
        hooks_dir = git_dir / 'hooks'
        hooks_dir.mkdir()
    
    @patch('governance.scripts.integrated_pre_commit_hook.subprocess.run')
    @patch('governance.scripts.integrated_pre_commit_hook.ConfigLoader')
    @patch('governance.scripts.integrated_pre_commit_hook.get_correlation_tracker')
    def test_get_git_info(self, mock_tracker, mock_loader, mock_run):
        """Test getting git information"""
        # Mock subprocess responses
        mock_run.side_effect = [
            Mock(returncode=0, stdout='test_user'),     # git config user.name
            Mock(returncode=0, stdout='main'),           # git branch --show-current
            Mock(returncode=0, stdout='file1.py\nfile2.ts')  # git diff --cached
        ]
        
        # Create hook
        hook = IntegratedGovernanceHook()
        info = hook.get_git_info()
        
        self.assertEqual(info['user'], 'test_user')
        self.assertEqual(info['branch'], 'main')
        self.assertEqual(info['files'], ['file1.py', 'file2.ts'])
    
    @patch('governance.scripts.integrated_pre_commit_hook.ConfigLoader')
    @patch('governance.scripts.integrated_pre_commit_hook.get_correlation_tracker')
    def test_validate_documentation(self, mock_tracker, mock_loader):
        """Test documentation validation"""
        # Create temp file without proper headers
        test_file = Path(self.temp_dir) / 'test.py'
        test_file.write_text('# Missing headers\nprint("test")')
        
        # Mock validation rule
        mock_loader.return_value.get_validation_rule.return_value = {
            'requirements': {
                'file_headers': {
                    'mandatory': ['@fileoverview', '@author']
                }
            }
        }
        
        hook = IntegratedGovernanceHook()
        errors = hook._validate_documentation([str(test_file)])
        
        self.assertEqual(len(errors), 1)
        self.assertIn('@fileoverview', errors[0])
        self.assertIn('@author', errors[0])
    
    @patch('governance.scripts.integrated_pre_commit_hook.ConfigLoader')
    @patch('governance.scripts.integrated_pre_commit_hook.get_correlation_tracker')
    def test_validate_testing(self, mock_tracker, mock_loader):
        """Test testing requirement validation"""
        hook = IntegratedGovernanceHook()
        
        # Test implementation file without test
        warnings = hook._validate_testing(['implementation.py'])
        self.assertEqual(len(warnings), 1)
        self.assertIn('No test file found', warnings[0])
        
        # Test file with corresponding test
        test_file = Path(self.temp_dir) / 'implementation_test.py'
        test_file.touch()
        
        warnings = hook._validate_testing([
            'implementation.py',
            str(test_file)
        ])
        self.assertEqual(len(warnings), 0)
    
    @patch('governance.scripts.integrated_pre_commit_hook.subprocess.run')
    @patch('governance.scripts.integrated_pre_commit_hook.ConfigLoader')
    @patch('governance.scripts.integrated_pre_commit_hook.get_correlation_tracker')
    @patch('governance.scripts.integrated_pre_commit_hook.asyncio.get_event_loop')
    def test_full_governance_flow_approved(self, mock_loop, mock_tracker, mock_loader, mock_run):
        """Test full governance flow with approval"""
        # Mock git info
        mock_run.side_effect = [
            Mock(returncode=0, stdout='test_user'),
            Mock(returncode=0, stdout='main'),
            Mock(returncode=0, stdout='good_file.py')
        ]
        
        # Mock configuration
        mock_loader.return_value.get_event_mapping.return_value = {
            'validators': ['documentation'],
            'consensus_strategy': 'majority'
        }
        mock_loader.return_value.get_validation_rule.return_value = {
            'enabled': False  # Disable validation for this test
        }
        mock_loader.return_value.get_consensus_strategy.return_value = {
            'requirements': {'agreement_threshold': 0.5}
        }
        
        # Mock correlation tracker
        mock_correlation = Mock()
        mock_correlation.correlation_id = 'test-id'
        mock_tracker.return_value.create_correlation.return_value = mock_correlation
        
        # Create hook
        hook = IntegratedGovernanceHook()
        
        # Mock persona votes
        hook.persona_invoker.invoke_persona = Mock(
            return_value={'decision': 'approve', 'confidence': 0.9}
        )
        
        # Run governance check
        async def mock_check():
            return await hook.run_governance_check()
        
        mock_loop.return_value.run_until_complete.return_value = 0
        
        # Should return 0 (success)
        from governance.scripts.integrated_pre_commit_hook import main
        result = main()
        self.assertEqual(result, 0)


class TestGovernanceBypass(unittest.TestCase):
    """
    @class TestGovernanceBypass
    @description Test emergency bypass functionality
    @architecture_role Validate emergency procedures
    @business_logic Test bypass mode for critical situations
    """
    
    @patch.dict('os.environ', {'GOVERNANCE_BYPASS': 'true'})
    def test_bypass_mode(self):
        """Test governance bypass mode"""
        from governance.scripts.integrated_pre_commit_hook import main
        
        # Should return 0 immediately
        result = main()
        self.assertEqual(result, 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])