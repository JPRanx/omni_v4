# Restaurant Analytics System Architecture
## QuickBooks + Toast Payroll Reconciliation System

---

## System Overview

**Primary Goal**: Calculate weekly payroll from Toast data, then reconcile against QuickBooks actuals when available.

**Data Flow**:
```
Toast POS (Hours Worked)
    ↓
Weekly Payroll Estimation (Toast hours × QB rates)
    ↓ (when QB file available)
QuickBooks Reconciliation (Actual vs Expected)
    ↓
Variance Reports
```

---

## Core Principles

1. **Toast = Source of Truth for Hours**: What employees actually worked
2. **QuickBooks = Source of Truth for Rates**: What employees actually get paid per hour
3. **No SSN Storage**: Privacy-first design, use names only for matching
4. **Weekly Cadence**: Payroll estimates run weekly, reconciliation when QB available
5. **Human-in-the-Loop Matching**: Manual confirmation of employee name matches via HTML interface

---

## System Components

### Component 1: Rate Lookup Service

**Purpose**: Maintain employee hourly rates from QuickBooks data

**Data Source**: Book77.xlsx (and future QB files)

**Storage Schema** (rates table):
```json
{
  "employee_name": "Ivana Abundiz",        // Normalized format
  "qb_name_original": "ABUNDIZ, IVANA",    // Original QB format (for reference)
  "job_type": "HOSTESS",                    // QB job type
  "hourly_rate": 15.00,                     // $/hour
  "pay_period_start": "2025-10-01",         // When this rate was effective
  "pay_period_end": "2025-10-19",
  "is_salary": false,                       // true for salaried employees
  "last_updated": "2025-11-03T12:00:00Z"
}
```

**Features**:
- Historical rate tracking (rates can change over time)
- Multi-job support (employee can have different rates for different jobs)
- Latest rate lookup by employee + job type
- Rate history for auditing

**API**:
```python
get_rate(employee_name: str, job_type: str, date: str) -> float
get_all_rates(employee_name: str) -> List[Dict]
update_rates_from_qb(qb_file_path: str) -> int  # returns count updated
```

---

### Component 2: Employee Name Matching Service

**Purpose**: Map Toast employee names to QuickBooks employee names (with human confirmation)

**Workflow**:

#### Step 1: Automatic Fuzzy Matching
```python
# When new QB file is loaded
qb_names = ["ABUNDIZ, IVANA", "ARIAS, SANDRA", ...]
toast_names = ["Ivana Abundiz", "Sandra Arias", "Genaro", ...]

# Fuzzy match with confidence scores
matches = [
  {"qb": "ABUNDIZ, IVANA", "toast": "Ivana Abundiz", "confidence": 0.95, "status": "auto"},
  {"qb": "ARIAS, SANDRA", "toast": "Sandra Arias", "confidence": 0.92, "status": "auto"},
  {"qb": "AVILES, GENARO", "toast": "Genaro", "confidence": 0.65, "status": "needs_review"},
]
```

#### Step 2: Generate HTML Confirmation Interface
```html
<!-- matching_confirmation.html -->
<h1>Employee Name Matching Confirmation</h1>

<h2>High Confidence Matches (Auto-approved if > 0.90)</h2>
<table>
  <tr>
    <th>QuickBooks Name</th>
    <th>Toast Name</th>
    <th>Confidence</th>
    <th>Confirm?</th>
  </tr>
  <tr>
    <td>ABUNDIZ, IVANA</td>
    <td>Ivana Abundiz</td>
    <td>95%</td>
    <td><input type="checkbox" checked> ✓</td>
  </tr>
</table>

<h2>Low Confidence Matches (Please Review)</h2>
<table>
  <tr>
    <th>QuickBooks Name</th>
    <th>Toast Name Options</th>
    <th>Action</th>
  </tr>
  <tr>
    <td>AVILES, GENARO</td>
    <td>
      <select>
        <option>Genaro (65% match)</option>
        <option>Genaro Aviles (would need to add)</option>
        <option>Not in Toast (ignore)</option>
      </select>
    </td>
    <td><button>Confirm</button></td>
  </tr>
</table>

<h2>Unmatched QuickBooks Names</h2>
<ul>
  <li>GONZALES, MARIA G → <input type="text" placeholder="Enter Toast name"> <button>Link</button></li>
</ul>

<h2>Unmatched Toast Names</h2>
<ul>
  <li>Mike (nickname?) → <input type="text" placeholder="Enter QB name"> <button>Link</button></li>
</ul>

<button>Save All Mappings</button>
```

