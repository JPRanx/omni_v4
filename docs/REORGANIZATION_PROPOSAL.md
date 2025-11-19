# OMNI V4 - Professional Reorganization Proposal
**Date:** 2025-11-11
**Goal:** Clean, industry-standard project structure

---

## Current Structure Issues

### 🔴 Critical Problems:

1. **Root-Level Clutter** (18 files!)
   - batch_results.json (3 versions)
   - test_*.json (9 test output files)
   - dashboard_*.js/html (3 dashboard files)
   - Loose data files in root

2. **Mixed Concerns**
   - Backend (src/) and Frontend (dashboard/) in same project
   - No clear separation of pipeline vs. dashboard

3. **Unclear Data Organization**
   - data/input, data/logs, data/state - purpose unclear
   - Test fixtures mixed with production code paths

4. **Documentation Sprawl**
   - 20 MD files in docs/ (good content, needs organization)
   - No clear navigation structure

5. **Archive Confusion**
   - Multiple archive subdirectories for different purposes
   - Not clear what's safe to delete

---

## Current Structure (As-Is)

```
omni_v4/
├── 📄 .coverage                          ❌ Root clutter
├── 📄 .env                               ✅ Keep
├── 📄 .env.example                       ✅ Keep
├── 📁 .git/                              ✅ Keep
├── 📄 .gitignore                         ✅ Keep
├── 📁 .pytest_cache/                     ✅ Keep (auto-generated)
│
├── 📁 archive/                           ⚠️ Unclear purpose
│   ├── docs/                            (Old PROGRESS.md)
│   ├── quickbooks_payroll/              (What is this?)
│   └── scripts_temp/                    (Temporary? Delete?)
│
├── 📄 batch_results.json                 ❌ Should be in outputs/
├── 📄 batch_results_aug_2025.json        ❌ Should be in outputs/
├── 📄 batch_results_aug_2025_enhanced.json ❌ Should be in outputs/
│
├── 📁 config/                            ✅ Good structure
│   ├── base.yaml
│   ├── environments/
│   └── restaurants/
│
├── 📁 dashboard/                         ⚠️ Frontend in backend project
│   ├── components/
│   ├── data/
│   ├── engines/
│   ├── shared/
│   ├── styles/
│   ├── index.html
│   ├── app.js
│   ├── PROGRESS.md
│   └── v4Data.js
│
├── 📄 dashboard_data.js                  ❌ Should be in outputs/
├── 📄 dashboard_v4.html                  ❌ Should be in outputs/
├── 📄 dashboard_v4_with_service_mix.js   ❌ Should be in outputs/
│
├── 📁 data/                              ⚠️ Purpose unclear
│   ├── input/                           (Empty? For what?)
│   ├── logs/                            (Should be outputs/logs)
│   └── state/                           (Checkpoints? Should be outputs/)
│
├── 📁 docs/                              ⚠️ Needs organization
│   ├── ARCHITECTURE_DECISIONS.md
│   ├── CONSOLIDATION_SUMMARY.md
│   ├── CRITICAL_FINDING_*.md
│   ├── V3_*.md (5 files)
│   ├── V4_*.md (4 files)
│   ├── WEEK*_*.md (14 files)           ⬅️ Daily logs, needs archive/
│   └── V4_DASHBOARD_INTEGRATION_STATUS.md
│
├── 📁 htmlcov/                           ❌ Should be in outputs/coverage/
│
├── 📄 nul                                ❌ Empty file, delete
│
├── 📄 PROGRESS.md                        ✅ Keep (main progress tracker)
├── 📄 pytest.ini                         ✅ Keep
├── 📄 README.md                          ✅ Keep
├── 📄 requirements.txt                   ✅ Keep
│
├── 📁 schema/                            ✅ Good (database schemas)
│
├── 📁 scripts/                           ✅ Good structure
│   ├── build_and_serve.py
│   ├── discover_toast_files.py
│   ├── discovery_report.json            ⬅️ Should move to outputs/
│   ├── generate_dashboard.py
│   ├── generate_dashboard_data.py
│   ├── run_date_range.py
│   ├── run_pipeline_with_metrics.py
│   ├── run_single_day.py
│   └── serve_dashboard.py
│
├── 📄 sdr_metrics.json                   ❌ Should be in outputs/metrics/
├── 📄 setup.py                           ✅ Keep
│
├── 📁 src/                               ✅ Good structure (backend code)
│   ├── core/
│   ├── dashboard/
│   ├── infrastructure/
│   ├── ingestion/
│   ├── models/
│   ├── orchestration/
│   ├── pipelines/
│   └── processing/
│
├── 📄 test_cash_flow.json                ❌ Should be in outputs/test_results/
├── 📄 test_cash_flow_complete.json       ❌ Should be in outputs/test_results/
├── 📄 test_cash_flow_final.json          ❌ Should be in outputs/test_results/
├── 📄 test_cash_flow_sdr.json            ❌ Should be in outputs/test_results/
├── 📄 test_cash_flow_with_mgmt.json      ❌ Should be in outputs/test_results/
├── 📄 test_dashboard_data.js             ❌ Should be in outputs/test_results/
├── 📄 test_dashboard_with_cash.js        ❌ Should be in outputs/test_results/
├── 📄 test_overtime_oct.json             ❌ Should be in outputs/test_results/
├── 📄 test_overtime_output.json          ❌ Should be in outputs/test_results/
│
├── 📁 tests/                             ✅ Good structure
│   ├── benchmarks/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
│
├── 📄 timeslot_test_results.json         ❌ Should be in outputs/test_results/
│
├── 📁 venv/                              ✅ Keep (Python virtual environment)
│
└── 📄 week7_day1_results.json            ❌ Should be in outputs/pipeline_runs/
```

