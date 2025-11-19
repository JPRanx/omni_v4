"""
Order Categorizer - Determines order type (Lobby/Drive-Thru/ToGo).

Implements V3's filter-based categorization logic using multiple data sources
to determine the most likely service type for each order.
"""

from typing import Dict, Optional, List
import pandas as pd

from src.core.result import Result
from src.core.errors import ProcessingError
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class OrderCategorizer:
    """
    Categorizes orders into Lobby, Drive-Thru, or ToGo based on multiple signals.

    Uses a filter-based cascade:
    1. Lobby detection: Table presence in multiple sources
    2. Drive-Thru detection: Cash drawer, employee position, fast service
    3. ToGo: Default for everything else

    This logic matches V3's analysis_engine.py categorize_order() method exactly.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize categorizer with optional configuration.

        Args:
            config: Optional configuration dict with thresholds:
                - lobby_table_threshold: Tables in N+ sources = Lobby (default: 2)
                - lobby_time_kitchen_min: Kitchen time > N min with table = Lobby (default: 15)
                - lobby_time_order_min: Order duration > N min with table = Lobby (default: 20)
                - drive_thru_time_kitchen_max: Kitchen time < N min, no table = Drive-Thru (default: 7)
                - drive_thru_time_order_max: Order duration < N min, no table = Drive-Thru (default: 10)
        """
        config = config or {}

        # Thresholds (matching V3)
        self.lobby_table_threshold = config.get('lobby_table_threshold', 2)
        self.lobby_time_kitchen_min = config.get('lobby_time_kitchen_min', 15)
        self.lobby_time_order_min = config.get('lobby_time_order_min', 20)
        self.drive_thru_time_kitchen_max = config.get('drive_thru_time_kitchen_max', 7)
        self.drive_thru_time_order_max = config.get('drive_thru_time_order_max', 10)

        logger.info("order_categorizer_initialized",
                    lobby_table_threshold=self.lobby_table_threshold,
                    lobby_time_kitchen_min=self.lobby_time_kitchen_min,
                    drive_thru_time_kitchen_max=self.drive_thru_time_kitchen_max)

    def categorize_order(
        self,
        check_number: str,
        kitchen_df: pd.DataFrame,
        eod_df: pd.DataFrame,
        order_details_df: pd.DataFrame,
        time_entries_df: Optional[pd.DataFrame] = None
    ) -> Result[str]:
        """
        Categorize a single order as Lobby, Drive-Thru, or ToGo.

        Uses V3's filter cascade logic:
        - Filter 1: Lobby (table in 2+ sources, OR table + server, OR table + long duration)
        - Filter 2: Drive-Thru (drive cash drawer, OR drive position, OR fast service)
        - Filter 3: ToGo (default)

        Args:
            check_number: Order check number to categorize
            kitchen_df: Kitchen Details DataFrame
            eod_df: EOD DataFrame
            order_details_df: OrderDetails DataFrame
            time_entries_df: Optional TimeEntries DataFrame for employee positions

        Returns:
            Result[str]: 'Lobby', 'Drive-Thru', or 'ToGo' on success, error on failure
        """
        try:
            # Collect signals from all data sources
            signals = self._collect_signals(
                check_number,
                kitchen_df,
                eod_df,
                order_details_df,
                time_entries_df
            )

            # Run filter cascade
            category = self._apply_filter_cascade(signals)

            logger.debug("order_categorized",
                        check_number=check_number,
                        category=category,
                        table_count=signals['table_count'],
                        kitchen_duration=signals['kitchen_duration'])

            return Result.ok(category)

        except Exception as e:
            return Result.fail(
                ProcessingError(
                    f"Failed to categorize order {check_number}: {str(e)}",
                    context={'check_number': check_number, 'error': str(e)}
                )
            )

    def categorize_all_orders(
        self,
        kitchen_df: pd.DataFrame,
        eod_df: pd.DataFrame,
        order_details_df: pd.DataFrame,
        time_entries_df: Optional[pd.DataFrame] = None
    ) -> Result[Dict[str, str]]:
        """
        Categorize all orders in the dataset.

        Only categorizes orders that have Kitchen Details entries (fulfilled orders).
        Uses OrderDetails as source of truth for order list.

        Args:
            kitchen_df: Kitchen Details DataFrame
            eod_df: EOD DataFrame
            order_details_df: OrderDetails DataFrame
            time_entries_df: Optional TimeEntries DataFrame

        Returns:
            Result[Dict[str, str]]: Mapping of check_number -> category, or error
        """
        try:
            # Get valid check numbers from Kitchen CSV (fulfilled orders only)
            valid_checks = set(kitchen_df['Check #'].unique())

            # Filter OrderDetails to only fulfilled orders
            fulfilled_orders = order_details_df[
                order_details_df['Order #'].isin(valid_checks)
            ]

            categorizations = {}
            total_orders = len(fulfilled_orders)

            logger.info("categorization_started",
                       total_orders=total_orders,
                       valid_kitchen_checks=len(valid_checks))

            # Categorize each order
            for idx, order_row in fulfilled_orders.iterrows():
                check_num = str(order_row['Order #'])

                result = self.categorize_order(
                    check_num,
                    kitchen_df,
                    eod_df,
                    order_details_df,
                    time_entries_df
                )

                if result.is_ok():
                    categorizations[check_num] = result.unwrap()
                else:
                    # Log error but continue (graceful degradation)
                    logger.warning("order_categorization_failed",
                                 check_number=check_num,
                                 error=str(result.unwrap_err()))
                    categorizations[check_num] = "ToGo"  # Safe default

            # Log distribution
            distribution = self._calculate_distribution(categorizations)
            logger.info("categorization_complete",
                       total=total_orders,
                       categorized=len(categorizations),
                       lobby=distribution['Lobby'],
                       drive_thru=distribution['Drive-Thru'],
                       togo=distribution['ToGo'])

            return Result.ok(categorizations)

        except Exception as e:
            return Result.fail(
                ProcessingError(
                    f"Failed to categorize orders: {str(e)}",
                    context={'error': str(e)}
                )
            )

    def _collect_signals(
        self,
        check_number: str,
        kitchen_df: pd.DataFrame,
        eod_df: pd.DataFrame,
        order_details_df: pd.DataFrame,
        time_entries_df: Optional[pd.DataFrame]
    ) -> Dict:
        """
        Collect categorization signals from all data sources.

        Returns dict with:
        - has_table_kitchen: bool
        - has_table_eod: bool
        - has_table_order: bool
        - table_count: int
        - cash_drawer: str
        - employee_position: str
        - kitchen_duration: float
        - order_duration: float
        - server_name: str
        """
        signals = {
            'has_table_kitchen': False,
            'has_table_eod': False,
            'has_table_order': False,
            'table_count': 0,
            'cash_drawer': '',
            'employee_position': '',
            'kitchen_duration': 0.0,
            'order_duration': 0.0,
            'server_name': ''
        }

        # Normalize check_number to string for comparison
        check_num_str = str(check_number)

        # Check Kitchen for table and duration
        kitchen_rows = kitchen_df[kitchen_df['Check #'].astype(str) == check_num_str]
        if not kitchen_rows.empty:
            table = self._safe_float(kitchen_rows.iloc[0].get('Table'))
            if table and table > 0:
                signals['has_table_kitchen'] = True

            # Get fulfillment time - PARSE duration string (e.g., "5 minutes and 39 seconds")
            duration = kitchen_rows.iloc[0].get('Fulfillment Time')
            signals['kitchen_duration'] = self._parse_duration_string(duration)

            # Get server name
            signals['server_name'] = str(kitchen_rows.iloc[0].get('Server', ''))

        # Check EOD for table and cash drawer
        eod_rows = eod_df[eod_df['Check #'].astype(str) == check_num_str]
        if not eod_rows.empty:
            table = self._safe_float(eod_rows.iloc[0].get('Table'))
            if table and table > 0:
                signals['has_table_eod'] = True

            cash_drawer = eod_rows.iloc[0].get('Cash Drawer', '')
            signals['cash_drawer'] = str(cash_drawer).lower().strip()

        # Check OrderDetails for table and duration
        order_rows = order_details_df[order_details_df['Order #'].astype(str) == check_num_str]
        if not order_rows.empty:
            table = self._safe_float(order_rows.iloc[0].get('Table'))
            if table and table > 0:
                signals['has_table_order'] = True

            # Parse duration string (e.g., "2 minutes and 52 seconds" or "1:23")
            duration_str = order_rows.iloc[0].get('Duration (Opened to Paid)')
            signals['order_duration'] = self._parse_duration_string(duration_str)

        # Check employee position from TimeEntries
        if time_entries_df is not None and not time_entries_df.empty and signals['server_name']:
            position = self._lookup_employee_position(
                signals['server_name'],
                time_entries_df
            )
            signals['employee_position'] = position

        # Calculate table count
        signals['table_count'] = sum([
            signals['has_table_kitchen'],
            signals['has_table_eod'],
            signals['has_table_order']
        ])

        return signals

    def _apply_filter_cascade(self, signals: Dict) -> str:
        """
        Apply V3's filter cascade to categorize order.

        Filter 1: Lobby Detection
        - Table in 2+ sources
        - Table in 1+ source AND server position
        - Table in 1+ source AND long duration

        Filter 2: Drive-Thru Detection
        - Cash drawer contains 'drive'
        - Employee position contains 'drive'
        - No table AND fast kitchen service (<7 min)
        - No table AND fast order completion (<10 min)

        Filter 3: ToGo (Default)
        - Everything else
        """
        table_count = signals['table_count']
        kitchen_duration = signals['kitchen_duration']
        order_duration = signals['order_duration']
        cash_drawer = signals['cash_drawer']
        employee_position = signals['employee_position']

        # FILTER 1: LOBBY CHARACTERISTICS
        if table_count >= self.lobby_table_threshold:
            return "Lobby"

        if table_count >= 1 and employee_position and 'server' in employee_position:
            return "Lobby"

        if table_count >= 1 and (
            kitchen_duration > self.lobby_time_kitchen_min or
            order_duration > self.lobby_time_order_min
        ):
            return "Lobby"

        # FILTER 2: DRIVE-THRU CHARACTERISTICS
        if cash_drawer and ('drive box' in cash_drawer or 'drive' in cash_drawer):
            return "Drive-Thru"

        if employee_position and 'drive' in employee_position:
            return "Drive-Thru"

        if table_count == 0 and kitchen_duration > 0 and kitchen_duration < self.drive_thru_time_kitchen_max:
            return "Drive-Thru"

        if table_count == 0 and order_duration > 0 and order_duration < self.drive_thru_time_order_max:
            return "Drive-Thru"

        # FILTER 3: TOGO (DEFAULT)
        return "ToGo"

    def _safe_float(self, value) -> Optional[float]:
        """
        Safely convert value to float, returning None on failure.

        Handles:
        - None, NaN, empty strings
        - String numbers ('23.5')
        - Already floats
        """
        if value is None or pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        # Try string conversion
        try:
            return float(str(value).strip())
        except (ValueError, AttributeError):
            return None

    def _parse_duration_string(self, duration_str) -> float:
        """
        Parse Toast duration strings to minutes.

        Supports formats:
        - "2 minutes and 52 seconds" -> 2.87
        - "1:23" (MM:SS) -> 1.38
        - "1:23:45" (HH:MM:SS) -> 83.75
        - "15.5" (direct float) -> 15.5
        - None/NaN -> 0.0
        """
        # Handle None first
        if duration_str is None:
            return 0.0

        # Handle pandas NA/NaN (need to check before boolean operations)
        try:
            if pd.isna(duration_str):
                return 0.0
        except TypeError:
            # pd.NA can cause TypeError in boolean context
            return 0.0

        duration_str = str(duration_str).strip()

        # Empty string check
        if not duration_str:
            return 0.0

        # Try direct float conversion first
        try:
            return float(duration_str)
        except ValueError:
            pass

        # Try HH:MM:SS or MM:SS format
        if ':' in duration_str:
            parts = duration_str.split(':')
            try:
                if len(parts) == 3:  # HH:MM:SS
                    return float(parts[0]) * 60 + float(parts[1]) + float(parts[2]) / 60
                elif len(parts) == 2:  # MM:SS
                    return float(parts[0]) + float(parts[1]) / 60
            except (ValueError, IndexError):
                pass

        # Try "X minutes and Y seconds" format
        if 'minute' in duration_str.lower() or 'second' in duration_str.lower():
            import re
            minutes_match = re.search(r'(\d+)\s*minute', duration_str, re.IGNORECASE)
            seconds_match = re.search(r'(\d+)\s*second', duration_str, re.IGNORECASE)

            total_minutes = 0.0
            if minutes_match:
                total_minutes += float(minutes_match.group(1))
            if seconds_match:
                total_minutes += float(seconds_match.group(1)) / 60

            return total_minutes

        # Could not parse
        return 0.0

    def _lookup_employee_position(self, server_name: str, time_entries_df: pd.DataFrame) -> str:
        """
        Look up employee position from TimeEntries by server name.

        Handles name matching:
        - "Smith, John" -> matches "John Smith"
        - "John Smith" -> matches "Smith, John"
        - Partial name matching
        """
        if not server_name:
            return ''

        # Split name into parts
        name_parts = server_name.split(',') if ',' in server_name else server_name.split()

        for name_part in name_parts:
            name_part = name_part.strip()
            if not name_part:
                continue

            # Search for partial name match
            employee_rows = time_entries_df[
                time_entries_df['Employee'].str.contains(name_part, case=False, na=False)
            ]

            if not employee_rows.empty:
                position = str(employee_rows.iloc[0].get('Job Title', '')).lower()
                return position

        return ''

    def _calculate_distribution(self, categorizations: Dict[str, str]) -> Dict[str, int]:
        """Calculate count of each category."""
        distribution = {'Lobby': 0, 'Drive-Thru': 0, 'ToGo': 0}

        for category in categorizations.values():
            if category in distribution:
                distribution[category] += 1

        return distribution

    def __repr__(self) -> str:
        return (
            f"OrderCategorizer("
            f"lobby_table_threshold={self.lobby_table_threshold}, "
            f"drive_thru_time_max={self.drive_thru_time_kitchen_max})"
        )
