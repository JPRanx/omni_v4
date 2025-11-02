"""
Pattern DTO

Data Transfer Object for traffic and staffing patterns.
Patterns are learned from historical data and used to predict future needs.

Pattern Types:
- Traffic Patterns: Expected customer volume by hour/service type
- Staffing Patterns: Expected labor needs by hour/service type

Usage:
    from src.models.pattern import Pattern
    from src.core import Result

    # Create traffic pattern
    result = Pattern.create(
        restaurant_code="SDR",
        service_type="Lobby",
        hour=12,
        day_of_week=1,
        expected_volume=85.5,
        expected_staffing=3.2,
        confidence=0.75,
        observations=120
    )

    if result.is_ok():
        pattern = result.unwrap()
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from src.core import Result, ValidationError


class ServiceType(Enum):
    """Service type enumeration."""
    LOBBY = "Lobby"
    DRIVE_THRU = "Drive-Thru"
    TO_GO = "ToGo"


@dataclass(frozen=True)
class Pattern:
    """
    Immutable DTO representing a learned traffic/staffing pattern.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        service_type: Service type (Lobby, Drive-Thru, ToGo)
        hour: Hour of day (0-23)
        day_of_week: Day of week (0=Monday, 6=Sunday)

        # Pattern predictions
        expected_volume: Expected customer volume (checks/hour)
        expected_staffing: Expected staffing need (employees)

        # Pattern reliability
        confidence: Pattern confidence (0.0-1.0)
        observations: Number of observations used to learn pattern

        # Metadata
        last_updated: When pattern was last updated (ISO 8601)
        created_at: When pattern was first created (ISO 8601)
        metadata: Additional context (extensible)
    """

    # Required identification fields
    restaurant_code: str
    service_type: str
    hour: int
    day_of_week: int

    # Pattern predictions
    expected_volume: float
    expected_staffing: float

    # Pattern reliability
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
        service_type: str,
        hour: int,
        day_of_week: int,
        expected_volume: float,
        expected_staffing: float,
        confidence: float,
        observations: int,
        last_updated: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result["Pattern"]:
        """
        Create and validate Pattern.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type (Lobby, Drive-Thru, ToGo)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            expected_volume: Expected customer volume
            expected_staffing: Expected staffing need
            confidence: Pattern confidence (0.0-1.0)
            observations: Number of observations
            last_updated: Last update timestamp (optional)
            created_at: Creation timestamp (optional)
            metadata: Additional metadata (optional)

        Returns:
            Result[Pattern]: Success with Pattern or failure with ValidationError
        """
        # Use provided timestamps or generate defaults
        if last_updated is None:
            last_updated = datetime.utcnow().isoformat()
        if created_at is None:
            created_at = datetime.utcnow().isoformat()

        pattern = Pattern(
            restaurant_code=restaurant_code,
            service_type=service_type,
            hour=hour,
            day_of_week=day_of_week,
            expected_volume=expected_volume,
            expected_staffing=expected_staffing,
            confidence=confidence,
            observations=observations,
            last_updated=last_updated,
            created_at=created_at,
            metadata=metadata or {},
        )

        return pattern.validate()

    def validate(self) -> Result["Pattern"]:
        """
        Validate Pattern fields.

        Returns:
            Result[Pattern]: Self if valid, ValidationError if invalid
        """
        # Validate restaurant code
        if not self.restaurant_code or not self.restaurant_code.strip():
            return Result.fail(
                ValidationError(
                    message="restaurant_code is required",
                    context={"field": "restaurant_code", "value": self.restaurant_code}
                )
            )

        # Validate service type
        valid_service_types = ["Lobby", "Drive-Thru", "ToGo"]
        if self.service_type not in valid_service_types:
            return Result.fail(
                ValidationError(
                    message=f"service_type must be one of: {', '.join(valid_service_types)}",
                    context={
                        "field": "service_type",
                        "value": self.service_type,
                        "valid_types": valid_service_types
                    }
                )
            )

        # Validate hour (0-23)
        if not isinstance(self.hour, int) or self.hour < 0 or self.hour > 23:
            return Result.fail(
                ValidationError(
                    message="hour must be an integer between 0 and 23",
                    context={"field": "hour", "value": self.hour}
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

        # Validate expected_volume (non-negative)
        if self.expected_volume < 0:
            return Result.fail(
                ValidationError(
                    message="expected_volume must be non-negative",
                    context={"field": "expected_volume", "value": self.expected_volume}
                )
            )

        # Validate expected_staffing (non-negative)
        if self.expected_staffing < 0:
            return Result.fail(
                ValidationError(
                    message="expected_staffing must be non-negative",
                    context={"field": "expected_staffing", "value": self.expected_staffing}
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary (for database storage or JSON).

        Returns:
            Dict[str, Any]: Pattern data
        """
        return {
            "restaurant_code": self.restaurant_code,
            "service_type": self.service_type,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
            "expected_volume": self.expected_volume,
            "expected_staffing": self.expected_staffing,
            "confidence": self.confidence,
            "observations": self.observations,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Result["Pattern"]:
        """
        Deserialize from dictionary.

        Args:
            data: Pattern data

        Returns:
            Result[Pattern]: Success with Pattern or failure with ValidationError
        """
        try:
            return Pattern.create(
                restaurant_code=data["restaurant_code"],
                service_type=data["service_type"],
                hour=data["hour"],
                day_of_week=data["day_of_week"],
                expected_volume=data["expected_volume"],
                expected_staffing=data["expected_staffing"],
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
                    message=f"Pattern deserialization failed: {e}",
                    context={"error": str(e), "data": data}
                )
            )

    def get_key(self) -> str:
        """
        Get unique pattern key for storage/retrieval.

        Returns:
            str: Pattern key (restaurant_code:service_type:hour:day_of_week)
        """
        return f"{self.restaurant_code}:{self.service_type}:{self.hour}:{self.day_of_week}"

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
        new_volume: float,
        new_staffing: float,
        learning_rate: float = 0.3
    ) -> "Pattern":
        """
        Create new Pattern with updated predictions using exponential moving average.

        Args:
            new_volume: New observed volume
            new_staffing: New observed staffing
            learning_rate: Learning rate for exponential moving average (0.0-1.0)

        Returns:
            Pattern: New pattern with updated predictions
        """
        updated_volume = (
            (1 - learning_rate) * self.expected_volume +
            learning_rate * new_volume
        )
        updated_staffing = (
            (1 - learning_rate) * self.expected_staffing +
            learning_rate * new_staffing
        )

        # Calculate new confidence (increases with more observations)
        # Confidence grows asymptotically towards 1.0
        new_observations = self.observations + 1
        new_confidence = min(1.0, 1.0 - (1.0 / (new_observations + 1)))

        # Create new pattern (frozen dataclass requires new instance)
        return Pattern(
            restaurant_code=self.restaurant_code,
            service_type=self.service_type,
            hour=self.hour,
            day_of_week=self.day_of_week,
            expected_volume=updated_volume,
            expected_staffing=updated_staffing,
            confidence=new_confidence,
            observations=new_observations,
            last_updated=datetime.utcnow().isoformat(),
            created_at=self.created_at,  # Preserve original creation time
            metadata=self.metadata,
        )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Pattern("
            f"restaurant={self.restaurant_code}, "
            f"service={self.service_type}, "
            f"hour={self.hour}, "
            f"dow={self.day_of_week}, "
            f"vol={self.expected_volume:.1f}, "
            f"staff={self.expected_staffing:.1f}, "
            f"conf={self.confidence:.2f}, "
            f"obs={self.observations})"
        )
