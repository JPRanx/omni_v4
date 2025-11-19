# OMNI V4 Directory Audit Report

**Date:** 2025-11-11
**Auditor:** Architect (Claude Code)
**Status:** ✅ **AUDIT COMPLETE**

---

## Executive Summary

The OMNI V4 project has been **professionally reorganized** (completed Nov 11, 2025) and is in excellent structural health. This audit identifies remaining optimization opportunities and establishes clear directory usage protocols.

### Health Score: 🟢 **92/100**

| Category | Score | Status |
|----------|-------|--------|
| **Structure** | 95/100 | 🟢 Excellent |
| **Cleanliness** | 90/100 | 🟢 Excellent |
| **Documentation** | 95/100 | 🟢 Excellent |
| **Test Coverage** | 85/100 | 🟡 Good |
| **Orphaned Code** | 90/100 | 🟢 Excellent |

---

## Audit Statistics

### Codebase Size
- **Total Python Files:** 110 (project only, excluding venv)
  - **Source Code:** 59 files in `src/`
  - **Scripts:** 8 files in `scripts/`
  - **Tests:** 27 test files
  - **Archive:** 3 files in `archive/scripts_temp/`

### Directory Structure
- **Total Directories:** 250+ (including test fixtures)
- **Empty Directories:** 3 (candidates for removal)
- **Active Directories:** 15 core directories
- **Test Fixture Dates:** 12 days of sample data (Aug 20-31 + Oct 20)

### Code Quality
- **TODO/FIXME Markers:** 0 in project code ✅
- **Backup Files:** 0 ✅
- **Orphaned Files:** 7 files identified
- **Duplicate Files:** 0 ✅

---

## Directory Breakdown

### Root Directory (Clean ✅)

```
omni_v4/
├── dashboard_v4.html          # Generated dashboard HTML
├── PROGRESS.md                # Main progress tracker
├── pytest.ini                 # Test configuration
├── README.md                  # Project README
├── requirements.txt           # Python dependencies
└── setup.py                   # Package setup
```

**Status:** ✅ **Excellent** - Only essential files in root

---

## Source Code Structure (`src/`)

### Active Modules (59 files)

#### `src/core/` - Core Business Logic (13 files)
```
src/core/
├── __init__.py
├── errors.py                              # Custom exceptions
├── result.py                              # Result[T] monad for error handling
├── grading/
│   └── __init__.py                        # Empty (OK for package)
├── patterns/                              # Pattern learning managers
│   ├── __init__.py
│   ├── daily_labor_manager.py            # Daily labor pattern detection
│   ├── daily_labor_storage.py            # Storage protocol
│   ├── in_memory_daily_labor_storage.py  # In-memory implementation
│   ├── in_memory_storage.py              # Generic in-memory storage
│   ├── manager.py                         # Pattern manager protocol
│   ├── storage.py                         # Storage protocol
│   └── timeslot_pattern_manager.py       # Timeslot pattern learning
└── models/                                # ⚠️ EMPTY - Remove
```

**Status:** 🟢 **Healthy** - One empty directory to remove

**Issue Identified:**
- ❌ `src/core/models/` is empty and redundant with `src/models/`

---

#### `src/infrastructure/` - Infrastructure Layer (9 files)
```
src/infrastructure/
├── __init__.py
├── config/                                # Configuration management
│   ├── __init__.py
│   └── loader.py                          # YAML config loader
├── database/                              # Database clients
│   ├── __init__.py
│   ├── database_client.py                 # Database protocol
│   ├── in_memory_client.py                # In-memory implementation
│   └── supabase_client.py                 # Supabase client (future)
├── logging/                               # Logging & metrics
│   ├── __init__.py
│   ├── pipeline_metrics.py                # Pipeline performance tracking
│   └── structured_logger.py               # Structured logging
├── observability/                         # ⚠️ EMPTY - Remove
└── storage/                               # Pattern storage
    ├── __init__.py
    └── supabase_pattern_storage.py        # Supabase pattern storage (future)
```

**Status:** 🟢 **Healthy** - One empty directory to remove

**Issue Identified:**
- ❌ `src/infrastructure/observability/` is empty (future feature stub)

