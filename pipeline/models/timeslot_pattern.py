"""
Timeslot Pattern Model

Represents historical performance patterns for specific timeslots, enabling adaptive grading
that accounts for restaurant-specific, time-specific, and category-specific performance baselines.

Pattern Key Format: {restaurant}_{day_of_week}_{shift}_{timeslot}_{category}
Example: SDR_Monday_morning_11:00-11:15_Lobby

Pattern Learning:
- Uses exponential moving average (alpha = 0.2) to adapt to changing conditions
- Tracks confidence based on observation count
- Requires minimum confidence (≥0.6) and observations (≥4) to be considered reliable
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class TimeslotPattern:
    """
    Historical pattern for a specific timeslot + category + day of week.

    This model captures learned performance baselines that enable adaptive grading.
    Patterns become more reliable as observation count increases.

    Attributes:
        restaurant_code: Restaurant identifier (e.g., 'SDR', 'T12')
        day_of_week: Day name (e.g., 'Monday', 'Tuesday')
        time_window: 15-minute window (e.g., '11:00-11:15')
        shift: Shift name ('morning' or 'evening')
        category: Order category ('Lobby', 'Drive-Thru', 'ToGo')
        baseline_time: Average fulfillment time in minutes (e.g., 12.3)
        variance: Acceptable variance in minutes (e.g., 2.1)
        confidence: Pattern reliability score 0.0-1.0
        observations_count: Number of data points used to learn this pattern
        last_updated: Timestamp of last pattern update
    """

    restaurant_code: str
    day_of_week: str
    time_window: str
    shift: str
    category: str
    baseline_time: float
    variance: float
    confidence: float
    observations_count: int
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pattern to dictionary for storage/export.

        Returns:
            Dictionary with all pattern fields, datetime as ISO string
        """
        return {
            'restaurant_code': self.restaurant_code,
            'day_of_week': self.day_of_week,
            'time_window': self.time_window,
            'shift': self.shift,
            'category': self.category,
            'baseline_time': round(self.baseline_time, 2),
            'variance': round(self.variance, 2),
            'confidence': round(self.confidence, 3),
            'observations_count': self.observations_count,
            'last_updated': self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeslotPattern':
        """
        Create pattern from dictionary.

        Args:
            data: Dictionary with pattern fields

        Returns:
            TimeslotPattern instance
        """
        return cls(
            restaurant_code=data['restaurant_code'],
            day_of_week=data['day_of_week'],
            time_window=data['time_window'],
            shift=data['shift'],
            category=data['category'],
            baseline_time=float(data['baseline_time']),
            variance=float(data['variance']),
            confidence=float(data['confidence']),
            observations_count=int(data['observations_count']),
            last_updated=datetime.fromisoformat(data['last_updated']),
        )

    def is_reliable(self, min_confidence: float = 0.6, min_observations: int = 4) -> bool:
        """
        Check if pattern is reliable enough to use for grading.

        A pattern is considered reliable when it has:
        1. Sufficient confidence (learned from enough variance in data)
        2. Sufficient observations (seen enough real-world examples)

        Args:
            min_confidence: Minimum confidence threshold (default: 0.6)
            min_observations: Minimum observation count (default: 4)

        Returns:
            True if pattern meets reliability criteria
        """
        return self.confidence >= min_confidence and self.observations_count >= min_observations

    @staticmethod
    def make_key(restaurant: str, day_of_week: str, shift: str, time_window: str, category: str) -> str:
        """
        Create unique pattern key from components.

        Args:
            restaurant: Restaurant code (e.g., 'SDR')
            day_of_week: Day name (e.g., 'Monday')
            shift: Shift name ('morning' or 'evening')
            time_window: Time window (e.g., '11:00-11:15')
            category: Category name (e.g., 'Lobby')

        Returns:
            Pattern key string (e.g., 'SDR_Monday_morning_11:00-11:15_Lobby')
        """
        return f"{restaurant}_{day_of_week}_{shift}_{time_window}_{category}"

    def get_key(self) -> str:
        """
        Get unique key for this pattern.

        Returns:
            Pattern key string
        """
        return self.make_key(
            self.restaurant_code,
            self.day_of_week,
            self.shift,
            self.time_window,
            self.category
        )
