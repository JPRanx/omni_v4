"""
OMNI V4 Error Hierarchy

Defines all custom exceptions used throughout the OMNI V4 system.
Follows a hierarchical structure for granular error handling.

Error Hierarchy:
    OMNIError (base)
    ├── ConfigError
    ├── IngestionError
    │   ├── MissingFileError
    │   ├── QualityCheckError
    │   └── DataValidationError
    ├── ProcessingError
    │   ├── PatternError
    │   ├── GradingError
    │   └── ShiftSplitError
    └── StorageError
        ├── DatabaseError
        └── TransactionError

Usage:
    from pipeline.services.errors import IngestionError, MissingFileError

    # Raise specific error
    raise MissingFileError(file_path="/data/toast_data.csv", restaurant="SDR")

    # Catch hierarchy
    try:
        process_data()
    except IngestionError as e:  # Catches all ingestion errors
        logger.error(f"Ingestion failed: {e}")
"""

from typing import Optional, Dict, Any


class OMNIError(Exception):
    """
    Base exception for all OMNI V4 errors.

    All custom exceptions inherit from this to enable catching
    all OMNI-specific errors with a single except clause.

    Attributes:
        message: Human-readable error description
        context: Additional error context (restaurant, date, etc.)
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize OMNI error.

        Args:
            message: Error description
            context: Additional context (e.g., restaurant_code, date)
        """
        self.message = message
        self.context = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with context."""
        if not self.context:
            return self.message

        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{self.message} [{context_str}]"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(message={self.message!r}, context={self.context!r})"


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigError(OMNIError):
    """
    Configuration-related errors.

    Raised when:
    - Configuration files are missing or invalid
    - Environment variables are not set
    - Configuration validation fails

    Example:
        raise ConfigError(
            message="Missing environment variable",
            context={"variable": "SUPABASE_URL"}
        )
    """
    pass


# ============================================================================
# Ingestion Errors
# ============================================================================

class IngestionError(OMNIError):
    """
    Base class for data ingestion errors.

    Raised during the ingestion pipeline when loading or validating
    raw Toast data.
    """
    pass


class MissingFileError(IngestionError):
    """
    File not found during ingestion.

    Raised when expected Toast export files are missing.

    Example:
        raise MissingFileError(
            message="Toast export file not found",
            context={
                "file_path": "/data/input/SDR_2024-01-15.csv",
                "restaurant": "SDR",
                "date": "2024-01-15"
            }
        )
    """

    def __init__(
        self,
        message: str = "Required file not found",
        file_path: Optional[str] = None,
        restaurant: Optional[str] = None,
        date: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize MissingFileError with convenience parameters.

        Args:
            message: Error description
            file_path: Path to missing file
            restaurant: Restaurant code
            date: Business date
            **kwargs: Additional context
        """
        context = kwargs
        if file_path:
            context["file_path"] = file_path
        if restaurant:
            context["restaurant"] = restaurant
        if date:
            context["date"] = date

        super().__init__(message=message, context=context)


class QualityCheckError(IngestionError):
    """
    Data quality check failed during ingestion (L1 validation).

    Raised when ingested data fails quality thresholds:
    - Missing required columns
    - Invalid data types
    - Out-of-range values
    - Insufficient data volume

    Example:
        raise QualityCheckError(
            message="Insufficient records",
            context={
                "restaurant": "SDR",
                "date": "2024-01-15",
                "records": 5,
                "threshold": 50
            }
        )
    """
    pass


class DataValidationError(IngestionError):
    """
    Data validation failed during schema validation.

    Raised when data doesn't match expected schema:
    - Invalid column names
    - Wrong data types
    - Failed constraints (nullability, uniqueness)

    Example:
        raise DataValidationError(
            message="Invalid column schema",
            context={
                "expected": ["employee_id", "hours"],
                "actual": ["emp_id", "hrs"],
                "restaurant": "SDR"
            }
        )
    """
    pass


class ValidationError(IngestionError):
    """
    DTO or schema validation failed.

    Raised when:
    - DTO fields fail validation
    - Business rules are violated
    - Data constraints are not met
    - Quality level requirements not satisfied

    Example:
        raise ValidationError(
            message="Quality level mismatch",
            context={
                "quality_level": 3,
                "required_field": "efficiency_metrics_path",
                "error": "L3 requires efficiency metrics"
            }
        )
    """
    pass


# ============================================================================
# Serialization Errors
# ============================================================================

class SerializationError(OMNIError):
    """
    Serialization or deserialization failed.

    Raised when:
    - DTO cannot be serialized to checkpoint
    - Checkpoint cannot be deserialized to DTO
    - JSON encoding/decoding fails
    - Type conversion fails during serialization

    Example:
        raise SerializationError(
            message="Checkpoint deserialization failed",
            context={
                "checkpoint_path": "/data/state/SDR_2024-01-15.json",
                "error": "Missing required field: business_date"
            }
        )
    """
    pass


