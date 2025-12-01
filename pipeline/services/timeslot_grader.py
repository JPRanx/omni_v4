"""
TimeslotGrader - Grades 15-minute timeslots against standards.

Implements V3's strict grading logic:
- DUAL ASSESSMENT: Fixed standards + learned historical patterns
- STRICT GRADING: ANY failure = timeslot fails
- PURE LOGIC: No external dependencies

Matches V3's timeslot_grader.py exactly.
"""

from typing import Dict, List, Optional
import statistics

from pipeline.models.timeslot_dto import TimeslotDTO
from pipeline.models.order_dto import OrderDTO
from pipeline.services.pass_rate_calculator import PassRateCalculator
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


class TimeslotGrader:
    """
    Grades a single 15-minute timeslot independently.

    Design Philosophy (from V3):
    - STRICT GRADING: ANY failure = timeslot fails (100% required)
    - PURE LOGIC: Only knows about orders and patterns (no external context)
    - DUAL ASSESSMENT: Standards (fixed) + Historical (adaptive)
    """

    def __init__(self, standards: Optional[Dict[str, float]] = None):
        """
        Initialize with business standards.

        Args:
            standards: Target fulfillment times by category
                {'Lobby': 15.0, 'Drive-Thru': 8.0, 'ToGo': 10.0}
                If None, uses defaults
        """
        self.standards = standards or {
            'Lobby': 15.0,      # 15 minutes max for lobby service
            'Drive-Thru': 8.0,  # 8 minutes max for drive-thru
            'ToGo': 10.0        # 10 minutes max for to-go
        }

        logger.info("timeslot_grader_initialized",
                   lobby_standard=self.standards['Lobby'],
                   drive_thru_standard=self.standards['Drive-Thru'],
                   togo_standard=self.standards['ToGo'])

    def grade_timeslot(
        self,
        timeslot: TimeslotDTO,
        timeslot_patterns: Optional[Dict[str, Dict]] = None
    ) -> TimeslotDTO:
        """
        Grade a timeslot against standards and historical patterns.

        Args:
            timeslot: TimeslotDTO to grade
            timeslot_patterns: Learned patterns for this specific timeslot
                {
                    'Lobby': {
                        'baseline_time': 13.2,
                        'variance': 2.1,
                        'confidence': 0.8,
                        'observations_count': 10
                    }
                }

        Returns:
            Updated TimeslotDTO with grading results populated
        """
        if timeslot.is_empty:
            # Empty slot = auto pass (no orders = no failures)
            return self._create_graded_timeslot(
                timeslot,
                passed_standards=True,
                passed_historical=True,
                pass_rate_standards=100.0,
                pass_rate_historical=100.0,
                failures=[],
                by_category={},
                streak_type=None,
                status='pass'  # Empty = auto pass
            )

        # Group orders by category
        orders_by_category = self._group_orders_by_category(timeslot.orders)

        # Grade each category
        by_category = {}
        all_failures = []

        for category in ['Lobby', 'Drive-Thru', 'ToGo']:
            if category not in orders_by_category:
                continue

            orders = orders_by_category[category]
            pattern = timeslot_patterns.get(category, {}) if timeslot_patterns else {}

            result = self._grade_category(
                category=category,
                orders=orders,
                pattern=pattern,
                time_window=timeslot.time_window
            )

            by_category[category] = result['metrics']
            all_failures.extend(result['failures'])

        # Overall pass/fail (STRICT: any failure = slot fails)
        passed_standards = len([f for f in all_failures if f['failed_standard']]) == 0
        passed_historical = len([f for f in all_failures if f['failed_historical']]) == 0

        # Calculate overall pass rates
        total_orders = len(timeslot.orders)
        failed_standards = len([f for f in all_failures if f['failed_standard']])
        failed_historical = len([f for f in all_failures if f['failed_historical']])

        pass_rate_standards = ((total_orders - failed_standards) / total_orders * 100) if total_orders > 0 else 100
        pass_rate_historical = ((total_orders - failed_historical) / total_orders * 100) if total_orders > 0 else 100

        # Sort failures chronologically and flag first
        all_failures.sort(key=lambda f: f['order_time'])
        if all_failures:
            all_failures[0]['is_first_failure'] = True

        # Determine streak type based on pass rate
        streak_type = self._determine_streak(pass_rate_standards)

        # Determine status (pass/warning/fail) for Investigation Modal
        status = PassRateCalculator.get_status_from_pass_rate(pass_rate_standards)

        return self._create_graded_timeslot(
            timeslot,
            passed_standards=passed_standards,
            passed_historical=passed_historical,
            pass_rate_standards=round(pass_rate_standards, 2),
            pass_rate_historical=round(pass_rate_historical, 2),
            failures=all_failures,
            by_category=by_category,
            streak_type=streak_type,
            status=status
        )

    def _grade_category(
        self,
        category: str,
        orders: List[OrderDTO],
        pattern: Dict,
        time_window: str
    ) -> Dict:
        """
        Grade orders of a single category.

        Returns:
            {
                'metrics': {success rates, targets, etc.},
                'failures': [failing orders]
            }
        """
        standard_target = self.standards.get(category, 15.0)

        # Determine if we should use historical pattern
        use_historical = self._should_use_pattern(pattern)

        historical_target = None
        historical_baseline = None
        historical_variance = None
        pattern_confidence = 0.0

        if use_historical:
            historical_baseline = pattern.get('baseline_time', pattern.get('baseline'))
            historical_variance = pattern.get('variance', 0)
            historical_target = historical_baseline + historical_variance
            pattern_confidence = pattern.get('confidence', 0.0)

        # Grade each order
        failed_standard = 0
        failed_historical = 0
        failures = []

        for order in orders:
            fulfillment = order.fulfillment_minutes

            # Check against standard
            fail_std = fulfillment > standard_target
            if fail_std:
                failed_standard += 1

            # Check against historical (if using)
            fail_hist = False
            if use_historical and historical_target is not None:
                fail_hist = fulfillment > historical_target
                if fail_hist:
                    failed_historical += 1

            # Record failure if either failed
            if fail_std or fail_hist:
                failures.append({
                    'check_number': order.check_number,
                    'category': category,
                    'employee_name': order.server,
                    'order_time': order.order_time,
                    'fulfillment_minutes': fulfillment,
                    'failed_standard': fail_std,
                    'failed_historical': fail_hist,
                    'standard_target': standard_target,
                    'historical_target': historical_target,
                    'historical_baseline': historical_baseline,
                    'historical_variance': historical_variance,
                    'pattern_confidence': pattern_confidence,
                    'time_window': time_window,
                    'is_first_failure': False  # Will be set later
                })

        # Calculate success rates
        total = len(orders)
        success_rate_standard = ((total - failed_standard) / total * 100) if total > 0 else 100
        success_rate_historical = ((total - failed_historical) / total * 100) if total > 0 else 100

        return {
            'metrics': {
                'total': total,
                'failed_standard': failed_standard,
                'failed_historical': failed_historical,
                'success_rate_standard': round(success_rate_standard, 2),
                'success_rate_historical': round(success_rate_historical, 2),
                'standard_target': standard_target,
                'historical_target': historical_target,
                'historical_baseline': historical_baseline,
                'historical_variance': historical_variance,
                'pattern_confidence': pattern_confidence
            },
            'failures': failures
        }

    def _should_use_pattern(self, pattern: Dict) -> bool:
        """
        Determine if pattern is reliable enough to use.

        Decision: Confidence >= 0.6 AND observations >= 4
        """
        if not pattern:
            return False

        confidence = pattern.get('confidence', 0)
        observations = pattern.get('observations_count', 0)

        return confidence >= 0.6 and observations >= 4

    def _determine_streak(self, pass_rate: float) -> Optional[str]:
        """
        Determine streak type from pass rate.

        Returns:
            'hot' if pass_rate >= 85%
            'cold' if pass_rate < 70%
            None otherwise
        """
        if pass_rate >= 85:
            return 'hot'
        elif pass_rate < 70:
            return 'cold'
        else:
            return None

    def _group_orders_by_category(self, orders: List[OrderDTO]) -> Dict[str, List[OrderDTO]]:
        """Group orders by category (Lobby/Drive-Thru/ToGo)."""
        grouped = {}
        for order in orders:
            category = order.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(order)
        return grouped

    def _create_graded_timeslot(
        self,
        original: TimeslotDTO,
        passed_standards: bool,
        passed_historical: bool,
        pass_rate_standards: float,
        pass_rate_historical: float,
        failures: List[Dict],
        by_category: Dict,
        streak_type: Optional[str],
        status: Optional[str]
    ) -> TimeslotDTO:
        """
        Create new TimeslotDTO with grading results.

        Since TimeslotDTO is frozen, we need to create a new instance.
        """
        from dataclasses import replace
        return replace(
            original,
            passed_standards=passed_standards,
            passed_historical=passed_historical,
            pass_rate_standards=pass_rate_standards,
            pass_rate_historical=pass_rate_historical,
            failures=failures,
            by_category=by_category,
            streak_type=streak_type,
            status=status
        )

    def grade_all_timeslots(
        self,
        timeslots: Dict[str, List[TimeslotDTO]],
        patterns: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, List[TimeslotDTO]]:
        """
        Grade all timeslots for both shifts.

        Args:
            timeslots: Dict with 'morning' and 'evening' keys
            patterns: Learned patterns by time_window and category
                {
                    '11:00-11:15': {
                        'Lobby': {baseline_time, variance, confidence, observations_count}
                    }
                }

        Returns:
            Dict with graded timeslots
        """
        graded_timeslots = {
            'morning': [],
            'evening': []
        }

        for shift in ['morning', 'evening']:
            for timeslot in timeslots.get(shift, []):
                # Get patterns for this specific timeslot
                slot_patterns = patterns.get(timeslot.time_window, {}) if patterns else {}

                # Grade the timeslot
                graded = self.grade_timeslot(timeslot, slot_patterns)
                graded_timeslots[shift].append(graded)

        # Calculate consecutive streaks
        graded_timeslots = self._calculate_streaks(graded_timeslots)

        logger.info("timeslots_graded",
                   morning_slots=len(graded_timeslots['morning']),
                   evening_slots=len(graded_timeslots['evening']),
                   morning_passed=sum(1 for s in graded_timeslots['morning'] if s.passed_standards),
                   evening_passed=sum(1 for s in graded_timeslots['evening'] if s.passed_standards))

        return graded_timeslots

    def _calculate_streaks(self, timeslots: Dict[str, List[TimeslotDTO]]) -> Dict[str, List[TimeslotDTO]]:
        """
        Calculate consecutive pass/fail streaks across timeslots.

        Streaks are tracked separately for each shift.
        """
        for shift in ['morning', 'evening']:
            slots = timeslots[shift]
            consecutive_passes = 0
            consecutive_fails = 0

            updated_slots = []
            for slot in slots:
                if slot.is_empty:
                    # Empty slots don't break streaks
                    updated_slots.append(slot)
                    continue

                # Update streaks based on pass/fail
                if slot.passed_standards:
                    consecutive_passes += 1
                    consecutive_fails = 0
                else:
                    consecutive_fails += 1
                    consecutive_passes = 0

                # Create updated slot with streak counts
                from dataclasses import replace
                updated_slot = replace(
                    slot,
                    consecutive_passes=consecutive_passes,
                    consecutive_fails=consecutive_fails
                )
                updated_slots.append(updated_slot)

            timeslots[shift] = updated_slots

        return timeslots
