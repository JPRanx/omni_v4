"""
Daily Labor Pattern - Daily aggregate labor cost patterns

This pattern type learns daily labor cost expectations:
- Labor percentage (labor cost / sales revenue)
- Total hours worked
- Patterns by day of week (Monday vs Friday differences)

This is NOT hourly patterns (that's HourlyServicePattern).
This is daily aggregates: "On Mondays, SDR typically has 28.5% labor cost."

Example:
    pattern = DailyLaborPattern.create(
        restaurant_code="SDR",
        day_of_week=0,  # Monday
        expected_labor_percentage=28.5,
        expected_total_hours=245.0,
        confidence=0.85,
        observations=12
    )

    # Pattern predicts:
    # "On Mondays at SDR, expect 28.5% labor cost with 245 total hours"

Architecture Note:
    This replaces the hack in PatternLearningStage where we were
    using Pattern(service_type="Lobby", hour=12) as a placeholder
    for daily patterns. Now we have a proper type.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from src.core import Result, ValidationError


@dataclass(frozen=True)
class DailyLaborPattern:
    """
    Immutable DTO for daily labor cost patterns.

    Dimensions (uniquely identify pattern):
    - restaurant_code: Which restaurant (SDR, T12, TK9)
    - day_of_week: Which day (0=Monday, 6=Sunday)

    Metrics (what pattern predicts):
    - expected_labor_percentage: Expected labor cost as % of sales
    - expected_total_hours: Expected total hours worked

    Quality (how reliable):
    - confidence: Pattern reliability (0.0-1.0)
    - observations: Number of data points used

    Metadata:
    - created_at: When first learned (ISO 8601)
    - last_updated: When last updated (ISO 8601)
    - metadata: Extensible dict for future use
    """

    # Dimensions
    restaurant_code: str
    day_of_week: int  # 0=Monday, 6=Sunday

    # Metrics
    expected_labor_percentage: float
    expected_total_hours: float

    # Quality
    confidence: float
    observations: int

    # Timestamps
    last_updated: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    # Extensible metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        restaurant_code: str,
        day_of_week: int,
        expected_labor_percentage: float,
        expected_total_hours: float,
        confidence: float,
        observations: int,
        last_updated: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result["DailyLaborPattern"]:
        """
        Create and validate DailyLaborPattern.

        Args:
            restaurant_code: Restaurant identifier (SDR, T12, TK9)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            expected_labor_percentage: Expected labor cost %
            expected_total_hours: Expected total hours worked
            confidence: Pattern confidence (0.0-1.0)
            observations: Number of observations
            last_updated: Last update timestamp (optional)
            created_at: Creation timestamp (optional)
            metadata: Additional metadata (optional)

        Returns:
            Result[DailyLaborPattern]: Success with pattern or failure with ValidationError
        """
        # Use provided timestamps or generate defaults
        if last_updated is None:
            last_updated = datetime.utcnow().isoformat()
        if created_at is None:
            created_at = datetime.utcnow().isoformat()

        pattern = DailyLaborPattern(
            restaurant_code=restaurant_code,
            day_of_week=day_of_week,
            expected_labor_percentage=expected_labor_percentage,
            expected_total_hours=expected_total_hours,
            confidence=confidence,
            observations=observations,
            last_updated=last_updated,
            created_at=created_at,
            metadata=metadata or {},
        )

        return pattern.validate()

    def validate(self) -> Result["DailyLaborPattern"]:
        """
        Validate DailyLaborPattern fields.

        Returns:
            Result[DailyLaborPattern]: Self if valid, ValidationError if invalid
        """
        # Validate restaurant code
        if not self.restaurant_code or not self.restaurant_code.strip():
            return Result.fail(
                ValidationError(
                    message="restaurant_code is required",
                    context={"field": "restaurant_code", "value": self.restaurant_code}
                )
            )

        # Validate day_of_week (0-6)
        if not isinstance(self.day_of_week, int) or self.day_of_week < 0 or self.day_of_week > 6:
            return Result.fail(
                ValidationError(
                    message="day_of_week must be an integer between 0 (Monday) and 6 (Sunday)",
                    context={"field": "day_of_week", "value": self.day_of_week}
                )
            )

        # Validate expected_labor_percentage (0-100)
        if self.expected_labor_percentage < 0 or self.expected_labor_percentage > 100:
            return Result.fail(
                ValidationError(
                    message="expected_labor_percentage must be between 0 and 100",
                    context={"field": "expected_labor_percentage", "value": self.expected_labor_percentage}
                )
            )

        # Validate expected_total_hours (non-negative)
        if self.expected_total_hours < 0:
            return Result.fail(
                ValidationError(
                    message="expected_total_hours must be non-negative",
                    context={"field": "expected_total_hours", "value": self.expected_total_hours}
                )
            )

        # Validate confidence (0.0-1.0)
        if not 0.0 <= self.confidence <= 1.0:
            return Result.fail(
                ValidationError(
                    message="confidence must be between 0.0 and 1.0",
                    context={"field": "confidence", "value": self.confidence}
                )
            )

        # Validate observations (non-negative integer)
        if not isinstance(self.observations, int) or self.observations < 0:
            return Result.fail(
                ValidationError(
                    message="observations must be a non-negative integer",
                    context={"field": "observations", "value": self.observations}
                )
            )

        return Result.ok(self)

    def get_pattern_type(self) -> str:
        """Get pattern type identifier."""
        return "daily_labor"

    def get_dimensions(self) -> Dict[str, Any]:
        """
        Get pattern dimensions for querying.

        Returns:
            Dict with restaurant_code, day_of_week, and pattern_type
        """
        return {
            "pattern_type": "daily_labor",
            "restaurant_code": self.restaurant_code,
            "day_of_week": self.day_of_week
        }

    def get_metrics(self) -> Dict[str, float]:
        """
        Get pattern metrics.

        Returns:
            Dict with labor_percentage and total_hours
        """
        return {
            "labor_percentage": self.expected_labor_percentage,
            "total_hours": self.expected_total_hours
        }

    def matches(self, **dimensions) -> bool:
        """
        Check if pattern matches given dimensions.

        Args:
            **dimensions: Dimension key-value pairs to match

        Returns:
            bool: True if pattern matches ALL provided dimensions
        """
        for key, value in dimensions.items():
            if key == "restaurant_code" and value != self.restaurant_code:
                return False
            if key == "day_of_week" and value != self.day_of_week:
                return False
            if key == "pattern_type" and value != "daily_labor":
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dict[str, Any]: Complete pattern data
        """
        return {
            "pattern_type": "daily_labor",
            "restaurant_code": self.restaurant_code,
            "day_of_week": self.day_of_week,
            "expected_labor_percentage": self.expected_labor_percentage,
            "expected_total_hours": self.expected_total_hours,
            "confidence": self.confidence,
            "observations": self.observations,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Result["DailyLaborPattern"]:
        """
        Deserialize from dictionary.

        Args:
            data: Pattern data

        Returns:
            Result[DailyLaborPattern]: Success with pattern or failure with ValidationError
        """
        try:
            return DailyLaborPattern.create(
                restaurant_code=data["restaurant_code"],
                day_of_week=data["day_of_week"],
                expected_labor_percentage=data["expected_labor_percentage"],
                expected_total_hours=data["expected_total_hours"],
                confidence=data["confidence"],
                observations=data["observations"],
                last_updated=data.get("last_updated"),
                created_at=data.get("created_at"),
                metadata=data.get("metadata", {}),
            )
        except KeyError as e:
            return Result.fail(
                ValidationError(
                    message=f"Missing required field: {e}",
                    context={"missing_field": str(e), "data": data}
                )
            )
        except Exception as e:
            return Result.fail(
                ValidationError(
                    message=f"DailyLaborPattern deserialization failed: {e}",
                    context={"error": str(e), "data": data}
                )
            )

    def get_key(self) -> str:
        """
        Get unique pattern key for storage/retrieval.

        Returns:
            str: Pattern key (restaurant_code:day_of_week)
        """
        return f"{self.restaurant_code}:daily_labor:{self.day_of_week}"

    def is_reliable(self, min_confidence: float = 0.6, min_observations: int = 10) -> bool:
        """
        Check if pattern is reliable enough to use.

        Args:
            min_confidence: Minimum confidence threshold (default: 0.6)
            min_observations: Minimum observations threshold (default: 10)

        Returns:
            bool: True if pattern meets reliability thresholds
        """
        return (
            self.confidence >= min_confidence and
            self.observations >= min_observations
        )

    def with_updated_prediction(
        self,
        new_labor_percentage: float,
        new_total_hours: float,
        learning_rate: float = 0.3
    ) -> "DailyLaborPattern":
        """
        Create new pattern with updated predictions using exponential moving average.

        Args:
            new_labor_percentage: New observed labor percentage
            new_total_hours: New observed total hours
            learning_rate: Learning rate for EMA (0.0-1.0)

        Returns:
            DailyLaborPattern: New pattern with updated predictions
        """
        updated_labor_pct = (
            (1 - learning_rate) * self.expected_labor_percentage +
            learning_rate * new_labor_percentage
        )
        updated_total_hours = (
            (1 - learning_rate) * self.expected_total_hours +
            learning_rate * new_total_hours
        )

        # Calculate new confidence (increases with more observations)
        # Confidence grows asymptotically towards 1.0
        new_observations = self.observations + 1
        new_confidence = min(1.0, 1.0 - (1.0 / (new_observations + 1)))

        # Create new pattern (frozen dataclass requires new instance)
        return DailyLaborPattern(
            restaurant_code=self.restaurant_code,
            day_of_week=self.day_of_week,
            expected_labor_percentage=updated_labor_pct,
            expected_total_hours=updated_total_hours,
            confidence=new_confidence,
            observations=new_observations,
            last_updated=datetime.utcnow().isoformat(),
            created_at=self.created_at,  # Preserve original creation time
            metadata=self.metadata,
        )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_name = days[self.day_of_week] if 0 <= self.day_of_week <= 6 else "???"

        return (
            f"DailyLaborPattern("
            f"restaurant={self.restaurant_code}, "
            f"day={day_name}, "
            f"labor_pct={self.expected_labor_percentage:.1f}%, "
            f"hours={self.expected_total_hours:.1f}, "
            f"conf={self.confidence:.2f}, "
            f"obs={self.observations})"
        )
