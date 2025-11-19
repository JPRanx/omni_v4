"""
Test CSV loading for order categorization files (Kitchen Details, EOD, OrderDetails).

Verifies that the enhanced IngestionStage can load all CSVs needed for
order categorization without errors.
"""

import pytest
from pathlib import Path

from src.ingestion.csv_data_source import CSVDataSource
from src.ingestion.data_validator import DataValidator
from src.processing.stages.ingestion_stage import IngestionStage
from src.orchestration.pipeline.context import PipelineContext


class TestOrderCSVLoading:
    """Test loading of Kitchen Details, EOD, and OrderDetails CSVs."""

    @pytest.fixture
    def sample_data_path(self):
        """Path to SDR sample data for 2025-08-20."""
        return Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR")

    @pytest.fixture
    def data_source(self, sample_data_path):
        """Create CSVDataSource for sample data."""
        return CSVDataSource(sample_data_path)

    @pytest.fixture
    def validator(self):
        """Create DataValidator."""
        return DataValidator()

    @pytest.fixture
    def ingestion_stage(self, validator):
        """Create IngestionStage."""
        return IngestionStage(validator)

    def test_kitchen_details_loads(self, data_source):
        """Test that Kitchen Details CSV loads successfully."""
        result = data_source.get_csv("Kitchen Details_2025_08_20.csv")

        assert result.is_ok(), f"Failed to load Kitchen Details: {result.unwrap_err()}"

        df = result.unwrap()
        assert not df.empty, "Kitchen Details DataFrame is empty"
        assert 'Check #' in df.columns, "Missing 'Check #' column"
        assert 'Fulfillment Time' in df.columns, "Missing 'Fulfillment Time' column"
        assert 'Table' in df.columns, "Missing 'Table' column"
        assert 'Expediter Level' in df.columns, "Missing 'Expediter Level' column"

    def test_eod_loads(self, data_source):
        """Test that EOD CSV loads successfully."""
        result = data_source.get_csv("EOD_2025_08_20.csv")

        assert result.is_ok(), f"Failed to load EOD: {result.unwrap_err()}"

        df = result.unwrap()
        assert not df.empty, "EOD DataFrame is empty"
        assert 'Check #' in df.columns, "Missing 'Check #' column"
        assert 'Cash Drawer' in df.columns, "Missing 'Cash Drawer' column"
        assert 'Table' in df.columns, "Missing 'Table' column"

    def test_order_details_loads(self, data_source):
        """Test that OrderDetails CSV loads successfully."""
        result = data_source.get_csv("OrderDetails_2025_08_20.csv")

        assert result.is_ok(), f"Failed to load OrderDetails: {result.unwrap_err()}"

        df = result.unwrap()
        assert not df.empty, "OrderDetails DataFrame is empty"
        assert 'Order #' in df.columns, "Missing 'Order #' column"
        assert 'Opened' in df.columns, "Missing 'Opened' column"
        assert 'Server' in df.columns, "Missing 'Server' column"
        assert 'Amount' in df.columns, "Missing 'Amount' column"

    def test_validator_handles_optional_files(self, validator):
        """Test that DataValidator properly validates optional files."""
        # Kitchen Details should have required columns
        assert 'kitchen' in validator.OPTIONAL_COLUMNS
        assert 'Table' in validator.OPTIONAL_COLUMNS['kitchen']
        assert 'Expediter Level' in validator.OPTIONAL_COLUMNS['kitchen']

        # EOD should have required columns
        assert 'eod' in validator.OPTIONAL_COLUMNS
        assert 'Cash Drawer' in validator.OPTIONAL_COLUMNS['eod']
        assert 'Table' in validator.OPTIONAL_COLUMNS['eod']

    def test_ingestion_stage_loads_all_files(self, ingestion_stage):
        """Test that IngestionStage loads all files including new optional ones."""
        # Create context with required inputs
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', 'C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR')

        # Execute ingestion stage
        result = ingestion_stage.execute(context)

        assert result.is_ok(), f"Ingestion failed: {result.unwrap_err()}"

        # Check that context has raw_dataframes
        assert context.has('raw_dataframes'), "Missing raw_dataframes in context"

        dfs = context.get('raw_dataframes')

        # Required files should be present
        assert 'labor' in dfs, "Missing labor data"
        assert 'sales' in dfs, "Missing sales data"
        assert 'orders' in dfs, "Missing orders data"

        # Optional files should be present (since they exist in sample data)
        assert 'kitchen' in dfs, "Missing kitchen data (optional but present)"
        assert 'eod' in dfs, "Missing EOD data (optional but present)"
        assert 'payroll' in dfs, "Missing payroll data (optional but present)"

    def test_ingestion_stage_kitchen_details_columns(self, ingestion_stage):
        """Test that Kitchen Details has all required columns after loading."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', 'C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR')

        result = ingestion_stage.execute(context)
        assert result.is_ok()

        dfs = context.get('raw_dataframes')
        kitchen_df = dfs['kitchen']

        # Verify all columns needed for order categorization
        required_cols = ['Check #', 'Table', 'Fulfillment Time', 'Server', 'Expediter Level']
        for col in required_cols:
            assert col in kitchen_df.columns, f"Missing column: {col}"

    def test_ingestion_stage_eod_columns(self, ingestion_stage):
        """Test that EOD has all required columns after loading."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', 'C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR')

        result = ingestion_stage.execute(context)
        assert result.is_ok()

        dfs = context.get('raw_dataframes')
        eod_df = dfs['eod']

        # Verify all columns needed for order categorization
        required_cols = ['Check #', 'Table', 'Cash Drawer']
        for col in required_cols:
            assert col in eod_df.columns, f"Missing column: {col}"

    def test_sample_data_quality(self, ingestion_stage):
        """Test sample data quality - verify we have enough data for categorization."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', 'C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR')

        result = ingestion_stage.execute(context)
        assert result.is_ok()

        dfs = context.get('raw_dataframes')

        # Check we have orders to categorize
        orders_df = dfs['orders']
        assert len(orders_df) > 0, "No orders in sample data"

        # Check we have kitchen data
        kitchen_df = dfs['kitchen']
        assert len(kitchen_df) > 0, "No kitchen details in sample data"

        # Check we have EOD data
        eod_df = dfs['eod']
        assert len(eod_df) > 0, "No EOD data in sample data"

        # Verify some orders have tables (Lobby orders)
        orders_with_tables = orders_df['Table'].notna().sum()
        assert orders_with_tables > 0, "No orders with tables (expected some Lobby orders)"

        print(f"Sample data quality:")
        print(f"  - Orders: {len(orders_df)}")
        print(f"  - Kitchen entries: {len(kitchen_df)}")
        print(f"  - EOD entries: {len(eod_df)}")
        print(f"  - Orders with tables: {orders_with_tables}")
