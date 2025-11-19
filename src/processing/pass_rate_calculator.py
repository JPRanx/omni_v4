"""
PassRateCalculator - Calculate pass rates for timeslot orders against baselines.

Determines what percentage of orders met expected performance baselines.
"""

from typing import List, Dict, Optional
from src.models.order_dto import OrderDTO


class PassRateCalculator:
    """
    Calculates pass rates for orders based on baseline comparisons.

    Uses learned patterns to determine if orders met expected performance thresholds.
    """

    # Performance thresholds
    PASS_THRESHOLD = 0.85  # >= 85% pass rate = "pass"
    WARNING_THRESHOLD = 0.70  # >= 70% pass rate = "warning"
    # < 70% pass rate = "fail"

    # Tolerance for meeting baseline (15% buffer)
    BASELINE_TOLERANCE = 1.15  # Allow up to 115% of baseline time

    @classmethod
    def calculate_pass_rate(
        cls,
        orders: List[OrderDTO],
        learned_patterns: Optional[Dict[str, Dict]] = None
    ) -> Dict:
        """
        Calculate pass rate for a list of orders.

        Args:
            orders: List of orders to evaluate
            learned_patterns: Optional dict of baseline times by category
                Format: {'Lobby': {'baseline_time': 12.5, ...}, ...}

        Returns:
            Dict with:
                - pass_rate: Percentage of orders that passed (0-100)
                - passing_count: Number of orders that passed
                - failing_count: Number of orders that failed
                - total_count: Total orders evaluated
                - status: 'pass', 'warning', or 'fail'
                - by_category: Pass rates broken down by category
        """
        if not orders:
            return {
                'pass_rate': 100.0,  # No orders = perfect score
                'passing_count': 0,
                'failing_count': 0,
                'total_count': 0,
                'status': 'pass',
                'by_category': {}
            }

        # If no learned patterns, use fixed standards
        if not learned_patterns:
            return cls._calculate_pass_rate_fixed_standards(orders)

        # Evaluate each order against learned baseline
        passing = 0
        failing = 0
        by_category = {}

        for order in orders:
            category = order.category
            actual_time = order.fulfillment_minutes

            # Get baseline for this category
            if category in learned_patterns:
                baseline_time = learned_patterns[category].get('baseline_time')

                if baseline_time:
                    # Check if order met threshold
                    max_allowed = baseline_time * cls.BASELINE_TOLERANCE

                    if actual_time <= max_allowed:
                        passing += 1
                    else:
                        failing += 1

                    # Track by category
                    if category not in by_category:
                        by_category[category] = {'passing': 0, 'failing': 0}

                    if actual_time <= max_allowed:
                        by_category[category]['passing'] += 1
                    else:
                        by_category[category]['failing'] += 1
                else:
                    # No baseline available, count as passing
                    passing += 1
            else:
                # No pattern for this category, count as passing
                passing += 1

        total = len(orders)
        pass_rate = (passing / total * 100) if total > 0 else 100.0

        # Determine status
        if pass_rate >= cls.PASS_THRESHOLD * 100:
            status = 'pass'
        elif pass_rate >= cls.WARNING_THRESHOLD * 100:
            status = 'warning'
        else:
            status = 'fail'

        # Calculate per-category pass rates
        category_rates = {}
        for cat, counts in by_category.items():
            cat_total = counts['passing'] + counts['failing']
            cat_rate = (counts['passing'] / cat_total * 100) if cat_total > 0 else 100.0
            category_rates[cat] = {
                'pass_rate': round(cat_rate, 1),
                'passing': counts['passing'],
                'failing': counts['failing']
            }

        return {
            'pass_rate': round(pass_rate, 1),
            'passing_count': passing,
            'failing_count': failing,
            'total_count': total,
            'status': status,
            'by_category': category_rates
        }

    @classmethod
    def _calculate_pass_rate_fixed_standards(cls, orders: List[OrderDTO]) -> Dict:
        """
        Calculate pass rate using fixed standards (fallback when no patterns exist).

        Fixed standards (from V3):
        - Lobby: 15 minutes
        - Drive-Thru: 8 minutes
        - ToGo: 10 minutes

        Args:
            orders: List of orders to evaluate

        Returns:
            Dict with pass rate metrics
        """
        FIXED_STANDARDS = {
            'Lobby': 15.0,
            'Drive-Thru': 8.0,
            'ToGo': 10.0
        }

        passing = 0
        failing = 0
        by_category = {}

        for order in orders:
            category = order.category
            actual_time = order.fulfillment_minutes

            # Get fixed standard for this category
            standard = FIXED_STANDARDS.get(category, 15.0)  # Default 15 min
            max_allowed = standard * cls.BASELINE_TOLERANCE

            if actual_time <= max_allowed:
                passing += 1
            else:
                failing += 1

            # Track by category
            if category not in by_category:
                by_category[category] = {'passing': 0, 'failing': 0}

            if actual_time <= max_allowed:
                by_category[category]['passing'] += 1
            else:
                by_category[category]['failing'] += 1

        total = len(orders)
        pass_rate = (passing / total * 100) if total > 0 else 100.0

        # Determine status
        if pass_rate >= cls.PASS_THRESHOLD * 100:
            status = 'pass'
        elif pass_rate >= cls.WARNING_THRESHOLD * 100:
            status = 'warning'
        else:
            status = 'fail'

        # Calculate per-category pass rates
        category_rates = {}
        for cat, counts in by_category.items():
            cat_total = counts['passing'] + counts['failing']
            cat_rate = (counts['passing'] / cat_total * 100) if cat_total > 0 else 100.0
            category_rates[cat] = {
                'pass_rate': round(cat_rate, 1),
                'passing': counts['passing'],
                'failing': counts['failing'],
                'standard': FIXED_STANDARDS.get(cat, 15.0)
            }

        return {
            'pass_rate': round(pass_rate, 1),
            'passing_count': passing,
            'failing_count': failing,
            'total_count': total,
            'status': status,
            'by_category': category_rates
        }

    @classmethod
    def get_status_from_pass_rate(cls, pass_rate: float) -> str:
        """
        Determine status string from pass rate.

        Args:
            pass_rate: Pass rate percentage (0-100)

        Returns:
            'pass', 'warning', or 'fail'
        """
        if pass_rate >= cls.PASS_THRESHOLD * 100:
            return 'pass'
        elif pass_rate >= cls.WARNING_THRESHOLD * 100:
            return 'warning'
        else:
            return 'fail'
