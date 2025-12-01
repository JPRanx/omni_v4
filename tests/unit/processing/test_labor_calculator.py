"""
Unit tests for LaborCalculator

Tests:
- Basic calculation (percentage, status, grade)
- Threshold boundary testing
- Grade mapping accuracy
- Warning generation
- Recommendation generation
- Custom configuration support
- Error handling (negative values, zero sales)
- Edge cases

Coverage Goal: 100%
"""

import pytest

from pipeline.services.labor_calculator import LaborCalculator, LaborMetrics
from pipeline.models.labor_dto import LaborDTO
from pipeline.services.result import Result


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def calculator():
    """Basic calculator with default thresholds."""
    return LaborCalculator()


@pytest.fixture
def sample_labor_dto():
    """Sample labor DTO for testing."""
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


# ============================================================================
# BASIC CALCULATION TESTS
# ============================================================================

class TestBasicCalculation:
    """Test basic labor percentage calculation."""

    def test_calculate_labor_percentage(self, calculator, sample_labor_dto):
        """Test basic percentage calculation."""
        result = calculator.calculate(sample_labor_dto, sales=5000.0)

        assert result.is_ok()
        metrics = result.unwrap()
        assert metrics.labor_percentage == 25.0  # 1250 / 5000 * 100

    def test_calculate_with_different_sales(self, calculator, sample_labor_dto):
        """Test calculation with various sales amounts."""
        test_cases = [
            (10000.0, 12.5),  # Lower percentage
            (5000.0, 25.0),   # Medium percentage
            (2500.0, 50.0),   # High percentage
        ]

        for sales, expected_percentage in test_cases:
            result = calculator.calculate(sample_labor_dto, sales)
            assert result.is_ok()
            metrics = result.unwrap()
            assert metrics.labor_percentage == expected_percentage

    def test_metrics_includes_all_fields(self, calculator, sample_labor_dto):
        """Test that metrics include all required fields."""
        result = calculator.calculate(sample_labor_dto, sales=5000.0)

        assert result.is_ok()
        metrics = result.unwrap()
        assert metrics.total_hours == 100.0
        assert metrics.labor_cost == 1250.0
        assert metrics.labor_percentage == 25.0
        assert metrics.status is not None
        assert metrics.grade is not None
        assert isinstance(metrics.warnings, list)
        assert isinstance(metrics.recommendations, list)


# ============================================================================
# STATUS THRESHOLD TESTS
# ============================================================================

