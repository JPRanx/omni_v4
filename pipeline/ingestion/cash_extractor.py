"""
CashExtractor - Extract cash flow data from Cash activity CSV.

Reads Toast POS Cash activity.csv and extracts:
- Total cash payments (cash_collected)
- Tips distributed (gratuity + tips)
- Total cash (net_cash)
"""

import csv
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

from pipeline.services.result import Result


@dataclass
class CashMetrics:
    """Cash flow metrics extracted from Cash activity CSV."""

    cash_collected: float = 0.0
    tips_distributed: float = 0.0
    vendor_payouts: float = 0.0
    net_cash: float = 0.0


class CashExtractor:
    """Extract cash flow metrics from Cash activity CSV file."""

    @staticmethod
    def detect_cash_activity_file(directory: Path) -> Optional[Path]:
        """
        Detect Cash activity file.

        Supports formats:
        - Cash activity.csv (with space)
        - CashActivity.csv (no space)

        Args:
            directory: Directory to search

        Returns:
            Path to Cash activity file or None if not found
        """
        formats = [
            "Cash activity.csv",
            "CashActivity.csv",
        ]

        for filename in formats:
            file_path = directory / filename
            if file_path.exists():
                return file_path

        return None

    @classmethod
    def extract(cls, file_path: Path) -> Result[CashMetrics]:
        """
        Extract cash metrics from Cash activity CSV.

        Expected columns:
        - Total cash payments
        - Cash gratuity
        - Credit/non-cash gratuity
        - Credit/non-cash tips
        - Total cash

        Args:
            file_path: Path to Cash activity CSV

        Returns:
            Result containing CashMetrics or error
        """
        try:
            if not file_path.exists():
                # No cash file means no cash data - return zeros
                return Result.ok(CashMetrics())

            # Try UTF-8 first, fall back to latin-1 for special characters
            encoding = 'utf-8-sig'
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            except UnicodeDecodeError:
                encoding = 'latin-1'
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

            if len(rows) == 0:
                return Result.ok(CashMetrics())

            # Cash activity CSV has only one data row (daily totals)
            row = rows[0]

            # Extract values, handling empty strings and converting to float
            def safe_float(value: str) -> float:
                """Safely convert string to float, returning 0.0 if empty or invalid."""
                if not value or value.strip() == '':
                    return 0.0
                try:
                    return float(value.strip())
                except (ValueError, AttributeError):
                    return 0.0

            # Map CSV columns to our fields
            cash_collected = safe_float(row.get('Total cash payments', '0'))

            # Tips distributed = Cash gratuity + Credit/non-cash gratuity + Credit/non-cash tips
            # (Note: Credit tips might be negative in the CSV, representing tips paid out)
            cash_gratuity = safe_float(row.get('Cash gratuity', '0'))
            credit_gratuity = safe_float(row.get('Credit/non-cash gratuity', '0'))
            credit_tips = safe_float(row.get('Credit/non-cash tips', '0'))
            tips_distributed = abs(cash_gratuity) + abs(credit_gratuity) + abs(credit_tips)

            net_cash = safe_float(row.get('Total cash', '0'))

            # Vendor payouts not in this CSV - would need separate source
            vendor_payouts = 0.0

            return Result.ok(CashMetrics(
                cash_collected=cash_collected,
                tips_distributed=tips_distributed,
                vendor_payouts=vendor_payouts,
                net_cash=net_cash
            ))

        except Exception as e:
            return Result.fail(ValueError(f"Failed to extract cash metrics: {str(e)}"))

    @classmethod
    def extract_from_directory(cls, directory: Path) -> Result[CashMetrics]:
        """
        Auto-detect and extract cash data from directory.

        Args:
            directory: Directory containing Cash activity CSV

        Returns:
            Result containing CashMetrics (zeros if no file found)
        """
        file_path = cls.detect_cash_activity_file(directory)

        if file_path is None:
            # No cash file means no cash data - return zeros
            return Result.ok(CashMetrics())

        return cls.extract(file_path)