"""
Unit tests for error hierarchy

Tests all custom exception classes in src/core/errors.py:
- Base OMNIError
- Configuration errors
- Ingestion errors (with subclasses)
- Processing errors (with subclasses)
- Storage errors (with subclasses)
- Factory functions
"""

import pytest
from pipeline.services.errors import (
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
    # Factory functions
    missing_file,
    quality_check_failed,
    pattern_not_found,
    database_connection_failed,
)


class TestOMNIError:
    """Test base OMNIError class."""

    def test_basic_error_creation(self):
        """Test creating error with just message."""
        error = OMNIError("Something went wrong")

        assert error.message == "Something went wrong"
        assert error.context == {}
        assert str(error) == "Something went wrong"

    def test_error_with_context(self):
        """Test creating error with context."""
        error = OMNIError(
            message="Operation failed",
            context={"restaurant": "SDR", "date": "2024-01-15"}
        )

        assert error.message == "Operation failed"
        assert error.context == {"restaurant": "SDR", "date": "2024-01-15"}
        assert "restaurant=SDR" in str(error)
        assert "date=2024-01-15" in str(error)

    def test_error_repr(self):
        """Test error repr for debugging."""
        error = OMNIError("Test", context={"key": "value"})

        repr_str = repr(error)
        assert "OMNIError" in repr_str
        assert "Test" in repr_str
        assert "key" in repr_str

    def test_error_is_exception(self):
        """Test error is a proper Exception."""
        error = OMNIError("Test")

        assert isinstance(error, Exception)
        assert isinstance(error, OMNIError)


class TestConfigError:
    """Test ConfigError class."""

    def test_config_error_creation(self):
        """Test creating config error."""
        error = ConfigError(
            message="Missing environment variable",
            context={"variable": "SUPABASE_URL"}
        )

        assert isinstance(error, OMNIError)
        assert isinstance(error, ConfigError)
        assert error.message == "Missing environment variable"
        assert error.context["variable"] == "SUPABASE_URL"

    def test_config_error_catchable_as_omni_error(self):
        """Test config error can be caught as OMNIError."""
        try:
            raise ConfigError("Invalid config")
        except OMNIError as e:
            assert isinstance(e, ConfigError)


class TestIngestionErrors:
    """Test ingestion error hierarchy."""

    def test_ingestion_error_is_omni_error(self):
        """Test IngestionError inherits from OMNIError."""
        error = IngestionError("Ingestion failed")

        assert isinstance(error, OMNIError)
        assert isinstance(error, IngestionError)

    def test_missing_file_error_basic(self):
        """Test MissingFileError with basic parameters."""
        error = MissingFileError(
            message="File not found",
            file_path="/data/toast.csv"
        )

        assert isinstance(error, IngestionError)
        assert isinstance(error, MissingFileError)
        assert error.context["file_path"] == "/data/toast.csv"

    def test_missing_file_error_full_context(self):
        """Test MissingFileError with all convenience parameters."""
        error = MissingFileError(
            message="Toast export missing",
            file_path="/data/SDR_2024-01-15.csv",
            restaurant="SDR",
            date="2024-01-15"
        )

        assert error.context["file_path"] == "/data/SDR_2024-01-15.csv"
        assert error.context["restaurant"] == "SDR"
        assert error.context["date"] == "2024-01-15"
        assert "file_path=/data/SDR_2024-01-15.csv" in str(error)

    def test_quality_check_error(self):
        """Test QualityCheckError."""
        error = QualityCheckError(
            message="Insufficient records",
            context={
                "restaurant": "SDR",
                "records": 5,
                "threshold": 50
            }
        )

        assert isinstance(error, IngestionError)
        assert isinstance(error, QualityCheckError)
        assert error.context["records"] == 5
        assert error.context["threshold"] == 50

    def test_data_validation_error(self):
        """Test DataValidationError."""
        error = DataValidationError(
            message="Schema mismatch",
            context={
                "expected": ["col1", "col2"],
                "actual": ["colA", "colB"]
            }
        )

        assert isinstance(error, IngestionError)
        assert isinstance(error, DataValidationError)

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError(
            message="Quality level mismatch",
            context={
                "quality_level": 3,
                "required_field": "efficiency_metrics_path",
                "error": "L3 requires efficiency metrics"
            }
        )

        assert isinstance(error, IngestionError)
        assert isinstance(error, ValidationError)
        assert error.context["quality_level"] == 3

    def test_catch_all_ingestion_errors(self):
        """Test catching all ingestion errors with base class."""
        errors = [
            MissingFileError("File missing"),
            QualityCheckError("Quality failed"),
            DataValidationError("Validation failed"),
            ValidationError("DTO validation failed")
        ]

        for error in errors:
            try:
                raise error
            except IngestionError as e:
                assert isinstance(e, IngestionError)


