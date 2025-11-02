"""
Supabase Pattern Storage Implementation

Implements PatternStorage protocol using Supabase (PostgreSQL) as backend.
Provides persistent storage for learned traffic and staffing patterns.

Usage:
    from supabase import create_client
    from src.infrastructure.storage import SupabasePatternStorage

    client = create_client(supabase_url, supabase_key)
    storage = SupabasePatternStorage(client)

    # Save pattern
    result = storage.save_pattern(pattern)

    # Retrieve pattern
    result = storage.get_pattern("SDR", "Lobby", 12, 1)
"""

from typing import Optional, List, Any, Dict
from datetime import datetime

from src.core import Result, PatternError, DatabaseError
from src.models.pattern import Pattern


class SupabasePatternStorage:
    """
    Supabase-backed pattern storage implementation.

    Implements PatternStorage protocol using Supabase PostgreSQL database.
    All operations return Result[T] for explicit error handling.

    Table: v4_patterns
    Schema: See schema/v4_patterns.sql

    Thread Safety: Thread-safe (Supabase client handles connection pooling)
    Performance: Target < 100ms for all operations
    """

    def __init__(self, client: Any, table_name: str = "v4_patterns"):
        """
        Initialize Supabase pattern storage.

        Args:
            client: Supabase client instance (from supabase.create_client())
            table_name: Name of patterns table (default: "v4_patterns")
        """
        self.client = client
        self.table_name = table_name

    def get_pattern(
        self,
        restaurant_code: str,
        service_type: str,
        hour: int,
        day_of_week: int
    ) -> Result[Optional[Pattern]]:
        """
        Retrieve a pattern by its unique key.

        Uses PRIMARY KEY index for fast lookup (< 10ms expected).

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type (Lobby, Drive-Thru, ToGo)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)

        Returns:
            Result[Optional[Pattern]]:
                - Success with Pattern if found
                - Success with None if not found
                - Failure with DatabaseError if query fails
        """
        try:
            # Query with composite primary key
            response = (
                self.client
                .table(self.table_name)
                .select("*")
                .eq("restaurant_code", restaurant_code)
                .eq("service_type", service_type)
                .eq("hour", hour)
                .eq("day_of_week", day_of_week)
                .execute()
            )

            # Check for database errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database query failed: {response.error}",
                        context={
                            "operation": "get_pattern",
                            "restaurant_code": restaurant_code,
                            "service_type": service_type,
                            "hour": hour,
                            "day_of_week": day_of_week,
                            "error": str(response.error)
                        }
                    )
                )

            # Parse response
            data = response.data
            if not data or len(data) == 0:
                return Result.ok(None)

            # Convert database row to Pattern
            row = data[0]
            pattern_result = self._row_to_pattern(row)

            if pattern_result.is_err():
                return pattern_result

            return Result.ok(pattern_result.unwrap())

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to get pattern: {e}",
                    context={
                        "operation": "get_pattern",
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

        Uses INSERT to enforce uniqueness constraint.

        Args:
            pattern: Pattern to save

        Returns:
            Result[bool]:
                - Success with True if pattern saved
                - Failure with DatabaseError if pattern already exists or insert fails
        """
        try:
            # Convert Pattern to database row
            row = self._pattern_to_row(pattern)

            # Insert (will fail if duplicate due to PRIMARY KEY constraint)
            response = (
                self.client
                .table(self.table_name)
                .insert(row)
                .execute()
            )

            # Check for errors (duplicate key, constraint violations, etc.)
            if hasattr(response, 'error') and response.error:
                error_msg = str(response.error)

                # Detect duplicate key error
                if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
                    return Result.fail(
                        PatternError(
                            message="Pattern already exists (use update_pattern or upsert_pattern)",
                            context={
                                "operation": "save_pattern",
                                "pattern_key": pattern.get_key(),
                                "restaurant_code": pattern.restaurant_code,
                                "service_type": pattern.service_type,
                                "hour": pattern.hour,
                                "day_of_week": pattern.day_of_week
                            }
                        )
                    )

                # Other database errors
                return Result.fail(
                    DatabaseError(
                        message=f"Database insert failed: {error_msg}",
                        context={"operation": "save_pattern", "error": error_msg}
                    )
                )

            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to save pattern: {e}",
                    context={
                        "operation": "save_pattern",
                        "pattern": pattern.to_dict(),
                        "error": str(e)
                    }
                )
            )

    def update_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Update an existing pattern in storage.

        Uses UPDATE with WHERE clause on primary key.

        Args:
            pattern: Pattern to update

        Returns:
            Result[bool]:
                - Success with True if pattern updated
                - Failure with PatternError if pattern not found
                - Failure with DatabaseError if update fails
        """
        try:
            # Convert Pattern to database row (exclude primary key fields from SET clause)
            row = self._pattern_to_row(pattern)

            # Remove primary key fields (they go in WHERE clause, not SET clause)
            update_data = {
                "expected_volume": row["expected_volume"],
                "expected_staffing": row["expected_staffing"],
                "confidence": row["confidence"],
                "observations": row["observations"],
                "last_updated": row["last_updated"],
                "metadata": row["metadata"]
            }

            # Update with composite primary key in WHERE clause
            response = (
                self.client
                .table(self.table_name)
                .update(update_data)
                .eq("restaurant_code", pattern.restaurant_code)
                .eq("service_type", pattern.service_type)
                .eq("hour", pattern.hour)
                .eq("day_of_week", pattern.day_of_week)
                .execute()
            )

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database update failed: {response.error}",
                        context={"operation": "update_pattern", "error": str(response.error)}
                    )
                )

            # Check if any rows were updated
            data = response.data
            if not data or len(data) == 0:
                return Result.fail(
                    PatternError(
                        message="Pattern not found (use save_pattern or upsert_pattern)",
                        context={
                            "operation": "update_pattern",
                            "pattern_key": pattern.get_key(),
                            "restaurant_code": pattern.restaurant_code,
                            "service_type": pattern.service_type,
                            "hour": pattern.hour,
                            "day_of_week": pattern.day_of_week
                        }
                    )
                )

            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to update pattern: {e}",
                    context={
                        "operation": "update_pattern",
                        "pattern": pattern.to_dict(),
                        "error": str(e)
                    }
                )
            )

    def upsert_pattern(self, pattern: Pattern) -> Result[bool]:
        """
        Insert or update a pattern (save if new, update if exists).

        Uses PostgreSQL UPSERT (INSERT ... ON CONFLICT DO UPDATE).

        Args:
            pattern: Pattern to upsert

        Returns:
            Result[bool]:
                - Success with True if pattern saved/updated
                - Failure with DatabaseError if operation fails
        """
        try:
            # Convert Pattern to database row
            row = self._pattern_to_row(pattern)

            # Upsert (INSERT ... ON CONFLICT ... DO UPDATE)
            response = (
                self.client
                .table(self.table_name)
                .upsert(row)
                .execute()
            )

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database upsert failed: {response.error}",
                        context={"operation": "upsert_pattern", "error": str(response.error)}
                    )
                )

            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to upsert pattern: {e}",
                    context={
                        "operation": "upsert_pattern",
                        "pattern": pattern.to_dict(),
                        "error": str(e)
                    }
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
                - Failure with DatabaseError if delete fails
        """
        try:
            # Delete with composite primary key
            response = (
                self.client
                .table(self.table_name)
                .delete()
                .eq("restaurant_code", restaurant_code)
                .eq("service_type", service_type)
                .eq("hour", hour)
                .eq("day_of_week", day_of_week)
                .execute()
            )

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database delete failed: {response.error}",
                        context={
                            "operation": "delete_pattern",
                            "restaurant_code": restaurant_code,
                            "service_type": service_type,
                            "hour": hour,
                            "day_of_week": day_of_week,
                            "error": str(response.error)
                        }
                    )
                )

            # Check if any rows were deleted
            data = response.data
            if not data or len(data) == 0:
                return Result.ok(False)  # Pattern didn't exist

            return Result.ok(True)  # Pattern deleted

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to delete pattern: {e}",
                    context={
                        "operation": "delete_pattern",
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

        Uses idx_patterns_restaurant or idx_patterns_service indexes.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Optional service type filter

        Returns:
            Result[List[Pattern]]:
                - Success with list of patterns (empty list if none found)
                - Failure with DatabaseError if query fails
        """
        try:
            # Build query
            query = (
                self.client
                .table(self.table_name)
                .select("*")
                .eq("restaurant_code", restaurant_code)
            )

            # Add service type filter if provided
            if service_type:
                query = query.eq("service_type", service_type)

            # Execute query
            response = query.execute()

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database query failed: {response.error}",
                        context={
                            "operation": "list_patterns",
                            "restaurant_code": restaurant_code,
                            "service_type": service_type,
                            "error": str(response.error)
                        }
                    )
                )

            # Convert rows to Patterns
            data = response.data
            if not data:
                return Result.ok([])

            patterns = []
            for row in data:
                pattern_result = self._row_to_pattern(row)

                if pattern_result.is_err():
                    # Log error but continue processing other patterns
                    # In production, might want to log this
                    continue

                patterns.append(pattern_result.unwrap())

            return Result.ok(patterns)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to list patterns: {e}",
                    context={
                        "operation": "list_patterns",
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "error": str(e)
                    }
                )
            )

    def clear_all(self) -> Result[bool]:
        """
        Clear all patterns from storage (for testing/reset).

        WARNING: This deletes ALL patterns for ALL restaurants.
        Use with caution!

        Returns:
            Result[bool]:
                - Success with True if all patterns cleared
                - Failure with DatabaseError if delete fails
        """
        try:
            # Delete all rows (no WHERE clause)
            response = (
                self.client
                .table(self.table_name)
                .delete()
                .neq("restaurant_code", "")  # Workaround: Supabase requires a filter
                .execute()
            )

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        message=f"Database delete failed: {response.error}",
                        context={"operation": "clear_all", "error": str(response.error)}
                    )
                )

            return Result.ok(True)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    message=f"Failed to clear all patterns: {e}",
                    context={"operation": "clear_all", "error": str(e)}
                )
            )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _pattern_to_row(self, pattern: Pattern) -> Dict[str, Any]:
        """
        Convert Pattern DTO to database row.

        Args:
            pattern: Pattern to convert

        Returns:
            Dictionary matching v4_patterns table schema
        """
        return {
            # Primary key
            "restaurant_code": pattern.restaurant_code,
            "service_type": pattern.service_type,
            "hour": pattern.hour,
            "day_of_week": pattern.day_of_week,

            # Predictions
            "expected_volume": pattern.expected_volume,
            "expected_staffing": pattern.expected_staffing,

            # Learning metadata
            "confidence": pattern.confidence,
            "observations": pattern.observations,

            # Timestamps
            "last_updated": pattern.last_updated,
            "created_at": pattern.created_at,

            # Extensibility
            "metadata": pattern.metadata or {}
        }

    def _row_to_pattern(self, row: Dict[str, Any]) -> Result[Pattern]:
        """
        Convert database row to Pattern DTO.

        Args:
            row: Database row dictionary

        Returns:
            Result[Pattern]:
                - Success with Pattern if conversion succeeds
                - Failure with PatternError if validation fails
        """
        try:
            # Extract and convert timestamps (Supabase returns ISO strings)
            last_updated = row.get("last_updated")
            created_at = row.get("created_at")

            # If timestamps are datetime objects, convert to ISO strings
            if isinstance(last_updated, datetime):
                last_updated = last_updated.isoformat()
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()

            # Create Pattern using factory method (includes validation)
            return Pattern.create(
                restaurant_code=row["restaurant_code"],
                service_type=row["service_type"],
                hour=row["hour"],
                day_of_week=row["day_of_week"],
                expected_volume=row["expected_volume"],
                expected_staffing=row["expected_staffing"],
                confidence=row["confidence"],
                observations=row["observations"],
                last_updated=last_updated,
                created_at=created_at,
                metadata=row.get("metadata", {})
            )

        except KeyError as e:
            return Result.fail(
                PatternError(
                    message=f"Missing required field in database row: {e}",
                    context={"row": row, "error": str(e)}
                )
            )
        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to convert row to pattern: {e}",
                    context={"row": row, "error": str(e)}
                )
            )
