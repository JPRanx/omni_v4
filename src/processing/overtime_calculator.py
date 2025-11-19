"""
OvertimeCalculator - Calculate employee overtime hours (>40 hours/week).

Tracks weekly employee hours (Monday-Sunday) and identifies overtime:
- Regular hours: ≤40 hours/week
- Overtime hours: >40 hours/week (paid at 1.5x rate)
- Severity levels: Normal (1-10h), Warning (10-20h), Critical (20+h)

This is different from AutoClockoutAnalyzer which detects forgot-to-clock-out issues.
"""

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from src.models.time_entry_dto import TimeEntryDTO
from src.core import Result
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class EmployeeOvertimeRecord:
    """
    Single employee's overtime record for the week.

    Matches V3 Overtime Modal format:
    - employee_name, job_title, restaurant
    - regular_hours (≤40), overtime_hours (>40), overtime_cost
    - hourly_rate, status (normal/warning/critical)
    """
    employee_name: str
    job_title: str
    restaurant: str
    regular_hours: float  # ≤40
    overtime_hours: float  # >40
    overtime_cost: float  # overtime_hours * hourly_rate * 1.5
    hourly_rate: float
    status: str  # 'normal', 'warning', 'critical'

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization."""
        return {
            'employee_name': self.employee_name,
            'job_title': self.job_title,
            'restaurant': self.restaurant,
            'regular_hours': round(self.regular_hours, 1),
            'overtime_hours': round(self.overtime_hours, 1),
            'overtime_cost': round(self.overtime_cost, 2),
            'hourly_rate': round(self.hourly_rate, 2),
            'status': self.status
        }


@dataclass(frozen=True)
class OvertimeSummary:
    """
    Summary of all employees with overtime for the week.
    """
    total_employees: int
    total_overtime_hours: float
    total_overtime_cost: float
    employees: List[EmployeeOvertimeRecord]

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization."""
        return {
            'total_employees': self.total_employees,
            'total_overtime_hours': round(self.total_overtime_hours, 1),
            'total_overtime_cost': round(self.total_overtime_cost, 2),
            'employees': [emp.to_dict() for emp in self.employees]
        }


class OvertimeCalculator:
    """
    Calculate employee overtime for a week of time entries.

    Overtime Rules:
    1. Regular hours = min(40, total_weekly_hours)
    2. Overtime hours = max(0, total_weekly_hours - 40)
    3. Overtime cost = overtime_hours * hourly_rate * 1.5
    4. Severity: Normal (1-10h), Warning (10-20h), Critical (20+h)
    """

    # Severity thresholds (same as V3 Overtime Modal)
    WARNING_THRESHOLD = 10.0  # 10-20 hours = warning
    CRITICAL_THRESHOLD = 20.0  # 20+ hours = critical

    @classmethod
    def calculate_weekly_overtime(
        cls,
        time_entries_by_date: Dict[str, List[TimeEntryDTO]],
        restaurant_code: str
    ) -> Result[OvertimeSummary]:
        """
        Calculate overtime for a week of time entries.

        Args:
            time_entries_by_date: Dict mapping date (YYYY-MM-DD) to TimeEntry list
            restaurant_code: Restaurant code (for record attribution)

        Returns:
            Result[OvertimeSummary] with employee overtime records
        """
        bound_logger = logger.bind(restaurant=restaurant_code)

        try:
            # Aggregate employee hours by week
            employee_hours = cls._aggregate_weekly_hours(time_entries_by_date)

            # Calculate overtime for each employee
            overtime_records = []

            for emp_key, data in employee_hours.items():
                employee_name = data['employee_name']
                job_title = data['job_title']
                total_hours = data['total_hours']
                hourly_rate = data['hourly_rate']

                # Skip employees with no overtime
                if total_hours <= 40.0:
                    continue

                # Calculate overtime
                regular_hours = min(40.0, total_hours)
                overtime_hours = max(0.0, total_hours - 40.0)
                overtime_cost = overtime_hours * hourly_rate * 1.5

                # Determine severity status
                if overtime_hours >= cls.CRITICAL_THRESHOLD:
                    status = 'critical'
                elif overtime_hours >= cls.WARNING_THRESHOLD:
                    status = 'warning'
                else:
                    status = 'normal'

                record = EmployeeOvertimeRecord(
                    employee_name=employee_name,
                    job_title=job_title,
                    restaurant=restaurant_code,
                    regular_hours=regular_hours,
                    overtime_hours=overtime_hours,
                    overtime_cost=overtime_cost,
                    hourly_rate=hourly_rate,
                    status=status
                )

                overtime_records.append(record)

            # Sort by overtime hours (descending)
            overtime_records.sort(key=lambda x: x.overtime_hours, reverse=True)

            # Calculate summary
            total_employees = len(overtime_records)
            total_overtime_hours = sum(r.overtime_hours for r in overtime_records)
            total_overtime_cost = sum(r.overtime_cost for r in overtime_records)

            summary = OvertimeSummary(
                total_employees=total_employees,
                total_overtime_hours=total_overtime_hours,
                total_overtime_cost=total_overtime_cost,
                employees=overtime_records
            )

            bound_logger.info(
                "overtime_calculated",
                total_employees=total_employees,
                total_ot_hours=total_overtime_hours,
                total_ot_cost=total_overtime_cost
            )

            return Result.ok(summary)

        except Exception as e:
            bound_logger.error("overtime_calculation_failed", error=str(e))
            return Result.fail(ValueError(f"Overtime calculation failed: {str(e)}"))

    @classmethod
    def _aggregate_weekly_hours(
        cls,
        time_entries_by_date: Dict[str, List[TimeEntryDTO]]
    ) -> Dict[str, Dict]:
        """
        Aggregate employee hours across all dates in the week.

        Args:
            time_entries_by_date: Dict mapping date to TimeEntry list

        Returns:
            Dict mapping employee_key to aggregated data:
            {
                'employee_name': str,
                'job_title': str,
                'total_hours': float,
                'hourly_rate': float (max rate seen),
                'dates': List[str]
            }
        """
        employee_data = defaultdict(lambda: {
            'employee_name': '',
            'job_title': '',
            'total_hours': 0.0,
            'hourly_rate': 0.0,
            'dates': []
        })

        for date_str, entries in time_entries_by_date.items():
            for entry in entries:
                # Create employee key (name + job title for uniqueness)
                emp_key = f"{entry.employee_name}|{entry.job_title}"

                # Initialize if first time seeing this employee
                if not employee_data[emp_key]['employee_name']:
                    employee_data[emp_key]['employee_name'] = entry.employee_name
                    employee_data[emp_key]['job_title'] = entry.job_title

                # Accumulate hours
                employee_data[emp_key]['total_hours'] += entry.total_hours

                # Track max hourly rate (use property)
                current_rate = entry.hourly_rate
                employee_data[emp_key]['hourly_rate'] = max(
                    employee_data[emp_key]['hourly_rate'],
                    current_rate
                )

                # Track dates worked
                if date_str not in employee_data[emp_key]['dates']:
                    employee_data[emp_key]['dates'].append(date_str)

        return dict(employee_data)
