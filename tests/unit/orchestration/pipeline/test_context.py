"""
Unit tests for PipelineContext

Tests:
- Context initialization
- State management (get/set/has)
- Stage tracking (mark_complete, is_complete)
- Timing tracking
- Metadata management
- Checkpoint serialization/deserialization
- Summary generation
"""

import pytest

from pipeline.orchestration.pipeline import PipelineContext


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "restaurant": {"code": "SDR", "name": "Sandra's"},
        "pattern_learning": {"enabled": True}
    }


@pytest.fixture
def context(sample_config):
    """Basic PipelineContext for testing."""
    return PipelineContext(
        restaurant_code="SDR",
        date="2025-01-15",
        config=sample_config
    )


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestContextInitialization:
    """Test PipelineContext initialization."""

    def test_create_basic_context(self, sample_config):
        """Test creating context with required fields."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )

        assert context.restaurant_code == "SDR"
        assert context.date == "2025-01-15"
        assert context.config == sample_config
        assert context.environment == "dev"  # Default
        assert context.dry_run is False  # Default

    def test_create_context_with_optional_fields(self, sample_config):
        """Test creating context with all optional fields."""
        context = PipelineContext(
            restaurant_code="T12",
            date="2025-01-15",
            config=sample_config,
            pipeline_id="test-123",
            environment="prod",
            dry_run=True
        )

        assert context.pipeline_id == "test-123"
        assert context.environment == "prod"
        assert context.dry_run is True

    def test_initial_state_is_empty(self, context):
        """Test context starts with empty state."""
        assert context.get_all_state() == {}
        assert context.get_completed_stages() == []
        assert context.get_total_duration() == 0.0


# ============================================================================
# STATE MANAGEMENT TESTS
# ============================================================================

class TestStateManagement:
    """Test context state management methods."""

    def test_set_and_get_value(self, context):
        """Test setting and retrieving state values."""
        context.set("test_key", "test_value")

        assert context.get("test_key") == "test_value"

    def test_get_nonexistent_key_returns_default(self, context):
        """Test getting non-existent key returns default value."""
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"

    def test_has_key(self, context):
        """Test checking if key exists."""
        assert context.has("test_key") is False

        context.set("test_key", "value")

        assert context.has("test_key") is True

    def test_set_multiple_values(self, context):
        """Test setting multiple state values."""
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        state = context.get_all_state()

        assert len(state) == 3
        assert state["key1"] == "value1"
        assert state["key2"] == "value2"
        assert state["key3"] == "value3"

    def test_overwrite_existing_value(self, context):
        """Test overwriting existing state value."""
        context.set("key", "original")
        assert context.get("key") == "original"

        context.set("key", "updated")
        assert context.get("key") == "updated"

    def test_set_complex_values(self, context):
        """Test storing complex objects in state."""
        complex_value = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "number": 42
        }

        context.set("complex", complex_value)

        retrieved = context.get("complex")
        assert retrieved == complex_value


# ============================================================================
# STAGE TRACKING TESTS
# ============================================================================

class TestStageTracking:
    """Test stage completion tracking."""

    def test_mark_stage_complete(self, context):
        """Test marking stage as complete."""
        context.mark_stage_complete("ingestion")

        assert context.is_stage_complete("ingestion")

    def test_mark_multiple_stages_complete(self, context):
        """Test marking multiple stages complete."""
        context.mark_stage_complete("ingestion")
        context.mark_stage_complete("processing")
        context.mark_stage_complete("storage")

        completed = context.get_completed_stages()

        assert len(completed) == 3
        assert completed == ["ingestion", "processing", "storage"]

    def test_is_stage_complete_false_initially(self, context):
        """Test stage not complete initially."""
        assert context.is_stage_complete("ingestion") is False

    def test_mark_stage_complete_idempotent(self, context):
        """Test marking same stage complete multiple times."""
        context.mark_stage_complete("ingestion")
        context.mark_stage_complete("ingestion")
        context.mark_stage_complete("ingestion")

        completed = context.get_completed_stages()

        assert len(completed) == 1
        assert completed == ["ingestion"]

    def test_stages_completed_in_order(self, context):
        """Test completed stages list maintains order."""
        context.mark_stage_complete("stage3")
        context.mark_stage_complete("stage1")
        context.mark_stage_complete("stage2")

        completed = context.get_completed_stages()

        assert completed == ["stage3", "stage1", "stage2"]


# ============================================================================
# TIMING TRACKING TESTS
# ============================================================================

class TestTimingTracking:
    """Test stage timing tracking."""

    def test_mark_stage_with_duration(self, context):
        """Test recording stage duration."""
        context.mark_stage_complete("ingestion", duration_seconds=2.5)

        assert context.get_stage_timing("ingestion") == 2.5

    def test_get_timing_for_nonexistent_stage(self, context):
        """Test getting timing for stage that hasn't run."""
        assert context.get_stage_timing("nonexistent") is None

    def test_total_duration(self, context):
        """Test calculating total pipeline duration."""
        context.mark_stage_complete("ingestion", duration_seconds=2.0)
        context.mark_stage_complete("processing", duration_seconds=3.5)
        context.mark_stage_complete("storage", duration_seconds=1.5)

        assert context.get_total_duration() == 7.0

    def test_total_duration_empty_pipeline(self, context):
        """Test total duration for pipeline with no stages."""
        assert context.get_total_duration() == 0.0


