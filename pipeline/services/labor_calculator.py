"""
Labor metrics calculation with threshold analysis.

Ported from V3:
- labor_processor.py: Basic labor calculations
- labor_analyzer.py: Threshold analysis and grading

Key Features:
- Calculate labor percentage from cost and sales
- Map percentage to status (EXCELLENT/GOOD/WARNING/CRITICAL/SEVERE)
- Convert percentage to letter grade (A+ to F)
- Generate warnings and recommendations
- All operations return Result[T] for error handling
"""

from dataclasses import dataclass, field
from typing import Optional

from pipeline.services.result import Result
from pipeline.models.labor_dto import LaborDTO


@dataclass
class LaborMetrics:
    """
    Calculated labor metrics with grading.

    Attributes:
        total_hours: Total hours worked by all employees
        labor_cost: Total labor cost for the period
        labor_percentage: Labor cost as percentage of sales
        status: Status level (EXCELLENT/GOOD/WARNING/CRITICAL/SEVERE)
        grade: Letter grade (A+ to F)
        warnings: List of warning messages
        recommendations: List of actionable recommendations
    """
    total_hours: float
    labor_cost: float
    labor_percentage: float
    status: str
    grade: str
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class LaborCalculator:
    """
    Calculates labor metrics with threshold analysis.

    Thresholds (from V3):
    - Excellent: ≤20%
    - Good: ≤25%
    - Warning: ≤30%
    - Critical: ≤35%
    - Severe: >40%

    Grade Mapping (from V3):
    - A+: ≤18%
    - A: ≤20%
    - B+: ≤23%
    - B: ≤25%
    - C+: ≤28%
    - C: ≤30%
    - D+: ≤33%
    - D: ≤35%
    - F: >35%
    """

    # Thresholds from V3 labor_analyzer.py
    THRESHOLDS = {
        'excellent': 20.0,
        'good': 25.0,
        'warning': 30.0,
        'critical': 35.0,
        'severe': 40.0
    }

    # Grade boundaries from V3 labor_analyzer.get_grade()
    GRADE_BOUNDARIES = [
        (18.0, 'A+'),
        (20.0, 'A'),
        (23.0, 'B+'),
        (25.0, 'B'),
        (28.0, 'C+'),
        (30.0, 'C'),
        (33.0, 'D+'),
        (35.0, 'D'),
        (float('inf'), 'F')
    ]

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize calculator with optional configuration.

        Args:
            config: Optional configuration for custom thresholds
        """
        self.config = config or {}

        # Allow threshold overrides from config
        self.thresholds = {
            'excellent': self.config.get('labor_excellent_threshold', self.THRESHOLDS['excellent']),
            'good': self.config.get('labor_good_threshold', self.THRESHOLDS['good']),
            'warning': self.config.get('labor_warning_threshold', self.THRESHOLDS['warning']),
            'critical': self.config.get('labor_critical_threshold', self.THRESHOLDS['critical']),
            'severe': self.config.get('labor_severe_threshold', self.THRESHOLDS['severe']),
        }

    def calculate(self, labor_dto: LaborDTO, sales: float) -> Result[LaborMetrics]:
        """
        Calculate labor metrics with grading.

        Ported from V3:
        - labor_processor.process(): Basic calculations
        - labor_analyzer.analyze(): Threshold analysis

        Args:
            labor_dto: Labor data containing hours and costs
            sales: Total sales for the period

        Returns:
            Result[LaborMetrics]: Calculated metrics or error

        Errors:
            ValueError: If sales <= 0 or labor_cost < 0
        """
        # Validation
        if sales <= 0:
            return Result.fail(ValueError("Sales must be positive"))

        if labor_dto.total_labor_cost < 0:
            return Result.fail(ValueError("Labor cost cannot be negative"))

        if labor_dto.total_hours_worked < 0:
            return Result.fail(ValueError("Hours worked cannot be negative"))

        # Calculate percentage (from V3 labor_analyzer.calculate_percentage)
        labor_percentage = (labor_dto.total_labor_cost / sales) * 100

        # Get status and grade (from V3 labor_analyzer)
        status = self._get_status(labor_percentage)
        grade = self._get_grade(labor_percentage)

        # Generate warnings (from V3 labor_processor.process)
        warnings = self._generate_warnings(labor_percentage)

        # Generate recommendations (from V3 labor_analyzer.analyze)
        recommendations = self._generate_recommendations(labor_percentage, status)

        metrics = LaborMetrics(
            total_hours=labor_dto.total_hours_worked,
            labor_cost=labor_dto.total_labor_cost,
            labor_percentage=labor_percentage,
            status=status,
            grade=grade,
            warnings=warnings,
            recommendations=recommendations
        )

        return Result.ok(metrics)

    def _get_status(self, percentage: float) -> str:
        """
        Map percentage to status level.

        Ported from V3 labor_analyzer.get_status()

        Args:
            percentage: Labor percentage

        Returns:
            Status string (EXCELLENT/GOOD/WARNING/CRITICAL/SEVERE)
        """
        if percentage <= self.thresholds['excellent']:
            return 'EXCELLENT'
        elif percentage <= self.thresholds['good']:
            return 'GOOD'
        elif percentage <= self.thresholds['warning']:
            return 'WARNING'
        elif percentage <= self.thresholds['critical']:
            return 'CRITICAL'
        else:
            return 'SEVERE'

    def _get_grade(self, percentage: float) -> str:
        """
        Convert percentage to letter grade.

        Ported from V3 labor_analyzer.get_grade()

        Args:
            percentage: Labor percentage

        Returns:
            Letter grade (A+ to F)
        """
        for boundary, grade in self.GRADE_BOUNDARIES:
            if percentage <= boundary:
                return grade
        return 'F'  # Fallback (should never reach here)

    def _generate_warnings(self, percentage: float) -> list[str]:
        """
        Generate warning messages based on percentage.

        Ported from V3 labor_processor.process() warnings logic

        Args:
            percentage: Labor percentage

        Returns:
            List of warning messages
        """
        warnings = []

        # Generate warnings based on thresholds
        # Check from highest to lowest to ensure correct warning level
        if percentage > self.thresholds['critical']:
            # SEVERE: > 35%
            warnings.append(
                f"SEVERE: Labor percentage ({percentage:.1f}%) exceeds severe threshold "
                f"({self.thresholds['critical']}%)"
            )
        elif percentage > self.thresholds['warning']:
            # CRITICAL: 30.01-35%
            warnings.append(
                f"CRITICAL: Labor percentage ({percentage:.1f}%) exceeds critical threshold "
                f"({self.thresholds['warning']}%)"
            )
        elif percentage > self.thresholds['good']:
            # WARNING: 25.01-30%
            warnings.append(
                f"WARNING: Labor percentage ({percentage:.1f}%) exceeds warning threshold "
                f"({self.thresholds['good']}%)"
            )
        elif percentage > self.thresholds['excellent']:
            # GOOD: 20.01-25% gets NOTICE
            warnings.append(
                f"NOTICE: Labor percentage ({percentage:.1f}%) exceeds target "
                f"({self.thresholds['good']}%)"
            )
        # EXCELLENT: ≤ 20% gets no warnings

        return warnings

    def _generate_recommendations(self, percentage: float, status: str) -> list[str]:
        """
        Generate actionable recommendations based on status.

        Ported from V3 labor_analyzer.analyze() recommendations logic

        Args:
            percentage: Labor percentage
            status: Current status level

        Returns:
            List of recommendations
        """
        recommendations = []

        if status == 'EXCELLENT':
            recommendations.append("Labor cost is excellent. Maintain current staffing levels.")
            recommendations.append("Monitor for understaffing - ensure service quality remains high.")

        elif status == 'GOOD':
            recommendations.append("Labor cost is within acceptable range.")
            recommendations.append("Look for minor optimization opportunities in scheduling.")

        elif status == 'WARNING':
            recommendations.append("Labor cost is elevated. Review staffing levels.")
            recommendations.append("Analyze busy periods - ensure appropriate staffing distribution.")
            recommendations.append("Consider cross-training to improve flexibility.")

        elif status == 'CRITICAL':
            recommendations.append("URGENT: Labor cost is critically high.")
            recommendations.append("Immediate action required: Review all shifts for overstaffing.")
            recommendations.append("Verify no overtime or auto-clockout issues.")
            recommendations.append("Compare to historical patterns to identify anomalies.")

        elif status == 'SEVERE':
            recommendations.append("CRITICAL ALERT: Labor cost is severely elevated.")
            recommendations.append("Emergency review required: Check for data errors or system issues.")
            recommendations.append("Investigate potential causes: overtime, auto-clockout, payroll errors.")
            recommendations.append("Management intervention required immediately.")

        return recommendations

    def calculate_target_hours(self, sales: float, target_percentage: float = 25.0) -> Result[float]:
        """
        Calculate target labor hours for a given sales amount and target percentage.

        Helper function for planning and recommendations.

        Args:
            sales: Target sales amount
            target_percentage: Target labor percentage (default: 25%)

        Returns:
            Result[float]: Target labor hours or error
        """
        if sales <= 0:
            return Result.fail(ValueError("Sales must be positive"))

        if target_percentage <= 0 or target_percentage >= 100:
            return Result.fail(ValueError("Target percentage must be between 0 and 100"))

        # This is a simplified calculation - actual implementation would need
        # average hourly wage from configuration or historical data
        # For now, we just document the interface
        return Result.fail(NotImplementedError(
            "Target hours calculation requires average wage data - "
            "to be implemented in future iteration"
        ))
