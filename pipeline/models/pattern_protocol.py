"""
Pattern Protocol - Base interface for all pattern types

Defines the protocol that all pattern types must implement,
enabling polymorphic storage and retrieval while maintaining
type safety for specific pattern implementations.

This is the foundation of the Hybrid Pattern Model:
- PatternProtocol: Base protocol (flexible interface)
- DailyLaborPattern: Daily aggregate labor patterns
- HourlyServicePattern: Hourly service-specific patterns (future)

Architecture:
    Protocol-based polymorphism allows storage layer to handle
    all pattern types uniformly, while concrete implementations
    provide type-safe field access and validation.

Usage:
    from pipeline.models.pattern_protocol import PatternProtocol
    from pipeline.models.daily_labor_pattern import DailyLaborPattern

    # Concrete type for type safety
    pattern: DailyLaborPattern = DailyLaborPattern.create(...)

    # Protocol type for storage polymorphism
    storage.save_pattern(pattern)  # Accepts any PatternProtocol
"""

from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class PatternProtocol(Protocol):
    """
    Protocol that all pattern types must implement.

    This enables:
    1. Type-safe concrete implementations (DailyLaborPattern, etc.)
    2. Polymorphic storage (PatternStorage accepts any PatternProtocol)
    3. Uniform querying (all patterns have dimensions/metrics)

    Pattern Identity:
    - restaurant_code: Which restaurant this pattern belongs to
    - Pattern-specific dimensions (time, service type, etc.)

    Pattern Quality:
    - confidence: How reliable is this pattern (0.0-1.0)
    - observations: How many data points used to learn it

    Pattern Metadata:
    - created_at: When pattern was first learned (ISO 8601)
    - last_updated: When pattern was last updated (ISO 8601)
    """

    # Required fields for all patterns
    restaurant_code: str
    confidence: float
    observations: int
    created_at: str
    last_updated: str

    def get_pattern_type(self) -> str:
        """
        Get pattern type identifier.

        Used for:
        - Storage table routing (daily_labor_patterns vs hourly_service_patterns)
        - Deserialization (know which concrete class to instantiate)
        - Querying (filter by pattern type)

        Returns:
            str: Pattern type (e.g., "daily_labor", "hourly_service")
        """
        ...

    def get_dimensions(self) -> Dict[str, Any]:
        """
        Get pattern dimensions for querying.

        Dimensions are the "coordinates" that uniquely identify a pattern:
        - DailyLaborPattern: {"restaurant_code", "day_of_week"}
        - HourlyServicePattern: {"restaurant_code", "service_type", "hour", "day_of_week"}

        Used for:
        - Pattern lookup (find pattern matching these dimensions)
        - Pattern uniqueness (two patterns with same dimensions = same pattern)
        - Fallback chains (find similar patterns)

        Returns:
            Dict[str, Any]: Dimension key-value pairs
        """
        ...

    def get_metrics(self) -> Dict[str, float]:
        """
        Get pattern metrics (the actual predictions/expectations).

        Metrics are what the pattern predicts:
        - DailyLaborPattern: {"labor_percentage", "total_hours"}
        - HourlyServicePattern: {"expected_volume", "expected_staffing"}

        Used for:
        - Pattern comparison (how different are two patterns?)
        - Metric retrieval (what does this pattern predict?)
        - Dashboard display (show key metrics)

        Returns:
            Dict[str, float]: Metric name -> value mapping
        """
        ...

    def matches(self, **dimensions) -> bool:
        """
        Check if pattern matches given dimensions.

        Used for:
        - Filtering patterns (find all patterns for Monday)
        - Pattern lookup (does this pattern match my query?)
        - Fallback logic (find similar patterns)

        Args:
            **dimensions: Dimension key-value pairs to match

        Returns:
            bool: True if pattern matches ALL provided dimensions

        Examples:
            pattern.matches(restaurant_code="SDR")  # True if SDR pattern
            pattern.matches(day_of_week=0)  # True if Monday pattern
            pattern.matches(restaurant_code="SDR", day_of_week=0)  # True if SDR Monday
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize pattern to dictionary.

        Used for:
        - Database storage (convert to row dict)
        - JSON serialization (API responses)
        - Debugging (human-readable representation)

        Returns:
            Dict[str, Any]: Complete pattern data
        """
        ...

    def validate(self) -> "Result[PatternProtocol]":
        """
        Validate pattern fields.

        Each concrete pattern type implements its own validation:
        - DailyLaborPattern: Validates labor_percentage, day_of_week
        - HourlyServicePattern: Validates hour, service_type

        Returns:
            Result[PatternProtocol]: Self if valid, ValidationError if invalid
        """
        ...
