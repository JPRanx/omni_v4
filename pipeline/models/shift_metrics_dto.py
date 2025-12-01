"""
ShiftMetricsDTO - Shift-level metrics data transfer object.

Represents morning and evening shift breakdown for a business day.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ShiftMetricsDTO:
    """
    Shift-level metrics for morning and evening shifts.

    Attributes:
        restaurant_code: Restaurant identifier (SDR, T12, TK9)
        business_date: Business date (ISO format: YYYY-MM-DD)

        morning_sales: Total sales for morning shift (6 AM - 2 PM)
        morning_labor: Total labor cost for morning shift
        morning_manager: Manager name for morning shift (or "Not Assigned")
        morning_voids: Number of void orders in morning
        morning_order_count: Number of orders in morning

        evening_sales: Total sales for evening shift (2 PM - 10 PM)
        evening_labor: Total labor cost for evening shift
        evening_manager: Manager name for evening shift (or "Not Assigned")
        evening_voids: Number of void orders in evening
        evening_order_count: Number of orders in evening
    """

    restaurant_code: str
    business_date: str

    # Morning shift (6 AM - 2 PM)
    morning_sales: float
    morning_labor: float
    morning_manager: str
    morning_voids: int
    morning_order_count: int

    # Evening shift (2 PM - 10 PM)
    evening_sales: float
    evening_labor: float
    evening_manager: str
    evening_voids: int
    evening_order_count: int

    @property
    def total_sales(self) -> float:
        """Total sales for both shifts."""
        return self.morning_sales + self.evening_sales

    @property
    def total_labor(self) -> float:
        """Total labor cost for both shifts."""
        return self.morning_labor + self.evening_labor

    @property
    def total_voids(self) -> int:
        """Total void orders for both shifts."""
        return self.morning_voids + self.evening_voids

    @property
    def total_orders(self) -> int:
        """Total orders for both shifts."""
        return self.morning_order_count + self.evening_order_count

    @property
    def morning_labor_percent(self) -> float:
        """Morning labor percentage."""
        return (self.morning_labor / self.morning_sales * 100) if self.morning_sales > 0 else 0

    @property
    def evening_labor_percent(self) -> float:
        """Evening labor percentage."""
        return (self.evening_labor / self.evening_sales * 100) if self.evening_sales > 0 else 0

    @property
    def total_labor_percent(self) -> float:
        """Overall labor percentage."""
        return (self.total_labor / self.total_sales * 100) if self.total_sales > 0 else 0

    @property
    def morning_avg_order_value(self) -> float:
        """Average order value for morning shift."""
        return (self.morning_sales / self.morning_order_count) if self.morning_order_count > 0 else 0

    @property
    def evening_avg_order_value(self) -> float:
        """Average order value for evening shift."""
        return (self.evening_sales / self.evening_order_count) if self.evening_order_count > 0 else 0

    def to_dict(self) -> dict:
        """
        Convert to dictionary format for Investigation Modal.

        Returns:
            Dict with shifts.morning and shifts.evening structure
        """
        return {
            'morning': {
                'sales': round(self.morning_sales, 2),
                'labor': round(self.morning_labor, 2),
                'laborPercent': round(self.morning_labor_percent, 1),
                'manager': self.morning_manager,
                'voids': self.morning_voids,
                'orderCount': self.morning_order_count,
                'avgOrderValue': round(self.morning_avg_order_value, 2)
            },
            'evening': {
                'sales': round(self.evening_sales, 2),
                'labor': round(self.evening_labor, 2),
                'laborPercent': round(self.evening_labor_percent, 1),
                'manager': self.evening_manager,
                'voids': self.evening_voids,
                'orderCount': self.evening_order_count,
                'avgOrderValue': round(self.evening_avg_order_value, 2)
            }
        }