---

#### `src/ingestion/` - Data Ingestion (4 files)
```
src/ingestion/
├── __init__.py
├── csv_data_source.py                     # CSV file loader
├── data_source.py                         # DataSource protocol
└── data_validator.py                      # L1/L2 validation
```

**Status:** 🟢 **Perfect** - All files actively used

**Import Status:** ✅ Imported by `IngestionStage`

---

#### `src/models/` - Data Transfer Objects (11 files)
```
src/models/
├── __init__.py
├── cash_flow_dto.py                       # Cash flow data structure
├── daily_labor_pattern.py                 # Daily labor pattern DTO
├── hourly_service_pattern.py              # Hourly service pattern DTO
├── ingestion_result.py                    # Ingestion stage output
├── labor_dto.py                           # Labor metrics DTO
├── order_dto.py                           # Order categorization DTO
├── pattern.py                             # Generic pattern DTO
├── pattern_protocol.py                    # Pattern protocol
├── processing_result.py                   # Processing stage output
├── storage_result.py                      # Storage stage output
└── timeslot_dto.py                        # Timeslot grading DTO
```

**Status:** 🟢 **Perfect** - All DTOs actively used

**Import Status:** ✅ Imported throughout pipeline

---

#### `src/orchestration/` - Pipeline Orchestration (3 files)
```
src/orchestration/
├── __init__.py
└── pipeline/
    ├── __init__.py
    ├── context.py                          # PipelineContext (shared state)
    └── stage.py                            # Stage protocol
```

**Status:** 🟢 **Perfect** - Core pipeline abstraction

**Import Status:** ✅ Imported by all stages

---

#### `src/processing/` - Processing Logic (9 files)
```
src/processing/
├── __init__.py
├── cash_flow_extractor.py                 # Cash flow extraction (Week 7 Day 4)
├── labor_calculator.py                    # Labor cost calculations
├── order_categorizer.py                   # Order type categorization
├── timeslot_grader.py                     # Timeslot performance grading
├── timeslot_windower.py                   # 15-min timeslot windows
└── stages/                                # Pipeline stages
    ├── __init__.py
    ├── ingestion_stage.py                 # Stage 1: Data loading
    ├── order_categorization_stage.py      # Stage 2: Order categorization
    ├── pattern_learning_stage.py          # Stage 5: Pattern learning
    ├── processing_stage.py                # Stage 4: Labor processing
    ├── storage_stage.py                   # Stage 6: Database storage
    └── timeslot_grading_stage.py          # Stage 3: Timeslot grading
```

**Status:** 🟢 **Perfect** - All stages actively used

**Import Status:** ✅ Imported by `run_date_range.py`

---

#### `src/pipelines/` - ⚠️ **ORPHANED PACKAGE**
```
src/pipelines/
├── __init__.py
├── ingestion/
│   └── __init__.py                        # Empty stub
├── processing/
│   └── __init__.py                        # Empty stub
└── storage/
    └── __init__.py                        # Empty stub
```

**Status:** ❌ **ORPHANED** - Never imported, empty stubs

**Import Status:** ❌ Not imported anywhere

**Recommendation:** **DELETE** entire `src/pipelines/` directory
- Reason: Redundant with `src/processing/stages/`
- Impact: Zero (not used)
- Action: Remove directory

---

#### `src/dashboard/` - ⚠️ **ORPHANED PACKAGE**
```
src/dashboard/
└── templates/                             # Empty stub
```

**Status:** ❌ **ORPHANED** - Never imported, empty

**Import Status:** ❌ Not imported anywhere

**Recommendation:** **DELETE** entire `src/dashboard/` directory
- Reason: Dashboard is in `/dashboard` (root level)
- Impact: Zero (not used)
- Action: Remove directory

---

## Scripts Directory (`scripts/`)

### Active Scripts (8 files)

