"""
TimeslotGradingStage - Pipeline stage for timeslot analysis.

Creates 15-minute timeslots, grades them, and stores results in context.
Integrates TimeslotWindower and TimeslotGrader into the V4 pipeline.
"""

import time
from typing import Dict, Optional
from datetime import datetime

from pipeline.orchestration.pipeline.stage import PipelineStage
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.services.timeslot_windower import TimeslotWindower
from pipeline.services.timeslot_grader import TimeslotGrader
from pipeline.services.patterns.timeslot_pattern_manager import TimeslotPatternManager
from pipeline.services.result import Result
from pipeline.services.errors import ProcessingError
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


class TimeslotGradingStage(PipelineStage):
    """
    Pipeline stage that creates and grades 15-minute timeslots.

    Flow:
    1. Get categorized orders from context
    2. Load learned patterns for this day of week (if available)
    3. Create 15-minute timeslots (64 total: 32 morning + 32 evening)
    4. Grade each timeslot against standards (and patterns if available)
    5. Store timeslot data and graded timeslots in context for downstream stages

    Context Input:
    - categorized_orders: List[OrderDTO] (from OrderCategorizationStage)
    - date: Business date string
    - restaurant: Restaurant code

    Context Output:
    - timeslots: Dict[str, List[TimeslotDTO]] with 'morning' and 'evening' keys
    - graded_timeslots: List[GradedTimeslot] for pattern learning
    - timeslot_metrics: Dict with summary metrics
    - timeslot_capacity: Dict with capacity analysis
    """

    def __init__(
        self,
        windower: TimeslotWindower = None,
        grader: TimeslotGrader = None,
        pattern_manager: Optional[TimeslotPatternManager] = None
    ):
        """
        Initialize the timeslot grading stage.

        Args:
            windower: TimeslotWindower instance (optional, creates default if None)
            grader: TimeslotGrader instance (optional, creates default if None)
            pattern_manager: TimeslotPatternManager for loading learned patterns (optional)
        """
        super().__init__()
        self.windower = windower or TimeslotWindower()
        self.grader = grader or TimeslotGrader()
        self.pattern_manager = pattern_manager

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute timeslot grading stage.

        Args:
            context: Pipeline context with categorized orders

        Returns:
            Result[PipelineContext]: Updated context with timeslot data
        """
        start_time = time.time()

        # Get required data from context
        restaurant = context.get('restaurant')
        date = context.get('date')
        categorized_orders = context.get('categorized_orders')

        # Bind logger to context
        bound_logger = logger.bind(
            restaurant=restaurant,
            date=date,
            stage='timeslot_grading'
        )

        bound_logger.info("timeslot_grading_started")

        # Validate required data
        if not categorized_orders:
            return Result.fail(
                ProcessingError(
                    "Missing 'categorized_orders' in context. Run OrderCategorizationStage first.",
                    context={'restaurant': restaurant, 'date': date}
                )
            )

        if not date:
            return Result.fail(
                ProcessingError(
                    "Missing 'date' in context.",
                    context={'restaurant': restaurant}
                )
            )

        try:
            # Get time entries for server counting (optional)
            time_entries = context.get('time_entries', [])

            # STEP 1: Create timeslots from categorized orders
            bound_logger.info("creating_timeslots", order_count=len(categorized_orders))

            timeslots_result = self.windower.create_timeslots(categorized_orders, date, time_entries)

            if timeslots_result.is_err():
                return Result.fail(timeslots_result.unwrap_err())

            timeslots = timeslots_result.unwrap()

            # STEP 2: Load learned patterns for this day of week (if pattern manager available)
            timeslot_patterns = self._load_timeslot_patterns(restaurant, date)

            # STEP 3: Grade all timeslots
            bound_logger.info("grading_timeslots",
                            morning_slots=len(timeslots['morning']),
                            evening_slots=len(timeslots['evening']),
                            has_patterns=bool(timeslot_patterns))

            graded_timeslots_dict = self.grader.grade_all_timeslots(timeslots, timeslot_patterns)

            # STEP 3.5: Flatten graded timeslots for pattern learning
            graded_timeslots_list = []
            graded_timeslots_list.extend(graded_timeslots_dict.get('morning', []))
            graded_timeslots_list.extend(graded_timeslots_dict.get('evening', []))

            # STEP 4: Calculate summary metrics
            metrics = self._calculate_summary_metrics(graded_timeslots_dict)

            # STEP 5: Calculate capacity analysis
            capacity = self.windower.calculate_capacity_metrics(graded_timeslots_dict)

            # STEP 5.5: Calculate shift-level category statistics (unique orders only)
            shift_category_stats = self._calculate_shift_category_stats(
                categorized_orders,
                graded_timeslots_dict
            )

            # STEP 6: Store in context
            context.set('timeslots', graded_timeslots_dict)
            context.set('graded_timeslots', graded_timeslots_list)  # For pattern learning
            context.set('timeslot_metrics', metrics)
            context.set('timeslot_capacity', capacity)
            context.set('shift_category_stats', shift_category_stats)  # NEW: Shift-level category stats

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            bound_logger.info("timeslot_grading_complete",
                            total_slots=metrics['total_slots'],
                            active_slots=metrics['active_slots'],
                            passed_standards=metrics['passed_standards'],
                            morning_pass_rate=metrics['morning_pass_rate'],
                            evening_pass_rate=metrics['evening_pass_rate'],
                            duration_ms=round(duration_ms, 0))

            return Result.ok(context)

        except Exception as e:
            bound_logger.error("timeslot_grading_failed", error=str(e))
            return Result.fail(
                ProcessingError(
                    f"Timeslot grading failed: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def _load_timeslot_patterns(self, restaurant: str, date: str) -> Dict:
        """
        Load learned timeslot patterns for this restaurant and day of week.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)

        Returns:
            Dict of patterns organized by timeslot and category,
            or empty dict if no pattern manager or invalid date
        """
        if self.pattern_manager is None:
            return {}

        try:
            # Parse date to get day of week
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date_obj.strftime("%A")  # "Monday", "Tuesday", etc.

            # Get patterns for this restaurant and day
            patterns = self.pattern_manager.get_patterns_for_day(
                restaurant_code=restaurant,
                day_of_week=day_of_week,
                reliable_only=True
            )

            return patterns

        except ValueError:
            logger.warning("timeslot_pattern_load_failed",
                         reason=f"Invalid date format: {date}")
            return {}

    def _calculate_shift_category_stats(
        self,
        categorized_orders: list,
        graded_timeslots: Dict
    ) -> Dict:
        """
        Calculate pass/fail statistics per category per shift from UNIQUE orders.

        This avoids double-counting issues from overlapping timeslot windows.

        Args:
            categorized_orders: List[OrderDTO] - unique orders before windowing
            graded_timeslots: Dict with graded timeslots containing failure info

        Returns:
            Dict with structure:
            {
                'Morning': {
                    'Lobby': {'total': 50, 'passed': 45, 'failed': 5},
                    'Drive-Thru': {'total': 120, 'passed': 115, 'failed': 5},
                    'ToGo': {'total': 80, 'passed': 68, 'failed': 12}
                },
                'Evening': { ... }
            }
        """
        SHIFT_CUTOFF_HOUR = 14  # Morning: hour < 14, Evening: hour >= 14

        # Initialize stats structure
        stats = {
            'Morning': {
                'Lobby': {'total': 0, 'passed': 0, 'failed': 0},
                'Drive-Thru': {'total': 0, 'passed': 0, 'failed': 0},
                'ToGo': {'total': 0, 'passed': 0, 'failed': 0}
            },
            'Evening': {
                'Lobby': {'total': 0, 'passed': 0, 'failed': 0},
                'Drive-Thru': {'total': 0, 'passed': 0, 'failed': 0},
                'ToGo': {'total': 0, 'passed': 0, 'failed': 0}
            }
        }

        # Build set of check_numbers that failed standards
        failed_check_numbers = set()
        for shift_name in ['morning', 'evening']:
            for timeslot in graded_timeslots.get(shift_name, []):
                for failure in timeslot.failures:
                    # Only count standard failures (not historical pattern failures)
                    if failure.get('failed_standard', False):
                        failed_check_numbers.add(failure.get('check_number'))

        # Count unique orders by shift and category
        for order in categorized_orders:
            # Determine shift
            hour = order.order_time.hour
            shift = 'Morning' if hour < SHIFT_CUTOFF_HOUR else 'Evening'

            # Get category
            category = order.category
            if category not in stats[shift]:
                continue  # Skip unknown categories

            # Increment total
            stats[shift][category]['total'] += 1

            # Check if this order failed
            if order.check_number in failed_check_numbers:
                stats[shift][category]['failed'] += 1
            else:
                stats[shift][category]['passed'] += 1

        return stats

    def _calculate_summary_metrics(self, graded_timeslots: Dict) -> Dict:
        """
        Calculate summary metrics across all timeslots.

        Args:
            graded_timeslots: Dict with 'morning' and 'evening' lists of graded TimeslotDTO

        Returns:
            Dict with summary statistics
        """
        morning_slots = graded_timeslots.get('morning', [])
        evening_slots = graded_timeslots.get('evening', [])

        # Count non-empty slots
        morning_non_empty = [s for s in morning_slots if not s.is_empty]
        evening_non_empty = [s for s in evening_slots if not s.is_empty]

        # Count passing slots
        morning_passed = sum(1 for s in morning_non_empty if s.passed_standards)
        evening_passed = sum(1 for s in evening_non_empty if s.passed_standards)

        # Calculate pass rates
        morning_pass_rate = (morning_passed / len(morning_non_empty) * 100) if morning_non_empty else 0
        evening_pass_rate = (evening_passed / len(evening_non_empty) * 100) if evening_non_empty else 0
        overall_pass_rate = ((morning_passed + evening_passed) / (len(morning_non_empty) + len(evening_non_empty)) * 100) if (morning_non_empty or evening_non_empty) else 0

        # Count streaks
        morning_hot = sum(1 for s in morning_non_empty if s.streak_type == 'hot')
        morning_cold = sum(1 for s in morning_non_empty if s.streak_type == 'cold')
        evening_hot = sum(1 for s in evening_non_empty if s.streak_type == 'hot')
        evening_cold = sum(1 for s in evening_non_empty if s.streak_type == 'cold')

        # Total orders
        morning_orders = sum(s.total_orders for s in morning_slots)
        evening_orders = sum(s.total_orders for s in evening_slots)

        # Total failures
        morning_failures = sum(len(s.failures) for s in morning_slots)
        evening_failures = sum(len(s.failures) for s in evening_slots)

        return {
            # Overall
            'total_slots': len(morning_slots) + len(evening_slots),
            'active_slots': len(morning_non_empty) + len(evening_non_empty),
            'passed_standards': morning_passed + evening_passed,
            'overall_pass_rate': round(overall_pass_rate, 2),
            'total_orders': morning_orders + evening_orders,
            'total_failures': morning_failures + evening_failures,

            # Morning
            'morning_total_slots': len(morning_slots),
            'morning_active_slots': len(morning_non_empty),
            'morning_passed': morning_passed,
            'morning_pass_rate': round(morning_pass_rate, 2),
            'morning_hot_streaks': morning_hot,
            'morning_cold_streaks': morning_cold,
            'morning_orders': morning_orders,
            'morning_failures': morning_failures,

            # Evening
            'evening_total_slots': len(evening_slots),
            'evening_active_slots': len(evening_non_empty),
            'evening_passed': evening_passed,
            'evening_pass_rate': round(evening_pass_rate, 2),
            'evening_hot_streaks': evening_hot,
            'evening_cold_streaks': evening_cold,
            'evening_orders': evening_orders,
            'evening_failures': evening_failures,
        }

    def validate(self, context: PipelineContext) -> Result[bool]:
        """
        Validate that context has required data.

        Args:
            context: Pipeline context

        Returns:
            Result[bool]: True if valid, error otherwise
        """
        if not context.has('categorized_orders'):
            return Result.fail(
                ProcessingError(
                    "Missing 'categorized_orders' in context",
                    context={'stage': 'timeslot_grading'}
                )
            )

        if not context.has('date'):
            return Result.fail(
                ProcessingError(
                    "Missing 'date' in context",
                    context={'stage': 'timeslot_grading'}
                )
            )

        return Result.ok(True)

    def rollback(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Rollback timeslot grading by removing data from context.

        Args:
            context: Pipeline context

        Returns:
            Result[PipelineContext]: Context with timeslot data removed
        """
        # Remove timeslot data from context
        if context.has('timeslots'):
            context.data.pop('timeslots', None)

        if context.has('timeslot_metrics'):
            context.data.pop('timeslot_metrics', None)

        if context.has('timeslot_capacity'):
            context.data.pop('timeslot_capacity', None)

        logger.info("timeslot_grading_rolled_back",
                   restaurant=context.get('restaurant'),
                   date=context.get('date'))

        return Result.ok(context)

    def __repr__(self) -> str:
        return "TimeslotGradingStage(windower=TimeslotWindower, grader=TimeslotGrader)"
