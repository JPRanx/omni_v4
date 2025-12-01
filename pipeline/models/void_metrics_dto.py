"""
VoidMetricsDTO - Void transaction data by shift.

Represents voided orders with detailed information including employees and reasons.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class VoidTransactionDTO:
    """
    Individual void transaction details.

    Attributes:
        order_number: Order number that was voided
        void_date: When the void occurred
        server: Server who initiated the order
        approver: Manager who approved the void
        reason: Reason for the void (e.g., "Customer Changed Mind", "Server Error")
        item_count: Number of items voided in this order
        total_amount: Total dollar amount voided
        items_detail: List of item names voided
    """

    order_number: str
    void_date: datetime
    server: str
    approver: str
    reason: str
    item_count: int
    total_amount: float
    items_detail: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'order_number': self.order_number,
            'void_date': self.void_date.isoformat() if isinstance(self.void_date, datetime) else str(self.void_date),
            'server': self.server,
            'approver': self.approver,
            'reason': self.reason,
            'item_count': self.item_count,
            'total_amount': round(self.total_amount, 2),
            'items': self.items_detail
        }


@dataclass(frozen=True)
class VoidMetricsDTO:
    """
    Void transactions split by shift.

    Attributes:
        morning_voids: List of void transactions in morning shift (6 AM - 2 PM)
        evening_voids: List of void transactions in evening shift (2 PM - 10 PM)
    """

    morning_voids: List[VoidTransactionDTO]
    evening_voids: List[VoidTransactionDTO]

    @property
    def morning_void_count(self) -> int:
        """Number of voided orders in morning shift."""
        return len(self.morning_voids)

    @property
    def evening_void_count(self) -> int:
        """Number of voided orders in evening shift."""
        return len(self.evening_voids)

    @property
    def total_void_count(self) -> int:
        """Total void orders for the day."""
        return self.morning_void_count + self.evening_void_count

    @property
    def morning_void_amount(self) -> float:
        """Total dollar amount voided in morning."""
        return sum(v.total_amount for v in self.morning_voids)

    @property
    def evening_void_amount(self) -> float:
        """Total dollar amount voided in evening."""
        return sum(v.total_amount for v in self.evening_voids)

    @property
    def total_void_amount(self) -> float:
        """Total dollar amount voided for the day."""
        return self.morning_void_amount + self.evening_void_amount

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'morning': {
                'count': self.morning_void_count,
                'amount': round(self.morning_void_amount, 2),
                'transactions': [v.to_dict() for v in self.morning_voids]
            },
            'evening': {
                'count': self.evening_void_count,
                'amount': round(self.evening_void_amount, 2),
                'transactions': [v.to_dict() for v in self.evening_voids]
            },
            'total': {
                'count': self.total_void_count,
                'amount': round(self.total_void_amount, 2)
            }
        }