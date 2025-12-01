"""
Unit tests for IngestionResult DTO

Tests:
- DTO creation and validation
- Quality level requirements (L1, L2, L3)
- Checkpoint serialization/deserialization
- File I/O operations
- Error handling
"""

import pytest
import json
import tempfile
from pathlib import Path

from pipeline.models.ingestion_result import IngestionResult
from pipeline.services import ValidationError, CheckpointError


class TestIngestionResultCreation:
    """Test IngestionResult creation and validation."""

    def test_create_l1_basic_success(self):
        """Test creating L1 (basic) IngestionResult."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/SDR_2024-01-15_toast.parquet"
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.business_date == "2024-01-15"
        assert dto.quality_level == 1
        assert dto.toast_data_path == "/data/SDR_2024-01-15_toast.parquet"
        assert dto.employee_data_path is None
        assert dto.timeslots_path is None
        assert dto.efficiency_metrics_path is None

    def test_create_l2_labor_success(self):
        """Test creating L2 (labor) IngestionResult."""
        result = IngestionResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            quality_level=2,
            toast_data_path="/data/T12_2024-01-15_toast.parquet",
            employee_data_path="/data/T12_2024-01-15_employees.parquet",
            timeslots_path="/data/T12_2024-01-15_timeslots.parquet"
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.quality_level == 2
        assert dto.employee_data_path is not None
        assert dto.timeslots_path is not None
        assert dto.efficiency_metrics_path is None

    def test_create_l3_efficiency_success(self):
        """Test creating L3 (efficiency) IngestionResult."""
        result = IngestionResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            quality_level=3,
            toast_data_path="/data/TK9_2024-01-15_toast.parquet",
            employee_data_path="/data/TK9_2024-01-15_employees.parquet",
            timeslots_path="/data/TK9_2024-01-15_timeslots.parquet",
            efficiency_metrics_path="/data/TK9_2024-01-15_efficiency.parquet"
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.quality_level == 3
        assert dto.employee_data_path is not None
        assert dto.timeslots_path is not None
        assert dto.efficiency_metrics_path is not None

    def test_create_with_record_counts(self):
        """Test creating IngestionResult with record counts."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet",
            record_counts={
                "toast_records": 1500,
                "checks": 450,
                "items": 2800
            }
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.record_counts["toast_records"] == 1500
        assert dto.record_counts["checks"] == 450

    def test_create_with_metadata(self):
        """Test creating IngestionResult with metadata."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet",
            metadata={
                "source": "manual_upload",
                "operator": "admin",
                "notes": "Special event day"
            }
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.metadata["source"] == "manual_upload"
        assert dto.metadata["operator"] == "admin"

    def test_immutability(self):
        """Test DTO is immutable (frozen dataclass)."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        )

        dto = result.unwrap()

        # Should not be able to modify frozen fields
        with pytest.raises(Exception):  # FrozenInstanceError
            dto.restaurant_code = "T12"  # type: ignore

        with pytest.raises(Exception):
            dto.quality_level = 2  # type: ignore


class TestIngestionResultValidation:
    """Test IngestionResult validation logic."""

    def test_validate_missing_restaurant_code(self):
        """Test validation fails for missing restaurant_code."""
        result = IngestionResult.create(
            restaurant_code="",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "restaurant_code" in error.message

    def test_validate_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="01/15/2024",  # Wrong format
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "YYYY-MM-DD" in error.message

    def test_validate_invalid_quality_level(self):
        """Test validation fails for invalid quality level."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=5,  # Invalid
            toast_data_path="/data/toast.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "quality_level" in error.message

    def test_validate_missing_toast_path(self):
        """Test validation fails for missing toast_data_path."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path=""
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "toast_data_path" in error.message

    def test_validate_l2_missing_employee_data(self):
        """Test L2 validation fails without employee_data_path."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=2,
            toast_data_path="/data/toast.parquet",
            # Missing employee_data_path
            timeslots_path="/data/timeslots.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "employee_data_path" in error.message

    def test_validate_l2_missing_timeslots(self):
        """Test L2 validation fails without timeslots_path."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=2,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet"
            # Missing timeslots_path
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "timeslots_path" in error.message

    def test_validate_l3_missing_efficiency_metrics(self):
        """Test L3 validation fails without efficiency_metrics_path."""
        result = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=3,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet",
            timeslots_path="/data/timeslots.parquet"
            # Missing efficiency_metrics_path
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "efficiency_metrics_path" in error.message


class TestCheckpointSerialization:
    """Test checkpoint serialization and deserialization."""

    def test_to_checkpoint_l1(self):
        """Test serializing L1 IngestionResult to checkpoint."""
        dto = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet",
            record_counts={"toast_records": 100}
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["restaurant_code"] == "SDR"
        assert checkpoint["business_date"] == "2024-01-15"
        assert checkpoint["quality_level"] == 1
        assert checkpoint["toast_data_path"] == "/data/toast.parquet"
        assert checkpoint["record_counts"]["toast_records"] == 100
        assert checkpoint["employee_data_path"] is None

    def test_to_checkpoint_l3(self):
        """Test serializing L3 IngestionResult to checkpoint."""
        dto = IngestionResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            quality_level=3,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet",
            timeslots_path="/data/timeslots.parquet",
            efficiency_metrics_path="/data/efficiency.parquet"
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["quality_level"] == 3
        assert checkpoint["employee_data_path"] == "/data/employees.parquet"
        assert checkpoint["timeslots_path"] == "/data/timeslots.parquet"
        assert checkpoint["efficiency_metrics_path"] == "/data/efficiency.parquet"

    def test_from_checkpoint_success(self):
        """Test deserializing checkpoint to IngestionResult."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            "quality_level": 1,
            "toast_data_path": "/data/toast.parquet",
            "employee_data_path": None,
            "timeslots_path": None,
            "efficiency_metrics_path": None,
            "ingestion_timestamp": "2024-01-15T10:30:00",
            "record_counts": {"toast_records": 100},
            "metadata": {"source": "test"}
        }

        result = IngestionResult.from_checkpoint(checkpoint)

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.record_counts["toast_records"] == 100
        assert dto.metadata["source"] == "test"

    def test_from_checkpoint_missing_field(self):
        """Test deserialization fails with missing required field."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            # Missing quality_level
            "toast_data_path": "/data/toast.parquet"
        }

        result = IngestionResult.from_checkpoint(checkpoint)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "Missing required checkpoint field" in error.message

    def test_roundtrip_checkpoint(self):
        """Test checkpoint roundtrip (to_checkpoint -> from_checkpoint)."""
        original = IngestionResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            quality_level=2,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet",
            timeslots_path="/data/timeslots.parquet",
            record_counts={"employees": 25},
            metadata={"shift": "morning"}
        ).unwrap()

        checkpoint = original.to_checkpoint()
        restored = IngestionResult.from_checkpoint(checkpoint).unwrap()

        assert restored.restaurant_code == original.restaurant_code
        assert restored.business_date == original.business_date
        assert restored.quality_level == original.quality_level
        assert restored.toast_data_path == original.toast_data_path
        assert restored.employee_data_path == original.employee_data_path
        assert restored.record_counts["employees"] == 25
        assert restored.metadata["shift"] == "morning"


