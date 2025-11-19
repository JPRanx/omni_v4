#!/usr/bin/env python
"""
Directory Guardian - Automated Directory Standards Enforcement

This script enforces directory organization standards, detects violations,
and provides auto-fix capabilities to maintain codebase health.

Usage:
    python scripts/directory_guardian.py --check         # Check compliance
    python scripts/directory_guardian.py --fix           # Auto-fix violations
    python scripts/directory_guardian.py --report        # Generate report
    python scripts/directory_guardian.py --enforce       # Strict mode (for git hooks)

Author: Directory Guardian System
Version: 1.0
Last Updated: 2025-11-11
"""

import sys
import json
import yaml
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class Violation:
    """Represents a directory standards violation."""

    type: str  # misplaced_file, forbidden_pattern, missing_required, etc.
    severity: str  # error, warning
    file_path: str
    message: str
    auto_fix: Optional[str] = None
    points_deducted: int = 0
    category: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Fix:
    """Represents an applied fix."""

    violation: Violation
    action: str
    old_path: Optional[str] = None
    new_path: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "violation_type": self.violation.type,
            "action": self.action,
            "old_path": self.old_path,
            "new_path": self.new_path,
            "success": self.success,
            "error": self.error
        }


@dataclass
class HealthReport:
    """Comprehensive health report."""

    timestamp: str
    score: int
    status: str  # excellent, good, warning, critical
    violations: List[Violation] = field(default_factory=list)
    fixes_applied: List[Fix] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "score": self.score,
            "status": self.status,
            "violations": [v.to_dict() for v in self.violations],
            "fixes_applied": [f.to_dict() for f in self.fixes_applied],
            "stats": self.stats,
            "recommendations": self.recommendations
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# ==============================================================================
# DIRECTORY GUARDIAN
# ==============================================================================

