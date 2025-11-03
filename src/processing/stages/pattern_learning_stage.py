"""
Pattern learning pipeline stage.

This stage learns both daily labor patterns and timeslot performance patterns
from processed data. It follows a resilient error handling approach where
pattern learning failures do not block the pipeline.

Inputs (from context):
- 'labor_metrics': LaborMetrics with calculated metrics
- 'graded_timeslots': List[GradedTimeslot] with timeslot grades (optional)
- 'restaurant_code': str
- 'date': str

Outputs (to context):
- 'learned_patterns': List[DailyLaborPattern] - Successfully learned labor patterns
- 'learned_timeslot_patterns': List[TimeslotPattern] - Successfully learned timeslot patterns
- 'pattern_warnings': List[str] - Warnings if pattern learning failed

Architecture Note:
    Week 4 Day 7: Refactored to use DailyLaborPatternManager for daily patterns
    Week 7 Day 1: Extended to learn timeslot patterns using TimeslotPatternManager
"""

from typing import Optional, List
from datetime import datetime
import time

from src.orchestration.pipeline import PipelineContext
from src.core.result import Result
from src.core.patterns.daily_labor_manager import DailyLaborPatternManager
from src.core.patterns.timeslot_pattern_manager import TimeslotPatternManager
from src.models.daily_labor_pattern import DailyLaborPattern
from src.models.timeslot_pattern import TimeslotPattern
from src.processing.labor_calculator import LaborMetrics
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class PatternLearningStage:
    """
    Pipeline stage for learning daily labor and timeslot performance patterns.

    Follows resilient error handling: pattern learning failures
    do not block the pipeline. Warnings are logged to context.

    Dependencies:
    - DailyLaborPatternManager: Injected for daily labor pattern learning
    - TimeslotPatternManager: Injected for timeslot pattern learning
    """

    def __init__(
        self,
        pattern_manager: DailyLaborPatternManager,
        timeslot_pattern_manager: Optional[TimeslotPatternManager] = None
    ):
        """
        Initialize pattern learning stage.

        Args:
            pattern_manager: DailyLaborPatternManager instance for learning daily patterns
            timeslot_pattern_manager: TimeslotPatternManager instance for learning timeslot patterns (optional)
        """
        self.pattern_manager = pattern_manager
        self.timeslot_pattern_manager = timeslot_pattern_manager or TimeslotPatternManager()

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
        start_time = time.time()

        # Bind context
        restaurant = context.get('restaurant', 'UNKNOWN')
        date = context.get('date', 'UNKNOWN')
        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("pattern_learning_started")

        # Get labor metrics from context
        labor_metrics = context.get('labor_metrics')

        # If no metrics available, log warning but continue
        if labor_metrics is None:
            bound_logger.warning("pattern_learning_skipped", reason="labor_metrics not found in context")
            context.set('pattern_warnings', [
                "Pattern learning skipped: labor_metrics not found in context"
            ])
            context.set('learned_patterns', [])
            return Result.ok(context)

        if not isinstance(labor_metrics, LaborMetrics):
            bound_logger.warning("pattern_learning_skipped",
                               reason=f"labor_metrics has wrong type ({type(labor_metrics).__name__})")
            context.set('pattern_warnings', [
                f"Pattern learning skipped: labor_metrics has wrong type ({type(labor_metrics).__name__})"
            ])
            context.set('learned_patterns', [])
            return Result.ok(context)

        # Learn patterns
        learned_patterns: List[DailyLaborPattern] = []
        learned_timeslot_patterns: List[TimeslotPattern] = []
        warnings: List[str] = []

        # Learn daily labor pattern
        pattern_result = self._learn_daily_labor_pattern(
            context.restaurant_code,
            context.date,
            labor_metrics
        )

        if pattern_result.is_ok():
            pattern = pattern_result.unwrap()
            learned_patterns.append(pattern)
            bound_logger.info("daily_pattern_learned",
                            confidence=round(pattern.confidence, 2),
                            observations=pattern.observations)
        else:
            # Log warning but continue (resilient)
            error = pattern_result.unwrap_err()
            warnings.append(f"Failed to learn daily labor pattern: {error}")
            bound_logger.warning("daily_pattern_learning_failed", error=str(error))

        # Learn timeslot patterns if graded timeslots are available
        graded_timeslots = context.get('graded_timeslots')
        if graded_timeslots is not None:
            timeslot_patterns = self._learn_timeslot_patterns(
                context.restaurant_code,
                context.date,
                graded_timeslots
            )
            learned_timeslot_patterns.extend(timeslot_patterns)
            if timeslot_patterns:
                bound_logger.info("timeslot_patterns_learned",
                                count=len(timeslot_patterns))

        # Calculate duration and log completion
        duration_ms = (time.time() - start_time) * 1000
        bound_logger.info("pattern_learning_complete",
                        daily_patterns=len(learned_patterns),
                        timeslot_patterns=len(learned_timeslot_patterns),
                        duration_ms=round(duration_ms, 0))

        # Store results in context
        context.set('learned_patterns', learned_patterns)
        context.set('learned_timeslot_patterns', learned_timeslot_patterns)
        context.set('pattern_warnings', warnings)

        # Always return success (resilient approach)
        return Result.ok(context)

    def _learn_daily_labor_pattern(
        self,
        restaurant_code: str,
        date: str,
        labor_metrics: LaborMetrics
    ) -> Result[DailyLaborPattern]:
        """
        Learn daily labor pattern.

        Args:
            restaurant_code: Restaurant identifier
            date: Business date (YYYY-MM-DD format)
            labor_metrics: Calculated labor metrics

        Returns:
            Result[DailyLaborPattern]: Learned pattern or error
        """
        # Parse date to extract day_of_week
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date_obj.weekday()  # 0=Monday, 6=Sunday
        except ValueError as e:
            from src.core import PatternError
            return Result.fail(PatternError(
                message=f"Invalid date format: {date}",
                context={"date": date, "error": str(e)}
            ))

        # Use DailyLaborPatternManager with proper daily pattern parameters
        pattern_result = self.pattern_manager.learn_pattern(
            restaurant_code=restaurant_code,
            day_of_week=day_of_week,
            observed_labor_percentage=labor_metrics.labor_percentage,
            observed_total_hours=labor_metrics.total_hours
        )

        return pattern_result

    def _learn_timeslot_patterns(
        self,
        restaurant_code: str,
        date: str,
        graded_timeslots: List
    ) -> List[TimeslotPattern]:
        """
        Learn timeslot performance patterns from graded timeslots.

        For each timeslot that passed quality standards, we learn the
        average fulfillment time per category. This builds a baseline
        for adaptive grading in future runs.

        Args:
            restaurant_code: Restaurant identifier
            date: Business date (YYYY-MM-DD format)
            graded_timeslots: List of GradedTimeslot objects

        Returns:
            List of learned TimeslotPattern objects
        """
        # Parse date to extract day_of_week name
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date_obj.strftime("%A")  # "Monday", "Tuesday", etc.
        except ValueError:
            logger.warning("timeslot_pattern_learning_skipped",
                         reason=f"Invalid date format: {date}")
            return []

        learned_patterns = []

        # Learn from each graded timeslot
        for graded_slot in graded_timeslots:
            # Only learn from timeslots that passed quality standards
            # (we want to learn from good performance, not bad)
            if not graded_slot.passed_standards:
                continue

            # Skip empty timeslots
            if graded_slot.is_empty:
                continue

            # Learn patterns for each category in this timeslot
            for category, metrics in graded_slot.by_category.items():
                # Skip if no orders in this category
                order_count = metrics.get('total', 0)
                if order_count == 0:
                    continue

                # Get average fulfillment time from TimeslotDTO's pre-calculated fields
                avg_time = None
                if category == 'Lobby':
                    avg_time = graded_slot.lobby_avg_fulfillment
                elif category == 'Drive-Thru':
                    avg_time = graded_slot.drive_thru_avg_fulfillment
                elif category == 'ToGo':
                    avg_time = graded_slot.togo_avg_fulfillment

                # Skip if no average time available (None or 0)
                if avg_time is None or avg_time <= 0:
                    continue

                # Learn pattern using TimeslotPatternManager
                pattern = self.timeslot_pattern_manager.learn_pattern(
                    restaurant_code=restaurant_code,
                    day_of_week=day_of_week,
                    shift=graded_slot.shift,
                    time_window=graded_slot.time_window,
                    category=category,
                    fulfillment_time=avg_time
                )

                learned_patterns.append(pattern)

        return learned_patterns

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"PatternLearningStage("
                f"pattern_manager={self.pattern_manager.__class__.__name__}, "
                f"timeslot_pattern_manager={self.timeslot_pattern_manager.__class__.__name__})")
