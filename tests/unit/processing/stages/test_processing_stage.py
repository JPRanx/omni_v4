"""
Unit tests for ProcessingStage

Tests:
- Stage execution with valid inputs
- Context input validation
- Context output validation
- Error propagation from calculator
- Type checking for inputs
- Integration with PipelineContext
- Result[T] pattern compliance

Coverage Goal: 100%
"""

import pytest

from src.processing.stages.processing_stage import ProcessingStage
from src.processing.labor_calculator import LaborCalculator, LaborMetrics
from src.orchestration.pipeline import PipelineContext
from src.models.labor_dto import LaborDTO
from src.core.result import Result


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "restaurant": {"code": "SDR", "name": "Sandra's"},
        "labor": {
            "excellent_threshold": 20.0,
            "good_threshold": 25.0,
        }
    }


@pytest.fixture
def calculator():
    """LaborCalculator for testing."""
    return LaborCalculator()


@pytest.fixture
def processing_stage(calculator):
    """ProcessingStage with calculator."""
    return ProcessingStage(calculator)


@pytest.fixture
def sample_labor_dto():
    """Sample labor DTO."""
    return LaborDTO(
        restaurant_code="SDR",
        business_date="2025-01-15",
        total_hours_worked=100.0,
        total_labor_cost=1250.0,
        employee_count=10,
        total_regular_hours=90.0,
        total_overtime_hours=10.0,
        total_regular_cost=1125.0,
        total_overtime_cost=125.0,
        average_hourly_rate=12.50
    )


@pytest.fixture
def context_with_data(sample_config, sample_labor_dto):
    """Pipeline context with labor_dto and sales."""
    context = PipelineContext(
        restaurant_code="SDR",
        date="2025-01-15",
        config=sample_config
    )
    context.set('labor_dto', sample_labor_dto)
    context.set('sales', 5000.0)
    return context


# ============================================================================
# BASIC EXECUTION TESTS
# ============================================================================

class TestBasicExecution:
    """Test basic stage execution."""

    def test_execute_with_valid_inputs(self, processing_stage, context_with_data):
        """Test stage executes successfully with valid inputs."""
        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.has('labor_metrics')

    def test_execute_stores_labor_metrics(self, processing_stage, context_with_data):
        """Test stage stores LaborMetrics in context."""
        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        metrics = updated_context.get('labor_metrics')
        assert isinstance(metrics, LaborMetrics)
        assert metrics.labor_percentage == 25.0

    def test_execute_stores_summary_values(self, processing_stage, context_with_data):
        """Test stage stores summary values for easy access."""
        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.has('labor_percentage')
        assert updated_context.has('labor_status')
        assert updated_context.has('labor_grade')
        assert updated_context.get('labor_percentage') == 25.0
        assert updated_context.get('labor_status') == 'GOOD'
        assert updated_context.get('labor_grade') == 'B'

    def test_execute_returns_same_context_object(self, processing_stage, context_with_data):
        """Test stage returns the same context object (mutated)."""
        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        # Should be the same object reference
        assert updated_context is context_with_data

    def test_execute_with_different_sales_values(self, processing_stage, sample_config, sample_labor_dto):
        """Test execution with various sales values."""
        test_cases = [
            (10000.0, 12.5, 'EXCELLENT'),
            (5000.0, 25.0, 'GOOD'),
            (3000.0, 41.67, 'SEVERE'),
        ]

        for sales, expected_percentage, expected_status in test_cases:
            context = PipelineContext(
                restaurant_code="SDR",
                date="2025-01-15",
                config=sample_config
            )
            context.set('labor_dto', sample_labor_dto)
            context.set('sales', sales)

            result = processing_stage.execute(context)
            assert result.is_ok()
            metrics = result.unwrap().get('labor_metrics')
            assert abs(metrics.labor_percentage - expected_percentage) < 0.1
            assert metrics.status == expected_status


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Test input validation and error handling."""

    def test_missing_labor_dto_error(self, processing_stage, sample_config):
        """Test error when labor_dto missing from context."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('sales', 5000.0)  # Sales present, but no labor_dto

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'labor_dto not found' in str(error)

    def test_missing_sales_error(self, processing_stage, sample_config, sample_labor_dto):
        """Test error when sales missing from context."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)  # Labor DTO present, but no sales

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'sales not found' in str(error)

    def test_invalid_labor_dto_type_error(self, processing_stage, sample_config):
        """Test error when labor_dto is wrong type."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', {'invalid': 'dict'})  # Wrong type!
        context.set('sales', 5000.0)

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'must be LaborDTO' in str(error)

    def test_invalid_sales_type_error(self, processing_stage, sample_config, sample_labor_dto):
        """Test error when sales is wrong type."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)
        context.set('sales', 'invalid')  # Wrong type!

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'must be numeric' in str(error)

    def test_sales_as_integer_works(self, processing_stage, sample_config, sample_labor_dto):
        """Test sales can be integer (not just float)."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)
        context.set('sales', 5000)  # Integer, not float

        result = processing_stage.execute(context)

        assert result.is_ok()
        metrics = result.unwrap().get('labor_metrics')
        assert metrics.labor_percentage == 25.0


