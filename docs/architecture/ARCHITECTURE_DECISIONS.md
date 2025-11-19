# Architecture Decision Records (ADRs)

**OMNI V4 Restaurant Analytics System**

This document captures key architectural decisions made during development, the context behind them, and their implications for the system's evolution.

---

## Table of Contents

1. [ADR-001: Hybrid Pattern Model Design](#adr-001-hybrid-pattern-model-design)
2. [ADR-002: Structured Logging with Context Binding](#adr-002-structured-logging-with-context-binding)
3. [ADR-003: Protocol-Based Dependency Injection](#adr-003-protocol-based-dependency-injection)
4. [ADR-004: Result[T] Pattern for Error Handling](#adr-004-resultt-pattern-for-error-handling)
5. [ADR-005: Immutable DTOs with Frozen Dataclasses](#adr-005-immutable-dtos-with-frozen-dataclasses)

---

## ADR-001: Hybrid Pattern Model Design

**Date**: 2025-11-03 (Week 4 Day 7)
**Status**: Accepted
**Decision Makers**: System Architect

### Context

OMNI V4 initially used a single `Pattern` model designed for hourly service-specific patterns (restaurant, service_type, hour, day_of_week). However, our actual use case in Week 4 was learning **daily aggregate labor patterns** (restaurant, day_of_week only).

This mismatch forced us to use hacks:
- `service_type="Lobby"` as placeholder
- `hour=12` as placeholder
- `observed_volume` for labor_percentage
- `observed_staffing` for total_hours

This technical debt would accumulate and break when we added real hourly patterns in Week 5-6.

### Decision

Implement a **Hybrid Pattern Model** with three components:

1. **PatternProtocol** - Base protocol defining common interface
   - Methods: `get_pattern_type()`, `get_dimensions()`, `get_metrics()`, `matches()`, `to_dict()`, `validate()`
   - Runtime checkable for duck typing

2. **Specialized Pattern Types** - Type-safe concrete implementations
   - `DailyLaborPattern` - Daily aggregate labor patterns
     - Dimensions: `restaurant_code`, `day_of_week`
     - Metrics: `expected_labor_percentage`, `expected_total_hours`
   - `HourlyServicePattern` - Hourly service patterns (stub for future)
     - Dimensions: `restaurant_code`, `service_type`, `hour`, `day_of_week`
     - Metrics: `expected_volume`, `expected_staffing`

3. **Dedicated Managers & Storage** - One per pattern type
   - `DailyLaborPatternManager` with `DailyLaborPatternStorage`
   - `HourlyServicePatternManager` with `HourlyServicePatternStorage` (future)

### Consequences

**Positive:**
- ✅ **No Hacks** - Proper domain modeling, no workarounds
- ✅ **Type Safety** - mypy catches errors at compile time
- ✅ **Extensibility** - Adding new pattern types is straightforward
- ✅ **Maintainability** - Code is self-documenting
- ✅ **Future-Proof** - Ready for hourly patterns without refactoring

**Negative:**
- ⚠️ **More Code** - 6 new files (~1,200 lines) vs 0 if we kept the hack
- ⚠️ **Complexity** - Protocol + multiple implementations vs single class
- ⚠️ **Learning Curve** - New developers must understand protocol pattern

**Migration Path:**
- Old `Pattern` class remains for backward compatibility
- Old `PatternManager` remains for legacy code
- New code uses `DailyLaborPatternManager`
- Week 5-6: Implement `HourlyServicePatternManager`
- Week 7-8: Deprecate old `Pattern` class

### Alternatives Considered

**Option A: Keep the Hack** ❌
- Simplest short-term
- Accumulates technical debt
- Breaks when hourly patterns added

**Option B: Single Flexible Pattern** ❌
```python
class Pattern:
    pattern_type: str
    dimensions: Dict[str, Any]
    metrics: Dict[str, float]
```
- Flexible but loses type safety
- No compile-time validation
- Hard to query (JSON fields)

**Option C: Hybrid Approach** ✅ (Selected)
- Type-safe concrete types
- Protocol for polymorphism
- Best of both worlds

### References

- Implementation: `src/models/pattern_protocol.py`
- Implementation: `src/models/daily_labor_pattern.py`
- Implementation: `src/core/patterns/daily_labor_manager.py`
- Tests: `tests/integration/test_full_pipeline.py` (15/15 passing)

---

## ADR-002: Structured Logging with Context Binding

**Date**: 2025-11-03 (Week 4 Day 7)
**Status**: Accepted
**Decision Makers**: System Architect

### Context

OMNI V4 needed production-grade observability to:
1. Debug issues in production
2. Track performance across stages
3. Monitor business metrics (labor cost)
4. Alert on threshold breaches (labor > 35%)

Traditional print statements or basic logging were insufficient:
- No structure (hard to parse)
- No context (which restaurant? which date?)
- No performance tracking
- No business awareness

### Decision

Implement **Structured Logging with Context Binding**:

1. **StructuredLogger** - Wrapper around Python logging
   - Context binding: `.bind(restaurant="SDR", date="2025-10-20")`
   - Structured key-value pairs: `.info("event", key=value)`
   - Immutable binding (returns new logger)

2. **PipelineMetrics** - Metrics tracker
   - Counters: pipelines_started, pipelines_completed, pipelines_failed
   - Timers: stage_duration_ms (automatic with context manager)
   - Gauges: labor_percentage, files_processed, rows_written
   - Business metrics: labor_cost_alerts, patterns_learned

3. **Stage Instrumentation** - Log at key points
   - Start: Log event with inputs
   - End: Log event with outputs + duration
   - Errors: Log with context
   - Alerts: Escalate log level (WARNING for high labor)

### Consequences

**Positive:**
- ✅ **Structured Data** - Easy to parse, query, analyze
- ✅ **Context Everywhere** - Restaurant/date in every log
- ✅ **Performance Tracking** - Automatic timing
- ✅ **Business Awareness** - Logs understand business logic
- ✅ **Production-Ready** - Can pipe to Datadog, CloudWatch, Grafana
- ✅ **Zero Refactoring** - Drop-in replacement for print/logging

**Negative:**
- ⚠️ **Overhead** - Minimal (~1-2ms per log)
- ⚠️ **Verbosity** - More logs = more noise (can filter by level)

**Example Output:**
```
[INFO] [SDR] [2025-10-20] ingestion_started data_path=/path/to/data
[INFO] [SDR] [2025-10-20] ingestion_complete sales=3036.4 files=6 quality_level=1 duration_ms=106.0
[INFO] [SDR] [2025-10-20] processing_started
[WARNING] [SDR] [2025-10-20] processing_complete labor_pct=46.9 total_hours=179.8 status=SEVERE grade=F duration_ms=0.0
```

### Alternatives Considered

**Option A: Print Statements** ❌
- No structure, no context, not production-ready

**Option B: Standard Python Logging** ❌
- No structure, no context binding, manual formatting

**Option C: Third-Party Library (structlog, loguru)** ⚠️
- More features but external dependency
- Deferred for now (can migrate later)

**Option D: Structured Logger (Custom)** ✅ (Selected)
- Lightweight, no dependencies
- Integrated with standard logging
- Easy to upgrade to third-party later

### References

- Implementation: `src/infrastructure/logging/structured_logger.py`
- Implementation: `src/infrastructure/logging/pipeline_metrics.py`
- Usage: `src/processing/stages/ingestion_stage.py`
- Usage: `src/processing/stages/processing_stage.py`

---

## ADR-003: Protocol-Based Dependency Injection

**Date**: 2025-10-01 (Week 4 Day 1-3)
**Status**: Accepted
**Decision Makers**: System Architect

### Context

OMNI V4 needed to support multiple storage backends (InMemory for testing, Supabase for production) without coupling stages to specific implementations.

### Decision

Use **Python Protocols** (PEP 544) for dependency injection:

```python
class DatabaseClient(Protocol):
    def insert(self, table: str, data: dict) -> Result[int]: ...
    def begin_transaction(self) -> Result[str]: ...
    def commit_transaction(self, transaction_id: str) -> Result[None]: ...

# Implementations
class InMemoryDatabaseClient: ...
class SupabaseDatabaseClient: ...

# Usage (no inheritance required)
class StorageStage:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client
```

### Consequences

**Positive:**
- ✅ **Duck Typing** - No inheritance, just matching interface
- ✅ **Testability** - Easy to mock/stub
- ✅ **Flexibility** - Swap implementations without changing code
- ✅ **Type Safety** - mypy validates protocol compliance

**Negative:**
- ⚠️ **Runtime Checks** - Protocol violations detected at runtime (with `@runtime_checkable`)

### References

- `src.infrastructure.database.database_client.DatabaseClient`
- `src.core.patterns.storage.PatternStorage`
- `src.ingestion.data_source.DataSource`

---

## ADR-004: Result[T] Pattern for Error Handling

**Date**: 2025-10-01 (Week 4 Day 1)
**Status**: Accepted
**Decision Makers**: System Architect

### Context

Python's exception-based error handling is implicit and hard to track. OMNI V4 needed explicit, composable error handling.

### Decision

Implement **Result[T] Monad** (Rust-inspired):

```python
# Success
result = Result.ok(42)
if result.is_ok():
    value = result.unwrap()

# Failure
result = Result.fail(ValueError("Error"))
if result.is_err():
    error = result.unwrap_err()
```

### Consequences

**Positive:**
- ✅ **Explicit** - Caller must check is_ok/is_err
- ✅ **Composable** - Chain operations with .and_then()
- ✅ **Type Safe** - mypy enforces error handling
- ✅ **No Exceptions** - Predictable control flow

**Negative:**
- ⚠️ **Verbosity** - More code than try/except
- ⚠️ **Learning Curve** - Unfamiliar to Python developers

### References

- Implementation: `src/core/result.py`
- Usage: Every stage's `execute()` method returns `Result[PipelineContext]`

---

## ADR-005: Immutable DTOs with Frozen Dataclasses

**Date**: 2025-10-01 (Week 4 Day 1)
**Status**: Accepted
**Decision Makers**: System Architect

### Context

Mutable data structures cause bugs (unexpected mutations, hard-to-debug side effects). OMNI V4 needed immutable data transfer objects.

### Decision

Use **Frozen Dataclasses** for all DTOs:

```python
@dataclass(frozen=True)
class LaborMetrics:
    total_hours: float
    labor_cost: float
    labor_percentage: float
    status: str
    grade: str
```

### Consequences

**Positive:**
- ✅ **Thread-Safe** - No mutation = no race conditions
- ✅ **Predictable** - Data doesn't change unexpectedly
- ✅ **Hashable** - Can use as dict keys
- ✅ **Fast** - No defensive copying

**Negative:**
- ⚠️ **Immutable** - Must create new instances for updates (by design)

### References

- `src.models.labor_dto.LaborDTO`
- `src.models.pattern.Pattern`
- `src.models.daily_labor_pattern.DailyLaborPattern`
- `src.processing.labor_calculator.LaborMetrics`

---

## Summary

These architectural decisions form the foundation of OMNI V4's design:

1. **Hybrid Pattern Model** - Type-safe, extensible pattern types
2. **Structured Logging** - Production-grade observability
3. **Protocol-Based DI** - Flexible, testable dependency injection
4. **Result[T] Pattern** - Explicit, composable error handling
5. **Frozen Dataclasses** - Immutable, thread-safe DTOs

Together, they create a system that is:
- **Type-Safe** - Caught at compile time
- **Testable** - Easy to mock and verify
- **Observable** - Clear insight into behavior
- **Maintainable** - Easy to understand and modify
- **Extensible** - Ready for future requirements

---

**Last Updated**: 2025-11-03
**Document Owner**: System Architect
**Review Cycle**: After major architectural changes
