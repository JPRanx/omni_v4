"""
Unit tests for PatternLearningStage

Tests:
- Successful pattern learning
- Resilient error handling (failures don't block pipeline)
- Missing input handling
- Invalid input type handling
- Context updates (learned_patterns, pattern_warnings)
- Integration with DailyLaborPatternManager

Coverage Goal: 90%+

Note: Refactored in Week 4 Day 7 to use DailyLaborPatternManager instead of PatternManager.
"""

import pytest
from unittest.mock import Mock, MagicMock

from pipeline.stages.pattern_learning_stage import PatternLearningStage
from pipeline.services.labor_calculator import LaborMetrics
from pipeline.orchestration.pipeline import PipelineContext
from pipeline.services.result import Result
from pipeline.models.daily_labor_pattern import DailyLaborPattern
from pipeline.services.patterns.daily_labor_manager import DailyLaborPatternManager


def create_mock_pattern(confidence=0.75, observations=5):
    """Create a mock pattern with numeric attributes for logging."""
    mock_pattern = Mock()
    mock_pattern.confidence = confidence
    mock_pattern.observations = observations
    return mock_pattern


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
def sample_labor_metrics():
    """Sample labor metrics."""
    return LaborMetrics(
        total_hours=100.0,
        labor_cost=1250.0,
        labor_percentage=25.0,
        status='GOOD',
        grade='B',
        warnings=[],
        recommendations=[]
    )


@pytest.fixture
def mock_pattern_manager():
    """Mock DailyLaborPatternManager for testing."""
    return Mock(spec=DailyLaborPatternManager)


@pytest.fixture
def pattern_learning_stage(mock_pattern_manager):
    """PatternLearningStage with mocked PatternManager."""
    return PatternLearningStage(mock_pattern_manager)


@pytest.fixture
def context_with_metrics(sample_config, sample_labor_metrics):
    """Pipeline context with labor_metrics."""
    context = PipelineContext(
        restaurant_code="SDR",
        date="2025-01-15",
        config=sample_config
    )
    context.set('labor_metrics', sample_labor_metrics)
    return context


# ============================================================================
# SUCCESSFUL PATTERN LEARNING TESTS
# ============================================================================

