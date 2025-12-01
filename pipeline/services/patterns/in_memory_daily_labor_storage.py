"""
In-Memory Daily Labor Pattern Storage

Fast, non-persistent storage for testing and development.
Stores patterns in a dictionary keyed by (restaurant_code, day_of_week).

Thread Safety: NOT thread-safe (use locks if needed in production)

Usage:
    from pipeline.services.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage

    storage = InMemoryDailyLaborPatternStorage()

    # Save pattern
    pattern = DailyLaborPattern.create(...)
    storage.save_pattern(pattern)

    # Retrieve pattern
    result = storage.get_pattern("SDR", 0)  # Monday
"""

from typing import Dict, Optional, List, Tuple

from pipeline.services import Result, PatternError
from pipeline.models.daily_labor_pattern import DailyLaborPattern


class InMemoryDailyLaborPatternStorage:
    """
    In-memory storage for daily labor patterns.

    Implements DailyLaborPatternStorage protocol using a dictionary.
    Fast and deterministic, perfect for testing.

    Storage Format:
        {
            ("SDR", 0): DailyLaborPattern(...),  # SDR Monday
            ("SDR", 1): DailyLaborPattern(...),  # SDR Tuesday
            ("T12", 0): DailyLaborPattern(...),  # T12 Monday
            ...
        }
    """

    def __init__(self):
        """Initialize empty storage."""
        self._patterns: Dict[Tuple[str, int], DailyLaborPattern] = {}

    def get_pattern(
        self,
        restaurant_code: str,
        day_of_week: int
    ) -> Result[Optional[DailyLaborPattern]]:
        """
        Retrieve a daily labor pattern by key.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day of week (0-6)

        Returns:
            Result[Optional[DailyLaborPattern]]:
                - Success with pattern if found
                - Success with None if not found
                - Never fails (in-memory storage doesn't have I/O errors)
        """
        key = (restaurant_code, day_of_week)
        pattern = self._patterns.get(key)
        return Result.ok(pattern)

    def save_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Save a new daily labor pattern.

        Args:
            pattern: Pattern to save

        Returns:
            Result[bool]:
                - Success with True if pattern saved
                - Failure with PatternError if pattern already exists
        """
        key = (pattern.restaurant_code, pattern.day_of_week)

        if key in self._patterns:
            return Result.fail(
                PatternError(
                    message="Daily labor pattern already exists (use update_pattern or upsert_pattern)",
                    context={
                        "restaurant_code": pattern.restaurant_code,
                        "day_of_week": pattern.day_of_week,
                        "operation": "save"
                    }
                )
            )

        self._patterns[key] = pattern
        return Result.ok(True)

    def update_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Update an existing daily labor pattern.

        Args:
            pattern: Pattern to update

        Returns:
            Result[bool]:
                - Success with True if pattern updated
                - Failure with PatternError if pattern not found
        """
        key = (pattern.restaurant_code, pattern.day_of_week)

        if key not in self._patterns:
            return Result.fail(
                PatternError(
                    message="Daily labor pattern not found (use save_pattern or upsert_pattern)",
                    context={
                        "restaurant_code": pattern.restaurant_code,
                        "day_of_week": pattern.day_of_week,
                        "operation": "update"
                    }
                )
            )

        self._patterns[key] = pattern
        return Result.ok(True)

    def upsert_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Insert or update a daily labor pattern.

        Args:
            pattern: Pattern to upsert

        Returns:
            Result[bool]:
                - Success with True if pattern saved/updated
                - Never fails (in-memory storage doesn't have I/O errors)
        """
        key = (pattern.restaurant_code, pattern.day_of_week)
        self._patterns[key] = pattern
        return Result.ok(True)

    def delete_pattern(
        self,
        restaurant_code: str,
        day_of_week: int
    ) -> Result[bool]:
        """
        Delete a daily labor pattern.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day of week

        Returns:
            Result[bool]:
                - Success with True if pattern deleted
                - Success with False if pattern not found
                - Never fails (in-memory storage doesn't have I/O errors)
        """
        key = (restaurant_code, day_of_week)

        if key in self._patterns:
            del self._patterns[key]
            return Result.ok(True)
        else:
            return Result.ok(False)

    def list_patterns(
        self,
        restaurant_code: str
    ) -> Result[List[DailyLaborPattern]]:
        """
        List all daily labor patterns for a restaurant.

        Args:
            restaurant_code: Restaurant identifier

        Returns:
            Result[List[DailyLaborPattern]]:
                - Success with list of patterns (empty if none found)
                - Never fails (in-memory storage doesn't have I/O errors)
        """
        patterns = [
            pattern for (rest_code, _), pattern in self._patterns.items()
            if rest_code == restaurant_code
        ]
        return Result.ok(patterns)

    def clear_all(self) -> Result[bool]:
        """
        Clear all daily labor patterns from storage.

        Returns:
            Result[bool]:
                - Success with True (always succeeds)
                - Never fails (in-memory storage doesn't have I/O errors)
        """
        self._patterns.clear()
        return Result.ok(True)

    def __len__(self) -> int:
        """Get total number of patterns in storage."""
        return len(self._patterns)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"InMemoryDailyLaborPatternStorage(patterns={len(self._patterns)})"
