# OMNI V4 Documentation

**Last Updated:** 2025-11-11
**Project Status:** Week 7 Day 3 Complete (43% V3 feature parity)

---

## Quick Links

- [Architecture Documentation](architecture/) - Design patterns, DTOs, pipeline architecture
- [Analysis Documentation](analysis/) - V3/V4 comparisons, data audits, gap analysis
- [Integration Documentation](integration/) - Dashboard integration, external systems
- [Guides](guides/) - Setup, configuration, deployment guides (coming soon)

---

## Root Documentation

### Project Overview
- [CONSOLIDATION_SUMMARY.md](CONSOLIDATION_SUMMARY.md) - High-level project summary
- [REORGANIZATION_PROPOSAL.md](REORGANIZATION_PROPOSAL.md) - Directory structure reorganization plan

---

## Documentation Structure

```
docs/
├── README.md                     # This file
├── CONSOLIDATION_SUMMARY.md      # Project overview
├── REORGANIZATION_PROPOSAL.md    # Folder reorganization plan
├── architecture/                 # Design & architecture docs
│   ├── README.md
│   └── ARCHITECTURE_DECISIONS.md
├── analysis/                     # V3/V4 analysis & audits
│   ├── README.md
│   ├── CRITICAL_FINDING_V3_LABOR_DISCREPANCY.md
│   ├── V3_VS_V4_FEATURE_GAP_ANALYSIS.md
│   ├── V4_DATA_AUDIT_COMPLETE.md
│   └── V4_DATA_AUDIT_REPORT.md
├── integration/                  # Integration documentation
│   ├── README.md
│   ├── V3_DASHBOARD_INTEGRATION_ANALYSIS.md
│   ├── V4_DASHBOARD_INTEGRATION_COMPLETE.md
│   ├── V4_DASHBOARD_INTEGRATION_STATUS.md
│   └── V4_DASHBOARD_SOLUTION.md
└── guides/                       # User & developer guides
    └── README.md
```

---

## Finding Documentation

### Architecture & Design
For information about V4 pipeline architecture, DTOs, patterns, and design decisions:
→ [architecture/README.md](architecture/README.md)

### Analysis & Comparisons
For V3 vs V4 feature comparisons, data audits, and discrepancy findings:
→ [analysis/README.md](analysis/README.md)

### Integration & External Systems
For dashboard integration, Supabase, and external system connections:
→ [integration/README.md](integration/README.md)

### Setup & Configuration
For getting started, configuration, and deployment guides:
→ [guides/README.md](guides/README.md)

---

## Daily Progress Logs

Historical development progress logs have been moved to:
→ [../archive/daily_logs/](../archive/daily_logs/)

Current active development progress:
→ [../PROGRESS.md](../PROGRESS.md)

---

## Contributing Documentation

When adding new documentation:

1. **Architecture docs** → `docs/architecture/`
   - Design patterns, DTOs, pipeline stages
   - Technical architecture decisions
   - Code structure and organization

2. **Analysis docs** → `docs/analysis/`
   - Feature comparisons (V3 vs V4)
   - Data audits and validation
   - Performance analysis
   - Gap analysis

3. **Integration docs** → `docs/integration/`
   - Dashboard integration
   - External system connections (Supabase, APIs)
   - Data flow diagrams
   - Integration status reports

4. **Guides** → `docs/guides/`
   - Getting started guides
   - Configuration guides
   - Deployment guides
   - Troubleshooting guides

---

## Documentation Standards

- Use Markdown format (.md)
- Include date and status in header
- Add clear section headings
- Use code blocks for examples
- Include links to related docs
- Update this index when adding new docs

---

**Project Root:** [../](../)
**Source Code:** [../src/](../src/)
**Tests:** [../tests/](../tests/)
**Scripts:** [../scripts/](../scripts/)