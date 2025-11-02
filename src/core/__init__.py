"""Core business logic and domain models"""

from .errors import (
    OMNIError,
    ConfigError,
    IngestionError,
    MissingFileError,
    QualityCheckError,
    DataValidationError,
    ValidationError,
    SerializationError,
    ProcessingError,
    PatternError,
    GradingError,
    ShiftSplitError,
    StorageError,
    DatabaseError,
    TransactionError,
    CheckpointError,
)
from .result import Result, from_optional, from_exception, collect, partition

__all__ = [
    # Base error
    "OMNIError",
    # Config errors
    "ConfigError",
    # Ingestion errors
    "IngestionError",
    "MissingFileError",
    "QualityCheckError",
    "DataValidationError",
    "ValidationError",
    # Serialization errors
    "SerializationError",
    # Processing errors
    "ProcessingError",
    "PatternError",
    "GradingError",
    "ShiftSplitError",
    # Storage errors
    "StorageError",
    "DatabaseError",
    "TransactionError",
    "CheckpointError",
    # Result type
    "Result",
    "from_optional",
    "from_exception",
    "collect",
    "partition",
]