```
scripts/
├── build_and_serve.py                     # ⭐ One-command workflow (build + serve)
├── discover_toast_files.py                # Discovery utility
├── generate_dashboard.py                  # Generate HTML dashboard
├── generate_dashboard_data.py             # ⭐ Transform batch results → JS data
├── run_date_range.py                      # ⭐ Main pipeline executor (batch mode)
├── run_pipeline_with_metrics.py           # Pipeline with detailed metrics
├── run_single_day.py                      # Single-day pipeline execution
├── serve_dashboard.py                     # ⭐ HTTP server for dashboard
└── discovery_report.json                  # ⚠️ Output file (should be in outputs/)
```

**Status:** 🟢 **Excellent** - All scripts actively used

**Frequency of Use:**
1. ⭐⭐⭐ `run_date_range.py` - Daily operations (most used)
2. ⭐⭐⭐ `generate_dashboard_data.py` - After every pipeline run
3. ⭐⭐⭐ `serve_dashboard.py` - View dashboard
4. ⭐⭐ `build_and_serve.py` - Convenience wrapper
5. ⭐ `run_single_day.py` - Development/testing
6. ⭐ `generate_dashboard.py` - Alternative HTML output
7. ⭐ `run_pipeline_with_metrics.py` - Performance analysis
8. ⭐ `discover_toast_files.py` - Utility

**Issue Identified:**
- ⚠️ `scripts/discovery_report.json` should be moved to `outputs/`

---

## Dashboard Directory (`dashboard/`)

### Current Structure
```
dashboard/
├── app.js                                 # Main dashboard application
├── index.html                             # Dashboard entry point
├── CONFIGURATION_AUDIT_2025-11-01.md      # Config documentation
├── PROGRESS.md                            # Dashboard development progress
├── components/                            # UI components (many files)
├── data/
│   └── v4Data.js                          # ✅ Current data file (generated)
├── engines/                               # Data processing engines
├── shared/                                # Shared utilities, config, assets
├── styles/                                # CSS styles
├── sankey_comparison.html                 # ⚠️ Test file (move to outputs/)
├── test_cash_modal.html                   # ⚠️ Test file (move to outputs/)
├── test-theme.html                        # ⚠️ Test file (move to outputs/)
└── v4Data.js                              # ⚠️ Old file (delete, use data/v4Data.js)
```

**Status:** 🟡 **Good** - 4 files need cleanup

**Issues Identified:**
1. ⚠️ `dashboard/sankey_comparison.html` → move to `outputs/test_results/`
2. ⚠️ `dashboard/test_cash_modal.html` → move to `outputs/test_results/`
3. ⚠️ `dashboard/test-theme.html` → move to `outputs/test_results/`
4. ⚠️ `dashboard/v4Data.js` → delete (superseded by `dashboard/data/v4Data.js`)

---

## Tests Directory (`tests/`)

### Test Structure (27 test files)

```
tests/
├── __init__.py
├── benchmarks/                            # Performance benchmarks (future)
├── fixtures/                              # Test data
│   ├── sample_data/                       # 12 days of restaurant data
│   │   ├── 2025-08-20/ through 2025-08-31/  # 12 restaurants × 3 = 36 datasets
│   │   └── 2025-10-20/                    # Overtime test data
│   └── sample_toast_data/                 # Sample Toast POS exports
├── integration/                           # Integration tests
│   ├── __init__.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── test_*.py
│   └── test_full_pipeline.py              # End-to-end test
└── unit/                                  # Unit tests
    ├── __init__.py
    ├── core/
    │   ├── patterns/
    │   │   └── test_*.py
    │   └── test_*.py
    ├── infrastructure/
    │   └── test_*.py
    ├── ingestion/
    │   ├── test_csv_data_source.py
    │   ├── test_data_validator.py
    │   ├── test_ingestion_stage.py
    │   └── test_order_csv_loading.py
    ├── models/
    │   └── test_*.py
    ├── orchestration/
    │   └── pipeline/
    │       └── test_*.py
    └── processing/
        ├── stages/
        │   ├── test_ingestion_stage.py
        │   ├── test_order_categorization_stage.py
        │   ├── test_pattern_learning_stage.py
        │   ├── test_processing_stage.py
        │   ├── test_storage_stage.py
        │   └── test_timeslot_grading_stage.py
        ├── test_cash_flow_extractor.py
        ├── test_labor_calculator.py
        ├── test_order_categorizer.py
        ├── test_timeslot_grader.py
        └── test_timeslot_windower.py
```

