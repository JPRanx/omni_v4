"""
ShiftSplitter - Split daily data into morning and evening shifts.

Follows V3's shift splitting logic:
- Morning: 6 AM - 2 PM (hour < 14)
- Evening: 2 PM - 10 PM (hour >= 14)
"""

from datetime import datetime, time
from typing import List, Optional
import pandas as pd

from src.models.time_entry_dto import TimeEntryDTO
from src.models.shift_metrics_dto import ShiftMetricsDTO
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class ShiftSplitter:
    """
    Splits daily business data into morning and evening shifts.

    Uses order timestamps and time entries to calculate shift-level metrics.
    """

    # Shift boundaries (matching V3)
    MORNING_START_HOUR = 6
    SHIFT_CUTOFF_HOUR = 14  # 2 PM
    EVENING_END_HOUR = 22

    @classmethod
    def split_day(
        cls,
        restaurant_code: str,
        business_date: str,
        daily_sales: float,
        daily_labor: float,
        time_entries: List[TimeEntryDTO],
        raw_dataframes: Optional[dict] = None
    ) -> ShiftMetricsDTO:
        """
        Split daily data into morning and evening shifts.

        Args:
            restaurant_code: Restaurant identifier
            business_date: Business date (YYYY-MM-DD)
            daily_sales: Total daily sales
            daily_labor: Total daily labor cost
            time_entries: List of time entry DTOs
            raw_dataframes: Optional dict of raw DataFrames for detailed splitting

        Returns:
            ShiftMetricsDTO with morning and evening breakdown
        """
        bound_logger = logger.bind(restaurant=restaurant_code, date=business_date)

        # If we have OrderDetails or Kitchen Details, use actual timestamps
        if raw_dataframes and ('orders' in raw_dataframes or 'kitchen' in raw_dataframes):
            return cls._split_by_order_timestamps(
                restaurant_code,
                business_date,
                daily_sales,
                daily_labor,
                time_entries,
                raw_dataframes
            )

        # Otherwise, use ratio estimation (35% morning, 65% evening)
        bound_logger.warning("shift_split_using_ratio",
                           reason="No order timestamps available")

        return cls._split_by_ratio(
            restaurant_code,
            business_date,
            daily_sales,
            daily_labor,
            time_entries
        )

    @classmethod
    def _split_by_order_timestamps(
        cls,
        restaurant_code: str,
        business_date: str,
        daily_sales: float,
        daily_labor: float,
        time_entries: List[TimeEntryDTO],
        raw_dataframes: dict
    ) -> ShiftMetricsDTO:
        """Split using actual order timestamps from Kitchen Details or Order Details."""

        # Try Kitchen Details first (has fire times)
        if 'kitchen' in raw_dataframes:
            df = raw_dataframes['kitchen'].copy()
            time_column = 'Fire Time'
        elif 'orders' in raw_dataframes:
            df = raw_dataframes['orders'].copy()
            time_column = 'Order Time'  # Or whatever the column is called
        else:
            # Fall back to ratio
            return cls._split_by_ratio(restaurant_code, business_date, daily_sales, daily_labor, time_entries)

        # Parse timestamps and extract hour
        try:
            # Try different datetime formats
            if time_column in df.columns:
                # Parse times (handle different formats)
                df['parsed_time'] = pd.to_datetime(df[time_column], errors='coerce')
                df['hour'] = df['parsed_time'].dt.hour

                # Filter valid hours
                df = df[df['hour'].notna()]

                # Split by cutoff hour
                morning_orders = df[df['hour'] < cls.SHIFT_CUTOFF_HOUR]
                evening_orders = df[df['hour'] >= cls.SHIFT_CUTOFF_HOUR]

                # Calculate sales split
                morning_count = len(morning_orders)
                evening_count = len(evening_orders)
                total_count = morning_count + evening_count

                if total_count > 0:
                    morning_ratio = morning_count / total_count
                    evening_ratio = evening_count / total_count
                else:
                    morning_ratio = 0.35
                    evening_ratio = 0.65

                morning_sales = daily_sales * morning_ratio
                evening_sales = daily_sales * evening_ratio

                # Split labor proportionally
                morning_labor = daily_labor * morning_ratio
                evening_labor = daily_labor * evening_ratio

            else:
                # Column not found, use ratio
                return cls._split_by_ratio(restaurant_code, business_date, daily_sales, daily_labor, time_entries)

        except Exception as e:
            logger.warning("order_timestamp_parse_failed", error=str(e))
            return cls._split_by_ratio(restaurant_code, business_date, daily_sales, daily_labor, time_entries)

        # Identify managers
        morning_manager = cls._identify_manager(time_entries, cls.MORNING_START_HOUR, cls.SHIFT_CUTOFF_HOUR)
        evening_manager = cls._identify_manager(time_entries, cls.SHIFT_CUTOFF_HOUR, cls.EVENING_END_HOUR)

        # Count voids (if available in dataframes)
        morning_voids = 0
        evening_voids = 0

        if 'eod' in raw_dataframes:
            # Check EOD for void tracking
            # This is simplified - V3 has more complex void detection
            pass

        return ShiftMetricsDTO(
            restaurant_code=restaurant_code,
            business_date=business_date,
            morning_sales=morning_sales,
            morning_labor=morning_labor,
            morning_manager=morning_manager,
            morning_voids=morning_voids,
            morning_order_count=morning_count,
            evening_sales=evening_sales,
            evening_labor=evening_labor,
            evening_manager=evening_manager,
            evening_voids=evening_voids,
            evening_order_count=evening_count
        )

    @classmethod
    def _split_by_ratio(
        cls,
        restaurant_code: str,
        business_date: str,
        daily_sales: float,
        daily_labor: float,
        time_entries: List[TimeEntryDTO]
    ) -> ShiftMetricsDTO:
        """
        Split using historical 35/65 ratio.

        Fallback when order timestamps are not available.
        """
        # V3's fallback ratio
        MORNING_RATIO = 0.35
        EVENING_RATIO = 0.65

        morning_sales = daily_sales * MORNING_RATIO
        evening_sales = daily_sales * EVENING_RATIO

        morning_labor = daily_labor * MORNING_RATIO
        evening_labor = daily_labor * EVENING_RATIO

        # Identify managers
        morning_manager = cls._identify_manager(time_entries, cls.MORNING_START_HOUR, cls.SHIFT_CUTOFF_HOUR)
        evening_manager = cls._identify_manager(time_entries, cls.SHIFT_CUTOFF_HOUR, cls.EVENING_END_HOUR)

        # Estimate order counts (rough approximation)
        # Assume 50 orders per $1000 in sales
        morning_orders = int(morning_sales / 1000 * 50)
        evening_orders = int(evening_sales / 1000 * 50)

        return ShiftMetricsDTO(
            restaurant_code=restaurant_code,
            business_date=business_date,
            morning_sales=morning_sales,
            morning_labor=morning_labor,
            morning_manager=morning_manager,
            morning_voids=0,
            morning_order_count=morning_orders,
            evening_sales=evening_sales,
            evening_labor=evening_labor,
            evening_manager=evening_manager,
            evening_voids=0,
            evening_order_count=evening_orders
        )

    @classmethod
    def _identify_manager(
        cls,
        time_entries: List[TimeEntryDTO],
        shift_start_hour: int,
        shift_end_hour: int
    ) -> str:
        """
        Identify manager working during specified shift window.

        Args:
            time_entries: List of time entry DTOs
            shift_start_hour: Shift start hour (0-23)
            shift_end_hour: Shift end hour (0-23)

        Returns:
            Manager name or "Not Assigned" if no manager found
        """
        # Filter for managers working during this shift
        managers = [
            entry for entry in time_entries
            if entry.is_manager and entry.is_working_during(shift_start_hour, shift_end_hour)
        ]

        if not managers:
            return "Not Assigned"

        # Return first manager found (prioritize earlier clock-in)
        managers.sort(key=lambda e: e.clock_in_datetime)
        return managers[0].employee_name
