#!/usr/bin/env python3
"""
@fileoverview Basic hallucination detection for AI-generated content
@author Dr. Elena Vasquez v1.0 - 2025-01-28
@architecture Backend - Content validation
@responsibility Detect potential hallucinations using pattern matching
@dependencies re, typing, pathlib, yaml
@integration_points SmartRules, pre-commit hooks, fact-checking persona
@testing_strategy Pattern detection tests, false positive rate measurement
@governance Phase 1.5b implementation - basic pattern detection

Business Logic Summary:
- Pattern-based detection of suspicious content
- Configuration-driven for easy updates
- Performance-optimized for git hooks
- Pluggable architecture for future enhancement

Architecture Integration:
- Plugin for SmartRules engine
- Used by Dr. Elena Vasquez persona
- Minimal performance impact (<500ms)
- YAML-based configuration

Sarah's Framework Check:
- What breaks first: Regex performance on large files
- How we know: Performance monitoring in place
- Plan B: File size limits and pattern count limits
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HallucinationSeverity(Enum):
    """Severity levels for detected hallucinations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HallucinationFinding:
    """
    @class HallucinationFinding
    @description Represents a detected potential hallucination
    @architecture_role Data model for findings
    @business_logic Encapsulates detection result with context
    """
    pattern_name: str
    matched_text: str
    line_number: int
    severity: HallucinationSeverity
    suggestion: str
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'pattern': self.pattern_name,
            'text': self.matched_text[:100],  # Limit text length
            'line': self.line_number,
            'severity': self.severity.value,
            'suggestion': self.suggestion,
            'confidence': self.confidence
        }


