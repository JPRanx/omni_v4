"""
Cash Flow Extractor.

Extracts cash flow data from Toast POS CSV exports:
- Cash activity.csv (summary totals)
- Cash summary.csv (closeout reconciliation)
- cash-mgmt_{date}.csv (transaction-level detail)

All PAY_OUT transactions are treated as vendor payouts (COGS).
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd
import logging

from pipeline.models.cash_flow_dto import (
    VendorPayout,
    CashCollectionEvent,
    DrawerCashFlow,
    ShiftCashFlow,
    DailyCashFlow
)
from pipeline.services.result import Result


logger = logging.getLogger(__name__)


class CashFlowExtractor:
    """Extracts cash flow data from Toast CSV files."""

    def extract_from_csvs(
        self,
        csv_dir: Path,
        business_date: str,
        restaurant_code: str
    ) -> Result[DailyCashFlow]:
        """
        Extract complete cash flow from Toast CSV files.

        Args:
            csv_dir: Directory containing CSV files
            business_date: YYYY-MM-DD format
            restaurant_code: SDR, T12, or TK9

        Returns:
            Result[DailyCashFlow]: Complete daily cash flow or error
        """
        try:
            # Load CSV files
            cash_activity = self._load_cash_activity(csv_dir / "Cash activity.csv")
            cash_summary = self._load_cash_summary(csv_dir / "Cash summary.csv")

            # Load cash-mgmt file (with date in filename)
            date_underscore = business_date.replace('-', '_')
            cash_mgmt_path = csv_dir / f"cash-mgmt_{date_underscore}.csv"
            cash_mgmt = self._load_cash_mgmt(cash_mgmt_path)

            if cash_mgmt is None:
                logger.warning(f"No cash-mgmt file found for {business_date}, using summary only")
                # Graceful degradation: use summary data only
                return self._build_flow_from_summary(
                    cash_activity,
                    cash_summary,
                    business_date,
                    restaurant_code
                )

            # Extract transactions by type
            payouts = self._extract_payouts(cash_mgmt)
            tips = self._extract_tipouts(cash_mgmt)
            payments = self._extract_payments(cash_mgmt)
            collections = self._extract_collections(cash_mgmt)

            # Build shift-level flows
            morning_shift = self._build_shift_flow(
                shift_name="Morning",
                payouts=payouts,
                tips=tips,
                payments=payments,
                collections=collections
            )

            evening_shift = self._build_shift_flow(
                shift_name="Evening",
                payouts=payouts,
                tips=tips,
                payments=payments,
                collections=collections
            )

            # Create daily cash flow
            daily_flow = DailyCashFlow.create(
                business_date=business_date,
                restaurant_code=restaurant_code,
                morning_shift=morning_shift,
                evening_shift=evening_shift
            )

            return Result.ok(daily_flow)

        except Exception as e:
            return Result.fail(ValueError(f"Failed to extract cash flow: {e}"))

    def _load_cash_activity(self, path: Path) -> Dict:
        """Load Cash activity.csv (single row with totals)."""
        if not path.exists():
            logger.warning(f"Cash activity file not found: {path}")
            return {'total_cash': 0, 'cash_payments': 0, 'cash_gratuity': 0}

        try:
            df = pd.read_csv(path)
            if df.empty:
                return {'total_cash': 0, 'cash_payments': 0, 'cash_gratuity': 0}

            row = df.iloc[0]
            return {
                'total_cash': float(row.get('Total cash', 0) or 0),
                'cash_payments': float(row.get('Total cash payments', 0) or 0),
                'cash_gratuity': float(row.get('Cash gratuity', 0) or 0)
            }
        except Exception as e:
            logger.error(f"Error loading Cash activity: {e}")
            return {'total_cash': 0, 'cash_payments': 0, 'cash_gratuity': 0}

    def _load_cash_summary(self, path: Path) -> Dict:
        """Load Cash summary.csv (closeout data)."""
        if not path.exists():
            logger.warning(f"Cash summary file not found: {path}")
            return {'expected_cash': 0, 'actual_cash': 0}

        try:
            df = pd.read_csv(path)
            if df.empty:
                return {'expected_cash': 0, 'actual_cash': 0}

            row = df.iloc[0]
            return {
                'expected_cash': float(row.get('Expected closeout cash', 0) or 0),
                'actual_cash': float(row.get('Actual closeout cash', 0) or 0)
            }
        except Exception as e:
            logger.error(f"Error loading Cash summary: {e}")
            return {'expected_cash': 0, 'actual_cash': 0}

    def _load_cash_mgmt(self, path: Path) -> Optional[pd.DataFrame]:
        """Load cash-mgmt CSV (transaction detail)."""
        if not path.exists():
            logger.warning(f"Cash management file not found: {path}")
            return None

        # Try multiple encodings for special characters (Spanish names, etc.)
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1']
        last_error = None

        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(path, encoding=encoding)
                if df.empty:
                    logger.warning(f"Cash management file is empty: {path}")
                    return None
                return df
            except UnicodeDecodeError as e:
                last_error = e
                continue  # Try next encoding
            except Exception as e:
                logger.error(f"Error loading cash-mgmt file: {e}")
                return None

        # If all encodings failed
        logger.error(f"Error loading cash-mgmt file: Could not decode with any encoding (tried utf-8, utf-8-sig, latin-1). Last error: {last_error}")
        return None

    def _extract_payouts(self, df: pd.DataFrame) -> List[VendorPayout]:
        """
        Extract all PAY_OUT transactions as vendor payouts.
        All PAY_OUT = COGS vendor expenses.
        """
        if df is None or df.empty:
            return []

        try:
            # Column is called "Action" not "Action Type"
            action_col = 'Action' if 'Action' in df.columns else 'Action Type'
            payouts_df = df[df[action_col] == 'PAY_OUT'].copy()
            if payouts_df.empty:
                return []

            payouts = []
            for _, row in payouts_df.iterrows():
                try:
                    # PAY_OUT amounts are negative in CSV (money leaving)
                    # Store as positive for expense calculations
                    amount = abs(float(row.get('Amount', 0) or 0))
                    reason = str(row.get('Payout Reason', 'Unknown') or 'Unknown')
                    # Column is "Comment" not "Comments"
                    comments = str(row.get('Comment', row.get('Comments', '')) or '')
                    time_str = str(row.get('Created Date', ''))
                    manager = str(row.get('Employee', 'Unknown') or 'Unknown')
                    drawer = str(row.get('Cash Drawer', 'Unknown') or 'Unknown')

                    shift = self._detect_shift(time_str)
                    vendor_name = self._extract_vendor_name(reason)

                    payouts.append(VendorPayout(
                        amount=amount,
                        reason=reason,
                        comments=comments,
                        time=time_str,
                        manager=manager,
                        drawer=drawer,
                        shift=shift,
                        vendor_name=vendor_name
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse payout row: {e}")
                    continue

            return payouts

        except Exception as e:
            logger.error(f"Error extracting payouts: {e}")
            return []

    def _extract_tipouts(self, df: pd.DataFrame) -> List[Tuple[float, str]]:
        """Extract TIP_OUT transactions."""
        if df is None or df.empty:
            return []

        try:
            action_col = 'Action' if 'Action' in df.columns else 'Action Type'
            tipouts_df = df[df[action_col] == 'TIP_OUT'].copy()
            if tipouts_df.empty:
                return []

            tipouts = []
            for _, row in tipouts_df.iterrows():
                try:
                    # TIP_OUT amounts are negative in CSV (money leaving)
                    # Store as positive for expense calculations
                    amount = abs(float(row.get('Amount', 0) or 0))
                    time_str = str(row.get('Created Date', ''))
                    tipouts.append((amount, time_str))
                except Exception as e:
                    logger.warning(f"Failed to parse tipout row: {e}")
                    continue

            return tipouts

        except Exception as e:
            logger.error(f"Error extracting tipouts: {e}")
            return []

    def _extract_payments(self, df: pd.DataFrame) -> List[Tuple[float, str, str]]:
        """Extract CASH_PAYMENT transactions (customer payments)."""
        if df is None or df.empty:
            return []

        try:
            action_col = 'Action' if 'Action' in df.columns else 'Action Type'
            payments_df = df[df[action_col] == 'CASH_PAYMENT'].copy()
            if payments_df.empty:
                return []

            payments = []
            for _, row in payments_df.iterrows():
                try:
                    amount = float(row.get('Amount', 0) or 0)
                    time_str = str(row.get('Created Date', ''))
                    drawer = str(row.get('Cash Drawer', 'Unknown') or 'Unknown')
                    payments.append((amount, time_str, drawer))
                except Exception as e:
                    logger.warning(f"Failed to parse payment row: {e}")
                    continue

            return payments

        except Exception as e:
            logger.error(f"Error extracting payments: {e}")
            return []

    def _extract_collections(self, df: pd.DataFrame) -> List[CashCollectionEvent]:
        """Extract CASH_COLLECTED events (manager cash pulls)."""
        if df is None or df.empty:
            return []

        try:
            action_col = 'Action' if 'Action' in df.columns else 'Action Type'
            collections_df = df[df[action_col] == 'CASH_COLLECTED'].copy()
            if collections_df.empty:
                return []

            collections = []
            for _, row in collections_df.iterrows():
                try:
                    amount = float(row.get('Amount', 0) or 0)
                    time_str = str(row.get('Created Date', ''))
                    manager = str(row.get('Employee', 'Unknown') or 'Unknown')
                    drawer = str(row.get('Cash Drawer', 'Unknown') or 'Unknown')

                    collections.append(CashCollectionEvent(
                        amount=amount,
                        time=time_str,
                        manager=manager,
                        drawer=drawer
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse collection row: {e}")
                    continue

            return collections

        except Exception as e:
            logger.error(f"Error extracting collections: {e}")
            return []

    def _detect_shift(self, timestamp: str) -> str:
        """
        Determine shift from timestamp.
        Morning: 6am - 2pm (6:00 - 13:59)
        Evening: 2pm - close (14:00 - 05:59)
        """
        try:
            # Try multiple timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%m/%d/%y %I:%M %p',  # 10/20/25 3:52 PM
                '%m/%d/%Y %I:%M %p'   # 10/20/2025 3:52 PM
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    hour = dt.hour
                    return 'Morning' if 6 <= hour < 14 else 'Evening'
                except ValueError:
                    continue

            logger.warning(f"Could not parse timestamp: {timestamp}")
            return 'Evening'  # Default to evening
        except Exception as e:
            logger.error(f"Error detecting shift: {e}")
            return 'Evening'

    def _extract_vendor_name(self, payout_reason: str) -> str:
        """
        Extract vendor name from payout reason using keyword matching.
        Auto-categorizes common vendors.
        """
        if not payout_reason or payout_reason == 'Unknown':
            return 'Other Vendor'

        reason_lower = payout_reason.lower()

        # Keyword matching for common vendors
        if 'sysco' in reason_lower:
            return 'Sysco Food Services'
        elif any(x in reason_lower for x in ['us foods', 'usf', 'us food']):
            return 'US Foods'
        elif any(x in reason_lower for x in ['labatt', 'beer', 'beverage', 'drink']):
            return 'Labatt (Beverage)'
        elif any(x in reason_lower for x in ['depot', 'restaurant depot']):
            return 'Restaurant Depot'
        elif any(x in reason_lower for x in ['produce', 'fresh', 'vegetable', 'fruit']):
            return 'Produce Supplier'
        else:
            # Return first word capitalized as vendor name
            words = payout_reason.split()
            if words:
                return words[0].title()
            return 'Other Vendor'

    def _build_shift_flow(
        self,
        shift_name: str,
        payouts: List[VendorPayout],
        tips: List[Tuple[float, str]],
        payments: List[Tuple[float, str, str]],
        collections: List[CashCollectionEvent]
    ) -> ShiftCashFlow:
        """Build cash flow for a single shift."""

        # Filter transactions for this shift
        shift_payouts = [p for p in payouts if p.shift == shift_name]
        shift_tips = [
            amount for amount, time in tips
            if self._detect_shift(time) == shift_name
        ]
        shift_payments = [
            (amount, time, drawer) for amount, time, drawer in payments
            if self._detect_shift(time) == shift_name
        ]
        shift_collections = [
            c for c in collections
            if self._detect_shift(c.time) == shift_name
        ]

        # Calculate totals
        cash_collected = sum(amount for amount, _, _ in shift_payments)
        tips_total = sum(shift_tips)
        payouts_total = sum(p.amount for p in shift_payouts)
        net_cash = cash_collected - tips_total - payouts_total

        # Group payments by drawer
        drawers = self._group_by_drawer(shift_payments, cash_collected)

        return ShiftCashFlow(
            shift_name=shift_name,
            cash_collected=cash_collected,
            tips_distributed=tips_total,
            vendor_payouts=shift_payouts,
            net_cash=net_cash,
            drawers=drawers,
            cash_collection_events=shift_collections
        )

    def _group_by_drawer(
        self,
        payments: List[Tuple[float, str, str]],
        shift_total: float
    ) -> List[DrawerCashFlow]:
        """Group payments by drawer and calculate percentages."""
        if not payments:
            return []

        drawer_totals = {}
        drawer_counts = {}

        for amount, time, drawer in payments:
            if drawer not in drawer_totals:
                drawer_totals[drawer] = 0
                drawer_counts[drawer] = 0
            drawer_totals[drawer] += amount
            drawer_counts[drawer] += 1

        drawers = []
        for drawer_id in sorted(drawer_totals.keys()):
            total = drawer_totals[drawer_id]
            count = drawer_counts[drawer_id]
            percentage = (total / shift_total * 100) if shift_total > 0 else 0

            drawers.append(DrawerCashFlow(
                drawer_id=drawer_id,
                cash_collected=total,
                transaction_count=count,
                percentage_of_shift=percentage
            ))

        return drawers

    def _build_flow_from_summary(
        self,
        cash_activity: Dict,
        cash_summary: Dict,
        business_date: str,
        restaurant_code: str
    ) -> Result[DailyCashFlow]:
        """
        Build cash flow from summary files only (graceful degradation).
        Used when cash-mgmt file is missing.
        """
        try:
            total_cash = cash_activity.get('total_cash', 0)
            cash_gratuity = cash_activity.get('cash_gratuity', 0)

            # Assume 60/40 split for morning/evening
            morning_cash = total_cash * 0.6
            evening_cash = total_cash * 0.4
            morning_tips = cash_gratuity * 0.6
            evening_tips = cash_gratuity * 0.4

            morning_shift = ShiftCashFlow(
                shift_name="Morning",
                cash_collected=morning_cash,
                tips_distributed=morning_tips,
                vendor_payouts=[],
                net_cash=morning_cash - morning_tips,
                drawers=[],
                cash_collection_events=[]
            )

            evening_shift = ShiftCashFlow(
                shift_name="Evening",
                cash_collected=evening_cash,
                tips_distributed=evening_tips,
                vendor_payouts=[],
                net_cash=evening_cash - evening_tips,
                drawers=[],
                cash_collection_events=[]
            )

            daily_flow = DailyCashFlow.create(
                business_date=business_date,
                restaurant_code=restaurant_code,
                morning_shift=morning_shift,
                evening_shift=evening_shift
            )

            return Result.ok(daily_flow)

        except Exception as e:
            return Result.fail(ValueError(f"Failed to build flow from summary: {e}"))