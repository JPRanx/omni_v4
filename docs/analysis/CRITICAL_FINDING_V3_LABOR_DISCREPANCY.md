# CRITICAL FINDING: V3 Labor Cost Discrepancy

**OMNI V4 Restaurant Analytics System**
**Date**: 2025-11-03
**Priority**: HIGH - Blocking Dashboard Integration
**Status**: Investigation Required

---

## Summary

V3 is reporting **DOUBLE** the actual labor cost, causing severe miscalculation of labor percentages.

**Evidence for SDR on August 20, 2025**:
- **V3 P&L Report**: $2,801.10 labor cost (71.76% of sales)
- **Actual PayrollExport CSV**: $1,436.26 total pay (36.8% of sales)
- **Discrepancy**: $1,364.84 (approximately 2x the actual cost)

**Impact**: V3 dashboards are showing restaurant performance as much worse than reality.

---

## Detailed Analysis

### Source Data (PayrollExport_2025_08_20.csv)

**File Path**: `restaurant_analytics_v3/Config/2025-08-20/SDR/PayrollExport_2025_08_20.csv`

**Actual Totals**:
```
Total Regular Hours:  186.74 hours
Total Overtime Hours:   0.00 hours
Total Hours:          186.74 hours
Total Pay:         $1,436.26
```

**Sales Data** (Net sales summary.csv):
```
Gross Sales:       $3,991.79
Sales Discounts:     -$88.48
Net Sales:         $3,903.31
```

**Correct Labor Percentage**:
```
Labor % = ($1,436.26 / $3,903.31) × 100 = 36.8%
```

This matches **V4's calculation exactly** ✅

---

### V3 P&L Report (SDR_2025-08-20_pnl.json)

**File Path**: `restaurant_analytics_v3/Output/PNL/SDR_2025-08-20_pnl.json`

**Reported Values**:
```json
{
  "expenses": {
    "labor": {
      "wages": 2801.1,
      "total": 2801.1,
      "percentage": 71.76
    }
  },
  "margins": {
    "labor_pct": 71.76
  }
}
```

**V3's Calculation**:
```
Labor % = ($2,801.10 / $3,903.31) × 100 = 71.76%
```

---

## The Discrepancy

| Metric | Actual (PayrollExport) | V3 Reported | Difference |
|--------|----------------------|-------------|------------|
| Labor Cost | $1,436.26 | $2,801.10 | +$1,364.84 (+95%) |
| Labor % | 36.8% | 71.76% | +34.96 pp |
| **Factor** | **1.0x** | **~2.0x** | **V3 doubles cost** |

---

## Possible Causes

### Hypothesis 1: V3 Includes Employer Taxes/Benefits (Most Likely)

**Theory**: V3 might be calculating:
```
Total Labor Cost = Wages + Employer Taxes + Benefits
                 = $1,436.26 + (employer burden)
```

**Common Employer Burden Rates**:
- Social Security: 6.2% of wages
- Medicare: 1.45% of wages
- FUTA: ~0.6% of wages
- SUTA: varies by state (2-6%)
- Workers Comp: varies (2-10%)
- **Total Typical Burden**: 10-25% of wages

**Problem**: Even with 25% burden, that's only $1,795 total, not $2,801.

**To Double the Cost** (95% burden):
- Would need extremely high insurance/benefits
- OR a calculation error

### Hypothesis 2: V3 Double-Counts Labor Data

**Theory**: V3 might be:
1. Reading PayrollExport ($1,436.26)
2. ALSO reading TimeEntries and calculating hours × rate
3. Summing both (double counting)

**Evidence Needed**:
- Check V3 ToastProcessor code
- Trace where `total_labor_cost` comes from
- Verify if multiple data sources are combined

### Hypothesis 3: V3 Uses Different Data Source

**Theory**: V3 might not use PayrollExport at all:
- Might calculate from TimeEntries.csv
- Might apply incorrect hourly rates
- Might include overhead/burden incorrectly

**Evidence**:
- V3 has both PayrollExport and TimeEntries files
- Need to check which one V3 actually uses

### Hypothesis 4: Bug in V3 Calculation

**Theory**: Simple programming error:
- Multiplying by 2 somewhere
- Adding same cost twice
- Using wrong formula

---

## V4 Validation

**V4's Approach**:
```python
# From extract_labor_dto_from_payroll() in integration tests
total_pay = payroll_df['Total Pay'].fillna(0).sum()  # $1,436.26
sales = 3903.31
labor_percentage = (total_pay / sales) * 100  # 36.8%
```

**V4 Result**: 36.8% labor ✅

**V4 is calculating correctly** - matches the source PayrollExport CSV exactly.

---

## Business Impact

### On SDR Restaurant (Example)

**V3 Reporting (Incorrect)**:
- Labor Cost: $2,801 (71.76%)
- Status: CRITICAL
- Grade: F
- Message: "Severe labor cost problem - immediate action required!"

