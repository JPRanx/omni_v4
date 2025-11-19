# Architecture Documentation

**Last Updated:** 2025-11-11
**Status:** Week 7 Day 3 Complete

---

## Overview

This directory contains all architectural design documentation for the OMNI V4 project, including:
- Pipeline architecture and stage design
- Data Transfer Objects (DTOs)
- Design patterns and principles
- Architectural decision records (ADRs)

---

## Documents

### Architecture Decisions
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)
  - Core architectural decisions
  - Result[T] pattern for error handling
  - Pipeline stage abstraction
  - Dependency injection patterns
  - Configuration system design

---

## V4 Pipeline Architecture

### Stage-Based Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      PipelineContext                         │
│  (Shared state, configuration, restaurant code, date)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Ingestion                                         │
│  - Load CSVs (Sales, Payroll, Orders)                      │
│  - Validate data (L1: fatal, L2: quality)                  │
│  - Extract raw dataframes                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Order Categorization                              │
│  - Parse order CSV                                          │
│  - Categorize orders (Lobby/Drive-Thru/ToGo)              │
│  - Calculate service mix percentages                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Timeslot Grading                                  │
│  - Window data into 15-min timeslots (64 per day)         │
│  - Grade each timeslot vs standards                         │
│  - Detect hot/cold streaks                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Processing                                        │
│  - Calculate labor metrics (cost, %, grade)                │
│  - Extract cash flow data                                   │
│  - Compute overtime hours/costs                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Pattern Learning                                  │
│  - Learn daily labor patterns                               │
│  - Learn timeslot patterns                                  │
│  - Update pattern storage                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 6: Storage                                           │
│  - Store results in database (in-memory or Supabase)       │
│  - Return row counts and storage confirmation              │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Design Patterns

### 1. Result[T] Pattern
Functional error handling without exceptions:
```python
from src.core.result import Result

def calculate(value: float) -> Result[float]:
    if value < 0:
        return Result.fail(ValueError("Value must be positive"))
    return Result.ok(value * 2)
```

### 2. Pipeline Stage Abstraction
All stages implement the `Stage` protocol:
```python
class Stage(Protocol):
    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        ...
```

### 3. Dependency Injection
Components receive dependencies through constructors:
```python
class ProcessingStage:
    def __init__(self, calculator: LaborCalculator):
        self._calculator = calculator
```

---

## Data Transfer Objects (DTOs)

### LaborDTO
```python
@dataclass
class LaborDTO:
    restaurant_code: str
    business_date: str
    total_hours_worked: float
    total_labor_cost: float
    employee_count: int
    # ... additional fields
```

### ProcessingResult
```python
@dataclass
class ProcessingResult:
    labor_percentage: float
    labor_grade: str
    overtime_hours: float
    # ... additional fields
```

---

## Key Architectural Principles

1. **Separation of Concerns**
   - Each stage has a single responsibility
   - Clear boundaries between components

2. **Testability**
   - Dependency injection enables easy mocking
   - Pure functions where possible
   - Result[T] makes error handling explicit

3. **Configurability**
   - YAML-based configuration system
   - Environment overlays (dev, staging, prod)
   - Restaurant-specific overrides

4. **Type Safety**
   - Comprehensive type hints
   - DTOs for data transfer
   - Protocol-based interfaces

5. **Error Handling**
   - Result[T] pattern for all operations
   - No silent failures
   - Explicit error propagation

---

## Related Documentation

- [Project Overview](../README.md)
- [Analysis & Comparisons](../analysis/README.md)
- [Integration Documentation](../integration/README.md)

---

**Back to:** [Documentation Index](../README.md) | [Project Root](../../)