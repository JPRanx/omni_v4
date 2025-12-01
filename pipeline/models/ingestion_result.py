"""
IngestionResult DTO

Data Transfer Object for the ingestion pipeline output.
Follows immutability pattern (frozen dataclass) and references file paths
instead of embedding large data.

Quality Levels:
    L1 (Basic): Toast data + basic validation
    L2 (Labor): L1 + employee data + timeslots
    L3 (Efficiency): L2 + efficiency metrics + advanced analysis

Usage:
    from pipeline.models.ingestion_result import IngestionResult
    from pipeline.services import Result

    # Create from validation
    result = IngestionResult.create(
        restaurant_code="SDR",
        business_date="2024-01-15",
        toast_data_path="/data/SDR_2024-01-15_toast.parquet",
        quality_level=1
    )

    if result.is_ok():
        dto = result.unwrap()
        checkpoint = dto.to_checkpoint()
        dto2 = IngestionResult.from_checkpoint(checkpoint).unwrap()
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json

from pipeline.services import Result, ValidationError


@dataclass(frozen=True)
class IngestionResult:
    """
    Immutable DTO representing ingestion pipeline output.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date (YYYY-MM-DD)
        quality_level: Data quality level (1=Basic, 2=Labor, 3=Efficiency)

        # File paths (not embedded data)
        toast_data_path: Path to ingested Toast data (parquet)
        employee_data_path: Path to employee data (parquet) [L2+]
        timeslots_path: Path to timeslots data (parquet) [L2+]
        efficiency_metrics_path: Path to efficiency metrics (parquet) [L3]

        # Metadata
        ingestion_timestamp: When ingestion completed (ISO 8601)
        record_counts: Count of records per entity
        metadata: Additional context (extensible)
    """

    # Required fields
    restaurant_code: str
    business_date: str
    quality_level: int
    toast_data_path: str

    # Optional fields (quality level dependent)
    employee_data_path: Optional[str] = None
    timeslots_path: Optional[str] = None
    efficiency_metrics_path: Optional[str] = None

    # Metadata
    ingestion_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    record_counts: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        restaurant_code: str,
        business_date: str,
        quality_level: int,
        toast_data_path: str,
        employee_data_path: Optional[str] = None,
        timeslots_path: Optional[str] = None,
        efficiency_metrics_path: Optional[str] = None,
        record_counts: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result["IngestionResult"]:
        """
        Create and validate IngestionResult.

        Args:
            restaurant_code: Restaurant identifier
            business_date: Business date (YYYY-MM-DD)
            quality_level: Quality level (1, 2, or 3)
            toast_data_path: Path to Toast data
            employee_data_path: Path to employee data (required for L2+)
            timeslots_path: Path to timeslots (required for L2+)
            efficiency_metrics_path: Path to efficiency metrics (required for L3)
            record_counts: Record counts per entity
            metadata: Additional metadata

        Returns:
            Result[IngestionResult]: Success with DTO or failure with ValidationError
        """
        dto = IngestionResult(
            restaurant_code=restaurant_code,
            business_date=business_date,
            quality_level=quality_level,
            toast_data_path=toast_data_path,
            employee_data_path=employee_data_path,
            timeslots_path=timeslots_path,
            efficiency_metrics_path=efficiency_metrics_path,
            record_counts=record_counts or {},
            metadata=metadata or {},
        )

        return dto.validate()

    def validate(self) -> Result["IngestionResult"]:
        """
        Validate DTO fields and quality level requirements.

        Returns:
            Result[IngestionResult]: Self if valid, ValidationError if invalid
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

        # Validate quality level
        if self.quality_level not in [1, 2, 3]:
            return Result.fail(
                ValidationError(
                    message="quality_level must be 1, 2, or 3",
                    context={"field": "quality_level", "value": self.quality_level}
                )
            )

        # Validate toast_data_path
        if not self.toast_data_path or not self.toast_data_path.strip():
            return Result.fail(
                ValidationError(
                    message="toast_data_path is required",
                    context={"field": "toast_data_path"}
                )
            )

        # Quality level L2+ requires employee and timeslot data
        if self.quality_level >= 2:
            if not self.employee_data_path:
                return Result.fail(
                    ValidationError(
                        message="employee_data_path is required for quality level 2+",
                        context={
                            "quality_level": self.quality_level,
                            "missing_field": "employee_data_path"
                        }
                    )
                )

            if not self.timeslots_path:
                return Result.fail(
                    ValidationError(
                        message="timeslots_path is required for quality level 2+",
                        context={
                            "quality_level": self.quality_level,
                            "missing_field": "timeslots_path"
                        }
                    )
                )

        # Quality level L3 requires efficiency metrics
        if self.quality_level == 3:
            if not self.efficiency_metrics_path:
                return Result.fail(
                    ValidationError(
                        message="efficiency_metrics_path is required for quality level 3",
                        context={
                            "quality_level": self.quality_level,
                            "missing_field": "efficiency_metrics_path"
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
            "quality_level": self.quality_level,
            "toast_data_path": self.toast_data_path,
            "employee_data_path": self.employee_data_path,
            "timeslots_path": self.timeslots_path,
            "efficiency_metrics_path": self.efficiency_metrics_path,
            "ingestion_timestamp": self.ingestion_timestamp,
            "record_counts": self.record_counts,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_checkpoint(checkpoint: Dict[str, Any]) -> Result["IngestionResult"]:
        """
        Deserialize from checkpoint dictionary.

        Args:
            checkpoint: Checkpoint data

        Returns:
            Result[IngestionResult]: Success with DTO or failure with ValidationError
        """
        try:
            return IngestionResult.create(
                restaurant_code=checkpoint["restaurant_code"],
                business_date=checkpoint["business_date"],
                quality_level=checkpoint["quality_level"],
                toast_data_path=checkpoint["toast_data_path"],
                employee_data_path=checkpoint.get("employee_data_path"),
                timeslots_path=checkpoint.get("timeslots_path"),
                efficiency_metrics_path=checkpoint.get("efficiency_metrics_path"),
                record_counts=checkpoint.get("record_counts", {}),
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
        from pipeline.services import CheckpointError

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
    def load_checkpoint(checkpoint_path: str) -> Result["IngestionResult"]:
        """
        Load checkpoint from JSON file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Result[IngestionResult]: Success with DTO or failure with CheckpointError
        """
        from pipeline.services import CheckpointError

        try:
            with open(checkpoint_path, "r") as f:
                checkpoint = json.load(f)

            return IngestionResult.from_checkpoint(checkpoint)
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

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"IngestionResult("
            f"restaurant={self.restaurant_code}, "
            f"date={self.business_date}, "
            f"quality_level={self.quality_level})"
        )
