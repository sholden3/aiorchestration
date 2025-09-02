#!/usr/bin/env python3
"""
Governance Automated Reporting System
Generates and distributes governance reports on schedule

@author Dr. Sarah Chen v1.2 - Backend Systems & Governance Architecture
@architecture Automated reporting system with scheduled generation and distribution
@business_logic Provides compliance tracking, metrics aggregation, and trend analysis
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GovernanceReporter:
    """Automated governance reporting system"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize reporter"""
        self.repo_root = repo_root or Path.cwd()
        self.db_path = self.repo_root / ".governance" / "metrics.db"
        self.reports_dir = self.repo_root / ".governance" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load reporting configuration"""
        config_file = self.repo_root / "governance-config" / "enforcement-policies.yml"
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_daily_report(self) -> Dict:
        """Generate daily governance report"""
        report = {
            'type': 'daily',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'details': {},
            'recommendations': []
        }
        
        # Get 24-hour metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=24)
        
        # Violation summary
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM governance_events
            WHERE timestamp >= ? AND event_type LIKE '%violation%'
            GROUP BY severity
            ORDER BY count DESC
        """, (since,))
        
        violations = {}
        total_violations = 0
        for row in cursor.fetchall():
            violations[row[0]] = row[1]
            total_violations += row[1]
        
        report['summary']['violations'] = violations
        report['summary']['total_violations'] = total_violations
        
        # Files with most issues
        cursor.execute("""
            SELECT file_path, COUNT(*) as count
            FROM governance_events
            WHERE timestamp >= ? AND file_path != ''
            GROUP BY file_path
            ORDER BY count DESC
            LIMIT 10
        """, (since,))
        
        problem_files = []
        for row in cursor.fetchall():
            problem_files.append({'file': row[0], 'issues': row[1]})
        
        report['details']['problem_files'] = problem_files
        
        # Commit blocks
        cursor.execute("""
            SELECT COUNT(*) FROM commit_blocks WHERE timestamp >= ?
        """, (since,))
        
        blocks = cursor.fetchone()[0]
        report['summary']['commits_blocked'] = blocks
        
        # Developer impact
        cursor.execute("""
            SELECT user, COUNT(*) as blocks
            FROM commit_blocks
            WHERE timestamp >= ?
            GROUP BY user
            ORDER BY blocks DESC
        """, (since,))
        
        developer_impact = []
        for row in cursor.fetchall():
            developer_impact.append({'developer': row[0], 'blocks': row[1]})
        
        report['details']['developer_impact'] = developer_impact
        
        # Test execution status
        cursor.execute("""
            SELECT MAX(timestamp) as last_run,
                   AVG(passed * 100.0 / (passed + failed)) as pass_rate
            FROM test_executions
            WHERE timestamp >= ?
        """, (since,))
        
        row = cursor.fetchone()
        if row[0]:
            report['summary']['tests'] = {
                'last_run': row[0],
                'pass_rate': f"{row[1]:.1f}%" if row[1] else "N/A"
            }
        
        # Exemptions used
        cursor.execute("""
            SELECT exemption_type, COUNT(*) as count
            FROM exemption_usage
            WHERE timestamp >= ?
            GROUP BY exemption_type
            ORDER BY count DESC
        """, (since,))
        
        exemptions = []
        for row in cursor.fetchall():
            exemptions.append({'type': row[0], 'count': row[1]})
        
        report['details']['exemptions_used'] = exemptions
        
        conn.close()
        
        # Generate recommendations
        if total_violations > 50:
            report['recommendations'].append(
                "High violation count - consider reviewing rules or providing training"
            )
        
        if blocks > 5:
            report['recommendations'].append(
                "Multiple commits blocked - review blocking criteria"
            )
        
        if violations.get('CRITICAL', 0) > 0:
            report['recommendations'].append(
                "Critical violations detected - immediate attention required"
            )
        
        # Save report
        report_file = self.reports_dir / f"daily_{report['date']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_weekly_report(self) -> Dict:
        """Generate weekly governance report"""
        report = {
            'type': 'weekly',
            'week_ending': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'trends': {},
            'compliance': {},
            'recommendations': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(days=7)
        
        # Weekly violation trend
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM governance_events
            WHERE timestamp >= ? AND event_type LIKE '%violation%'
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (since,))
        
        daily_violations = []
        for row in cursor.fetchall():
            daily_violations.append({'date': row[0], 'count': row[1]})
        
        report['trends']['daily_violations'] = daily_violations
        
        # Compliance score calculation
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN event_type = 'commit_allowed' THEN 1 END) as allowed,
                COUNT(CASE WHEN event_type = 'commit_blocked' THEN 1 END) as blocked
            FROM governance_events
            WHERE timestamp >= ?
        """, (since,))
        
        row = cursor.fetchone()
        if row[0] + row[1] > 0:
            compliance_rate = row[0] * 100.0 / (row[0] + row[1])
            report['compliance']['rate'] = f"{compliance_rate:.1f}%"
            report['compliance']['commits_allowed'] = row[0]
            report['compliance']['commits_blocked'] = row[1]
        
        # Most common violations
        cursor.execute("""
            SELECT message, COUNT(*) as count
            FROM governance_events
            WHERE timestamp >= ? AND event_type LIKE '%violation%'
            GROUP BY message
            ORDER BY count DESC
            LIMIT 10
        """, (since,))
        
        common_violations = []
        for row in cursor.fetchall():
            common_violations.append({'violation': row[0][:100], 'count': row[1]})
        
        report['summary']['common_violations'] = common_violations
        
        # Test coverage trend
        cursor.execute("""
            SELECT DATE(timestamp) as date, AVG(coverage) as avg_coverage
            FROM test_executions
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (since,))
        
        coverage_trend = []
        for row in cursor.fetchall():
            if row[1]:
                coverage_trend.append({'date': row[0], 'coverage': f"{row[1]:.1f}%"})
        
        report['trends']['test_coverage'] = coverage_trend
        
        conn.close()
        
        # Calculate improvement areas
        if common_violations:
            report['recommendations'].append(
                f"Focus on addressing: {common_violations[0]['violation']}"
            )
        
        if compliance_rate < 80:
            report['recommendations'].append(
                "Compliance rate below target - review enforcement policies"
            )
        
        # Save report
        report_file = self.reports_dir / f"weekly_{report['week_ending']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_monthly_report(self) -> Dict:
        """Generate monthly governance report"""
        report = {
            'type': 'monthly',
            'month': datetime.now().strftime('%Y-%m'),
            'generated_at': datetime.now().isoformat(),
            'executive_summary': {},
            'detailed_metrics': {},
            'phase_progression': {},
            'recommendations': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(days=30)
        
        # Executive summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT file_path) as files_checked,
                COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high
            FROM governance_events
            WHERE timestamp >= ?
        """, (since,))
        
        row = cursor.fetchone()
        report['executive_summary'] = {
            'total_events': row[0],
            'files_analyzed': row[1],
            'critical_issues': row[2],
            'high_issues': row[3]
        }
        
        # Calculate governance health score
        health_score = 100
        if row[2] > 0:  # Critical issues
            health_score -= 30
        if row[3] > 10:  # Many high issues
            health_score -= 20
        
        # Check false positive rate (from exemptions)
        cursor.execute("""
            SELECT COUNT(*) FROM exemption_usage WHERE timestamp >= ?
        """, (since,))
        
        exemptions = cursor.fetchone()[0]
        if row[0] > 0:
            false_positive_rate = exemptions * 100.0 / row[0]
            if false_positive_rate > 20:
                health_score -= 10
            
            report['detailed_metrics']['false_positive_rate'] = f"{false_positive_rate:.1f}%"
        
        report['executive_summary']['governance_health_score'] = health_score
        
        # Phase progression readiness
        phase_ready = {
            'current_phase': 2,
            'ready_for_next': False,
            'criteria_met': [],
            'criteria_not_met': []
        }
        
        # Check criteria
        if false_positive_rate < 10:
            phase_ready['criteria_met'].append('False positive rate < 10%')
        else:
            phase_ready['criteria_not_met'].append(f'False positive rate: {false_positive_rate:.1f}%')
        
        if health_score > 70:
            phase_ready['criteria_met'].append('Health score > 70')
        else:
            phase_ready['criteria_not_met'].append(f'Health score: {health_score}')
        
        if row[2] == 0:  # No critical in last 30 days
            phase_ready['criteria_met'].append('No critical violations')
        else:
            phase_ready['criteria_not_met'].append(f'Critical violations: {row[2]}')
        
        phase_ready['ready_for_next'] = len(phase_ready['criteria_not_met']) == 0
        report['phase_progression'] = phase_ready
        
        conn.close()
        
        # Generate strategic recommendations
        if phase_ready['ready_for_next']:
            report['recommendations'].append(
                "Ready to progress to Phase 3 (Enforcement)"
            )
        else:
            report['recommendations'].append(
                f"Address these before Phase 3: {', '.join(phase_ready['criteria_not_met'])}"
            )
        
        if health_score < 70:
            report['recommendations'].append(
                "Governance health needs improvement - consider training or rule refinement"
            )
        
        # Save report
        report_file = self.reports_dir / f"monthly_{report['month']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def format_report_text(self, report: Dict) -> str:
        """Format report as readable text"""
        lines = []
        
        report_type = report.get('type', 'unknown').upper()
        lines.append("="*70)
        lines.append(f"GOVERNANCE {report_type} REPORT")
        lines.append("="*70)
        lines.append(f"Generated: {report.get('generated_at', 'Unknown')}")
        
        # Summary section
        if 'summary' in report:
            lines.append("\n📊 SUMMARY")
            lines.append("-"*40)
            
            summary = report['summary']
            if 'violations' in summary:
                lines.append("Violations by Severity:")
                for severity, count in summary['violations'].items():
                    emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}.get(severity, '⚪')
                    lines.append(f"  {emoji} {severity}: {count}")
            
            if 'total_violations' in summary:
                lines.append(f"\nTotal Violations: {summary['total_violations']}")
            
            if 'commits_blocked' in summary:
                lines.append(f"Commits Blocked: {summary['commits_blocked']}")
            
            if 'tests' in summary:
                lines.append(f"\nTest Status:")
                lines.append(f"  Last Run: {summary['tests'].get('last_run', 'Unknown')}")
                lines.append(f"  Pass Rate: {summary['tests'].get('pass_rate', 'N/A')}")
        
        # Executive summary for monthly
        if 'executive_summary' in report:
            lines.append("\n📈 EXECUTIVE SUMMARY")
            lines.append("-"*40)
            exec_summary = report['executive_summary']
            lines.append(f"Governance Health Score: {exec_summary.get('governance_health_score', 0)}/100")
            lines.append(f"Total Events: {exec_summary.get('total_events', 0)}")
            lines.append(f"Files Analyzed: {exec_summary.get('files_analyzed', 0)}")
            lines.append(f"Critical Issues: {exec_summary.get('critical_issues', 0)}")
            lines.append(f"High Issues: {exec_summary.get('high_issues', 0)}")
        
        # Compliance section
        if 'compliance' in report:
            lines.append("\n✅ COMPLIANCE")
            lines.append("-"*40)
            compliance = report['compliance']
            lines.append(f"Compliance Rate: {compliance.get('rate', 'N/A')}")
            lines.append(f"Commits Allowed: {compliance.get('commits_allowed', 0)}")
            lines.append(f"Commits Blocked: {compliance.get('commits_blocked', 0)}")
        
        # Phase progression
        if 'phase_progression' in report:
            lines.append("\n🚀 PHASE PROGRESSION")
            lines.append("-"*40)
            phase = report['phase_progression']
            lines.append(f"Current Phase: {phase.get('current_phase', 'Unknown')}")
            lines.append(f"Ready for Next: {'Yes' if phase.get('ready_for_next') else 'No'}")
            
            if phase.get('criteria_met'):
                lines.append("\n✅ Criteria Met:")
                for criteria in phase['criteria_met']:
                    lines.append(f"  • {criteria}")
            
            if phase.get('criteria_not_met'):
                lines.append("\n❌ Criteria Not Met:")
                for criteria in phase['criteria_not_met']:
                    lines.append(f"  • {criteria}")
        
        # Recommendations
        if report.get('recommendations'):
            lines.append("\n💡 RECOMMENDATIONS")
            lines.append("-"*40)
            for i, rec in enumerate(report['recommendations'], 1):
                lines.append(f"{i}. {rec}")
        
        lines.append("\n" + "="*70)
        
        return '\n'.join(lines)
    
    def send_email_report(self, report: Dict, recipients: List[str]) -> bool:
        """Send report via email"""
        # This would need SMTP configuration
        # Placeholder for email functionality
        print(f"Would send report to: {recipients}")
        return True
    
    def post_to_slack(self, report: Dict, webhook_url: str) -> bool:
        """Post report summary to Slack"""
        # This would need Slack webhook configuration
        # Placeholder for Slack integration
        print(f"Would post to Slack webhook: {webhook_url[:20]}...")
        return True
    
    def schedule_reports(self):
        """Schedule automated report generation"""
        # This would integrate with cron or task scheduler
        print("Report scheduling configured:")
        print("  • Daily: Every day at 9 AM")
        print("  • Weekly: Every Monday at 9 AM")
        print("  • Monthly: First day of month at 9 AM")


def main():
    """Generate and display reports"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Governance Reporting')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], 
                       default='daily', help='Report type to generate')
    parser.add_argument('--email', nargs='*', help='Email recipients')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    reporter = GovernanceReporter()
    
    # Generate report
    if args.type == 'daily':
        report = reporter.generate_daily_report()
    elif args.type == 'weekly':
        report = reporter.generate_weekly_report()
    else:
        report = reporter.generate_monthly_report()
    
    # Output report
    if args.format == 'json':
        print(json.dumps(report, indent=2))
    else:
        print(reporter.format_report_text(report))
    
    # Send if requested
    if args.email:
        reporter.send_email_report(report, args.email)
    
    print(f"\n✅ Report saved to: .governance/reports/")


if __name__ == '__main__':
    main()