"""
Timeslot Pattern Manager

Manages learning and retrieval of timeslot performance patterns using exponential moving average.

Pattern Learning Algorithm:
- Alpha = 0.2 (20% weight to new observation, 80% to historical average)
- Confidence increases with each observation (capped at 1.0)
- Variance tracks standard deviation of fulfillment times

Storage:
- In-memory dictionary (Supabase integration deferred to Week 8)
- Patterns persisted in pipeline context for multi-day batch runs
"""

from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

from pipeline.models.timeslot_pattern import TimeslotPattern


class TimeslotPatternManager:
    """
    Manages learning and retrieval of timeslot performance patterns.

    Patterns are learned using exponential moving average with alpha=0.2,
    allowing recent observations to gradually update historical baselines
    while maintaining stability.
    """

    # Learning parameters
    LEARNING_RATE = 0.2  # Alpha for exponential moving average
    MIN_CONFIDENCE = 0.6  # Minimum confidence to use pattern
    MIN_OBSERVATIONS = 4  # Minimum observations to use pattern

    def __init__(self):
        """Initialize empty pattern storage."""
        self._patterns: Dict[str, TimeslotPattern] = {}

    def learn_pattern(
        self,
        restaurant_code: str,
        day_of_week: str,
        shift: str,
        time_window: str,
        category: str,
        fulfillment_time: float,
    ) -> TimeslotPattern:
        """
        Learn or update a pattern from a new observation.

        Uses exponential moving average to blend new observation with historical pattern:
        - New baseline = (alpha * new_time) + ((1 - alpha) * old_baseline)
        - Confidence increases with each observation (approaches 1.0)

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day name (e.g., 'Monday')
            shift: Shift name ('morning' or 'evening')
            time_window: 15-minute window (e.g., '11:00-11:15')
            category: Order category (e.g., 'Lobby')
            fulfillment_time: Observed fulfillment time in minutes

        Returns:
            Updated TimeslotPattern
        """
        pattern_key = TimeslotPattern.make_key(
            restaurant_code, day_of_week, shift, time_window, category
        )

        existing = self._patterns.get(pattern_key)

        if existing is None:
            # First observation - create new pattern
            new_pattern = TimeslotPattern(
                restaurant_code=restaurant_code,
                day_of_week=day_of_week,
                time_window=time_window,
                shift=shift,
                category=category,
                baseline_time=fulfillment_time,
                variance=0.0,  # No variance with single observation
                confidence=0.2,  # Low confidence with single observation
                observations_count=1,
                last_updated=datetime.now(),
            )
        else:
            # Update existing pattern with exponential moving average
            alpha = self.LEARNING_RATE
            new_baseline = (alpha * fulfillment_time) + ((1 - alpha) * existing.baseline_time)

            # Calculate variance (simple approach: track deviation from baseline)
            deviation = abs(fulfillment_time - new_baseline)
            new_variance = (alpha * deviation) + ((1 - alpha) * existing.variance)

            # Increase confidence with each observation (asymptotically approaches 1.0)
            new_observations = existing.observations_count + 1
            new_confidence = min(1.0, existing.confidence + (0.1 / (1 + existing.observations_count)))

            new_pattern = TimeslotPattern(
                restaurant_code=restaurant_code,
                day_of_week=day_of_week,
                time_window=time_window,
                shift=shift,
                category=category,
                baseline_time=new_baseline,
                variance=new_variance,
                confidence=new_confidence,
                observations_count=new_observations,
                last_updated=datetime.now(),
            )

        # Store updated pattern
        self._patterns[pattern_key] = new_pattern
        return new_pattern

    def get_pattern(
        self,
        restaurant_code: str,
        day_of_week: str,
        shift: str,
        time_window: str,
        category: str,
    ) -> Optional[TimeslotPattern]:
        """
        Retrieve a specific pattern.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day name
            shift: Shift name
            time_window: Time window
            category: Order category

        Returns:
            TimeslotPattern if exists, None otherwise
        """
        pattern_key = TimeslotPattern.make_key(
            restaurant_code, day_of_week, shift, time_window, category
        )
        return self._patterns.get(pattern_key)

    def get_patterns_for_day(
        self,
        restaurant_code: str,
        day_of_week: str,
        reliable_only: bool = True,
    ) -> Dict[str, Dict[str, Dict]]:
        """
        Get all patterns for a specific restaurant and day of week.

        Returns patterns organized by timeslot and category for easy lookup
        during grading.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day name (e.g., 'Monday')
            reliable_only: If True, only return reliable patterns (default: True)

        Returns:
            Dictionary structure:
            {
                'morning_11:00-11:15': {
                    'Lobby': {...},
                    'Drive-Thru': {...},
                    'ToGo': {...}
                },
                'evening_14:00-14:15': {
                    'Lobby': {...},
                    ...
                }
            }
        """
        result = defaultdict(dict)

        for pattern in self._patterns.values():
            # Filter by restaurant and day
            if pattern.restaurant_code != restaurant_code:
                continue
            if pattern.day_of_week != day_of_week:
                continue

            # Filter by reliability if requested
            if reliable_only and not pattern.is_reliable():
                continue

            # Create timeslot key: shift_timewindow (e.g., 'morning_11:00-11:15')
            timeslot_key = f"{pattern.shift}_{pattern.time_window}"

            # Store pattern dict under category
            result[timeslot_key][pattern.category] = {
                'baseline_time': pattern.baseline_time,
                'variance': pattern.variance,
                'confidence': pattern.confidence,
                'observations': pattern.observations_count,
            }

        return dict(result)

    def get_all_patterns(self) -> List[TimeslotPattern]:
        """
        Get all stored patterns.

        Returns:
            List of all TimeslotPattern objects
        """
        return list(self._patterns.values())

    def get_pattern_count(self, reliable_only: bool = False) -> int:
        """
        Get count of stored patterns.

        Args:
            reliable_only: If True, only count reliable patterns

        Returns:
            Number of patterns
        """
        if not reliable_only:
            return len(self._patterns)

        return sum(1 for p in self._patterns.values() if p.is_reliable())

    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about learned patterns.

        Returns:
            Dictionary with pattern statistics:
            - total_patterns: Total number of patterns
            - reliable_patterns: Number of reliable patterns
            - avg_confidence: Average confidence across all patterns
            - avg_observations: Average observation count
            - by_restaurant: Breakdown by restaurant
            - by_category: Breakdown by category
        """
        if not self._patterns:
            return {
                'total_patterns': 0,
                'reliable_patterns': 0,
                'avg_confidence': 0.0,
                'avg_observations': 0,
                'by_restaurant': {},
                'by_category': {},
            }

        patterns = list(self._patterns.values())
        reliable = [p for p in patterns if p.is_reliable()]

        # By restaurant
        by_restaurant = defaultdict(lambda: {'total': 0, 'reliable': 0})
        for pattern in patterns:
            by_restaurant[pattern.restaurant_code]['total'] += 1
            if pattern.is_reliable():
                by_restaurant[pattern.restaurant_code]['reliable'] += 1

        # By category
        by_category = defaultdict(lambda: {'total': 0, 'reliable': 0})
        for pattern in patterns:
            by_category[pattern.category]['total'] += 1
            if pattern.is_reliable():
                by_category[pattern.category]['reliable'] += 1

        return {
            'total_patterns': len(patterns),
            'reliable_patterns': len(reliable),
            'avg_confidence': statistics.mean(p.confidence for p in patterns),
            'avg_observations': statistics.mean(p.observations_count for p in patterns),
            'by_restaurant': dict(by_restaurant),
            'by_category': dict(by_category),
        }

    def load_patterns(self, patterns: List[TimeslotPattern]) -> None:
        """
        Load patterns from external source (e.g., previous pipeline run).

        Args:
            patterns: List of TimeslotPattern objects to load
        """
        for pattern in patterns:
            self._patterns[pattern.get_key()] = pattern

    def clear(self) -> None:
        """Clear all stored patterns."""
        self._patterns.clear()