# ============================================================================
# METADATA TESTS
# ============================================================================

class TestMetadata:
    """Test metadata management."""

    def test_set_and_get_metadata(self, context):
        """Test setting and retrieving metadata."""
        context.set_metadata("user", "admin")

        assert context.get_metadata("user") == "admin"

    def test_get_nonexistent_metadata_returns_default(self, context):
        """Test getting non-existent metadata returns default."""
        assert context.get_metadata("nonexistent") is None
        assert context.get_metadata("nonexistent", "default") == "default"

    def test_set_multiple_metadata(self, context):
        """Test setting multiple metadata values."""
        context.set_metadata("user", "admin")
        context.set_metadata("source", "api")
        context.set_metadata("priority", "high")

        metadata = context.get_all_metadata()

        assert len(metadata) == 3
        assert metadata["user"] == "admin"
        assert metadata["source"] == "api"
        assert metadata["priority"] == "high"


# ============================================================================
# CHECKPOINT TESTS
# ============================================================================

class TestCheckpoint:
    """Test checkpoint serialization and deserialization."""

    def test_to_checkpoint_basic(self, context):
        """Test converting context to checkpoint."""
        checkpoint = context.to_checkpoint()

        assert checkpoint["restaurant_code"] == "SDR"
        assert checkpoint["date"] == "2025-01-15"
        assert checkpoint["environment"] == "dev"
        assert checkpoint["dry_run"] is False

    def test_to_checkpoint_with_state(self, context):
        """Test checkpoint includes state."""
        context.set("key1", "value1")
        context.set("key2", "value2")

        checkpoint = context.to_checkpoint()

        assert checkpoint["state"]["key1"] == "value1"
        assert checkpoint["state"]["key2"] == "value2"

    def test_to_checkpoint_with_completed_stages(self, context):
        """Test checkpoint includes completed stages."""
        context.mark_stage_complete("ingestion", duration_seconds=2.0)
        context.mark_stage_complete("processing", duration_seconds=3.0)

        checkpoint = context.to_checkpoint()

        assert checkpoint["completed_stages"] == ["ingestion", "processing"]
        assert checkpoint["stage_timings"]["ingestion"] == 2.0
        assert checkpoint["stage_timings"]["processing"] == 3.0

    def test_to_checkpoint_with_metadata(self, context):
        """Test checkpoint includes metadata."""
        context.set_metadata("user", "admin")
        context.set_metadata("notes", "test run")

        checkpoint = context.to_checkpoint()

        assert checkpoint["metadata"]["user"] == "admin"
        assert checkpoint["metadata"]["notes"] == "test run"

    def test_from_checkpoint_basic(self, sample_config):
        """Test restoring context from checkpoint."""
        checkpoint = {
            "restaurant_code": "T12",
            "date": "2025-01-20",
            "environment": "prod",
            "dry_run": True,
            "pipeline_id": "test-456",
            "state": {},
            "completed_stages": [],
            "stage_timings": {},
            "metadata": {}
        }

        context = PipelineContext.from_checkpoint(checkpoint, sample_config)

        assert context.restaurant_code == "T12"
        assert context.date == "2025-01-20"
        assert context.environment == "prod"
        assert context.dry_run is True
        assert context.pipeline_id == "test-456"

    def test_from_checkpoint_with_state(self, sample_config):
        """Test restoring context with state."""
        checkpoint = {
            "restaurant_code": "SDR",
            "date": "2025-01-15",
            "state": {"key1": "value1", "key2": "value2"},
            "completed_stages": [],
            "stage_timings": {},
            "metadata": {}
        }

        context = PipelineContext.from_checkpoint(checkpoint, sample_config)

        assert context.get("key1") == "value1"
        assert context.get("key2") == "value2"

    def test_from_checkpoint_with_completed_stages(self, sample_config):
        """Test restoring context with completed stages."""
        checkpoint = {
            "restaurant_code": "SDR",
            "date": "2025-01-15",
            "state": {},
            "completed_stages": ["ingestion", "processing"],
            "stage_timings": {"ingestion": 2.0, "processing": 3.0},
            "metadata": {}
        }

        context = PipelineContext.from_checkpoint(checkpoint, sample_config)

        assert context.get_completed_stages() == ["ingestion", "processing"]
        assert context.get_stage_timing("ingestion") == 2.0
        assert context.get_stage_timing("processing") == 3.0

    def test_checkpoint_round_trip(self, context):
        """Test checkpoint serialization and deserialization round trip."""
        # Set up context with state
        context.set("test_data", {"value": 123})
        context.mark_stage_complete("ingestion", duration_seconds=2.5)
        context.set_metadata("user", "admin")

        # Serialize to checkpoint
        checkpoint = context.to_checkpoint()

        # Deserialize from checkpoint
        restored = PipelineContext.from_checkpoint(checkpoint, context.config)

        # Verify all data preserved
        assert restored.restaurant_code == context.restaurant_code
        assert restored.date == context.date
        assert restored.get("test_data") == {"value": 123}
        assert restored.is_stage_complete("ingestion")
        assert restored.get_stage_timing("ingestion") == 2.5
        assert restored.get_metadata("user") == "admin"


