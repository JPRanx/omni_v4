# V3 Dashboard Integration Analysis

**OMNI V4 Restaurant Analytics System**
**Analysis Date**: 2025-11-03
**Purpose**: Understand V3 dashboard to integrate V4 data

---

## Executive Summary

The V3 dashboard system is a **FILE-BASED HTML dashboard** that reads daily P&L JSON files from disk. It does **NOT** currently use Supabase for dashboard data, though Supabase infrastructure exists in V3.

**Key Finding**: We can integrate V4 by either:
1. **Option A (Easiest)**: Make V4 write P&L JSON files in V3 format → Existing dashboard works immediately
2. **Option B (Better)**: Deploy V4 data to Supabase → Create new dashboard that reads from database

**Recommendation**: Start with **Option A** for immediate value, then migrate to **Option B** for production excellence.

---

## V3 Dashboard Architecture

### Data Flow

```
Toast CSVs → V3 Processing → Output/PNL/{RESTAURANT}_{DATE}_pnl.json → dashboard.html
```

### Dashboard Type: Static HTML Generator

- **Type**: Python script generates static HTML file
- **Input**: JSON files from `Output/PNL/` directory
- **Output**: `Output/dashboard.html` (single HTML file)
- **View Method**: Opens in web browser (`file:///` protocol)
- **Update Frequency**: Regenerated on-demand (not real-time)

### Dashboard Files

1. **generate_dashboard.py** (138 lines)
   - Basic weekly P&L dashboard
   - Reads from `Output/PNL/weekly/*_pnl.json`
   - Generates simple HTML with summary cards

2. **enhanced_dashboard_generator.py** (205 lines)
   - More visually appealing version
   - Per-restaurant cards with color coding
   - Grade-based styling (good/warning/critical)
   - Responsive design with hover effects

---

## V3 Data Format

### P&L JSON Structure

**File Naming**: `{RESTAURANT}_{DATE}_pnl.json`
- Example: `SDR_2025-08-20_pnl.json`

**Required Fields** (from actual V3 file):

```json
{
  "date": "2025-08-20",
  "restaurant": "SDR",

  "revenue": {
    "gross_sales": 3903.31,
    "net_sales": 3903.31
  },

  "expenses": {
    "labor": {
      "wages": 2801.1,
      "tips": 0,
      "total": 2801.1,
      "percentage": 71.76
    },
    "cogs": {
      "amount": 0,
      "percentage": 0
    },
    "operating": {
      "amount": 0,
      "percentage": 0.0
    },
    "total": 2801.1
  },

  "profit": {
    "gross": 3903.31,
    "operating": 1102.21,
    "net": 1102.21
  },

  "margins": {
    "gross_margin": 100.0,
    "operating_margin": 28.24,
    "net_margin": 28.24,
    "labor_pct": 71.76
  },

  "metrics": {
    "prime_cost": 2801.1,
    "prime_cost_pct": 71.76
  },

  "data_quality": {
    "confidence": 0.7388601036269431,
    "completeness": "good"
  },

  "grade_info": {
    "score": 70.0,
    "grade": "C",
    "breakdown": {
      "labor": 60,
      "speed": 70,
      "sales": 70,
      "waste": 80,
      "customer_satisfaction": 85
    },
    "recommendations": [
      "Review staffing levels - labor cost is high",
      "Focus on speed of service improvements",
      "Sales below target - review marketing/operations"
    ]
  },

  "performance": {
    "labor_status": "critical",
    "profit_status": "good",
    "prime_cost_status": "critical",
    "health_score": 55,
    "health_grade": "F"
  }
}
```

### Key Observations

**V3 Labor Percentage Calculation**:
- V3 uses: `labor_percentage = (labor_cost / sales) * 100`
- **PROBLEM**: The example shows 71.76% labor (wages $2,801 / sales $3,903)
- **V4 Actual**: We calculated 36.8% labor for SDR on Aug 20
- **Discrepancy**: V3 is calculating labor differently or using different source data

**Note**: This discrepancy needs investigation. Possible causes:
1. V3 might be using different CSV files
2. V3 might be including different cost categories
3. V3 might have a calculation bug
4. Data sources might be different

---

## Supabase in V3

### Current State

**Supabase Infrastructure EXISTS but NOT USED for Dashboard**:

1. **SupabaseManager** (`Modules/Core/supabase_manager.py`)
   - Handles connection using `.env` credentials
   - Uses `SUPABASE_SERVICE_KEY` (bypasses RLS)
   - Returns Supabase client for database operations