**Problems Summary:**
- ❌ 18 files in root that should be organized
- ⚠️ 4 directories with unclear purpose
- ✅ 10 items correctly structured

---

## Proposed Structure (Professional)

```
omni_v4/
│
├── 📁 .github/                           # CI/CD workflows (future)
│   └── workflows/
│
├── 📄 .coverage                          # Auto-generated (add to .gitignore)
├── 📄 .env                               # Environment secrets (gitignored)
├── 📄 .env.example                       # Template for .env
├── 📁 .git/                              # Version control
├── 📄 .gitignore                         # Ignore rules
├── 📁 .pytest_cache/                     # Auto-generated
│
├── 📁 archive/                           # ✨ REORGANIZED: Historical records
│   ├── 📁 daily_logs/                   # ← Move WEEK*_*.md here
│   │   ├── week4_summary.md
│   │   ├── week5_day1_day2_summary.md
│   │   ├── week6_day3_progress.md
│   │   ├── week6_day4_progress.md
│   │   ├── week6_day5_progress.md
│   │   ├── week7_day1_progress.md
│   │   ├── week7_day2_progress.md
│   │   ├── week7_day3_progress.md
│   │   └── week7_day4_progress.md
│   │
│   ├── 📁 old_docs/                     # ← Move archive/docs/ here
│   │   └── old_progress.md
│   │
│   ├── 📁 quickbooks_payroll/           # ← Keep if needed, else delete
│   │
│   └── 📁 deprecated_scripts/           # ← Move archive/scripts_temp/ here
│
├── 📁 config/                            # ✅ UNCHANGED: System configuration
│   ├── base.yaml                        # Base config
│   ├── 📁 environments/                 # Environment-specific
│   │   ├── dev.yaml
│   │   └── prod.yaml
│   └── 📁 restaurants/                  # Restaurant-specific
│       ├── SDR.yaml
│       ├── T12.yaml
│       └── TK9.yaml
│
├── 📁 dashboard/                         # ✨ OPTION A: Keep separate
│   ├── 📁 components/                   # UI components
│   ├── 📁 data/                         # Frontend data files
│   ├── 📁 engines/                      # Theme/Layout/Business engines
│   ├── 📁 shared/                       # Shared frontend utilities
│   ├── 📁 styles/                       # CSS/Styling
│   ├── index.html                       # Main entry point
│   ├── app.js                           # Main app logic
│   ├── PROGRESS.md                      # Dashboard development log
│   ├── README.md                        # ← ADD: Dashboard-specific docs
│   └── v4Data.js                        # Current data file
│
├── 📁 docs/                              # ✨ REORGANIZED: Documentation
│   ├── README.md                        # ← ADD: Documentation index
│   │
│   ├── 📁 architecture/                 # ← NEW: Architecture docs
│   │   ├── ARCHITECTURE_DECISIONS.md
│   │   └── CONSOLIDATION_SUMMARY.md
│   │
│   ├── 📁 analysis/                     # ← NEW: Analysis reports
│   │   ├── CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md
│   │   ├── V3_DASHBOARD_INTEGRATION_ANALYSIS.md
│   │   ├── V3_VS_V4_FEATURE_GAP_ANALYSIS.md
│   │   ├── V4_DATA_AUDIT_COMPLETE.md
│   │   └── V4_DATA_AUDIT_REPORT.md
│   │
│   ├── 📁 integration/                  # ← NEW: Integration docs
│   │   ├── V4_DASHBOARD_INTEGRATION_COMPLETE.md
│   │   ├── V4_DASHBOARD_INTEGRATION_STATUS.md
│   │   └── V4_DASHBOARD_SOLUTION.md
│   │
│   └── 📁 guides/                       # ← NEW: User guides (future)
│       ├── GETTING_STARTED.md
│       ├── CONFIGURATION_GUIDE.md
│       └── DEPLOYMENT_GUIDE.md
│
├── 📁 outputs/                           # ✨ NEW: All generated outputs
│   ├── 📁 pipeline_runs/                # ← Pipeline execution results
│   │   ├── batch_results.json
│   │   ├── batch_results_aug_2025.json
│   │   ├── batch_results_aug_2025_enhanced.json
│   │   └── week7_day1_results.json
│   │
│   ├── 📁 dashboard_exports/            # ← Dashboard data exports
│   │   ├── dashboard_data.js
│   │   ├── dashboard_v4.html
│   │   └── dashboard_v4_with_service_mix.js
│   │
│   ├── 📁 metrics/                      # ← Metrics and analytics
│   │   ├── sdr_metrics.json
│   │   └── timeslot_test_results.json
│   │
│   ├── 📁 test_results/                 # ← Test outputs
│   │   ├── test_cash_flow.json
│   │   ├── test_cash_flow_complete.json
│   │   ├── test_cash_flow_final.json
│   │   ├── test_cash_flow_sdr.json
│   │   ├── test_cash_flow_with_mgmt.json
│   │   ├── test_dashboard_data.js
│   │   ├── test_dashboard_with_cash.js
│   │   ├── test_overtime_oct.json
│   │   └── test_overtime_output.json
│   │
│   ├── 📁 coverage/                     # ← Code coverage reports
│   │   └── htmlcov/
│   │
│   ├── 📁 logs/                         # ← Application logs
│   │
│   ├── 📁 checkpoints/                  # ← Pipeline checkpoints
│   │
│   └── .gitkeep                         # Keep empty dir in git
│
├── 📄 PROGRESS.md                        # ✅ UNCHANGED: Main progress tracker
├── 📄 pytest.ini                         # ✅ UNCHANGED: Pytest config
├── 📄 README.md                          # ✅ UNCHANGED: Project overview
├── 📄 requirements.txt                   # ✅ UNCHANGED: Python dependencies
│
├── 📁 schema/                            # ✅ UNCHANGED: Database schemas
│
├── 📁 scripts/                           # ✅ MOSTLY UNCHANGED: Operational scripts
│   ├── build_and_serve.py
│   ├── generate_dashboard.py
│   ├── generate_dashboard_data.py
│   ├── run_date_range.py
│   ├── run_pipeline_with_metrics.py
│   ├── run_single_day.py
│   ├── serve_dashboard.py
│   │
│   ├── 📁 utilities/                    # ← NEW: Helper scripts
│   │   ├── discover_toast_files.py    # ← Move here
│   │   └── discovery_report.json      # ← Or move to outputs/
│   │
│   └── README.md                        # ← ADD: Scripts documentation
│
├── 📄 setup.py                           # ✅ UNCHANGED: Package setup
│
├── 📁 src/                               # ✅ UNCHANGED: Source code (backend)
│   ├── 📁 core/                         # Core business logic
│   │   ├── grading/
│   │   ├── models/
│   │   ├── patterns/
│   │   ├── errors.py
│   │   └── result.py
│   │
│   ├── 📁 dashboard/                    # Dashboard generation logic
│   │   └── templates/
│   │
│   ├── 📁 infrastructure/               # Infrastructure concerns
│   │   ├── config/
│   │   ├── database/
│   │   ├── logging/
│   │   ├── observability/
│   │   └── storage/
│   │
│   ├── 📁 ingestion/                    # Data ingestion
│   ├── 📁 models/                       # Data models (DTOs)
│   ├── 📁 orchestration/                # Pipeline orchestration
│   ├── 📁 pipelines/                    # Pipeline implementations
│   │   ├── ingestion/
│   │   ├── processing/
│   │   └── storage/
│   │
│   └── 📁 processing/                   # Data processing
│       └── stages/
│
├── 📁 tests/                             # ✅ UNCHANGED: Test suite
│   ├── 📁 benchmarks/
│   ├── 📁 fixtures/
│   │   └── sample_data/
│   ├── 📁 integration/
│   └── 📁 unit/
│
└── 📁 venv/                              # ✅ UNCHANGED: Python virtual env
```