class TestCheckpointFileIO:
    """Test checkpoint file I/O operations."""

    def test_save_checkpoint_success(self):
        """Test saving checkpoint to file."""
        dto = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"
            result = dto.save_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            assert checkpoint_path.exists()

            # Verify file contents
            with open(checkpoint_path) as f:
                data = json.load(f)
                assert data["restaurant_code"] == "SDR"

    def test_save_checkpoint_creates_directory(self):
        """Test save_checkpoint creates parent directories."""
        dto = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Nested path that doesn't exist
            checkpoint_path = Path(tmpdir) / "state" / "ingestion" / "checkpoint.json"
            result = dto.save_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            assert checkpoint_path.exists()

    def test_load_checkpoint_success(self):
        """Test loading checkpoint from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Create checkpoint file
            checkpoint_data = {
                "restaurant_code": "T12",
                "business_date": "2024-01-15",
                "quality_level": 1,
                "toast_data_path": "/data/toast.parquet",
                "employee_data_path": None,
                "timeslots_path": None,
                "efficiency_metrics_path": None,
                "ingestion_timestamp": "2024-01-15T10:00:00",
                "record_counts": {},
                "metadata": {}
            }

            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint_data, f)

            # Load checkpoint
            result = IngestionResult.load_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            dto = result.unwrap()
            assert dto.restaurant_code == "T12"
            assert dto.business_date == "2024-01-15"

    def test_load_checkpoint_file_not_found(self):
        """Test loading non-existent checkpoint fails."""
        result = IngestionResult.load_checkpoint("/nonexistent/checkpoint.json")

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, CheckpointError)
        assert "not found" in error.message

    def test_load_checkpoint_invalid_json(self):
        """Test loading invalid JSON checkpoint fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Write invalid JSON
            with open(checkpoint_path, "w") as f:
                f.write("{ invalid json }")

            result = IngestionResult.load_checkpoint(str(checkpoint_path))

            assert result.is_err()
            error = result.unwrap_err()
            assert isinstance(error, CheckpointError)
            assert "Invalid checkpoint JSON" in error.message

    def test_roundtrip_file_io(self):
        """Test full roundtrip: create -> save -> load."""
        original = IngestionResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            quality_level=3,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet",
            timeslots_path="/data/timeslots.parquet",
            efficiency_metrics_path="/data/efficiency.parquet",
            record_counts={"toast_records": 500},
            metadata={"operator": "system"}
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Save
            save_result = original.save_checkpoint(str(checkpoint_path))
            assert save_result.is_ok()

            # Load
            load_result = IngestionResult.load_checkpoint(str(checkpoint_path))
            assert load_result.is_ok()

            restored = load_result.unwrap()
            assert restored.restaurant_code == original.restaurant_code
            assert restored.quality_level == original.quality_level
            assert restored.efficiency_metrics_path == original.efficiency_metrics_path
            assert restored.record_counts["toast_records"] == 500
            assert restored.metadata["operator"] == "system"


class TestIngestionResultHelpers:
    """Test helper methods."""

    def test_repr(self):
        """Test __repr__ method."""
        dto = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=2,
            toast_data_path="/data/toast.parquet",
            employee_data_path="/data/employees.parquet",
            timeslots_path="/data/timeslots.parquet"
        ).unwrap()

        repr_str = repr(dto)
        assert "IngestionResult" in repr_str
        assert "SDR" in repr_str
        assert "2024-01-15" in repr_str
        assert "quality_level=2" in repr_str

    def test_ingestion_timestamp_auto_generated(self):
        """Test ingestion_timestamp is automatically generated."""
        dto = IngestionResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            quality_level=1,
            toast_data_path="/data/toast.parquet"
        ).unwrap()

        assert dto.ingestion_timestamp is not None
        assert "T" in dto.ingestion_timestamp  # ISO 8601 format