2. **Environment Variables Required**:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key
   ```

3. **Usage in V3**:
   - Connected in `Bmain.py`
   - Used for some operations (TBD - need to investigate further)
   - **NOT used for dashboard data** (dashboard reads JSON files)

---

## Integration Options

### Option A: V4 Writes P&L JSON Files (Quick Win)

**Approach**:
1. Create V4 script to export data in V3 P&L JSON format
2. Write to `restaurant_analytics_v3/Output/PNL/`
3. Existing V3 dashboard works immediately

**Pros**:
- ✅ Immediate integration (< 2 hours)
- ✅ No dashboard changes needed
- ✅ Users see V4 data in familiar format
- ✅ Can run V3 and V4 side-by-side (different dates)

**Cons**:
- ❌ File-based (not scalable)
- ❌ Not real-time
- ❌ Doesn't leverage Supabase
- ❌ Temporary solution

**Implementation Steps**:
1. Create `scripts/export_pnl_json.py` in V4
2. Map V4 metrics to V3 JSON structure
3. Write files to V3 Output directory
4. Run V3 `generate_dashboard.py`

**Estimated Time**: 2-3 hours

---

### Option B: V4 → Supabase → New Dashboard (Production Solution)

**Approach**:
1. Deploy V4 data to Supabase database
2. Create new dashboard that reads from Supabase
3. Migrate V3 dashboard users to new system

**Pros**:
- ✅ Production-grade architecture
- ✅ Real-time data access
- ✅ Scalable (database-backed)
- ✅ Enables advanced features (filtering, date ranges, trends)
- ✅ API-accessible for mobile/web apps

**Cons**:
- ❌ Requires Supabase deployment (2-4 hours)
- ❌ Requires new dashboard development (4-6 hours)
- ❌ Users need to learn new dashboard

**Implementation Steps**:

**Phase 1: Supabase Deployment** (Week 5 Day 3)
1. Create Supabase database schema
2. Implement `SupabaseDatabaseClient` in V4
3. Test with August data
4. Verify data integrity

**Phase 2: Dashboard Development** (Week 5 Day 4)
1. Create dashboard that queries Supabase
2. Implement filtering (restaurant, date range)
3. Add trend visualizations
4. Deploy and test

**Estimated Time**: 6-10 hours

---

## Recommended Integration Path

### Phase 1: Quick Integration (Week 5 Day 3) - **Option A**

**Goal**: Get V4 data visible in V3 dashboard TODAY

1. **Create P&L JSON Exporter** (2 hours)
   - Script: `scripts/export_v4_to_v3_format.py`
   - Map V4 batch results to V3 P&L JSON
   - Write to V3 Output directory

2. **Test with August Data** (30 min)
   - Export Aug 20-31 from V4
   - Run V3 dashboard generator
   - Verify visualizations work

3. **Compare V4 vs V3 Metrics** (30 min)
   - Investigate labor% discrepancy
   - Document differences
   - Validate V4 calculations

**Deliverable**: V4 data visible in V3 dashboard

---

### Phase 2: Supabase Deployment (Week 5 Day 4) - **Option B Foundation**

**Goal**: Production database infrastructure

1. **Create Database Schema** (1 hour)
   ```sql
   CREATE TABLE daily_performance (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       restaurant_code TEXT NOT NULL,
       business_date DATE NOT NULL,
       total_sales DECIMAL NOT NULL,
       total_labor_cost DECIMAL NOT NULL,
       labor_percentage DECIMAL NOT NULL,
       labor_grade TEXT,
       labor_status TEXT,
       total_hours DECIMAL,
       created_at TIMESTAMP DEFAULT NOW(),
       UNIQUE(restaurant_code, business_date)
   );

   CREATE TABLE learned_patterns (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       restaurant_code TEXT NOT NULL,
       day_of_week INTEGER NOT NULL,
       pattern_type TEXT NOT NULL,
       predicted_labor_percentage DECIMAL,
       predicted_total_hours DECIMAL,
       confidence DECIMAL,
       observations INTEGER,
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW()
   );

   CREATE INDEX idx_daily_perf_rest_date ON daily_performance(restaurant_code, business_date);
   CREATE INDEX idx_patterns_rest_day ON learned_patterns(restaurant_code, day_of_week);
   ```

2. **Implement SupabaseDatabaseClient** (2 hours)
   - Extends `DatabaseClient` protocol
   - Uses V3's `SupabaseManager` approach
   - Implements all CRUD operations
   - Adds comprehensive error handling

3. **Test with Real Data** (1 hour)
   - Connect to Supabase
   - Write August batch results
   - Verify transactions work
   - Check data integrity

**Deliverable**: V4 data persisted in Supabase

---

### Phase 3: Modern Dashboard (Week 5 Day 5) - **Option B Complete**

**Goal**: Production-ready dashboard

**Option 3A: Extend V3 Dashboard** (Easier)
- Modify V3 dashboard to read from Supabase
- Keep existing UI/UX
- Add database query layer

**Option 3B: New React/Next.js Dashboard** (Better)
- Modern web application
- Real-time updates
- Advanced filtering and analytics
- Mobile-responsive

**Recommendation**: Start with **Option 3A** (extend V3) for speed, plan **Option 3B** for Week 6.

---

## Data Mapping: V4 → V3 Format

### V4 Available Data (from batch_results_aug_2025.json)

```python
{
    "restaurant": "SDR",
    "date": "2025-08-20",
    "success": true,
    "labor_percentage": 36.8,          # V4 calculated
    "duration_ms": 66.4
}
```

### V4 Context Data (from pipeline)

```python
context.get('sales')                  # Total sales
context.get('labor_percentage')       # Labor %
context.get('labor_grade')            # A, B+, B, C, D, F
context.get('labor_status')           # EXCELLENT, GOOD, WARNING, CRITICAL, SEVERE
context.get('labor_metrics')          # LaborMetrics object
  .total_hours                        # Total hours worked
  .total_cost                         # Total labor cost
  .labor_percentage                   # Labor % (matches context)
  .grade                              # Grade letter
  .status                             # Status string
