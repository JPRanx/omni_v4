"""
DatabaseClient Protocol

Defines the interface for database operations used by StorageStage.
Follows protocol-based design for testability and flexibility.
"""

from typing import Protocol, Dict, List, Any
from pipeline.services.result import Result


class DatabaseClient(Protocol):
    """
    Protocol for database operations.

    All methods return Result[T] for consistent error handling.
    Implementations must support transactions for atomic operations.
    """

    def insert(self, table: str, data: Dict[str, Any]) -> Result[int]:
        """
        Insert a single row into a table.

        Args:
            table: Table name
            data: Dictionary of column names to values

        Returns:
            Result[int]: Number of rows inserted (1) on success, error otherwise
        """
        ...

    def insert_many(self, table: str, data: List[Dict[str, Any]]) -> Result[int]:
        """
        Insert multiple rows into a table.

        Args:
            table: Table name
            data: List of dictionaries (one per row)

        Returns:
            Result[int]: Number of rows inserted on success, error otherwise
        """
        ...

    def begin_transaction(self) -> Result[str]:
        """
        Begin a new database transaction.

        Returns:
            Result[str]: Transaction ID on success, error otherwise
        """
        ...

    def commit_transaction(self, transaction_id: str) -> Result[None]:
        """
        Commit a transaction.

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        ...

    def rollback_transaction(self, transaction_id: str) -> Result[None]:
        """
        Rollback a transaction.

        Args:
            transaction_id: Transaction ID from begin_transaction()

        Returns:
            Result[None]: Success or error
        """
        ...
