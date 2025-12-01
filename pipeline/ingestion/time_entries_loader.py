"""
TimeEntriesLoader - Load and parse TimeEntries CSV files.

Handles employee clock-in/out data with date-based filenames.
"""

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pipeline.models.time_entry_dto import TimeEntryDTO
from pipeline.services.result import Result


class TimeEntriesLoader:
    """Loads and parses TimeEntries CSV files."""

    @staticmethod
    def detect_time_entries_file(directory: Path, business_date: str) -> Optional[Path]:
        """
        Detect TimeEntries file with date in filename.

        Supports formats:
        - TimeEntries_YYYY_MM_DD.csv
        - TimeEntries_YYYYMMDD.csv
        - TimeEntries.csv (fallback)

        Args:
            directory: Directory to search
            business_date: Business date in YYYY-MM-DD format

        Returns:
            Path to TimeEntries file or None if not found
        """
        # Convert business_date to different formats
        date_obj = datetime.fromisoformat(business_date).date()
        formats = [
            f"TimeEntries_{date_obj.strftime('%Y_%m_%d')}.csv",  # 2025_08_20
            f"TimeEntries_{date_obj.strftime('%Y%m%d')}.csv",    # 20250820
            "TimeEntries.csv"  # Fallback
        ]

        for filename in formats:
            file_path = directory / filename
            if file_path.exists():
                return file_path

        return None

    @staticmethod
    def parse_datetime(date_str: str) -> Optional[datetime]:
        """
        Parse Toast POS datetime format.

        Supports:
        - M/D/YY H:MM AM/PM (e.g., "8/20/25 5:14 AM")
        - M/D/YYYY H:MM AM/PM (e.g., "8/20/2025 5:14 AM")

        Args:
            date_str: Datetime string from CSV

        Returns:
            Parsed datetime or None if empty/invalid
        """
        if not date_str or date_str.strip() == "":
            return None

        date_str = date_str.strip()

        # Try different formats
        formats = [
            "%m/%d/%y %I:%M %p",   # 8/20/25 5:14 AM
            "%m/%d/%Y %I:%M %p",   # 8/20/2025 5:14 AM
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If all formats fail, return None
        return None

    @classmethod
    def load(
        cls,
        file_path: Path,
        restaurant_code: str,
        business_date: str
    ) -> Result[List[TimeEntryDTO]]:
        """
        Load TimeEntries CSV file.

        Args:
            file_path: Path to TimeEntries CSV
            restaurant_code: Restaurant identifier (SDR, T12, TK9)
            business_date: Business date in YYYY-MM-DD format

        Returns:
            Result containing list of TimeEntryDTO objects or error
        """
        try:
            if not file_path.exists():
                return Result.fail(FileNotFoundError(f"TimeEntries file not found: {file_path}"))

            time_entries = []

            # Try UTF-8 first, fall back to latin-1 for special characters
            encoding = 'utf-8-sig'
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)  # Read all rows to test encoding
            except UnicodeDecodeError:
                # Fall back to latin-1 encoding
                encoding = 'latin-1'
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

            # Process rows
            for row_num, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
                try:
                    # Parse required fields
                    employee_name = row.get('Employee', '').strip()
                    job_title = row.get('Job Title', '').strip()
                    in_date_str = row.get('In Date', '').strip()

                    if not employee_name or not job_title or not in_date_str:
                        # Skip rows with missing critical fields
                        continue

                    # Parse datetimes
                    clock_in_dt = cls.parse_datetime(in_date_str)
                    if clock_in_dt is None:
                        print(f"[WARNING] Could not parse clock-in time on row {row_num}: {in_date_str}")
                        continue

                    out_date_str = row.get('Out Date', '').strip()
                    clock_out_dt = cls.parse_datetime(out_date_str)

                    # Parse boolean
                    auto_clockout_str = row.get('Auto Clock-out', '').strip()
                    auto_clockout = auto_clockout_str.lower() in ['yes', 'true', '1']

                    # Parse floats
                    try:
                        total_hours = float(row.get('Total Hours', '0').strip() or '0')
                        unpaid_break = float(row.get('Unpaid Break Time', '0').strip() or '0')
                        paid_break = float(row.get('Paid Break Time', '0').strip() or '0')
                        payable_hours = float(row.get('Payable Hours', '0').strip() or '0')
                    except ValueError as e:
                        print(f"[WARNING] Could not parse hours on row {row_num}: {e}")
                        continue

                    # Create DTO
                    entry = TimeEntryDTO(
                        employee_name=employee_name,
                        job_title=job_title,
                        clock_in_datetime=clock_in_dt,
                        clock_out_datetime=clock_out_dt,
                        auto_clockout=auto_clockout,
                        total_hours=total_hours,
                        unpaid_break_time=unpaid_break,
                        paid_break_time=paid_break,
                        payable_hours=payable_hours,
                        restaurant_code=restaurant_code,
                        business_date=business_date
                    )

                    time_entries.append(entry)

                except Exception as e:
                    print(f"[WARNING] Error parsing TimeEntries row {row_num}: {e}")
                    continue

            return Result.ok(time_entries)

        except Exception as e:
            return Result.fail(ValueError(f"Failed to load TimeEntries: {str(e)}"))

    @classmethod
    def load_from_directory(
        cls,
        directory: Path,
        restaurant_code: str,
        business_date: str
    ) -> Result[List[TimeEntryDTO]]:
        """
        Auto-detect and load TimeEntries file from directory.

        Args:
            directory: Directory containing TimeEntries CSV
            restaurant_code: Restaurant identifier
            business_date: Business date in YYYY-MM-DD format

        Returns:
            Result containing list of TimeEntryDTO objects or empty list if not found
        """
        file_path = cls.detect_time_entries_file(directory, business_date)

        if file_path is None:
            # Not finding TimeEntries is not a fatal error, return empty list
            return Result.ok([])

        return cls.load(file_path, restaurant_code, business_date)
