"""
ProcessingResult DTO

Data Transfer Object for the processing pipeline output.
Follows immutability pattern (frozen dataclass) and references file paths
instead of embedding large data.

Processing outputs:
- Timeslot grading (performance scores)
- Pattern learning updates (traffic patterns, staffing patterns)
- Shift assignments (morning/evening with managers)
- Performance metrics aggregation

Usage:
    from src.models.processing_result import ProcessingResult
    from src.core import Result

    # Create from validation
    result = ProcessingResult.create(
        restaurant_code="SDR",
        business_date="2024-01-15",
        graded_timeslots_path="/data/SDR_2024-01-15_graded.parquet",
        shift_assignments_path="/data/SDR_2024-01-15_shifts.parquet"
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
class ProcessingResult:
    """
    Immutable DTO representing processing pipeline output.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date (YYYY-MM-DD)

        # Output file paths
        graded_timeslots_path: Path to graded timeslots (parquet)
        shift_assignments_path: Path to shift assignments (parquet)
        pattern_updates_path: Path to pattern updates (parquet) [optional]
        aggregated_metrics_path: Path to aggregated metrics (parquet) [optional]

        # Processing summary
        processing_timestamp: When processing completed (ISO 8601)
        timeslot_count: Number of timeslots graded
        shift_summary: Shift breakdown (morning/evening managers, employee counts)
        pattern_updates: Summary of pattern learning updates
        metadata: Additional context (extensible)
    """

    # Required fields
    restaurant_code: str
    business_date: str
    graded_timeslots_path: str
    shift_assignments_path: str

    # Optional output paths
    pattern_updates_path: Optional[str] = None
    aggregated_metrics_path: Optional[str] = None

    # Processing summary
    processing_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    timeslot_count: int = 0
    shift_summary: Dict[str, Any] = field(default_factory=dict)
    pattern_updates: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        restaurant_code: str,
        business_date: str,
        graded_timeslots_path: str,
        shift_assignments_path: str,
        pattern_updates_path: Optional[str] = None,
        aggregated_metrics_path: Optional[str] = None,
        timeslot_count: int = 0,
        shift_summary: Optional[Dict[str, Any]] = None,
        pattern_updates: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result["ProcessingResult"]:
        """
        Create and validate ProcessingResult.

        Args:
            restaurant_code: Restaurant identifier
            business_date: Business date (YYYY-MM-DD)
            graded_timeslots_path: Path to graded timeslots
            shift_assignments_path: Path to shift assignments
            pattern_updates_path: Path to pattern updates (optional)
            aggregated_metrics_path: Path to aggregated metrics (optional)
            timeslot_count: Number of graded timeslots
            shift_summary: Shift breakdown summary
            pattern_updates: Pattern learning update summary
            metadata: Additional metadata

        Returns:
            Result[ProcessingResult]: Success with DTO or failure with ValidationError
        """
        dto = ProcessingResult(
            restaurant_code=restaurant_code,
            business_date=business_date,
            graded_timeslots_path=graded_timeslots_path,
            shift_assignments_path=shift_assignments_path,
            pattern_updates_path=pattern_updates_path,
            aggregated_metrics_path=aggregated_metrics_path,
            timeslot_count=timeslot_count,
            shift_summary=shift_summary or {},
            pattern_updates=pattern_updates or {},
            metadata=metadata or {},
        )

        return dto.validate()

    def validate(self) -> Result["ProcessingResult"]:
        """
        Validate DTO fields.

        Returns:
            Result[ProcessingResult]: Self if valid, ValidationError if invalid
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

        # Validate graded_timeslots_path
        if not self.graded_timeslots_path or not self.graded_timeslots_path.strip():
            return Result.fail(
                ValidationError(
                    message="graded_timeslots_path is required",
                    context={"field": "graded_timeslots_path"}
                )
            )

        # Validate shift_assignments_path
        if not self.shift_assignments_path or not self.shift_assignments_path.strip():
            return Result.fail(
                ValidationError(
                    message="shift_assignments_path is required",
                    context={"field": "shift_assignments_path"}
                )
            )

        # Validate timeslot_count is non-negative
        if self.timeslot_count < 0:
            return Result.fail(
                ValidationError(
                    message="timeslot_count must be non-negative",
                    context={"field": "timeslot_count", "value": self.timeslot_count}
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
            "graded_timeslots_path": self.graded_timeslots_path,
            "shift_assignments_path": self.shift_assignments_path,
            "pattern_updates_path": self.pattern_updates_path,
            "aggregated_metrics_path": self.aggregated_metrics_path,
            "processing_timestamp": self.processing_timestamp,
            "timeslot_count": self.timeslot_count,
            "shift_summary": self.shift_summary,
            "pattern_updates": self.pattern_updates,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_checkpoint(checkpoint: Dict[str, Any]) -> Result["ProcessingResult"]:
        """
        Deserialize from checkpoint dictionary.

        Args:
            checkpoint: Checkpoint data

        Returns:
            Result[ProcessingResult]: Success with DTO or failure with ValidationError
        """
        try:
            return ProcessingResult.create(
                restaurant_code=checkpoint["restaurant_code"],
                business_date=checkpoint["business_date"],
                graded_timeslots_path=checkpoint["graded_timeslots_path"],
                shift_assignments_path=checkpoint["shift_assignments_path"],
                pattern_updates_path=checkpoint.get("pattern_updates_path"),
                aggregated_metrics_path=checkpoint.get("aggregated_metrics_path"),
                timeslot_count=checkpoint.get("timeslot_count", 0),
                shift_summary=checkpoint.get("shift_summary", {}),
                pattern_updates=checkpoint.get("pattern_updates", {}),
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
    def load_checkpoint(checkpoint_path: str) -> Result["ProcessingResult"]:
        """
        Load checkpoint from JSON file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Result[ProcessingResult]: Success with DTO or failure with CheckpointError
        """
        from src.core import CheckpointError

        try:
            with open(checkpoint_path, "r") as f:
                checkpoint = json.load(f)

            return ProcessingResult.from_checkpoint(checkpoint)
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
            f"ProcessingResult("
            f"restaurant={self.restaurant_code}, "
            f"date={self.business_date}, "
            f"timeslots={self.timeslot_count})"
        )