class DirectoryGuardian:
    """
    Core enforcement engine that maintains directory standards.

    Responsibilities:
    - Load rules from configuration
    - Scan directory structure
    - Identify violations
    - Apply automatic fixes
    - Generate health reports
    """

    def __init__(self, rules_file: Optional[Path] = None, safe_mode: bool = True):
        """
        Initialize Directory Guardian.

        Args:
            rules_file: Path to rules YAML file
            safe_mode: Ask before applying fixes
        """
        self.project_root = project_root
        self.rules_file = rules_file or (project_root / "config" / "directory_rules.yaml")
        self.safe_mode = safe_mode

        # Load rules
        self.rules = self._load_rules()

        # Tracking
        self.violations: List[Violation] = []
        self.fixes_applied: List[Fix] = []

    def _load_rules(self) -> Dict[str, Any]:
        """Load rules from YAML configuration."""
        if not self.rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_file}")

        with open(self.rules_file, 'r') as f:
            rules = yaml.safe_load(f)

        return rules

    def check_compliance(self) -> Tuple[bool, List[Violation]]:
        """
        Check directory compliance against all rules.

        Returns:
            Tuple of (is_compliant, violations_list)
        """
        print("[*] Scanning directory structure...")

        self.violations = []

        # Check all rule categories
        self._check_file_locations()
        self._check_forbidden_patterns()
        self._check_required_structure()
        self._check_file_sizes()
        self._check_naming_conventions()

        is_compliant = len(self.violations) == 0

        return is_compliant, self.violations

    def _check_file_locations(self):
        """Check if files are in correct locations."""
        print("  [+] Checking file locations...")

        # Get all Python files
        python_files = list(self.project_root.glob("**/*.py"))

        allowed_python_dirs = self.rules.get("file_locations", {}).get("python_source", [])
        exempt_paths = self.rules.get("exceptions", {}).get("exempt_paths", [])

        for py_file in python_files:
            # Get relative path
            try:
                rel_path = py_file.relative_to(self.project_root)
            except ValueError:
                continue

            # Normalize path to use forward slashes
            rel_path_str = str(rel_path).replace('\\', '/')

            # Skip exempt paths (check if path starts with exempt directory)
            if any(rel_path_str.startswith(exempt.rstrip('/') + '/') or rel_path_str == exempt.rstrip('/') for exempt in exempt_paths):
                continue

            # Check if this is an allowed root file
            allowed_root_files = self.rules.get("exceptions", {}).get("allowed_root_files", [])
            if rel_path_str in allowed_root_files:
                continue

            # Check if in allowed directory
            in_allowed = any(
                rel_path_str.startswith(allowed_dir.rstrip('/') + '/') or
                rel_path_str.split('/')[0] == allowed_dir.rstrip('/')
                for allowed_dir in allowed_python_dirs
            )

            if not in_allowed:
                violation = Violation(
                    type="misplaced_file",
                    severity="error",
                    file_path=rel_path_str,
                    message=f"Python file not in allowed location ({', '.join(allowed_python_dirs)})",
                    auto_fix="move",
                    points_deducted=self.rules["health_scoring"]["violations"]["misplaced_file"],
                    category="file_location"
                )
                self.violations.append(violation)

    def _check_forbidden_patterns(self):
        """Check for forbidden patterns in source code."""
        print("  [+] Checking forbidden patterns...")

        # Get forbidden patterns for source files
        source_patterns = self.rules.get("forbidden_patterns", {}).get("in_source", [])
        any_patterns = self.rules.get("forbidden_patterns", {}).get("in_any", [])

        # Get all source files
        source_files = list(self.project_root.glob("src/**/*.py"))
        source_files.extend(list(self.project_root.glob("scripts/**/*.py")))

        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check source-specific patterns
                for pattern_rule in source_patterns:
                    pattern = pattern_rule["pattern"]
                    if pattern in content:
                        # Check if this file/pattern combo is in allowed_patterns
                        rel_path = str(source_file.relative_to(self.project_root)).replace('\\', '/')
                        allowed_patterns = self.rules.get("exceptions", {}).get("allowed_patterns", [])
                        is_allowed = any(
                            rel_path.startswith(ap.get("path", "").rstrip('/')) and ap.get("pattern") == pattern
                            for ap in allowed_patterns
                        )

                        if not is_allowed:
                            violation = Violation(
                                type="forbidden_pattern",
                                severity=pattern_rule["severity"],
                                file_path=rel_path,
                                message=f"{pattern_rule['message']} (found: {pattern})",
                                auto_fix=pattern_rule.get("auto_fix"),
                                points_deducted=self.rules["health_scoring"]["violations"][f"forbidden_pattern_{pattern_rule['severity']}"],
                                category="code_quality"
                            )
                            self.violations.append(violation)

            except Exception as e:
                # Skip files that can't be read
                pass

        # Check all files for general patterns
        all_files = list(self.project_root.glob("**/*"))
        exempt_paths = self.rules.get("exceptions", {}).get("exempt_paths", [])

        for file_path in all_files:
            if not file_path.is_file():
                continue

            # Get relative path and normalize
            try:
                rel_path = file_path.relative_to(self.project_root)
                rel_path_str = str(rel_path).replace('\\', '/')
            except ValueError:
                continue

            # Skip exempt paths
            if any(rel_path_str.startswith(exempt.rstrip('/') + '/') or rel_path_str == exempt.rstrip('/') for exempt in exempt_paths):
                continue

            # Check file extension patterns
            for pattern_rule in any_patterns:
                pattern = pattern_rule["pattern"]
                if file_path.name.endswith(pattern.replace("$", "")):
                    violation = Violation(
                        type="forbidden_file_type",
                        severity=pattern_rule["severity"],
                        file_path=rel_path_str,
                        message=pattern_rule["message"],
                        auto_fix=pattern_rule.get("auto_fix"),
                        points_deducted=self.rules["health_scoring"]["violations"][f"forbidden_pattern_{pattern_rule['severity']}"],
                        category="file_type"
                    )
                    self.violations.append(violation)

    def _check_required_structure(self):
        """Check for required files in required locations."""
        print("  [+] Checking required structure...")

        required = self.rules.get("required_structure", {})

        for directory, requirements in required.items():
            dir_path = self.project_root / directory

            if not dir_path.exists():
                continue  # Directory doesn't exist yet, skip

            required_files = requirements.get("required_files", [])

            for required_file in required_files:
                file_path = dir_path / required_file

                if not file_path.exists():
                    violation = Violation(
                        type="missing_required_file",
                        severity="error",
                        file_path=str(file_path.relative_to(self.project_root)),
                        message=f"Required file missing: {required_file} in {directory}",
                        auto_fix="create",
                        points_deducted=self.rules["health_scoring"]["violations"]["missing_required_file"],
                        category="structure"
                    )
                    self.violations.append(violation)

    def _check_file_sizes(self):
        """Check file sizes against limits."""
        print("  [+] Checking file sizes...")

        size_limits = self.rules.get("size_limits", {})

        for file_type, limits in size_limits.items():
            max_lines = limits.get("max_lines", float('inf'))

            # Determine file pattern
            if file_type == "python":
                pattern = "**/*.py"
            elif file_type == "json":
                pattern = "**/*.json"
            elif file_type == "markdown":
                pattern = "**/*.md"
            elif file_type == "yaml":
                pattern = "**/*.yaml"
            else:
                continue

            # Check all matching files
            files = list(self.project_root.glob(pattern))
            exempt_paths = self.rules.get("exceptions", {}).get("exempt_paths", [])

            for file_path in files:
                # Get relative path and normalize
                try:
                    rel_path = file_path.relative_to(self.project_root)
                    rel_path_str = str(rel_path).replace('\\', '/')
                except ValueError:
                    continue

                # Skip exempt paths
                if any(exempt.rstrip('/') in rel_path_str for exempt in exempt_paths):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)

                    if line_count > max_lines:
                        violation = Violation(
                            type="size_limit_exceeded",
                            severity=limits.get("severity", "warning"),
                            file_path=rel_path_str,
                            message=f"{limits.get('message', 'File too large')}: {line_count} lines (max: {max_lines})",
                            auto_fix=None,  # Requires manual refactoring
                            points_deducted=self.rules["health_scoring"]["violations"]["size_limit_exceeded"],
                            category="size"
                        )
                        self.violations.append(violation)

                except Exception:
                    pass

    def _check_naming_conventions(self):
        """Check file naming conventions."""
        print("  [+] Checking naming conventions...")

        naming_rules = self.rules.get("naming_conventions", {})

        # Check Python modules
        if "python_modules" in naming_rules:
            rule = naming_rules["python_modules"]
            pattern = re.compile(rule["pattern"])

            python_files = list(self.project_root.glob("src/**/*.py"))
            python_files.extend(list(self.project_root.glob("scripts/**/*.py")))

            for py_file in python_files:
                if py_file.name == "__init__.py":
                    continue  # Skip __init__.py

                if not pattern.match(py_file.name):
                    violation = Violation(
                        type="naming_violation",
                        severity=rule["severity"],
                        file_path=str(py_file.relative_to(self.project_root)),
                        message=f"{rule['message']}: {py_file.name}",
                        auto_fix=None,  # Requires manual renaming
                        points_deducted=self.rules["health_scoring"]["violations"][f"naming_violation_{rule['severity']}"],
                        category="naming"
                    )
                    self.violations.append(violation)

    def auto_fix(self, violations: Optional[List[Violation]] = None) -> List[Fix]:
        """
        Attempt automatic fixes for violations.

        Args:
            violations: List of violations to fix (defaults to all)

        Returns:
            List of fixes applied
        """
        if violations is None:
            violations = self.violations

        print("\n[*] Applying automatic fixes...")

        self.fixes_applied = []

        for violation in violations:
            if not violation.auto_fix:
                continue  # Not auto-fixable

            # Apply fix based on type
            if violation.auto_fix == "move":
                fix = self._fix_move_file(violation)
            elif violation.auto_fix == "delete_file":
                fix = self._fix_delete_file(violation)
            elif violation.auto_fix == "create":
                fix = self._fix_create_file(violation)
            elif violation.auto_fix == "remove_line":
                fix = self._fix_remove_pattern(violation)
            elif violation.auto_fix == "comment_out":
                fix = self._fix_comment_out(violation)
            else:
                continue  # Unknown fix type

            if fix:
                self.fixes_applied.append(fix)

        return self.fixes_applied

    def _fix_move_file(self, violation: Violation) -> Optional[Fix]:
        """Move misplaced file to correct location."""
        # This is complex and risky, skip for now
        return None

    def _fix_delete_file(self, violation: Violation) -> Optional[Fix]:
        """Delete forbidden file (backup, temp, etc)."""
        file_path = self.project_root / violation.file_path

        if not file_path.exists():
            return None

        if self.safe_mode:
            response = input(f"  Delete {violation.file_path}? [y/N]: ")
            if response.lower() != 'y':
                return None

        try:
            file_path.unlink()
            print(f"  [+] Deleted: {violation.file_path}")

            return Fix(
                violation=violation,
                action="delete",
                old_path=str(violation.file_path),
                success=True
            )

        except Exception as e:
            return Fix(
                violation=violation,
                action="delete",
                old_path=str(violation.file_path),
                success=False,
                error=str(e)
            )

    def _fix_create_file(self, violation: Violation) -> Optional[Fix]:
        """Create missing required file."""
        file_path = self.project_root / violation.file_path

        if file_path.exists():
            return None  # Already exists

        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file with appropriate content
        if file_path.name == "__init__.py":
            content = '"""Package initialization file."""\n'
        else:
            content = ""

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  [+] Created: {violation.file_path}")

            return Fix(
                violation=violation,
                action="create",
                new_path=str(violation.file_path),
                success=True
            )

        except Exception as e:
            return Fix(
                violation=violation,
                action="create",
                new_path=str(violation.file_path),
                success=False,
                error=str(e)
            )

    def _fix_remove_pattern(self, violation: Violation) -> Optional[Fix]:
        """Remove forbidden pattern from file."""
        # Complex, skip for now
        return None

    def _fix_comment_out(self, violation: Violation) -> Optional[Fix]:
        """Comment out forbidden pattern."""
        # Complex, skip for now
        return None

    def calculate_health_score(self) -> int:
        """
        Calculate health score based on violations.

        Returns:
            Health score (0-100)
        """
        base_score = self.rules["health_scoring"]["base_score"]
        total_deductions = sum(v.points_deducted for v in self.violations)

        score = max(0, base_score + total_deductions)  # Deductions are negative

        return score

    def get_status(self, score: int) -> str:
        """
        Get status based on score.

        Args:
            score: Health score

        Returns:
            Status string
        """
        thresholds = self.rules["health_scoring"]["thresholds"]

        if score >= thresholds["excellent"]:
            return "excellent"
        elif score >= thresholds["good"]:
            return "good"
        elif score >= thresholds["warning"]:
            return "warning"
        else:
            return "critical"

    def generate_report(self) -> HealthReport:
        """
        Generate comprehensive health report.

        Returns:
            HealthReport object
        """
        score = self.calculate_health_score()
        status = self.get_status(score)

        # Generate statistics
        stats = {
            "total_violations": len(self.violations),
            "by_severity": {},
            "by_category": {},
            "by_type": {},
            "total_fixes_applied": len(self.fixes_applied),
            "successful_fixes": sum(1 for f in self.fixes_applied if f.success)
        }

        # Count by severity
        for v in self.violations:
            stats["by_severity"][v.severity] = stats["by_severity"].get(v.severity, 0) + 1
            stats["by_category"][v.category] = stats["by_category"].get(v.category, 0) + 1
            stats["by_type"][v.type] = stats["by_type"].get(v.type, 0) + 1

        # Generate recommendations
        recommendations = []

        if score < 100:
            recommendations.append(f"Fix {len(self.violations)} violation(s) to reach 100/100")

        if stats.get("by_severity", {}).get("error", 0) > 0:
            recommendations.append("Address all error-level violations immediately")

        if stats.get("by_category", {}).get("code_quality", 0) > 0:
            recommendations.append("Remove debug code and TODO markers from source")

        # Create report
        report = HealthReport(
            timestamp=datetime.now().isoformat(),
            score=score,
            status=status,
            violations=self.violations,
            fixes_applied=self.fixes_applied,
            stats=stats,
            recommendations=recommendations
        )

        return report

    def save_report(self, report: HealthReport, format: str = "json"):
        """
        Save health report to file.

        Args:
            report: HealthReport to save
            format: Output format (json, html, markdown)
        """
        output_dir = self.project_root / "outputs" / "health"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            output_file = output_dir / f"health_report_{timestamp}.json"
            with open(output_file, 'w') as f:
                f.write(report.to_json())

            print(f"\n[+] Report saved: {output_file}")

        elif format == "markdown":
            output_file = output_dir / f"health_report_{timestamp}.md"
            md_content = self._generate_markdown_report(report)
            with open(output_file, 'w') as f:
                f.write(md_content)

            print(f"\n[+] Report saved: {output_file}")

    def _generate_markdown_report(self, report: HealthReport) -> str:
        """Generate markdown report."""
        lines = [
            f"# Directory Health Report",
            f"",
            f"**Timestamp:** {report.timestamp}",
            f"**Score:** {report.score}/100",
            f"**Status:** {report.status.upper()}",
            f"",
            f"## Summary",
            f"",
            f"- Total Violations: {report.stats['total_violations']}",
            f"- Fixes Applied: {report.stats['total_fixes_applied']}",
            f"- Successful Fixes: {report.stats['successful_fixes']}",
            f"",
        ]

        if report.violations:
            lines.append("## Violations")
            lines.append("")
            for v in report.violations:
                lines.append(f"### {v.type.replace('_', ' ').title()}")
                lines.append(f"- **File:** {v.file_path}")
                lines.append(f"- **Severity:** {v.severity}")
                lines.append(f"- **Message:** {v.message}")
                lines.append("")

        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)

    def print_summary(self, report: HealthReport):
        """Print human-readable summary."""
        print("\n" + "=" * 70)
        print("DIRECTORY HEALTH REPORT")
        print("=" * 70)

        # Score indicator
        score_indicator = "[OK]" if report.score == 100 else "[!!]" if report.score >= 95 else "[XX]"
        print(f"\nHealth Score: {score_indicator} {report.score}/100 ({report.status.upper()})")

        print(f"\nStatistics:")
        print(f"  Total Violations: {report.stats['total_violations']}")
        if report.stats.get('by_severity'):
            for severity, count in report.stats['by_severity'].items():
                print(f"    {severity.title()}: {count}")

        if report.fixes_applied:
            print(f"\nFixes Applied: {len(report.fixes_applied)}")
            print(f"  Successful: {report.stats['successful_fixes']}")

        if report.violations:
            print(f"\nViolations:")
            for v in report.violations[:10]:  # Show first 10
                print(f"  [{v.severity.upper()}] {v.file_path}")
                print(f"    {v.message}")

        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")

        print("\n" + "=" * 70)


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Directory Guardian - Automated Directory Standards Enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/directory_guardian.py --check          # Check compliance
  python scripts/directory_guardian.py --fix            # Auto-fix violations
  python scripts/directory_guardian.py --report         # Generate report
  python scripts/directory_guardian.py --enforce        # Strict mode (git hook)
        """
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check directory compliance"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix violations"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate health report"
    )

    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Strict mode for git hooks (blocks on violations)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="both",
        help="Report format"
    )

    parser.add_argument(
        "--no-safe-mode",
        action="store_true",
        help="Disable safe mode (auto-fix without confirmation)"
    )

    args = parser.parse_args()

    # Default to check if no action specified
    if not any([args.check, args.fix, args.report, args.enforce]):
        args.check = True

    # Initialize guardian
    guardian = DirectoryGuardian(safe_mode=not args.no_safe_mode)

    # Check compliance
    is_compliant, violations = guardian.check_compliance()

    # Apply fixes if requested
    if args.fix:
        guardian.auto_fix()

    # Generate report
    report = guardian.generate_report()

    # Print summary
    guardian.print_summary(report)

    # Save report
    if args.report or args.enforce:
        if args.format in ["json", "both"]:
            guardian.save_report(report, format="json")
        if args.format in ["markdown", "both"]:
            guardian.save_report(report, format="markdown")

    # Enforce mode (for git hooks)
    if args.enforce:
        min_score = guardian.rules["health_scoring"]["minimum_score"]
        if report.score < min_score:
            print(f"\n[XX] ENFORCEMENT FAILED: Score {report.score} below minimum {min_score}")
            sys.exit(1)

    # Exit with appropriate code
    if not is_compliant and args.enforce:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