#### Step 3: Storage Schema (employee_mappings table)
```json
{
  "toast_name": "Ivana Abundiz",
  "qb_name": "ABUNDIZ, IVANA",
  "match_confidence": 0.95,
  "match_method": "auto_fuzzy" | "manual_confirmed" | "manual_created",
  "confirmed_by": "Jorge",
  "confirmed_at": "2025-11-03T12:00:00Z",
  "is_active": true,
  "notes": "Exact name match"
}
```

**Features**:
- Fuzzy matching with SequenceMatcher (difflib)
- Manual override capability
- Audit trail (who confirmed, when)
- Support for nicknames (Toast: "Mike" → QB: "RODRIGUEZ, MICHAEL")
- Inactive flag (for former employees)

---

### Component 3: Job Type Mapping Service

**Purpose**: Map Toast job codes to QuickBooks job types

**Storage Schema** (job_mappings table):
```json
{
  "toast_job_code": "Server",
  "qb_job_type": "WAITER",          // Could map to WAITER or WAITRESS
  "qb_job_type_alt": "WAITRESS",    // Alternative mapping
  "mapping_rule": "Use WAITER for male names, WAITRESS for female names" | "Always use WAITER",
  "last_updated": "2025-11-03T12:00:00Z"
}
```

**Common Mappings**:
```
Toast              → QuickBooks
----------------------------------
Server             → WAITER / WAITRESS
Busser             → BUSSER
Host / Hostess     → HOSTESS
Dishwasher         → DISHWASHER
Line Cook          → LINE SERVER
Manager            → MANAGER
Drive-Thru         → DRIVE-THRU
```

**Features**:
- One-to-many mapping support (Server → WAITER or WAITRESS)
- Configurable mapping rules
- Easy updates via admin interface

---

### Component 4: Weekly Payroll Estimator

**Purpose**: Calculate expected payroll from Toast data using QB rates (runs every week, even without QB file)

**Input**:
- Toast TimeEntries for the week
- Employee rate lookup (from QB historical data)
- Job type mappings

**Process**:
```python
def calculate_weekly_payroll(week_start_date: str, week_end_date: str):
    """
    Calculate expected payroll for a week using Toast hours + QB rates
    """
    # 1. Get all Toast TimeEntries for the week
    time_entries = get_toast_time_entries(week_start_date, week_end_date)

    # 2. Group by employee + job type
    employee_hours = aggregate_hours_by_employee_and_job(time_entries)

    # 3. For each employee/job combination
    payroll_lines = []
    for emp_name, job_type, regular_hours, overtime_hours in employee_hours:
        # Look up rate
        rate = get_rate(emp_name, job_type, week_start_date)

        if rate is None:
            # Missing rate - flag for review
            payroll_lines.append({
                'employee': emp_name,
                'job_type': job_type,
                'regular_hours': regular_hours,
                'overtime_hours': overtime_hours,
                'rate': None,
                'status': 'missing_rate',
                'error': f'No rate found for {emp_name} as {job_type}'
            })
            continue

        # Calculate wages
        regular_wages = regular_hours * rate
        overtime_wages = overtime_hours * rate * 1.5
        total_wages = regular_wages + overtime_wages

        payroll_lines.append({
            'employee': emp_name,
            'job_type': job_type,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_hours,
            'rate': rate,
            'regular_wages': regular_wages,
            'overtime_wages': overtime_wages,
            'total_wages': total_wages,
            'status': 'estimated'
        })

    # 4. Store estimated payroll
    save_estimated_payroll(week_start_date, payroll_lines)

    return payroll_lines
```

