"""
Pattern learning pipeline stage.

This stage learns patterns from processed labor data and stores them
using the PatternManager. It follows a resilient error handling approach
where pattern learning failures do not block the pipeline.

Inputs (from context):
- 'labor_metrics': LaborMetrics with calculated metrics
- 'restaurant_code': str
- 'date': str

Outputs (to context):
- 'learned_patterns': List[Pattern] - Successfully learned patterns
- 'pattern_warnings': List[str] - Warnings if pattern learning failed
"""

from typing import Optional, List

from src.orchestration.pipeline import PipelineContext
from src.core.result import Result
from src.core.patterns.manager import PatternManager
from src.models.pattern import Pattern
from src.processing.labor_calculator import LaborMetrics


class PatternLearningStage:
    """
    Pipeline stage for learning patterns from labor data.

    Follows resilient error handling: pattern learning failures
    do not block the pipeline. Warnings are logged to context.

    Dependencies:
    - PatternManager: Injected for pattern learning/storage
    """

    def __init__(self, pattern_manager: PatternManager):
        """
        Initialize pattern learning stage.

        Args:
            pattern_manager: PatternManager instance for learning patterns
        """
        self.pattern_manager = pattern_manager

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute pattern learning stage.

        This stage is resilient - it always returns Result.ok() even if
        pattern learning fails. Failures are logged as warnings in context.

        Args:
            context: Pipeline context with labor_metrics

        Returns:
            Result[PipelineContext]: Always successful (resilient)
        """
        # Get labor metrics from context
        labor_metrics = context.get('labor_metrics')

        # If no metrics available, log warning but continue
        if labor_metrics is None:
            context.set('pattern_warnings', [
                "Pattern learning skipped: labor_metrics not found in context"
            ])
            context.set('learned_patterns', [])
            return Result.ok(context)

        if not isinstance(labor_metrics, LaborMetrics):
            context.set('pattern_warnings', [
                f"Pattern learning skipped: labor_metrics has wrong type ({type(labor_metrics).__name__})"
            ])
            context.set('learned_patterns', [])
            return Result.ok(context)

        # Learn pattern from labor percentage
        learned_patterns: List[Pattern] = []
        warnings: List[str] = []

        # Learn labor percentage pattern
        pattern_result = self._learn_labor_pattern(
            context.restaurant_code,
            context.date,
            labor_metrics
        )

        if pattern_result.is_ok():
            learned_patterns.append(pattern_result.unwrap())
        else:
            # Log warning but continue (resilient)
            error = pattern_result.unwrap_err()
            warnings.append(f"Failed to learn labor pattern: {error}")

        # Store results in context
        context.set('learned_patterns', learned_patterns)
        context.set('pattern_warnings', warnings)

        # Always return success (resilient approach)
        return Result.ok(context)

    def _learn_labor_pattern(
        self,
        restaurant_code: str,
        date: str,
        labor_metrics: LaborMetrics
    ) -> Result[Pattern]:
        """
        Learn labor percentage pattern.

        Args:
            restaurant_code: Restaurant identifier
            date: Business date
            labor_metrics: Calculated labor metrics

        Returns:
            Result[Pattern]: Learned pattern or error
        """
        # Use PatternManager to learn the pattern
        # Pattern type: "labor_percentage"
        # Value: labor percentage from metrics
        pattern_result = self.pattern_manager.learn_pattern(
            restaurant_code=restaurant_code,
            date=date,
            service_type="daily",  # Daily labor pattern
            time_slot="all_day",   # Full day pattern
            metric_type="labor_percentage",
            value=labor_metrics.labor_percentage,
            metadata={
                "labor_cost": labor_metrics.labor_cost,
                "total_hours": labor_metrics.total_hours,
                "status": labor_metrics.status,
                "grade": labor_metrics.grade
            }
        )

        return pattern_result

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"PatternLearningStage(pattern_manager={self.pattern_manager.__class__.__name__})"
