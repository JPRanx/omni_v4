"""
Daily Labor Pattern Storage Protocol

Defines the interface for daily labor pattern persistence.
Similar to PatternStorage but specialized for DailyLaborPattern.

Usage:
    from src.core.patterns.daily_labor_storage import DailyLaborPatternStorage
    from src.core.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage

    # Use in-memory storage for testing
    storage: DailyLaborPatternStorage = InMemoryDailyLaborPatternStorage()

    # Or use Supabase for production
    storage: DailyLaborPatternStorage = SupabaseDailyLaborPatternStorage(client)
"""

from typing import Protocol, Optional, List
from src.core import Result
from src.models.daily_labor_pattern import DailyLaborPattern


class DailyLaborPatternStorage(Protocol):
    """
    Protocol defining daily labor pattern storage operations.

    This is a duck-typed interface (Protocol) rather than an abstract base class,
    allowing any object with matching methods to satisfy the interface.

    All methods return Result[T] to force explicit error handling.
    """

    def get_pattern(
        self,
        restaurant_code: str,
        day_of_week: int
    ) -> Result[Optional[DailyLaborPattern]]:
        """
        Retrieve a daily labor pattern by its unique key.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day of week (0=Monday, 6=Sunday)

        Returns:
            Result[Optional[DailyLaborPattern]]:
                - Success with pattern if found
                - Success with None if not found
                - Failure with error if storage operation failed
        """
        ...

    def save_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Save a new daily labor pattern to storage.

        Args:
            pattern: Pattern to save

        Returns:
            Result[bool]:
                - Success with True if pattern saved
                - Failure with error if storage operation failed or pattern already exists
        """
        ...

    def update_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Update an existing daily labor pattern in storage.

        Args:
            pattern: Pattern to update

        Returns:
            Result[bool]:
                - Success with True if pattern updated
                - Failure with error if storage operation failed or pattern not found
        """
        ...

    def upsert_pattern(self, pattern: DailyLaborPattern) -> Result[bool]:
        """
        Insert or update a daily labor pattern (save if new, update if exists).

        Args:
            pattern: Pattern to upsert

        Returns:
            Result[bool]:
                - Success with True if pattern saved/updated
                - Failure with error if storage operation failed
        """
        ...

    def delete_pattern(
        self,
        restaurant_code: str,
        day_of_week: int
    ) -> Result[bool]:
        """
        Delete a daily labor pattern from storage.

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day of week

        Returns:
            Result[bool]:
                - Success with True if pattern deleted
                - Success with False if pattern not found
                - Failure with error if storage operation failed
        """
        ...

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
                - Success with list of patterns (empty list if none found)
                - Failure with error if storage operation failed
        """
        ...

    def clear_all(self) -> Result[bool]:
        """
        Clear all daily labor patterns from storage (for testing/reset).

        Returns:
            Result[bool]:
                - Success with True if all patterns cleared
                - Failure with error if storage operation failed
        """
        ...
