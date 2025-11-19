# Archive Folder

This folder contains files that are not part of the active project but are kept for reference.

## Structure

### `quickbooks_payroll/`
QuickBooks payroll Excel files that were used in the initial exploration phase:
- Book77.xlsx
- 12 payroll.xlsx
- SDR payroll.xlsx
- TAT payroll.xlsx
- tk9 ppayroll.xlsx

**Note**: We pivoted away from QuickBooks parsing to use Toast PayrollExport files instead, which are much simpler to work with.

### `docs/`
Documentation files from various phases:
- SYSTEM_ARCHITECTURE.md - Original system design (QB-focused)
- TOAST_PAYROLL_SUMMARY.md - Toast PayrollExport analysis
- QUICK_START.md - Quick start guide
- CONFIG.md - Configuration documentation
- PROGRESS.md - Development progress tracking
- WEEK2_SUMMARY.md - Week 2 summary
- VENV_SETUP.md - Virtual environment setup

### `scripts_temp/`
Temporary scripts created during exploration:
- extract_toast_payroll.py - Extract data from Toast PayrollExport
- compare_toast_sources.py - Compare PayrollExport vs TimeEntries
- toast_employee_extractor.py - Extract employee names from Toast
- toast_employees.json - Extracted employee data
- toast_payroll_data.json - Extracted payroll data

## Why These Were Archived

**QuickBooks files**: We initially tried to parse QuickBooks payroll exports, but they were too complex (wide format, 6-column employee blocks, overtime calculation issues, cash employee detection). We pivoted to using Toast's PayrollExport CSV files instead.

**Temporary scripts**: These were one-off exploration scripts. The actual ingestion pipeline uses proper modules in `src/` instead.

**Documentation**: These docs were created during the exploration phase. Current documentation is in the main README.md and inline code comments.

## What We're Using Instead

- **Toast PayrollExport CSVs**: Located in `tests/fixtures/sample_data/YYYY-MM-DD/RESTAURANT/PayrollExport_YYYY_MM_DD.csv`
- **Ingestion Pipeline**: `src/ingestion/` and `src/processing/`
- **Active Documentation**: Main `README.md` in project root

These archived files are kept for reference but are not part of the active codebase.