---

## Key Changes Summary

### 1. Cleaned Root Directory ✨
**Before:** 18 loose files in root
**After:** 8 config/documentation files only

**Moved:**
- 18 output/test files → `outputs/` (organized by type)
- HTML coverage → `outputs/coverage/`
- Deleted `nul` (empty file)

### 2. Organized Documentation 📚
**Before:** 20 MD files flat in docs/
**After:** 4 subdirectories with clear purpose

**Structure:**
```
docs/
├── architecture/    (2 files: design decisions)
├── analysis/        (5 files: V3/V4 comparisons)
├── integration/     (3 files: dashboard integration)
└── guides/          (future: user documentation)
```

### 3. Created `outputs/` Directory 🎯
**Purpose:** All generated/temporary files in one place

**Benefits:**
- Easy to add `outputs/` to .gitignore
- Clear separation: source code vs. generated artifacts
- Easy cleanup: delete outputs/ to start fresh
- Organized by purpose (runs, exports, tests, metrics)

### 4. Archived Daily Logs 📦
**Before:** 14 WEEK*_*.md files in docs/
**After:** Moved to `archive/daily_logs/`

**Reasoning:**
- Historical value, but not frequently accessed
- Cluttered main docs/ directory
- Still searchable if needed

### 5. Dashboard Decision Point 🤔
**Two options proposed (see below)**

