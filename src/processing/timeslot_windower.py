"""
TimeslotWindower - Creates 15-minute windows from orders.

Splits a day into 96 fifteen-minute timeslots and groups orders accordingly.
Matches V3's windowing logic with enhancements for V4.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from src.models.order_dto import OrderDTO
from src.models.timeslot_dto import TimeslotDTO
from src.core.result import Result
from src.core.errors import ProcessingError
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class TimeslotWindower:
    """
    Creates 15-minute timeslot windows from a day's orders.

    Design Philosophy:
    - 96 slots per day (24 hours × 4 slots/hour)
    - Orders assigned to slot based on order_time
    - Empty slots preserved (important for capacity analysis)
    - Two shifts: morning (6 AM - 2 PM) and evening (2 PM - 10 PM)
    """

    def __init__(self):
        """Initialize the timeslot windower."""
        # Shift boundaries (matching V3)
        self.morning_start = 6  # 6 AM
        self.morning_end = 14  # 2 PM
        self.evening_start = 14  # 2 PM
        self.evening_end = 22  # 10 PM

    def create_timeslots(
        self,
        orders: List[OrderDTO],
        business_date: str,
        time_entries: Optional[List] = None
    ) -> Result[Dict[str, List[TimeslotDTO]]]:
        """
        Create 15-minute timeslots from orders.

        Args:
            orders: List of OrderDTO objects for a single day
            business_date: Business date in YYYY-MM-DD format
            time_entries: Optional list of TimeEntryDTO for server counting

        Returns:
            Result[Dict[str, List[TimeslotDTO]]]: Dictionary with 'morning' and 'evening' keys
                containing lists of TimeslotDTO objects
        """
        try:
            # Parse business date
            base_date = datetime.strptime(business_date, '%Y-%m-%d')

            # Create all 96 timeslots for the day
            all_slots = self._generate_all_slots(base_date)

            # Group orders by timeslot
            orders_by_slot = self._group_orders_by_slot(orders, all_slots)

            # Create TimeslotDTO objects
            timeslots = {}

            # Morning shift
            morning_slots = []
            for slot_start, slot_end in all_slots['morning']:
                slot_key = (slot_start, slot_end)
                slot_orders = orders_by_slot.get(slot_key, [])
                timeslot = TimeslotDTO.create(slot_start, slot_end, 'morning', slot_orders, time_entries)
                morning_slots.append(timeslot)

            # Evening shift
            evening_slots = []
            for slot_start, slot_end in all_slots['evening']:
                slot_key = (slot_start, slot_end)
                slot_orders = orders_by_slot.get(slot_key, [])
                timeslot = TimeslotDTO.create(slot_start, slot_end, 'evening', slot_orders, time_entries)
                evening_slots.append(timeslot)

            timeslots = {
                'morning': morning_slots,
                'evening': evening_slots
            }

            logger.info("timeslots_created",
                       total_orders=len(orders),
                       morning_slots=len(morning_slots),
                       evening_slots=len(evening_slots),
                       morning_orders=sum(s.total_orders for s in morning_slots),
                       evening_orders=sum(s.total_orders for s in evening_slots))

            return Result.ok(timeslots)

        except Exception as e:
            return Result.fail(
                ProcessingError(
                    f"Failed to create timeslots: {str(e)}",
                    context={'business_date': business_date, 'order_count': len(orders)}
                )
            )

    def _generate_all_slots(self, base_date: datetime) -> Dict[str, List[tuple]]:
        """
        Generate all 15-minute slots for both shifts.

        Returns:
            Dict with 'morning' and 'evening' keys, each containing list of (start, end) tuples
        """
        morning_slots = []
        evening_slots = []

        # Morning shift: 6 AM to 2 PM
        for hour in range(self.morning_start, self.morning_end):
            for minute in [0, 15, 30, 45]:
                slot_start = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=15)
                morning_slots.append((slot_start, slot_end))

        # Evening shift: 2 PM to 10 PM
        for hour in range(self.evening_start, self.evening_end):
            for minute in [0, 15, 30, 45]:
                slot_start = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=15)
                evening_slots.append((slot_start, slot_end))

        return {
            'morning': morning_slots,
            'evening': evening_slots
        }

    def _group_orders_by_slot(
        self,
        orders: List[OrderDTO],
        all_slots: Dict[str, List[tuple]]
    ) -> Dict[tuple, List[OrderDTO]]:
        """
        Group orders into their respective 15-minute slots using overlap calculation.

        MATCHES V3 BEHAVIOR: Orders are assigned to ALL slots they overlap with during
        preparation time, not just the slot when they were placed.

        This gives accurate concurrent kitchen load for capacity analysis.

        Args:
            orders: All orders for the day
            all_slots: All timeslot boundaries

        Returns:
            Dict mapping (slot_start, slot_end) -> [orders]
        """
        orders_by_slot = defaultdict(list)

        # Flatten all slots into single list
        all_slot_boundaries = all_slots['morning'] + all_slots['evening']

        for order in orders:
            order_time = order.order_time

            # Calculate when order preparation ends
            # Use fulfillment_minutes to determine how long order was in kitchen
            order_end = order_time + timedelta(minutes=order.fulfillment_minutes)

            # Check which slots this order overlaps with
            for slot_start, slot_end in all_slot_boundaries:
                # Order overlaps with slot if:
                # - Order starts before slot ends: order_time <= slot_end
                # - Order ends after slot starts: order_end >= slot_start
                #
                # This matches V3's logic:
                # if order_start_comparable <= slot_end_time and order_end_comparable >= slot_time
                if order_time <= slot_end and order_end >= slot_start:
                    slot_key = (slot_start, slot_end)
                    orders_by_slot[slot_key].append(order)
                    # NOTE: Don't break! Order can be in multiple slots if preparation spans multiple windows

        return orders_by_slot

    def get_timeslots_for_shift(
        self,
        all_timeslots: Dict[str, List[TimeslotDTO]],
        shift: str
    ) -> List[TimeslotDTO]:
        """
        Get timeslots for a specific shift.

        Args:
            all_timeslots: Dictionary returned from create_timeslots()
            shift: 'morning' or 'evening'

        Returns:
            List of TimeslotDTO objects for the shift
        """
        return all_timeslots.get(shift, [])

    def get_peak_timeslots(
        self,
        all_timeslots: Dict[str, List[TimeslotDTO]]
    ) -> List[TimeslotDTO]:
        """
        Get only peak-time timeslots.

        Peak times:
        - Lunch: 11:30 AM - 1:00 PM
        - Dinner: 5:30 PM - 7:30 PM

        Returns:
            List of peak-time TimeslotDTO objects
        """
        peak_slots = []

        for shift in ['morning', 'evening']:
            for slot in all_timeslots.get(shift, []):
                if slot.is_peak_time:
                    peak_slots.append(slot)

        return peak_slots

    def get_non_empty_timeslots(
        self,
        all_timeslots: Dict[str, List[TimeslotDTO]]
    ) -> List[TimeslotDTO]:
        """
        Get only timeslots with orders.

        Returns:
            List of non-empty TimeslotDTO objects
        """
        non_empty = []

        for shift in ['morning', 'evening']:
            for slot in all_timeslots.get(shift, []):
                if not slot.is_empty:
                    non_empty.append(slot)

        return non_empty

    def calculate_capacity_metrics(
        self,
        all_timeslots: Dict[str, List[TimeslotDTO]]
    ) -> Dict:
        """
        Calculate capacity utilization metrics.

        Returns:
            Dict with capacity analysis metrics
        """
        morning_slots = all_timeslots.get('morning', [])
        evening_slots = all_timeslots.get('evening', [])

        # Count slots with orders
        morning_active = sum(1 for s in morning_slots if not s.is_empty)
        evening_active = sum(1 for s in evening_slots if not s.is_empty)

        # Total orders
        morning_orders = sum(s.total_orders for s in morning_slots)
        evening_orders = sum(s.total_orders for s in evening_slots)

        # Peak slots
        morning_peak = [s for s in morning_slots if s.is_peak_time]
        evening_peak = [s for s in evening_slots if s.is_peak_time]
        morning_peak_orders = sum(s.total_orders for s in morning_peak)
        evening_peak_orders = sum(s.total_orders for s in evening_peak)

        # Capacity utilization (% of slots with orders)
        morning_utilization = (morning_active / len(morning_slots) * 100) if morning_slots else 0
        evening_utilization = (evening_active / len(evening_slots) * 100) if evening_slots else 0

        return {
            'morning': {
                'total_slots': len(morning_slots),
                'active_slots': morning_active,
                'utilization_pct': round(morning_utilization, 1),
                'total_orders': morning_orders,
                'peak_orders': morning_peak_orders,
                'peak_slots': len(morning_peak),
            },
            'evening': {
                'total_slots': len(evening_slots),
                'active_slots': evening_active,
                'utilization_pct': round(evening_utilization, 1),
                'total_orders': evening_orders,
                'peak_orders': evening_peak_orders,
                'peak_slots': len(evening_peak),
            }
        }