# ============================================================================
# SUMMARY TESTS
# ============================================================================

class TestSummary:
    """Test summary generation."""

    def test_summary_basic(self, context):
        """Test basic summary."""
        summary = context.summary()

        assert summary["restaurant_code"] == "SDR"
        assert summary["date"] == "2025-01-15"
        assert summary["environment"] == "dev"
        assert summary["completed_stages"] == []
        assert summary["stage_count"] == 0
        assert summary["total_duration"] == 0.0

    def test_summary_with_stages(self, context):
        """Test summary with completed stages."""
        context.mark_stage_complete("ingestion", duration_seconds=2.0)
        context.mark_stage_complete("processing", duration_seconds=3.0)

        summary = context.summary()

        assert summary["completed_stages"] == ["ingestion", "processing"]
        assert summary["stage_count"] == 2
        assert summary["total_duration"] == 5.0

    def test_summary_with_state_and_metadata(self, context):
        """Test summary includes state keys and metadata."""
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set_metadata("user", "admin")

        summary = context.summary()

        assert "key1" in summary["state_keys"]
        assert "key2" in summary["state_keys"]
        assert summary["metadata"]["user"] == "admin"


# ============================================================================
# REPR TESTS
# ============================================================================

class TestRepr:
    """Test string representation."""

    def test_repr_empty_context(self, context):
        """Test repr for context with no completed stages."""
        repr_str = repr(context)

        assert "PipelineContext" in repr_str
        assert "restaurant=SDR" in repr_str
        assert "date=2025-01-15" in repr_str
        assert "completed_stages=[none]" in repr_str

    def test_repr_with_stages(self, context):
        """Test repr for context with completed stages."""
        context.mark_stage_complete("ingestion")
        context.mark_stage_complete("processing")

        repr_str = repr(context)

        assert "ingestion, processing" in repr_str