---

## Dashboard Organization: Two Options

### Option A: Keep Dashboard in V4 Project (Recommended)

**Current structure maintained:**
```
omni_v4/
├── dashboard/          # Frontend
└── src/               # Backend
```

**Pros:**
- ✅ Single repository (easier git management)
- ✅ Atomic deployments (backend + frontend together)
- ✅ Shared version control
- ✅ Easier CI/CD setup

**Cons:**
- ⚠️ Mixed concerns (Python + JavaScript in same repo)
- ⚠️ Larger repository size

**When to use:** Monorepo approach, tight coupling between backend/frontend

---

### Option B: Separate Dashboard into Own Project

**Create new project:**
```
C:\Users\Jorge Alexander\
├── omni_v4\               # Backend only
└── omni_v4_dashboard\     # Frontend only
```

**Pros:**
- ✅ Clear separation of concerns
- ✅ Independent deployment cycles
- ✅ Cleaner technology boundaries
- ✅ Easier for frontend-only developers

**Cons:**
- ⚠️ Two repositories to manage
- ⚠️ More complex deployment
- ⚠️ Version sync required

**When to use:** Microservices approach, different teams for backend/frontend

---

### Recommendation: **Option A (Keep Together)**

**Reasoning:**
1. V4 is still in development (Week 7 of 8)
2. Backend and dashboard are tightly coupled
3. Dashboard data format depends on backend DTOs
4. Single developer/team currently
5. Easier to maintain consistency

**Later migration path:** If needed, can extract dashboard to separate project after V4 stabilizes

---

## Migration Plan

### Phase 1: Create New Structure (30 minutes)