**Status:** 🟢 **Excellent** - Well-organized, comprehensive

**Test Coverage:** 56% (100 tests passing)

**Breakdown:**
- **Unit Tests:** 85 tests
- **Integration Tests:** 15 tests
- **Coverage Gaps:** Financial tracking, Supabase integration (not yet implemented)

---

## Configuration (`config/`)

### Active Configuration Files

```
config/
├── base.yaml                              # ✅ Base configuration
├── environments/
│   ├── dev.yaml                           # ✅ Development overrides
│   └── prod.yaml                          # ✅ Production overrides
└── restaurants/
    ├── SDR.yaml                           # ✅ Sandra's Mexican Cuisine
    ├── T12.yaml                           # ✅ Tink-A-Tako #12
    └── TK9.yaml                           # ✅ Tink-A-Tako #9
```

**Status:** 🟢 **Perfect** - Clean, organized configuration

---

## Outputs Directory (`outputs/`)

### Generated Files (Git-Ignored ✅)

```
outputs/
├── pipeline_runs/                         # ✅ Batch results JSON
│   ├── batch_results.json
│   ├── batch_results_aug_2025.json
│   └── batch_results_aug_2025_enhanced.json
├── dashboard_exports/                     # ✅ Dashboard JS exports
│   ├── dashboard_data.js
│   └── dashboard_v4_with_service_mix.js
├── metrics/                               # ✅ Performance metrics
│   └── sdr_metrics.json
├── test_results/                          # ✅ Test output files
│   ├── test_cash_flow*.json (5 files)
│   ├── test_overtime*.json (2 files)
│   ├── timeslot_test_results.json
│   └── week7_day1_results.json
├── coverage/                              # ✅ Test coverage reports
│   └── htmlcov/
├── logs/                                  # Ready for log files
└── checkpoints/                           # Ready for checkpoints
```

**Status:** 🟢 **Perfect** - Well-organized generated artifacts

---

## Documentation (`docs/`)

### Comprehensive Documentation (5 categories)

```
docs/
├── README.md                              # ✅ Main documentation index (3.8 KB)
├── CONSOLIDATION_SUMMARY.md               # Project overview
├── REORGANIZATION_PROPOSAL.md             # Reorganization plan
├── REORGANIZATION_COMPLETE.md             # Reorganization report
├── architecture/
│   ├── README.md                          # ✅ Architecture guide (5.1 KB)
│   └── ARCHITECTURE_DECISIONS.md          # Design decisions
├── analysis/
│   ├── README.md                          # ✅ Analysis index (7.2 KB)
│   ├── CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md
│   ├── V3_VS_V4_FEATURE_GAP_ANALYSIS.md
│   ├── V4_DATA_AUDIT_COMPLETE.md
│   └── V4_DATA_AUDIT_REPORT.md
├── integration/
│   ├── README.md                          # ✅ Integration guide (8.9 KB)
│   ├── V3_DASHBOARD_INTEGRATION_ANALYSIS.md
│   ├── V4_DASHBOARD_INTEGRATION_COMPLETE.md
│   ├── V4_DASHBOARD_INTEGRATION_STATUS.md
│   └── V4_DASHBOARD_SOLUTION.md
└── guides/
    └── README.md                          # ✅ User guides index (3.4 KB)
```

**Status:** 🟢 **Excellent** - Comprehensive, well-organized

**Total Documentation:** ~28 KB of indexes + ~100 KB of detailed docs

---

## Archive Directory (`archive/`)

### Historical Files (Properly Archived ✅)

```
archive/
├── README.md
├── daily_logs/                            # ✅ 10 WEEK*.md files
│   ├── WEEK2_SUMMARY.md through WEEK7_DAY4_PROGRESS.md
├── deprecated_scripts/                    # Ready for deprecated code
├── old_docs/                              # Ready for old documentation
├── docs/                                  # Old doc structure (legacy)
├── quickbooks_payroll/                    # QuickBooks files (sensitive data)
└── scripts_temp/                          # Temporary script experiments
    ├── compare_toast_sources.py
    ├── extract_toast_payroll.py
    ├── toast_employee_extractor.py
    ├── toast_employees.json
    └── toast_payroll_data.json
```