**Storage Schema** (estimated_payroll table):
```json
{
  "week_start_date": "2025-10-01",
  "week_end_date": "2025-10-07",
  "employee_name": "Ivana Abundiz",
  "job_type": "HOSTESS",
  "regular_hours": 40.0,
  "overtime_hours": 5.9,
  "hourly_rate": 15.00,
  "regular_wages": 600.00,
  "overtime_wages": 132.75,      // 5.9 × 15 × 1.5
  "total_wages": 732.75,
  "source": "toast_estimate",
  "status": "estimated",          // "estimated" | "reconciled" | "missing_rate"
  "created_at": "2025-11-03T12:00:00Z"
}
```

**Output**: Weekly payroll estimate (CSV or report)

---

### Component 5: QuickBooks Reconciliation Engine

**Purpose**: Compare Toast estimates vs QB actuals when QB file arrives

**Triggered By**: Loading a new QB file (Book77.xlsx or similar)

**Process**:
```python
def reconcile_payroll(qb_file_path: str, pay_period_start: str, pay_period_end: str):
    """
    Compare Toast estimated payroll vs QB actual payroll
    """
    # 1. Parse QB file
    qb_payroll = parse_quickbooks_payroll(qb_file_path)

    # 2. Get Toast estimates for same period
    toast_estimates = get_estimated_payroll(pay_period_start, pay_period_end)

    # 3. Match employees (using employee_mappings)
    matched_records = []
    unmatched_qb = []
    unmatched_toast = []

    for qb_record in qb_payroll:
        # Find matching Toast employee
        toast_name = get_toast_name_from_qb(qb_record['qb_name'])

        if toast_name is None:
            unmatched_qb.append(qb_record)
            continue

        # Find corresponding Toast estimate
        toast_record = find_toast_record(toast_estimates, toast_name, qb_record['job_type'])

        if toast_record is None:
            unmatched_qb.append(qb_record)
            continue

        # Compare
        variance = {
            'employee': toast_name,
            'job_type': qb_record['job_type'],

            # Toast (expected)
            'toast_hours': toast_record['total_hours'],
            'toast_rate': toast_record['hourly_rate'],
            'toast_wages': toast_record['total_wages'],

            # QuickBooks (actual)
            'qb_hours': qb_record['hours'],
            'qb_rate': qb_record['rate'],
            'qb_wages': qb_record['total'],

            # Variance
            'hours_diff': qb_record['hours'] - toast_record['total_hours'],
            'rate_diff': qb_record['rate'] - toast_record['hourly_rate'],
            'wages_diff': qb_record['total'] - toast_record['total_wages'],

            # Status
            'status': 'matched',
            'variance_pct': abs((qb_record['total'] - toast_record['total_wages']) / toast_record['total_wages'] * 100)
        }

        # Flag significant variances
        if abs(variance['hours_diff']) > 0.5:  # > 30 minutes
            variance['flags'] = variance.get('flags', []) + ['hours_mismatch']

        if abs(variance['rate_diff']) > 0.01:  # > 1 cent
            variance['flags'] = variance.get('flags', []) + ['rate_mismatch']

        if abs(variance['wages_diff']) > 5.00:  # > $5
            variance['flags'] = variance.get('flags', []) + ['wages_mismatch']

        matched_records.append(variance)

    # 4. Find Toast records that don't exist in QB
    for toast_record in toast_estimates:
        qb_match = find_qb_record(qb_payroll, toast_record['employee'], toast_record['job_type'])
        if qb_match is None:
            unmatched_toast.append(toast_record)

    # 5. Store reconciliation results
    save_reconciliation(pay_period_start, {
        'matched': matched_records,
        'unmatched_qb': unmatched_qb,
        'unmatched_toast': unmatched_toast,
        'summary': {
            'total_matched': len(matched_records),
            'total_variance': sum(r['wages_diff'] for r in matched_records),
            'flagged_count': len([r for r in matched_records if 'flags' in r]),
        }
    })

    return matched_records, unmatched_qb, unmatched_toast
```

**Storage Schema** (reconciliation_results table):
```json
{
  "pay_period_start": "2025-10-01",
  "pay_period_end": "2025-10-07",
  "employee_name": "Ivana Abundiz",
  "job_type": "HOSTESS",

  "toast_hours": 40.0,
  "toast_rate": 15.00,
  "toast_wages": 600.00,

  "qb_hours": 39.5,
  "qb_rate": 15.00,
  "qb_wages": 592.50,

  "hours_variance": -0.5,
  "rate_variance": 0.00,
  "wages_variance": -7.50,
  "variance_pct": 1.25,

  "status": "variance_detected",
  "flags": ["hours_mismatch"],
  "notes": "Toast shows 40 hrs, QB paid 39.5 hrs - investigate missing 30 min",

  "reconciled_at": "2025-11-03T12:00:00Z"
}
```

