"""
VoidExtractor - Extract and parse void transaction data.

Handles VoidDetails CSV files with shift-based grouping.
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from pipeline.models.void_metrics_dto import VoidMetricsDTO, VoidTransactionDTO
from pipeline.services.result import Result


class VoidExtractor:
    """Extract void transactions from CSV files and group by shift."""

    # Shift boundaries (same as shift_splitter.py)
    MORNING_START_HOUR = 6
    SHIFT_CUTOFF_HOUR = 14  # 2 PM
    EVENING_END_HOUR = 22

    @staticmethod
    def detect_void_details_file(directory: Path, business_date: str) -> Optional[Path]:
        """
        Detect VoidDetails file with date in filename.

        Supports formats:
        - VoidDetails_YYYY_MM_DD.csv
        - VoidDetails_YYYYMMDD.csv
        - Void Details_YYYY_MM_DD.csv (with space)

        Args:
            directory: Directory to search
            business_date: Business date in YYYY-MM-DD format

        Returns:
            Path to VoidDetails file or None if not found
        """
        date_obj = datetime.fromisoformat(business_date).date()
        formats = [
            f"VoidDetails_{date_obj.strftime('%Y_%m_%d')}.csv",
            f"VoidDetails_{date_obj.strftime('%Y%m%d')}.csv",
            f"Void Details_{date_obj.strftime('%Y_%m_%d')}.csv",
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
        - M/D/YY H:MM AM/PM (e.g., "8/4/25 12:09 PM")
        - M/D/YYYY H:MM AM/PM (e.g., "8/4/2025 12:09 PM")

        Args:
            date_str: Datetime string from CSV

        Returns:
            Parsed datetime or None if empty/invalid
        """
        if not date_str or date_str.strip() == "":
            return None

        date_str = date_str.strip()

        formats = [
            "%m/%d/%y %I:%M %p",   # 8/4/25 12:09 PM
            "%m/%d/%Y %I:%M %p",   # 8/4/2025 12:09 PM
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    @classmethod
    def determine_shift(cls, void_datetime: datetime) -> str:
        """
        Determine if void occurred in morning or evening shift.

        Args:
            void_datetime: When the void occurred

        Returns:
            'morning' or 'evening'
        """
        hour = void_datetime.hour
        if cls.MORNING_START_HOUR <= hour < cls.SHIFT_CUTOFF_HOUR:
            return 'morning'
        else:
            return 'evening'

    @classmethod
    def extract(
        cls,
        file_path: Path
    ) -> Result[VoidMetricsDTO]:
        """
        Extract void transactions from VoidDetails CSV.

        Groups void items by order number and splits into morning/evening shifts.

        Args:
            file_path: Path to VoidDetails CSV

        Returns:
            Result containing VoidMetricsDTO or error
        """
        try:
            if not file_path.exists():
                # No void file means no voids - return empty metrics
                return Result.ok(VoidMetricsDTO(
                    morning_voids=[],
                    evening_voids=[]
                ))

            # Group void items by order number
            orders_data: Dict[str, Dict] = defaultdict(lambda: {
                'items': [],
                'total_amount': 0.0,
                'void_date': None,
                'server': None,
                'approver': None,
                'reasons': set()
            })

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

            # Process each void line item
            for row_num, row in enumerate(rows, start=2):
                try:
                    order_num = row.get('Order #', '').strip()
                    void_date_str = row.get('Void Date', '').strip()
                    server = row.get('Server', '').strip()
                    approver = row.get('Approver', '').strip()
                    item_name = row.get('Item Name', '').strip()
                    reason = row.get('Reason', '').strip()

                    # Parse price
                    try:
                        price = float(row.get('Total Price', '0').strip() or '0')
                    except ValueError:
                        price = 0.0

                    if not order_num or not void_date_str:
                        continue

                    # Parse void datetime
                    void_dt = cls.parse_datetime(void_date_str)
                    if void_dt is None:
                        print(f"[WARNING] Could not parse void date on row {row_num}: {void_date_str}")
                        continue

                    # Accumulate data for this order
                    order_data = orders_data[order_num]
                    if order_data['void_date'] is None:
                        order_data['void_date'] = void_dt
                        order_data['server'] = server
                        order_data['approver'] = approver

                    order_data['items'].append(item_name)
                    order_data['total_amount'] += price
                    if reason:
                        order_data['reasons'].add(reason)

                except Exception as e:
                    print(f"[WARNING] Error parsing void row {row_num}: {e}")
                    continue

            # Convert grouped data to VoidTransactionDTO objects
            morning_voids = []
            evening_voids = []

            for order_num, data in orders_data.items():
                if data['void_date'] is None:
                    continue

                # Determine which shift this void belongs to
                shift = cls.determine_shift(data['void_date'])

                # Combine reasons (usually just one, but handle multiples)
                reason_str = ', '.join(sorted(data['reasons'])) if data['reasons'] else 'Unknown'

                void_transaction = VoidTransactionDTO(
                    order_number=order_num,
                    void_date=data['void_date'],
                    server=data['server'] or 'Unknown',
                    approver=data['approver'] or 'Unknown',
                    reason=reason_str,
                    item_count=len(data['items']),
                    total_amount=data['total_amount'],
                    items_detail=data['items']
                )

                if shift == 'morning':
                    morning_voids.append(void_transaction)
                else:
                    evening_voids.append(void_transaction)

            # Sort by void_date
            morning_voids.sort(key=lambda v: v.void_date)
            evening_voids.sort(key=lambda v: v.void_date)

            return Result.ok(VoidMetricsDTO(
                morning_voids=morning_voids,
                evening_voids=evening_voids
            ))

        except Exception as e:
            return Result.fail(ValueError(f"Failed to extract voids: {str(e)}"))

    @classmethod
    def extract_from_directory(
        cls,
        directory: Path,
        business_date: str
    ) -> Result[VoidMetricsDTO]:
        """
        Auto-detect and extract void data from directory.

        Args:
            directory: Directory containing VoidDetails CSV
            business_date: Business date in YYYY-MM-DD format

        Returns:
            Result containing VoidMetricsDTO (empty if no file found)
        """
        file_path = cls.detect_void_details_file(directory, business_date)

        if file_path is None:
            # No void file means no voids - return empty metrics
            return Result.ok(VoidMetricsDTO(
                morning_voids=[],
                evening_voids=[]
            ))

        return cls.extract(file_path)