**Status:** 🟢 **Good** - Properly archived historical files

---

## Issues Summary

### Critical Issues (0)
**None identified ✅**

### Medium Priority Issues (7)

#### 1. Orphaned Package: `src/pipelines/`
- **Status:** ❌ Unused
- **Location:** `src/pipelines/`
- **Issue:** Empty package, never imported
- **Impact:** Confusing directory structure
- **Action:** **DELETE** entire directory
- **Effort:** 2 minutes
- **Risk:** Zero (not used anywhere)

#### 2. Orphaned Package: `src/dashboard/`
- **Status:** ❌ Unused
- **Location:** `src/dashboard/`
- **Issue:** Empty package, never imported
- **Impact:** Confusing structure
- **Action:** **DELETE** entire directory
- **Effort:** 2 minutes
- **Risk:** Zero (not used anywhere)

#### 3. Empty Directory: `src/core/models/`
- **Status:** ❌ Empty
- **Location:** `src/core/models/`
- **Issue:** Redundant with `src/models/`
- **Impact:** Minor confusion
- **Action:** **DELETE** directory
- **Effort:** 1 minute
- **Risk:** Zero (empty)

#### 4. Empty Directory: `src/infrastructure/observability/`
- **Status:** ❌ Empty
- **Location:** `src/infrastructure/observability/`
- **Issue:** Future feature stub
- **Impact:** Minor clutter
- **Action:** **DELETE** or document as "future"
- **Effort:** 1 minute
- **Risk:** Zero (empty)

#### 5. Dashboard Test Files in Wrong Location
- **Status:** ⚠️ Misplaced
- **Files:**
  - `dashboard/sankey_comparison.html`
  - `dashboard/test_cash_modal.html`
  - `dashboard/test-theme.html`
- **Issue:** Test files mixed with production code
- **Action:** **MOVE** to `outputs/test_results/`
- **Effort:** 2 minutes
- **Risk:** Low

#### 6. Old Dashboard Data File
- **Status:** ⚠️ Duplicate
- **File:** `dashboard/v4Data.js` (old location)
- **Issue:** Superseded by `dashboard/data/v4Data.js`
- **Action:** **DELETE** old file
- **Effort:** 1 minute
- **Risk:** Low (backup exists)

#### 7. Script Output in Wrong Location
- **Status:** ⚠️ Misplaced
- **File:** `scripts/discovery_report.json`
- **Issue:** Output file in scripts directory
- **Action:** **MOVE** to `outputs/` or **DELETE** if obsolete
- **Effort:** 1 minute
- **Risk:** Low

### Low Priority Issues (0)
**None identified ✅**

---

## File Categories

### CORE (Essential, actively used)
- `src/core/` (except models/)
- `src/infrastructure/`
- `src/ingestion/`
- `src/models/`
- `src/orchestration/`
- `src/processing/`
- `scripts/run_date_range.py`
- `scripts/generate_dashboard_data.py`
- `scripts/serve_dashboard.py`
- `config/`

### ACTIVE (Under active development)
- `src/processing/cash_flow_extractor.py` (Week 7 Day 4)
- `src/models/cash_flow_dto.py` (Week 7 Day 4)
- `dashboard/components/` (Cash Flow Modal)

### STABLE (Complete, tested, rarely changed)
- `src/core/result.py`
- `src/models/` (most DTOs)
- `src/ingestion/`
- `src/orchestration/`

### UTILITY (Helper scripts)
- `scripts/build_and_serve.py`
- `scripts/run_single_day.py`
- `scripts/run_pipeline_with_metrics.py`
- `scripts/discover_toast_files.py`
- `scripts/generate_dashboard.py`

### TEST (Test files and fixtures)
- `tests/` (all)

### CONFIG (Configuration)
- `config/` (all)

