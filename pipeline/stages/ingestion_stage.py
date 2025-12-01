"""
Ingestion stage for the processing pipeline.

Loads and validates Toast POS CSV data, producing an IngestionResult DTO
for downstream processing stages.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import time

from pipeline.services.result import Result
from pipeline.services.errors import IngestionError
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.ingestion.data_source import DataSource
from pipeline.ingestion.csv_data_source import CSVDataSource
from pipeline.ingestion.data_validator import DataValidator
from pipeline.ingestion.time_entries_loader import TimeEntriesLoader
from pipeline.ingestion.void_extractor import VoidExtractor
from pipeline.services.cash_flow_extractor import CashFlowExtractor
from pipeline.models.ingestion_result import IngestionResult
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


class IngestionStage:
    """
    Pipeline stage for ingesting Toast POS data.

    Loads CSV files, validates data quality, and produces an IngestionResult
    DTO with quality metrics.
    """

    # Priority 1: Required CSV files (core operations)
    # Note: Toast exports use different naming patterns
    REQUIRED_FILES = {
        'labor': 'TimeEntries.csv',  # Or TimeEntries_YYYY_MM_DD.csv
        'sales': 'Net sales summary.csv',  # Note: space in filename, not underscore
        'orders': 'OrderDetails.csv',  # Or OrderDetails_YYYY_MM_DD.csv
    }

    # Priority 2: Optional CSV files (efficiency & management)
    # Enable higher quality levels when present
    OPTIONAL_FILES = {
        'cash_activity': 'Cash activity.csv',
        'kitchen': 'Kitchen Details.csv',  # Or Kitchen Details_YYYY_MM_DD.csv
        'payroll': 'PayrollExport.csv',  # Or PayrollExport_YYYY_MM_DD.csv
        'eod': 'EOD.csv',  # Or EOD_YYYY_MM_DD.csv - End of Day report
    }

    def __init__(self, validator: DataValidator):
        """
        Initialize ingestion stage.

        Args:
            validator: DataValidator for L1/L2 validation
        """
        self.validator = validator

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute ingestion stage.

        Expected context inputs:
        - date: str (YYYY-MM-DD format)
        - restaurant: str (restaurant code, e.g., 'SDR')
        - data_path: str (path to directory containing CSV files)

        Context outputs:
        - ingestion_result: IngestionResult DTO
        - sales: float (net sales amount)
        - raw_dataframes: dict[str, pd.DataFrame] (for downstream stages)

        Args:
            context: Pipeline context with required inputs

        Returns:
            Result[PipelineContext]: Updated context or error
        """
        start_time = time.time()

        # Extract required inputs
        date = context.get('date')
        restaurant = context.get('restaurant')
        data_path = context.get('data_path')

        # Bind context for all logs in this execution
        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("ingestion_started", data_path=data_path)

        # Validate inputs
        if date is None:
            bound_logger.error("ingestion_failed", reason="missing_date")
            return Result.fail(
                IngestionError("Missing required context key: 'date'")
            )

        if restaurant is None:
            bound_logger.error("ingestion_failed", reason="missing_restaurant")
            return Result.fail(
                IngestionError("Missing required context key: 'restaurant'")
            )

        if data_path is None:
            bound_logger.error("ingestion_failed", reason="missing_data_path")
            return Result.fail(
                IngestionError("Missing required context key: 'data_path'")
            )

        # Initialize data source
        source = CSVDataSource(Path(data_path))

        # Load required CSV files (with flexible date-suffixed naming)
        dfs_result = self._load_csvs(source, date)
        if dfs_result.is_err():
            return Result.fail(dfs_result.unwrap_err())

        dfs = dfs_result.unwrap()

        # Run L1 validation (fatal)
        validation_result = self.validator.validate_l1(dfs)
        if validation_result.is_err():
            return Result.fail(validation_result.unwrap_err())

        # Calculate L2 quality metrics
        quality_metrics = self.validator.calculate_l2_metrics(dfs)

        # Extract sales amount
        sales_result = self._extract_sales(dfs['sales'])
        if sales_result.is_err():
            return Result.fail(sales_result.unwrap_err())

        sales_amount = sales_result.unwrap()

        # Extract payroll data if present (optional)
        payroll_summary = self._extract_payroll_summary(dfs)

        # Load TimeEntries for shift analysis (optional)
        time_entries_result = TimeEntriesLoader.load_from_directory(
            Path(data_path),
            restaurant,
            date
        )

        time_entries = []
        if time_entries_result.is_ok():
            time_entries = time_entries_result.unwrap()
            bound_logger.info("time_entries_loaded", count=len(time_entries))
        else:
            # TimeEntries not found is okay - log warning and continue
            bound_logger.warning("time_entries_not_found",
                               reason=str(time_entries_result.unwrap_err()))

        # Save DataFrames to temp files (following V4 pattern of path references)
        temp_paths_result = self._save_temp_files(dfs, restaurant, date)
        if temp_paths_result.is_err():
            return Result.fail(temp_paths_result.unwrap_err())

        temp_paths = temp_paths_result.unwrap()

        # Determine quality level based on available files
        quality_level = self._determine_quality_level(dfs)

        # Create IngestionResult DTO
        ingestion_result = IngestionResult.create(
            restaurant_code=restaurant,
            business_date=date,
            quality_level=quality_level,
            toast_data_path=temp_paths.get('sales', ''),
            employee_data_path=temp_paths.get('labor'),
            metadata=quality_metrics  # Include L2 metrics in metadata
        )

        if ingestion_result.is_err():
            return Result.fail(ingestion_result.unwrap_err())

        # Store results in context
        context.set('ingestion_result', ingestion_result.unwrap())
        context.set('sales', sales_amount)
        context.set('raw_dataframes', dfs)

        # Store payroll summary if present
        if payroll_summary is not None:
            context.set('total_payroll_cost', payroll_summary)

        # Store time entries if loaded
        if len(time_entries) > 0:
            context.set('time_entries', time_entries)

        # Extract void transactions (optional)
        void_result = VoidExtractor.extract_from_directory(
            Path(data_path),
            date
        )

        if void_result.is_ok():
            void_metrics = void_result.unwrap()
            context.set('void_metrics', void_metrics)
            bound_logger.info("voids_extracted",
                            morning=void_metrics.morning_void_count,
                            evening=void_metrics.evening_void_count,
                            total=void_metrics.total_void_count,
                            total_amount=round(void_metrics.total_void_amount, 2))
        else:
            # Voids not found is okay - log warning and continue
            bound_logger.warning("voids_not_extracted",
                               reason=str(void_result.unwrap_err()))

        # Extract cash flow data (optional) - same extractor as static file system
        cash_flow_extractor = CashFlowExtractor()
        cash_result = cash_flow_extractor.extract_from_csvs(
            Path(data_path),
            date,
            restaurant
        )

        if cash_result.is_ok():
            cash_flow = cash_result.unwrap()
            context.set('cash_flow', cash_flow)  # DailyCashFlow DTO
            bound_logger.info("cash_flow_extracted",
                            total_cash=round(cash_flow.total_cash, 2),
                            total_tips=round(cash_flow.total_tips, 2),
                            total_vendor_payouts=round(cash_flow.total_vendor_payouts, 2),
                            net_cash=round(cash_flow.net_cash, 2))
        else:
            # Cash not found is okay - log warning and continue
            bound_logger.warning("cash_flow_not_extracted",
                               reason=str(cash_result.unwrap_err()))

        # Calculate duration and log success
        duration_ms = (time.time() - start_time) * 1000
        files_loaded = len(dfs)

        bound_logger.info("ingestion_complete",
                          sales=round(sales_amount, 2),
                          files=files_loaded,
                          quality_level=quality_level,
                          duration_ms=round(duration_ms, 0))

        return Result.ok(context)

    def _find_file(self, source: DataSource, base_name: str, date: str) -> Result[str]:
        """
        Find a CSV file with flexible naming (with or without date suffix).

        Toast exports can use different naming patterns:
        - TimeEntries.csv
        - TimeEntries_2025_10_20.csv

        Args:
            source: Data source to search
            base_name: Base filename (e.g., 'TimeEntries.csv')
            date: Date string (YYYY-MM-DD format)

        Returns:
            Result[str]: Found filename or error
        """
        # Try exact match first
        result = source.get_csv(base_name)
        if result.is_ok():
            return Result.ok(base_name)

        # Try with date suffix (YYYY_MM_DD format)
        date_formatted = date.replace('-', '_')
        base_without_ext = base_name.replace('.csv', '')
        date_suffixed = f"{base_without_ext}_{date_formatted}.csv"

        result = source.get_csv(date_suffixed)
        if result.is_ok():
            return Result.ok(date_suffixed)

        # Neither pattern found
        return Result.fail(
            IngestionError(
                f"Could not find file: tried '{base_name}' and '{date_suffixed}'",
                context={'base_name': base_name, 'date': date}
            )
        )

    def _load_csvs(self, source: DataSource, date: str) -> Result[Dict[str, pd.DataFrame]]:
        """
        Load all required CSV files with flexible naming, plus optional files.

        Implements graceful degradation:
        - Required files (Priority 1): Failure aborts pipeline
        - Optional files (Priority 2): Failure logged but pipeline continues

        Args:
            source: Data source to load from
            date: Business date (YYYY-MM-DD) for finding date-suffixed files

        Returns:
            Result[Dict[str, pd.DataFrame]]: Loaded DataFrames or error
        """
        dfs = {}

        # Load required files (Priority 1) - must succeed
        for data_type, base_filename in self.REQUIRED_FILES.items():
            # Find the actual filename (handles date suffixes)
            filename_result = self._find_file(source, base_filename, date)

            if filename_result.is_err():
                return Result.fail(
                    IngestionError(
                        f"Failed to find required file for {data_type}",
                        context={'data_type': data_type, 'error': str(filename_result.unwrap_err())}
                    )
                )

            actual_filename = filename_result.unwrap()

            # Load the file
            result = source.get_csv(actual_filename)

            if result.is_err():
                return Result.fail(
                    IngestionError(
                        f"Failed to load required file: {actual_filename}",
                        context={'data_type': data_type, 'error': str(result.unwrap_err())}
                    )
                )

            dfs[data_type] = result.unwrap()

        # Load optional files (Priority 2) - graceful degradation
        for data_type, base_filename in self.OPTIONAL_FILES.items():
            filename_result = self._find_file(source, base_filename, date)

            if filename_result.is_err():
                # Optional file not found - skip silently
                continue

            actual_filename = filename_result.unwrap()
            result = source.get_csv(actual_filename)

            if result.is_ok():
                dfs[data_type] = result.unwrap()
            # If loading fails, skip silently (graceful degradation)

        return Result.ok(dfs)

    def _extract_sales(self, sales_df: pd.DataFrame) -> Result[float]:
        """
        Extract net sales amount from sales DataFrame.

        Args:
            sales_df: Sales summary DataFrame

        Returns:
            Result[float]: Net sales amount or error
        """
        if 'Net sales' not in sales_df.columns:
            return Result.fail(
                IngestionError(
                    "Missing 'Net sales' column in sales data",
                    context={'columns': list(sales_df.columns)}
                )
            )

        if sales_df.empty:
            return Result.fail(
                IngestionError("Sales data is empty")
            )

        try:
            net_sales = float(sales_df['Net sales'].iloc[0])
            return Result.ok(net_sales)
        except (ValueError, TypeError) as e:
            return Result.fail(
                IngestionError(
                    f"Failed to parse net sales amount: {str(e)}",
                    context={'value': sales_df['Net sales'].iloc[0]}
                )
            )

    def _extract_payroll_summary(self, dfs: Dict[str, pd.DataFrame]) -> Optional[float]:
        """
        Extract payroll summary from PayrollExport DataFrame (optional).

        Calculates total payroll cost from 'Total Pay' column.
        Gracefully handles missing or invalid payroll data.

        Args:
            dfs: Dictionary of loaded DataFrames

        Returns:
            float | None: Total payroll cost or None if not available
        """
        # Check if payroll data is present
        if 'payroll' not in dfs:
            return None

        payroll_df = dfs['payroll']

        # Check if DataFrame is empty
        if payroll_df.empty:
            return None

        # Check if required column exists
        if 'Total Pay' not in payroll_df.columns:
            # Log warning but don't fail - graceful degradation
            return None

        try:
            # Sum all Total Pay values, handling NaN gracefully
            total_payroll = payroll_df['Total Pay'].fillna(0).sum()
            return float(total_payroll)
        except (ValueError, TypeError):
            # Failed to parse payroll data - return None (graceful degradation)
            return None

    def _extract_overtime_from_payroll(self, dfs: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        Extract overtime data from PayrollExport DataFrame (optional).

        Extracts overtime hours and costs from 'Overtime Hours' and 'Overtime Pay' columns.
        Following V3's approach of reading daily overtime from PayrollExport.

        Args:
            dfs: Dictionary of loaded DataFrames

        Returns:
            Dict with keys: total_overtime_hours, total_overtime_cost
        """
        result = {
            'total_overtime_hours': 0.0,
            'total_overtime_cost': 0.0
        }

        # Check if payroll data is present
        if 'payroll' not in dfs:
            return result

        payroll_df = dfs['payroll']

        # Check if DataFrame is empty
        if payroll_df.empty:
            return result

        # Extract overtime hours
        if 'Overtime Hours' in payroll_df.columns:
            try:
                overtime_hours = payroll_df['Overtime Hours'].fillna(0).sum()
                result['total_overtime_hours'] = float(overtime_hours)
            except (ValueError, TypeError):
                # Failed to parse - leave as 0.0
                pass

        # Extract overtime pay
        if 'Overtime Pay' in payroll_df.columns:
            try:
                # Handle currency format: remove $, commas
                overtime_pay_series = payroll_df['Overtime Pay'].fillna(0)
                if overtime_pay_series.dtype == object:
                    # String format - clean it
                    overtime_pay_series = overtime_pay_series.astype(str).str.replace('$', '').str.replace(',', '')
                overtime_pay = pd.to_numeric(overtime_pay_series, errors='coerce').fillna(0).sum()
                result['total_overtime_cost'] = float(overtime_pay)
            except (ValueError, TypeError):
                # Failed to parse - leave as 0.0
                pass

        return result

    def _save_temp_files(
        self,
        dfs: Dict[str, pd.DataFrame],
        restaurant: str,
        date: str
    ) -> Result[Dict[str, str]]:
        """
        Save DataFrames to temporary parquet files.

        Following V4 pattern of storing path references in DTOs
        instead of embedding data.

        Args:
            dfs: DataFrames to save
            restaurant: Restaurant code
            date: Business date

        Returns:
            Result[Dict[str, str]]: Mapping of data type to file path
        """
        # Use Windows-compatible temp path
        temp_dir = Path(f"C:/temp/omni/{restaurant}/{date}")

        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return Result.fail(
                IngestionError(
                    f"Failed to create temp directory: {str(e)}",
                    context={'path': str(temp_dir)}
                )
            )

        temp_paths = {}

        for data_type, df in dfs.items():
            file_path = temp_dir / f"{data_type}.parquet"

            try:
                df.to_parquet(file_path)
                temp_paths[data_type] = str(file_path)
            except Exception as e:
                return Result.fail(
                    IngestionError(
                        f"Failed to save {data_type} data: {str(e)}",
                        context={'path': str(file_path)}
                    )
                )

        return Result.ok(temp_paths)

    def _determine_quality_level(self, dfs: Dict[str, pd.DataFrame]) -> int:
        """
        Determine quality level based on available files.

        Note: For now, always returns 1 since quality levels 2+ require
        timeslots_path which is generated downstream. Optional files are
        tracked in metadata instead.

        Args:
            dfs: Dictionary of loaded DataFrames

        Returns:
            int: Quality level (always 1 for ingestion stage)
        """
        # Always return 1 for ingestion stage
        # Quality levels 2+ require timeslots_path which is generated
        # in downstream processing stages
        # Optional files loaded are tracked in L2 metrics instead
        return 1

    def __repr__(self) -> str:
        return f"IngestionStage(validator={self.validator})"