class TestSuccessfulPatternLearning:
    """Test successful pattern learning scenarios."""

    def test_learn_pattern_successfully(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test successful pattern learning."""
        # Setup mock to return successful pattern
        mock_pattern = create_mock_pattern()  # Use helper for proper numeric attributes
        mock_pattern_manager.learn_pattern.return_value = Result.ok(mock_pattern)

        # Execute stage
        result = pattern_learning_stage.execute(context_with_metrics)

        # Verify success
        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.has('learned_patterns')
        assert len(updated_context.get('learned_patterns')) == 1
        assert updated_context.get('learned_patterns')[0] == mock_pattern

    def test_pattern_manager_called_correctly(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test DailyLaborPatternManager is called with correct arguments."""
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        pattern_learning_stage.execute(context_with_metrics)

        # Verify DailyLaborPatternManager.learn_pattern was called
        mock_pattern_manager.learn_pattern.assert_called_once()
        call_args = mock_pattern_manager.learn_pattern.call_args
        assert call_args.kwargs['restaurant_code'] == 'SDR'
        assert call_args.kwargs['day_of_week'] == 2  # 2025-01-15 is Wednesday (day 2)
        assert call_args.kwargs['observed_labor_percentage'] == 25.0  # labor_percentage
        assert call_args.kwargs['observed_total_hours'] == 100.0  # total_hours

    def test_stores_empty_warnings_on_success(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test stores empty warnings list on successful learning."""
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        result = pattern_learning_stage.execute(context_with_metrics)

        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.has('pattern_warnings')
        assert len(updated_context.get('pattern_warnings')) == 0


# ============================================================================
# RESILIENT ERROR HANDLING TESTS
# ============================================================================

class TestResilientErrorHandling:
    """Test resilient error handling (failures don't block pipeline)."""

    def test_pattern_learning_failure_returns_success(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test pattern learning failure still returns success (resilient)."""
        # Setup mock to return error
        mock_pattern_manager.learn_pattern.return_value = Result.fail(ValueError("Pattern learning failed"))

        # Execute stage
        result = pattern_learning_stage.execute(context_with_metrics)

        # Should still return success (resilient)
        assert result.is_ok()

    def test_pattern_learning_failure_logs_warning(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test pattern learning failure logs warning in context."""
        mock_pattern_manager.learn_pattern.return_value = Result.fail(ValueError("Test error"))

        result = pattern_learning_stage.execute(context_with_metrics)

        updated_context = result.unwrap()
        assert updated_context.has('pattern_warnings')
        warnings = updated_context.get('pattern_warnings')
        assert len(warnings) == 1
        assert 'Failed to learn daily labor pattern' in warnings[0]
        assert 'Test error' in warnings[0]

    def test_pattern_learning_failure_stores_empty_patterns(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test pattern learning failure stores empty patterns list."""
        mock_pattern_manager.learn_pattern.return_value = Result.fail(ValueError("Test error"))

        result = pattern_learning_stage.execute(context_with_metrics)

        updated_context = result.unwrap()
        assert updated_context.has('learned_patterns')
        assert len(updated_context.get('learned_patterns')) == 0


# ============================================================================
# MISSING INPUT HANDLING TESTS
# ============================================================================

class TestMissingInputHandling:
    """Test handling of missing inputs from context."""

    def test_missing_labor_metrics(self, pattern_learning_stage, sample_config, mock_pattern_manager):
        """Test handling when labor_metrics missing from context."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        # No labor_metrics in context

        result = pattern_learning_stage.execute(context)

        # Should return success (resilient)
        assert result.is_ok()
        updated_context = result.unwrap()

        # Should log warning
        assert updated_context.has('pattern_warnings')
        warnings = updated_context.get('pattern_warnings')
        assert len(warnings) == 1
        assert 'labor_metrics not found' in warnings[0]

        # Should not call pattern manager
        mock_pattern_manager.learn_pattern.assert_not_called()

    def test_missing_labor_metrics_stores_empty_patterns(self, pattern_learning_stage, sample_config, mock_pattern_manager):
        """Test missing labor_metrics stores empty patterns list."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )

        result = pattern_learning_stage.execute(context)

        updated_context = result.unwrap()
        assert updated_context.has('learned_patterns')
        assert len(updated_context.get('learned_patterns')) == 0


# ============================================================================
# INVALID INPUT TYPE HANDLING TESTS
# ============================================================================

class TestInvalidInputTypeHandling:
    """Test handling of invalid input types."""

    def test_invalid_labor_metrics_type(self, pattern_learning_stage, sample_config, mock_pattern_manager):
        """Test handling when labor_metrics has wrong type."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_metrics', {'invalid': 'dict'})  # Wrong type!

        result = pattern_learning_stage.execute(context)

        # Should return success (resilient)
        assert result.is_ok()
        updated_context = result.unwrap()

        # Should log warning
        assert updated_context.has('pattern_warnings')
        warnings = updated_context.get('pattern_warnings')
        assert len(warnings) == 1
        assert 'wrong type' in warnings[0]

        # Should not call pattern manager
        mock_pattern_manager.learn_pattern.assert_not_called()


# ============================================================================
# CONTEXT INTEGRATION TESTS
# ============================================================================

class TestContextIntegration:
    """Test integration with PipelineContext."""

    def test_preserves_existing_context_data(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test stage preserves existing context data."""
        context_with_metrics.set('existing_key', 'existing_value')
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        result = pattern_learning_stage.execute(context_with_metrics)

        updated_context = result.unwrap()
        assert updated_context.get('existing_key') == 'existing_value'

    def test_returns_same_context_object(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test stage returns the same context object (mutated)."""
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        result = pattern_learning_stage.execute(context_with_metrics)

        updated_context = result.unwrap()
        assert updated_context is context_with_metrics


# ============================================================================
# REPR TESTS
# ============================================================================

class TestRepr:
    """Test string representation."""

    def test_repr_includes_pattern_manager_name(self, pattern_learning_stage):
        """Test repr includes pattern manager class name."""
        repr_str = repr(pattern_learning_stage)

        assert 'PatternLearningStage' in repr_str
        # Mock's spec creates a PatternManager instance, so check for that
        assert 'PatternManager' in repr_str or 'Mock' in repr_str


# ============================================================================
# PIPELINE STAGE PROTOCOL COMPLIANCE
# ============================================================================

class TestPipelineStageProtocol:
    """Test compliance with PipelineStage protocol."""

    def test_has_execute_method(self, pattern_learning_stage):
        """Test stage has execute method."""
        assert hasattr(pattern_learning_stage, 'execute')
        assert callable(pattern_learning_stage.execute)

    def test_execute_accepts_context(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test execute accepts PipelineContext."""
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        result = pattern_learning_stage.execute(context_with_metrics)
        assert isinstance(result, Result)

    def test_execute_returns_result_context(self, pattern_learning_stage, context_with_metrics, mock_pattern_manager):
        """Test execute returns Result[PipelineContext]."""
        mock_pattern_manager.learn_pattern.return_value = Result.ok(create_mock_pattern())

        result = pattern_learning_stage.execute(context_with_metrics)

        assert isinstance(result, Result)
        if result.is_ok():
            assert isinstance(result.unwrap(), PipelineContext)

    def test_can_use_in_pipeline_list(self, pattern_learning_stage):
        """Test stage can be used in pipeline stages list."""
        stages = [
            ('pattern_learning', pattern_learning_stage),
        ]

        for stage_name, stage_instance in stages:
            assert stage_name == 'pattern_learning'
            assert stage_instance is pattern_learning_stage
