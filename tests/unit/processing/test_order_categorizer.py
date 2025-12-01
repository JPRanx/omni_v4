"""
Tests for OrderCategorizer - Order type categorization logic.

Verifies that orders are correctly categorized as Lobby, Drive-Thru, or ToGo
based on V3's filter cascade logic.
"""

import pytest
import pandas as pd
from pathlib import Path

from pipeline.services.order_categorizer import OrderCategorizer


class TestOrderCategorizer:
    """Test OrderCategorizer filter cascade logic."""

    @pytest.fixture
    def categorizer(self):
        """Create OrderCategorizer with default config."""
        return OrderCategorizer()

    @pytest.fixture
    def sample_kitchen_df(self):
        """Create sample Kitchen Details DataFrame."""
        return pd.DataFrame([
            {'Check #': '1001', 'Table': 15, 'Fulfillment Time': 12.5, 'Server': 'Smith, John'},
            {'Check #': '1002', 'Table': None, 'Fulfillment Time': 5.2, 'Server': 'Doe, Jane'},
            {'Check #': '1003', 'Table': 8, 'Fulfillment Time': 18.0, 'Server': 'Brown, Alice'},
            {'Check #': '1004', 'Table': None, 'Fulfillment Time': 3.5, 'Server': 'White, Bob'},
            {'Check #': '1005', 'Table': 0, 'Fulfillment Time': 11.0, 'Server': 'Green, Carol'}
        ])

    @pytest.fixture
    def sample_eod_df(self):
        """Create sample EOD DataFrame."""
        return pd.DataFrame([
            {'Check #': '1001', 'Table': 15, 'Cash Drawer': 'Register 1'},
            {'Check #': '1002', 'Table': None, 'Cash Drawer': 'Drive Box 1'},
            {'Check #': '1003', 'Table': 8, 'Cash Drawer': 'Register 2'},
            {'Check #': '1004', 'Table': None, 'Cash Drawer': 'Register 3'},
            {'Check #': '1005', 'Table': None, 'Cash Drawer': 'ToGo Counter'}
        ])

    @pytest.fixture
    def sample_order_details_df(self):
        """Create sample OrderDetails DataFrame."""
        return pd.DataFrame([
            {'Order #': '1001', 'Table': 15, 'Duration (Opened to Paid)': '25:30', 'Server': 'Smith, John'},
            {'Order #': '1002', 'Table': None, 'Duration (Opened to Paid)': '6:15', 'Server': 'Doe, Jane'},
            {'Order #': '1003', 'Table': 8, 'Duration (Opened to Paid)': '32:00', 'Server': 'Brown, Alice'},
            {'Order #': '1004', 'Table': None, 'Duration (Opened to Paid)': '4:30', 'Server': 'White, Bob'},
            {'Order #': '1005', 'Table': None, 'Duration (Opened to Paid)': '15:00', 'Server': 'Green, Carol'}
        ])

    @pytest.fixture
    def sample_time_entries_df(self):
        """Create sample TimeEntries DataFrame."""
        return pd.DataFrame([
            {'Employee': 'John Smith', 'Job Title': 'Server'},
            {'Employee': 'Jane Doe', 'Job Title': 'Drive-Thru Operator'},
            {'Employee': 'Alice Brown', 'Job Title': 'Server'},
            {'Employee': 'Bob White', 'Job Title': 'Cashier'},
            {'Employee': 'Carol Green', 'Job Title': 'Cook'}
        ])

    # ========================================================================
    # FILTER 1: LOBBY DETECTION TESTS
    # ========================================================================

    def test_lobby_table_in_two_sources(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df):
        """Test: Order with table in 2+ sources = Lobby"""
        result = categorizer.categorize_order(
            '1001',  # Has table in kitchen + EOD + order_details
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()
        assert result.unwrap() == "Lobby"

    def test_lobby_table_plus_server_position(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df, sample_time_entries_df):
        """Test: Order with table in 1 source + server position = Lobby"""
        # Create order with table only in kitchen, but server position is 'server'
        kitchen_df = pd.DataFrame([{'Check #': '2001', 'Table': 10, 'Fulfillment Time': 8.0, 'Server': 'Smith, John'}])
        eod_df = pd.DataFrame([{'Check #': '2001', 'Table': None, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '2001', 'Table': None, 'Duration (Opened to Paid)': '12:00'}])

        result = categorizer.categorize_order(
            '2001',
            kitchen_df,
            eod_df,
            order_df,
            sample_time_entries_df
        )

        assert result.is_ok()
        assert result.unwrap() == "Lobby"

    def test_lobby_table_plus_long_duration(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df):
        """Test: Order with table + kitchen time > 15 min = Lobby"""
        result = categorizer.categorize_order(
            '1003',  # Has table and kitchen_duration=18.0 min
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()
        assert result.unwrap() == "Lobby"

    # ========================================================================
    # FILTER 2: DRIVE-THRU DETECTION TESTS
    # ========================================================================

    def test_drive_thru_cash_drawer(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df):
        """Test: Order with 'drive' in cash drawer = Drive-Thru"""
        result = categorizer.categorize_order(
            '1002',  # Cash Drawer = 'Drive Box 1'
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()
        assert result.unwrap() == "Drive-Thru"

    def test_drive_thru_employee_position(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df, sample_time_entries_df):
        """Test: Order served by drive-thru employee = Drive-Thru"""
        result = categorizer.categorize_order(
            '1002',  # Server is Jane Doe (Drive-Thru Operator)
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df,
            sample_time_entries_df
        )

        assert result.is_ok()
        assert result.unwrap() == "Drive-Thru"

    def test_drive_thru_fast_kitchen_time(self, categorizer):
        """Test: No table + kitchen time < 7 min = Drive-Thru"""
        kitchen_df = pd.DataFrame([{'Check #': '3001', 'Table': None, 'Fulfillment Time': 4.5, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '3001', 'Table': None, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '3001', 'Table': None, 'Duration (Opened to Paid)': '12:00'}])

        result = categorizer.categorize_order('3001', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        assert result.unwrap() == "Drive-Thru"

    def test_drive_thru_fast_order_time(self, categorizer):
        """Test: No table + order duration < 10 min = Drive-Thru"""
        kitchen_df = pd.DataFrame([{'Check #': '3002', 'Table': None, 'Fulfillment Time': 15.0, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '3002', 'Table': None, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '3002', 'Table': None, 'Duration (Opened to Paid)': '5:30'}])  # 5.5 min

        result = categorizer.categorize_order('3002', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        assert result.unwrap() == "Drive-Thru"

    # ========================================================================
    # FILTER 3: TOGO DEFAULT TESTS
    # ========================================================================

    def test_togo_default(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df):
        """Test: Order not matching Lobby or Drive-Thru = ToGo"""
        result = categorizer.categorize_order(
            '1005',  # No table, medium times, no drive indicators
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()
        assert result.unwrap() == "ToGo"

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_missing_kitchen_entry(self, categorizer):
        """Test: Order missing from kitchen details defaults to ToGo"""
        kitchen_df = pd.DataFrame([{'Check #': '9999', 'Table': 5, 'Fulfillment Time': 10.0, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '4001', 'Table': None, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '4001', 'Table': None, 'Duration (Opened to Paid)': '12:00'}])

        result = categorizer.categorize_order('4001', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        # With no kitchen data, no table signals, defaults to ToGo
        assert result.unwrap() == "ToGo"

    def test_missing_eod_entry(self, categorizer):
        """Test: Order missing from EOD still categorizes based on other sources"""
        kitchen_df = pd.DataFrame([{'Check #': '4002', 'Table': 12, 'Fulfillment Time': 14.0, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '9999', 'Table': 5, 'Cash Drawer': 'Drive Box'}])
        order_df = pd.DataFrame([{'Order #': '4002', 'Table': 12, 'Duration (Opened to Paid)': '18:00'}])

        result = categorizer.categorize_order('4002', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        # Has table in kitchen + order_details (2 sources) = Lobby
        assert result.unwrap() == "Lobby"

    def test_table_zero_treated_as_no_table(self, categorizer):
        """Test: Table = 0 is treated as no table"""
        kitchen_df = pd.DataFrame([{'Check #': '4003', 'Table': 0, 'Fulfillment Time': 4.0, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '4003', 'Table': 0, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '4003', 'Table': None, 'Duration (Opened to Paid)': '8:00'}])

        result = categorizer.categorize_order('4003', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        # No valid tables, fast kitchen time (4 min < 7) = Drive-Thru
        assert result.unwrap() == "Drive-Thru"

    def test_null_duration_handled(self, categorizer):
        """Test: Null/NaN duration doesn't crash"""
        kitchen_df = pd.DataFrame([{'Check #': '4004', 'Table': None, 'Fulfillment Time': None, 'Server': 'Test'}])
        eod_df = pd.DataFrame([{'Check #': '4004', 'Table': None, 'Cash Drawer': 'Register 1'}])
        order_df = pd.DataFrame([{'Order #': '4004', 'Table': None, 'Duration (Opened to Paid)': None}])

        result = categorizer.categorize_order('4004', kitchen_df, eod_df, order_df)

        assert result.is_ok()
        # No signals, defaults to ToGo
        assert result.unwrap() == "ToGo"

    # ========================================================================
    # DURATION PARSING TESTS
    # ========================================================================

    def test_parse_duration_mm_ss(self, categorizer):
        """Test: Parse MM:SS format"""
        assert categorizer._parse_duration_string("5:30") == pytest.approx(5.5, rel=0.01)
        assert categorizer._parse_duration_string("12:45") == pytest.approx(12.75, rel=0.01)

    def test_parse_duration_hh_mm_ss(self, categorizer):
        """Test: Parse HH:MM:SS format"""
        assert categorizer._parse_duration_string("1:23:30") == pytest.approx(83.5, rel=0.01)

    def test_parse_duration_text(self, categorizer):
        """Test: Parse 'X minutes and Y seconds' format"""
        assert categorizer._parse_duration_string("3 minutes and 45 seconds") == pytest.approx(3.75, rel=0.01)
        assert categorizer._parse_duration_string("15 minutes") == pytest.approx(15.0, rel=0.01)
        assert categorizer._parse_duration_string("30 seconds") == pytest.approx(0.5, rel=0.01)

    def test_parse_duration_float(self, categorizer):
        """Test: Parse direct float"""
        assert categorizer._parse_duration_string("12.5") == pytest.approx(12.5, rel=0.01)
        assert categorizer._parse_duration_string("7") == pytest.approx(7.0, rel=0.01)

    def test_parse_duration_none(self, categorizer):
        """Test: Parse None/NaN returns 0"""
        assert categorizer._parse_duration_string(None) == 0.0
        assert categorizer._parse_duration_string(pd.NA) == 0.0
        assert categorizer._parse_duration_string("") == 0.0

    # ========================================================================
    # BATCH CATEGORIZATION TESTS
    # ========================================================================

    def test_categorize_all_orders(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df):
        """Test: Categorize all orders in dataset"""
        result = categorizer.categorize_all_orders(
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()

        categorizations = result.unwrap()
        assert len(categorizations) == 5  # All 5 sample orders

        # Verify specific categorizations
        assert categorizations['1001'] == "Lobby"       # Table in 3 sources
        assert categorizations['1002'] == "Drive-Thru"  # Drive cash drawer
        assert categorizations['1003'] == "Lobby"       # Table + long duration
        assert categorizations['1005'] == "ToGo"        # Default

    def test_categorize_only_fulfilled_orders(self, categorizer):
        """Test: Only categorize orders with kitchen entries"""
        kitchen_df = pd.DataFrame([
            {'Check #': '5001', 'Table': 5, 'Fulfillment Time': 10.0, 'Server': 'Test'},
            {'Check #': '5002', 'Table': None, 'Fulfillment Time': 6.0, 'Server': 'Test'}
        ])
        eod_df = pd.DataFrame([
            {'Check #': '5001', 'Table': 5, 'Cash Drawer': 'Register 1'},
            {'Check #': '5003', 'Table': None, 'Cash Drawer': 'Register 2'}  # In EOD but not kitchen
        ])
        order_df = pd.DataFrame([
            {'Order #': '5001', 'Table': 5, 'Duration (Opened to Paid)': '15:00'},
            {'Order #': '5002', 'Table': None, 'Duration (Opened to Paid)': '8:00'},
            {'Order #': '5003', 'Table': None, 'Duration (Opened to Paid)': '10:00'}  # In orders but not kitchen
        ])

        result = categorizer.categorize_all_orders(kitchen_df, eod_df, order_df)

        assert result.is_ok()
        categorizations = result.unwrap()

        # Only orders with kitchen entries should be categorized
        assert len(categorizations) == 2
        assert '5001' in categorizations
        assert '5002' in categorizations
        assert '5003' not in categorizations  # No kitchen entry = not fulfilled

    def test_categorize_distribution_logging(self, categorizer, sample_kitchen_df, sample_eod_df, sample_order_details_df, caplog):
        """Test: Verify distribution logging works"""
        result = categorizer.categorize_all_orders(
            sample_kitchen_df,
            sample_eod_df,
            sample_order_details_df
        )

        assert result.is_ok()

        # Check logs contain distribution info
        assert 'categorization_complete' in caplog.text

    # ========================================================================
    # CONFIGURATION TESTS
    # ========================================================================

    def test_custom_thresholds(self):
        """Test: Custom thresholds can be configured"""
        custom_config = {
            'lobby_table_threshold': 3,  # Require table in 3 sources
            'drive_thru_time_kitchen_max': 5  # Faster drive-thru cutoff
        }

        categorizer = OrderCategorizer(config=custom_config)

        assert categorizer.lobby_table_threshold == 3
        assert categorizer.drive_thru_time_kitchen_max == 5

    # ========================================================================
    # HELPER METHOD TESTS
    # ========================================================================

    def test_safe_float_conversion(self, categorizer):
        """Test: _safe_float handles various inputs"""
        assert categorizer._safe_float(15) == 15.0
        assert categorizer._safe_float(15.5) == 15.5
        assert categorizer._safe_float("23") == 23.0
        assert categorizer._safe_float("23.7") == 23.7
        assert categorizer._safe_float(None) is None
        assert categorizer._safe_float(pd.NA) is None
        assert categorizer._safe_float("") is None
        assert categorizer._safe_float("invalid") is None

    def test_employee_position_lookup(self, categorizer, sample_time_entries_df):
        """Test: _lookup_employee_position handles name variations"""
        # "Last, First" format
        position = categorizer._lookup_employee_position("Smith, John", sample_time_entries_df)
        assert position == "server"

        # "First Last" format
        position = categorizer._lookup_employee_position("Jane Doe", sample_time_entries_df)
        assert position == "drive-thru operator"

        # Partial match
        position = categorizer._lookup_employee_position("Alice", sample_time_entries_df)
        assert position == "server"

        # No match
        position = categorizer._lookup_employee_position("Unknown Person", sample_time_entries_df)
        assert position == ""
