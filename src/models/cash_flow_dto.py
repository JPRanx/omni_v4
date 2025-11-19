"""
Cash Flow Data Transfer Objects.

Multi-level hierarchy for cash flow tracking:
- Owner (top level)
- Restaurants (SDR, T12, TK9)
- Days (7 days per week)
- Shifts (Morning/Evening per day)
- Drawers (multiple per shift)

All PAY_OUT transactions are treated as vendor payouts (COGS).
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass(frozen=True)
class VendorPayout:
    """
    Represents a single cash payout to a vendor (COGS expense).
    Extracted from cash-mgmt PAY_OUT transactions.
    """
    amount: float
    reason: str  # From "Payout Reason" column
    comments: str  # From "Comments" column
    time: str  # Timestamp of payout
    manager: str  # Employee who authorized payout
    drawer: str  # Which cash drawer
    shift: str  # "Morning" or "Evening"
    vendor_name: str  # Extracted from reason (e.g., "Sysco Food Services")

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'amount': self.amount,
            'reason': self.reason,
            'comments': self.comments,
            'time': self.time,
            'manager': self.manager,
            'drawer': self.drawer,
            'shift': self.shift,
            'vendor_name': self.vendor_name
        }


@dataclass(frozen=True)
class CashCollectionEvent:
    """
    Represents when a manager pulls cash from a drawer.
    Extracted from cash-mgmt CASH_COLLECTED transactions.
    """
    amount: float
    time: str
    manager: str
    drawer: str

    def to_dict(self) -> Dict:
        return {
            'amount': self.amount,
            'time': self.time,
            'manager': self.manager,
            'drawer': self.drawer
        }


@dataclass(frozen=True)
class DrawerCashFlow:
    """
    Cash flow for a single drawer within a shift.
    Detail level - clickable for reference.
    """
    drawer_id: str  # "Drawer 1", "Drawer 2", etc.
    cash_collected: float
    transaction_count: int
    percentage_of_shift: float

    def to_dict(self) -> Dict:
        return {
            'drawer_id': self.drawer_id,
            'cash_collected': self.cash_collected,
            'transaction_count': self.transaction_count,
            'percentage_of_shift': self.percentage_of_shift
        }


@dataclass(frozen=True)
class ShiftCashFlow:
    """
    Cash flow for a single shift (Morning or Evening).
    Prominent level - shows where cash went during shift.
    """
    shift_name: str  # "Morning" or "Evening"
    cash_collected: float  # Total cash from customers
    tips_distributed: float  # TIP_OUT total
    vendor_payouts: List[VendorPayout]  # PAY_OUT transactions
    net_cash: float  # What remains after tips and payouts
    drawers: List[DrawerCashFlow]  # Per-drawer breakdown
    cash_collection_events: List[CashCollectionEvent]  # Manager pulls

    def to_dict(self) -> Dict:
        return {
            'shift_name': self.shift_name,
            'cash_collected': self.cash_collected,
            'tips_distributed': self.tips_distributed,
            'vendor_payouts': [p.to_dict() for p in self.vendor_payouts],
            'total_vendor_payouts': sum(p.amount for p in self.vendor_payouts),
            'net_cash': self.net_cash,
            'drawers': [d.to_dict() for d in self.drawers],
            'cash_collection_events': [e.to_dict() for e in self.cash_collection_events]
        }


@dataclass(frozen=True)
class DailyCashFlow:
    """
    Complete cash flow for a single restaurant on a single day.
    Shows morning and evening shift breakdown.
    """
    business_date: str  # YYYY-MM-DD
    restaurant_code: str  # SDR, T12, or TK9
    morning_shift: ShiftCashFlow
    evening_shift: ShiftCashFlow

    # Daily totals
    total_cash: float
    total_tips: float
    total_vendor_payouts: float
    net_cash: float

    @classmethod
    def create(
        cls,
        business_date: str,
        restaurant_code: str,
        morning_shift: ShiftCashFlow,
        evening_shift: ShiftCashFlow
    ) -> 'DailyCashFlow':
        """Create DailyCashFlow with calculated totals."""
        total_cash = morning_shift.cash_collected + evening_shift.cash_collected
        total_tips = morning_shift.tips_distributed + evening_shift.tips_distributed
        total_vendor_payouts = (
            sum(p.amount for p in morning_shift.vendor_payouts) +
            sum(p.amount for p in evening_shift.vendor_payouts)
        )
        net_cash = total_cash - total_tips - total_vendor_payouts

        return cls(
            business_date=business_date,
            restaurant_code=restaurant_code,
            morning_shift=morning_shift,
            evening_shift=evening_shift,
            total_cash=total_cash,
            total_tips=total_tips,
            total_vendor_payouts=total_vendor_payouts,
            net_cash=net_cash
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'business_date': self.business_date,
            'restaurant_code': self.restaurant_code,
            'morning_shift': self.morning_shift.to_dict(),
            'evening_shift': self.evening_shift.to_dict(),
            'total_cash': self.total_cash,
            'total_tips': self.total_tips,
            'total_vendor_payouts': self.total_vendor_payouts,
            'net_cash': self.net_cash
        }

    def get_all_vendor_payouts(self) -> List[VendorPayout]:
        """Get all vendor payouts for the day (both shifts)."""
        return self.morning_shift.vendor_payouts + self.evening_shift.vendor_payouts


@dataclass(frozen=True)
class RestaurantWeeklyCashFlow:
    """
    Cash flow for a single restaurant across a week (7 days).
    Aggregates daily flows.
    """
    restaurant_code: str
    week_start: str  # YYYY-MM-DD (Monday)
    daily_flows: List[DailyCashFlow]  # 7 days

    # Weekly totals
    total_cash: float
    total_tips: float
    total_vendor_payouts: float
    net_cash: float

    @classmethod
    def create(
        cls,
        restaurant_code: str,
        week_start: str,
        daily_flows: List[DailyCashFlow]
    ) -> 'RestaurantWeeklyCashFlow':
        """Create RestaurantWeeklyCashFlow with calculated totals."""
        total_cash = sum(d.total_cash for d in daily_flows)
        total_tips = sum(d.total_tips for d in daily_flows)
        total_vendor_payouts = sum(d.total_vendor_payouts for d in daily_flows)
        net_cash = sum(d.net_cash for d in daily_flows)

        return cls(
            restaurant_code=restaurant_code,
            week_start=week_start,
            daily_flows=daily_flows,
            total_cash=total_cash,
            total_tips=total_tips,
            total_vendor_payouts=total_vendor_payouts,
            net_cash=net_cash
        )

    def to_dict(self) -> Dict:
        return {
            'restaurant_code': self.restaurant_code,
            'week_start': self.week_start,
            'daily_flows': [d.to_dict() for d in self.daily_flows],
            'total_cash': self.total_cash,
            'total_tips': self.total_tips,
            'total_vendor_payouts': self.total_vendor_payouts,
            'net_cash': self.net_cash
        }

    def get_all_vendor_payouts(self) -> List[VendorPayout]:
        """Get all vendor payouts for the week."""
        payouts = []
        for daily_flow in self.daily_flows:
            payouts.extend(daily_flow.get_all_vendor_payouts())
        return payouts


@dataclass(frozen=True)
class OwnerWeeklyCashFlow:
    """
    Top-level cash flow for owner across all restaurants for a week.
    Owner → Restaurants → Days → Shifts → Drawers
    """
    week_start: str  # YYYY-MM-DD (Monday)
    week_end: str  # YYYY-MM-DD (Sunday)
    restaurants: Dict[str, RestaurantWeeklyCashFlow]  # {SDR: ..., T12: ..., TK9: ...}

    # Owner-level totals
    owner_total_cash: float
    owner_total_tips: float
    owner_total_vendor_payouts: float
    owner_net_cash: float

    @classmethod
    def create(
        cls,
        week_start: str,
        week_end: str,
        restaurants: Dict[str, RestaurantWeeklyCashFlow]
    ) -> 'OwnerWeeklyCashFlow':
        """Create OwnerWeeklyCashFlow with calculated totals."""
        owner_total_cash = sum(r.total_cash for r in restaurants.values())
        owner_total_tips = sum(r.total_tips for r in restaurants.values())
        owner_total_vendor_payouts = sum(r.total_vendor_payouts for r in restaurants.values())
        owner_net_cash = sum(r.net_cash for r in restaurants.values())

        return cls(
            week_start=week_start,
            week_end=week_end,
            restaurants=restaurants,
            owner_total_cash=owner_total_cash,
            owner_total_tips=owner_total_tips,
            owner_total_vendor_payouts=owner_total_vendor_payouts,
            owner_net_cash=owner_net_cash
        )

    def to_dict(self) -> Dict:
        return {
            'week_start': self.week_start,
            'week_end': self.week_end,
            'restaurants': {code: r.to_dict() for code, r in self.restaurants.items()},
            'owner_total_cash': self.owner_total_cash,
            'owner_total_tips': self.owner_total_tips,
            'owner_total_vendor_payouts': self.owner_total_vendor_payouts,
            'owner_net_cash': self.owner_net_cash
        }

    def get_all_vendor_payouts(self) -> List[VendorPayout]:
        """Get all vendor payouts across all restaurants."""
        payouts = []
        for restaurant in self.restaurants.values():
            payouts.extend(restaurant.get_all_vendor_payouts())
        return payouts

    def get_vendor_payouts_by_restaurant(self) -> Dict[str, List[VendorPayout]]:
        """Get vendor payouts grouped by restaurant."""
        return {
            code: restaurant.get_all_vendor_payouts()
            for code, restaurant in self.restaurants.items()
        }