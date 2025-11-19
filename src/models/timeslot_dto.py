"""
TimeslotDTO - 15-minute window performance tracking.

Represents a single 15-minute timeslot with all orders, metrics, and grading results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from .order_dto import OrderDTO


@dataclass(frozen=True)
class TimeslotDTO:
    """
    Immutable 15-minute timeslot with orders and performance metrics.

    Matches V3's timeslot structure with enhancements for V4.
    """

    # Time boundaries
    slot_start: datetime
    slot_end: datetime
    time_window: str  # e.g., "11:00-11:15"
    shift: str  # "morning" or "evening"

    # Orders in this slot
    orders: List[OrderDTO] = field(default_factory=list)

    # Order counts by category
    lobby_count: int = 0
    drive_thru_count: int = 0
    togo_count: int = 0
    total_orders: int = 0

    # Staffing levels (from TimeEntries)
    active_servers: int = 0  # Number of servers clocked in during this window
    active_cooks: int = 0    # Number of cooks clocked in during this window
    total_staff: int = 0     # Total staff clocked in during this window

    # Performance metrics
    avg_fulfillment: float = 0.0  # Average fulfillment time across all orders
    median_fulfillment: float = 0.0  # Median fulfillment time (robust to outliers)

    # Category-specific fulfillment averages
    lobby_avg_fulfillment: Optional[float] = None
    drive_thru_avg_fulfillment: Optional[float] = None
    togo_avg_fulfillment: Optional[float] = None

    # Grading results (populated by TimeslotGrader)
    passed_standards: Optional[bool] = None  # All orders met fixed standards
    passed_historical: Optional[bool] = None  # All orders met learned patterns
    pass_rate_standards: Optional[float] = None  # Percentage passing standards
    pass_rate_historical: Optional[float] = None  # Percentage passing historical
    status: Optional[str] = None  # 'pass' (>=85%), 'warning' (>=70%), 'fail' (<70%)

    # Failure details
    failures: List[Dict] = field(default_factory=list)  # Failed orders with details

    # Category breakdown
    by_category: Dict[str, Dict] = field(default_factory=dict)  # Detailed metrics per category

    # Streak tracking
    streak_type: Optional[str] = None  # "hot" (≥85% pass), "cold" (<70% pass), or None
    consecutive_passes: int = 0  # How many consecutive passing slots
    consecutive_fails: int = 0  # How many consecutive failing slots

    # Metadata
    is_peak_time: bool = False  # True if lunch/dinner rush
    is_empty: bool = False  # True if no orders in this slot

    @classmethod
    def create(
        cls,
        slot_start: datetime,
        slot_end: datetime,
        shift: str,
        orders: List[OrderDTO],
        time_entries: Optional[List] = None
    ) -> "TimeslotDTO":
        """
        Create TimeslotDTO from time boundaries and orders.

        Args:
            slot_start: Start of 15-minute window
            slot_end: End of 15-minute window
            shift: "morning" or "evening"
            orders: All orders in this timeslot
            time_entries: Optional list of TimeEntryDTO for server counting

        Returns:
            TimeslotDTO with calculated metrics
        """
        # Format time window string
        time_window = f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"

        # Count orders by category
        lobby_count = sum(1 for o in orders if o.category == 'Lobby')
        drive_thru_count = sum(1 for o in orders if o.category == 'Drive-Thru')
        togo_count = sum(1 for o in orders if o.category == 'ToGo')
        total_orders = len(orders)

        # Calculate fulfillment times
        if orders:
            fulfillment_times = [o.fulfillment_minutes for o in orders]
            avg_fulfillment = sum(fulfillment_times) / len(fulfillment_times)

            # Median (robust to outliers)
            sorted_times = sorted(fulfillment_times)
            n = len(sorted_times)
            if n % 2 == 0:
                median_fulfillment = (sorted_times[n//2 - 1] + sorted_times[n//2]) / 2
            else:
                median_fulfillment = sorted_times[n//2]

            # Category-specific averages
            lobby_orders = [o for o in orders if o.category == 'Lobby']
            drive_thru_orders = [o for o in orders if o.category == 'Drive-Thru']
            togo_orders = [o for o in orders if o.category == 'ToGo']

            lobby_avg = sum(o.fulfillment_minutes for o in lobby_orders) / len(lobby_orders) if lobby_orders else None
            drive_avg = sum(o.fulfillment_minutes for o in drive_thru_orders) / len(drive_thru_orders) if drive_thru_orders else None
            togo_avg = sum(o.fulfillment_minutes for o in togo_orders) / len(togo_orders) if togo_orders else None
        else:
            avg_fulfillment = 0.0
            median_fulfillment = 0.0
            lobby_avg = None
            drive_avg = None
            togo_avg = None

        # Determine if peak time (lunch 11:30-13:00, dinner 17:30-19:30)
        hour = slot_start.hour
        minute = slot_start.minute
        is_peak = (
            (shift == 'morning' and hour == 11 and minute >= 30) or
            (shift == 'morning' and hour == 12) or
            (shift == 'evening' and hour == 17 and minute >= 30) or
            (shift == 'evening' and hour == 18) or
            (shift == 'evening' and hour == 19 and minute < 30)
        )

        # Count active staff if time entries provided
        active_servers = 0
        active_cooks = 0
        total_staff = 0

        if time_entries:
            from src.processing.server_counter import ServerCounter
            staffing = ServerCounter.get_staffing_summary(time_entries, slot_start, slot_end)
            active_servers = staffing['servers']
            active_cooks = staffing['cooks']
            total_staff = staffing['total_staff']

        return cls(
            slot_start=slot_start,
            slot_end=slot_end,
            time_window=time_window,
            shift=shift,
            orders=orders,
            lobby_count=lobby_count,
            drive_thru_count=drive_thru_count,
            togo_count=togo_count,
            total_orders=total_orders,
            active_servers=active_servers,
            active_cooks=active_cooks,
            total_staff=total_staff,
            avg_fulfillment=round(avg_fulfillment, 2),
            median_fulfillment=round(median_fulfillment, 2),
            lobby_avg_fulfillment=round(lobby_avg, 2) if lobby_avg else None,
            drive_thru_avg_fulfillment=round(drive_avg, 2) if drive_avg else None,
            togo_avg_fulfillment=round(togo_avg, 2) if togo_avg else None,
            is_peak_time=is_peak,
            is_empty=(total_orders == 0)
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        # Convert failures list with datetime objects to JSON-serializable format
        serializable_failures = []
        for failure in self.failures:
            serializable_failure = failure.copy()
            # Convert datetime to ISO string format
            if 'order_time' in serializable_failure and isinstance(serializable_failure['order_time'], datetime):
                serializable_failure['order_time'] = serializable_failure['order_time'].isoformat()
            serializable_failures.append(serializable_failure)

        return {
            'time_window': self.time_window,
            'shift': self.shift,
            'orders': self.total_orders,
            'lobby': self.lobby_count,
            'drive_thru': self.drive_thru_count,
            'togo': self.togo_count,
            'avg_fulfillment': self.avg_fulfillment,
            'median_fulfillment': self.median_fulfillment,
            'lobby_avg': self.lobby_avg_fulfillment,
            'drive_avg': self.drive_thru_avg_fulfillment,
            'togo_avg': self.togo_avg_fulfillment,
            'passed_standards': self.passed_standards,
            'passed_historical': self.passed_historical,
            'pass_rate_standards': self.pass_rate_standards,
            'pass_rate_historical': self.pass_rate_historical,
            'streak_type': self.streak_type,
            'is_peak_time': self.is_peak_time,
            'is_empty': self.is_empty,
            'failures_count': len(self.failures),
            'failures': serializable_failures,  # Export full failure details for deduplication
            'by_category': self.by_category,  # Category-level grading metrics
        }

    def __repr__(self) -> str:
        return (
            f"TimeslotDTO("
            f"time={self.time_window}, "
            f"shift={self.shift}, "
            f"orders={self.total_orders}, "
            f"L{self.lobby_count}/D{self.drive_thru_count}/T{self.togo_count}, "
            f"avg={self.avg_fulfillment}min)"
        )
