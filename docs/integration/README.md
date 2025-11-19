# Integration Documentation

**Last Updated:** 2025-11-11
**Status:** ✅ V4 Dashboard Integration Working

---

## Overview

This directory contains all integration documentation for the OMNI V4 project, including:
- Dashboard integration status and architecture
- External system connections
- Data flow diagrams
- Integration troubleshooting

---

## Documents

### Dashboard Integration
- [V4_DASHBOARD_INTEGRATION_STATUS.md](V4_DASHBOARD_INTEGRATION_STATUS.md)
  - **Most Comprehensive** - Complete integration status
  - Two-project structure explanation
  - Integration flow documentation
  - V4 features vs V3 comparison
  - Recommendations and next steps

- [V4_DASHBOARD_INTEGRATION_COMPLETE.md](V4_DASHBOARD_INTEGRATION_COMPLETE.md)
  - Integration completion report
  - Working end-to-end flow
  - Generated data examples

- [V4_DASHBOARD_SOLUTION.md](V4_DASHBOARD_SOLUTION.md)
  - Technical solution architecture
  - Data transformation logic
  - Implementation details

### V3 Dashboard Analysis
- [V3_DASHBOARD_INTEGRATION_ANALYSIS.md](V3_DASHBOARD_INTEGRATION_ANALYSIS.md)
  - V3 dashboard connection analysis
  - Comparison with V4 approach
  - Historical context

---

## Integration Architecture

### V4 Backend → Dashboard Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Run V4 Pipeline                                     │
│  python scripts/run_date_range.py --start X --end Y         │
│  └─> Produces: outputs/pipeline_runs/batch_results.json    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Transform to Dashboard Format                      │
│  python scripts/generate_dashboard_data.py batch_results.json│
│  └─> Produces: dashboard/data/v4Data.js                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Serve Dashboard                                    │
│  python scripts/serve_dashboard.py                          │
│  └─> Opens: http://localhost:8080/index.html               │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure Clarification

### Two Separate Projects

**Project 1: restaurant_analytics_v3** (Legacy)
```
C:\Users\Jorge Alexander\restaurant_analytics_v3\
├── Modules/                    # V3 backend
├── DashboardV3/ipad/           # V3 frontend (development sandbox)
│   └── data/v4Data.js          # Mock data (modified Nov 6)
└── main_v3.py
```

**Project 2: omni_v4** (Current)
```
C:\Users\Jorge Alexander\omni_v4\
├── src/                        # V4 backend (43% complete)
├── scripts/
│   ├── run_date_range.py       # Pipeline executor
│   ├── generate_dashboard_data.py  # Data transformer
│   └── serve_dashboard.py      # HTTP server
├── dashboard/                  # V4 frontend (production)
│   └── data/v4Data.js          # Real V4 data (generated Nov 3)
└── outputs/
    └── pipeline_runs/
        └── batch_results.json  # Pipeline output
```

---

## Dashboard Versions

