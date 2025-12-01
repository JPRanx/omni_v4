"""
LaborDTO - Data Transfer Object for labor data

Represents labor cost and hours data from ingestion stage.
Immutable (frozen dataclass) to ensure data integrity throughout pipeline.

Usage:
    from pipeline.models.labor_dto import LaborDTO
    from pipeline.services import Result

    # Create from validation
    result = LaborDTO.create(
        restaurant_code="SDR",
        business_date="2025-01-15",
        total_hours_worked=100.0,
        total_labor_cost=1250.0,
        employee_count=10
    )

    if result.is_ok():
        dto = result.unwrap()
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

from pipeline.services import Result, ValidationError


@dataclass(frozen=True)
class LaborDTO:
    """
    Immutable DTO representing labor data from Toast POS.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date (YYYY-MM-DD)
        total_hours_worked: Total hours worked across all employees
        total_labor_cost: Total labor cost (regular + overtime)
        employee_count: Number of employees who worked
        total_regular_hours: Total regular hours (≤40 per week per employee)
        total_overtime_hours: Total overtime hours (>40 per week per employee)
        total_regular_cost: Cost of regular hours
        total_overtime_cost: Cost of overtime hours
        average_hourly_rate: Average hourly rate across all employees
    """

    # Required fields
    restaurant_code: str
    business_date: str
    total_hours_worked: float
    total_labor_cost: float
    employee_count: int

    # Optional detailed breakdown
    total_regular_hours: float = 0.0
    total_overtime_hours: float = 0.0
    total_regular_cost: float = 0.0
    total_overtime_cost: float = 0.0
    average_hourly_rate: float = 0.0

    @staticmethod
    def create(
        restaurant_code: str,
        business_date: str,
        total_hours_worked: float,
        total_labor_cost: float,
        employee_count: int,
        total_regular_hours: float = 0.0,
        total_overtime_hours: float = 0.0,
        total_regular_cost: float = 0.0,
        total_overtime_cost: float = 0.0,
        average_hourly_rate: float = 0.0,
    ) -> Result["LaborDTO"]:
        """
        Create and validate LaborDTO.

        Args:
            restaurant_code: Restaurant identifier
            business_date: Business date (YYYY-MM-DD)
            total_hours_worked: Total hours worked
            total_labor_cost: Total labor cost
            employee_count: Number of employees
            total_regular_hours: Regular hours (optional)
            total_overtime_hours: Overtime hours (optional)
            total_regular_cost: Regular cost (optional)
            total_overtime_cost: Overtime cost (optional)
            average_hourly_rate: Average hourly rate (optional)

        Returns:
            Result[LaborDTO]: Success with DTO or failure with ValidationError
        """
        dto = LaborDTO(
            restaurant_code=restaurant_code,
            business_date=business_date,
            total_hours_worked=total_hours_worked,
            total_labor_cost=total_labor_cost,
            employee_count=employee_count,
            total_regular_hours=total_regular_hours,
            total_overtime_hours=total_overtime_hours,
            total_regular_cost=total_regular_cost,
            total_overtime_cost=total_overtime_cost,
            average_hourly_rate=average_hourly_rate,
        )

        return dto.validate()

    def validate(self) -> Result["LaborDTO"]:
        """
        Validate DTO fields.

        Returns:
            Result[LaborDTO]: Self if valid, ValidationError if invalid
        """
        # Validate restaurant code
        if not self.restaurant_code or not self.restaurant_code.strip():
            return Result.fail(
                ValidationError(
                    message="restaurant_code is required",
                    context={"field": "restaurant_code", "value": self.restaurant_code}
                )
            )

        # Validate business date format (YYYY-MM-DD)
        if not self._is_valid_date(self.business_date):
            return Result.fail(
                ValidationError(
                    message="business_date must be in YYYY-MM-DD format",
                    context={"field": "business_date", "value": self.business_date}
                )
            )

        # Validate numeric fields are non-negative
        if self.total_hours_worked < 0:
            return Result.fail(
                ValidationError(
                    message="total_hours_worked cannot be negative",
                    context={"field": "total_hours_worked", "value": self.total_hours_worked}
                )
            )

        if self.total_labor_cost < 0:
            return Result.fail(
                ValidationError(
                    message="total_labor_cost cannot be negative",
                    context={"field": "total_labor_cost", "value": self.total_labor_cost}
                )
            )

        if self.employee_count < 0:
            return Result.fail(
                ValidationError(
                    message="employee_count cannot be negative",
                    context={"field": "employee_count", "value": self.employee_count}
                )
            )

        if self.total_regular_hours < 0:
            return Result.fail(
                ValidationError(
                    message="total_regular_hours cannot be negative",
                    context={"field": "total_regular_hours", "value": self.total_regular_hours}
                )
            )

        if self.total_overtime_hours < 0:
            return Result.fail(
                ValidationError(
                    message="total_overtime_hours cannot be negative",
                    context={"field": "total_overtime_hours", "value": self.total_overtime_hours}
                )
            )

        if self.total_regular_cost < 0:
            return Result.fail(
                ValidationError(
                    message="total_regular_cost cannot be negative",
                    context={"field": "total_regular_cost", "value": self.total_regular_cost}
                )
            )

        if self.total_overtime_cost < 0:
            return Result.fail(
                ValidationError(
                    message="total_overtime_cost cannot be negative",
                    context={"field": "total_overtime_cost", "value": self.total_overtime_cost}
                )
            )

        if self.average_hourly_rate < 0:
            return Result.fail(
                ValidationError(
                    message="average_hourly_rate cannot be negative",
                    context={"field": "average_hourly_rate", "value": self.average_hourly_rate}
                )
            )

        # Validate breakdown consistency (if provided)
        breakdown_hours = self.total_regular_hours + self.total_overtime_hours
        if breakdown_hours > 0:
            # Allow 0.1% tolerance for floating point errors
            tolerance = self.total_hours_worked * 0.001
            if abs(breakdown_hours - self.total_hours_worked) > tolerance:
                return Result.fail(
                    ValidationError(
                        message="Regular + overtime hours must equal total hours",
                        context={
                            "total_hours_worked": self.total_hours_worked,
                            "regular_hours": self.total_regular_hours,
                            "overtime_hours": self.total_overtime_hours,
                            "sum": breakdown_hours
                        }
                    )
                )

        breakdown_cost = self.total_regular_cost + self.total_overtime_cost
        if breakdown_cost > 0:
            # Allow 0.1% tolerance for floating point errors
            tolerance = self.total_labor_cost * 0.001
            if abs(breakdown_cost - self.total_labor_cost) > tolerance:
                return Result.fail(
                    ValidationError(
                        message="Regular + overtime cost must equal total cost",
                        context={
                            "total_labor_cost": self.total_labor_cost,
                            "regular_cost": self.total_regular_cost,
                            "overtime_cost": self.total_overtime_cost,
                            "sum": breakdown_cost
                        }
                    )
                )

        return Result.ok(self)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary (JSON-serializable).

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "restaurant_code": self.restaurant_code,
            "business_date": self.business_date,
            "total_hours_worked": self.total_hours_worked,
            "total_labor_cost": self.total_labor_cost,
            "employee_count": self.employee_count,
            "total_regular_hours": self.total_regular_hours,
            "total_overtime_hours": self.total_overtime_hours,
            "total_regular_cost": self.total_regular_cost,
            "total_overtime_cost": self.total_overtime_cost,
            "average_hourly_rate": self.average_hourly_rate,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Result["LaborDTO"]:
        """
        Create from dictionary.

        Args:
            data: Dictionary with labor data

        Returns:
            Result[LaborDTO]: Success with DTO or failure with ValidationError
        """
        try:
            return LaborDTO.create(
                restaurant_code=data["restaurant_code"],
                business_date=data["business_date"],
                total_hours_worked=float(data["total_hours_worked"]),
                total_labor_cost=float(data["total_labor_cost"]),
                employee_count=int(data["employee_count"]),
                total_regular_hours=float(data.get("total_regular_hours", 0.0)),
                total_overtime_hours=float(data.get("total_overtime_hours", 0.0)),
                total_regular_cost=float(data.get("total_regular_cost", 0.0)),
                total_overtime_cost=float(data.get("total_overtime_cost", 0.0)),
                average_hourly_rate=float(data.get("average_hourly_rate", 0.0)),
            )
        except KeyError as e:
            return Result.fail(
                ValidationError(
                    message=f"Missing required field: {e}",
                    context={"missing_field": str(e), "data": data}
                )
            )
        except (ValueError, TypeError) as e:
            return Result.fail(
                ValidationError(
                    message=f"Invalid data type: {e}",
                    context={"error": str(e), "data": data}
                )
            )

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"LaborDTO("
            f"restaurant={self.restaurant_code}, "
            f"date={self.business_date}, "
            f"hours={self.total_hours_worked:.1f}, "
            f"cost=${self.total_labor_cost:.2f}, "
            f"employees={self.employee_count})"
        )
