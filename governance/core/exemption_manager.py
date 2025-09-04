#!/usr/bin/env python3
"""
Exemption Manager for Governance System

Manages validation exemptions from configuration, allowing specific files
or patterns to be exempt from certain checks with proper documentation
and audit trail.

Author: Alex Novak & Dr. Sarah Chen
Created: 2025-09-03
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import yaml
import fnmatch
import json
from dataclasses import dataclass, asdict


@dataclass
class ExemptionUsage:
    """Record of exemption usage for audit trail"""
    timestamp: str
    file_path: str
    rule: str
    exemption_type: str
    reason: str
    approved_by: str
    expires: str


class ExemptionManager:
    """
    Manages validation exemptions from configuration.
    
    Provides a centralized way to check if files or patterns are exempt
    from specific validation rules, with full audit trail and governance.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize exemption manager with configuration.
        
        Args:
            config_path: Path to governance config.yaml
        """
        self.config_path = config_path
        self.exemptions = self._load_exemptions()
        self.usage_log: List[ExemptionUsage] = []
        self.audit_file = Path(".governance/audit/exemption_usage.jsonl")
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_exemptions(self) -> Dict[str, Any]:
        """Load exemptions from configuration file"""
        if not self.config_path.exists():
            return {}
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        return config.get('validation_exemptions', {})
        
    def is_exempt(self, file_path: str, rule: str, context: Dict = None) -> bool:
        """
        Check if a file is exempt from a specific rule.
        
        Args:
            file_path: Path to file being validated
            rule: Validation rule ID
            context: Additional context about the validation
            
        Returns:
            True if file is exempt, False otherwise
        """
        # Normalize the file path for comparison
        file_path = Path(file_path).as_posix()
        
        # Check file-level exemptions
        if self._check_file_exemption(file_path, rule):
            return True
            
        # Check pattern exemptions
        if self._check_pattern_exemption(file_path, rule):
            return True
            
        # Check context-based exemptions
        if context and self._check_context_exemption(rule, context):
            return True
            
        return False
        
    def _check_file_exemption(self, file_path: str, rule: str) -> bool:
        """Check if specific file is exempt from rule"""
        file_exemptions = self.exemptions.get('file_exemptions', [])
        
        for exemption in file_exemptions:
            # Check if this is the right file
            if Path(exemption['path']).as_posix() == file_path:
                # Check if rule is exempt
                for rule_config in exemption.get('rules', []):
                    if rule_config['id'] == rule:
                        # Check if exemption is still valid
                        if self._is_exemption_valid(rule_config):
                            self._log_usage(
                                file_path, 
                                rule, 
                                "file_exemption",
                                rule_config.get('reason', 'No reason provided'),
                                rule_config.get('approved_by', 'Unknown'),
                                rule_config.get('expires', 'Never')
                            )
                            return True
        return False
        
    def _check_pattern_exemption(self, file_path: str, rule: str) -> bool:
        """Check if file matches pattern exemption"""
        pattern_exemptions = self.exemptions.get('pattern_exemptions', [])
        
        for exemption in pattern_exemptions:
            pattern = exemption['pattern']
            
            # Check if file matches pattern
            if fnmatch.fnmatch(file_path, pattern):
                # Check if rule is exempt
                for rule_config in exemption.get('rules', []):
                    if rule_config['id'] == rule or rule_config['id'] == 'all_documentation_checks':
                        self._log_usage(
                            file_path,
                            rule,
                            "pattern_exemption",
                            rule_config.get('reason', 'No reason provided'),
                            rule_config.get('approved_by', 'Unknown'),
                            rule_config.get('expires', 'Never')
                        )
                        return True
        return False
        
    def _check_context_exemption(self, rule: str, context: Dict) -> bool:
        """Check if context allows exemption"""
        context_exemptions = self.exemptions.get('context_exemptions', [])
        
        for exemption in context_exemptions:
            if exemption['rule'] == rule:
                allowed_contexts = exemption.get('allowed_when', [])
                
                # Check if any allowed context matches
                for allowed in allowed_contexts:
                    if context.get(allowed):
                        self._log_usage(
                            context.get('file_path', 'Unknown'),
                            rule,
                            "context_exemption",
                            f"Context: {allowed}",
                            "System",
                            "Context-based"
                        )
                        return True
        return False
        
    def _is_exemption_valid(self, rule_config: Dict) -> bool:
        """Check if exemption is still valid (not expired)"""
        expires = rule_config.get('expires')
        if not expires or expires == 'Never':
            return True
            
        try:
            expiry_date = datetime.strptime(expires, '%Y-%m-%d')
            return datetime.now() < expiry_date
        except ValueError:
            return True  # If can't parse, assume valid
            
    def _log_usage(self, file_path: str, rule: str, exemption_type: str, 
                   reason: str, approved_by: str, expires: str):
        """Log exemption usage for audit trail"""
        usage = ExemptionUsage(
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            rule=rule,
            exemption_type=exemption_type,
            reason=reason,
            approved_by=approved_by,
            expires=expires
        )
        
        self.usage_log.append(usage)
        
        # Write to audit file
        try:
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(usage)) + '\n')
        except Exception:
            pass  # Don't fail validation if audit logging fails
            
    def get_expired_exemptions(self) -> List[Dict]:
        """Get list of expired exemptions that need review"""
        expired = []
        
        # Check file exemptions
        for exemption in self.exemptions.get('file_exemptions', []):
            for rule in exemption.get('rules', []):
                if not self._is_exemption_valid(rule):
                    expired.append({
                        'type': 'file',
                        'path': exemption['path'],
                        'rule': rule['id'],
                        'expired': rule.get('expires'),
                        'approved_by': rule.get('approved_by')
                    })
                    
        return expired
        
    def get_usage_report(self) -> Dict:
        """Get summary of exemption usage"""
        return {
            'total_exemptions_used': len(self.usage_log),
            'by_type': self._count_by_type(),
            'by_rule': self._count_by_rule(),
            'expired_exemptions': self.get_expired_exemptions()
        }
        
    def _count_by_type(self) -> Dict[str, int]:
        """Count exemptions by type"""
        counts = {}
        for usage in self.usage_log:
            counts[usage.exemption_type] = counts.get(usage.exemption_type, 0) + 1
        return counts
        
    def _count_by_rule(self) -> Dict[str, int]:
        """Count exemptions by rule"""
        counts = {}
        for usage in self.usage_log:
            counts[usage.rule] = counts.get(usage.rule, 0) + 1
        return counts