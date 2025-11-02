"""
Unit tests for ProcessingResult DTO

Tests:
- DTO creation and validation
- Required and optional fields
- Checkpoint serialization/deserialization
- File I/O operations
- Error handling
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.models.processing_result import ProcessingResult
from src.core import ValidationError, CheckpointError


class TestProcessingResultCreation:
    """Test ProcessingResult creation and validation."""

    def test_create_basic_success(self):
        """Test creating basic ProcessingResult with required fields."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/SDR_2024-01-15_graded.parquet",
            shift_assignments_path="/data/SDR_2024-01-15_shifts.parquet"
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.business_date == "2024-01-15"
        assert dto.graded_timeslots_path == "/data/SDR_2024-01-15_graded.parquet"
        assert dto.shift_assignments_path == "/data/SDR_2024-01-15_shifts.parquet"
        assert dto.pattern_updates_path is None
        assert dto.aggregated_metrics_path is None

    def test_create_with_all_fields(self):
        """Test creating ProcessingResult with all optional fields."""
        result = ProcessingResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            pattern_updates_path="/data/patterns.parquet",
            aggregated_metrics_path="/data/metrics.parquet",
            timeslot_count=150
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.pattern_updates_path == "/data/patterns.parquet"
        assert dto.aggregated_metrics_path == "/data/metrics.parquet"
        assert dto.timeslot_count == 150

    def test_create_with_shift_summary(self):
        """Test creating ProcessingResult with shift summary."""
        shift_summary = {
            "morning": {
                "manager": "John Doe",
                "employees": 12,
                "hours": "06:00-14:00"
            },
            "evening": {
                "manager": "Jane Smith",
                "employees": 15,
                "hours": "14:00-22:00"
            }
        }

        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            shift_summary=shift_summary
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.shift_summary["morning"]["manager"] == "John Doe"
        assert dto.shift_summary["evening"]["employees"] == 15

    def test_create_with_pattern_updates(self):
        """Test creating ProcessingResult with pattern updates."""
        pattern_updates = {
            "Lobby": {"updated": True, "observations": 50},
            "Drive-Thru": {"updated": True, "observations": 120},
            "ToGo": {"updated": False, "observations": 10}
        }

        result = ProcessingResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            pattern_updates=pattern_updates
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.pattern_updates["Lobby"]["updated"] is True
        assert dto.pattern_updates["Drive-Thru"]["observations"] == 120

    def test_create_with_metadata(self):
        """Test creating ProcessingResult with metadata."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            metadata={
                "processing_version": "4.0",
                "operator": "system",
                "notes": "Holiday processing"
            }
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.metadata["processing_version"] == "4.0"
        assert dto.metadata["operator"] == "system"

    def test_immutability(self):
        """Test DTO is immutable (frozen dataclass)."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
        )

        dto = result.unwrap()

        # Should not be able to modify frozen fields
        with pytest.raises(Exception):  # FrozenInstanceError
            dto.restaurant_code = "T12"  # type: ignore

        with pytest.raises(Exception):
            dto.timeslot_count = 100  # type: ignore


class TestProcessingResultValidation:
    """Test ProcessingResult validation logic."""

    def test_validate_missing_restaurant_code(self):
        """Test validation fails for missing restaurant_code."""
        result = ProcessingResult.create(
            restaurant_code="",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "restaurant_code" in error.message

    def test_validate_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="01/15/2024",  # Wrong format
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "YYYY-MM-DD" in error.message

    def test_validate_missing_graded_timeslots_path(self):
        """Test validation fails for missing graded_timeslots_path."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="",
            shift_assignments_path="/data/shifts.parquet"
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "graded_timeslots_path" in error.message

    def test_validate_missing_shift_assignments_path(self):
        """Test validation fails for missing shift_assignments_path."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path=""
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "shift_assignments_path" in error.message

    def test_validate_negative_timeslot_count(self):
        """Test validation fails for negative timeslot_count."""
        result = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            timeslot_count=-1
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "timeslot_count" in error.message


class TestCheckpointSerialization:
    """Test checkpoint serialization and deserialization."""

    def test_to_checkpoint_basic(self):
        """Test serializing basic ProcessingResult to checkpoint."""
        dto = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            timeslot_count=100
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["restaurant_code"] == "SDR"
        assert checkpoint["business_date"] == "2024-01-15"
        assert checkpoint["graded_timeslots_path"] == "/data/graded.parquet"
        assert checkpoint["shift_assignments_path"] == "/data/shifts.parquet"
        assert checkpoint["timeslot_count"] == 100
        assert checkpoint["pattern_updates_path"] is None

    def test_to_checkpoint_full(self):
        """Test serializing full ProcessingResult to checkpoint."""
        shift_summary = {"morning": {"manager": "John"}}
        pattern_updates = {"Lobby": {"updated": True}}

        dto = ProcessingResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            pattern_updates_path="/data/patterns.parquet",
            aggregated_metrics_path="/data/metrics.parquet",
            timeslot_count=150,
            shift_summary=shift_summary,
            pattern_updates=pattern_updates
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["pattern_updates_path"] == "/data/patterns.parquet"
        assert checkpoint["aggregated_metrics_path"] == "/data/metrics.parquet"
        assert checkpoint["shift_summary"]["morning"]["manager"] == "John"
        assert checkpoint["pattern_updates"]["Lobby"]["updated"] is True

    def test_from_checkpoint_success(self):
        """Test deserializing checkpoint to ProcessingResult."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            "graded_timeslots_path": "/data/graded.parquet",
            "shift_assignments_path": "/data/shifts.parquet",
            "pattern_updates_path": None,
            "aggregated_metrics_path": None,
            "processing_timestamp": "2024-01-15T10:30:00",
            "timeslot_count": 100,
            "shift_summary": {},
            "pattern_updates": {},
            "metadata": {"source": "test"}
        }

        result = ProcessingResult.from_checkpoint(checkpoint)

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.timeslot_count == 100
        assert dto.metadata["source"] == "test"

    def test_from_checkpoint_missing_field(self):
        """Test deserialization fails with missing required field."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            # Missing graded_timeslots_path
            "shift_assignments_path": "/data/shifts.parquet"
        }

        result = ProcessingResult.from_checkpoint(checkpoint)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "Missing required checkpoint field" in error.message

    def test_roundtrip_checkpoint(self):
        """Test checkpoint roundtrip (to_checkpoint -> from_checkpoint)."""
        original = ProcessingResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            pattern_updates_path="/data/patterns.parquet",
            timeslot_count=200,
            shift_summary={"morning": {"manager": "Alice"}},
            pattern_updates={"Lobby": {"observations": 50}},
            metadata={"version": "4.0"}
        ).unwrap()

        checkpoint = original.to_checkpoint()
        restored = ProcessingResult.from_checkpoint(checkpoint).unwrap()

        assert restored.restaurant_code == original.restaurant_code
        assert restored.business_date == original.business_date
        assert restored.graded_timeslots_path == original.graded_timeslots_path
        assert restored.pattern_updates_path == original.pattern_updates_path
        assert restored.timeslot_count == 200
        assert restored.shift_summary["morning"]["manager"] == "Alice"
        assert restored.metadata["version"] == "4.0"


