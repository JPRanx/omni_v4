"""
CSV directory data source implementation.

Loads CSV files from a local directory with encoding detection
and error handling.
"""

from pathlib import Path
from typing import Optional
import pandas as pd

from pipeline.services.result import Result
from pipeline.services.errors import IngestionError


class CSVDataSource:
    """
    Load CSV files from a local directory.

    Handles encoding detection and provides graceful error handling
    for missing or malformed files.
    """

    def __init__(self, base_path: Path):
        """
        Initialize CSV data source.

        Args:
            base_path: Directory containing CSV files
        """
        self.base_path = Path(base_path)

    def get_csv(self, filename: str) -> Result[pd.DataFrame]:
        """
        Load a specific CSV file from the directory.

        Args:
            filename: Name of the CSV file (e.g., 'TimeEntries.csv')

        Returns:
            Result[pd.DataFrame]: Loaded DataFrame on success, error on failure
        """
        file_path = self.base_path / filename

        # Check if file exists
        if not file_path.exists():
            return Result.fail(
                IngestionError(
                    f"CSV file not found: {filename}",
                    context={'path': str(file_path)}
                )
            )

        # Try loading with UTF-8 first, then fallback encodings
        # This is more reliable than chardet for Toast POS CSV files
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1']
        last_error = None

        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                return Result.ok(df)
            except UnicodeDecodeError as e:
                # Try next encoding
                last_error = e
                continue
            except pd.errors.EmptyDataError:
                return Result.fail(
                    IngestionError(
                        f"CSV file is empty: {filename}",
                        context={'path': str(file_path)}
                    )
                )
            except pd.errors.ParserError as e:
                return Result.fail(
                    IngestionError(
                        f"Failed to parse CSV: {filename}",
                        context={'path': str(file_path), 'error': str(e)}
                    )
                )
            except Exception as e:
                return Result.fail(
                    IngestionError(
                        f"Unexpected error loading CSV: {filename}",
                        context={'path': str(file_path), 'error': str(e)}
                    )
                )

        # If all encodings failed, return the last error
        return Result.fail(
            IngestionError(
                f"Failed to load CSV with any encoding: {filename}",
                context={'path': str(file_path), 'error': str(last_error)}
            )
        )

    def list_available(self) -> Result[list[str]]:
        """
        List all CSV files in the directory.

        Returns:
            Result[list[str]]: List of CSV filenames on success
        """
        if not self.base_path.exists():
            return Result.fail(
                IngestionError(
                    f"Data directory not found: {self.base_path}",
                    context={'path': str(self.base_path)}
                )
            )

        if not self.base_path.is_dir():
            return Result.fail(
                IngestionError(
                    f"Path is not a directory: {self.base_path}",
                    context={'path': str(self.base_path)}
                )
            )

        try:
            csv_files = [f.name for f in self.base_path.glob('*.csv')]
            return Result.ok(sorted(csv_files))
        except Exception as e:
            return Result.fail(
                IngestionError(
                    f"Failed to list CSV files in directory",
                    context={'path': str(self.base_path), 'error': str(e)}
                )
            )


    def __repr__(self) -> str:
        return f"CSVDataSource(base_path='{self.base_path}')"