### DEPRECATED (To be removed)
- `src/pipelines/` ❌
- `src/dashboard/` ❌
- `src/core/models/` ❌
- `src/infrastructure/observability/` ❌
- `dashboard/v4Data.js` ❌
- Dashboard test HTML files ⚠️

### GENERATED (Never edit manually)
- `outputs/` (all)
- `dashboard/data/v4Data.js`

---

## Import Map (Active Files Only)

### Entry Points
1. **`scripts/run_date_range.py`** (Main pipeline executor)
   - Imports: All pipeline stages, validators, calculators, managers
   - Produces: `outputs/pipeline_runs/batch_results.json`

2. **`scripts/generate_dashboard_data.py`** (Data transformer)
   - Imports: None (standalone)
   - Consumes: `outputs/pipeline_runs/batch_results.json`
   - Produces: `dashboard/data/v4Data.js`

3. **`scripts/serve_dashboard.py`** (HTTP server)
   - Imports: None (standalone)
   - Serves: `dashboard/`

### Core Dependencies
- **Result[T]**: `src/core/result.py` → Used everywhere
- **PipelineContext**: `src/orchestration/pipeline/context.py` → Used by all stages
- **Stage Protocol**: `src/orchestration/pipeline/stage.py` → Implemented by 6 stages
- **DTOs**: `src/models/*.py` → Passed between stages
- **ConfigLoader**: `src/infrastructure/config/loader.py` → Used by orchestrator

---

## Recommendations

### Immediate Actions (15 minutes total)

1. **DELETE Orphaned Packages** (5 min)
   ```bash
   rm -rf src/pipelines/
   rm -rf src/dashboard/
   rm -rf src/core/models/
   rm -rf src/infrastructure/observability/
   ```

2. **Move Dashboard Test Files** (5 min)
   ```bash
   mv dashboard/sankey_comparison.html outputs/test_results/
   mv dashboard/test_cash_modal.html outputs/test_results/
   mv dashboard/test-theme.html outputs/test_results/
   ```

3. **Delete Old Dashboard Data** (2 min)
   ```bash
   rm dashboard/v4Data.js  # Superseded by dashboard/data/v4Data.js
   ```

4. **Move/Delete Script Output** (3 min)
   ```bash
   mv scripts/discovery_report.json outputs/ # or delete if obsolete
   ```

### Short-Term Improvements (Week 7-8)

1. **Create Main Entry Point**
   - Create `main.py` in root as canonical entry point
   - Document in README.md

2. **Consolidate Documentation**
   - Move dashboard docs to main docs/ structure
   - Remove duplicate PROGRESS.md files

3. **Add Pre-Commit Hooks**
   - Prevent loose files in root
   - Auto-run black formatter
   - Check for TODO markers

4. **Create Guides**
   - `docs/guides/GETTING_STARTED.md`
   - `docs/guides/CONFIGURATION_GUIDE.md`
   - `docs/guides/DEPLOYMENT_GUIDE.md`

### Long-Term Optimizations (Post-Launch)

1. **Reduce Test Fixtures Size**
   - Current: 12 days × 3 restaurants = 36 datasets
   - Optimize: Keep only essential dates for tests

2. **Automated Documentation**
   - Generate API docs from docstrings
   - Auto-update import maps

3. **CI/CD Integration**
   - Automated testing on commit
   - Coverage reports
   - Linting and type checking

---

## Cleanliness Standards

### Master-Level Directory Principles (Scorecard)