class TestSerializationError:
    """Test SerializationError class."""

    def test_serialization_error_creation(self):
        """Test creating serialization error."""
        error = SerializationError(
            message="Checkpoint deserialization failed",
            context={
                "checkpoint_path": "/data/state/SDR_2024-01-15.json",
                "error": "Missing required field: business_date"
            }
        )

        assert isinstance(error, OMNIError)
        assert isinstance(error, SerializationError)
        assert error.message == "Checkpoint deserialization failed"
        assert "/data/state/SDR_2024-01-15.json" in error.context["checkpoint_path"]

    def test_serialization_error_catchable_as_omni_error(self):
        """Test serialization error can be caught as OMNIError."""
        try:
            raise SerializationError("JSON encoding failed")
        except OMNIError as e:
            assert isinstance(e, SerializationError)


class TestProcessingErrors:
    """Test processing error hierarchy."""

    def test_processing_error_is_omni_error(self):
        """Test ProcessingError inherits from OMNIError."""
        error = ProcessingError("Processing failed")

        assert isinstance(error, OMNIError)
        assert isinstance(error, ProcessingError)

    def test_pattern_error(self):
        """Test PatternError."""
        error = PatternError(
            message="Pattern confidence too low",
            context={
                "restaurant": "SDR",
                "service_type": "Lobby",
                "confidence": 0.3,
                "threshold": 0.6
            }
        )

        assert isinstance(error, ProcessingError)
        assert isinstance(error, PatternError)
        assert error.context["confidence"] == 0.3

    def test_grading_error(self):
        """Test GradingError."""
        error = GradingError(
            message="Missing metrics",
            context={
                "restaurant": "SDR",
                "timeslot_id": 12345
            }
        )

        assert isinstance(error, ProcessingError)
        assert isinstance(error, GradingError)

    def test_shift_split_error(self):
        """Test ShiftSplitError."""
        error = ShiftSplitError(
            message="No manager found",
            context={
                "restaurant": "SDR",
                "shift": "morning",
                "cutoff_hour": 14
            }
        )

        assert isinstance(error, ProcessingError)
        assert isinstance(error, ShiftSplitError)
        assert error.context["shift"] == "morning"

    def test_catch_all_processing_errors(self):
        """Test catching all processing errors with base class."""
        errors = [
            PatternError("Pattern failed"),
            GradingError("Grading failed"),
            ShiftSplitError("Split failed")
        ]

        for error in errors:
            try:
                raise error
            except ProcessingError as e:
                assert isinstance(e, ProcessingError)


class TestStorageErrors:
    """Test storage error hierarchy."""

    def test_storage_error_is_omni_error(self):
        """Test StorageError inherits from OMNIError."""
        error = StorageError("Storage failed")

        assert isinstance(error, OMNIError)
        assert isinstance(error, StorageError)

    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError(
            message="Connection timeout",
            context={
                "database": "Supabase",
                "table": "daily_performance",
                "timeout": 30
            }
        )

        assert isinstance(error, StorageError)
        assert isinstance(error, DatabaseError)
        assert error.context["database"] == "Supabase"

    def test_transaction_error(self):
        """Test TransactionError."""
        error = TransactionError(
            message="Constraint violation",
            context={
                "table": "daily_performance",
                "constraint": "unique_restaurant_date"
            }
        )

        assert isinstance(error, StorageError)
        assert isinstance(error, TransactionError)

    def test_checkpoint_error(self):
        """Test CheckpointError."""
        error = CheckpointError(
            message="Checkpoint save failed",
            context={
                "checkpoint_path": "/data/state/ingestion/SDR_2024-01-15.json",
                "error": "Permission denied"
            }
        )

        assert isinstance(error, StorageError)
        assert isinstance(error, CheckpointError)
        assert "Permission denied" in error.context["error"]

    def test_catch_all_storage_errors(self):
        """Test catching all storage errors with base class."""
        errors = [
            DatabaseError("DB failed"),
            TransactionError("Transaction failed"),
            CheckpointError("Checkpoint failed")
        ]

        for error in errors:
            try:
                raise error
            except StorageError as e:
                assert isinstance(e, StorageError)