class BasicHallucinationDetector:
    """
    @class BasicHallucinationDetector
    @description Phase 1.5b basic pattern-based hallucination detection
    @architecture_role Core detection engine
    @business_logic Simple pattern matching with performance limits
    @failure_modes Pattern miss, false positive, performance degradation
    @debugging_info Logs all detections with pattern names
    
    Alex's 3AM Test: Simple regex patterns, clear configuration, easy to debug
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize detector with configuration
        
        @param config_file Optional YAML configuration file path
        """
        self.patterns = self._load_patterns(config_file)
        self.max_file_size = 500000  # 500KB limit for performance
        self.max_lines = 1000  # Process first 1000 lines only
        
    def _load_patterns(self, config_file: Optional[str]) -> Dict[str, List[Dict]]:
        """Load detection patterns from configuration"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('patterns', self._get_default_patterns())
        
        return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, List[Dict]]:
        """Get default detection patterns"""
        return {
            'critical': [
                {
                    'name': 'fake_percentage',
                    'pattern': r'\b(?:exactly\s+)?(\d{2}\.\d+)%\s+of\s+(?:all\s+)?(?:users|developers|companies)',
                    'severity': HallucinationSeverity.ERROR,
                    'confidence': 0.7,
                    'suggestion': 'Verify statistic and add source citation'
                },
                {
                    'name': 'future_date',
                    'pattern': r'\b20[3-9]\d\s+(?:study|research|survey)',
                    'severity': HallucinationSeverity.CRITICAL,
                    'confidence': 0.9,
                    'suggestion': 'Remove future date reference'
                },
                {
                    'name': 'fake_version',
                    'pattern': r'(?:Python\s+[4-9]\.|Node\.js\s+v?2[5-9]|React\s+2[0-9])',
                    'severity': HallucinationSeverity.ERROR,
                    'confidence': 0.95,
                    'suggestion': 'Correct version number to existing version'
                }
            ],
            'warning': [
                {
                    'name': 'vague_attribution',
                    'pattern': r'(?:studies\s+show|research\s+indicates|experts\s+say|it\s+is\s+known)\s+that',
                    'severity': HallucinationSeverity.WARNING,
                    'confidence': 0.4,
                    'suggestion': 'Add specific source or use qualified language'
                },
                {
                    'name': 'suspicious_claim',
                    'pattern': r'(?:always|never|guaranteed|definitely|certainly)\s+(?:will|works|fails)',
                    'severity': HallucinationSeverity.WARNING,
                    'confidence': 0.3,
                    'suggestion': 'Use qualified language instead of absolutes'
                }
            ],
            'info': [
                {
                    'name': 'unverified_stat',
                    'pattern': r'\b\d+x\s+(?:faster|slower|better|worse)',
                    'severity': HallucinationSeverity.INFO,
                    'confidence': 0.3,
                    'suggestion': 'Consider adding benchmark data'
                }
            ]
        }
    
    def detect(self, content: str, file_path: Optional[str] = None) -> List[HallucinationFinding]:
        """
        Detect potential hallucinations in content
        
        @param content Text content to check
        @param file_path Optional file path for context
        @returns List of findings
        
        BUSINESS RULE: Performance must stay under 500ms
        """
        findings = []
        
        # Performance check
        if len(content) > self.max_file_size:
            return []  # Skip large files
        
        # Skip non-content files
        if file_path:
            skip_extensions = ['.json', '.yml', '.yaml', '.lock', '.svg', '.png']
            if any(file_path.endswith(ext) for ext in skip_extensions):
                return []
        
        lines = content.split('\n')[:self.max_lines]
        
        # Check each pattern category
        for severity_level, patterns in self.patterns.items():
            for pattern_config in patterns:
                pattern = re.compile(pattern_config['pattern'], re.IGNORECASE)
                
                for line_num, line in enumerate(lines, 1):
                    matches = pattern.finditer(line)
                    for match in matches:
                        finding = HallucinationFinding(
                            pattern_name=pattern_config['name'],
                            matched_text=match.group(0),
                            line_number=line_num,
                            severity=pattern_config['severity'],
                            suggestion=pattern_config['suggestion'],
                            confidence=pattern_config.get('confidence', 0.5)
                        )
                        findings.append(finding)
        
        return findings
    
    def check_file(self, file_path: str) -> Dict[str, Any]:
        """
        Check a file for hallucinations
        
        @param file_path Path to file
        @returns Detection results
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            findings = self.detect(content, file_path)
            
            return {
                'file': file_path,
                'has_hallucinations': len(findings) > 0,
                'critical_count': sum(1 for f in findings if f.severity == HallucinationSeverity.CRITICAL),
                'error_count': sum(1 for f in findings if f.severity == HallucinationSeverity.ERROR),
                'warning_count': sum(1 for f in findings if f.severity == HallucinationSeverity.WARNING),
                'findings': [f.to_dict() for f in findings]
            }
            
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'has_hallucinations': False
            }
    
    def get_severity_score(self, findings: List[HallucinationFinding]) -> float:
        """
        Calculate overall severity score
        
        @param findings List of findings
        @returns Score from 0.0 (no issues) to 1.0 (critical issues)
        """
        if not findings:
            return 0.0
        
        severity_weights = {
            HallucinationSeverity.CRITICAL: 1.0,
            HallucinationSeverity.ERROR: 0.7,
            HallucinationSeverity.WARNING: 0.3,
            HallucinationSeverity.INFO: 0.1
        }
        
        total_score = sum(
            severity_weights[f.severity] * f.confidence 
            for f in findings
        )
        
        # Normalize to 0-1 range
        return min(total_score / len(findings), 1.0)


# Integration helper for SmartRules
def create_detector_for_smart_rules() -> BasicHallucinationDetector:
    """
    Factory function to create detector for SmartRules integration
    
    @returns Configured detector instance
    """
    config_paths = [
        Path('governance-config/hallucination-patterns.yml'),
        Path('.governance/hallucination-patterns.yml')
    ]
    
    config_file = None
    for path in config_paths:
        if path.exists():
            config_file = str(path)
            break
    
    return BasicHallucinationDetector(config_file)


# Standalone CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python basic_hallucination_detector.py <file>")
        sys.exit(1)
    
    detector = BasicHallucinationDetector()
    results = detector.check_file(sys.argv[1])
    
    if results.get('error'):
        print(f"Error: {results['error']}")
        sys.exit(1)
    
    if results['has_hallucinations']:
        print(f"Found {len(results['findings'])} potential hallucinations:")
        for finding in results['findings']:
            print(f"  Line {finding['line']}: {finding['pattern']} - {finding['suggestion']}")
        sys.exit(1)
    else:
        print("No hallucinations detected")
        sys.exit(0)