**Output**: Reconciliation report (HTML dashboard + CSV export)

---

## Storage Solution: Recommendation

### Option 1: Supabase (PostgreSQL) ✓ RECOMMENDED

**Pros**:
- You already have it set up
- Structured, relational data model
- Real-time updates
- Built-in auth and security
- Easy to query (SQL)
- API access (REST/GraphQL)
- Can build dashboards on top
- Free tier is generous
- Supports views, functions, triggers

**Cons**:
- Requires internet connection
- Slight learning curve for schema design

**Schema Tables**:
```sql
-- Employee rates from QB
CREATE TABLE employee_rates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_name TEXT NOT NULL,
  qb_name_original TEXT NOT NULL,
  job_type TEXT NOT NULL,
  hourly_rate DECIMAL(10,2),
  is_salary BOOLEAN DEFAULT FALSE,
  pay_period_start DATE NOT NULL,
  pay_period_end DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(employee_name, job_type, pay_period_start)
);

-- Employee name mappings (Toast ↔ QB)
CREATE TABLE employee_mappings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  toast_name TEXT UNIQUE NOT NULL,
  qb_name TEXT NOT NULL,
  match_confidence DECIMAL(3,2),
  match_method TEXT,
  confirmed_by TEXT,
  confirmed_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job type mappings (Toast ↔ QB)
CREATE TABLE job_mappings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  toast_job_code TEXT UNIQUE NOT NULL,
  qb_job_type TEXT NOT NULL,
  qb_job_type_alt TEXT,
  mapping_rule TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly payroll estimates (from Toast)
CREATE TABLE estimated_payroll (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  employee_name TEXT NOT NULL,
  job_type TEXT NOT NULL,
  regular_hours DECIMAL(10,2),
  overtime_hours DECIMAL(10,2),
  hourly_rate DECIMAL(10,2),
  regular_wages DECIMAL(10,2),
  overtime_wages DECIMAL(10,2),
  total_wages DECIMAL(10,2),
  source TEXT DEFAULT 'toast_estimate',
  status TEXT DEFAULT 'estimated',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(week_start_date, employee_name, job_type)
);

-- QB actual payroll (from QB files)
CREATE TABLE qb_payroll (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pay_period_start DATE NOT NULL,
  pay_period_end DATE NOT NULL,
  qb_name TEXT NOT NULL,
  employee_name TEXT,  -- Mapped Toast name
  job_type TEXT NOT NULL,
  hours DECIMAL(10,2),
  hourly_rate DECIMAL(10,2),
  total_wages DECIMAL(10,2),
  gross_pay DECIMAL(10,2),
  net_pay DECIMAL(10,2),
  source_file TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(pay_period_start, qb_name, job_type)
);

-- Reconciliation results
CREATE TABLE reconciliation_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pay_period_start DATE NOT NULL,
  pay_period_end DATE NOT NULL,
  employee_name TEXT NOT NULL,
  job_type TEXT NOT NULL,

  toast_hours DECIMAL(10,2),
  toast_rate DECIMAL(10,2),
  toast_wages DECIMAL(10,2),

  qb_hours DECIMAL(10,2),
  qb_rate DECIMAL(10,2),
  qb_wages DECIMAL(10,2),

  hours_variance DECIMAL(10,2),
  rate_variance DECIMAL(10,2),
  wages_variance DECIMAL(10,2),
  variance_pct DECIMAL(5,2),

  status TEXT,
  flags JSONB,
  notes TEXT,

  reconciled_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(pay_period_start, employee_name, job_type)
);
```

### Option 2: SQLite + Parquet Hybrid

**Pros**:
- Local, no internet required
- Fast queries (SQLite)
- Efficient storage (Parquet for raw data)
- Simple deployment

**Cons**:
- No real-time collaboration
- Manual backup needed
- Harder to build dashboards

### Option 3: DuckDB + Parquet

