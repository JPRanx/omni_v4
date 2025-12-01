"""
TimeEntryDTO - Time entry data transfer object.

Represents employee clock-in/out data from TimeEntries CSV.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from pipeline.services import Result


@dataclass(frozen=True)
class TimeEntryDTO:
    """
    Time entry data for employee shift tracking.

    Attributes:
        employee_name: Employee full name
        job_title: Job position (Server, Cook, Shift Manager, etc.)
        clock_in_datetime: Clock-in timestamp
        clock_out_datetime: Clock-out timestamp (None if still clocked in)
        auto_clockout: Whether this was an automatic clockout
        total_hours: Total hours worked
        unpaid_break_time: Hours of unpaid breaks
        paid_break_time: Hours of paid breaks
        payable_hours: Hours eligible for payment
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date for this entry
    """

    employee_name: str
    job_title: str
    clock_in_datetime: datetime
    clock_out_datetime: Optional[datetime]
    auto_clockout: bool
    total_hours: float
    unpaid_break_time: float
    paid_break_time: float
    payable_hours: float
    restaurant_code: str
    business_date: str  # ISO format: YYYY-MM-DD

    @property
    def is_manager(self) -> bool:
        """Check if employee is a manager based on job title."""
        manager_keywords = ['manager', 'shift leader']
        return any(keyword in self.job_title.lower() for keyword in manager_keywords)

    @property
    def is_server(self) -> bool:
        """Check if employee is a server based on job title."""
        server_keywords = ['server', 'waiter', 'waitress']
        return any(keyword in self.job_title.lower() for keyword in server_keywords)

    @property
    def is_cook(self) -> bool:
        """Check if employee is a cook based on job title."""
        cook_keywords = ['cook', 'chef', 'prep']
        return any(keyword in self.job_title.lower() for keyword in cook_keywords)

    @property
    def clock_in_hour(self) -> int:
        """Get clock-in hour (0-23)."""
        return self.clock_in_datetime.hour

    @property
    def clock_out_hour(self) -> Optional[int]:
        """Get clock-out hour (0-23) or None if not clocked out."""
        return self.clock_out_datetime.hour if self.clock_out_datetime else None

    def is_working_during(self, start_hour: int, end_hour: int) -> bool:
        """
        Check if employee was working during specified hour range.

        Args:
            start_hour: Start hour (0-23)
            end_hour: End hour (0-23)

        Returns:
            True if employee's shift overlaps with the specified range
        """
        if self.clock_out_datetime is None:
            # Still clocked in, assume working through end of day
            return self.clock_in_hour <= end_hour

        # Check if shift overlaps with target range
        return (self.clock_in_hour < end_hour and
                (self.clock_out_hour is None or self.clock_out_hour > start_hour))

    def is_working_at(self, target_datetime: datetime) -> bool:
        """
        Check if employee was clocked in at a specific datetime.

        Args:
            target_datetime: The datetime to check

        Returns:
            True if employee was clocked in at the specified time
        """
        if self.clock_out_datetime is None:
            # Still clocked in, check if target is after clock-in
            return target_datetime >= self.clock_in_datetime

        # Check if target is within shift window
        return (self.clock_in_datetime <= target_datetime <= self.clock_out_datetime)

    @property
    def hourly_rate(self) -> float:
        """
        Calculate hourly rate from payable hours.
        Default to $15/hr if calculation not possible.
        """
        # This is a simplified estimation
        # In reality, hourly rate should come from PayrollExport
        return 15.0  # Default rate

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'employee_name': self.employee_name,
            'job_title': self.job_title,
            'clock_in_datetime': self.clock_in_datetime.isoformat() if self.clock_in_datetime else None,
            'clock_out_datetime': self.clock_out_datetime.isoformat() if self.clock_out_datetime else None,
            'auto_clockout': self.auto_clockout,
            'total_hours': self.total_hours,
            'unpaid_break_time': self.unpaid_break_time,
            'paid_break_time': self.paid_break_time,
            'payable_hours': self.payable_hours,
            'restaurant_code': self.restaurant_code,
            'business_date': self.business_date
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Result["TimeEntryDTO"]:
        """Create TimeEntryDTO from dictionary."""
        try:
            clock_in = datetime.fromisoformat(data['clock_in_datetime']) if data.get('clock_in_datetime') else None
            clock_out = datetime.fromisoformat(data['clock_out_datetime']) if data.get('clock_out_datetime') else None

            return Result.ok(TimeEntryDTO(
                employee_name=data['employee_name'],
                job_title=data['job_title'],
                clock_in_datetime=clock_in,
                clock_out_datetime=clock_out,
                auto_clockout=data.get('auto_clockout', False),
                total_hours=float(data.get('total_hours', 0.0)),
                unpaid_break_time=float(data.get('unpaid_break_time', 0.0)),
                paid_break_time=float(data.get('paid_break_time', 0.0)),
                payable_hours=float(data.get('payable_hours', 0.0)),
                restaurant_code=data.get('restaurant_code', ''),
                business_date=data.get('business_date', '')
            ))
        except (KeyError, ValueError, TypeError) as e:
            from pipeline.services import ValidationError
            return Result.fail(ValidationError(
                message=f"Failed to deserialize TimeEntryDTO: {str(e)}",
                context={'data': data, 'error': str(e)}
            ))
