"""
InMemoryDatabaseClient

In-memory implementation of DatabaseClient protocol for testing.
No actual database operations - all data stored in dictionaries.
"""

from typing import Dict, List, Any
import uuid
from pipeline.services.result import Result
from pipeline.services.errors import DatabaseError


class InMemoryDatabaseClient:
    """
    In-memory database client for testing.

    Stores data in dictionaries and simulates transaction behavior.
    Thread-safe for single-threaded tests (not meant for production).
    """

    def __init__(self):
        """Initialize in-memory storage."""
        # Table name -> list of rows
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        # Transaction ID -> pending changes
        self.transactions: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        # Track active transactions
        self.active_transactions: set = set()

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
            # Initialize table if needed
            if table not in self.tables:
                self.tables[table] = []

            # Add row
            self.tables[table].append(data.copy())
            return Result.ok(1)

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
            # Initialize table if needed
            if table not in self.tables:
                self.tables[table] = []

            # Add all rows
            for row in data:
                self.tables[table].append(row.copy())

            return Result.ok(len(data))

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

        Returns:
            Result[str]: Transaction ID on success, error otherwise
        """
        try:
            # Generate unique transaction ID
            transaction_id = str(uuid.uuid4())

            # Initialize transaction storage (snapshot of current state)
            self.transactions[transaction_id] = {
                table: rows.copy() for table, rows in self.tables.items()
            }

            # Mark as active
            self.active_transactions.add(transaction_id)

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

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        try:
            # Check transaction exists
            if transaction_id not in self.active_transactions:
                return Result.fail(
                    DatabaseError(
                        f"Transaction {transaction_id} not found or already completed",
                        context={'transaction_id': transaction_id}
                    )
                )

            # Commit is a no-op in our simple implementation
            # (changes are already applied directly to self.tables)

            # Clean up transaction
            self.active_transactions.remove(transaction_id)
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]

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

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        try:
            # Check transaction exists
            if transaction_id not in self.active_transactions:
                return Result.fail(
                    DatabaseError(
                        f"Transaction {transaction_id} not found or already completed",
                        context={'transaction_id': transaction_id}
                    )
                )

            # Restore saved state from transaction start
            if transaction_id in self.transactions:
                self.tables = self.transactions[transaction_id].copy()

            # Clean up transaction
            self.active_transactions.remove(transaction_id)
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                DatabaseError(
                    f"Failed to rollback transaction: {str(e)}",
                    context={'transaction_id': transaction_id, 'error': str(e)}
                )
            )

    def get_table_data(self, table: str) -> List[Dict[str, Any]]:
        """
        Get all rows from a table (test helper method).

        Args:
            table: Table name

        Returns:
            List of rows (empty list if table doesn't exist)
        """
        return self.tables.get(table, []).copy()

    def get_row_count(self, table: str) -> int:
        """
        Get row count for a table (test helper method).

        Args:
            table: Table name

        Returns:
            Number of rows in table
        """
        return len(self.tables.get(table, []))

    def clear_all(self) -> None:
        """
        Clear all data (test helper method).

        Useful for test cleanup between test cases.
        """
        self.tables.clear()
        self.transactions.clear()
        self.active_transactions.clear()

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        table_counts = {table: len(rows) for table, rows in self.tables.items()}
        return f"InMemoryDatabaseClient(tables={table_counts})"
