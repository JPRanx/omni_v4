"""
Supabase Database Client for OMNI V4.

Handles all database operations for persisting restaurant analytics data.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env from project root explicitly
_current_file = Path(__file__)
_project_root = _current_file.parent.parent.parent
_env_path = _project_root / '.env'
load_dotenv(_env_path, override=True)


class SupabaseClient:
    """Client for interacting with Supabase database."""

    def __init__(self):
        """Initialize Supabase client with credentials from environment."""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

        self.client: Client = create_client(self.url, self.key)

    # ========================================================================
    # DAILY OPERATIONS
    # ========================================================================

    def insert_daily_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert or update a daily operation record.

        Args:
            data: Dictionary with keys matching daily_operations table columns

        Returns:
            Inserted/updated record
        """
        result = self.client.table('daily_operations').upsert(
            data,
            on_conflict='business_date,restaurant_code'
        ).execute()

        return result.data[0] if result.data else {}

    def insert_daily_operations_batch(self, records: List[Dict[str, Any]]) -> int:
        """
        Insert multiple daily operations in batch.

        Args:
            records: List of daily operation dictionaries

        Returns:
            Number of records inserted
        """
        if not records:
            return 0

        result = self.client.table('daily_operations').upsert(
            records,
            on_conflict='business_date,restaurant_code'
        ).execute()

        return len(result.data)

    # ========================================================================
    # SHIFT OPERATIONS
    # ========================================================================

    def insert_shift_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a shift operation record."""
        result = self.client.table('shift_operations').upsert(
            data,
            on_conflict='business_date,restaurant_code,shift_name'
        ).execute()

        return result.data[0] if result.data else {}

    def insert_shift_operations_batch(self, records: List[Dict[str, Any]]) -> int:
        """Insert multiple shift operations in batch."""
        if not records:
            return 0

        result = self.client.table('shift_operations').upsert(
            records,
            on_conflict='business_date,restaurant_code,shift_name'
        ).execute()

        return len(result.data)

    # ========================================================================
    # VENDOR PAYOUTS
    # ========================================================================

    def delete_vendor_payouts(self, business_date: str, restaurant_code: str) -> int:
        """
        Delete all vendor payouts for a specific date and restaurant.

        Args:
            business_date: YYYY-MM-DD
            restaurant_code: Restaurant code (SDR, T12, TK9)

        Returns:
            Number of records deleted
        """
        result = self.client.table('vendor_payouts').delete().eq(
            'business_date', business_date
        ).eq(
            'restaurant_code', restaurant_code
        ).execute()

        return len(result.data) if result.data else 0

    def insert_vendor_payouts_batch(self, records: List[Dict[str, Any]]) -> int:
        """Insert multiple vendor payouts in batch (simple insert, no upsert)."""
        if not records:
            return 0

        result = self.client.table('vendor_payouts').insert(records).execute()
        return len(result.data)

    # ========================================================================
    # VOID TRANSACTIONS
    # ========================================================================

    def insert_void_transactions_batch(self, records: List[Dict[str, Any]]) -> int:
        """Insert multiple void transactions in batch."""
        if not records:
            return 0

        result = self.client.table('void_transactions').upsert(
            records,
            on_conflict='business_date,restaurant_code,order_number'
        ).execute()

        return len(result.data)

    # ========================================================================
    # PATTERNS
    # ========================================================================

    def insert_timeslot_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a timeslot pattern."""
        result = self.client.table('timeslot_patterns').upsert(
            data,
            on_conflict='pattern_key'
        ).execute()

        return result.data[0] if result.data else {}

    def insert_timeslot_patterns_batch(self, records: List[Dict[str, Any]]) -> int:
        """Insert multiple timeslot patterns in batch."""
        if not records:
            return 0

        result = self.client.table('timeslot_patterns').upsert(
            records,
            on_conflict='pattern_key'
        ).execute()

        return len(result.data)

    def insert_daily_labor_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a daily labor pattern."""
        result = self.client.table('daily_labor_patterns').upsert(
            data,
            on_conflict='restaurant_code,day_of_week'
        ).execute()

        return result.data[0] if result.data else {}

    # ========================================================================
    # TIMESLOT RESULTS
    # ========================================================================

    def insert_timeslot_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a timeslot result."""
        result = self.client.table('timeslot_results').upsert(
            data,
            on_conflict='business_date,restaurant_code,timeslot_index'
        ).execute()

        return result.data[0] if result.data else {}

    def insert_timeslot_results_batch(self, records: List[Dict[str, Any]]) -> int:
        """Insert multiple timeslot results in batch."""
        if not records:
            return 0

        result = self.client.table('timeslot_results').upsert(
            records,
            on_conflict='business_date,restaurant_code,timeslot_index'
        ).execute()

        return len(result.data)

    # ========================================================================
    # BATCH RUNS
    # ========================================================================

    def create_batch_run(
        self,
        start_date: str,
        end_date: str,
        restaurants: List[str]
    ) -> str:
        """
        Create a new batch run record.

        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            restaurants: List of restaurant codes

        Returns:
            Batch run ID (UUID)
        """
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'restaurants_processed': restaurants,
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }

        result = self.client.table('batch_runs').insert(data).execute()
        return result.data[0]['id']

    def update_batch_run(
        self,
        batch_id: str,
        status: str,
        records_processed: int,
        errors_count: int = 0,
        error_messages: Optional[Dict] = None
    ) -> None:
        """Update a batch run with completion status."""
        data = {
            'status': status,
            'records_processed': records_processed,
            'errors_count': errors_count,
            'completed_at': datetime.now().isoformat()
        }

        if error_messages:
            data['error_messages'] = error_messages

        self.client.table('batch_runs').update(data).eq('id', batch_id).execute()

    # ========================================================================
    # QUERIES
    # ========================================================================

    def get_daily_operations(
        self,
        restaurant_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query daily operations with filters.

        Args:
            restaurant_code: Filter by restaurant (optional)
            start_date: Filter by date >= start_date (optional)
            end_date: Filter by date <= end_date (optional)

        Returns:
            List of daily operation records
        """
        query = self.client.table('daily_operations').select("*")

        if restaurant_code:
            query = query.eq('restaurant_code', restaurant_code)

        if start_date:
            query = query.gte('business_date', start_date)

        if end_date:
            query = query.lte('business_date', end_date)

        query = query.order('business_date', desc=True)

        result = query.execute()
        return result.data

    def get_timeslot_patterns(
        self,
        restaurant_code: Optional[str] = None,
        reliable_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query timeslot patterns.

        Args:
            restaurant_code: Filter by restaurant (optional)
            reliable_only: Only return patterns with confidence >= 0.6

        Returns:
            List of pattern records
        """
        query = self.client.table('timeslot_patterns').select("*")

        if restaurant_code:
            query = query.eq('restaurant_code', restaurant_code)

        if reliable_only:
            query = query.gte('confidence', 0.6)

        result = query.execute()
        return result.data
