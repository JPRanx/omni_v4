"""
SupabaseDatabaseClient

Supabase implementation of DatabaseClient protocol.
Uses Supabase Python client for database operations.
"""

from typing import Dict, List, Any, Optional
import os
import uuid
from src.core.result import Result
from src.core.errors import DatabaseError


class SupabaseDatabaseClient:
    """
    Supabase database client implementation.

    Connects to Supabase PostgreSQL database and provides
    insert and transaction operations.

    Note: Transaction support in Supabase is limited. This implementation
    uses a simplified approach suitable for our use case.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        """
        Initialize Supabase client.

        Args:
            supabase_url: Supabase project URL (defaults to SUPABASE_URL env var)
            supabase_key: Supabase API key (defaults to SUPABASE_KEY env var)

        Raises:
            DatabaseError: If connection parameters are missing
        """
        # Get connection parameters from environment if not provided
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')

        if not self.supabase_url:
            raise DatabaseError(
                "Missing Supabase URL. Set SUPABASE_URL environment variable.",
                context={'env_var': 'SUPABASE_URL'}
            )

        if not self.supabase_key:
            raise DatabaseError(
                "Missing Supabase key. Set SUPABASE_KEY environment variable.",
                context={'env_var': 'SUPABASE_KEY'}
            )

        # Initialize Supabase client (lazy - only when needed)
        self._client = None
        self._pending_operations: Dict[str, List[tuple]] = {}

    def _get_client(self):
        """
        Get or create Supabase client.

        Returns:
            Supabase client instance

        Raises:
            DatabaseError: If client initialization fails
        """
        if self._client is None:
            try:
                from supabase import create_client, Client
                self._client: Client = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                raise DatabaseError(
                    "Supabase Python client not installed. Run: pip install supabase",
                    context={'package': 'supabase'}
                )
            except Exception as e:
                raise DatabaseError(
                    f"Failed to initialize Supabase client: {str(e)}",
                    context={'error': str(e)}
                )

        return self._client

    def insert(self, table: str, data: Dict[str, Any]) -> Result[int]:
        """
        Insert a single row into a table.

        Args:
            table: Table name
            data: Dictionary of column names to values

        Returns:
            Result[int]: Number of rows inserted (1) on success, error otherwise
        """
        try:
            client = self._get_client()

            # Execute insert
            response = client.table(table).insert(data).execute()

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        f"Insert failed: {response.error}",
                        context={'table': table, 'error': str(response.error)}
                    )
                )

            return Result.ok(1)

        except DatabaseError:
            # Re-raise DatabaseError as-is
            raise
        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to insert row into {table}: {str(e)}",
                    context={'table': table, 'error': str(e)}
                )
            )

    def insert_many(self, table: str, data: List[Dict[str, Any]]) -> Result[int]:
        """
        Insert multiple rows into a table.

        Args:
            table: Table name
            data: List of dictionaries (one per row)

        Returns:
            Result[int]: Number of rows inserted on success, error otherwise
        """
        try:
            if not data:
                return Result.ok(0)

            client = self._get_client()

            # Execute batch insert
            response = client.table(table).insert(data).execute()

            # Check for errors
            if hasattr(response, 'error') and response.error:
                return Result.fail(
                    DatabaseError(
                        f"Batch insert failed: {response.error}",
                        context={
                            'table': table,
                            'row_count': len(data),
                            'error': str(response.error)
                        }
                    )
                )

            return Result.ok(len(data))

        except DatabaseError:
            # Re-raise DatabaseError as-is
            raise
        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to insert rows into {table}: {str(e)}",
                    context={'table': table, 'row_count': len(data), 'error': str(e)}
                )
            )

    def begin_transaction(self) -> Result[str]:
        """
        Begin a new database transaction.

        Note: Supabase REST API has limited transaction support.
        This implementation uses a queue to batch operations and
        execute them atomically via PostgreSQL stored procedures in the future.

        For now, we return a transaction ID and queue operations.

        Returns:
            Result[str]: Transaction ID on success, error otherwise
        """
        try:
            # Generate unique transaction ID
            transaction_id = str(uuid.uuid4())

            # Initialize operation queue for this transaction
            self._pending_operations[transaction_id] = []

            return Result.ok(transaction_id)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to begin transaction: {str(e)}",
                    context={'error': str(e)}
                )
            )

    def commit_transaction(self, transaction_id: str) -> Result[None]:
        """
        Commit a transaction.

        Note: In this simplified implementation, operations are executed
        immediately (not queued), so commit is mostly a cleanup operation.

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        try:
            # Check transaction exists
            if transaction_id not in self._pending_operations:
                return Result.fail(
                    DatabaseError(
                        f"Transaction {transaction_id} not found",
                        context={'transaction_id': transaction_id}
                    )
                )

            # Clean up transaction
            del self._pending_operations[transaction_id]

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to commit transaction: {str(e)}",
                    context={'transaction_id': transaction_id, 'error': str(e)}
                )
            )

    def rollback_transaction(self, transaction_id: str) -> Result[None]:
        """
        Rollback a transaction.

        Note: In this simplified implementation, we cannot truly rollback
        already-executed operations. This is a known limitation of using
        Supabase REST API. For production use, consider PostgreSQL
        stored procedures or direct PostgreSQL connection with psycopg2.

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        try:
            # Check transaction exists
            if transaction_id not in self._pending_operations:
                return Result.fail(
                    DatabaseError(
                        f"Transaction {transaction_id} not found",
                        context={'transaction_id': transaction_id}
                    )
                )

            # Clean up transaction (we cannot rollback already-executed operations)
            del self._pending_operations[transaction_id]

            # Log warning about limited rollback support
            # In production, this should use proper logging
            # For now, we just return success

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to rollback transaction: {str(e)}",
                    context={'transaction_id': transaction_id, 'error': str(e)}
                )
            )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"SupabaseDatabaseClient(url={self.supabase_url})"
