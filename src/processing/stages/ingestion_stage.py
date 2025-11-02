"""
Ingestion stage for the processing pipeline.

Loads and validates Toast POS CSV data, producing an IngestionResult DTO
for downstream processing stages.
"""

from pathlib import Path
from typing import Dict
import pandas as pd

from src.core.result import Result
from src.core.errors import IngestionError
from src.orchestration.pipeline.context import PipelineContext
from src.ingestion.data_source import DataSource
from src.ingestion.csv_data_source import CSVDataSource
from src.ingestion.data_validator import DataValidator
from src.models.ingestion_result import IngestionResult


class IngestionStage:
    """
    Pipeline stage for ingesting Toast POS data.

    Loads CSV files, validates data quality, and produces an IngestionResult
    DTO with quality metrics.
    """

    # Required CSV files mapping
    # Note: Toast exports use different naming patterns
    REQUIRED_FILES = {
        'labor': 'TimeEntries.csv',  # Or TimeEntries_YYYY_MM_DD.csv
        'sales': 'Net sales summary.csv',  # Note: space in filename, not underscore
        'orders': 'OrderDetails.csv',  # Or OrderDetails_YYYY_MM_DD.csv
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
        # Extract required inputs
        date = context.get('date')
        restaurant = context.get('restaurant')
        data_path = context.get('data_path')

        # Validate inputs
        if date is None:
            return Result.fail(
                IngestionError("Missing required context key: 'date'")
            )

        if restaurant is None:
            return Result.fail(
                IngestionError("Missing required context key: 'restaurant'")
            )

        if data_path is None:
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

        # Save DataFrames to temp files (following V4 pattern of path references)
        temp_paths_result = self._save_temp_files(dfs, restaurant, date)
        if temp_paths_result.is_err():
            return Result.fail(temp_paths_result.unwrap_err())

        temp_paths = temp_paths_result.unwrap()

        # Create IngestionResult DTO
        #  Note: Using quality_level=1 for basic ingestion
        # L2+ requires timeslots_path which is generated downstream
        ingestion_result = IngestionResult.create(
            restaurant_code=restaurant,
            business_date=date,
            quality_level=1,  # Basic ingestion (L1 validation passed)
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
        Load all required CSV files with flexible naming.

        Args:
            source: Data source to load from
            date: Business date (YYYY-MM-DD) for finding date-suffixed files

        Returns:
            Result[Dict[str, pd.DataFrame]]: Loaded DataFrames or error
        """
        dfs = {}

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

    def __repr__(self) -> str:
        return f"IngestionStage(validator={self.validator})"