```

### Mapping Strategy

**Direct Mappings**:
- `date` → V4 `date`
- `restaurant` → V4 `restaurant_code`
- `revenue.gross_sales` → V4 `sales`
- `revenue.net_sales` → V4 `sales` (same for now)
- `expenses.labor.total` → V4 `labor_metrics.total_cost`
- `expenses.labor.percentage` → V4 `labor_percentage`
- `margins.labor_pct` → V4 `labor_percentage`
- `performance.labor_status` → V4 `labor_status` (lowercase)
- `performance.health_grade` → V4 `labor_grade`

**Calculated Fields**:
- `profit.operating` = `sales - labor_cost`
- `profit.net` = `profit.operating` (for now)
- `margins.operating_margin` = `(operating_profit / sales) * 100`

**Stub Fields** (V4 doesn't have yet):
- `expenses.cogs` → 0 (not tracking yet)
- `expenses.operating` → 0 (not tracking yet)
- `metrics.prime_cost` → `labor_cost` (no COGS data)
- `grade_info.breakdown` → Use labor grade only
- `grade_info.recommendations` → Generate from labor status

---

## V3 vs V4 Labor Calculation Discrepancy

### Issue

**Same Restaurant, Same Date, Different Results**:
- **V3**: SDR 2025-08-20 shows 71.76% labor
- **V4**: SDR 2025-08-20 shows 36.8% labor

### Possible Causes

1. **Different Source Files**
   - V3 might use different CSVs
   - V3 might aggregate multiple files
   - V3 might include additional costs

2. **Different Calculation**
   - V3: `labor% = (wages + ?) / sales`
   - V4: `labor% = total_labor_cost / sales`

3. **Data Quality**
   - V3 might have bad data
   - V4 might be missing costs
   - Different PayrollExport parsing

### Investigation Needed

**Action Items**:
1. Compare V3 and V4 source CSVs for Aug 20
2. Trace V3 calculation logic
3. Verify V4 PayrollExport parsing
4. Document authoritative calculation method

**Priority**: HIGH (blocking accurate dashboard integration)

---

## Next Steps

### Immediate (Week 5 Day 3)

1. **Investigate Labor Calculation Discrepancy** (1 hour)
   - Compare source data
   - Trace calculation logic
   - Document findings

2. **Create P&L JSON Exporter** (2 hours)
   - Map V4 → V3 format
   - Handle missing fields gracefully
   - Test with August data

3. **Test Dashboard Integration** (30 min)
   - Export V4 data
   - Generate dashboard
   - Verify visualizations

### Short-term (Week 5 Day 4)

1. **Deploy Supabase Schema** (1 hour)
2. **Implement SupabaseDatabaseClient** (2 hours)
3. **Write August Data to Supabase** (30 min)
4. **Create Test Suite** (1 hour)

### Medium-term (Week 5 Day 5)

1. **Extend V3 Dashboard for Supabase** (3 hours)
2. **Add Date Range Filtering** (1 hour)
3. **Deploy and Test** (1 hour)

---

## Questions for Jorge

1. **Dashboard Preference**:
   - Should we stick with file-based dashboard (Option A)?
   - Or invest in Supabase + new dashboard (Option B)?
   - Or hybrid (both during transition)?

2. **Labor Calculation**:
   - Is V3's 71.76% labor% correct?
   - Or is V4's 36.8% labor% correct?
   - Which calculation should be authoritative?

3. **Timeline**:
   - Need dashboard integration urgently?
   - Or can we take time for production solution?

4. **Features**:
   - What dashboard features are most important?
   - Date range filtering?
   - Trend charts?
   - Pattern confidence tracking?

---

## Conclusion

V3 uses a **file-based HTML dashboard** reading daily P&L JSON files. V4 can integrate by:

1. **Quick Path**: Export V4 data to V3 JSON format (2-3 hours)
2. **Production Path**: Deploy to Supabase + new dashboard (6-10 hours)

**Recommendation**: Start with quick integration to get immediate value, then migrate to Supabase for production excellence.

**Blocker**: Labor calculation discrepancy (V3: 71.76% vs V4: 36.8%) must be resolved first to ensure data accuracy.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
**Author**: System Architect
**Review Status**: Awaiting User Feedback
