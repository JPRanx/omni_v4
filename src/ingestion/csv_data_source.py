"""
CSV directory data source implementation.

Loads CSV files from a local directory with encoding detection
and error handling.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import chardet

from src.core.result import Result
from src.core.errors import IngestionError


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

        # Detect encoding
        encoding_result = self._detect_encoding(file_path)
        if encoding_result.is_err():
            return Result.fail(encoding_result.unwrap_err())

        encoding = encoding_result.unwrap()

        # Load CSV with detected encoding
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return Result.ok(df)
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

    def _detect_encoding(self, file_path: Path) -> Result[str]:
        """
        Detect the encoding of a CSV file.

        Uses chardet library with fallback to common encodings.

        Args:
            file_path: Path to the CSV file

        Returns:
            Result[str]: Detected encoding on success
        """
        try:
            # Read first 10KB for detection
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)

            # Use chardet for detection
            detection = chardet.detect(raw_data)
            encoding = detection.get('encoding')

            # Fallback chain if detection failed or confidence low
            if not encoding or detection.get('confidence', 0) < 0.7:
                # Try common encodings in order
                for fallback in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        raw_data.decode(fallback)
                        return Result.ok(fallback)
                    except UnicodeDecodeError:
                        continue

                # If all fallbacks failed, use latin-1 (accepts all bytes)
                return Result.ok('latin-1')

            return Result.ok(encoding)

        except Exception as e:
            return Result.fail(
                IngestionError(
                    f"Failed to detect encoding for {file_path.name}",
                    context={'path': str(file_path), 'error': str(e)}
                )
            )

    def __repr__(self) -> str:
        return f"CSVDataSource(base_path='{self.base_path}')"