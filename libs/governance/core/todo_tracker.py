#!/usr/bin/env python3
"""
@fileoverview TODO/FIXME/HACK tracking and enforcement system
@author Sam Martinez v3.2.0 - 2025-01-28
@architecture Backend/Core - Code annotation tracking
@responsibility Track and enforce TODO/FIXME standards from CLAUDE.md
@dependencies re, datetime, pathlib, typing
@integration_points Git hooks, code scanners, issue trackers
@testing_strategy Unit tests for pattern detection, integration tests for enforcement
@governance Enforces TODO management standards

Business Logic Summary:
- Scan code for TODO/FIXME/HACK annotations
- Enforce format and age requirements
- Auto-escalate stale items
- Create issues for tracking

Architecture Integration:
- Integrates with git hooks
- Scans on commit
- Reports to governance
- Links to issue tracker
"""

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class TodoPriority(Enum):
    """TODO priority levels"""
    P0 = "P0"  # Critical - 1 day
    P1 = "P1"  # High - 7 days
    P2 = "P2"  # Medium - 30 days
    P3 = "P3"  # Low - 90 days


class TodoType(Enum):
    """Types of code annotations"""
    TODO = "TODO"
    FIXME = "FIXME"
    HACK = "HACK"
    NOTE = "NOTE"
    WARNING = "WARNING"


@dataclass
class TodoItem:
    """
    @class TodoItem
    @description Represents a TODO/FIXME annotation in code
    @architecture_role Data model for code annotations
    @business_logic Tracks annotation lifecycle and enforcement
    """
    type: TodoType
    file_path: str
    line_number: int
    content: str
    author: str = ""
    issue_number: str = ""
    priority: TodoPriority = TodoPriority.P2
    created_date: Optional[datetime] = None
    description: str = ""
    raw_text: str = ""
    
    def get_age_days(self) -> int:
        """Get age of TODO in days"""
        if not self.created_date:
            return 0
        return (datetime.now() - self.created_date).days
    
    def is_overdue(self, max_age_days: Dict[str, int]) -> bool:
        """Check if TODO exceeds age limit"""
        if self.priority.value not in max_age_days:
            return False
        
        age = self.get_age_days()
        max_age = max_age_days[self.priority.value]
        
        return age > max_age
    
    def format_for_issue(self) -> str:
        """Format TODO for issue creation"""
        return f"""
**Type**: {self.type.value}
**Priority**: {self.priority.value}
**File**: {self.file_path}:{self.line_number}
**Author**: {self.author}
**Created**: {self.created_date.isoformat() if self.created_date else 'Unknown'}

**Description**:
{self.description}

**Code Context**:
```
{self.raw_text}
```
"""