```bash
cd C:\Users\Jorge Alexander\omni_v4

# 1. Create new directories
mkdir -p outputs/{pipeline_runs,dashboard_exports,metrics,test_results,coverage,logs,checkpoints}
mkdir -p docs/{architecture,analysis,integration,guides}
mkdir -p archive/{daily_logs,old_docs,deprecated_scripts}
mkdir -p scripts/utilities

# 2. Move daily logs to archive
mv docs/WEEK*.md archive/daily_logs/

# 3. Move old progress to archive
mv archive/docs/* archive/old_docs/
mv archive/scripts_temp/* archive/deprecated_scripts/ 2>/dev/null || true

# 4. Move organized docs to subdirectories
mv docs/ARCHITECTURE_DECISIONS.md docs/architecture/
mv docs/CONSOLIDATION_SUMMARY.md docs/architecture/
mv docs/CRITICAL_FINDING*.md docs/analysis/
mv docs/V3_*.md docs/analysis/
mv docs/V4_DATA_*.md docs/analysis/
mv docs/V4_DASHBOARD*.md docs/integration/

# 5. Move output files to organized locations
mv batch_results*.json outputs/pipeline_runs/
mv week7_day1_results.json outputs/pipeline_runs/
mv dashboard_data.js dashboard_v4* outputs/dashboard_exports/
mv sdr_metrics.json timeslot_test_results.json outputs/metrics/
mv test_*.json test_*.js outputs/test_results/
mv htmlcov outputs/coverage/

# 6. Move discovery report to utilities
mv scripts/discovery_report.json scripts/utilities/
mv scripts/discover_toast_files.py scripts/utilities/

# 7. Delete empty file
rm nul

# 8. Create README files for new directories
touch docs/README.md scripts/README.md outputs/.gitkeep
```

### Phase 2: Update References (1 hour)

**Files to update:**

1. **scripts/generate_dashboard_data.py**
   - Update output path references
   - Change: `./dashboard_data.js` → `./outputs/dashboard_exports/dashboard_data.js`

2. **scripts/run_date_range.py**
   - Update batch_results output path
   - Change: `./batch_results.json` → `./outputs/pipeline_runs/batch_results.json`

3. **.gitignore**
   - Add: `outputs/` (except .gitkeep files)
   - Add: `.coverage`
   - Keep: `.env`, `venv/`, `__pycache__/`, `.pytest_cache/`

4. **PROGRESS.md**
   - Update: Reference to docs organization
   - Add: Note about outputs/ directory

5. **README.md**
   - Update: Directory structure diagram
   - Add: Quick start commands with new paths

### Phase 3: Create Documentation Index (30 minutes)

**Create docs/README.md:**
```markdown
# OMNI V4 Documentation

## Quick Navigation

### Architecture
- [Architecture Decisions](architecture/ARCHITECTURE_DECISIONS.md)
- [Consolidation Summary](architecture/CONSOLIDATION_SUMMARY.md)

### Analysis & Audits
- [V3 vs V4 Feature Gap](analysis/V3_VS_V4_FEATURE_GAP_ANALYSIS.md)
- [V3 Labor Discrepancy](analysis/CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md)
- [V4 Data Audit](analysis/V4_DATA_AUDIT_COMPLETE.md)
- [... more](analysis/)

### Integration
- [Dashboard Integration Status](integration/V4_DASHBOARD_INTEGRATION_STATUS.md)
- [Dashboard Solution](integration/V4_DASHBOARD_SOLUTION.md)
- [... more](integration/)

### Daily Progress Logs
See [archive/daily_logs/](../archive/daily_logs/) for historical development logs.
```

**Create scripts/README.md:**
```markdown
# OMNI V4 Scripts

## Pipeline Execution
- `run_single_day.py` - Process a single restaurant-date
- `run_date_range.py` - Batch process multiple days
- `run_pipeline_with_metrics.py` - Run with performance metrics

## Dashboard Generation
- `generate_dashboard_data.py` - Transform pipeline output to dashboard format
- `generate_dashboard.py` - Generate full dashboard
- `serve_dashboard.py` - Start local HTTP server
- `build_and_serve.py` - One-command build + serve

## Utilities
- `utilities/discover_toast_files.py` - Analyze Toast CSV structure
```

### Phase 4: Update .gitignore (5 minutes)

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Outputs (generated files)
outputs/
!outputs/.gitkeep

# OS
.DS_Store
Thumbs.db
nul

# Build
build/
dist/
*.egg-info/

# Logs
*.log
```

### Phase 5: Test & Verify (30 minutes)

```bash
# 1. Verify directory structure
tree -L 2 -I 'venv|__pycache__|.git|node_modules'

# 2. Test pipeline with new paths
python scripts/run_single_day.py --restaurant SDR --date 2025-08-20

