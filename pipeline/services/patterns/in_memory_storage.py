"""
In-Memory Pattern Storage

Simple dictionary-based pattern storage for testing and development.
Not suitable for production (no persistence, not thread-safe).

Usage:
    from pipeline.services.patterns.in_memory_storage import InMemoryPatternStorage

    storage = InMemoryPatternStorage()

    # Save a pattern
    result = storage.save_pattern(pattern)

    # Retrieve a pattern
    result = storage.get_pattern("SDR", "Lobby", 12, 1)
"""

from typing import Optional, List, Dict
from pipeline.services import Result, PatternError
from pipeline.models.pattern import Pattern


class InMemoryPatternStorage:
    """
    In-memory pattern storage using dictionary.

    Patterns are stored in memory using pattern key as dictionary key.
    All data is lost when the instance is destroyed.

    Thread Safety: NOT thread-safe. For testing only.
    Persistence: NO persistence. For testing only.
    """

    def __init__(self):
        """Initialize empty pattern storage."""
        self._patterns: Dict[str, Pattern] = {}

    def get_pattern(
        self,
        restaurant_code: str,
        service_type: str,
        hour: int,
        day_of_week: int
    ) -> Result[Optional[Pattern]]:
        """
        Retrieve a pattern by its unique key.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type (Lobby, Drive-Thru, ToGo)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)

        Returns:
            Result[Optional[Pattern]]:
                - Success with Pattern if found
                - Success with None if not found
                - Failure should never occur (no I/O errors in memory)
        """
        try:
            # Create temporary pattern just to get the key
            temp_pattern = Pattern(
                restaurant_code=restaurant_code,
                service_type=service_type,
                hour=hour,
                day_of_week=day_of_week,
                expected_volume=0.0,
                expected_staffing=0.0,
                confidence=0.0,
                observations=0
            )
            key = temp_pattern.get_key()

            pattern = self._patterns.get(key)
            return Result.ok(pattern)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to retrieve pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def save_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Save a new pattern to storage.

        Args:
            pattern: Pattern to save

        Returns:
            Result[bool]:
                - Success with True if pattern saved
                - Failure if pattern already exists
        """
        try:
            key = pattern.get_key()

            if key in self._patterns:
                return Result.fail(
                    PatternError(
                        message="Pattern already exists (use update_pattern or upsert_pattern)",
                        context={
                            "pattern_key": key,
                            "restaurant_code": pattern.restaurant_code,
                            "service_type": pattern.service_type,
                            "hour": pattern.hour,
                            "day_of_week": pattern.day_of_week
                        }
                    )
                )

            self._patterns[key] = pattern
            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to save pattern: {e}",
                    context={"error": str(e), "pattern": pattern.to_dict()}
                )
            )

    def update_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Update an existing pattern in storage.

        Args:
            pattern: Pattern to update

        Returns:
            Result[bool]:
                - Success with True if pattern updated
                - Failure if pattern not found
        """
        try:
            key = pattern.get_key()

            if key not in self._patterns:
                return Result.fail(
                    PatternError(
                        message="Pattern not found (use save_pattern or upsert_pattern)",
                        context={
                            "pattern_key": key,
                            "restaurant_code": pattern.restaurant_code,
                            "service_type": pattern.service_type,
                            "hour": pattern.hour,
                            "day_of_week": pattern.day_of_week
                        }
                    )
                )

            self._patterns[key] = pattern
            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to update pattern: {e}",
                    context={"error": str(e), "pattern": pattern.to_dict()}
                )
            )

    def upsert_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Insert or update a pattern (save if new, update if exists).

        Args:
            pattern: Pattern to upsert

        Returns:
            Result[bool]:
                - Success with True if pattern saved/updated
                - Failure should never occur for in-memory storage
        """
        try:
            key = pattern.get_key()
            self._patterns[key] = pattern
            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to upsert pattern: {e}",
                    context={"error": str(e), "pattern": pattern.to_dict()}
                )
            )

    def delete_pattern(
        self,
        restaurant_code: str,
        service_type: str,
        hour: int,
        day_of_week: int
    ) -> Result[bool]:
        """
        Delete a pattern from storage.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type
            hour: Hour of day
            day_of_week: Day of week

        Returns:
            Result[bool]:
                - Success with True if pattern deleted
                - Success with False if pattern not found
        """
        try:
            # Create temporary pattern just to get the key
            temp_pattern = Pattern(
                restaurant_code=restaurant_code,
                service_type=service_type,
                hour=hour,
                day_of_week=day_of_week,
                expected_volume=0.0,
                expected_staffing=0.0,
                confidence=0.0,
                observations=0
            )
            key = temp_pattern.get_key()

            if key in self._patterns:
                del self._patterns[key]
                return Result.ok(True)
            else:
                return Result.ok(False)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to delete pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def list_patterns(
        self,
        restaurant_code: str,
        service_type: Optional[str] = None
    ) -> Result[List[Pattern]]:
        """
        List all patterns for a restaurant, optionally filtered by service type.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Optional service type filter

        Returns:
            Result[List[Pattern]]:
                - Success with list of patterns (empty list if none found)
        """
        try:
            patterns = [
                p for p in self._patterns.values()
                if p.restaurant_code == restaurant_code
            ]

            if service_type:
                patterns = [
                    p for p in patterns
                    if p.service_type == service_type
                ]

            return Result.ok(patterns)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to list patterns: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "error": str(e)
                    }
                )
            )

    def clear_all(self) -> Result[bool]:
        """
        Clear all patterns from storage (for testing/reset).

        Returns:
            Result[bool]:
                - Success with True if all patterns cleared
        """
        try:
            self._patterns.clear()
            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to clear all patterns: {e}",
                    context={"error": str(e)}
                )
            )

    def count(self) -> int:
        """
        Get the number of patterns in storage (helper for testing).

        Returns:
            int: Number of patterns
        """
        return len(self._patterns)
