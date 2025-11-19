# Toast PayrollExport Data Summary

## Overview
Successfully pivoted from QuickBooks parsing to using Toast's native PayrollExport files. This approach is much simpler and more reliable.

## Files Cleaned Up
All QuickBooks-related files and employee matching system have been removed:
- `qb_parser.py`, `qb_parser_v2.py`
- `qb_parsed_data.json`, `qb_parsed_data_v2.json`
- `check_qb_files.py`
- `fuzzy_matcher.py`
- `generate_html_interface.py`
- `generate_summary_report.py`
- `matching_script_v2.py`
- `matching_results.json`, `matching_results_v2.json`
- `employee_matching_interface.html`, `employee_matching_interface_v2.html`
- All QB documentation files

## Toast Data Sources Found

### 1. PayrollExport Files (RECOMMENDED)
**Location:** `tests/fixtures/sample_data/2025-10-20/[LOCATION]/PayrollExport_2025_10_20.csv`

**Structure:**
```
Employee,Job Title,Regular Hours,Overtime Hours,Hourly Rate,Regular Pay,Overtime Pay,Total Pay,Net Sales,Declared Tips,Non-Cash Tips,Total Tips,Tips Withheld,Total Gratuity,Employee ID,Job Code,Location,Location Code
```

**Key Fields:**
- `Employee`: Full employee name (e.g., "Aragon, Brianna")
- `Job Title`: Position (e.g., "Host", "Server", "Cook")
- `Regular Hours`: Regular hours worked (decimal)
- `Overtime Hours`: OT hours worked (decimal)
- `Location`: Full restaurant location address

**Advantages:**
- Clean, simple CSV format
- Pre-calculated totals for regular and overtime hours
- Employee names are properly formatted
- No complex parsing required
- One row per employee per job title

### 2. TimeEntries Files (ALTERNATIVE)
**Location:** `tests/fixtures/sample_data/2025-10-20/[LOCATION]/TimeEntries_2025_10_20.csv`

**Structure:**
```
Location,Employee,Job Title,In Date,Out Date,Total Hours,Unpaid Break Time,Paid Break Time,Payable Hours
```

**Key Fields:**
- `Employee`: Full employee name
- `Job Title`: Position
- `In Date`: Clock in timestamp
- `Out Date`: Clock out timestamp
- `Payable Hours`: Actual payable hours (after breaks)

**Advantages:**
- Detailed clock in/out times
- Break time tracking
- Individual shift entries (multiple rows per employee)

## Data Extracted (2025-10-20)

### SDR Location (12060 Potranco Road)
- **Employees:** 17
- **Total Hours:** 179.83
- **Positions:** Host, Server, Cook, Chef, Driver, Prep, Busser, Tortillera, Shift Manager

### T12 Location (Tink-a-Tako - Potranco)
- **Employees:** 20
- **Total Hours:** 179.97
- **Positions:** Host, Server, Cook, Dishwasher, Tortillero, Drive-Thru, Shift Manager, Regular

### TK9 Location (2919 Blanco Rd)
- **Employees:** 9
- **Total Hours:** 101.72
- **Positions:** Server, Cook, Tortillero/a, Drive-Thru, Shift Manager, General Manager

## Implementation

### Simple Extraction Script
Created `extract_toast_payroll.py` which:
1. Reads PayrollExport CSV files
2. Extracts employee name, job title, and hours
3. Calculates total hours (regular + overtime)
4. Outputs clean JSON structure

**Usage:**
```bash
python extract_toast_payroll.py
```

**Output:** `toast_payroll_data.json`

### JSON Structure
```json
{
  "SDR": [
    {
      "name": "Aragon, Brianna",
      "job_title": "Host",
      "regular_hours": 11.11,
      "overtime_hours": 0.0,
      "total_hours": 11.11,
      "location": "12060 Potranco Road"
    },
    ...
  ],
  "T12": [...],
  "TK9": [...]
}
```

## Key Benefits of This Approach

1. **Simple:** No complex parsing, fuzzy matching, or pattern recognition needed
2. **Reliable:** Data is pre-formatted by Toast POS system
3. **Clean:** Employee names are consistent and properly formatted
4. **Complete:** Includes all necessary fields (name, hours, job title, location)
5. **Fast:** Straightforward CSV reading with minimal processing

## Next Steps

Choose your preferred data source:
- **PayrollExport:** If you want pre-calculated totals and don't need shift-level detail
- **TimeEntries:** If you need individual clock in/out times and shift breakdowns

The extraction script can easily be modified to use either source.
