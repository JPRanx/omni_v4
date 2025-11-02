"""
Processing pipeline stage for labor metrics calculation.

This stage:
1. Retrieves labor_dto and sales from PipelineContext
2. Calculates labor metrics using LaborCalculator
3. Stores results back in PipelineContext
4. Returns Result[PipelineContext] following PipelineStage protocol

Inputs (from context):
- 'labor_dto': LaborDTO with hours and costs
- 'sales': float with total sales

Outputs (to context):
- 'labor_metrics': LaborMetrics with calculated metrics and grading
"""

from src.orchestration.pipeline import PipelineContext
from src.core.result import Result
from src.processing.labor_calculator import LaborCalculator, LaborMetrics
from src.models.labor_dto import LaborDTO


class ProcessingStage:
    """
    Pipeline stage for processing labor data.

    Follows PipelineStage protocol:
    - execute(context) -> Result[PipelineContext]
    - Reads inputs from context
    - Performs calculations
    - Stores outputs in context
    - Returns Result with updated context

    Dependencies:
    - LaborCalculator: Injected for calculating metrics
    """

    def __init__(self, calculator: LaborCalculator):
        """
        Initialize processing stage.

        Args:
            calculator: LaborCalculator instance for metrics calculation
        """
        self.calculator = calculator

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute processing stage.

        Args:
            context: Pipeline context with labor_dto and sales

        Returns:
            Result[PipelineContext]: Updated context or error

        Errors:
            ValueError: If required inputs missing from context
            Any error from LaborCalculator.calculate()
        """
        # Get inputs from context
        labor_dto = context.get('labor_dto')
        sales = context.get('sales')

        # Validate inputs
        if labor_dto is None:
            return Result.fail(
                ValueError(
                    "labor_dto not found in context. "
                    "Ensure IngestionStage runs before ProcessingStage."
                )
            )

        if not isinstance(labor_dto, LaborDTO):
            return Result.fail(
                TypeError(
                    f"labor_dto must be LaborDTO, got {type(labor_dto).__name__}"
                )
            )

        if sales is None:
            return Result.fail(
                ValueError(
                    "sales not found in context. "
                    "Ensure sales data is available before ProcessingStage."
                )
            )

        if not isinstance(sales, (int, float)):
            return Result.fail(
                TypeError(
                    f"sales must be numeric, got {type(sales).__name__}"
                )
            )

        # Calculate labor metrics
        metrics_result = self.calculator.calculate(labor_dto, float(sales))

        if metrics_result.is_err():
            return Result.fail(metrics_result.unwrap_err())

        metrics = metrics_result.unwrap()

        # Store results in context
        context.set('labor_metrics', metrics)

        # Also store summary for easy access
        context.set('labor_percentage', metrics.labor_percentage)
        context.set('labor_status', metrics.status)
        context.set('labor_grade', metrics.grade)

        return Result.ok(context)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ProcessingStage(calculator={self.calculator.__class__.__name__})"
