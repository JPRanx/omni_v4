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

import time
from pipeline.orchestration.pipeline import PipelineContext
from pipeline.services.result import Result
from pipeline.services.labor_calculator import LaborCalculator, LaborMetrics
from pipeline.services.shift_splitter import ShiftSplitter
from pipeline.services.auto_clockout_analyzer import AutoClockoutAnalyzer
from pipeline.models.labor_dto import LaborDTO
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


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
        start_time = time.time()

        # Bind context
        restaurant = context.get('restaurant', 'UNKNOWN')
        date = context.get('date', 'UNKNOWN')
        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("processing_started")

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

        # Calculate shift-level breakdown if time entries available
        time_entries = context.get('time_entries', [])
        raw_dataframes = context.get('raw_dataframes', {})
        void_metrics = context.get('void_metrics')  # Get void metrics from ingestion stage

        if len(time_entries) > 0 or raw_dataframes:
            shift_metrics = ShiftSplitter.split_day(
                restaurant_code=restaurant,
                business_date=date,
                daily_sales=float(sales),
                daily_labor=float(labor_dto.total_labor_cost),
                time_entries=time_entries,
                raw_dataframes=raw_dataframes,
                void_metrics=void_metrics
            )

            context.set('shift_metrics', shift_metrics)
            bound_logger.info("shift_split_complete",
                            morning_manager=shift_metrics.morning_manager,
                            evening_manager=shift_metrics.evening_manager)
        else:
            bound_logger.warning("shift_split_skipped",
                               reason="No time entries or order data available")

        # Analyze auto clock-outs if time entries available
        if len(time_entries) > 0:
            auto_clockout_result = AutoClockoutAnalyzer.analyze(
                time_entries=time_entries,
                restaurant_code=restaurant,
                business_date=date
            )

            if auto_clockout_result.is_ok():
                auto_clockout_summary = auto_clockout_result.unwrap()
                context.set('auto_clockout_summary', auto_clockout_summary)

                # Log summary if any auto-clockouts detected
                if auto_clockout_summary.total_detected > 0:
                    bound_logger.warning("auto_clockouts_detected",
                                       count=auto_clockout_summary.total_detected,
                                       cost_impact=round(auto_clockout_summary.estimated_cost_impact, 2))
            else:
                bound_logger.warning("auto_clockout_analysis_failed",
                                   error=str(auto_clockout_result.unwrap_err()))

        # Calculate duration and log success
        duration_ms = (time.time() - start_time) * 1000

        # Log with alert if labor cost is high
        log_level = "warning" if metrics.labor_percentage > 35 else "info"
        log_method = getattr(bound_logger, log_level)

        log_method("processing_complete",
                   labor_pct=round(metrics.labor_percentage, 1),
                   total_hours=round(metrics.total_hours, 1),
                   status=metrics.status,
                   grade=metrics.grade,
                   duration_ms=round(duration_ms, 0))

        return Result.ok(context)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ProcessingStage(calculator={self.calculator.__class__.__name__})"
