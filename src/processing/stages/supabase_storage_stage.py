"""
SupabaseStorageStage - Pipeline stage for persisting V4 data to Supabase.

Writes Investigation Modal-ready data including:
- Daily P&L metrics (daily_operations table)
- Shift breakdown with managers (shift_operations table)
- Timeslot analysis with failures (timeslot_results table)
- Pattern learning updates (timeslot_patterns table)
"""

import time
from typing import Optional, Dict, List
from datetime import datetime

from src.core.result import Result
from src.core.errors import StorageError
from src.orchestration.pipeline.context import PipelineContext
from src.orchestration.pipeline.stage import PipelineStage
from src.storage.supabase_client import SupabaseClient
from src.models.shift_metrics_dto import ShiftMetricsDTO
from src.models.timeslot_dto import TimeslotDTO
from src.models.labor_dto import LaborDTO
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SupabaseStorageStage(PipelineStage):
    """
    Pipeline stage for storing Investigation Modal data to Supabase.

    Transforms pipeline DTOs into Supabase schema format and writes to tables:
    - daily_operations: Daily P&L metrics
    - shift_operations: Morning/evening breakdown with managers
    - timeslot_results: 15-minute timeslot analysis
    - timeslot_patterns: Pattern learning updates (handled by pattern learning stage)
    """

    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """
        Initialize Supabase storage stage.

        Args:
            supabase_client: SupabaseClient instance (creates default if None)
        """
        super().__init__()
        self._supabase_client = supabase_client

    @property
    def supabase_client(self) -> SupabaseClient:
        """Lazy-initialize Supabase client."""
        if self._supabase_client is None:
            self._supabase_client = SupabaseClient()
        return self._supabase_client

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute Supabase storage stage.

        Expected context inputs:
        - sales: float (required)
        - labor_dto: LaborDTO (required)
        - labor_metrics: LaborMetrics (required)
        - shift_metrics: ShiftMetricsDTO (optional)
        - timeslots: Dict[str, List[TimeslotDTO]] (optional)
        - restaurant: str (required)
        - date: str (required)

        Context outputs:
        - storage_result: Dict with storage metrics

        Args:
            context: Pipeline context with data to store

        Returns:
            Result[PipelineContext]: Updated context or error
        """
        start_time = time.time()

        # Get context data
        restaurant = context.get('restaurant')
        date = context.get('date')
        sales = context.get('sales')
        labor_dto = context.get('labor_dto')
        labor_metrics = context.get('labor_metrics')
        shift_metrics = context.get('shift_metrics')
        timeslots = context.get('timeslots')
        shift_category_stats = context.get('shift_category_stats')  # NEW: Category-level stats

        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("supabase_storage_started")

        # Validate required data
        if not restaurant or not date:
            return Result.fail(
                StorageError(
                    "Missing required context: 'restaurant' and 'date' must be present",
                    context={'has_restaurant': bool(restaurant), 'has_date': bool(date)}
                )
            )

        if not sales or not labor_dto or not labor_metrics:
            return Result.fail(
                StorageError(
                    "Missing required context: 'sales', 'labor_dto', and 'labor_metrics' must be present",
                    context={'restaurant': restaurant, 'date': date,
                           'has_sales': bool(sales), 'has_labor_dto': bool(labor_dto),
                           'has_labor_metrics': bool(labor_metrics)}
                )
            )

        try:
            tables_written = []
            row_counts = {}

            # Write daily operations
            daily_op_result = self._write_daily_operation(
                restaurant, date, sales, labor_dto, labor_metrics
            )
            if daily_op_result.is_err():
                return Result.fail(daily_op_result.unwrap_err())

            tables_written.append('daily_operations')
            row_counts['daily_operations'] = 1

            # Write shift operations if available
            if shift_metrics:
                shift_op_result = self._write_shift_operations(
                    restaurant, date, shift_metrics, shift_category_stats
                )
                if shift_op_result.is_err():
                    return Result.fail(shift_op_result.unwrap_err())

                tables_written.append('shift_operations')
                row_counts['shift_operations'] = 2  # Morning + Evening

            # Write timeslot results if available
            if timeslots:
                timeslot_result = self._write_timeslot_results(
                    restaurant, date, timeslots
                )
                if timeslot_result.is_err():
                    return Result.fail(timeslot_result.unwrap_err())

                tables_written.append('timeslot_results')
                # Count total timeslots
                total_slots = len(timeslots.get('morning', [])) + len(timeslots.get('evening', []))
                row_counts['timeslot_results'] = total_slots

            # Store result in context
            storage_result = {
                'restaurant': restaurant,
                'date': date,
                'tables_written': tables_written,
                'row_counts': row_counts,
                'success': True
            }
            context.set('storage_result', storage_result)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            total_rows = sum(row_counts.values())

            bound_logger.info("supabase_storage_complete",
                            tables_written=len(tables_written),
                            total_rows=total_rows,
                            duration_ms=round(duration_ms, 0))

            return Result.ok(context)

        except Exception as e:
            bound_logger.error("supabase_storage_failed", error=str(e))
            return Result.fail(
                StorageError(
                    f"Supabase storage failed: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def _write_daily_operation(
        self,
        restaurant: str,
        date: str,
        sales: float,
        labor_dto: LaborDTO,
        labor_metrics
    ) -> Result[None]:
        """
        Write daily operation record to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            sales: Daily sales
            labor_dto: Labor DTO
            labor_metrics: Labor metrics from LaborCalculator

        Returns:
            Result[None]: Success or error
        """
        try:
            labor_cost = labor_dto.total_labor_cost
            labor_percent = labor_metrics.labor_percentage

            # Calculate profit (COGS not included for now)
            net_profit = sales - labor_cost
            profit_margin = (net_profit / sales * 100) if sales > 0 else 0

            data = {
                'business_date': date,
                'restaurant_code': restaurant,
                'total_sales': round(sales, 2),
                'labor_cost': round(labor_cost, 2),
                'labor_percent': round(labor_percent, 1),
                'labor_hours': round(labor_dto.total_hours_worked, 2),
                'employee_count': labor_dto.employee_count,
                'net_profit': round(net_profit, 2),
                'profit_margin': round(profit_margin, 1),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            self.supabase_client.insert_daily_operation(data)
            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                StorageError(
                    f"Failed to write daily operation: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def _write_shift_operations(
        self,
        restaurant: str,
        date: str,
        shift_metrics: ShiftMetricsDTO,
        shift_category_stats: Optional[Dict] = None
    ) -> Result[None]:
        """
        Write shift operation records to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            shift_metrics: Shift metrics DTO
            shift_category_stats: Category-level pass/fail stats (optional)

        Returns:
            Result[None]: Success or error
        """
        try:
            # Morning shift (only include columns that exist in schema)
            morning_data = {
                'business_date': date,
                'restaurant_code': restaurant,
                'shift_name': 'Morning',
                'sales': round(shift_metrics.morning_sales, 2),
                'labor_cost': round(shift_metrics.morning_labor, 2),
                'order_count': shift_metrics.morning_order_count,
                'created_at': datetime.now().isoformat()
            }

            # Add category stats if available
            if shift_category_stats and 'Morning' in shift_category_stats:
                morning_data['category_stats'] = shift_category_stats['Morning']

            # Evening shift (only include columns that exist in schema)
            evening_data = {
                'business_date': date,
                'restaurant_code': restaurant,
                'shift_name': 'Evening',
                'sales': round(shift_metrics.evening_sales, 2),
                'labor_cost': round(shift_metrics.evening_labor, 2),
                'order_count': shift_metrics.evening_order_count,
                'created_at': datetime.now().isoformat()
            }

            # Add category stats if available
            if shift_category_stats and 'Evening' in shift_category_stats:
                evening_data['category_stats'] = shift_category_stats['Evening']

            # Insert both shifts
            self.supabase_client.insert_shift_operations_batch([morning_data, evening_data])
            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                StorageError(
                    f"Failed to write shift operations: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def _write_timeslot_results(
        self,
        restaurant: str,
        date: str,
        timeslots: Dict[str, List[TimeslotDTO]]
    ) -> Result[None]:
        """
        Write timeslot result records to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            timeslots: Dict with 'morning' and 'evening' timeslot lists

        Returns:
            Result[None]: Success or error
        """
        try:
            # Flatten timeslots into single list with index
            all_timeslots = []
            timeslot_index = 0

            for shift in ['morning', 'evening']:
                for timeslot in timeslots.get(shift, []):
                    # Match schema columns only
                    timeslot_data = {
                        'business_date': date,
                        'restaurant_code': restaurant,
                        'timeslot_index': timeslot_index,
                        'timeslot_label': timeslot.time_window,
                        'shift_name': shift.capitalize(),
                        'orders': timeslot.total_orders,
                        'sales': round(getattr(timeslot, 'sales', 0), 2),
                        'labor_cost': round(getattr(timeslot, 'labor_cost', 0), 2),
                        'efficiency_score': round(timeslot.pass_rate_standards, 2) if hasattr(timeslot, 'pass_rate_standards') else None,
                        'grade': getattr(timeslot, 'grade', None),
                        'pass_fail': timeslot.passed_standards if hasattr(timeslot, 'passed_standards') else None,
                        'created_at': datetime.now().isoformat()
                    }
                    all_timeslots.append(timeslot_data)
                    timeslot_index += 1

            # Insert all timeslots in batch
            if all_timeslots:
                self.supabase_client.insert_timeslot_results_batch(all_timeslots)

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                StorageError(
                    f"Failed to write timeslot results: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def validate(self, context: PipelineContext) -> Result[bool]:
        """
        Validate that context has required data for storage.

        Args:
            context: Pipeline context

        Returns:
            Result[bool]: True if valid, error otherwise
        """
        if not context.has('restaurant'):
            return Result.fail(
                StorageError(
                    "Missing 'restaurant' in context",
                    context={'stage': 'supabase_storage'}
                )
            )

        if not context.has('date'):
            return Result.fail(
                StorageError(
                    "Missing 'date' in context",
                    context={'stage': 'supabase_storage'}
                )
            )

        if not context.has('sales'):
            return Result.fail(
                StorageError(
                    "Missing 'sales' in context",
                    context={'stage': 'supabase_storage'}
                )
            )

        if not context.has('labor_dto'):
            return Result.fail(
                StorageError(
                    "Missing 'labor_dto' in context",
                    context={'stage': 'supabase_storage'}
                )
            )

        if not context.has('labor_metrics'):
            return Result.fail(
                StorageError(
                    "Missing 'labor_metrics' in context",
                    context={'stage': 'supabase_storage'}
                )
            )

        return Result.ok(True)

    def rollback(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Rollback Supabase storage.

        Note: Supabase REST API has limited rollback support.
        This is a best-effort cleanup.

        Args:
            context: Pipeline context

        Returns:
            Result[PipelineContext]: Context unchanged (rollback not fully supported)
        """
        logger.warning("supabase_rollback_requested",
                     restaurant=context.get('restaurant'),
                     date=context.get('date'),
                     note="Supabase REST API has limited rollback support")

        return Result.ok(context)

    def __repr__(self) -> str:
        return "SupabaseStorageStage(client=SupabaseClient)"