**V4 Reporting (Correct)**:
- Labor Cost: $1,436 (36.8%)
- Status: SEVERE (still high, but not critical)
- Grade: F (borderline D+)
- Message: "Labor cost needs improvement"

**Reality**: SDR has a labor problem, but it's not as catastrophic as V3 suggests.

### Across All Restaurants

**Impact on Decision Making**:
1. **Panic Mode**: Managers see 71% labor and panic
2. **Over-Correction**: Might cut staff too aggressively
3. **Lost Trust**: Inaccurate reporting damages credibility
4. **Wrong Priorities**: Focus on "fixing" a problem that's half as bad

**Impact on Historical Data**:
- All V3 P&L reports may be wrong
- Historical trends may be misleading
- Pattern learning from V3 data would be incorrect

---

## Investigation Steps

### Step 1: Trace V3 Data Flow ✅ (Partially Complete)

**What We Know**:
1. V3 `LaborProcessor.process()` gets `total_labor_cost` from `toast_data`
2. `toast_data` comes from ToastProcessor (need to examine)
3. PayrollExport file has correct values
4. V3 P&L has inflated values

**Next**:
- [ ] Read V3 `ToastProcessor` code
- [ ] Trace where `total_labor_cost` is calculated
- [ ] Check if it reads PayrollExport or TimeEntries
- [ ] Look for any multipliers or burden calculations

### Step 2: Compare Multiple Days

Test if this is consistent across all days:
- [ ] Check Aug 21, 22, 23 for same pattern
- [ ] Check T12 and TK9 data
- [ ] See if all restaurants show ~2x labor cost

### Step 3: Check V3 Documentation

- [ ] Search for any notes about labor cost calculation
- [ ] Check if "employer burden" is mentioned
- [ ] Look for configuration files with burden rates

### Step 4: Ask Jorge

**Questions for User**:
1. Are V3's labor percentages known to be high?
2. Has anyone questioned why labor costs seem so high?
3. Is there a known "employer burden" factor in V3?
4. Which is correct - V3 or PayrollExport CSV?

---

## Recommendations

### Immediate Actions

1. **DO NOT Trust V3 P&L Data** for labor costs
   - Until discrepancy is resolved
   - V3 dashboards may be misleading

2. **Use V4 Calculations as Authoritative**
   - V4 reads directly from PayrollExport
   - Matches source data exactly
   - No unexplained multipliers

3. **Investigate V3 Thoroughly**
   - Find root cause of 2x multiplication
   - Document whether it's intentional (burden) or bug
   - Fix if it's a bug, document if it's intentional

4. **Communicate Findings to Jorge**
   - Show the discrepancy clearly
   - Explain business impact
   - Get guidance on correct approach

### Dashboard Integration Strategy

**Option 1: Use V4 Data Only** (Recommended)
- Ignore V3 P&L files
- Export V4 calculations to dashboard
- Provides accurate labor percentages

**Option 2: Fix V3 First**
- Investigate and fix V3 calculation
- Then integrate V4 with corrected V3
- Takes longer but preserves historical data

**Option 3: Dual Display**
- Show both V3 and V4 calculations
- Label clearly: "V3 (includes burden)" vs "V4 (actual wages)"
- Let user decide which to trust

---

## Sample Code to Investigate V3

```python
# Script to trace V3 labor calculation
import json
import pandas as pd
from pathlib import Path

# Load V3 P&L
with open('restaurant_analytics_v3/Output/PNL/SDR_2025-08-20_pnl.json') as f:
    v3_pnl = json.load(f)

# Load PayrollExport
payroll = pd.read_csv('restaurant_analytics_v3/Config/2025-08-20/SDR/PayrollExport_2025_08_20.csv')

# Compare
v3_labor_cost = v3_pnl['expenses']['labor']['total']
actual_labor_cost = payroll['Total Pay'].sum()

print(f"V3 Reported: ${v3_labor_cost:,.2f}")
print(f"PayrollExport: ${actual_labor_cost:,.2f}")
print(f"Difference: ${v3_labor_cost - actual_labor_cost:,.2f}")
print(f"Multiplier: {v3_labor_cost / actual_labor_cost:.2f}x")
```

---

## Next Steps

1. **Read V3 ToastProcessor** to trace labor cost calculation
2. **Check multiple dates** to confirm pattern
3. **Document findings** in this report
4. **Present to Jorge** with recommendation
5. **Decide on integration approach** based on findings

---

## Conclusion

**V3 is over-reporting labor costs by approximately 2x**, causing severe misrepresentation of restaurant performance.

**V4 is calculating correctly** and matches source data (PayrollExport CSV) exactly.

**Critical Decision Required**: Should V4 dashboard integration use:
- V4's accurate calculations (recommended), OR
- V3's inflated calculations (for consistency with history), OR
- Both with clear labeling?

**This must be resolved before dashboard integration proceeds.**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
**Author**: System Architect
**Review Status**: Requires Jorge's Input