class TestCheckpointFileIO:
    """Test checkpoint file I/O operations."""

    def test_save_checkpoint_success(self):
        """Test saving checkpoint to file."""
        dto = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
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
        dto = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "state" / "processing" / "checkpoint.json"
            result = dto.save_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            assert checkpoint_path.exists()

    def test_load_checkpoint_success(self):
        """Test loading checkpoint from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            checkpoint_data = {
                "restaurant_code": "T12",
                "business_date": "2024-01-15",
                "graded_timeslots_path": "/data/graded.parquet",
                "shift_assignments_path": "/data/shifts.parquet",
                "pattern_updates_path": None,
                "aggregated_metrics_path": None,
                "processing_timestamp": "2024-01-15T10:00:00",
                "timeslot_count": 150,
                "shift_summary": {},
                "pattern_updates": {},
                "metadata": {}
            }

            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint_data, f)

            result = ProcessingResult.load_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            dto = result.unwrap()
            assert dto.restaurant_code == "T12"
            assert dto.timeslot_count == 150

    def test_load_checkpoint_file_not_found(self):
        """Test loading non-existent checkpoint fails."""
        result = ProcessingResult.load_checkpoint("/nonexistent/checkpoint.json")

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, CheckpointError)
        assert "not found" in error.message

    def test_load_checkpoint_invalid_json(self):
        """Test loading invalid JSON checkpoint fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            with open(checkpoint_path, "w") as f:
                f.write("{ invalid json }")

            result = ProcessingResult.load_checkpoint(str(checkpoint_path))

            assert result.is_err()
            error = result.unwrap_err()
            assert isinstance(error, CheckpointError)
            assert "Invalid checkpoint JSON" in error.message

    def test_roundtrip_file_io(self):
        """Test full roundtrip: create -> save -> load."""
        original = ProcessingResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            pattern_updates_path="/data/patterns.parquet",
            aggregated_metrics_path="/data/metrics.parquet",
            timeslot_count=250,
            shift_summary={"evening": {"manager": "Bob"}},
            pattern_updates={"Drive-Thru": {"updated": True}},
            metadata={"processor": "advanced"}
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Save
            save_result = original.save_checkpoint(str(checkpoint_path))
            assert save_result.is_ok()

            # Load
            load_result = ProcessingResult.load_checkpoint(str(checkpoint_path))
            assert load_result.is_ok()

            restored = load_result.unwrap()
            assert restored.restaurant_code == original.restaurant_code
            assert restored.timeslot_count == 250
            assert restored.aggregated_metrics_path == original.aggregated_metrics_path
            assert restored.shift_summary["evening"]["manager"] == "Bob"
            assert restored.pattern_updates["Drive-Thru"]["updated"] is True
            assert restored.metadata["processor"] == "advanced"


class TestProcessingResultHelpers:
    """Test helper methods."""

    def test_repr(self):
        """Test __repr__ method."""
        dto = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet",
            timeslot_count=120
        ).unwrap()

        repr_str = repr(dto)
        assert "ProcessingResult" in repr_str
        assert "SDR" in repr_str
        assert "2024-01-15" in repr_str
        assert "timeslots=120" in repr_str

    def test_processing_timestamp_auto_generated(self):
        """Test processing_timestamp is automatically generated."""
        dto = ProcessingResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            graded_timeslots_path="/data/graded.parquet",
            shift_assignments_path="/data/shifts.parquet"
        ).unwrap()

        assert dto.processing_timestamp is not None
        assert "T" in dto.processing_timestamp  # ISO 8601 format
