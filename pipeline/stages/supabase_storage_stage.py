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

from pipeline.services.result import Result
from pipeline.services.errors import StorageError
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.orchestration.pipeline.stage import PipelineStage
from pipeline.storage.supabase_client import SupabaseClient
from pipeline.models.shift_metrics_dto import ShiftMetricsDTO
from pipeline.models.timeslot_dto import TimeslotDTO
from pipeline.models.labor_dto import LaborDTO
from pipeline.models.void_metrics_dto import VoidMetricsDTO
from pipeline.infrastructure.logging import get_logger

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
        shift_category_stats = context.get('shift_category_stats')  # Category-level stats
        void_metrics = context.get('void_metrics')  # Void transaction details

        # Extract additional context data for dashboard
        labor_status = context.get('labor_status')  # Labor status (WARNING, GOOD, etc.)
        labor_grade = context.get('labor_grade')  # Labor grade (C, B+, A, etc.)
        service_mix = context.get('service_mix')  # Order categorization breakdown
        categorized_orders_list = context.get('categorized_orders')  # List of categorized orders
        categorized_orders_count = len(categorized_orders_list) if categorized_orders_list else 0
        time_entries = context.get('time_entries', [])  # Time entries for shift hour calculation
        cash_flow = context.get('cash_flow')  # DailyCashFlow DTO from CashFlowExtractor (same as static file)

        # Calculate shift labor hours from time entries
        morning_hours, evening_hours = self._calculate_shift_hours(time_entries)

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
                restaurant, date, sales, labor_dto, labor_metrics,
                labor_status, labor_grade, service_mix, categorized_orders_count,
                cash_flow
            )
            if daily_op_result.is_err():
                return Result.fail(daily_op_result.unwrap_err())

            tables_written.append('daily_operations')
            row_counts['daily_operations'] = 1

            # Write shift operations if available
            if shift_metrics:
                shift_op_result = self._write_shift_operations(
                    restaurant, date, shift_metrics, shift_category_stats,
                    morning_hours, evening_hours, cash_flow
                )
                if shift_op_result.is_err():
                    return Result.fail(shift_op_result.unwrap_err())

                tables_written.append('shift_operations')
                row_counts['shift_operations'] = 2  # Morning + Evening

            # Write void transactions if available
            if void_metrics:
                void_result = self._write_void_transactions(
                    restaurant, date, void_metrics
                )
                if void_result.is_err():
                    return Result.fail(void_result.unwrap_err())

                tables_written.append('void_transactions')
                row_counts['void_transactions'] = void_metrics.total_void_count

            # Write vendor payouts if available
            if cash_flow:
                vendor_payouts = cash_flow.get_all_vendor_payouts()
                if vendor_payouts:
                    vendor_result = self._write_vendor_payouts(
                        restaurant, date, vendor_payouts
                    )
                    if vendor_result.is_err():
                        return Result.fail(vendor_result.unwrap_err())

                    tables_written.append('vendor_payouts')
                    row_counts['vendor_payouts'] = len(vendor_payouts)

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
        labor_metrics,
        labor_status: Optional[str] = None,
        labor_grade: Optional[str] = None,
        service_mix: Optional[Dict] = None,
        categorized_orders_count: Optional[int] = None,
        cash_flow = None
    ) -> Result[None]:
        """
        Write daily operation record to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            sales: Daily sales
            labor_dto: Labor DTO
            labor_metrics: Labor metrics from LaborCalculator
            labor_status: Labor status (WARNING, GOOD, CRITICAL, etc.)
            labor_grade: Labor grade (A, B+, C, etc.)
            service_mix: Order categorization breakdown (lobby, drivethru, togo counts)
            categorized_orders: Total categorized orders
            cash_flow: DailyCashFlow DTO from CashFlowExtractor (same as static file)

        Returns:
            Result[None]: Success or error
        """
        try:
            labor_cost = labor_dto.total_labor_cost
            labor_percent = labor_metrics.labor_percentage

            # Calculate profit (COGS not included for now)
            net_profit = sales - labor_cost
            profit_margin = (net_profit / sales * 100) if sales > 0 else 0

            # Calculate order categorization percentages
            lobby_percent = None
            drivethru_percent = None
            togo_percent = None
            if service_mix and categorized_orders_count and categorized_orders_count > 0:
                lobby_count = service_mix.get('Lobby', 0)
                drivethru_count = service_mix.get('Drive-Thru', 0)
                togo_count = service_mix.get('ToGo', 0)
                lobby_percent = round((lobby_count / categorized_orders_count) * 100, 1)
                drivethru_percent = round((drivethru_count / categorized_orders_count) * 100, 1)
                togo_percent = round((togo_count / categorized_orders_count) * 100, 1)

            data = {
                'business_date': date,
                'restaurant_code': restaurant,
                'total_sales': round(sales, 2),
                'order_count': categorized_orders_count,  # Total orders
                'labor_cost': round(labor_cost, 2),
                'labor_percent': round(labor_percent, 1),
                'labor_hours': round(labor_dto.total_hours_worked, 2),
                'employee_count': labor_dto.employee_count,
                'overtime_hours': round(labor_dto.total_overtime_hours, 2),
                'overtime_cost': round(labor_dto.total_overtime_cost, 2),
                'net_profit': round(net_profit, 2),
                'profit_margin': round(profit_margin, 1),
                'lobby_percent': lobby_percent,
                'drivethru_percent': drivethru_percent,
                'togo_percent': togo_percent,
                'categorized_orders': categorized_orders_count,
                'labor_status': labor_status,  # Dashboard needs this!
                'labor_grade': labor_grade,  # Dashboard needs this!
                'food_cost': round(cash_flow.total_vendor_payouts, 2) if cash_flow else 0.0,  # COGS from vendor payouts
                'food_cost_percent': round((cash_flow.total_vendor_payouts / sales * 100), 1) if cash_flow and sales > 0 else None,
                'cash_collected': round(cash_flow.total_cash, 2) if cash_flow else 0.0,
                'tips_distributed': round(cash_flow.total_tips, 2) if cash_flow else 0.0,
                'vendor_payouts_total': round(cash_flow.total_vendor_payouts, 2) if cash_flow else 0.0,
                'net_cash': round(cash_flow.net_cash, 2) if cash_flow else 0.0,
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
        shift_category_stats: Optional[Dict] = None,
        morning_hours: Optional[float] = None,
        evening_hours: Optional[float] = None,
        cash_flow = None
    ) -> Result[None]:
        """
        Write shift operation records to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            shift_metrics: Shift metrics DTO
            shift_category_stats: Category-level pass/fail stats (optional)
            morning_hours: Calculated morning shift labor hours (optional)
            evening_hours: Calculated evening shift labor hours (optional)
            cash_flow: DailyCashFlow DTO with actual per-shift cash data (same as static file)

        Returns:
            Result[None]: Success or error
        """
        try:
            # Extract actual per-shift cash data from DailyCashFlow (same as static file system)
            if cash_flow:
                # Morning shift cash - actual values, not proportional estimates
                morning_cash = round(cash_flow.morning_shift.cash_collected, 2)
                morning_tips = round(cash_flow.morning_shift.tips_distributed, 2)
                morning_payouts = round(sum(p.amount for p in cash_flow.morning_shift.vendor_payouts), 2)
                morning_net = round(cash_flow.morning_shift.net_cash, 2)

                # Evening shift cash - actual values, not proportional estimates
                evening_cash = round(cash_flow.evening_shift.cash_collected, 2)
                evening_tips = round(cash_flow.evening_shift.tips_distributed, 2)
                evening_payouts = round(sum(p.amount for p in cash_flow.evening_shift.vendor_payouts), 2)
                evening_net = round(cash_flow.evening_shift.net_cash, 2)
            else:
                morning_cash = morning_tips = morning_payouts = morning_net = 0.0
                evening_cash = evening_tips = evening_payouts = evening_net = 0.0

            # Morning shift (only include columns that exist in schema)
            morning_data = {
                'business_date': date,
                'restaurant_code': restaurant,
                'shift_name': 'Morning',
                'sales': round(shift_metrics.morning_sales, 2),
                'labor_cost': round(shift_metrics.morning_labor, 2),
                'labor_hours': round(morning_hours, 2) if morning_hours else None,
                'order_count': shift_metrics.morning_order_count,
                'manager': shift_metrics.morning_manager,
                'voids': shift_metrics.morning_voids,
                'cash_collected': morning_cash,
                'tips_distributed': morning_tips,
                'vendor_payouts': morning_payouts,
                'net_cash': morning_net,
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
                'labor_hours': round(evening_hours, 2) if evening_hours else None,
                'order_count': shift_metrics.evening_order_count,
                'manager': shift_metrics.evening_manager,
                'voids': shift_metrics.evening_voids,
                'cash_collected': evening_cash,
                'tips_distributed': evening_tips,
                'vendor_payouts': evening_payouts,
                'net_cash': evening_net,
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

    def _write_void_transactions(
        self,
        restaurant: str,
        date: str,
        void_metrics: VoidMetricsDTO
    ) -> Result[None]:
        """
        Write void transaction records to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            void_metrics: Void metrics DTO with morning and evening transactions

        Returns:
            Result[None]: Success or error
        """
        try:
            import json

            void_records = []

            # Morning void transactions
            for void_txn in void_metrics.morning_voids:
                void_record = {
                    'business_date': date,
                    'restaurant_code': restaurant,
                    'shift_name': 'Morning',
                    'order_number': void_txn.order_number,
                    'void_date': void_txn.void_date.isoformat() if hasattr(void_txn.void_date, 'isoformat') else str(void_txn.void_date),
                    'server': void_txn.server,
                    'approver': void_txn.approver,
                    'reason': void_txn.reason,
                    'item_count': void_txn.item_count,
                    'total_amount': round(void_txn.total_amount, 2),
                    'items_detail': json.dumps(void_txn.items_detail),  # Store as JSON
                    'created_at': datetime.now().isoformat()
                }
                void_records.append(void_record)

            # Evening void transactions
            for void_txn in void_metrics.evening_voids:
                void_record = {
                    'business_date': date,
                    'restaurant_code': restaurant,
                    'shift_name': 'Evening',
                    'order_number': void_txn.order_number,
                    'void_date': void_txn.void_date.isoformat() if hasattr(void_txn.void_date, 'isoformat') else str(void_txn.void_date),
                    'server': void_txn.server,
                    'approver': void_txn.approver,
                    'reason': void_txn.reason,
                    'item_count': void_txn.item_count,
                    'total_amount': round(void_txn.total_amount, 2),
                    'items_detail': json.dumps(void_txn.items_detail),  # Store as JSON
                    'created_at': datetime.now().isoformat()
                }
                void_records.append(void_record)

            # Insert all void records (if any)
            if void_records:
                self.supabase_client.insert_void_transactions_batch(void_records)

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                StorageError(
                    f"Failed to write void transactions: {str(e)}",
                    context={'restaurant': restaurant, 'date': date, 'error': str(e)}
                )
            )

    def _write_vendor_payouts(
        self,
        restaurant: str,
        date: str,
        vendor_payouts: list
    ) -> Result[None]:
        """
        Write vendor payout records to Supabase.

        Args:
            restaurant: Restaurant code
            date: Business date (YYYY-MM-DD)
            vendor_payouts: List of VendorPayout objects from DailyCashFlow

        Returns:
            Result[None]: Success or error
        """
        try:
            payout_records = []

            for payout in vendor_payouts:
                payout_record = {
                    'business_date': date,
                    'restaurant_code': restaurant,
                    'shift_name': payout.shift,
                    'vendor_name': payout.vendor_name,
                    'amount': round(payout.amount, 2),
                    'reason': payout.reason,
                    'comments': payout.comments,
                    'payout_time': payout.time,
                    'manager': payout.manager,
                    'drawer': payout.drawer,
                    'created_at': datetime.now().isoformat()
                }
                payout_records.append(payout_record)

            # Delete existing payouts for this date/restaurant, then insert new ones
            # This avoids complex unique constraint issues
            self.supabase_client.delete_vendor_payouts(date, restaurant)

            # Insert all payout records (if any)
            if payout_records:
                self.supabase_client.insert_vendor_payouts_batch(payout_records)

            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                StorageError(
                    f"Failed to write vendor payouts: {str(e)}",
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

    @staticmethod
    def _calculate_shift_hours(time_entries: List) -> tuple[Optional[float], Optional[float]]:
        """
        Calculate morning and evening shift labor hours from time entries.

        Uses shift boundaries from shift_splitter.py:
        - Morning: 6 AM - 2 PM (hour < 14)
        - Evening: 2 PM - 10 PM (hour >= 14)

        Args:
            time_entries: List of TimeEntryDTO objects

        Returns:
            Tuple of (morning_hours, evening_hours)
        """
        if not time_entries:
            return (None, None)

        SHIFT_CUTOFF_HOUR = 14  # 2 PM

        morning_hours = 0.0
        evening_hours = 0.0

        for entry in time_entries:
            # Use clock_in_datetime to determine which shift the entry belongs to
            if entry.clock_in_datetime:
                hour = entry.clock_in_datetime.hour

                # Assign all hours to the shift where employee clocked in
                if hour < SHIFT_CUTOFF_HOUR:
                    morning_hours += entry.payable_hours
                else:
                    evening_hours += entry.payable_hours

        return (morning_hours if morning_hours > 0 else None,
                evening_hours if evening_hours > 0 else None)

    def __repr__(self) -> str:
        return "SupabaseStorageStage(client=SupabaseClient)"
