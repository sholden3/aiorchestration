#!/usr/bin/env python
"""
Documentation Validation Utilities
@description: Helper functions and utilities for documentation validation
@author: Governance System v2.0
@version: 2.0.0
@dependencies: re, pathlib, subprocess, fnmatch, typing
@exports: Utility functions for doc validation
@testing: 0% (needs implementation)
@last_review: 2025-09-03
"""

import re
import fnmatch
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import json
from datetime import datetime


def get_staged_markdown_files(repo_root: Path = None) -> List[str]:
    """
    Get list of staged markdown files from git
    
    Args:
        repo_root: Repository root path
        
    Returns:
        List of relative paths to staged .md files
    """
    if repo_root is None:
        repo_root = Path.cwd()
    
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, cwd=repo_root
        )
        
        if result.returncode != 0:
            return []
        
        files = result.stdout.strip().split('\\n')
        markdown_files = [f for f in files if f and f.endswith('.md')]
        
        return markdown_files
        
    except Exception:
        return []


def match_file_pattern(file_path: str, patterns: List[str]) -> bool:
    """
    Check if file path matches any of the given patterns
    
    Args:
        file_path: Path to check
        patterns: List of patterns (supports wildcards)
        
    Returns:
        True if file matches any pattern
    """
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
        
        # Also check just the filename
        filename = Path(file_path).name
        if fnmatch.fnmatch(filename, pattern):
            return True
    
    return False


def extract_markdown_sections(content: str) -> Dict[str, Tuple[int, str]]:
    """
    Extract markdown sections and their levels
    
    Args:
        content: Markdown content
        
    Returns:
        Dict mapping section names to (level, content) tuples
    """
    sections = {}
    lines = content.split('\\n')
    
    current_section = None
    current_level = 0
    current_content = []
    
    for line in lines:
        header_match = re.match(r'^(#+)\\s+(.+)$', line.strip())
        
        if header_match:
            # Save previous section if exists
            if current_section:
                sections[current_section] = (current_level, '\\n'.join(current_content))
            
            # Start new section
            level = len(header_match.group(1))
            section_name = header_match.group(2).strip()
            current_section = section_name
            current_level = level
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # Don't forget the last section
    if current_section:
        sections[current_section] = (current_level, '\\n'.join(current_content))
    
    return sections


def find_placeholder_matches(content: str, placeholder_pattern: str = r'\\[([A-Z_][A-Z0-9_]*)\\]') -> List[str]:
    """
    Find all placeholder matches in content
    
    Args:
        content: Text content to search
        placeholder_pattern: Regex pattern for placeholders
        
    Returns:
        List of placeholder names found
    """
    matches = re.findall(placeholder_pattern, content)
    return list(set(matches))  # Remove duplicates


def validate_section_hierarchy(sections: Dict[str, Tuple[int, str]]) -> List[str]:
    """
    Validate section hierarchy (no skipped levels)
    
    Args:
        sections: Dict from extract_markdown_sections
        
    Returns:
        List of hierarchy issues found
    """
    issues = []
    
    if not sections:
        return issues
    
    section_items = list(sections.items())
    prev_level = 0
    
    for section_name, (level, content) in section_items:
        if level > prev_level + 1:
            issues.append(f"Section '{section_name}' skips header levels (from h{prev_level} to h{level})")
        prev_level = level
    
    return issues


def count_words_in_sections(sections: Dict[str, Tuple[int, str]]) -> Dict[str, int]:
    """
    Count words in each section
    
    Args:
        sections: Dict from extract_markdown_sections
        
    Returns:
        Dict mapping section names to word counts
    """
    word_counts = {}
    
    for section_name, (level, content) in sections.items():
        # Simple word count (split on whitespace)
        words = content.split()
        word_counts[section_name] = len(words)
    
    return word_counts


def find_broken_links(content: str, base_path: Path = None) -> List[str]:
    """
    Find potentially broken internal links
    
    Args:
        content: Markdown content
        base_path: Base path for resolving relative links
        
    Returns:
        List of potentially broken link descriptions
    """
    broken_links = []
    
    if base_path is None:
        base_path = Path.cwd()
    
    # Find markdown links [text](url)
    link_pattern = r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)'
    links = re.findall(link_pattern, content)
    
    for link_text, url in links:
        # Skip external links
        if url.startswith(('http://', 'https://', 'mailto:', 'ftp://')):
            continue
        
        # Skip anchors
        if url.startswith('#'):
            continue
        
        # Check if file exists for relative links
        if not url.startswith('/'):
            link_path = base_path / url
            if not link_path.exists():
                broken_links.append(f"Link '{link_text}' points to non-existent file: {url}")
    
    return broken_links


