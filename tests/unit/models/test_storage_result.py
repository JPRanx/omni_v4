"""
Unit tests for StorageResult DTO

Tests:
- DTO creation and validation
- Tables and row counts validation
- Checkpoint serialization/deserialization
- File I/O operations
- Error handling
"""

import pytest
import json
import tempfile
from pathlib import Path

from pipeline.models.storage_result import StorageResult
from pipeline.services import ValidationError, CheckpointError


class TestStorageResultCreation:
    """Test StorageResult creation and validation."""

    def test_create_basic_success(self):
        """Test creating basic StorageResult."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading"],
            row_counts={"daily_performance": 1, "timeslot_grading": 150}
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.business_date == "2024-01-15"
        assert len(dto.tables_written) == 2
        assert dto.row_counts["daily_performance"] == 1
        assert dto.row_counts["timeslot_grading"] == 150
        assert dto.success is True
        assert dto.transaction_id is None

    def test_create_with_transaction_id(self):
        """Test creating StorageResult with transaction ID."""
        result = StorageResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1},
            transaction_id="txn_20240115_123456"
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.transaction_id == "txn_20240115_123456"

    def test_create_with_errors(self):
        """Test creating StorageResult with errors list."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1},
            success=False,
            errors=["Table conflict", "Retry succeeded"]
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.success is False
        assert len(dto.errors) == 2
        assert "Table conflict" in dto.errors

    def test_create_with_metadata(self):
        """Test creating StorageResult with metadata."""
        result = StorageResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1},
            metadata={
                "database": "Supabase",
                "region": "us-west-1",
                "retry_count": 0
            }
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.metadata["database"] == "Supabase"
        assert dto.metadata["retry_count"] == 0

    def test_create_multiple_tables(self):
        """Test creating StorageResult with multiple tables."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=[
                "daily_performance",
                "timeslot_grading",
                "shift_assignments",
                "employee_performance"
            ],
            row_counts={
                "daily_performance": 1,
                "timeslot_grading": 150,
                "shift_assignments": 27,
                "employee_performance": 25
            }
        )

        assert result.is_ok()
        dto = result.unwrap()
        assert len(dto.tables_written) == 4
        assert dto.get_total_rows() == 203

    def test_immutability(self):
        """Test DTO is immutable (frozen dataclass)."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        )

        dto = result.unwrap()

        # Should not be able to modify frozen fields
        with pytest.raises(Exception):  # FrozenInstanceError
            dto.restaurant_code = "T12"  # type: ignore

        with pytest.raises(Exception):
            dto.success = False  # type: ignore


class TestStorageResultValidation:
    """Test StorageResult validation logic."""

    def test_validate_missing_restaurant_code(self):
        """Test validation fails for missing restaurant_code."""
        result = StorageResult.create(
            restaurant_code="",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "restaurant_code" in error.message

    def test_validate_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="01/15/2024",  # Wrong format
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "YYYY-MM-DD" in error.message

    def test_validate_empty_tables_written(self):
        """Test validation fails for empty tables_written."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=[],
            row_counts={}
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "tables_written" in error.message

    def test_validate_empty_row_counts(self):
        """Test validation fails for empty row_counts."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={}
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "row_counts" in error.message

    def test_validate_negative_row_count(self):
        """Test validation fails for negative row count."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": -1}
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "non-negative" in error.message

    def test_validate_tables_row_counts_mismatch(self):
        """Test validation fails when tables_written doesn't match row_counts keys."""
        result = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading"],
            row_counts={"daily_performance": 1}  # Missing timeslot_grading
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "matching tables" in error.message


class TestCheckpointSerialization:
    """Test checkpoint serialization and deserialization."""

    def test_to_checkpoint_basic(self):
        """Test serializing basic StorageResult to checkpoint."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["restaurant_code"] == "SDR"
        assert checkpoint["business_date"] == "2024-01-15"
        assert checkpoint["tables_written"] == ["daily_performance"]
        assert checkpoint["row_counts"]["daily_performance"] == 1
        assert checkpoint["success"] is True
        assert checkpoint["transaction_id"] is None

    def test_to_checkpoint_full(self):
        """Test serializing full StorageResult to checkpoint."""
        dto = StorageResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading"],
            row_counts={"daily_performance": 1, "timeslot_grading": 150},
            transaction_id="txn_123",
            success=True,
            errors=[],
            metadata={"database": "Supabase"}
        ).unwrap()

        checkpoint = dto.to_checkpoint()

        assert checkpoint["transaction_id"] == "txn_123"
        assert checkpoint["success"] is True
        assert checkpoint["errors"] == []
        assert checkpoint["metadata"]["database"] == "Supabase"

    def test_from_checkpoint_success(self):
        """Test deserializing checkpoint to StorageResult."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            "tables_written": ["daily_performance", "timeslot_grading"],
            "row_counts": {"daily_performance": 1, "timeslot_grading": 150},
            "transaction_id": "txn_456",
            "storage_timestamp": "2024-01-15T10:30:00",
            "success": True,
            "errors": [],
            "metadata": {"region": "us-west"}
        }

        result = StorageResult.from_checkpoint(checkpoint)

        assert result.is_ok()
        dto = result.unwrap()
        assert dto.restaurant_code == "SDR"
        assert dto.transaction_id == "txn_456"
        assert dto.metadata["region"] == "us-west"

    def test_from_checkpoint_missing_field(self):
        """Test deserialization fails with missing required field."""
        checkpoint = {
            "restaurant_code": "SDR",
            "business_date": "2024-01-15",
            # Missing tables_written
            "row_counts": {"daily_performance": 1}
        }

        result = StorageResult.from_checkpoint(checkpoint)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "Missing required checkpoint field" in error.message

    def test_roundtrip_checkpoint(self):
        """Test checkpoint roundtrip (to_checkpoint -> from_checkpoint)."""
        original = StorageResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading", "shift_assignments"],
            row_counts={
                "daily_performance": 1,
                "timeslot_grading": 200,
                "shift_assignments": 30
            },
            transaction_id="txn_789",
            success=True,
            errors=[],
            metadata={"retry_count": 0}
        ).unwrap()

        checkpoint = original.to_checkpoint()
        restored = StorageResult.from_checkpoint(checkpoint).unwrap()

        assert restored.restaurant_code == original.restaurant_code
        assert restored.business_date == original.business_date
        assert restored.tables_written == original.tables_written
        assert restored.row_counts == original.row_counts
        assert restored.transaction_id == original.transaction_id
        assert restored.success == original.success
        assert restored.metadata["retry_count"] == 0


