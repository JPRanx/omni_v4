# Guides & Tutorials

**Last Updated:** 2025-11-11
**Status:** Coming Soon

---

## Overview

This directory will contain user and developer guides for the OMNI V4 project, including:
- Getting started guides
- Configuration guides
- Deployment guides
- Troubleshooting guides

---

## Planned Guides

### Getting Started
- [ ] **GETTING_STARTED.md** (Coming Soon)
  - Project setup
  - Environment configuration
  - Running your first pipeline
  - Viewing the dashboard

### Configuration
- [ ] **CONFIGURATION_GUIDE.md** (Coming Soon)
  - YAML configuration structure
  - Environment overlays (dev, staging, prod)
  - Restaurant-specific configuration
  - Labor standards and thresholds

### Development
- [ ] **DEVELOPMENT_GUIDE.md** (Coming Soon)
  - Development environment setup
  - Code style and standards
  - Running tests
  - Adding new features

### Deployment
- [ ] **DEPLOYMENT_GUIDE.md** (Coming Soon)
  - Production deployment
  - Server configuration
  - Automated scheduling
  - Monitoring and alerts

### Troubleshooting
- [ ] **TROUBLESHOOTING.md** (Coming Soon)
  - Common issues and solutions
  - Debugging techniques
  - Error message reference
  - Performance optimization

---

## Quick Start (Temporary)

Until full guides are written, here's a quick start:

### Prerequisites
```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Run Pipeline
```bash
cd C:\Users\Jorge Alexander\omni_v4

# Single restaurant, single day
python scripts/run_date_range.py SDR 2025-08-20 2025-08-20 --verbose

# Multiple restaurants, date range
python scripts/run_date_range.py ALL 2025-08-20 2025-08-31 --output batch_results.json --verbose
```

### Generate Dashboard
```bash
# Generate dashboard data from batch results
python scripts/generate_dashboard_data.py batch_results.json

# Serve dashboard
python scripts/serve_dashboard.py
# Opens http://localhost:8080/index.html
```

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/ingestion/test_ingestion_stage.py

# With coverage
pytest --cov=src --cov-report=html
# View coverage: htmlcov/index.html
```

---

## Common Tasks

### Add New Restaurant
1. Add CSV data to `tests/fixtures/sample_data/YYYY-MM-DD/RESTAURANT_CODE/`
2. Create config file: `config/restaurants/RESTAURANT_CODE.yaml`
3. Run pipeline: `python scripts/run_date_range.py RESTAURANT_CODE ...`

### Update Labor Standards
Edit `config/base.yaml`:
```yaml
business_logic:
  labor:
    target_labor_percentage: 25.0
    warning_threshold: 30.0
    critical_threshold: 35.0
```

### Change Timeslot Duration
Edit `config/base.yaml`:
```yaml
timeslot:
  duration_minutes: 15
  slots_per_day: 64
```

---

## Documentation Needed

Help us improve documentation by contributing:

1. **Getting Started Guide**
   - Complete setup instructions
   - First-time user walkthrough
   - Common pitfalls and solutions

2. **Configuration Guide**
   - Detailed configuration reference
   - Examples for different scenarios
   - Best practices

3. **API Documentation**
   - Function/class reference
   - Usage examples
   - Integration patterns

4. **Deployment Guide**
   - Production setup checklist
   - Security considerations
   - Scaling recommendations

---

## Contributing

To add a new guide:

1. Create markdown file in `docs/guides/`
2. Use consistent formatting
3. Include code examples
4. Add to this README
5. Link from main documentation

---

## Related Documentation

- [Project Overview](../README.md)
- [Architecture Documentation](../architecture/README.md)
- [Analysis & Comparisons](../analysis/README.md)
- [Integration Documentation](../integration/README.md)

---

**Back to:** [Documentation Index](../README.md) | [Project Root](../../)