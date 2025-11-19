"""
Order Categorization Stage - Categorizes orders by service type.

Converts raw DataFrames into categorized OrderDTOs for downstream processing.
"""

from typing import Dict, List, Optional
import pandas as pd
import time
from datetime import datetime

from src.core.result import Result
from src.core.errors import ProcessingError
from src.orchestration.pipeline.context import PipelineContext
from src.orchestration.pipeline.stage import PipelineStage
from src.processing.order_categorizer import OrderCategorizer
from src.models.order_dto import OrderDTO
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class OrderCategorizationStage(PipelineStage):
    """
    Pipeline stage for order categorization.

    Takes raw DataFrames from IngestionStage and produces:
    - List of categorized OrderDTOs
    - Service mix statistics (% Lobby, Drive-Thru, ToGo)
    - Categorization metadata

    Expected context inputs:
    - raw_dataframes: Dict[str, pd.DataFrame] with kitchen, eod, orders
    - restaurant: str (restaurant code)
    - date: str (business date)

    Context outputs:
    - categorized_orders: List[OrderDTO]
    - order_categories: Dict[str, str] (check_number -> category)
    - service_mix: Dict[str, float] (category percentages)
    - categorization_metadata: Dict (stats, quality metrics)
    """

    def __init__(self, categorizer: Optional[OrderCategorizer] = None):
        """
        Initialize order categorization stage.

        Args:
            categorizer: Optional OrderCategorizer instance (creates default if None)
        """
        self.categorizer = categorizer or OrderCategorizer()

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute order categorization stage.

        Args:
            context: Pipeline context with raw DataFrames

        Returns:
            Result[PipelineContext]: Updated context or error
        """
        start_time = time.time()

        # Extract required inputs
        restaurant = context.get('restaurant')
        date = context.get('date')
        raw_dataframes = context.get('raw_dataframes')

        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("order_categorization_started")

        # Validate inputs
        if raw_dataframes is None:
            return Result.fail(
                ProcessingError(
                    "Missing required context key: 'raw_dataframes'",
                    context={'restaurant': restaurant, 'date': date}
                )
            )

        # Check for required DataFrames
        required_dfs = ['kitchen', 'eod', 'orders']
        missing_dfs = [df for df in required_dfs if df not in raw_dataframes]

        if missing_dfs:
            return Result.fail(
                ProcessingError(
                    f"Missing required DataFrames: {', '.join(missing_dfs)}",
                    context={'missing': missing_dfs, 'available': list(raw_dataframes.keys())}
                )
            )

        kitchen_df = raw_dataframes['kitchen']
        eod_df = raw_dataframes['eod']
        order_details_df = raw_dataframes['orders']
        time_entries_df = raw_dataframes.get('labor')  # Optional

        # Run categorization
        categorization_result = self.categorizer.categorize_all_orders(
            kitchen_df,
            eod_df,
            order_details_df,
            time_entries_df
        )

        if categorization_result.is_err():
            return Result.fail(categorization_result.unwrap_err())

        order_categories = categorization_result.unwrap()

        # Convert to OrderDTOs
        orders_result = self._create_order_dtos(
            order_categories,
            kitchen_df,
            eod_df,
            order_details_df,
            date
        )

        if orders_result.is_err():
            return Result.fail(orders_result.unwrap_err())

        categorized_orders = orders_result.unwrap()

        # Calculate service mix
        service_mix = self._calculate_service_mix(order_categories)

        # Create metadata
        metadata = {
            'total_orders': len(order_categories),
            'categorized_orders': len(categorized_orders),
            'service_mix': service_mix,
            'kitchen_rows': len(kitchen_df),
            'eod_rows': len(eod_df),
            'order_details_rows': len(order_details_df),
            'has_time_entries': time_entries_df is not None
        }

        # Store results in context
        context.set('categorized_orders', categorized_orders)
        context.set('order_categories', order_categories)
        context.set('service_mix', service_mix)
        context.set('categorization_metadata', metadata)

        # Calculate duration and log success
        duration_ms = (time.time() - start_time) * 1000

        bound_logger.info("order_categorization_complete",
                          total_orders=len(order_categories),
                          lobby_pct=service_mix.get('Lobby', 0),
                          drive_thru_pct=service_mix.get('Drive-Thru', 0),
                          togo_pct=service_mix.get('ToGo', 0),
                          duration_ms=round(duration_ms, 0))

        return Result.ok(context)

    def _create_order_dtos(
        self,
        order_categories: Dict[str, str],
        kitchen_df: pd.DataFrame,
        eod_df: pd.DataFrame,
        order_details_df: pd.DataFrame,
        business_date: str
    ) -> Result[List[OrderDTO]]:
        """
        Convert categorized orders to OrderDTO objects.

        Args:
            order_categories: Mapping of check_number -> category
            kitchen_df: Kitchen Details DataFrame
            eod_df: EOD DataFrame
            order_details_df: OrderDetails DataFrame
            business_date: Business date string (YYYY-MM-DD)

        Returns:
            Result[List[OrderDTO]]: List of OrderDTOs or error
        """
        orders = []
        errors = []

        for check_number, category in order_categories.items():
            try:
                # Get order data from each source
                # Normalize check_number: if it's a float like 1.0, convert to "1"
                # This handles cases where Order # is float but Check # is int
                check_num_str = str(check_number)
                # If it's a string like "1.0", try to parse as float and convert to int
                if '.' in check_num_str:
                    try:
                        float_val = float(check_num_str)
                        if float_val.is_integer():
                            check_num_str = str(int(float_val))
                    except ValueError:
                        pass  # Keep original string if parsing fails

                # Kitchen data (always present for categorized orders)
                # Handle float check numbers (e.g., "4.0" should match "4")
                kitchen_check_col = kitchen_df['Check #']
                if kitchen_check_col.dtype in ['float64', 'float32']:
                    # Convert float to int then string to match "4" instead of "4.0"
                    kitchen_matches = kitchen_check_col.fillna(-1).astype(int).astype(str) == check_num_str
                else:
                    kitchen_matches = kitchen_check_col.astype(str) == check_num_str

                kitchen_rows = kitchen_df[kitchen_matches]
                if kitchen_rows.empty:
                    errors.append(f"{check_number}: No kitchen data found")
                    continue  # Skip if no kitchen data

                kitchen_row = kitchen_rows.iloc[0]

                # EOD data (optional)
                eod_check_col = eod_df['Check #']
                if eod_check_col.dtype in ['float64', 'float32']:
                    eod_matches = eod_check_col.fillna(-1).astype(int).astype(str) == check_num_str
                else:
                    eod_matches = eod_check_col.astype(str) == check_num_str
                eod_rows = eod_df[eod_matches]
                eod_row = eod_rows.iloc[0] if not eod_rows.empty else None

                # OrderDetails data (optional)
                order_check_col = order_details_df['Order #']
                if order_check_col.dtype in ['float64', 'float32']:
                    order_matches = order_check_col.fillna(-1).astype(int).astype(str) == check_num_str
                else:
                    order_matches = order_check_col.astype(str) == check_num_str
                order_rows = order_details_df[order_matches]
                order_row = order_rows.iloc[0] if not order_rows.empty else None

                # Extract fields for OrderDTO
                # Parse Kitchen Details "Fulfillment Time" (e.g., "5 minutes and 39 seconds")
                fulfillment_str = kitchen_row.get('Fulfillment Time', '')
                fulfillment_minutes = self.categorizer._parse_duration_string(str(fulfillment_str)) if fulfillment_str else 0.0

                # Get order duration from OrderDetails if available
                order_duration = None
                if order_row is not None:
                    duration_str = order_row.get('Duration (Opened to Paid)')
                    if duration_str:
                        order_duration = self._parse_duration_string(str(duration_str))

                # Get order time from OrderDetails 'Opened' field
                order_time = self._parse_order_time(order_row, business_date)

                # Get server name
                server = str(kitchen_row.get('Server', 'Unknown'))

                # Determine shift (morning = 6 AM - 2 PM, evening = 2 PM - 10 PM)
                shift = self._determine_shift(order_time)

                # Get table
                table = None
                if eod_row is not None:
                    table_val = eod_row.get('Table')
                    if table_val and self._safe_float(table_val) and self._safe_float(table_val) > 0:
                        table = str(int(self._safe_float(table_val)))

                # Get cash drawer
                cash_drawer = None
                if eod_row is not None:
                    cash_drawer = str(eod_row.get('Cash Drawer', '')) if pd.notna(eod_row.get('Cash Drawer')) else None

                # Get dining option
                dining_option = None
                if eod_row is not None:
                    dining_option = str(eod_row.get('Dining Option', '')) if pd.notna(eod_row.get('Dining Option')) else None

                # Create OrderDTO
                order_result = OrderDTO.create(
                    check_number=check_num_str,
                    category=category,
                    fulfillment_minutes=fulfillment_minutes,
                    order_duration_minutes=order_duration,
                    order_time=order_time,
                    server=server,
                    shift=shift,
                    table=table,
                    cash_drawer=cash_drawer,
                    dining_option=dining_option,
                    metadata={'kitchen_row': int(kitchen_rows.index[0])}
                )

                if order_result.is_ok():
                    orders.append(order_result.unwrap())
                else:
                    errors.append(f"{check_number}: {order_result.unwrap_err()}")

            except Exception as e:
                errors.append(f"{check_number}: {str(e)}")

        if errors:
            logger.warning("order_dto_conversion_errors",
                          error_count=len(errors),
                          sample_errors=errors[:5])

        if not orders:
            return Result.fail(
                ProcessingError(
                    "Failed to create any OrderDTOs",
                    context={'errors': errors[:10]}
                )
            )

        return Result.ok(orders)

    def _calculate_service_mix(self, order_categories: Dict[str, str]) -> Dict[str, float]:
        """
        Calculate service mix percentages.

        Args:
            order_categories: Mapping of check_number -> category

        Returns:
            dict: Percentages for each category
        """
        if not order_categories:
            return {'Lobby': 0.0, 'Drive-Thru': 0.0, 'ToGo': 0.0}

        counts = {'Lobby': 0, 'Drive-Thru': 0, 'ToGo': 0}

        for category in order_categories.values():
            if category in counts:
                counts[category] += 1

        total = len(order_categories)

        return {
            'Lobby': round((counts['Lobby'] / total * 100), 1),
            'Drive-Thru': round((counts['Drive-Thru'] / total * 100), 1),
            'ToGo': round((counts['ToGo'] / total * 100), 1)
        }

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or pd.isna(value):
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_duration_string(self, duration_str: str) -> float:
        """Parse duration string to minutes (simplified version from categorizer)."""
        try:
            return float(duration_str)
        except ValueError:
            pass

        # Try MM:SS format
        if ':' in duration_str:
            parts = duration_str.split(':')
            try:
                if len(parts) == 2:  # MM:SS
                    return float(parts[0]) + float(parts[1]) / 60
            except (ValueError, IndexError):
                pass

        return 0.0

    def _parse_order_time(self, order_row, business_date: str) -> datetime:
        """
        Parse order time from OrderDetails 'Opened' field.

        If not available, defaults to business date at noon.
        """
        if order_row is not None:
            opened = order_row.get('Opened')
            if opened and not pd.isna(opened):
                try:
                    # Try to parse as datetime
                    if isinstance(opened, datetime):
                        return opened
                    elif isinstance(opened, str):
                        # Common Toast formats
                        for fmt in ['%m/%d/%y %I:%M %p', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                            try:
                                return datetime.strptime(opened, fmt)
                            except ValueError:
                                continue
                except Exception:
                    pass

        # Default to business date at noon
        try:
            return datetime.strptime(f"{business_date} 12:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.now()

    def _determine_shift(self, order_time: datetime) -> str:
        """
        Determine shift based on order time.

        Morning: 6 AM - 2 PM
        Evening: 2 PM - 10 PM
        """
        hour = order_time.hour

        if 6 <= hour < 14:
            return "morning"
        else:
            return "evening"

    def __repr__(self) -> str:
        return f"OrderCategorizationStage(categorizer={self.categorizer})"
