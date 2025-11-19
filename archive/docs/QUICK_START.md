# Quick Start - Toast Payroll Data

## What Changed
- **OLD:** Complex QuickBooks PDF parsing with fuzzy employee matching
- **NEW:** Simple Toast PayrollExport CSV extraction

## Files You Need

### Toast PayrollExport CSV Structure
```
Employee,Job Title,Regular Hours,Overtime Hours,Hourly Rate,Regular Pay,...
"Garcia, Enriqueta",Chef,20.97,0.0,15.00,314.55,...
"Morales, Adrian",Server,17.69,0.0,3.00,53.07,...
```

### Location of Files
```
tests/fixtures/sample_data/2025-10-20/
├── SDR/
│   ├── PayrollExport_2025_10_20.csv   <- USE THIS
│   └── TimeEntries_2025_10_20.csv     <- Alternative with shift details
├── T12/
│   ├── PayrollExport_2025_10_20.csv
│   └── TimeEntries_2025_10_20.csv
└── TK9/
    ├── PayrollExport_2025_10_20.csv
    └── TimeEntries_2025_10_20.csv
```

## Extract Employee Hours (Simple)

```python
import csv

# Read PayrollExport
with open('PayrollExport_2025_10_20.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['Employee']
        regular_hours = float(row['Regular Hours'] or 0)
        overtime_hours = float(row['Overtime Hours'] or 0)
        total_hours = regular_hours + overtime_hours
        print(f"{name}: {total_hours} hours")
```

## Run Provided Scripts

```bash
# Extract all locations to JSON
python extract_toast_payroll.py

# Compare PayrollExport vs TimeEntries
python compare_toast_sources.py
```

## Output Format

### toast_payroll_data.json
```json
{
  "SDR": [
    {
      "name": "Garcia, Enriqueta",
      "job_title": "Chef",
      "regular_hours": 20.97,
      "overtime_hours": 0.0,
      "total_hours": 20.97,
      "location": "12060 Potranco Road"
    }
  ]
}
```

## Key Data Points (2025-10-20)

| Location | Employees | Total Hours |
|----------|-----------|-------------|
| SDR      | 17        | 179.83      |
| T12      | 20        | 179.97      |
| TK9      | 9         | 101.72      |

## Two Data Source Options

### PayrollExport (RECOMMENDED)
- Pre-calculated totals
- One row per employee per job title
- Simple, clean format
- Best for: Payroll calculations, employee hours

### TimeEntries (ALTERNATIVE)
- Individual shift timestamps
- Multiple rows per employee (one per shift)
- Includes clock in/out times
- Best for: Shift analysis, time tracking detail

## No More QuickBooks!
All QB parsing code, employee matching system, and related files have been removed. This approach is:
- Simpler (no PDF parsing)
- Faster (CSV reading)
- More reliable (structured data from Toast)
- Cleaner (no fuzzy name matching needed)