# ============================================================================
# Processing Errors
# ============================================================================

class ProcessingError(OMNIError):
    """
    Base class for data processing errors.

    Raised during the processing pipeline when transforming or analyzing data.
    """
    pass


class PatternError(ProcessingError):
    """
    Pattern learning or pattern application failed.

    Raised when:
    - Pattern update fails
    - Pattern retrieval fails
    - Pattern confidence too low
    - Pattern data corrupted

    Example:
        raise PatternError(
            message="Pattern confidence too low",
            context={
                "restaurant": "SDR",
                "service_type": "Lobby",
                "hour": 12,
                "confidence": 0.3,
                "threshold": 0.6
            }
        )
    """
    pass


class GradingError(ProcessingError):
    """
    Timeslot grading failed.

    Raised when:
    - Grading calculation fails
    - Missing required metrics
    - Invalid grade values

    Example:
        raise GradingError(
            message="Missing service time data for grading",
            context={
                "restaurant": "SDR",
                "timeslot_id": 12345,
                "service_type": "Drive-Thru"
            }
        )
    """
    pass


class ShiftSplitError(ProcessingError):
    """
    Shift splitting failed.

    Raised when:
    - Shift cutoff hour is invalid
    - Employee shift assignment fails
    - Manager identification fails

    Example:
        raise ShiftSplitError(
            message="No manager found for shift",
            context={
                "restaurant": "SDR",
                "date": "2024-01-15",
                "shift": "morning",
                "cutoff_hour": 14
            }
        )
    """
    pass


# ============================================================================
# Storage Errors
# ============================================================================

class StorageError(OMNIError):
    """
    Base class for data storage errors.

    Raised during the storage pipeline when writing to database.
    """
    pass


class DatabaseError(StorageError):
    """
    Database operation failed.

    Raised when:
    - Connection to database fails
    - Query execution fails
    - Database timeout
    - Permission denied

    Example:
        raise DatabaseError(
            message="Connection timeout",
            context={
                "database": "Supabase",
                "table": "daily_performance",
                "operation": "insert",
                "timeout": 30
            }
        )
    """
    pass


class TransactionError(StorageError):
    """
    Database transaction failed.

    Raised when:
    - Transaction commit fails
    - Transaction rollback fails
    - Deadlock detected
    - Constraint violation

    Example:
        raise TransactionError(
            message="Unique constraint violation",
            context={
                "table": "daily_performance",
                "constraint": "unique_restaurant_date",
                "restaurant": "SDR",
                "date": "2024-01-15"
            }
        )
    """
    pass


class CheckpointError(StorageError):
    """
    Checkpoint save or restore failed.

    Raised when:
    - Checkpoint file cannot be written
    - Checkpoint file cannot be read
    - Checkpoint directory doesn't exist
    - Checkpoint file is corrupted

    Example:
        raise CheckpointError(
            message="Checkpoint save failed",
            context={
                "checkpoint_path": "/data/state/ingestion/SDR_2024-01-15.json",
                "error": "Permission denied"
            }
        )
    """
    pass


# ============================================================================
# Error Factory Functions
# ============================================================================

def missing_file(file_path: str, restaurant: str, date: str) -> MissingFileError:
    """
    Factory function for MissingFileError.

    Args:
        file_path: Path to missing file
        restaurant: Restaurant code
        date: Business date

    Returns:
        MissingFileError instance
    """
    return MissingFileError(
        message=f"Toast export file not found: {file_path}",
        file_path=file_path,
        restaurant=restaurant,
        date=date
    )


def quality_check_failed(
    check_name: str,
    restaurant: str,
    date: str,
    **metrics
) -> QualityCheckError:
    """
    Factory function for QualityCheckError.

    Args:
        check_name: Name of quality check that failed
        restaurant: Restaurant code
        date: Business date
        **metrics: Additional metrics (records, threshold, etc.)

    Returns:
        QualityCheckError instance
    """
    context = {"restaurant": restaurant, "date": date, "check": check_name}
    context.update(metrics)

    return QualityCheckError(
        message=f"Quality check failed: {check_name}",
        context=context
    )


def pattern_not_found(
    restaurant: str,
    service_type: str,
    hour: int
) -> PatternError:
    """
    Factory function for PatternError when pattern not found.

    Args:
        restaurant: Restaurant code
        service_type: Service type (Lobby, Drive-Thru, ToGo)
        hour: Hour of day (0-23)

    Returns:
        PatternError instance
    """
    return PatternError(
        message="Pattern not found",
        context={
            "restaurant": restaurant,
            "service_type": service_type,
            "hour": hour
        }
    )


def database_connection_failed(database: str, reason: str) -> DatabaseError:
    """
    Factory function for DatabaseError.

    Args:
        database: Database name (e.g., "Supabase")
        reason: Failure reason

    Returns:
        DatabaseError instance
    """
    return DatabaseError(
        message=f"Database connection failed: {reason}",
        context={"database": database}
    )
