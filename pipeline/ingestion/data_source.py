"""
Protocol for data source abstraction.

Defines the interface for loading CSV data from various sources
(directory, ZIP, cloud storage, etc.).
"""

from pathlib import Path
from typing import Protocol, runtime_checkable
import pandas as pd
from pipeline.services.result import Result


@runtime_checkable
class DataSource(Protocol):
    """
    Protocol for data source implementations.

    Abstracts the source of CSV data, allowing for different
    implementations (local directory, ZIP file, S3, etc.)
    """

    def get_csv(self, filename: str) -> Result[pd.DataFrame]:
        """
        Load a specific CSV file.

        Args:
            filename: Name of the CSV file to load (e.g., 'TimeEntries.csv')

        Returns:
            Result[pd.DataFrame]: Loaded DataFrame on success, error on failure
        """
        ...

    def list_available(self) -> Result[list[str]]:
        """
        List all available CSV files in the data source.

        Returns:
            Result[list[str]]: List of available filenames on success
        """
        ...