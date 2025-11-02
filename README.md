# OMNI V4 - Restaurant Analytics Pipeline

**Version**: 4.0
**Status**: In Development
**Architecture**: Modular pipelines with 6x parallelization

## Overview

OMNI V4 is a complete rewrite of the restaurant analytics processing system, designed to fix architectural issues in V3 while enabling parallel processing for faster throughput.

### Key Improvements Over V3

- ✅ **6x Parallelization**: Process multiple restaurants and days simultaneously
- ✅ **Clean Architecture**: Separated pipelines (ingestion → processing → storage)
- ✅ **Configurable**: YAML-based configuration per restaurant
- ✅ **Testable**: Dependency injection and comprehensive test coverage
- ✅ **Resilient**: State tracking with retry logic and error handling
- ✅ **Observable**: Metrics, logging, and health checks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OMNI V4 Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Ingestion   │───▶│  Processing  │───▶│   Storage    │ │
│  │   Pipeline   │    │   Pipeline   │    │   Pipeline   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│       │                     │                    │         │
│   Toast CSV            Labor Analysis       Supabase      │
│   Validation           Efficiency Grading   Writes        │
│   Quality Checks       Pattern Learning                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
omni_v4/
├── src/
│   ├── pipelines/          # Core processing pipelines
│   │   ├── ingestion/      # Toast data loading & validation
│   │   ├── processing/     # Labor & efficiency analysis
│   │   └── storage/        # Database persistence
│   ├── core/               # Shared business logic
│   │   ├── models.py       # Data transfer objects
│   │   ├── patterns/       # Pattern learning (from V3)
│   │   └── grading/        # Grading logic (from V3)
│   ├── infrastructure/     # External dependencies
│   │   ├── database/       # Supabase, state tracking
│   │   ├── config/         # Configuration loader
│   │   └── observability/  # Metrics, logging
│   └── orchestration/      # Pipeline coordination
│       ├── pipeline_runner.py
│       └── parallel_executor.py
├── config/                 # YAML configuration
│   ├── base.yaml
│   ├── restaurants/        # Per-restaurant config
│   └── environments/       # dev/staging/prod
├── tests/
│   ├── unit/              # Component tests
│   ├── integration/       # Pipeline flow tests
│   ├── fixtures/          # Real Toast data samples
│   └── benchmarks/        # Performance tests
├── scripts/               # Operational scripts
│   └── run_pipeline.py    # CLI entry point
├── data/                  # Runtime data (gitignored)
│   ├── input/            # Toast exports
│   ├── state/            # Processing status
│   └── logs/
└── PROGRESS.md           # Development tracking
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Supabase credentials

# Run pipeline (dev mode)
python scripts/run_pipeline.py --env dev --date 2025-01-15

# Run tests
pytest tests/
```

## Development Status

See [PROGRESS.md](PROGRESS.md) for detailed implementation tracking.

## Migration from V3

OMNI V4 runs alongside V3 during transition:
- **Week 1-2**: Shadow mode (validate outputs)
- **Week 3-4**: Gradual migration (one restaurant at a time)
- **Week 5+**: Full migration, decommission V3

## Key Concepts

### Quality Levels
- **Level 1**: Basic metrics (sales, labor, COGS)
- **Level 2**: Labor analysis (overtime, auto-clockout)
- **Level 3**: Efficiency grading (timeslot analysis, patterns)

### Parallelization
- Process 6 concurrent tasks (2 days × 3 restaurants)
- Each task runs full pipeline (ingestion → processing → storage)
- Pattern updates queued and flushed asynchronously

### Configuration
- Base defaults in `config/base.yaml`
- Restaurant overrides in `config/restaurants/{code}.yaml`
- Environment-specific in `config/environments/{env}.yaml`

## Contact

For questions or issues, see V3 repository or contact system administrator.