# OMNI V4 Project Structure Summary

**Generated**: 2025-11-19
**Purpose**: Quick reference for project organization and cleanup

---

## 📁 Directory Overview

```
omni_v4/
├── src/                    # ✅ CORE - Pipeline source code
├── tests/                  # ✅ CORE - Test suite (40 files)
├── scripts/                # ✅ CORE - Production scripts
├── dashboard/              # ✅ CORE - Main dashboard (with clutter)
├── config/                 # ✅ CORE - Configuration files
├── schema/                 # ✅ CORE - Database schema
├── migrations/             # ✅ CORE - DB migrations
├── data/                   # ✅ CORE - Input CSV files (87 days × 3 restaurants)
├── outputs/                # ⚠️ MIXED - Has test files to clean
├── docs/                   # ✅ CORE - Documentation
├── archive/                # ℹ️ HISTORICAL - Old docs/scripts
└── [ROOT FILES]            # 🔴 MANY INVESTIGATION FILES TO DELETE
```

---

## 🔴 Files to DELETE (~40+ files)

### Root Directory Investigation Scripts (11 files):
All created Nov 17, 2025 during Investigation Modal debugging:

```
investigate_pipeline.py             [!] DELETE
investigate_order_grading.py         [!] DELETE
investigate_order_counts.py         [!] DELETE
compare_v3_v4_time_fields.py        [!] DELETE
extract_v3_exact_logic.py           [!] DELETE
test_v3_v4_with_same_order.py       [!] DELETE
verify_capacity_analysis_counts.py  [!] DELETE
deep_dive_v4data_counts.py          [!] DELETE
diagnose_missing_categories.py      [!] DELETE
test_current_output.py              [!] DELETE
test_ingestion_only.py              [!] DELETE
```

### Root Directory Investigation Outputs (4 files):
```
pipeline_investigation.json         [!] DELETE
order_count_investigation.json      [!] DELETE
order_grading_forensics.json        [!] DELETE
v3_v4_comparison.json               [!] DELETE
```

### Dashboard Test HTML Files (5 files):
All in `dashboard/`, created Nov 17:

```
test_disconnected.html              [!] DELETE
test_databridge.html                [!] DELETE
test_clean_modal.html               [!] DELETE
test_investigation_modal.html       [!] DELETE
debug_investigation_modal.html      [!] DELETE
```

### Dashboard Documentation Files (2 files):
```
dashboard/PHASE1_COMPLETE.md        [!] DELETE
dashboard/SURGICAL_DISCONNECTION_SUMMARY.md  [!] DELETE
```

### Experimental Dashboard Components (3 files):
All in `dashboard/components/` or `dashboard/services/`:

```
InvestigationModal_DISCONNECTED.js  [!] DELETE (experimental)
InvestigationModal_CLEAN.js         [!] DELETE (experimental)
services/InvestigationDataBridge.js [!] DELETE (experimental)
```

### Misplaced Root Files (8 files):
```
dashboard_v4.html                   [!] DELETE or MOVE
dashboard_test.js                   [!] DELETE or MOVE
dashboard_week.js                   [!] DELETE or MOVE
test_auto_clockout_dashboard.js     [!] DELETE or MOVE
test_cogs_dashboard.js              [!] DELETE or MOVE
test_dashboard_data.js              [!] DELETE or MOVE
v4Data_oct.js                       [!] DELETE (outdated)
nul                                 [!] DELETE (Windows artifact)
```

### Duplicate v4Data Files (4 files):
```
outputs/dashboard/v4Data.js         [!] DELETE (44MB - too large)
outputs/dashboard/v4Data_with_patterns.js  [!] DELETE
outputs/dashboard/v4Data_with_trends.js    [!] DELETE
dashboard/data/v4Data_test.js       [!] DELETE (test version)
```

**Total Files to Delete**: ~40 files

---

## ✅ Core Files to KEEP

### Pipeline Source (src/):
```
src/
├── core/                   # Result pattern, errors, patterns
├── infrastructure/         # Logging, config, database clients
├── ingestion/              # CSV loading, validation
├── models/                 # DTOs (LaborDTO, OrderDTO, TimeslotDTO, etc.)
├── orchestration/          # Pipeline context
├── output/                 # V3 data transformer
├── processing/             # Core logic (calculators, categorizers, graders)
└── storage/                # Supabase client, storage stages
```

### Tests (tests/):
```
tests/
├── unit/                   # 30+ unit test files
├── integration/            # 10+ integration test files
├── benchmarks/             # Performance tests
└── fixtures/               # Sample data
```

### Scripts (scripts/):
```
scripts/
├── run_date_range.py                   # ✅ Main pipeline runner
├── generate_dashboard_data.py          # ✅ Dashboard export
├── backfill_to_supabase.py             # ✅ DB backfill
├── export_from_supabase.py             # ✅ DB export
├── wipe_supabase_data.py               # ✅ DB utility
└── utilities/                          # Helper scripts
```

### Dashboard (dashboard/):
```
dashboard/
├── index.html                          # ✅ Main dashboard
├── app.js                              # ✅ App entry point
├── components/
│   ├── InvestigationModal.js           # ✅ ORIGINAL (needs fix)
│   ├── CashFlowModal.js                # ✅ Cash flow modal
│   ├── Header.js, WeekTabs.js, etc.    # ✅ Core components
│   └── [DELETE experimental versions]
├── data/
│   └── v4Data.js                       # ✅ ACTIVE DATA FILE (853KB)
├── engines/                            # ✅ Theme, layout, business engines
├── shared/                             # ✅ Config, utils
├── styles/                             # ✅ CSS
└── [DELETE test HTML files]
```

