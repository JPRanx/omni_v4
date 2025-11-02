"""
Data validation for Toast POS CSV files - Enhanced version.

Implements two-level validation with graceful degradation:
- L1 (Fatal): Schema validation, required columns
- L2 (Metrics): Quality tracking, parse rates, completeness
- Supports both required and optional files
"""

from typing import Dict, List, Set
import pandas as pd

from src.core.result import Result
from src.core.errors import ValidationError


class DataValidator:
    """
    Validates Toast POS CSV data quality with graceful degradation.

    Performs structural validation (L1) and quality metrics calculation (L2).
    Supports both required files (Priority 1) and optional files (Priority 2).
    """

    # Priority 1: Core operations (required for basic pipeline)
    REQUIRED_COLUMNS = {
        'labor': {
            'Employee', 'Job Title', 'In Date', 'Out Date',
            'Total Hours', 'Payable Hours'
        },
        'sales': {
            'Gross sales', 'Sales discounts', 'Sales refunds', 'Net sales'
        },
        'orders': {
            'Order #', 'Opened', 'Server', 'Amount'
        }
    }

    # Priority 2: Efficiency & management (optional, enables L2+ quality)
    OPTIONAL_COLUMNS = {
        'cash_activity': {
            'Total cash payments', 'Cash adjustments', 'Cash refunds',
            'Cash before tipouts', 'Total cash'
        },
        'kitchen': {
            'Location', 'Server', 'Check #', 'Fired Date',
            'Fulfilled Date', 'Fulfillment Time'
        }
    }

    def validate_l1(self, dfs: Dict[str, pd.DataFrame]) -> Result[None]:
        """
        L1 (Fatal) validation - schema and required columns.

        Checks:
        - All required DataFrames present (labor, sales, orders)
        - Required columns exist in each DataFrame
        - DataFrames are not empty
        - Optional files validated if present

        Args:
            dfs: Dictionary mapping data type to DataFrame
                 Required keys: 'labor', 'sales', 'orders'
                 Optional keys: 'cash_activity', 'kitchen'

        Returns:
            Result[None]: Success or ValidationError
        """
        # Check all required data types present
        required_keys = {'labor', 'sales', 'orders'}
        missing_keys = required_keys - set(dfs.keys())

        if missing_keys:
            return Result.fail(
                ValidationError(
                    f"Missing required data types: {', '.join(sorted(missing_keys))}",
                    context={'missing': list(missing_keys), 'provided': list(dfs.keys())}
                )
            )

        # Validate required DataFrames
        for data_type, df in dfs.items():
            # Skip if not in any columns map
            if data_type not in self.REQUIRED_COLUMNS and data_type not in self.OPTIONAL_COLUMNS:
                continue

            # Check DataFrame not empty
            if df.empty:
                # Empty optional files are warnings, not errors
                if data_type in self.OPTIONAL_COLUMNS:
                    continue

                return Result.fail(
                    ValidationError(
                        f"DataFrame is empty: {data_type}",
                        context={'data_type': data_type}
                    )
                )

            # Check required columns present
            column_map = (
                self.REQUIRED_COLUMNS if data_type in self.REQUIRED_COLUMNS
                else self.OPTIONAL_COLUMNS
            )
            required_cols = column_map[data_type]
            df_cols = set(df.columns)
            missing_cols = required_cols - df_cols

            if missing_cols:
                # Missing columns in optional files are warnings, not errors
                if data_type in self.OPTIONAL_COLUMNS:
                    continue

                return Result.fail(
                    ValidationError(
                        f"Missing required columns in {data_type}: {', '.join(sorted(missing_cols))}",
                        context={
                            'data_type': data_type,
                            'missing_columns': list(missing_cols),
                            'available_columns': list(df_cols)
                        }
                    )
                )

        return Result.ok(None)

    def calculate_l2_metrics(self, dfs: Dict[str, pd.DataFrame]) -> Dict:
        """
        L2 quality metrics - parsing and completeness tracking.

        Calculates:
        - Files successfully loaded
        - Validation level reached
        - Parse errors and warnings
        - Timestamp parsing quality
        - Data completeness rates

        Args:
            dfs: Dictionary mapping data type to DataFrame

        Returns:
            dict: Quality metrics for inclusion in IngestionResult
        """
        metrics = {
            'files_loaded': list(dfs.keys()),
            'validation_level': 'L2',
            'parse_errors': {},
            'warnings': [],
            'row_counts': {},
            'completeness': {},
            'optional_files_present': []
        }

        # Track which optional files are present
        for optional_type in self.OPTIONAL_COLUMNS.keys():
            if optional_type in dfs:
                metrics['optional_files_present'].append(optional_type)

        # Calculate row counts
        for data_type, df in dfs.items():
            metrics['row_counts'][data_type] = len(df)

        # Calculate timestamp quality for labor data
        if 'labor' in dfs:
            timestamp_quality = self._calculate_timestamp_quality(dfs['labor'])
            metrics['timestamp_quality'] = timestamp_quality

        # Calculate data completeness (non-null rates)
        all_columns = {**self.REQUIRED_COLUMNS, **self.OPTIONAL_COLUMNS}
        for data_type, df in dfs.items():
            if data_type in all_columns:
                required_cols = all_columns[data_type]
                completeness = {}

                for col in required_cols:
                    if col in df.columns:
                        non_null_count = df[col].notna().sum()
                        total_count = len(df)
                        completeness[col] = (
                            non_null_count / total_count if total_count > 0 else 0.0
                        )

                metrics['completeness'][data_type] = completeness

        # Calculate overall completeness rate
        all_rates = [
            rate
            for type_completeness in metrics['completeness'].values()
            for rate in type_completeness.values()
        ]
        metrics['overall_completeness'] = (
            sum(all_rates) / len(all_rates) if all_rates else 0.0
        )

        # Add warnings for low completeness
        for data_type, completeness in metrics['completeness'].items():
            for col, rate in completeness.items():
                if rate < 0.9:  # Less than 90% complete
                    metrics['warnings'].append(
                        f"{data_type}.{col} has low completeness: {rate:.1%}"
                    )

        return metrics

    def _calculate_timestamp_quality(self, labor_df: pd.DataFrame) -> float:
        """
        Calculate timestamp parsing quality for labor data.

        Args:
            labor_df: Labor DataFrame with 'In Date' and 'Out Date' columns

        Returns:
            float: Proportion of successfully parsed timestamps (0.0-1.0)
        """
        if labor_df.empty:
            return 0.0

        total_timestamps = 0
        successful_parses = 0

        # Check 'In Date' column
        if 'In Date' in labor_df.columns:
            total_timestamps += len(labor_df)
            # Count non-null, non-empty values
            successful_parses += labor_df['In Date'].notna().sum()

        # Check 'Out Date' column
        if 'Out Date' in labor_df.columns:
            total_timestamps += len(labor_df)
            successful_parses += labor_df['Out Date'].notna().sum()

        if total_timestamps == 0:
            return 0.0

        return successful_parses / total_timestamps

    def __repr__(self) -> str:
        return "DataValidator(levels=['L1', 'L2'], optional_files=True)"