class TestCheckpointFileIO:
    """Test checkpoint file I/O operations."""

    def test_save_checkpoint_success(self):
        """Test saving checkpoint to file."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
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
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "state" / "storage" / "checkpoint.json"
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
                "tables_written": ["daily_performance"],
                "row_counts": {"daily_performance": 1},
                "transaction_id": None,
                "storage_timestamp": "2024-01-15T10:00:00",
                "success": True,
                "errors": [],
                "metadata": {}
            }

            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint_data, f)

            result = StorageResult.load_checkpoint(str(checkpoint_path))

            assert result.is_ok()
            dto = result.unwrap()
            assert dto.restaurant_code == "T12"

    def test_load_checkpoint_file_not_found(self):
        """Test loading non-existent checkpoint fails."""
        result = StorageResult.load_checkpoint("/nonexistent/checkpoint.json")

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

            result = StorageResult.load_checkpoint(str(checkpoint_path))

            assert result.is_err()
            error = result.unwrap_err()
            assert isinstance(error, CheckpointError)
            assert "Invalid checkpoint JSON" in error.message

    def test_roundtrip_file_io(self):
        """Test full roundtrip: create -> save -> load."""
        original = StorageResult.create(
            restaurant_code="TK9",
            business_date="2024-01-15",
            tables_written=[
                "daily_performance",
                "timeslot_grading",
                "shift_assignments",
                "employee_performance"
            ],
            row_counts={
                "daily_performance": 1,
                "timeslot_grading": 250,
                "shift_assignments": 35,
                "employee_performance": 28
            },
            transaction_id="txn_final",
            success=True,
            errors=[],
            metadata={"storage_engine": "supabase-postgrest"}
        ).unwrap()

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Save
            save_result = original.save_checkpoint(str(checkpoint_path))
            assert save_result.is_ok()

            # Load
            load_result = StorageResult.load_checkpoint(str(checkpoint_path))
            assert load_result.is_ok()

            restored = load_result.unwrap()
            assert restored.restaurant_code == original.restaurant_code
            assert restored.tables_written == original.tables_written
            assert restored.row_counts == original.row_counts
            assert restored.transaction_id == original.transaction_id
            assert restored.get_total_rows() == 314
            assert restored.metadata["storage_engine"] == "supabase-postgrest"


class TestStorageResultHelpers:
    """Test helper methods."""

    def test_get_total_rows(self):
        """Test get_total_rows() calculation."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading", "shift_assignments"],
            row_counts={
                "daily_performance": 1,
                "timeslot_grading": 150,
                "shift_assignments": 27
            }
        ).unwrap()

        total = dto.get_total_rows()
        assert total == 178

    def test_get_total_rows_single_table(self):
        """Test get_total_rows() with single table."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        ).unwrap()

        total = dto.get_total_rows()
        assert total == 1

    def test_repr_success(self):
        """Test __repr__ method for successful storage."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance", "timeslot_grading"],
            row_counts={"daily_performance": 1, "timeslot_grading": 120},
            success=True
        ).unwrap()

        repr_str = repr(dto)
        assert "StorageResult" in repr_str
        assert "SDR" in repr_str
        assert "2024-01-15" in repr_str
        assert "tables=2" in repr_str
        assert "rows=121" in repr_str
        assert "SUCCESS" in repr_str

    def test_repr_failed(self):
        """Test __repr__ method for failed storage."""
        dto = StorageResult.create(
            restaurant_code="T12",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1},
            success=False
        ).unwrap()

        repr_str = repr(dto)
        assert "FAILED" in repr_str

    def test_storage_timestamp_auto_generated(self):
        """Test storage_timestamp is automatically generated."""
        dto = StorageResult.create(
            restaurant_code="SDR",
            business_date="2024-01-15",
            tables_written=["daily_performance"],
            row_counts={"daily_performance": 1}
        ).unwrap()

        assert dto.storage_timestamp is not None
        assert "T" in dto.storage_timestamp  # ISO 8601 format