# 3. Verify outputs go to correct location
ls -la outputs/pipeline_runs/

# 4. Test dashboard generation
python scripts/generate_dashboard_data.py outputs/pipeline_runs/batch_results.json

# 5. Verify dashboard export location
ls -la outputs/dashboard_exports/

# 6. Test dashboard serving
python scripts/serve_dashboard.py

# 7. Run tests to ensure nothing broke
pytest
```

---

## Benefits of Reorganization

### 1. Professional Appearance 🎯
- Clean root directory (industry standard)
- Clear separation of concerns
- Easy to navigate for new developers

### 2. Better Git Hygiene 🔧
- `outputs/` can be gitignored
- Only source code and docs in version control
- Smaller repository size

### 3. Easier Cleanup 🧹
- Delete `outputs/` to clear all generated files
- Archive old logs without cluttering main docs
- Clear what's safe to delete

### 4. Improved Documentation 📚
- Organized by purpose (architecture/analysis/integration)
- Easy to find relevant docs
- Clear navigation with index files

### 5. Scalability 📈
- Room for growth (guides/, utilities/)
- Clear patterns for adding new files
- Maintainable long-term

---

## Risks & Mitigation

### Risk 1: Breaking Path References
**Impact:** Scripts may fail if paths hardcoded
**Mitigation:**
- Update all scripts in Phase 2
- Test thoroughly in Phase 5
- Use relative paths from project root

### Risk 2: Lost Work
**Impact:** Files accidentally deleted during move
**Mitigation:**
- Use `mv` not `rm` (files moved, not deleted)
- Test with `--dry-run` flag where possible
- Commit current state before starting

### Risk 3: Git History Confusion
**Impact:** Git blame may be harder to trace
**Mitigation:**
- Use `git mv` instead of `mv` for tracked files
- Document reorganization in commit message
- Keep archive/ for historical reference

### Risk 4: Dashboard Serving Breaks
**Impact:** Dashboard can't find data files
**Mitigation:**
- Update serve_dashboard.py paths
- Test serving immediately after reorganization
- Keep old v4Data.js until confirmed working

---

## Rollback Plan

If reorganization causes issues:

```bash
# 1. Stash changes
git stash

# 2. Or revert commit
git revert HEAD

# 3. Or restore specific files
git checkout HEAD -- scripts/generate_dashboard_data.py

# 4. Or restore entire directory
git checkout HEAD -- .
```

**Prevention:** Commit before starting, test incrementally

---

## Post-Reorganization TODO

### Immediate (Day 1):
- [ ] Update PROGRESS.md with new structure
- [ ] Update README.md with new directory tree
- [ ] Test all scripts end-to-end
- [ ] Verify dashboard still works

### Short-term (Week 8):
- [ ] Create docs/guides/GETTING_STARTED.md
- [ ] Create docs/guides/CONFIGURATION_GUIDE.md
- [ ] Create docs/guides/DEPLOYMENT_GUIDE.md
- [ ] Add outputs/ samples to .gitignore exceptions (for docs)

### Long-term (Post-launch):
- [ ] Consider Option B (separate dashboard project) if needed
- [ ] Set up CI/CD with new structure
- [ ] Archive more old daily logs as they become stale
- [ ] Create automated cleanup scripts for outputs/

---

## Approval Checklist

Before executing reorganization:

- [ ] **Jorge reviews proposal** - Confirm approach
- [ ] **Backup current state** - Commit or zip entire project
- [ ] **Test scripts updated** - Phase 2 complete
- [ ] **Dry-run commands** - Verify mv commands work
- [ ] **Set aside 2-3 hours** - For execution + testing
- [ ] **No active development** - Avoid conflicts with other work

---

## Conclusion

**Recommended Approach:** Execute full reorganization (Option A)

**Timeline:**
- Planning: 1 hour (this document)
- Execution: 2.5 hours (Phases 1-5)
- **Total: 3.5 hours one-time investment**

**Long-term benefit:** Professional, maintainable structure for years to come

**Alternative:** If too risky during Week 7, defer to Week 9 (post-launch cleanup)

---

**Status:** ⏸️ Awaiting Approval
**Next Step:** Jorge approval + set execution time
**Risk Level:** 🟡 Medium (path updates required, but reversible)
**Value:** 🟢 High (long-term maintainability)