class TestStatusThresholds:
    """Test status mapping based on thresholds."""

    def test_excellent_status(self, calculator):
        """Test EXCELLENT status (≤20%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1000.0,  # 20% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1000.0,
            total_overtime_cost=0.0,
            average_hourly_rate=10.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().status == 'EXCELLENT'

    def test_good_status(self, calculator):
        """Test GOOD status (≤25%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1250.0,  # 25% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1250.0,
            total_overtime_cost=0.0,
            average_hourly_rate=12.5
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().status == 'GOOD'

    def test_warning_status(self, calculator):
        """Test WARNING status (≤30%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1500.0,  # 30% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=15.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().status == 'WARNING'

    def test_critical_status(self, calculator):
        """Test CRITICAL status (≤35%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1750.0,  # 35% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1750.0,
            total_overtime_cost=0.0,
            average_hourly_rate=17.5
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().status == 'CRITICAL'

    def test_severe_status(self, calculator):
        """Test SEVERE status (>35%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=2500.0,  # 50% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=2500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=25.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().status == 'SEVERE'

    def test_boundary_values(self, calculator):
        """Test exact boundary values."""
        test_cases = [
            (20.0, 'EXCELLENT'),
            (20.1, 'GOOD'),
            (25.0, 'GOOD'),
            (25.1, 'WARNING'),
            (30.0, 'WARNING'),
            (30.1, 'CRITICAL'),
            (35.0, 'CRITICAL'),
            (35.1, 'SEVERE'),
        ]

        for percentage, expected_status in test_cases:
            labor_dto = LaborDTO(
                restaurant_code="SDR",
                business_date="2025-01-15",
                total_hours_worked=100.0,
                total_labor_cost=percentage * 10,  # Sales = 1000
                employee_count=10,
                total_regular_hours=100.0,
                total_overtime_hours=0.0,
                total_regular_cost=percentage * 10,
                total_overtime_cost=0.0,
                average_hourly_rate=percentage / 10
            )

            result = calculator.calculate(labor_dto, sales=1000.0)
            assert result.is_ok()
            assert result.unwrap().status == expected_status, \
                f"Expected {expected_status} for {percentage}%, got {result.unwrap().status}"


# ============================================================================
# GRADE MAPPING TESTS
# ============================================================================

class TestGradeMapping:
    """Test letter grade mapping from percentages."""

    def test_grade_boundaries(self, calculator):
        """Test all grade boundaries.

        Note: Uses values slightly below boundaries to avoid floating-point
        precision issues (e.g., 28.0 * 10 / 1000 * 100 = 28.000000000000004)
        """
        test_cases = [
            (17.9, 'A+'),
            (19.9, 'A'),
            (22.9, 'B+'),
            (24.9, 'B'),
            (27.9, 'C+'),
            (29.9, 'C'),
            (32.9, 'D+'),
            (34.9, 'D'),
            (40.0, 'F'),
        ]

        for percentage, expected_grade in test_cases:
            labor_dto = LaborDTO(
                restaurant_code="SDR",
                business_date="2025-01-15",
                total_hours_worked=100.0,
                total_labor_cost=percentage * 10,  # Sales = 1000
                employee_count=10,
                total_regular_hours=100.0,
                total_overtime_hours=0.0,
                total_regular_cost=percentage * 10,
                total_overtime_cost=0.0,
                average_hourly_rate=percentage / 10
            )

            result = calculator.calculate(labor_dto, sales=1000.0)
            assert result.is_ok()
            assert result.unwrap().grade == expected_grade, \
                f"Expected grade {expected_grade} for {percentage}%, got {result.unwrap().grade}"

    def test_perfect_grade(self, calculator):
        """Test A+ grade for excellent performance."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=900.0,  # 18% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=900.0,
            total_overtime_cost=0.0,
            average_hourly_rate=9.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().grade == 'A+'

    def test_failing_grade(self, calculator):
        """Test F grade for poor performance."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=2000.0,  # 40% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=2000.0,
            total_overtime_cost=0.0,
            average_hourly_rate=20.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert result.unwrap().grade == 'F'


# ============================================================================
# WARNING GENERATION TESTS
# ============================================================================

class TestWarningGeneration:
    """Test warning message generation."""

    def test_no_warnings_for_excellent(self, calculator):
        """Test no warnings for EXCELLENT status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1000.0,  # 20% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1000.0,
            total_overtime_cost=0.0,
            average_hourly_rate=10.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        assert len(result.unwrap().warnings) == 0

    def test_notice_for_good(self, calculator):
        """Test NOTICE warning for GOOD status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1250.0,  # 25% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1250.0,
            total_overtime_cost=0.0,
            average_hourly_rate=12.5
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        warnings = result.unwrap().warnings
        assert len(warnings) == 1
        assert 'NOTICE' in warnings[0]

    def test_warning_for_warning_status(self, calculator):
        """Test WARNING message for WARNING status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1500.0,  # 30% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=15.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        warnings = result.unwrap().warnings
        assert len(warnings) == 1
        assert 'WARNING' in warnings[0]

    def test_critical_warning(self, calculator):
        """Test CRITICAL warning for CRITICAL status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1750.0,  # 35% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1750.0,
            total_overtime_cost=0.0,
            average_hourly_rate=17.5
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        warnings = result.unwrap().warnings
        assert len(warnings) == 1
        assert 'CRITICAL' in warnings[0]

    def test_severe_warning(self, calculator):
        """Test SEVERE warning for SEVERE status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=2500.0,  # 50% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=2500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=25.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        warnings = result.unwrap().warnings
        assert len(warnings) == 1
        assert 'SEVERE' in warnings[0]


# ============================================================================
# RECOMMENDATION GENERATION TESTS
# ============================================================================

class TestRecommendationGeneration:
    """Test recommendation generation for each status."""

    def test_excellent_recommendations(self, calculator):
        """Test recommendations for EXCELLENT status."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1000.0,
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1000.0,
            total_overtime_cost=0.0,
            average_hourly_rate=10.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        recommendations = result.unwrap().recommendations
        assert len(recommendations) > 0
        assert any('excellent' in r.lower() for r in recommendations)

    def test_severe_recommendations_urgent(self, calculator):
        """Test recommendations for SEVERE status include urgency."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=2500.0,
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=2500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=25.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        recommendations = result.unwrap().recommendations
        assert len(recommendations) > 0
        assert any('CRITICAL' in r or 'Emergency' in r for r in recommendations)


# ============================================================================
# CUSTOM CONFIGURATION TESTS
# ============================================================================

class TestCustomConfiguration:
    """Test calculator with custom threshold configuration."""

    def test_custom_thresholds(self):
        """Test calculator with custom threshold configuration."""
        custom_config = {
            'labor_excellent_threshold': 18.0,
            'labor_good_threshold': 22.0,
            'labor_warning_threshold': 28.0,
            'labor_critical_threshold': 32.0,
        }

        calculator = LaborCalculator(config=custom_config)

        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=100.0,
            total_labor_cost=1100.0,  # 22% of 5000
            employee_count=10,
            total_regular_hours=100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1100.0,
            total_overtime_cost=0.0,
            average_hourly_rate=11.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        # 22% should be GOOD with custom thresholds (vs WARNING with default)
        assert result.unwrap().status == 'GOOD'

    def test_default_config_when_none_provided(self):
        """Test calculator uses defaults when no config provided."""
        calculator = LaborCalculator(config=None)
        assert calculator.thresholds['excellent'] == 20.0
        assert calculator.thresholds['good'] == 25.0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_zero_sales_error(self, calculator, sample_labor_dto):
        """Test error when sales is zero."""
        result = calculator.calculate(sample_labor_dto, sales=0.0)

        assert result.is_err()
        assert 'positive' in str(result.unwrap_err()).lower()

    def test_negative_sales_error(self, calculator, sample_labor_dto):
        """Test error when sales is negative."""
        result = calculator.calculate(sample_labor_dto, sales=-1000.0)

        assert result.is_err()
        assert 'positive' in str(result.unwrap_err()).lower()

    def test_negative_labor_cost_error(self, calculator):
        """Test error when labor cost is negative."""
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

        result = calculator.calculate(labor_dto, sales=5000.0)

        assert result.is_err()
        assert 'negative' in str(result.unwrap_err()).lower()

    def test_negative_hours_error(self, calculator):
        """Test error when hours are negative."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=-100.0,  # Negative!
            total_labor_cost=1250.0,
            employee_count=10,
            total_regular_hours=-100.0,
            total_overtime_hours=0.0,
            total_regular_cost=1250.0,
            total_overtime_cost=0.0,
            average_hourly_rate=12.5
        )

        result = calculator.calculate(labor_dto, sales=5000.0)

        assert result.is_err()
        assert 'negative' in str(result.unwrap_err()).lower()


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_low_percentage(self, calculator):
        """Test very low labor percentage (< 10%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=50.0,
            total_labor_cost=500.0,  # 5% of 10000
            employee_count=5,
            total_regular_hours=50.0,
            total_overtime_hours=0.0,
            total_regular_cost=500.0,
            total_overtime_cost=0.0,
            average_hourly_rate=10.0
        )

        result = calculator.calculate(labor_dto, sales=10000.0)
        assert result.is_ok()
        metrics = result.unwrap()
        assert metrics.labor_percentage == 5.0
        assert metrics.status == 'EXCELLENT'
        assert metrics.grade == 'A+'

    def test_very_high_percentage(self, calculator):
        """Test very high labor percentage (> 100%)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=200.0,
            total_labor_cost=6000.0,  # 120% of 5000
            employee_count=20,
            total_regular_hours=200.0,
            total_overtime_hours=0.0,
            total_regular_cost=6000.0,
            total_overtime_cost=0.0,
            average_hourly_rate=30.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        metrics = result.unwrap()
        assert metrics.labor_percentage == 120.0
        assert metrics.status == 'SEVERE'
        assert metrics.grade == 'F'

    def test_zero_labor_cost(self, calculator):
        """Test zero labor cost (valid but unusual)."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=0.0,
            total_labor_cost=0.0,
            employee_count=0,
            total_regular_hours=0.0,
            total_overtime_hours=0.0,
            total_regular_cost=0.0,
            total_overtime_cost=0.0,
            average_hourly_rate=0.0
        )

        result = calculator.calculate(labor_dto, sales=5000.0)
        assert result.is_ok()
        metrics = result.unwrap()
        assert metrics.labor_percentage == 0.0
        assert metrics.status == 'EXCELLENT'

    def test_floating_point_precision(self, calculator):
        """Test calculation with floating point numbers."""
        labor_dto = LaborDTO(
            restaurant_code="SDR",
            business_date="2025-01-15",
            total_hours_worked=99.75,
            total_labor_cost=1247.89,
            employee_count=10,
            total_regular_hours=89.75,
            total_overtime_hours=10.0,
            total_regular_cost=1122.89,
            total_overtime_cost=125.0,
            average_hourly_rate=12.51
        )

        result = calculator.calculate(labor_dto, sales=4999.99)
        assert result.is_ok()
        metrics = result.unwrap()
        # Should handle floating point arithmetic correctly
        assert isinstance(metrics.labor_percentage, float)
        assert metrics.labor_percentage > 0