class TodoTracker:
    """
    @class TodoTracker
    @description Tracks and enforces TODO/FIXME standards
    @architecture_role Code annotation management
    @business_logic Enforces age limits and format requirements
    @failure_modes Pattern matching failures, false positives
    @debugging_info Complete TODO inventory with locations
    
    Defensive Programming Patterns:
    - Robust regex patterns
    - Error handling for file access
    - Validation of formats
    
    Sarah's Framework Check:
    - What breaks first: Stale TODOs accumulate
    - How we know: Age tracking and reporting
    - Plan B: Auto-escalation to issues
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize TODO tracker"""
        self.config = config or {}
        
        # Age limits by priority (in days)
        self.max_age_days = self.config.get('max_age_days', {
            'P0': 1,
            'P1': 7,
            'P2': 30,
            'P3': 90
        })
        
        # Regex patterns for different formats
        self.patterns = {
            'todo': re.compile(
                r'#\s*TODO\s*\(([^)]+)\):\s*(.+?)(?:\s*#(\d+))?$',
                re.MULTILINE | re.IGNORECASE
            ),
            'fixme': re.compile(
                r'#\s*FIXME\s*\(([^)]+)\):\s*(.+?)$',
                re.MULTILINE | re.IGNORECASE
            ),
            'hack': re.compile(
                r'#\s*HACK\s*\(([^)]+)\):\s*(.+?)$',
                re.MULTILINE | re.IGNORECASE
            ),
            # Also match simpler formats
            'simple_todo': re.compile(
                r'#\s*TODO:\s*(.+?)$',
                re.MULTILINE | re.IGNORECASE
            ),
            'simple_fixme': re.compile(
                r'#\s*FIXME:\s*(.+?)$',
                re.MULTILINE | re.IGNORECASE
            )
        }
        
        # Track found items
        self.todos: List[TodoItem] = []
        self.statistics = {
            'total': 0,
            'by_type': {},
            'by_priority': {},
            'overdue': 0
        }
    
    def scan_file(self, file_path: str) -> List[TodoItem]:
        """
        Scan a single file for TODOs
        
        @param file_path Path to file
        @returns List of found TODO items
        """
        items = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check each pattern type
            for line_num, line in enumerate(lines, 1):
                # TODO pattern with author
                match = self.patterns['todo'].search(line)
                if match:
                    author = match.group(1)
                    description = match.group(2)
                    issue = match.group(3) if match.group(3) else ""
                    
                    item = TodoItem(
                        type=TodoType.TODO,
                        file_path=file_path,
                        line_number=line_num,
                        content=line,
                        author=author,
                        description=description,
                        issue_number=issue,
                        raw_text=line
                    )
                    
                    # Try to extract priority
                    if 'P0' in description:
                        item.priority = TodoPriority.P0
                    elif 'P1' in description:
                        item.priority = TodoPriority.P1
                    elif 'P2' in description:
                        item.priority = TodoPriority.P2
                    elif 'P3' in description:
                        item.priority = TodoPriority.P3
                    
                    # Try to extract date
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                    if date_match:
                        try:
                            item.created_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                        except:
                            pass
                    
                    items.append(item)
                    continue
                
                # FIXME pattern
                match = self.patterns['fixme'].search(line)
                if match:
                    issue = match.group(1) if '(' in line else ""
                    description = match.group(2) if match.lastindex >= 2 else match.group(1)
                    
                    item = TodoItem(
                        type=TodoType.FIXME,
                        file_path=file_path,
                        line_number=line_num,
                        content=line,
                        issue_number=issue,
                        description=description,
                        priority=TodoPriority.P0,  # FIXMEs are high priority
                        raw_text=line
                    )
                    items.append(item)
                    continue
                
                # HACK pattern
                match = self.patterns['hack'].search(line)
                if match:
                    author = match.group(1)
                    justification = match.group(2)
                    
                    item = TodoItem(
                        type=TodoType.HACK,
                        file_path=file_path,
                        line_number=line_num,
                        content=line,
                        author=author,
                        description=justification,
                        priority=TodoPriority.P1,  # HACKs need removal
                        raw_text=line
                    )
                    items.append(item)
                    continue
                
                # Simple TODO without author
                match = self.patterns['simple_todo'].search(line)
                if match:
                    item = TodoItem(
                        type=TodoType.TODO,
                        file_path=file_path,
                        line_number=line_num,
                        content=line,
                        description=match.group(1),
                        priority=TodoPriority.P2,
                        raw_text=line
                    )
                    items.append(item)
                    continue
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return items
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> List[TodoItem]:
        """
        Scan directory for TODOs
        
        @param directory Directory to scan
        @param extensions File extensions to include
        @returns All found TODO items
        """
        if extensions is None:
            extensions = ['.py', '.ts', '.js', '.java', '.cpp', '.c', '.h']
        
        self.todos = []
        dir_path = Path(directory)
        
        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                # Skip test files and node_modules
                if 'node_modules' in str(file_path) or '__pycache__' in str(file_path):
                    continue
                
                items = self.scan_file(str(file_path))
                self.todos.extend(items)
        
        self._update_statistics()
        return self.todos
    
    def validate_format(self, todo_item: TodoItem) -> Tuple[bool, List[str]]:
        """
        Validate TODO format against standards
        
        @param todo_item Item to validate
        @returns (is_valid, list of issues)
        """
        issues = []
        
        # Check author
        if todo_item.type == TodoType.TODO and not todo_item.author:
            issues.append("TODO missing author")
        
        # Check issue reference for certain priorities
        if todo_item.priority in [TodoPriority.P0, TodoPriority.P1]:
            if not todo_item.issue_number:
                issues.append(f"{todo_item.priority.value} priority requires issue number")
        
        # Check FIXME has timeline
        if todo_item.type == TodoType.FIXME:
            if not todo_item.created_date:
                issues.append("FIXME requires timeline/date")
        
        # Check HACK has removal plan
        if todo_item.type == TodoType.HACK:
            if not todo_item.description or len(todo_item.description) < 10:
                issues.append("HACK requires removal plan")
        
        return len(issues) == 0, issues
    
    def get_overdue_todos(self) -> List[TodoItem]:
        """Get all overdue TODOs"""
        overdue = []
        
        for todo in self.todos:
            if todo.is_overdue(self.max_age_days):
                overdue.append(todo)
        
        return overdue
    
    def generate_report(self) -> str:
        """Generate TODO report"""
        report = ["TODO/FIXME Report", "=" * 50, ""]
        
        # Summary
        report.append(f"Total items: {self.statistics['total']}")
        report.append("")
        
        # By type
        report.append("By Type:")
        for todo_type, count in self.statistics['by_type'].items():
            report.append(f"  {todo_type}: {count}")
        report.append("")
        
        # By priority
        report.append("By Priority:")
        for priority, count in self.statistics['by_priority'].items():
            report.append(f"  {priority}: {count}")
        report.append("")
        
        # Overdue items
        overdue = self.get_overdue_todos()
        if overdue:
            report.append(f"OVERDUE ITEMS ({len(overdue)}):")
            for item in overdue:
                age = item.get_age_days()
                report.append(f"  - {item.file_path}:{item.line_number}")
                report.append(f"    {item.type.value} ({item.priority.value}): {item.description[:50]}")
                report.append(f"    Age: {age} days")
                report.append("")
        
        # Format violations
        report.append("Format Violations:")
        violations = 0
        for todo in self.todos:
            valid, issues = self.validate_format(todo)
            if not valid:
                violations += 1
                report.append(f"  - {todo.file_path}:{todo.line_number}")
                for issue in issues:
                    report.append(f"    {issue}")
        
        if violations == 0:
            report.append("  None")
        
        return "\n".join(report)
    
    def create_issues_for_overdue(self) -> List[Dict[str, Any]]:
        """Create issue data for overdue TODOs"""
        issues = []
        
        for todo in self.get_overdue_todos():
            issue_data = {
                'title': f"[{todo.type.value}] {todo.description[:50]}",
                'body': todo.format_for_issue(),
                'labels': [
                    todo.type.value.lower(),
                    todo.priority.value,
                    'auto-created',
                    'overdue'
                ],
                'assignee': todo.author if todo.author else None
            }
            issues.append(issue_data)
        
        return issues
    
    def _update_statistics(self):
        """Update internal statistics"""
        self.statistics = {
            'total': len(self.todos),
            'by_type': {},
            'by_priority': {},
            'overdue': 0
        }
        
        for todo in self.todos:
            # By type
            type_name = todo.type.value
            self.statistics['by_type'][type_name] = \
                self.statistics['by_type'].get(type_name, 0) + 1
            
            # By priority
            priority_name = todo.priority.value
            self.statistics['by_priority'][priority_name] = \
                self.statistics['by_priority'].get(priority_name, 0) + 1
            
            # Overdue
            if todo.is_overdue(self.max_age_days):
                self.statistics['overdue'] += 1
    
    def save_report(self, file_path: str):
        """Save report to file"""
        report = self.generate_report()
        
        with open(file_path, 'w') as f:
            f.write(report)
        
        # Also save JSON data
        json_path = file_path.replace('.txt', '.json')
        data = {
            'scan_date': datetime.now().isoformat(),
            'statistics': self.statistics,
            'todos': [
                {
                    'type': todo.type.value,
                    'file': todo.file_path,
                    'line': todo.line_number,
                    'author': todo.author,
                    'priority': todo.priority.value,
                    'description': todo.description,
                    'age_days': todo.get_age_days(),
                    'overdue': todo.is_overdue(self.max_age_days)
                }
                for todo in self.todos
            ]
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)