def check_markdown_formatting(content: str) -> List[str]:
    """
    Check for common markdown formatting issues
    
    Args:
        content: Markdown content to check
        
    Returns:
        List of formatting issue descriptions
    """
    issues = []
    lines = content.split('\\n')
    
    for i, line in enumerate(lines, 1):
        # Check header formatting
        if line.strip().startswith('#'):
            # Headers without space after #
            if re.match(r'^#+[^\\s#]', line.strip()):
                issues.append(f"Line {i}: Header missing space after #")
        
        # Check list formatting
        if re.match(r'^\\s*[-\\*\\+][^\\s]', line):
            issues.append(f"Line {i}: List item missing space after marker")
        
        # Check for tabs (should use spaces)
        if '\\t' in line:
            issues.append(f"Line {i}: Contains tab characters (use spaces)")
        
        # Check for trailing whitespace
        if line.endswith(' ') or line.endswith('\\t'):
            issues.append(f"Line {i}: Contains trailing whitespace")
    
    return issues


def generate_section_toc(content: str, max_level: int = 3) -> str:
    """
    Generate table of contents from markdown headers
    
    Args:
        content: Markdown content
        max_level: Maximum header level to include
        
    Returns:
        Generated TOC as markdown
    """
    toc_lines = []
    lines = content.split('\\n')
    
    for line in lines:
        header_match = re.match(r'^(#+)\\s+(.+)$', line.strip())
        
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            
            if level <= max_level:
                # Create anchor link
                anchor = title.lower().replace(' ', '-').replace('[^a-z0-9-]', '')
                indent = '  ' * (level - 1)
                toc_lines.append(f"{indent}- [{title}](#{anchor})")
    
    if toc_lines:
        return '\\n'.join(['## Table of Contents', ''] + toc_lines + [''])
    else:
        return ''


def calculate_readability_score(content: str) -> Dict[str, Any]:
    """
    Calculate basic readability metrics
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dict with readability metrics
    """
    # Remove markdown formatting for analysis
    text = re.sub(r'[#\\*\\[\\]\\(\\)_`]', '', content)
    text = re.sub(r'\\n+', ' ', text)
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not words or not sentences:
        return {
            'word_count': 0,
            'sentence_count': 0,
            'avg_words_per_sentence': 0,
            'readability_grade': 'N/A'
        }
    
    word_count = len(words)
    sentence_count = len(sentences)
    avg_words_per_sentence = word_count / sentence_count
    
    # Simple readability grade estimation
    if avg_words_per_sentence < 10:
        grade = 'Easy'
    elif avg_words_per_sentence < 15:
        grade = 'Moderate'
    elif avg_words_per_sentence < 20:
        grade = 'Difficult'
    else:
        grade = 'Very Difficult'
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_words_per_sentence': round(avg_words_per_sentence, 1),
        'readability_grade': grade
    }


def should_skip_validation(content: str, file_path: str) -> Tuple[bool, str]:
    """
    Check if validation should be skipped for this file
    
    Args:
        content: File content
        file_path: Path to the file
        
    Returns:
        (should_skip, reason)
    """
    # Check for skip marker
    if '<!-- SKIP_DOC_VALIDATION -->' in content:
        return True, "Skip marker found in content"
    
    # Check for generated file markers
    generated_markers = [
        'AUTO-GENERATED',
        'DO NOT EDIT',
        'GENERATED FILE',
        'This file was automatically generated'
    ]
    
    for marker in generated_markers:
        if marker in content:
            return True, f"Generated file marker found: {marker}"
    
    # Check file size (skip very large files)
    if len(content) > 1024 * 1024:  # 1MB
        return True, "File too large for validation"
    
    # Skip certain paths
    skip_patterns = [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**',
        '**/build/**'
    ]
    
    for pattern in skip_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True, f"File path matches skip pattern: {pattern}"
    
    return False, ""


def format_validation_summary(total_files: int, valid_files: int, violations: Dict[str, int]) -> str:
    """
    Format a validation summary for display
    
    Args:
        total_files: Total number of files checked
        valid_files: Number of files that passed validation
        violations: Dict mapping severity to count
        
    Returns:
        Formatted summary string
    """
    invalid_files = total_files - valid_files
    compliance_rate = (valid_files / total_files * 100) if total_files > 0 else 100
    
    summary_lines = [
        f"📊 Validation Summary",
        f"  Total Files: {total_files}",
        f"  Valid: {valid_files} ({compliance_rate:.1f}%)",
        f"  Invalid: {invalid_files}"
    ]
    
    if violations:
        summary_lines.append("  Violations:")
        for severity, count in violations.items():
            if count > 0:
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(severity, "⚪")
                summary_lines.append(f"    {icon} {severity.title()}: {count}")
    
    return '\\n'.join(summary_lines)


def create_validation_report_json(results: List[Dict[str, Any]], output_path: Path) -> bool:
    """
    Create a JSON validation report
    
    Args:
        results: List of validation results
        output_path: Where to save the report
        
    Returns:
        True if report was created successfully
    """
    try:
        report_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_files": len(results),
            "valid_files": sum(1 for r in results if r.get('is_valid', False)),
            "results": results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return True
        
    except Exception as e:
        print(f"Failed to create JSON report: {e}")
        return False