**Pros**:
- Best for analytics queries
- Efficient columnar storage
- Can query Parquet directly
- Great for large datasets

**Cons**:
- Less mature ecosystem
- Not as good for transactional updates

**RECOMMENDATION: Use Supabase (PostgreSQL)** since you already have it and it fits all requirements.

---

## Weekly Workflow

### Week 1: Toast-Only (No QB file yet)
```
Monday: Week starts (Oct 1)
├─ Toast TimeEntries accumulate daily
└─ No action needed

Sunday: Week ends (Oct 7)
├─ Run weekly payroll estimator
├─ Calculate: Toast hours × QB rates (from historical data)
├─ Output: estimated_payroll_2025-10-01.csv
└─ Status: "Estimated (awaiting QB confirmation)"
```

### Week 2: Reconciliation (QB file arrives)
```
Monday: New week starts (Oct 8)
├─ Toast TimeEntries accumulate for Week 2
└─ Previous week still showing "Estimated"

Wednesday: QB file arrives for Week 1 (Book77.xlsx)
├─ Parse QB file
├─ Update employee rates (if changed)
├─ Run reconciliation for Week 1
├─ Generate variance report
├─ Flag mismatches for review
└─ Status: "Reconciled" or "Variance Detected"

Sunday: Week 2 ends (Oct 14)
├─ Run estimator for Week 2
└─ Status: "Estimated (awaiting QB confirmation)"
```

---

## HTML Interfaces Needed

### 1. Employee Name Matching Interface
- Auto-generated after QB file upload
- Shows fuzzy matches with confidence scores
- Allows manual confirmation/override
- Saves to employee_mappings table

### 2. Reconciliation Dashboard
- Shows matched records (green)
- Shows variances (yellow/red by severity)
- Shows unmatched records (gray)
- Allows drilling into details
- Export to Excel

### 3. Weekly Payroll Report
- Shows estimated payroll by employee
- Groups by job type
- Shows total labor cost
- Flags missing rates
- Export to PDF/Excel

---

## Implementation Phases

### Phase 1: Rate Management (Week 4 Day 4-5)
- [ ] Parse QB file (Book77.xlsx)
- [ ] Extract employee rates
- [ ] Store in Supabase (employee_rates table)
- [ ] Create rate lookup API
- [ ] Update rates when new QB file arrives

### Phase 2: Employee Matching (Week 5)
- [ ] Fuzzy match Toast names → QB names
- [ ] Generate HTML confirmation interface
- [ ] Manual confirmation workflow
- [ ] Store mappings in Supabase (employee_mappings table)

### Phase 3: Job Type Mapping (Week 5)
- [ ] Create job_mappings table
- [ ] Seed with common mappings
- [ ] Admin interface to update mappings

### Phase 4: Weekly Payroll Estimator (Week 5-6)
- [ ] Aggregate Toast TimeEntries by week
- [ ] Calculate regular vs overtime hours
- [ ] Apply overtime rules (1.5x after 40 hrs/week)
- [ ] Look up rates from employee_rates
- [ ] Calculate estimated wages
- [ ] Store in estimated_payroll table
- [ ] Generate CSV report

### Phase 5: Reconciliation Engine (Week 6)
- [ ] Parse QB file
- [ ] Match to Toast estimates
- [ ] Calculate variances
- [ ] Flag significant differences
- [ ] Store in reconciliation_results table
- [ ] Generate HTML dashboard

### Phase 6: Reporting & Alerts (Week 7)
- [ ] HTML reconciliation dashboard
- [ ] Email alerts for variances > threshold
- [ ] Weekly payroll summary email
- [ ] Excel export functionality

---

## Next Steps

**Immediate (Now)**:
1. Confirm Supabase as storage solution
2. Set up Supabase tables (I can generate SQL)
3. Implement QB parser (using QUICKBOOKS_PARSING_RULES.md)
4. Load Book77.xlsx into employee_rates table

**Questions for You**:
1. Do you want me to generate the Supabase SQL schema now?
2. Should I create the QB parser next, or the employee matching HTML first?
3. What's your Supabase project URL? (I can help with connection setup)
4. Any specific variance thresholds? (e.g., flag if > $10 or > 2% difference)

Ready to proceed with implementation!
