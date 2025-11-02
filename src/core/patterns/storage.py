"""
Pattern Storage Protocol

Defines the interface for pattern persistence, allowing different
storage backends (in-memory, Supabase, Redis, etc.) without coupling
the Pattern Manager to a specific implementation.

Usage:
    from src.core.patterns.storage import PatternStorage
    from src.core.patterns.in_memory_storage import InMemoryPatternStorage

    # Use in-memory storage for testing
    storage: PatternStorage = InMemoryPatternStorage()

    # Or use Supabase for production
    storage: PatternStorage = SupabasePatternStorage(client)
"""

from typing import Protocol, Optional, List
from src.core import Result
from src.models.pattern import Pattern


class PatternStorage(Protocol):
    """
    Protocol defining pattern storage operations.

    This is a duck-typed interface (Protocol) rather than an abstract base class,
    allowing any object with matching methods to satisfy the interface.

    All methods return Result[T] to force explicit error handling.
    """

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
                - Failure with error if storage operation failed
        """
        ...

    def save_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Save a new pattern to storage.

        Args:
            pattern: Pattern to save

        Returns:
            Result[bool]:
                - Success with True if pattern saved
                - Failure with error if storage operation failed or pattern already exists
        """
        ...

    def update_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Update an existing pattern in storage.

        Args:
            pattern: Pattern to update

        Returns:
            Result[bool]:
                - Success with True if pattern updated
                - Failure with error if storage operation failed or pattern not found
        """
        ...

    def upsert_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Insert or update a pattern (save if new, update if exists).

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
                - Failure with error if storage operation failed
        """
        ...

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
                - Failure with error if storage operation failed
        """
        ...

    def clear_all(self) -> Result[bool]:
        """
        Clear all patterns from storage (for testing/reset).

        Returns:
            Result[bool]:
                - Success with True if all patterns cleared
                - Failure with error if storage operation failed
        """
        ...
