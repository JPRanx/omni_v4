"""
StorageResult DTO

Data Transfer Object for the storage pipeline output.
Follows immutability pattern (frozen dataclass).

Storage outputs:
- Database write confirmations
- Row counts per table
- Transaction IDs
- Storage timestamps

Usage:
    from src.models.storage_result import StorageResult
    from src.core import Result

    # Create from validation
    result = StorageResult.create(
        restaurant_code="SDR",
        business_date="2024-01-15",
        tables_written=["daily_performance", "timeslot_grading", "shift_assignments"],
        row_counts={"daily_performance": 1, "timeslot_grading": 150, "shift_assignments": 27}
    )

    if result.is_ok():
        dto = result.unwrap()
        checkpoint = dto.to_checkpoint()
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

from src.core import Result, ValidationError


@dataclass(frozen=True)
class StorageResult:
    """
    Immutable DTO representing storage pipeline output.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date (YYYY-MM-DD)

        # Storage summary
        tables_written: List of database tables written to
        row_counts: Dictionary mapping table name to row count
        transaction_id: Database transaction ID (optional)
        storage_timestamp: When storage completed (ISO 8601)

        # Status tracking
        success: Whether all storage operations succeeded
        errors: List of any errors encountered (even if recovered)
        metadata: Additional context (extensible)
    """

    # Required fields
    restaurant_code: str
    business_date: str
    tables_written: List[str]
    row_counts: Dict[str, int]

    # Optional tracking fields
    transaction_id: Optional[str] = None
    storage_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    # Status fields
    success: bool = True
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        restaurant_code: str,
        business_date: str,
        tables_written: List[str],
        row_counts: Dict[str, int],
        transaction_id: Optional[str] = None,
        success: bool = True,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result["StorageResult"]:
        """
        Create and validate StorageResult.

        Args:
            restaurant_code: Restaurant identifier
            business_date: Business date (YYYY-MM-DD)
            tables_written: List of database tables written
            row_counts: Row counts per table
            transaction_id: Database transaction ID
            success: Whether all operations succeeded
            errors: List of error messages
            metadata: Additional metadata

        Returns:
            Result[StorageResult]: Success with DTO or failure with ValidationError
        """
        dto = StorageResult(
            restaurant_code=restaurant_code,
            business_date=business_date,
            tables_written=tables_written,
            row_counts=row_counts,
            transaction_id=transaction_id,
            success=success,
            errors=errors or [],
            metadata=metadata or {},
        )

        return dto.validate()

    def validate(self) -> Result["StorageResult"]:
        """
        Validate DTO fields.

        Returns:
            Result[StorageResult]: Self if valid, ValidationError if invalid
        """
        # Validate restaurant code
        if not self.restaurant_code or not self.restaurant_code.strip():
            return Result.fail(
                ValidationError(
                    message="restaurant_code is required",
                    context={"field": "restaurant_code", "value": self.restaurant_code}
                )
            )

        # Validate business date format (YYYY-MM-DD)
        if not self._is_valid_date(self.business_date):
            return Result.fail(
                ValidationError(
                    message="business_date must be in YYYY-MM-DD format",
                    context={"field": "business_date", "value": self.business_date}
                )
            )

        # Validate tables_written is not empty
        if not self.tables_written or len(self.tables_written) == 0:
            return Result.fail(
                ValidationError(
                    message="tables_written must contain at least one table",
                    context={"field": "tables_written", "value": self.tables_written}
                )
            )

        # Validate row_counts is not empty
        if not self.row_counts or len(self.row_counts) == 0:
            return Result.fail(
                ValidationError(
                    message="row_counts must contain at least one entry",
                    context={"field": "row_counts", "value": self.row_counts}
                )
            )

        # Validate all row counts are non-negative
        for table, count in self.row_counts.items():
            if count < 0:
                return Result.fail(
                    ValidationError(
                        message=f"Row count for table '{table}' must be non-negative",
                        context={
                            "field": "row_counts",
                            "table": table,
                            "value": count
                        }
                    )
                )

        # Validate tables_written matches row_counts keys
        tables_set = set(self.tables_written)
        row_counts_set = set(self.row_counts.keys())

        if tables_set != row_counts_set:
            return Result.fail(
                ValidationError(
                    message="tables_written and row_counts must have matching tables",
                    context={
                        "tables_written": self.tables_written,
                        "row_counts_keys": list(self.row_counts.keys()),
                        "missing_from_row_counts": list(tables_set - row_counts_set),
                        "extra_in_row_counts": list(row_counts_set - tables_set)
                    }
                )
            )

        return Result.ok(self)

    def to_checkpoint(self) -> Dict[str, Any]:
        """
        Serialize to checkpoint dictionary (JSON-serializable).

        Returns:
            Dict[str, Any]: Checkpoint data
        """
        return {
            "restaurant_code": self.restaurant_code,
            "business_date": self.business_date,
            "tables_written": self.tables_written,
            "row_counts": self.row_counts,
            "transaction_id": self.transaction_id,
            "storage_timestamp": self.storage_timestamp,
            "success": self.success,
            "errors": self.errors,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_checkpoint(checkpoint: Dict[str, Any]) -> Result["StorageResult"]:
        """
        Deserialize from checkpoint dictionary.

        Args:
            checkpoint: Checkpoint data

        Returns:
            Result[StorageResult]: Success with DTO or failure with ValidationError
        """
        try:
            return StorageResult.create(
                restaurant_code=checkpoint["restaurant_code"],
                business_date=checkpoint["business_date"],
                tables_written=checkpoint["tables_written"],
                row_counts=checkpoint["row_counts"],
                transaction_id=checkpoint.get("transaction_id"),
                success=checkpoint.get("success", True),
                errors=checkpoint.get("errors", []),
                metadata=checkpoint.get("metadata", {}),
            )
        except KeyError as e:
            return Result.fail(
                ValidationError(
                    message=f"Missing required checkpoint field: {e}",
                    context={"missing_field": str(e), "checkpoint": checkpoint}
                )
            )
        except Exception as e:
            return Result.fail(
                ValidationError(
                    message=f"Checkpoint deserialization failed: {e}",
                    context={"error": str(e), "checkpoint": checkpoint}
                )
            )

    def save_checkpoint(self, checkpoint_path: str) -> Result[str]:
        """
        Save checkpoint to JSON file.

        Args:
            checkpoint_path: Path to save checkpoint

        Returns:
            Result[str]: Success with path or failure with CheckpointError
        """
        from src.core import CheckpointError

        try:
            path = Path(checkpoint_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            checkpoint = self.to_checkpoint()
            with open(path, "w") as f:
                json.dump(checkpoint, f, indent=2)

            return Result.ok(str(path))
        except Exception as e:
            return Result.fail(
                CheckpointError(
                    message=f"Failed to save checkpoint: {e}",
                    context={
                        "checkpoint_path": checkpoint_path,
                        "error": str(e)
                    }
                )
            )

    @staticmethod
    def load_checkpoint(checkpoint_path: str) -> Result["StorageResult"]:
        """
        Load checkpoint from JSON file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Result[StorageResult]: Success with DTO or failure with CheckpointError
        """
        from src.core import CheckpointError

        try:
            with open(checkpoint_path, "r") as f:
                checkpoint = json.load(f)

            return StorageResult.from_checkpoint(checkpoint)
        except FileNotFoundError:
            return Result.fail(
                CheckpointError(
                    message="Checkpoint file not found",
                    context={"checkpoint_path": checkpoint_path}
                )
            )
        except json.JSONDecodeError as e:
            return Result.fail(
                CheckpointError(
                    message=f"Invalid checkpoint JSON: {e}",
                    context={
                        "checkpoint_path": checkpoint_path,
                        "error": str(e)
                    }
                )
            )
        except Exception as e:
            return Result.fail(
                CheckpointError(
                    message=f"Failed to load checkpoint: {e}",
                    context={
                        "checkpoint_path": checkpoint_path,
                        "error": str(e)
                    }
                )
            )

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def get_total_rows(self) -> int:
        """Calculate total rows written across all tables."""
        return sum(self.row_counts.values())

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        total_rows = self.get_total_rows()
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"StorageResult("
            f"restaurant={self.restaurant_code}, "
            f"date={self.business_date}, "
            f"tables={len(self.tables_written)}, "
            f"rows={total_rows}, "
            f"status={status})"
        )
