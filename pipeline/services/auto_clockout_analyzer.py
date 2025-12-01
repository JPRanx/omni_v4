"""
AutoClockoutAnalyzer - Detects and analyzes auto clock-outs.

Identifies employees who were automatically clocked out (forgot to clock out manually),
calculates suggested hours based on shift schedules, and estimates cost impact.

Inspired by V3's auto-clockout detection with V4 architecture.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from pipeline.models.time_entry_dto import TimeEntryDTO
from pipeline.services.result import Result
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AutoClockoutAlert:
    """
    Alert for an employee who was automatically clocked out.
    """
    employee_name: str
    job_title: str
    position_type: str  # 'FOH' or 'BOH'
    clock_in_time: str  # HH:MM AM/PM format
    clock_in_day: str  # Mon, Tue, Wed, etc.
    shift_type: str  # 'morning' or 'evening'
    recorded_hours: float  # Hours system recorded (inflated)
    suggested_hours: float  # Hours they should have worked
    hours_difference: float  # Overage amount
    cost_impact: float  # Estimated $ impact at $15/hr

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'employee': self.employee_name,
            'jobTitle': self.job_title,
            'positionType': self.position_type,
            'clockIn': self.clock_in_time,
            'clockInDay': self.clock_in_day,
            'shiftType': self.shift_type,
            'recordedHours': round(self.recorded_hours, 2),
            'suggestedHours': round(self.suggested_hours, 2),
            'hoursDifference': round(self.hours_difference, 2),
            'costImpact': round(self.cost_impact, 2)
        }


@dataclass(frozen=True)
class AutoClockoutSummary:
    """
    Summary of auto clock-out analysis for a day.
    """
    restaurant_code: str
    business_date: str
    total_detected: int
    total_hours_inflated: float
    total_hours_suggested: float
    estimated_cost_impact: float
    alerts: List[AutoClockoutAlert]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'restaurant': self.restaurant_code,
            'date': self.business_date,
            'totalDetected': self.total_detected,
            'totalHoursInflated': round(self.total_hours_inflated, 2),
            'totalHoursSuggested': round(self.total_hours_suggested, 2),
            'estimatedCostImpact': round(self.estimated_cost_impact, 2),
            'alerts': [alert.to_dict() for alert in self.alerts]
        }


class AutoClockoutAnalyzer:
    """
    Analyzes auto clock-outs from TimeEntries data.

    Detects employees who were automatically clocked out, suggests corrected hours
    based on shift schedules, and calculates cost impact.
    """

    # Shift end times by restaurant and day
    SHIFT_SCHEDULES = {
        'SDR': {
            'weekday': {
                'FOH': {'morning_end': time(14, 0), 'evening_end': time(21, 0)},  # 2pm, 9pm
                'BOH': {'morning_end': time(14, 0), 'evening_end': time(21, 30)}   # 2pm, 9:30pm
            },
            'sunday': {
                'FOH': {'single_shift_end': time(16, 0)},   # 4pm
                'BOH': {'single_shift_end': time(16, 30)}   # 4:30pm
            }
        },
        'TK9': {
            'weekday': {
                'FOH': {'morning_end': time(14, 0), 'evening_end': time(21, 0)},
                'BOH': {'morning_end': time(14, 0), 'evening_end': time(21, 30)}
            },
            'sunday': {
                'FOH': {'single_shift_end': time(16, 0)},
                'BOH': {'single_shift_end': time(16, 30)}
            }
        },
        'T12': {
            'weekday': {
                'FOH': {'morning_end': time(14, 0), 'evening_end': time(22, 0)},   # 2pm, 10pm
                'BOH': {'morning_end': time(14, 0), 'evening_end': time(22, 30)}   # 2pm, 10:30pm
            },
            'sunday': {
                'FOH': {'single_shift_end': time(16, 0)},
                'BOH': {'single_shift_end': time(16, 30)}
            }
        }
    }

    # Position keywords
    FOH_KEYWORDS = [
        'manager', 'shift leader', 'server', 'cashier', 'host', 'hostess',
        'bartender', 'waitress', 'waiter', 'front of house', 'foh', 'counter',
        'drive thru', 'drive-thru'
    ]

    BOH_KEYWORDS = [
        'cook', 'chef', 'kitchen', 'tortillera', 'prep', 'dishwasher',
        'line cook', 'back of house', 'boh', 'grill', 'fryer', 'regular'
    ]

    SHIFT_CUTOFF_HOUR = 14  # 2:00 PM
    AVERAGE_HOURLY_RATE = 15.0  # Default rate for cost estimation

    @classmethod
    def analyze(
        cls,
        time_entries: List[TimeEntryDTO],
        restaurant_code: str,
        business_date: str
    ) -> Result[AutoClockoutSummary]:
        """
        Analyze auto clock-outs for a single day.

        Args:
            time_entries: List of TimeEntryDTO objects
            restaurant_code: Restaurant code
            business_date: Business date (YYYY-MM-DD)

        Returns:
            Result[AutoClockoutSummary]: Summary with alerts
        """
        bound_logger = logger.bind(restaurant=restaurant_code, date=business_date)

        if not time_entries:
            bound_logger.info("no_time_entries_for_auto_clockout")
            return Result.ok(AutoClockoutSummary(
                restaurant_code=restaurant_code,
                business_date=business_date,
                total_detected=0,
                total_hours_inflated=0.0,
                total_hours_suggested=0.0,
                estimated_cost_impact=0.0,
                alerts=[]
            ))

        alerts = []
        total_hours_inflated = 0.0
        total_hours_suggested = 0.0

        # Analyze each time entry
        for entry in time_entries:
            if not entry.auto_clockout:
                continue

            # Skip cashiers (system employees)
            if 'cashier' in entry.employee_name.lower():
                continue

            alert = cls._analyze_entry(entry, restaurant_code, business_date)
            if alert:
                alerts.append(alert)
                total_hours_inflated += alert.recorded_hours
                total_hours_suggested += alert.suggested_hours

        # Calculate total cost impact
        hours_difference = total_hours_inflated - total_hours_suggested
        estimated_cost = hours_difference * cls.AVERAGE_HOURLY_RATE

        summary = AutoClockoutSummary(
            restaurant_code=restaurant_code,
            business_date=business_date,
            total_detected=len(alerts),
            total_hours_inflated=total_hours_inflated,
            total_hours_suggested=total_hours_suggested,
            estimated_cost_impact=estimated_cost,
            alerts=alerts
        )

        bound_logger.info("auto_clockout_analysis_complete",
                        detected=len(alerts),
                        cost_impact=round(estimated_cost, 2))

        return Result.ok(summary)

    @classmethod
    def _analyze_entry(
        cls,
        entry: TimeEntryDTO,
        restaurant_code: str,
        business_date: str
    ) -> Optional[AutoClockoutAlert]:
        """
        Analyze a single auto clock-out entry.

        Args:
            entry: TimeEntryDTO with auto_clockout=True
            restaurant_code: Restaurant code
            business_date: Business date

        Returns:
            AutoClockoutAlert or None if analysis fails
        """
        try:
            # Determine position type (FOH vs BOH)
            position_type = cls._determine_position_type(entry.job_title)

            # Determine shift type (morning vs evening)
            shift_type = cls._determine_shift_type(entry.clock_in_datetime)

            # Get day of week
            day_type = cls._get_day_type(entry.clock_in_datetime)
            day_name = entry.clock_in_datetime.strftime('%a')  # Mon, Tue, etc.

            # Calculate suggested hours
            suggested_hours = cls._calculate_suggested_hours(
                clock_in=entry.clock_in_datetime,
                shift_type=shift_type,
                position_type=position_type,
                restaurant=restaurant_code,
                day_type=day_type
            )

            # Calculate impact
            hours_difference = entry.total_hours - suggested_hours
            cost_impact = hours_difference * cls.AVERAGE_HOURLY_RATE

            # Format clock-in time
            clock_in_str = entry.clock_in_datetime.strftime('%I:%M %p')

            return AutoClockoutAlert(
                employee_name=entry.employee_name,
                job_title=entry.job_title,
                position_type=position_type,
                clock_in_time=clock_in_str,
                clock_in_day=day_name,
                shift_type=shift_type,
                recorded_hours=entry.total_hours,
                suggested_hours=suggested_hours,
                hours_difference=hours_difference,
                cost_impact=cost_impact
            )

        except Exception as e:
            logger.warning("auto_clockout_analysis_failed",
                         employee=entry.employee_name,
                         error=str(e))
            return None

    @classmethod
    def _determine_position_type(cls, job_title: str) -> str:
        """Determine if position is FOH or BOH."""
        job_lower = job_title.lower()

        for keyword in cls.FOH_KEYWORDS:
            if keyword in job_lower:
                return 'FOH'

        for keyword in cls.BOH_KEYWORDS:
            if keyword in job_lower:
                return 'BOH'

        # Default to FOH if can't determine
        logger.debug("position_type_defaulted", job_title=job_title, default='FOH')
        return 'FOH'

    @classmethod
    def _determine_shift_type(cls, clock_in: datetime) -> str:
        """Determine if morning or evening shift based on clock-in time."""
        return 'morning' if clock_in.hour < cls.SHIFT_CUTOFF_HOUR else 'evening'

    @classmethod
    def _get_day_type(cls, date: datetime) -> str:
        """Get day type (weekday vs sunday)."""
        return 'sunday' if date.weekday() == 6 else 'weekday'

    @classmethod
    def _calculate_suggested_hours(
        cls,
        clock_in: datetime,
        shift_type: str,
        position_type: str,
        restaurant: str,
        day_type: str
    ) -> float:
        """
        Calculate suggested hours based on shift schedules.

        Args:
            clock_in: Clock-in datetime
            shift_type: 'morning' or 'evening'
            position_type: 'FOH' or 'BOH'
            restaurant: Restaurant code
            day_type: 'weekday' or 'sunday'

        Returns:
            Suggested hours (float)
        """
        try:
            # Get schedule
            schedule = cls.SHIFT_SCHEDULES.get(restaurant, cls.SHIFT_SCHEDULES['SDR'])
            day_schedule = schedule[day_type]
            position_schedule = day_schedule.get(position_type, day_schedule['FOH'])

            # Get expected end time
            if day_type == 'sunday':
                end_time = position_schedule['single_shift_end']
            else:
                end_time_key = f'{shift_type}_end'
                end_time = position_schedule[end_time_key]

            # Calculate hours
            clock_in_time = clock_in.time()
            clock_in_dt = datetime.combine(datetime.today(), clock_in_time)
            end_dt = datetime.combine(datetime.today(), end_time)

            # Handle shifts that go past midnight
            if end_dt < clock_in_dt:
                end_dt += timedelta(days=1)

            duration = end_dt - clock_in_dt
            hours = duration.total_seconds() / 3600

            return round(hours, 2)

        except Exception as e:
            logger.error("suggested_hours_calculation_failed", error=str(e))
            # Default to 8 hours if calculation fails
            return 8.0

    @classmethod
    def format_summary(cls, summary: AutoClockoutSummary) -> str:
        """
        Format auto clock-out summary for display.

        Args:
            summary: AutoClockoutSummary object

        Returns:
            Formatted string
        """
        if summary.total_detected == 0:
            return f"[{summary.restaurant_code}] [{summary.business_date}] No auto clock-outs detected"

        lines = [
            f"[{summary.restaurant_code}] [{summary.business_date}] Auto Clock-Out Summary:",
            f"  Detected: {summary.total_detected} employees",
            f"  Hours Inflated: {summary.total_hours_inflated:.1f}h",
            f"  Suggested Hours: {summary.total_hours_suggested:.1f}h",
            f"  Cost Impact: ${summary.estimated_cost_impact:.2f}",
            ""
        ]

        # Show top 5 alerts
        for alert in summary.alerts[:5]:
            lines.extend([
                f"  * {alert.employee_name} ({alert.position_type})",
                f"    Clock-in: {alert.clock_in_time} {alert.clock_in_day} ({alert.shift_type} shift)",
                f"    Hours: {alert.recorded_hours:.1f}h -> {alert.suggested_hours:.1f}h (${alert.cost_impact:.2f} impact)",
                ""
            ])

        if len(summary.alerts) > 5:
            lines.append(f"  ... and {len(summary.alerts) - 5} more")

        return '\n'.join(lines)
