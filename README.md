# OMNI V4 - Restaurant Analytics Pipeline

**Version:** 4.0
**Status:** 🟢 Project Reorganization Complete (55% V3 Feature Parity)
**Last Updated:** 2025-12-01

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Entry Points](#entry-points)
- [Development](#development)
- [Directory Governance](#directory-governance)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contact](#contact)

---

## Overview

OMNI V4 is a complete rewrite of the restaurant analytics processing system, fixing critical V3 issues (labor cost 2x inflation bug) while introducing pattern learning, timeslot grading, and accurate cash flow tracking.

### Key Features ✨

- ✅ **Accurate Labor Analytics** - Fixed V3's 2x inflation bug (100% accuracy)
- ✅ **Timeslot Grading** - 64 timeslots/day with performance analysis
- ✅ **Pattern Learning** - Daily labor and timeslot pattern detection
- ✅ **Order Categorization** - Lobby/Drive-Thru/ToGo service mix analysis
- ✅ **Cash Flow Tracking** - Hierarchical cash flow with vendor payouts
- ✅ **Overtime Detection** - Real-time overtime hour tracking
- ✅ **Dashboard Integration** - Real-time analytics dashboard
- 🟡 **Test Coverage** - 100 tests passing, 56% coverage

### V3 Improvements

| Feature | V3 Status | V4 Status |
|---------|-----------|-----------|
| Labor Analytics | ❌ 2x inflation bug | ✅ 100% accurate |
| Processing Speed | ~1600ms/day | ✅ ~1200ms/day (25% faster) |
| Test Coverage | Unknown | ✅ 56% (100 tests) |
| Code Quality | TODO markers | ✅ Zero TODO markers |
| Documentation | Minimal | ✅ Comprehensive (28 KB indexes) |

---

## Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# Clone repository (if needed)
cd C:\Users\Jorge Alexander\omni_v4
```

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Pipeline (Most Common)

```bash
# Process date range for all restaurants
python scripts/run_date_range.py ALL 2025-08-20 2025-08-31 --output batch_results.json --verbose

# Generate dashboard data
python scripts/generate_dashboard_data.py batch_results_aug_2025.json

# Serve dashboard
python scripts/serve_dashboard.py
# Opens http://localhost:8080/index.html
```

### One-Command Workflow

```bash
# Process data and serve dashboard in one command
python scripts/build_and_serve.py --dates 2025-08-20 2025-08-31
```

---

## Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: CSV Files (Toast POS Export)                        │
│  Location: tests/fixtures/sample_data/YYYY-MM-DD/CODE/     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Ingestion                                         │
│  - Load CSVs (Sales, Payroll, Orders)                      │
│  - Validate data (L1: fatal, L2: quality)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Order Categorization                              │
│  - Categorize orders (Lobby/Drive-Thru/ToGo)              │
│  - Calculate service mix percentages                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Timeslot Grading                                  │
│  - Window data into 15-min timeslots (64 per day)         │
│  - Grade each timeslot vs standards                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Processing                                        │
│  - Calculate labor metrics (cost, %, grade)                │
│  - Extract cash flow data                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Pattern Learning                                  │
│  - Learn daily labor patterns                               │
│  - Learn timeslot patterns                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 6: Storage                                           │
│  - Store results (in-memory or Supabase)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: outputs/pipeline_runs/batch_results.json          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DASHBOARD: Transform → Serve → User                        │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

- **Result[T] Pattern** - Functional error handling without exceptions
- **Pipeline Stages** - Modular, testable, resumable processing
- **Dependency Injection** - All dependencies passed through constructors
- **DTOs** - Immutable data transfer objects for type safety
- **YAML Configuration** - Flexible, hierarchical configuration system

---

## Project Structure

```
omni_v4/
├── pipeline/                             # Python backend (clear purpose)
│   ├── cli.py                           # Entry point (main pipeline executor)
│   ├── stages/                          # 7 pipeline stages (elevated to top)
│   │   ├── ingestion_stage.py
│   │   ├── order_categorization_stage.py
│   │   ├── timeslot_grading_stage.py
│   │   ├── processing_stage.py
│   │   ├── pattern_learning_stage.py
│   │   ├── storage_stage.py
│   │   └── supabase_storage_stage.py
│   ├── services/                        # Business logic
│   │   ├── labor_calculator.py
│   │   ├── order_categorizer.py
│   │   ├── timeslot_grader.py
│   │   ├── cash_flow_extractor.py
│   │   ├── shift_splitter.py
│   │   ├── result.py                    # Result[T] monad
│   │   ├── errors.py                    # Custom exceptions
│   │   └── patterns/                    # Pattern learning managers
│   │       ├── daily_labor_manager.py
│   │       ├── timeslot_pattern_manager.py
│   │       └── in_memory_storage.py
│   ├── models/                          # Data Transfer Objects (16 DTOs)
│   │   ├── labor_dto.py
│   │   ├── cash_flow_dto.py
│   │   ├── timeslot_dto.py
│   │   ├── order_dto.py
│   │   └── [12 more DTOs]
│   ├── ingestion/                       # CSV loading & validation
│   │   ├── csv_data_source.py
│   │   ├── data_source.py               # Protocol
│   │   └── data_validator.py            # L1/L2 validation
│   ├── storage/                         # Supabase client + migrations
│   │   ├── supabase_client.py
│   │   └── migrations/                  # SQL schema files
│   ├── infrastructure/                  # Infrastructure layer
│   │   ├── config/                      # YAML configuration loader
│   │   ├── database/                    # Database clients
│   │   └── logging/                     # Structured logging, metrics
│   ├── orchestration/                   # Pipeline orchestration
│   │   └── pipeline/
│   │       ├── context.py               # Shared state
│   │       └── stage.py                 # Stage protocol
│   └── output/                          # Output transformers
│       └── v3_data_transformer.py
│
├── scripts/                              # Utility scripts
│   ├── generate_dashboard_data.py       # ⭐ Data transformer
│   ├── run_single_day.py                # Single-day execution
│   ├── run_pipeline_with_metrics.py     # Performance analysis
│   └── backfill_to_supabase.py          # Database backfill
│
├── tests/                                # Test suite (8.3 MB, 27 test files)
│   ├── unit/                            # 85 unit tests
│   │   ├── core/
│   │   ├── infrastructure/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── orchestration/
│   │   └── processing/
│   ├── integration/                     # 15 integration tests
│   │   ├── test_full_pipeline.py        # End-to-end test
│   │   └── [6 more integration tests]
│   ├── fixtures/                        # Test data
│   │   └── sample_data/                 # 12 days × 3 restaurants
│   └── benchmarks/                      # Performance tests (future)
│
├── dashboard/                            # Analytics dashboard (1 MB)
│   ├── index.html                       # Dashboard entry point
│   ├── app.js                           # Main application
│   ├── components/                      # UI components
│   ├── data/
│   │   └── v4Data.js                    # Generated data (from pipeline)
│   ├── engines/                         # Data processing engines
│   ├── shared/                          # Utilities, config, assets
│   └── styles/                          # CSS styles
│
├── config/                               # Configuration (36 KB)
│   ├── base.yaml                        # Base configuration
│   ├── environments/                    # Environment overrides
│   │   ├── dev.yaml
│   │   └── prod.yaml
│   └── restaurants/                     # Restaurant-specific configs
│       ├── SDR.yaml                     # Sandra's Mexican Cuisine
│       ├── T12.yaml                     # Tink-A-Tako #12
│       └── TK9.yaml                     # Tink-A-Tako #9
│
├── outputs/                              # Generated files (git-ignored)
│   ├── pipeline_runs/                   # batch_results*.json
│   ├── dashboard_exports/               # dashboard_data.js files
│   ├── metrics/                         # Performance metrics
│   ├── test_results/                    # Test outputs
│   ├── coverage/                        # Coverage reports
│   ├── logs/                            # Log files
│   └── checkpoints/                     # Processing checkpoints
│
├── docs/                                 # Documentation (260 KB)
│   ├── README.md                        # Documentation index
│   ├── architecture/                    # Design & architecture
│   ├── analysis/                        # V3/V4 comparisons, audits
│   ├── integration/                     # Integration guides
│   └── guides/                          # User guides (coming soon)
│
├── archive/                              # Historical files
│   ├── daily_logs/                      # WEEK*.md files (10 files)
│   ├── deprecated_scripts/
│   ├── old_docs/
│   └── scripts_temp/                    # Experimental scripts
│
├── data/                                 # Runtime data (git-ignored)
│   ├── input/                           # CSV imports
│   ├── state/                           # Processing state
│   └── logs/                            # Runtime logs
│
├── schema/                               # Data schemas
│
├── PROGRESS.md                          # Development progress tracker
├── README.md                            # This file
├── requirements.txt                     # Python dependencies
├── setup.py                             # Package setup
├── pytest.ini                           # Test configuration
└── dashboard_v4.html                    # Generated dashboard HTML
```

---

## Entry Points

### Daily Operations

| Purpose | Command | Description |
|---------|---------|-------------|
| **Process New Data** | `python -m pipeline.cli ALL 2025-08-20 2025-08-31 --verbose` | Run pipeline for date range |
| **Generate Dashboard** | `python scripts/generate_dashboard_data.py batch_results_aug_2025.json` | Transform results to dashboard format |
| **View Dashboard** | `python -m http.server 8080 -d dashboard` | Serve dashboard on localhost:8080 |

### Development Workflow

| Purpose | Command | Description |
|---------|---------|-------------|
| **Run Tests** | `pytest` | Run all tests |
| **Test Coverage** | `pytest --cov=pipeline --cov-report=html` | Generate coverage report |
| **Single Day** | `python scripts/run_single_day.py SDR 2025-08-20 --verbose` | Test single restaurant/day |
| **With Metrics** | `python scripts/run_pipeline_with_metrics.py SDR 2025-08-20` | Performance analysis |

### Configuration

| Purpose | File | Description |
|---------|------|-------------|
| **Base Config** | `config/base.yaml` | Default settings |
| **Environment** | `config/environments/{env}.yaml` | Environment-specific overrides |
| **Restaurant** | `config/restaurants/{code}.yaml` | Restaurant-specific overrides |

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd omni_v4

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black mypy flake8 pytest-cov
```

### Code Style

```bash
# Format code
black pipeline/ scripts/ tests/

# Type checking
mypy pipeline/

# Linting
flake8 pipeline/ scripts/ tests/
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/ingestion/test_ingestion_stage.py -v

# With coverage
pytest --cov=pipeline --cov-report=html
# View coverage: open outputs/coverage/htmlcov/index.html
```

### Adding New Features

1. **Create DTO** in `pipeline/models/` if needed
2. **Implement Logic** in appropriate module (`pipeline/services/`, `pipeline/stages/`, etc.)
3. **Add Tests** in `tests/unit/` and `tests/integration/`
4. **Update Documentation** in `docs/`
5. **Update Configuration** in `config/base.yaml` if needed

---

## Directory Governance

### Automated Standards Enforcement

OMNI V4 uses the **Directory Guardian System** to automatically maintain directory organization and code quality standards.

**Current Health Score:** 97/100 (Excellent)

### Quick Check

```bash
# Check directory compliance
python scripts/directory_guardian.py --check

# Auto-fix violations
python scripts/directory_guardian.py --fix

# Generate health report
python scripts/directory_guardian.py --report
```

### Mandatory Workflow

**Before starting work:**
```bash
python scripts/directory_guardian.py --check
# Verify score ≥ 95
```

**After making changes:**
```bash
python scripts/directory_guardian.py --check
python scripts/directory_guardian.py --fix  # If violations detected
```

### Directory Standards

- **pipeline/** - Production source code (Python backend)
- **scripts/** - Utility scripts only
- **tests/** - Test suite only
- **dashboard/** - JavaScript frontend
- **docs/** - Documentation only (organized by category)
- **outputs/** - Generated files (never manually edited)
- **config/** - YAML configuration only
- **data/** - Input CSV files

### Code Quality Standards

- ✅ No TODO/FIXME comments (use GitHub issues)
- ✅ No debug statements (breakpoint, pdb, print in pipeline/)
- ✅ No backup files (.bak, .tmp, ~)
- ✅ Files in correct locations
- ✅ Required __init__.py files present
- ✅ Python files <1000 lines (suggests refactoring needed)

### Score Thresholds

| Score | Status | Action Required |
|-------|--------|-----------------|
| **100** | Excellent | Perfect, no violations |
| **95-99** | Good | Minor warnings (acceptable) |
| **90-94** | Warning | Should fix before commit |
| **<90** | Critical | Fix immediately, do not commit |

### Common Violations & Fixes

| Violation | Fix |
|-----------|-----|
| Python file in wrong location | Move to pipeline/, scripts/, or tests/ |
| TODO comment in source | Remove, use GitHub issues |
| Debug statement | Remove breakpoint(), pdb |
| Missing __init__.py | Auto-creates |
| Temp file committed | Auto-deletes |
| File too large | Refactor into smaller modules |

### Complete Documentation

For comprehensive guidance, see:
- **[Directory Governance Guide](docs/DIRECTORY_GOVERNANCE.md)** - Complete system documentation (800+ lines)
- **[Builder Protocol](.claude_instructions)** - Workflow instructions for AI assistants
- **[Configuration](config/directory_rules.yaml)** - Rules configuration

### Health Reports

Generated reports saved to `outputs/health/`:
- `health_report_YYYYMMDD_HHMMSS.json` - Machine-readable format
- `health_report_YYYYMMDD_HHMMSS.md` - Human-readable format

### Integration

The guardian integrates with:
- **Pre-commit hooks** (planned) - Block commits if score < 95
- **Claude Builder** - Enforces standards during AI-assisted development
- **CI/CD** (planned) - Automated checks on push

**Benefits:**
- 🎯 Consistent directory organization
- 🔒 Prevents common mistakes automatically
- 📊 Tracks code quality over time
- 🚀 Easier onboarding for new developers
- 🛡️ Maintains professional standards

---

## Testing

### Test Structure

- **Unit Tests** (85 tests) - Test individual components
  - Located in `tests/unit/`
  - Fast, isolated, no external dependencies
  - 100% passing

- **Integration Tests** (15 tests) - Test pipeline flow
  - Located in `tests/integration/`
  - Test stage interactions
  - Use sample fixture data
  - 100% passing

- **Fixtures** - Real Toast POS data samples
  - Located in `tests/fixtures/sample_data/`
  - 12 days of data (Aug 20-31, Oct 20)
  - 3 restaurants (SDR, T12, TK9)

### Test Coverage

- **Current:** 56% overall
- **Core modules:** 80-98%
- **Infrastructure:** 70-85%
- **Processing:** 85-95%

### Running Specific Tests

```bash
# Test specific stage
pytest tests/unit/processing/stages/test_ingestion_stage.py

# Test with verbose output
pytest tests/unit/ingestion/ -v

# Test with debug output
pytest tests/unit/ingestion/ -v --tb=short

# Test pattern matching
pytest -k "test_csv" -v
```

---

## Documentation

### Quick Links

- **[Architecture Guide](docs/architecture/README.md)** - Design patterns, pipeline stages, DTOs
- **[Analysis & Audits](docs/analysis/README.md)** - V3 vs V4 comparisons, data accuracy
- **[Integration Guide](docs/integration/README.md)** - Dashboard integration, external systems
- **[User Guides](docs/guides/README.md)** - Getting started, configuration (coming soon)
- **[Directory Audit](docs/DIRECTORY_AUDIT_2025-11-11.md)** - Complete codebase audit
- **[Development Progress](PROGRESS.md)** - Detailed implementation tracking

### Key Documents

- **V3 Labor Bug** - [CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md](docs/analysis/CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md)
- **Feature Comparison** - [V3_VS_V4_FEATURE_GAP_ANALYSIS.md](docs/analysis/V3_VS_V4_FEATURE_GAP_ANALYSIS.md)
- **Integration Status** - [V4_DASHBOARD_INTEGRATION_STATUS.md](docs/integration/V4_DASHBOARD_INTEGRATION_STATUS.md)
- **Architecture Decisions** - [ARCHITECTURE_DECISIONS.md](docs/architecture/ARCHITECTURE_DECISIONS.md)

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Import errors** | Ensure `PYTHONPATH` includes omni_v4 root |
| **Missing data** | Check CSV files in `tests/fixtures/sample_data/` |
| **Dashboard blank** | Run `generate_dashboard_data.py` first |
| **Tests failing** | Update test fixtures, check file paths |
| **Port in use** | Use `--port 8081` flag for serve_dashboard.py |

### Performance

- Pipeline processes ~8-12 restaurant-days/second
- Dashboard loads in <2 seconds
- Database queries <50ms (in-memory)

---

## Roadmap

### Week 7-8 (Current)
- ✅ Core pipeline complete (Week 7 Day 4)
- ✅ Cash flow tracking implemented
- ✅ Dashboard integration working
- ⏸️ Supabase integration (Week 8)

### Week 8-9 (Next)
- [ ] Complete Supabase StorageStage
- [ ] Real-time dashboard updates
- [ ] Production deployment
- [ ] Monitoring and alerts

### Post-Launch
- [ ] Full V3 feature parity (60-70%)
- [ ] Financial tracking (COGS, P&L)
- [ ] Advanced employee analytics
- [ ] Forecasting & predictions

---

## Contributing

### Development Standards

1. **All new code requires tests** (unit + integration)
2. **Run formatter:** `black pipeline/ scripts/ tests/`
3. **Check types:** `mypy pipeline/`
4. **Update docs** when adding features
5. **Follow existing patterns** (Result[T], DTOs, stages)

### Pull Request Process

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Run full test suite
5. Format and lint code
6. Submit PR with description

---

## Project Stats

- **Lines of Code:** ~15,000 (excluding tests)
- **Test Files:** 27
- **Test Cases:** 100 (100% passing)
- **Code Coverage:** 56%
- **Documentation:** 28 KB indexes + 100 KB detailed docs
- **Configuration Files:** 6 YAML files
- **Supported Restaurants:** 3 (SDR, T12, TK9)
- **Test Data:** 12 days × 3 restaurants

---

## Contact

- **GitHub Repository:** [https://github.com/JPRanx/omni_v4](https://github.com/JPRanx/omni_v4)
- **Local Path:** `C:\Users\Jorge Alexander\omni_v4\`
- **Related Project:** `restaurant_analytics_v3` (legacy V3 system)
- **Documentation:** [docs/README.md](docs/README.md)
- **Progress Tracking:** [PROGRESS.md](PROGRESS.md)
- **Issues:** Create GitHub issue at repository

---

**Last Updated:** 2025-12-01
**Version:** 4.0
**Status:** 🟢 Project Reorganization Complete (55% V3 Feature Parity)