class TestErrorHierarchy:
    """Test error hierarchy structure."""

    def test_all_errors_are_omni_errors(self):
        """Test all custom errors inherit from OMNIError."""
        errors = [
            ConfigError("Config"),
            IngestionError("Ingestion"),
            MissingFileError("File"),
            QualityCheckError("Quality"),
            DataValidationError("Validation"),
            ValidationError("DTO Validation"),
            SerializationError("Serialization"),
            ProcessingError("Processing"),
            PatternError("Pattern"),
            GradingError("Grading"),
            ShiftSplitError("Shift"),
            StorageError("Storage"),
            DatabaseError("Database"),
            TransactionError("Transaction"),
            CheckpointError("Checkpoint"),
        ]

        for error in errors:
            assert isinstance(error, OMNIError)
            assert isinstance(error, Exception)

    def test_catch_all_omni_errors(self):
        """Test catching all OMNI errors with base class."""
        errors = [
            ConfigError("Config"),
            MissingFileError("File"),
            PatternError("Pattern"),
            DatabaseError("DB"),
        ]

        for error in errors:
            try:
                raise error
            except OMNIError as e:
                # Should catch all
                assert True


class TestFactoryFunctions:
    """Test error factory functions."""

    def test_missing_file_factory(self):
        """Test missing_file() factory function."""
        error = missing_file(
            file_path="/data/toast.csv",
            restaurant="SDR",
            date="2024-01-15"
        )

        assert isinstance(error, MissingFileError)
        assert error.context["file_path"] == "/data/toast.csv"
        assert error.context["restaurant"] == "SDR"
        assert error.context["date"] == "2024-01-15"
        assert "Toast export file not found" in error.message

    def test_quality_check_failed_factory(self):
        """Test quality_check_failed() factory function."""
        error = quality_check_failed(
            check_name="insufficient_records",
            restaurant="SDR",
            date="2024-01-15",
            records=5,
            threshold=50
        )

        assert isinstance(error, QualityCheckError)
        assert error.context["check"] == "insufficient_records"
        assert error.context["records"] == 5
        assert error.context["threshold"] == 50
        assert "Quality check failed" in error.message

    def test_pattern_not_found_factory(self):
        """Test pattern_not_found() factory function."""
        error = pattern_not_found(
            restaurant="SDR",
            service_type="Lobby",
            hour=12
        )

        assert isinstance(error, PatternError)
        assert error.context["restaurant"] == "SDR"
        assert error.context["service_type"] == "Lobby"
        assert error.context["hour"] == 12
        assert "Pattern not found" in error.message

    def test_database_connection_failed_factory(self):
        """Test database_connection_failed() factory function."""
        error = database_connection_failed(
            database="Supabase",
            reason="Timeout after 30s"
        )

        assert isinstance(error, DatabaseError)
        assert error.context["database"] == "Supabase"
        assert "Timeout after 30s" in error.message


class TestErrorUsagePatterns:
    """Test realistic error usage patterns."""

    def test_raise_and_catch_specific_error(self):
        """Test raising and catching specific error type."""
        with pytest.raises(MissingFileError) as exc_info:
            raise MissingFileError(
                message="File not found",
                file_path="/data/test.csv"
            )

        error = exc_info.value
        assert error.context["file_path"] == "/data/test.csv"

    def test_raise_and_catch_base_class(self):
        """Test raising specific error but catching base class."""
        with pytest.raises(IngestionError):
            raise MissingFileError("File not found")

    def test_error_in_try_except(self):
        """Test error handling in try/except."""
        def risky_operation():
            raise QualityCheckError(
                message="Check failed",
                context={"records": 5}
            )

        try:
            risky_operation()
            pytest.fail("Should have raised QualityCheckError")
        except QualityCheckError as e:
            assert e.context["records"] == 5
        except Exception:
            pytest.fail("Should have caught as QualityCheckError")

    def test_multiple_error_types(self):
        """Test handling multiple error types."""
        def operation(error_type: str):
            if error_type == "file":
                raise MissingFileError("File missing")
            elif error_type == "quality":
                raise QualityCheckError("Quality failed")
            elif error_type == "pattern":
                raise PatternError("Pattern failed")

        # Test each error type
        with pytest.raises(MissingFileError):
            operation("file")

        with pytest.raises(QualityCheckError):
            operation("quality")

        with pytest.raises(PatternError):
            operation("pattern")

        # Test catching all as OMNIError
        for error_type in ["file", "quality", "pattern"]:
            try:
                operation(error_type)
            except OMNIError:
                pass  # Successfully caught