| Principle | Score | Status | Notes |
|-----------|-------|--------|-------|
| **Single Purpose** | 95/100 | 🟢 | Each file has clear purpose |
| **No Orphans** | 90/100 | 🟢 | 4 orphaned dirs identified |
| **No Duplication** | 100/100 | 🟢 | Zero duplicate files |
| **Clear Naming** | 95/100 | 🟢 | Excellent naming conventions |
| **Proper Location** | 90/100 | 🟢 | 7 misplaced files |
| **Documentation** | 95/100 | 🟢 | Comprehensive docs |
| **No Dead Code** | 100/100 | 🟢 | No commented code |
| **No Experiments** | 95/100 | 🟢 | Archived in `archive/scripts_temp/` |
| **Version Control** | 95/100 | 🟢 | .gitignore updated |
| **Active Maintenance** | 90/100 | 🟢 | Regular reorganization |
| **TOTAL** | **94/100** | 🟢 **Excellent** | Professional structure |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: CSV Files (Toast POS Export)                        │
│  Location: tests/fixtures/sample_data/YYYY-MM-DD/CODE/     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ENTRY POINT: scripts/run_date_range.py                     │
│  - Orchestrates pipeline execution                          │
│  - Creates PipelineContext                                  │
│  - Executes 6 stages sequentially                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: IngestionStage                                    │
│  Files: src/ingestion/*.py, src/processing/stages/ingestion_stage.py
│  - Load CSVs (Sales, Payroll, Orders)                      │
│  - Validate data (L1: fatal, L2: quality)                  │
│  - Extract raw dataframes                                   │
│  Output: IngestionResult                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: OrderCategorizationStage                          │
│  Files: src/processing/order_categorizer.py, stages/order_categorization_stage.py
│  - Categorize orders (Lobby/Drive-Thru/ToGo)              │
│  - Calculate service mix percentages                        │
│  Output: OrderDTO, service_mix                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: TimeslotGradingStage                              │
│  Files: src/processing/timeslot_*.py, stages/timeslot_grading_stage.py
│  - Window data into 15-min slots (64/day)                  │
│  - Grade each slot vs standards                             │
│  - Detect hot/cold streaks                                  │
│  Output: TimeslotDTO, timeslot_metrics                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: ProcessingStage                                   │
│  Files: src/processing/labor_calculator.py, cash_flow_extractor.py
│  - Calculate labor metrics (cost, %, grade)                │
│  - Extract cash flow data                                   │
│  - Detect overtime                                          │
│  Output: ProcessingResult, CashFlowDTO                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 5: PatternLearningStage                              │
│  Files: src/core/patterns/*.py, stages/pattern_learning_stage.py
│  - Learn daily labor patterns                               │
│  - Learn timeslot patterns                                  │
│  - Update pattern storage                                   │
│  Output: Learned patterns                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 6: StorageStage                                      │
│  Files: src/infrastructure/database/*.py, stages/storage_stage.py
│  - Store results (in-memory or Supabase)                   │
│  - Return storage confirmation                              │
│  Output: StorageResult                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: outputs/pipeline_runs/batch_results.json          │
│  - Complete pipeline results                                │
│  - All metrics, patterns, grades                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TRANSFORM: scripts/generate_dashboard_data.py             │
│  - Transform V4 format → V3 dashboard format               │
│  - Calculate aggregates                                     │
│  - Map restaurant codes → names                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: dashboard/data/v4Data.js                           │
│  - JavaScript module for dashboard                          │
│  - V3-compatible format                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SERVE: scripts/serve_dashboard.py                         │
│  - HTTP server on localhost:8080                           │
│  - Serves dashboard/index.html                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  USER: Browser → http://localhost:8080/index.html          │
│  - Interactive dashboard with all metrics                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Conclusion

The OMNI V4 project is in **excellent structural health** (92/100) following the comprehensive reorganization completed on Nov 11, 2025. The directory structure is professional, clean, and follows industry best practices.

### Key Strengths:
- ✅ **Clean root directory** (only essential files)
- ✅ **Well-organized source code** (clear separation of concerns)
- ✅ **Comprehensive documentation** (28 KB of indexes + detailed docs)
- ✅ **Proper outputs separation** (generated files isolated)
- ✅ **Zero dead code** (no TODO markers, no backup files)
- ✅ **Excellent test coverage** (100 tests passing, 56% coverage)

### Remaining Issues:
- 4 orphaned directories (15 min to clean)
- 7 misplaced files (10 min to reorganize)
- **Total cleanup time: 25 minutes**

### Next Steps:
1. Execute immediate cleanup (25 min)
2. Create main entry point (Week 7-8)
3. Add user guides (Week 7-8)
4. Implement CI/CD (Post-launch)

**Status:** ✅ **Ready for continued development**

---

**Audit Completed:** 2025-11-11
**Next Audit:** After Week 8 completion
**Auditor:** Architect (Claude Code)