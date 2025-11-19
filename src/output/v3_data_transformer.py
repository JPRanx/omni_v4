"""
V3DataTransformer - Transform pipeline outputs to V3 Investigation Modal format.

Converts internal DTOs to the exact format expected by the V3 Investigation Modal:
- Daily P&L summary (Level 1)
- Shift breakdown with managers (Level 2)
- Timeslot analysis with failures (Level 3)
"""

from typing import Dict, List, Optional
from src.models.shift_metrics_dto import ShiftMetricsDTO
from src.models.timeslot_dto import TimeslotDTO
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class V3DataTransformer:
    """
    Transforms V4 pipeline outputs into V3 Investigation Modal format.

    The V3 Investigation Modal expects a specific nested structure:
    - Top level: Daily P&L metrics
    - Second level: Morning/Evening shift breakdown
    - Third level: 15-minute timeslot analysis with failure details
    """

    @classmethod
    def transform_day(
        cls,
        daily_metrics,  # Daily P&L metrics (dict or DTO)
        shift_metrics: Optional[ShiftMetricsDTO],
        timeslots: Dict[str, List[TimeslotDTO]],
        restaurant_code: str,
        business_date: str
    ) -> Dict:
        """
        Transform a single day's data to V3 format.

        Note: This method is currently unused. Use transform_from_json instead.

        Args:
            daily_metrics: Daily P&L metrics (dict or DTO)
            shift_metrics: Shift breakdown (optional)
            timeslots: Dict with 'morning' and 'evening' timeslot lists
            restaurant_code: Restaurant code
            business_date: str (YYYY-MM-DD)

        Returns:
            Dict in V3 Investigation Modal format
        """
        bound_logger = logger.bind(restaurant=restaurant_code, date=business_date)

        # Level 1: Daily P&L
        daily_data = {
            'date': business_date,
            'restaurant': restaurant_code,
            'sales': round(daily_metrics.net_sales, 2),
            'labor': round(daily_metrics.total_labor_cost, 2),
            'laborPercent': round(daily_metrics.labor_percent, 1),
            'cogs': round(daily_metrics.cogs, 2) if daily_metrics.cogs else 0.0,
            'cogsPercent': round(daily_metrics.cogs_percent, 1) if daily_metrics.cogs_percent else 0.0,
            'profit': round(daily_metrics.profit, 2),
            'profitMargin': round(daily_metrics.profit_margin, 1)
        }

        # Level 2: Shift breakdown
        if shift_metrics:
            daily_data['shifts'] = shift_metrics.to_dict()
            bound_logger.debug("shift_data_added",
                             morning_manager=shift_metrics.morning_manager,
                             evening_manager=shift_metrics.evening_manager)
        else:
            # No shift data available
            daily_data['shifts'] = {
                'morning': cls._empty_shift_data(),
                'evening': cls._empty_shift_data()
            }
            bound_logger.warning("no_shift_data_available")

        # Level 3: Timeslot analysis
        timeslot_list = []

        # Add morning timeslots
        for timeslot in timeslots.get('morning', []):
            timeslot_data = cls._transform_timeslot(timeslot)
            timeslot_list.append(timeslot_data)

        # Add evening timeslots
        for timeslot in timeslots.get('evening', []):
            timeslot_data = cls._transform_timeslot(timeslot)
            timeslot_list.append(timeslot_data)

        daily_data['timeslots'] = timeslot_list

        bound_logger.info("v3_transform_complete",
                        timeslot_count=len(timeslot_list),
                        has_shift_data=shift_metrics is not None)

        return daily_data

    @classmethod
    def _transform_timeslot(cls, timeslot: TimeslotDTO) -> Dict:
        """
        Transform a single timeslot to V3 format.

        Args:
            timeslot: TimeslotDTO from pipeline

        Returns:
            Dict in V3 timeslot format
        """
        # Handle empty timeslots
        if timeslot.is_empty:
            return {
                'timeWindow': timeslot.time_window,
                'shift': timeslot.shift,
                'isEmpty': True,
                'status': 'pass',  # Empty = auto pass
                'totalOrders': 0,
                'passRate': 100.0,
                'activeServers': timeslot.active_servers,
                'activeCooks': timeslot.active_cooks,
                'totalStaff': timeslot.total_staff,
                'failures': [],
                'byCategory': {}
            }

        # Transform failures list
        failures = cls._transform_failures(timeslot.failures)

        # Transform by_category metrics
        by_category = cls._transform_category_metrics(timeslot.by_category)

        return {
            'timeWindow': timeslot.time_window,
            'shift': timeslot.shift,
            'isEmpty': False,
            'status': timeslot.status or 'pass',  # 'pass', 'warning', 'fail'
            'totalOrders': timeslot.total_orders,
            'passRate': timeslot.pass_rate_standards,
            'passRateHistorical': timeslot.pass_rate_historical,
            'passedStandards': timeslot.passed_standards,
            'passedHistorical': timeslot.passed_historical,
            'activeServers': timeslot.active_servers,
            'activeCooks': timeslot.active_cooks,
            'totalStaff': timeslot.total_staff,
            'consecutivePasses': timeslot.consecutive_passes,
            'consecutiveFails': timeslot.consecutive_fails,
            'streakType': timeslot.streak_type,  # 'hot', 'cold', or None
            'failures': failures,
            'byCategory': by_category
        }

    @classmethod
    def _transform_failures(cls, failures: List[Dict]) -> List[Dict]:
        """
        Transform failure list to V3 format.

        Args:
            failures: List of failure dicts from TimeslotGrader

        Returns:
            List of failures in V3 format
        """
        if not failures:
            return []

        transformed = []
        for failure in failures:
            transformed.append({
                'checkNumber': failure.get('check_number', ''),
                'category': failure.get('category', ''),
                'employeeName': failure.get('employee_name', ''),
                'orderTime': failure.get('order_time', ''),
                'fulfillmentMinutes': round(failure.get('fulfillment_minutes', 0), 1),
                'failedStandard': failure.get('failed_standard', False),
                'failedHistorical': failure.get('failed_historical', False),
                'standardTarget': failure.get('standard_target'),
                'historicalTarget': failure.get('historical_target'),
                'historicalBaseline': failure.get('historical_baseline'),
                'historicalVariance': failure.get('historical_variance'),
                'patternConfidence': failure.get('pattern_confidence', 0),
                'isFirstFailure': failure.get('is_first_failure', False)
            })

        return transformed

    @classmethod
    def _transform_category_metrics(cls, by_category: Dict) -> Dict:
        """
        Transform category metrics to V3 format.

        Args:
            by_category: Dict of category metrics from TimeslotGrader

        Returns:
            Dict of category metrics in V3 format
        """
        if not by_category:
            return {}

        transformed = {}
        for category, metrics in by_category.items():
            transformed[category] = {
                'total': metrics.get('total', 0),
                'failedStandard': metrics.get('failed_standard', 0),
                'failedHistorical': metrics.get('failed_historical', 0),
                'successRateStandard': metrics.get('success_rate_standard', 100.0),
                'successRateHistorical': metrics.get('success_rate_historical', 100.0),
                'standardTarget': metrics.get('standard_target'),
                'historicalTarget': metrics.get('historical_target'),
                'historicalBaseline': metrics.get('historical_baseline'),
                'historicalVariance': metrics.get('historical_variance'),
                'patternConfidence': metrics.get('pattern_confidence', 0)
            }

        return transformed

    @classmethod
    def _empty_shift_data(cls) -> Dict:
        """
        Create empty shift data structure.

        Returns:
            Dict with empty shift metrics
        """
        return {
            'sales': 0.0,
            'labor': 0.0,
            'laborPercent': 0.0,
            'manager': 'Not Assigned',
            'voids': 0,
            'orderCount': 0,
            'avgOrderValue': 0.0
        }

    @classmethod
    def transform_date_range(
        cls,
        pipeline_results: List[Dict],
        restaurant_code: str
    ) -> List[Dict]:
        """
        Transform multiple days of pipeline results to V3 format.

        Args:
            pipeline_results: List of pipeline output dicts
            restaurant_code: Restaurant code

        Returns:
            List of days in V3 format
        """
        transformed_days = []

        for result in pipeline_results:
            # Extract data from pipeline result
            daily_metrics = result.get('daily_metrics')
            shift_metrics = result.get('shift_metrics')
            timeslots = result.get('timeslots', {'morning': [], 'evening': []})
            business_date = result.get('date')

            if not daily_metrics or not business_date:
                logger.warning("missing_required_data",
                             date=business_date,
                             has_daily_metrics=bool(daily_metrics))
                continue

            # Transform to V3 format
            day_data = cls.transform_day(
                daily_metrics=daily_metrics,
                shift_metrics=shift_metrics,
                timeslots=timeslots,
                restaurant_code=restaurant_code,
                business_date=business_date
            )

            transformed_days.append(day_data)

        logger.info("date_range_transformed",
                   restaurant=restaurant_code,
                   day_count=len(transformed_days))

        return transformed_days

    @classmethod
    def transform_from_json(
        cls,
        run_data: Dict,
        restaurant_code: str,
        business_date: str
    ) -> Dict:
        """
        Transform batch runner JSON output to V3 Investigation Modal format.

        This method works with serialized JSON from batch_results.json,
        not DTOs. It creates the Investigation Modal compatible structure.

        Args:
            run_data: Single pipeline run dict from batch_results.json
            restaurant_code: Restaurant code
            business_date: Business date (YYYY-MM-DD)

        Returns:
            Dict in V3 Investigation Modal format
        """
        # Level 1: Daily P&L
        sales = run_data.get('sales', 0)
        labor_cost = run_data.get('labor_cost', 0)
        labor_percent = (labor_cost / sales * 100) if sales > 0 else 0

        # Get COGS from cash flow vendor payouts
        cogs = run_data.get('cash_flow', {}).get('total_vendor_payouts', 0)
        cogs_percent = (cogs / sales * 100) if sales > 0 else 0

        profit = sales - labor_cost - cogs
        profit_margin = (profit / sales * 100) if sales > 0 else 0

        day_data = {
            'date': business_date,
            'restaurant': restaurant_code,
            'sales': round(sales, 2),
            'labor': round(labor_cost, 2),
            'laborPercent': round(labor_percent, 1),
            'cogs': round(cogs, 2),
            'cogsPercent': round(cogs_percent, 1),
            'profit': round(profit, 2),
            'profitMargin': round(profit_margin, 1)
        }

        # Level 2: Shift breakdown
        shift_metrics = run_data.get('shift_metrics')
        shift_category_stats = run_data.get('shift_category_stats', {})

        if shift_metrics:
            # shift_metrics is a dict with morning/evening keys
            day_data['shifts'] = shift_metrics

            # Add category statistics to each shift
            if shift_category_stats:
                if 'Morning' in shift_category_stats and 'morning' in day_data['shifts']:
                    day_data['shifts']['morning']['category_stats'] = shift_category_stats['Morning']
                if 'Evening' in shift_category_stats and 'evening' in day_data['shifts']:
                    day_data['shifts']['evening']['category_stats'] = shift_category_stats['Evening']

            logger.debug("shift_data_added",
                       restaurant=restaurant_code,
                       date=business_date,
                       has_morning=bool(shift_metrics.get('morning')),
                       has_evening=bool(shift_metrics.get('evening')),
                       has_category_stats=bool(shift_category_stats))
        else:
            # No shift data available
            day_data['shifts'] = {
                'morning': cls._empty_shift_data(),
                'evening': cls._empty_shift_data()
            }
            logger.warning("no_shift_data_in_run",
                         restaurant=restaurant_code,
                         date=business_date)

        # Level 3: Timeslot analysis
        timeslot_metrics = run_data.get('timeslot_metrics', [])

        # The timeslot_metrics might already be in the right format,
        # but ensure it matches V3 Investigation Modal expectations
        transformed_timeslots = []
        for ts in timeslot_metrics:
            # Check if already in V3 format (has 'timeWindow' key)
            if 'timeWindow' in ts or 'time_window' in ts:
                # Already formatted or nearly formatted
                # Use full by_category data from backend if available
                # Backend provides: {category: {total, failed_standard, failed_historical, ...}}
                by_category_data = ts.get('by_category', {})

                # If by_category not provided, build from individual counts (fallback)
                if not by_category_data:
                    lobby_count = ts.get('lobby', 0)
                    drive_thru_count = ts.get('drive_thru', 0)
                    togo_count = ts.get('togo', 0)

                    if lobby_count > 0:
                        by_category_data['Lobby'] = {'total': lobby_count}
                    if drive_thru_count > 0:
                        by_category_data['Drive-Thru'] = {'total': drive_thru_count}
                    if togo_count > 0:
                        by_category_data['ToGo'] = {'total': togo_count}

                transformed_ts = {
                    'timeWindow': ts.get('timeWindow') or ts.get('time_window', ''),
                    'shift': ts.get('shift', ''),
                    'isEmpty': ts.get('isEmpty', ts.get('is_empty', False)),
                    'status': ts.get('status', 'pass'),
                    'totalOrders': ts.get('totalOrders', ts.get('orders', 0)),  # FIXED: use 'orders' field
                    'passRate': ts.get('passRate', ts.get('pass_rate_standards', 100.0)),
                    'passRateHistorical': ts.get('passRateHistorical', ts.get('pass_rate_historical', 100.0)),
                    'passedStandards': ts.get('passedStandards', ts.get('passed_standards', True)),
                    'passedHistorical': ts.get('passedHistorical', ts.get('passed_historical', True)),
                    'activeServers': ts.get('activeServers', ts.get('active_servers', 0)),
                    'activeCooks': ts.get('activeCooks', ts.get('active_cooks', 0)),
                    'totalStaff': ts.get('totalStaff', ts.get('total_staff', 0)),
                    'consecutivePasses': ts.get('consecutivePasses', ts.get('consecutive_passes', 0)),
                    'consecutiveFails': ts.get('consecutiveFails', ts.get('consecutive_fails', 0)),
                    'streakType': ts.get('streakType', ts.get('streak_type')),
                    'failures': ts.get('failures', []),
                    'byCategory': ts.get('byCategory', by_category_data)  # FIXED: build from individual counts
                }
                transformed_timeslots.append(transformed_ts)

        day_data['timeslots'] = transformed_timeslots

        logger.info("json_transform_complete",
                  restaurant=restaurant_code,
                  date=business_date,
                  timeslot_count=len(transformed_timeslots),
                  has_shift_data=shift_metrics is not None)

        return day_data
