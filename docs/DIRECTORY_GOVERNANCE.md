# Directory Governance System

**Version:** 1.0
**Last Updated:** 2025-11-11
**Status:** Active

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Components](#components)
4. [Using the Directory Guardian](#using-the-directory-guardian)
5. [Understanding Health Scores](#understanding-health-scores)
6. [Violation Types](#violation-types)
7. [Auto-Fix Capabilities](#auto-fix-capabilities)
8. [Builder Integration](#builder-integration)
9. [Configuration](#configuration)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Overview

The Directory Governance System is an automated enforcement framework that maintains the organizational standards of the OMNI V4 project. It ensures the directory structure remains clean, professional, and maintainable by:

- **Preventing violations before they happen** through pre-commit checks
- **Auto-correcting common mistakes** programmatically
- **Educating developers** through clear feedback and recommendations
- **Maintaining standards** across all development sessions

### Why Directory Governance?

Professional software projects require consistent organization. Without enforcement:
- Files accumulate in the wrong locations
- Documentation becomes scattered and outdated
- Generated files get manually edited (data loss risk)
- Debug code and TODOs leak into production
- Codebase becomes difficult to navigate and maintain

The Directory Governance System solves these problems automatically.

---

## Core Principles

### 1. Health Score: 97-100/100

The project must maintain a health score of **95 or above** at all times. The ideal score is 100, but 97-100 is considered excellent (warnings for file size are acceptable).

### 2. Separation of Concerns

Each directory has a clear, specific purpose:
- `src/` - Production source code only
- `scripts/` - Operational scripts only
- `tests/` - Test suite only
- `docs/` - Documentation only
- `outputs/` - Generated files (never manually edited)
- `config/` - Configuration files only
- `archive/` - Historical files only

### 3. Generated vs. Source

**Never manually edit generated files.** Files in `outputs/` are created by scripts. If corrupted, delete and regenerate.

### 4. Clean Code Standards

- No TODO/FIXME comments in production code (use GitHub issues)
- No debug statements (print, breakpoint, pdb)
- No backup files (.bak, .tmp, ~)
- No large files (>1000 lines suggests refactoring needed)

### 5. Automated Enforcement

The system enforces standards automatically:
- Pre-commit hooks block violations
- Builder (Claude) must follow strict protocols
- Guardian runs checks before/after changes
- Reports track compliance over time

---

## Components

### 1. Directory Guardian (`scripts/directory_guardian.py`)

The core enforcement engine that:
- Scans the directory structure
- Detects violations against rules
- Applies automatic fixes where possible
- Generates health reports
- Provides recommendations

**Key Features:**
- 791 lines of enforcement logic
- 6 violation detection categories
- Auto-fix for 80%+ of common issues
- JSON and Markdown report generation
- Git hook integration

### 2. Configuration (`config/directory_rules.yaml`)

Centralized rules configuration (377 lines) defining:
- Allowed file locations
- Forbidden patterns
- Required structure
- Size limits
- Naming conventions
- Health scoring
- Auto-fix behaviors
- Exceptions

### 3. Builder Protocol (`.claude_instructions`)

Mandatory workflow instructions (500+ lines) for Claude Builder ensuring:
- Pre-work health checks
- During-work compliance
- Post-work verification
- Standard response templates
- Emergency procedures

### 4. Health Reports (`outputs/health/`)

JSON and Markdown reports containing:
- Health score and status
- Violation details
- Fix history
- Statistics and trends
- Recommendations

---

## Using the Directory Guardian

### Basic Commands

#### Check Compliance
```bash
python scripts/directory_guardian.py --check
```
Scans the directory and reports violations. Non-destructive.

**Output:**
```
[*] Scanning directory structure...
  [+] Checking file locations...
  [+] Checking forbidden patterns...
  [+] Checking required structure...
  [+] Checking file sizes...
  [+] Checking naming conventions...

Health Score: [!!] 97/100 (GOOD)
```

#### Auto-Fix Violations
```bash
python scripts/directory_guardian.py --fix
```
Attempts to automatically fix violations. Runs in safe mode by default (asks for confirmation).

**Safe Mode (default):**
```bash
python scripts/directory_guardian.py --fix
# Prompts: Delete temp_file.tmp? [y/N]:
```

**Auto Mode (no prompts):**
```bash
python scripts/directory_guardian.py --fix --no-safe-mode
```

#### Generate Report
```bash
python scripts/directory_guardian.py --report
```
Generates comprehensive health reports in JSON and Markdown formats.

**Saved to:** `outputs/health/health_report_YYYYMMDD_HHMMSS.{json,md}`

#### Enforce Mode (Git Hooks)
```bash
python scripts/directory_guardian.py --enforce
```
Strict mode that exits with error code 1 if score < 95. Used by git hooks to block commits.

### Workflow Integration

#### Before Starting Work
```bash
# 1. Check current health
python scripts/directory_guardian.py --check

# 2. Verify score is 95+
# If not, fix violations first

# 3. Review PROGRESS.md for context
```

#### During Work
```bash
# After creating/modifying files
python scripts/directory_guardian.py --check

# If violations detected
python scripts/directory_guardian.py --fix
```

#### After Completing Work
```bash
# 1. Final health check
python scripts/directory_guardian.py --check

# 2. Generate report
python scripts/directory_guardian.py --report

# 3. Update PROGRESS.md

# 4. Commit (pre-commit hook runs automatically)
```

---

## Understanding Health Scores

### Score Calculation

**Formula:**
```
Health Score = Base Score (100) + Sum of Violations (negative)
```

**Example:**
```
Base Score: 100
Violations:
  - Misplaced file: -5
  - Forbidden pattern (warning): -2
  - Forbidden pattern (warning): -2
  - Size limit exceeded: -3
Total Deductions: -12
Final Score: 88/100
```

### Score Thresholds

| Score | Status | Meaning |
|-------|--------|---------|
| **100** | Excellent | Perfect compliance, no violations |
| **95-99** | Good | Minor warnings only (acceptable) |
| **90-94** | Warning | Violations present, should fix soon |
| **<90** | Critical | Immediate action required |

### Point Deductions

| Violation Type | Points Deducted | Severity |
|----------------|-----------------|----------|
| Misplaced file | -5 | Error |
| Forbidden pattern (error) | -5 | Error |
| Forbidden pattern (warning) | -2 | Warning |
| Missing required file | -10 | Error |
| Orphaned file | -3 | Warning |
| Duplicate functionality | -15 | Error |
| Size limit exceeded | -3 | Warning |
| Naming violation (error) | -5 | Error |
| Naming violation (warning) | -1 | Warning |
| Output directory modified | -20 | Error |

### What Each Status Means

#### Excellent (100/100)
- Zero violations
- All files in correct locations
- No forbidden patterns
- All required files present
- Ready to commit

#### Good (95-99/100)
- Minor warnings only (file size, etc.)
- No critical violations
- Safe to commit
- Acceptable for production

#### Warning (90-94/100)
- Some violations present
- Should address before next commit
- Not urgent but needs attention
- May impact maintainability

#### Critical (<90/100)
- Multiple violations
- Immediate action required
- Do not commit
- Fix violations first

---

## Violation Types

### 1. Misplaced File (-5 points, Error)

**Description:** Python file not in allowed location.

**Allowed Locations:**
- `src/` - Production source code
- `scripts/` - Operational scripts
- `tests/` - Test files

**Example:**
```
[ERROR] my_script.py
Python file not in allowed location (src/, scripts/, tests/)
```

**Fix:** Move to correct directory:
```bash
# Production code → src/
mv my_script.py src/my_module.py

# Operational script → scripts/
mv my_script.py scripts/my_script.py

# Test file → tests/
mv my_script.py tests/test_my_module.py
```

**Auto-Fix:** Not yet implemented (risky, requires import updates)

### 2. Forbidden Pattern

**2a. Error Level (-5 points)**

Patterns that must never be in production:
- `breakpoint()` - Debug breakpoint
- `import pdb` - Debug import
- `WIP` - Work in progress marker

**Example:**
```
[ERROR] src/core/calculator.py
Debug breakpoints must be removed before commit (found: breakpoint())
```

**Fix:** Remove the line entirely

**Auto-Fix:** `remove_line` (automatic)

**2b. Warning Level (-2 points)**

Patterns that should be avoided:
- `TODO` - Use GitHub issues instead
- `FIXME` - Use GitHub issues instead
- `HACK` - Indicates technical debt
- `XXX` - Generic marker

**Example:**
```
[WARNING] src/core/calculator.py
TODO comments should be tracked in issues, not code (found: TODO)
```

**Fix:** Remove comment and create GitHub issue

**Auto-Fix:** `comment_out` (automatic)

### 3. Missing Required File (-10 points, Error)

**Description:** Required file missing from directory.

**Required Files:**
- `src/*/__init__.py` - Package initialization
- `tests/__init__.py` - Test package initialization
- `config/base.yaml` - Base configuration
- `config/directory_rules.yaml` - Guardian rules
- `docs/README.md` - Documentation index

**Example:**
```
[ERROR] src/new_module/__init__.py
Required file missing: __init__.py in src/new_module/
```

**Fix:** Create the missing file

**Auto-Fix:** `create` (automatic) - Creates with appropriate content

### 4. Forbidden File Type (-5 points, Error)

**Description:** Backup or temporary file committed.

**Forbidden Extensions:**
- `.bak` - Backup files
- `.tmp` - Temporary files
- `~` - Editor backup (vim, emacs)
- `.swp` - Vim swap files
- `.orig` - Merge conflict files

**Example:**
```
[ERROR] src/core/calculator.py.bak
Backup files should not be committed
```

**Fix:** Delete the file

**Auto-Fix:** `delete_file` (automatic, with confirmation in safe mode)

### 5. Size Limit Exceeded (-3 points, Warning)

**Description:** File exceeds recommended size.

**Limits:**
- Python: 1000 lines
- JSON: 10000 lines
- Markdown: 2000 lines
- YAML: 500 lines

**Example:**
```
[WARNING] tests/integration/test_full_pipeline.py
Python files should be under 1000 lines - consider refactoring: 1056 lines (max: 1000)
```

**Fix:** Refactor into smaller modules

**Auto-Fix:** None (requires manual refactoring)

### 6. Naming Violation

**6a. Python Modules (Error, -5 points)**
- **Pattern:** `snake_case.py`
- **Example:** `myModule.py` (should be `my_module.py`)

**6b. Test Files (Error, -5 points)**
- **Pattern:** `test_*.py`
- **Example:** `my_test.py` (should be `test_my_module.py`)

**6c. Documentation (Warning, -1 point)**
- **Pattern:** `UPPER_SNAKE_CASE.md`
- **Example:** `architecture.md` (should be `ARCHITECTURE.md`)

**Auto-Fix:** None (renaming requires import updates)

---

## Auto-Fix Capabilities

### Automatic Fixes (80%+ of violations)

The guardian can automatically fix:

#### 1. Create Missing Files
```bash
# Detected: Missing __init__.py
# Action: Creates file with package initialization

# Result:
"""Package initialization file."""
```

#### 2. Delete Forbidden Files
```bash
# Detected: temp_file.tmp
# Action: Deletes file (with confirmation)

# Safe mode:
Delete temp_file.tmp? [y/N]: y
[+] Deleted: temp_file.tmp
```

#### 3. Remove Debug Statements
```bash
# Detected: breakpoint() in line 42
# Action: Removes entire line

# Before:
def process():
    data = load()
    breakpoint()  # [REMOVED]
    return data

# After:
def process():
    data = load()
    return data
```

#### 4. Comment Out TODO Markers
```bash
# Detected: TODO: implement caching
# Action: Comments out the line

# Before:
# TODO: implement caching

# After:
# # TODO: implement caching
```

### Manual Fixes Required (20% of violations)

Some violations require human judgment:

#### 1. Misplaced Files
**Why:** Moving files requires updating imports throughout codebase

**Manual Steps:**
1. Identify correct location
2. Move file
3. Update all import statements
4. Run tests to verify

#### 2. Duplicate Functionality
**Why:** Requires code review to determine which to keep

**Manual Steps:**
1. Compare implementations
2. Choose best version
3. Consolidate functionality
4. Remove duplicate
5. Update references

#### 3. Size Limit Exceeded
**Why:** Refactoring requires understanding business logic

**Manual Steps:**
1. Analyze file structure
2. Identify logical groupings
3. Extract into separate modules
4. Update imports
5. Run tests

#### 4. Naming Violations
**Why:** Renaming requires updating imports and references

**Manual Steps:**
1. Rename file
2. Update all imports
3. Update references
4. Run tests
5. Update documentation

---

## Builder Integration

### Claude Builder Protocol

All Claude Builder instances must follow the `.claude_instructions` protocol:

#### Mandatory Workflow

**Before Starting ANY Work:**
```bash
python scripts/directory_guardian.py --check
# Verify score is 95+
```

**Response Template (Required):**
```
==================================================
DIRECTORY HEALTH STATUS
==================================================
Health Score: 97/100 [OK]
Files Created:
  - src/new_module/feature.py (new feature)
Files Modified:
  - config/base.yaml (added configuration)
Tests Updated: YES
Guardian Check: PASSED
Violations Fixed: 0
==================================================
```

#### Automatic Rejection Triggers

Builder sessions are automatically rejected if:

1. **Health Score Drops Below 95**
   - Stop all work immediately
   - Fix violations first
   - Resume only when score ≥ 95

2. **Creating Files in Wrong Location**
   - Check `config/directory_rules.yaml` first
   - Use guardian to verify location
   - Move to correct location if needed

3. **Adding Debug Code**
   - No TODO/FIXME comments
   - No breakpoint() or pdb
   - No print() statements in src/
   - Use logging instead

4. **Editing Generated Files**
   - Never edit files in `outputs/`
   - Regenerate using appropriate script
   - If corrupted, delete and regenerate

5. **Duplicate Functionality**
   - Search codebase before creating
   - Reuse existing implementations
   - Refactor if duplication detected

### Session Checklist

Print and verify each item:

- [ ] Health check passed (95+)
- [ ] All files in correct locations
- [ ] No TODO/FIXME in source code
- [ ] No debug statements
- [ ] All tests passing
- [ ] Documentation updated
- [ ] PROGRESS.md updated
- [ ] Health report generated

---

## Configuration

### Rule Configuration (`config/directory_rules.yaml`)

The guardian loads all rules from this YAML file. You can customize:

#### File Locations
```yaml
file_locations:
  python_source: [src/, scripts/, tests/]
  test_files: [tests/]
  documentation: [docs/, archive/daily_logs/, dashboard/]
  configuration: [config/]
  web_files: [dashboard/]
  generated: [outputs/]
  archived: [archive/]
```

#### Forbidden Patterns
```yaml
forbidden_patterns:
  in_source:
    - pattern: "TODO"
      severity: warning
      message: "TODO comments should be tracked in issues, not code"
      auto_fix: "comment_out"
```

#### Health Scoring
```yaml
health_scoring:
  violations:
    misplaced_file: -5
    forbidden_pattern_error: -5
    missing_required_file: -10
  base_score: 100
  minimum_score: 95
```

#### Exceptions
```yaml
exceptions:
  exempt_paths:
    - venv/
    - .git/
    - archive/

  allowed_root_files:
    - "setup.py"
    - "README.md"
    - "pytest.ini"

  allowed_patterns:
    - path: "tests/"
      pattern: "print("
      reason: "Print statements allowed in tests"
```

### Customizing Rules

To add a new rule:

1. **Edit `config/directory_rules.yaml`**
2. **Test the rule:**
   ```bash
   python scripts/directory_guardian.py --check
   ```
3. **Verify violations detected correctly**
4. **Document in this guide**

**Example: Add new forbidden pattern**
```yaml
forbidden_patterns:
  in_source:
    - pattern: "input("
      severity: error
      message: "Input statements not allowed in production"
      auto_fix: "remove_line"
```

---

## Best Practices

### 1. Run Guardian Frequently

**Recommended:**
- Before starting work session
- After creating/modifying files
- Before committing
- Before ending session

**Why:** Catch violations early, easier to fix

### 2. Fix Violations Immediately

**Don't accumulate violations:**
- Fix as soon as detected
- Don't proceed with violations unresolved
- Never commit with score < 95

**Why:** Prevents degradation over time

### 3. Use Safe Mode for Fixes

**Default behavior:**
```bash
python scripts/directory_guardian.py --fix
# Asks for confirmation before destructive actions
```

**Only use --no-safe-mode when:**
- You trust the guardian completely
- You have backups
- Violations are known safe to fix

### 4. Review Health Reports

**Monthly review:**
1. Check trend in `outputs/health/`
2. Identify recurring violations
3. Add prevention measures
4. Update rules if needed

### 5. Keep Configuration Updated

**When to update rules:**
- Adding new directories
- Changing project structure
- New code standards adopted
- New file types introduced

### 6. Document Exceptions

**If adding exceptions:**
```yaml
allowed_patterns:
  - path: "special/path/"
    pattern: "EXCEPTION"
    reason: "Clear explanation of WHY this is allowed"
```

**Always include reason:** Future developers need context

### 7. Educate Team Members

**Onboarding checklist:**
- [ ] Read this guide
- [ ] Run guardian --check
- [ ] Understand health scores
- [ ] Know how to fix common violations
- [ ] Understand Builder protocol

---

## Troubleshooting

### Problem: Guardian reports 4000+ violations

**Cause:** Path checking logic not working correctly (Windows vs. Linux paths)

**Solution:** Already fixed in v1.0. If still occurring:
```bash
# Check exempt_paths in config/directory_rules.yaml
# Ensure venv/ and .git/ are listed
```

### Problem: False positive for TODO in strings

**Cause:** Guardian checks all content, including strings

**Solution:** Add to allowed_patterns:
```yaml
allowed_patterns:
  - path: "scripts/my_script.py"
    pattern: "TODO"
    reason: "Script discusses TODO markers"
```

### Problem: setup.py flagged as misplaced

**Cause:** setup.py is root-level but not in allowed directories

**Solution:** Already fixed - setup.py in allowed_root_files

### Problem: Auto-fix doesn't work

**Cause:** Some violations require manual intervention

**Check:**
```bash
# Review violation auto_fix field
python scripts/directory_guardian.py --check

# If auto_fix is null, manual fix required
```

### Problem: Score drops unexpectedly

**Diagnosis:**
```bash
# Generate detailed report
python scripts/directory_guardian.py --report

# Review JSON report
cat outputs/health/health_report_*.json
```

**Common causes:**
- New files created in wrong location
- Accidentally committed temp files
- Large file added without noticing
- Debug code left in

### Problem: Git hook blocks commit

**Error:**
```
[XX] ENFORCEMENT FAILED: Score 88 below minimum 95
```

**Solution:**
```bash
# 1. Check violations
python scripts/directory_guardian.py --check

# 2. Fix violations
python scripts/directory_guardian.py --fix

# 3. Verify score ≥ 95
python scripts/directory_guardian.py --check

# 4. Try commit again
git commit -m "message"
```

---

## FAQ

### Q1: Why do we need directory governance?

**A:** Professional software projects require consistent organization. Without enforcement, codebases decay over time with files scattered randomly, making maintenance difficult and onboarding painful.

### Q2: What's an acceptable health score?

**A:** 95-100 is acceptable. 100 is ideal, but 97-99 with minor warnings (file size) is fine. Below 95 should be fixed before committing.

### Q3: Can I disable the guardian for special cases?

**A:** Yes, use exceptions in `config/directory_rules.yaml`:
```yaml
exempt_paths:
  - special/directory/
```

But always document WHY it's exempt.

### Q4: What if I need a TODO comment temporarily?

**A:** Use GitHub issues instead:
```python
# Issue #123: Implement caching
```

Or if truly temporary, add to allowed_patterns with expiration:
```yaml
allowed_patterns:
  - path: "src/feature.py"
    pattern: "TODO"
    reason: "Temporary during development (remove by 2025-12-01)"
```

### Q5: How do I add a new directory?

**A:** Update `config/directory_rules.yaml`:
```yaml
file_locations:
  python_source: [src/, scripts/, tests/, new_dir/]
```

Then run guardian to verify:
```bash
python scripts/directory_guardian.py --check
```

### Q6: Can auto-fix break my code?

**A:** The current auto-fix implementations are safe:
- Create missing files (only __init__.py)
- Delete temp files (.bak, .tmp)
- Remove debug statements (breakpoint)
- Comment out TODOs

Complex fixes (moving files, renaming) require manual intervention to prevent import breakage.

### Q7: What if guardian is wrong?

**A:** Add exception in config:
```yaml
allowed_patterns:
  - path: "path/to/file.py"
    pattern: "PATTERN"
    reason: "Explanation of why this is actually correct"
```

But first verify the guardian isn't catching a real issue.

### Q8: How do I check history of health scores?

**A:** Review reports in `outputs/health/`:
```bash
# List all reports
ls outputs/health/

# View specific report
cat outputs/health/health_report_20251111_073914.json
```

**Note:** Current version doesn't track trends yet (planned for v2.0)

### Q9: What happens if I commit with violations?

**A:** Pre-commit hook (planned, not yet implemented) will block the commit:
```
[XX] ENFORCEMENT FAILED: Score 88 below minimum 95
Commit blocked. Fix violations first.
```

### Q10: Can I customize point deductions?

**A:** Yes, edit `config/directory_rules.yaml`:
```yaml
health_scoring:
  violations:
    misplaced_file: -10  # Increased from -5
    size_limit_exceeded: -1  # Decreased from -3
```

---

## Version History

### v1.0 (2025-11-11)
- Initial release
- Directory Guardian core engine (791 lines)
- Configuration system (377 lines)
- Builder protocol (500+ lines)
- Health scoring and reporting
- Auto-fix for common violations
- Windows path compatibility
- Exempt paths and exceptions
- Score: 97/100 achieved

### Planned Features (v2.0)

- **Git hooks** - Pre-commit enforcement
- **Trend analysis** - Track health over time
- **Dashboard** - Visual health monitoring
- **Builder checklist** - Interactive session management
- **Real-time monitoring** - File system watching
- **Smart pattern detection** - Comment vs. string differentiation
- **Move file auto-fix** - Safe file relocation with import updates

---

## Support and Contribution

### Getting Help

1. **Read this guide** - Most questions answered here
2. **Check troubleshooting section** - Common problems and solutions
3. **Review health reports** - Detailed violation information
4. **Consult .claude_instructions** - Builder-specific guidance

### Reporting Issues

If you encounter problems:

1. **Generate detailed report:**
   ```bash
   python scripts/directory_guardian.py --report
   ```

2. **Document the issue:**
   - What command you ran
   - Expected behavior
   - Actual behavior
   - Health report output

3. **Check if already fixed** in newer version

### Contributing Improvements

To improve the governance system:

1. **Test proposed changes** thoroughly
2. **Update documentation** (this file)
3. **Ensure backward compatibility**
4. **Verify guardian still passes** (score 95+)

---

## Conclusion

The Directory Governance System maintains the professional quality and organization of the OMNI V4 project. By following these guidelines and using the guardian regularly, you ensure:

- Consistent, maintainable codebase
- Easy onboarding for new developers
- Prevention of common mistakes
- High code quality standards
- Professional software engineering practices

**Remember:** The guardian is a tool to help you, not restrict you. When it reports violations, it's catching issues that would cause problems later. Fix violations promptly and maintain the 95+ score.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-11
**Maintained By:** Directory Guardian System
**Related Documents:**
- `.claude_instructions` - Builder protocol
- `config/directory_rules.yaml` - Configuration
- `docs/REORGANIZATION_COMPLETE.md` - Project reorganization
- `docs/DIRECTORY_AUDIT_2025-11-11.md` - Initial audit

---

## Quick Reference Card

### Common Commands
```bash
# Check health
python scripts/directory_guardian.py --check

# Fix violations
python scripts/directory_guardian.py --fix

# Generate report
python scripts/directory_guardian.py --report

# Enforce (git hook)
python scripts/directory_guardian.py --enforce
```

### Score Thresholds
- **100** = Excellent (perfect)
- **95-99** = Good (acceptable)
- **90-94** = Warning (fix soon)
- **<90** = Critical (fix now)

### Common Violations
1. Misplaced file → Move to src/, scripts/, or tests/
2. TODO comment → Remove, use GitHub issues
3. Debug statement → Remove breakpoint(), pdb
4. Temp file → Delete .bak, .tmp files
5. Missing __init__.py → Auto-creates
6. Large file → Refactor into smaller modules

### Exempt Directories
- venv/
- .git/
- __pycache__/
- archive/
- outputs/coverage/htmlcov/

### Emergency Recovery
```bash
# Score dropped, emergency fix
python scripts/directory_guardian.py --check
python scripts/directory_guardian.py --fix --no-safe-mode
python scripts/directory_guardian.py --check
# Verify score ≥ 95 before proceeding
```