### Dashboard A: omni_v4/dashboard/ ✅
- **Location:** `C:\Users\Jorge Alexander\omni_v4\dashboard\`
- **Backend:** V4 (working)
- **Data:** Real V4 batch results
- **Status:** ✅ Fully integrated and operational
- **Access:** `python scripts/serve_dashboard.py` from omni_v4

### Dashboard B: restaurant_analytics_v3/DashboardV3/ipad/ ⚠️
- **Location:** `C:\Users\Jorge Alexander\restaurant_analytics_v3\DashboardV3\ipad\`
- **Backend:** None (mock data)
- **Data:** Hardcoded in v4Data.js
- **Status:** ⚠️ Disconnected, development/demo version
- **Purpose:** Frontend development sandbox

**Relationship:** Dashboard B is where frontend features are developed independently, then copied to Dashboard A when ready.

---

## Data Transformation

### V4 Pipeline Output Format
```json
{
  "restaurants": ["SDR", "T12", "TK9"],
  "start_date": "2025-08-20",
  "end_date": "2025-08-31",
  "pipeline_runs": [
    {
      "restaurant": "SDR",
      "date": "2025-08-20",
      "success": true,
      "labor_percentage": 24.8,
      "labor_cost": 15568.33,
      "sales": 62870.42,
      "service_mix": {
        "Lobby": 28.4,
        "Drive-Thru": 63.2,
        "ToGo": 8.4
      },
      "timeslot_metrics": { ... }
    }
  ]
}
```

### Dashboard Expected Format
```javascript
export const v4Data = {
  week1: {
    overview: {
      totalSales: 188611.26,
      totalLabor: 46706.98,
      laborPercent: 24.8,
      // ...
    },
    restaurants: [
      {
        id: "rest-sdr",
        name: "Sandra's Mexican Cuisine",
        sales: 62870.42,
        laborCost: 15568.33,
        laborPercent: 24.8,
        grade: "B",
        status: "excellent",
        serviceMix: { ... },
        dailyBreakdown: [ ... ],
        timeslotMetrics: { ... }
      }
    ]
  }
};
```

---

## External System Status

### Current Integrations

| System | Status | Purpose | Notes |
|--------|--------|---------|-------|
| **V4 Dashboard** | ✅ Working | Data visualization | Working since Nov 3 |
| **CSV Data Sources** | ✅ Working | Data ingestion | Toast POS exports |
| **In-Memory DB** | ✅ Working | Temporary storage | Current implementation |

### Planned Integrations

| System | Status | Priority | Timeline |
|--------|--------|----------|----------|
| **Supabase** | ⏸️ Pending | High | Week 8 (1-2 weeks) |
| **Real-time Alerts** | ❌ Not Started | Medium | Post-launch |
| **Mobile App** | ❌ Not Started | Low | Future |

---

## Integration Testing

### End-to-End Test Process

1. **Data Preparation**
   ```bash
   # Ensure test data exists
   ls tests/fixtures/sample_data/2025-08-20/SDR/
   ```

2. **Run Pipeline**
   ```bash
   cd C:\Users\Jorge Alexander\omni_v4
   python scripts/run_date_range.py SDR 2025-08-20 2025-08-31 --output test_batch.json --verbose
   ```

3. **Generate Dashboard Data**
   ```bash
   python scripts/generate_dashboard_data.py test_batch.json
   ```

4. **Serve & Verify**
   ```bash
   python scripts/serve_dashboard.py
   # Open browser to http://localhost:8080/index.html
   ```

5. **Validation**
   - Check labor % matches source CSV
   - Verify service mix percentages
   - Confirm timeslot metrics appear
   - Test all dashboard features

---

## Troubleshooting

### Common Issues

**Issue 1: Dashboard shows no data**
- **Cause:** v4Data.js not generated or empty
- **Fix:** Run `generate_dashboard_data.py` with valid batch_results.json
- **Check:** `cat dashboard/data/v4Data.js`

**Issue 2: Labor percentages seem wrong**
- **Cause:** Using V3 data (2x inflated)
- **Fix:** Ensure using V4 batch_results.json
- **Check:** Compare against source PayrollExport.csv

**Issue 3: Server won't start**
- **Cause:** Port 8080 already in use
- **Fix:** Use `--port 8081` flag or kill existing process
- **Check:** `netstat -ano | findstr 8080` (Windows)

**Issue 4: batch_results.json not found**
- **Cause:** File in old location (root instead of outputs/pipeline_runs/)
- **Fix:** Check outputs/pipeline_runs/ directory
- **Check:** `ls outputs/pipeline_runs/`

---

## Next Steps

### Week 7-8 Integration Tasks

1. **Supabase Integration** (Week 8)
   - Implement StorageStage with Supabase client
   - Create database schema
   - Test historical pattern queries
   - **Estimated:** 1-2 weeks

2. **Real-time Dashboard Updates** (Week 8)
   - WebSocket integration
   - Live data streaming
   - Auto-refresh on new data
   - **Estimated:** 3-5 days

3. **Production Deployment** (Week 8-9)
   - Host dashboard on production server
   - Schedule automated batch processing
   - Set up monitoring and alerts
   - **Estimated:** 1 week

---

## Related Documentation

- [Project Overview](../README.md)
- [Architecture Documentation](../architecture/README.md)
- [Analysis & Comparisons](../analysis/README.md)

---

**Back to:** [Documentation Index](../README.md) | [Project Root](../../)