### Configuration:
```
config/
├── base.yaml                           # ✅ Base config
├── directory_rules.yaml                # ✅ Governance rules
├── restaurants/                        # ✅ Per-restaurant config
│   ├── SDR.yaml
│   ├── T12.yaml
│   └── TK9.yaml
└── environments/                       # ✅ Environment config
    ├── dev.yaml
    └── prod.yaml
```

### Data:
```
data/
├── 2025-08-04/                         # ✅ Sample data (87 days)
│   ├── SDR/
│   ├── T12/
│   └── TK9/
├── ...
└── 2025-10-29/
```

---

## 📊 Statistics

**Current State**:
- Investigation Scripts (root): 11 files [!]
- Investigation Outputs (root): 4 files [!]
- Test HTML Pages (dashboard/): 5 files [!]
- Experimental Components: 3 files [!]
- Duplicate v4Data.js: 4 files [!]
- Misc Root Files: 8 files [!]
- **Total to Delete**: ~40 files

**After Cleanup**:
- Clean root directory (only essentials)
- Clean dashboard/ (no test HTML, no experimental files)
- Single v4Data.js in correct location
- Professional, production-ready structure

---

## 🎯 Key Findings

### 1. v4Data.js - THE CORRECT ONE
**Location**: `dashboard/data/v4Data.js` (853KB)
- ✅ This is what the dashboard uses
- ✅ Contains all 3 categories (Lobby, Drive-Thru, ToGo)
- ✅ Date range: 2025-08-04 to 2025-10-29 (87 days, 13 weeks)
- ✅ 174 category_stats entries (87 days × 2 shifts)

### 2. Investigation Modal Bug
**File**: `dashboard/components/InvestigationModal.js` (49.4KB, Nov 17)
- This is the ACTIVE modal (not _CLEAN or _DISCONNECTED)
- Bug is in this file's JavaScript, not in the data
- Data exists and is correct in v4Data.js

### 3. November 17 = Investigation Day
- 25+ files created/modified on Nov 17
- All investigation scripts, test HTMLs, experimental components
- These were emergency debugging attempts
- Can all be safely deleted

---

## 🚀 Cleanup Plan

### Step 1: Backup (Optional but Recommended)
```bash
# Create backup of investigation files before deletion
mkdir backup_nov17
mv investigate_*.py backup_nov17/
mv diagnose_*.py backup_nov17/
mv test_*.html backup_nov17/
mv *_investigation.json backup_nov17/
# ... etc
```

### Step 2: Delete Investigation Scripts
```bash
# Root directory
rm investigate_*.py
rm diagnose_*.py
rm verify_*.py
rm compare_*.py
rm extract_v3_exact_logic.py
rm deep_dive_*.py
rm test_current_output.py
rm test_ingestion_only.py
rm *_investigation.json
rm *_forensics.json
rm v3_v4_comparison.json
```

### Step 3: Delete Dashboard Test Files
```bash
cd dashboard/
rm test_*.html
rm debug_*.html
rm PHASE1_COMPLETE.md
rm SURGICAL_DISCONNECTION_SUMMARY.md
```

### Step 4: Delete Experimental Components
```bash
cd dashboard/components/
rm InvestigationModal_DISCONNECTED.js
rm InvestigationModal_CLEAN.js
cd ../services/
rm InvestigationDataBridge.js
```

### Step 5: Delete Duplicate v4Data Files
```bash
cd outputs/dashboard/
rm v4Data.js  # 44MB version
rm v4Data_with_*.js
cd ../../dashboard/data/
rm v4Data_test.js
cd ../../
rm v4Data_oct.js
```

### Step 6: Clean Misplaced Files
```bash
rm dashboard_*.html
rm dashboard_*.js
rm test_*.js  # root level test files
rm nul
```

### Step 7: Verify
```bash
# Check what's left in root
ls *.py  # Should only see setup.py
ls *.json  # Should only see package files, not investigation files
ls *.html  # Should be empty

# Check dashboard
cd dashboard/
ls *.html  # Should only see index.html
ls components/*.js | grep -E "_CLEAN|_DISCONNECTED"  # Should be empty
```

---

## ✅ Clean Directory Structure (After Cleanup)

```
omni_v4/
├── src/                    # Core pipeline code
├── tests/                  # Test suite
├── scripts/                # Production scripts only
├── dashboard/              # Clean dashboard (no test files)
│   ├── index.html
│   ├── app.js
│   ├── components/         # Only production components
│   ├── data/
│   │   └── v4Data.js       # Single source of truth
│   └── ...
├── config/                 # Configuration
├── data/                   # Input CSVs
├── outputs/                # Clean outputs (no test files)
├── docs/                   # Documentation
├── PROGRESS.md
├── README.md
├── requirements.txt
└── setup.py
```

---

## 📝 After Cleanup TODO

1. ✅ Delete all ~40 orphaned files
2. 🔧 Fix bug in `InvestigationModal.js` (Drive-Thru/ToGo display)
3. ✅ Run test suite: `pytest tests/ --cov=src`
4. ✅ Update PROGRESS.md with cleanup notes and roadmap
5. ✅ Commit: "Clean up: Remove investigation files from Nov 17 debugging session"

---

**For Complete Details**:
- Full dependency analysis: `DEPENDENCY_ANALYSIS_SUMMARY.md`
- Complete file tree: `project_tree.txt`
- Technical trace: `dependency_analysis.txt`
