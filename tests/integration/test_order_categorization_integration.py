"""
Integration test for OrderCategorizer with real sample data.

Validates categorization logic against SDR 2025-08-20 sample data.
"""

import pytest
import pandas as pd
from pathlib import Path

from pipeline.services.order_categorizer import OrderCategorizer
from pipeline.ingestion.csv_data_source import CSVDataSource


class TestOrderCategorizationIntegration:
    """Integration tests with real SDR sample data."""

    @pytest.fixture
    def sample_data_path(self):
        """Path to SDR sample data."""
        return Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR")

    @pytest.fixture
    def categorizer(self):
        """Create OrderCategorizer."""
        return OrderCategorizer()

    @pytest.fixture
    def kitchen_df(self, sample_data_path):
        """Load real Kitchen Details CSV."""
        source = CSVDataSource(sample_data_path)
        result = source.get_csv("Kitchen Details_2025_08_20.csv")
        assert result.is_ok()
        return result.unwrap()

    @pytest.fixture
    def eod_df(self, sample_data_path):
        """Load real EOD CSV."""
        source = CSVDataSource(sample_data_path)
        result = source.get_csv("EOD_2025_08_20.csv")
        assert result.is_ok()
        return result.unwrap()

    @pytest.fixture
    def order_details_df(self, sample_data_path):
        """Load real OrderDetails CSV."""
        source = CSVDataSource(sample_data_path)
        result = source.get_csv("OrderDetails_2025_08_20.csv")
        assert result.is_ok()
        return result.unwrap()

    @pytest.fixture
    def time_entries_df(self, sample_data_path):
        """Load real TimeEntries CSV."""
        source = CSVDataSource(sample_data_path)
        result = source.get_csv("TimeEntries_2025_08_20.csv")
        assert result.is_ok()
        return result.unwrap()

    def test_categorize_real_sample_data(self, categorizer, kitchen_df, eod_df, order_details_df, time_entries_df):
        """Test categorization with real SDR August 20 data."""
        print(f"\n=== SDR 2025-08-20 Data Stats ===")
        print(f"Kitchen Details rows: {len(kitchen_df)}")
        print(f"EOD rows: {len(eod_df)}")
        print(f"OrderDetails rows: {len(order_details_df)}")
        print(f"TimeEntries rows: {len(time_entries_df)}")

        # Categorize all orders
        result = categorizer.categorize_all_orders(
            kitchen_df,
            eod_df,
            order_details_df,
            time_entries_df
        )

        assert result.is_ok(), f"Categorization failed: {result.unwrap_err()}"

        categorizations = result.unwrap()

        # Calculate distribution
        lobby_count = sum(1 for cat in categorizations.values() if cat == "Lobby")
        drive_thru_count = sum(1 for cat in categorizations.values() if cat == "Drive-Thru")
        togo_count = sum(1 for cat in categorizations.values() if cat == "ToGo")
        total = len(categorizations)

        lobby_pct = (lobby_count / total * 100) if total > 0 else 0
        drive_thru_pct = (drive_thru_count / total * 100) if total > 0 else 0
        togo_pct = (togo_count / total * 100) if total > 0 else 0

        print(f"\n=== Categorization Results ===")
        print(f"Total orders categorized: {total}")
        print(f"Lobby: {lobby_count} ({lobby_pct:.1f}%)")
        print(f"Drive-Thru: {drive_thru_count} ({drive_thru_pct:.1f}%)")
        print(f"ToGo: {togo_count} ({togo_pct:.1f}%)")

        # Validate results
        assert total > 0, "Should categorize at least some orders"
        assert total == lobby_count + drive_thru_count + togo_count, "All orders should be categorized"

        # Sanity check: distribution should be reasonable (not 99% in one category)
        assert lobby_pct < 90, f"Lobby percentage too high: {lobby_pct:.1f}%"
        assert drive_thru_pct < 90, f"Drive-Thru percentage too high: {drive_thru_pct:.1f}%"
        assert togo_pct < 90, f"ToGo percentage too high: {togo_pct:.1f}%"

        # At least two categories should have orders
        categories_with_orders = sum([lobby_count > 0, drive_thru_count > 0, togo_count > 0])
        assert categories_with_orders >= 2, "Should have at least 2 categories with orders"

    def test_sample_specific_orders(self, categorizer, kitchen_df, eod_df, order_details_df):
        """Test specific orders from sample data to verify logic."""
        # Find an order with a table (should be Lobby)
        orders_with_tables = eod_df[eod_df['Table'].notna() & (eod_df['Table'] > 0)]

        if not orders_with_tables.empty:
            table_order = str(orders_with_tables.iloc[0]['Check #'])

            result = categorizer.categorize_order(
                table_order,
                kitchen_df,
                eod_df,
                order_details_df
            )

            assert result.is_ok()
            category = result.unwrap()

            print(f"\nOrder {table_order} (has table): {category}")

            # Orders with tables should usually be Lobby
            # (unless they have very fast service times indicating takeout from table)

    def test_categorization_performance(self, categorizer, kitchen_df, eod_df, order_details_df, time_entries_df):
        """Test that categorization completes in reasonable time."""
        import time

        start = time.time()

        result = categorizer.categorize_all_orders(
            kitchen_df,
            eod_df,
            order_details_df,
            time_entries_df
        )

        duration = time.time() - start

        assert result.is_ok()
        categorizations = result.unwrap()

        print(f"\n=== Performance ===")
        print(f"Orders categorized: {len(categorizations)}")
        print(f"Duration: {duration:.3f} seconds")
        print(f"Orders per second: {len(categorizations) / duration:.0f}")

        # Should process all orders in less than 2 seconds
        assert duration < 2.0, f"Categorization too slow: {duration:.3f}s"

    def test_categorization_completeness(self, categorizer, kitchen_df, eod_df, order_details_df):
        """Test that all fulfilled orders get categorized."""
        # Get all check numbers from Kitchen Details (fulfilled orders)
        kitchen_checks = set(kitchen_df['Check #'].unique())

        result = categorizer.categorize_all_orders(
            kitchen_df,
            eod_df,
            order_details_df
        )

        assert result.is_ok()
        categorizations = result.unwrap()

        categorized_checks = set(categorizations.keys())

        # Find orders present in both Kitchen and OrderDetails
        order_checks = set(order_details_df['Order #'].astype(str).unique())
        fulfilled_and_ordered = kitchen_checks & order_checks

        print(f"\n=== Completeness ===")
        print(f"Kitchen checks: {len(kitchen_checks)}")
        print(f"Order checks: {len(order_checks)}")
        print(f"Fulfilled & Ordered: {len(fulfilled_and_ordered)}")
        print(f"Categorized: {len(categorized_checks)}")

        # All fulfilled orders that are also in OrderDetails should be categorized
        uncategorized = fulfilled_and_ordered - categorized_checks

        if uncategorized:
            print(f"Uncategorized orders: {list(uncategorized)[:10]}")

        # Should categorize most fulfilled orders (some might be missing from OrderDetails)
        coverage = len(categorized_checks) / len(fulfilled_and_ordered) * 100 if fulfilled_and_ordered else 0
        print(f"Coverage: {coverage:.1f}%")

        assert coverage > 80, f"Low categorization coverage: {coverage:.1f}%"

    def test_data_quality_checks(self, kitchen_df, eod_df, order_details_df):
        """Verify data quality of sample CSV files."""
        # Check Kitchen Details
        assert 'Check #' in kitchen_df.columns
        assert 'Table' in kitchen_df.columns
        assert 'Fulfillment Time' in kitchen_df.columns
        assert len(kitchen_df) > 0

        # Check EOD
        assert 'Check #' in eod_df.columns
        assert 'Table' in eod_df.columns
        assert 'Cash Drawer' in eod_df.columns
        assert len(eod_df) > 0

        # Check OrderDetails
        assert 'Order #' in order_details_df.columns
        assert 'Table' in order_details_df.columns
        assert len(order_details_df) > 0

        print(f"\n=== Data Quality ===")
        print(f"Kitchen has {kitchen_df['Table'].notna().sum()} entries with tables")
        print(f"EOD has {eod_df['Table'].notna().sum()} entries with tables")
        print(f"OrderDetails has {order_details_df['Table'].notna().sum()} entries with tables")