# ============================================================================
# ERROR PROPAGATION TESTS
# ============================================================================

class TestErrorPropagation:
    """Test error propagation from LaborCalculator."""

    def test_propagate_zero_sales_error(self, processing_stage, sample_config, sample_labor_dto):
        """Test propagation of zero sales error from calculator."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)
        context.set('sales', 0.0)  # Zero sales

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'positive' in str(error).lower()

    def test_propagate_negative_sales_error(self, processing_stage, sample_config, sample_labor_dto):
        """Test propagation of negative sales error from calculator."""
        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)
        context.set('sales', -1000.0)  # Negative sales

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'positive' in str(error).lower()

    def test_propagate_negative_labor_cost_error(self, processing_stage, sample_config):
        """Test propagation of negative labor cost error."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=-1250.0,  # Negative!
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=-1250.0,
            total_overtime_cost=0.0,
            average_hourly_rate=12.5
        )

        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', labor_dto)
        context.set('sales', 5000.0)

        result = processing_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'negative' in str(error).lower()


# ============================================================================
# CONTEXT INTEGRATION TESTS
# ============================================================================

class TestContextIntegration:
    """Test integration with PipelineContext."""

    def test_preserves_existing_context_data(self, processing_stage, context_with_data):
        """Test stage preserves existing context data."""
        context_with_data.set('existing_key', 'existing_value')

        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.get('existing_key') == 'existing_value'

    def test_context_metadata_preserved(self, processing_stage, context_with_data):
        """Test context metadata is preserved."""
        context_with_data.set_metadata('user', 'admin')

        result = processing_stage.execute(context_with_data)

        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.get_metadata('user') == 'admin'

    def test_multiple_executions_same_context(self, processing_stage, context_with_data):
        """Test executing stage multiple times on same context."""
        # First execution
        result1 = processing_stage.execute(context_with_data)
        assert result1.is_ok()
        metrics1 = result1.unwrap().get('labor_metrics')

        # Update sales
        context_with_data.set('sales', 10000.0)

        # Second execution
        result2 = processing_stage.execute(context_with_data)
        assert result2.is_ok()
        metrics2 = result2.unwrap().get('labor_metrics')

        # Metrics should be different
        assert metrics1.labor_percentage != metrics2.labor_percentage


# ============================================================================
# CUSTOM CALCULATOR TESTS
# ============================================================================

class TestCustomCalculator:
    """Test stage with custom calculator configuration."""

    def test_custom_calculator_thresholds(self, sample_config, sample_labor_dto):
        """Test stage with custom calculator thresholds."""
        custom_config = {
            'labor_excellent_threshold': 18.0,
            'labor_good_threshold': 22.0,
        }
        calculator = LaborCalculator(config=custom_config)
        stage = ProcessingStage(calculator)

        context = PipelineContext(
            restaurant_code="SDR",
            date="2025-01-15",
            config=sample_config
        )
        context.set('labor_dto', sample_labor_dto)
        context.set('sales', 5000.0)  # 25% labor

        result = stage.execute(context)

        assert result.is_ok()
        metrics = result.unwrap().get('labor_metrics')
        # With custom thresholds, 25% should be WARNING (vs GOOD with defaults)
        assert metrics.status == 'WARNING'


# ============================================================================
# REPR TESTS
# ============================================================================

class TestRepr:
    """Test string representation."""

    def test_repr_includes_calculator_name(self, processing_stage):
        """Test repr includes calculator class name."""
        repr_str = repr(processing_stage)

        assert 'ProcessingStage' in repr_str
        assert 'LaborCalculator' in repr_str


# ============================================================================
# PIPELINE STAGE PROTOCOL COMPLIANCE
# ============================================================================

class TestPipelineStageProtocol:
    """Test compliance with PipelineStage protocol."""

    def test_has_execute_method(self, processing_stage):
        """Test stage has execute method."""
        assert hasattr(processing_stage, 'execute')
        assert callable(processing_stage.execute)

    def test_execute_accepts_context(self, processing_stage, context_with_data):
        """Test execute accepts PipelineContext."""
        # Should not raise
        result = processing_stage.execute(context_with_data)
        assert isinstance(result, Result)

    def test_execute_returns_result_context(self, processing_stage, context_with_data):
        """Test execute returns Result[PipelineContext]."""
        result = processing_stage.execute(context_with_data)

        assert isinstance(result, Result)
        if result.is_ok():
            assert isinstance(result.unwrap(), PipelineContext)

    def test_can_use_in_pipeline_list(self, processing_stage):
        """Test stage can be used in pipeline stages list."""
        stages = [
            ('processing', processing_stage),
        ]

        # Should be able to iterate and extract name and stage
        for stage_name, stage_instance in stages:
            assert stage_name == 'processing'
            assert stage_instance is processing_stage
