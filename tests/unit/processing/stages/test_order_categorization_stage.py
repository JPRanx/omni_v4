"""
Tests for OrderCategorizationStage.

Verifies that the stage integrates OrderCategorizer into the V4 pipeline correctly.
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime

from pipeline.stages.order_categorization_stage import OrderCategorizationStage
from pipeline.services.order_categorizer import OrderCategorizer
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.ingestion.csv_data_source import CSVDataSource
from pipeline.ingestion.data_validator import DataValidator
from pipeline.stages.ingestion_stage import IngestionStage


class TestOrderCategorizationStage:
    """Test OrderCategorizationStage with sample data."""

    @pytest.fixture
    def sample_data_path(self):
        """Path to SDR sample data."""
        return Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR")

    @pytest.fixture
    def categorization_stage(self):
        """Create OrderCategorizationStage."""
        return OrderCategorizationStage()

    @pytest.fixture
    def ingestion_stage(self):
        """Create IngestionStage."""
        validator = DataValidator()
        return IngestionStage(validator)

    @pytest.fixture
    def context_with_dataframes(self, sample_data_path, ingestion_stage):
        """Create context with loaded DataFrames."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(sample_data_path))

        # Run ingestion to load DataFrames
        result = ingestion_stage.execute(context)
        assert result.is_ok(), f"Ingestion failed: {result.unwrap_err()}"

        return context

    def test_execute_with_real_data(self, categorization_stage, context_with_dataframes):
        """Test stage execution with real sample data."""
        result = categorization_stage.execute(context_with_dataframes)

        assert result.is_ok(), f"Stage failed: {result.unwrap_err()}"

        # Verify context has categorization results
        assert context_with_dataframes.has('categorized_orders')
        assert context_with_dataframes.has('order_categories')
        assert context_with_dataframes.has('service_mix')
        assert context_with_dataframes.has('categorization_metadata')

    def test_categorized_orders_created(self, categorization_stage, context_with_dataframes):
        """Test that OrderDTOs are created."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        categorized_orders = context_with_dataframes.get('categorized_orders')

        assert isinstance(categorized_orders, list)
        assert len(categorized_orders) > 0

        # Check first order is an OrderDTO
        first_order = categorized_orders[0]
        assert hasattr(first_order, 'check_number')
        assert hasattr(first_order, 'category')
        assert hasattr(first_order, 'fulfillment_minutes')
        assert hasattr(first_order, 'shift')

        # Category should be valid
        assert first_order.category in ['Lobby', 'Drive-Thru', 'ToGo']

        # Shift should be valid
        assert first_order.shift in ['morning', 'evening']

    def test_service_mix_calculated(self, categorization_stage, context_with_dataframes):
        """Test that service mix percentages are calculated."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        service_mix = context_with_dataframes.get('service_mix')

        assert isinstance(service_mix, dict)
        assert 'Lobby' in service_mix
        assert 'Drive-Thru' in service_mix
        assert 'ToGo' in service_mix

        # Percentages should sum to ~100%
        total_pct = service_mix['Lobby'] + service_mix['Drive-Thru'] + service_mix['ToGo']
        assert 99.0 <= total_pct <= 101.0, f"Service mix percentages don't sum to 100%: {total_pct}"

    def test_order_categories_dict(self, categorization_stage, context_with_dataframes):
        """Test that order_categories mapping is created."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        order_categories = context_with_dataframes.get('order_categories')

        assert isinstance(order_categories, dict)
        assert len(order_categories) > 0

        # All values should be valid categories
        for category in order_categories.values():
            assert category in ['Lobby', 'Drive-Thru', 'ToGo']

    def test_categorization_metadata(self, categorization_stage, context_with_dataframes):
        """Test that categorization metadata is populated."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        metadata = context_with_dataframes.get('categorization_metadata')

        assert isinstance(metadata, dict)
        assert 'total_orders' in metadata
        assert 'categorized_orders' in metadata
        assert 'service_mix' in metadata
        assert 'kitchen_rows' in metadata
        assert 'eod_rows' in metadata
        assert 'order_details_rows' in metadata

        # Counts should be reasonable
        assert metadata['total_orders'] > 0
        assert metadata['categorized_orders'] > 0
        assert metadata['kitchen_rows'] > 0

    def test_missing_dataframes_error(self, categorization_stage):
        """Test that stage fails gracefully if DataFrames missing."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        # Don't set raw_dataframes

        result = categorization_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'raw_dataframes' in str(error)

    def test_missing_required_df(self, categorization_stage):
        """Test that stage fails if required DataFrame is missing."""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')

        # Missing 'kitchen' DataFrame
        context.set('raw_dataframes', {
            'eod': pd.DataFrame(),
            'orders': pd.DataFrame()
        })

        result = categorization_stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'kitchen' in str(error).lower()

    def test_shift_determination(self, categorization_stage, context_with_dataframes):
        """Test that shifts are correctly determined."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        categorized_orders = context_with_dataframes.get('categorized_orders')

        # Should have orders in both shifts
        morning_orders = [o for o in categorized_orders if o.shift == 'morning']
        evening_orders = [o for o in categorized_orders if o.shift == 'evening']

        print(f"\nShift distribution:")
        print(f"  Morning (6 AM - 2 PM): {len(morning_orders)}")
        print(f"  Evening (2 PM - 10 PM): {len(evening_orders)}")

        # At least one shift should have orders (depends on sample data times)
        assert len(morning_orders) + len(evening_orders) == len(categorized_orders)

    def test_order_dto_fields_populated(self, categorization_stage, context_with_dataframes):
        """Test that OrderDTO fields are properly populated from DataFrames."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        categorized_orders = context_with_dataframes.get('categorized_orders')

        # Check a sample order
        sample_order = categorized_orders[0]

        # Required fields
        assert sample_order.check_number is not None
        assert sample_order.category is not None
        assert sample_order.fulfillment_minutes >= 0
        assert isinstance(sample_order.order_time, datetime)
        assert sample_order.server is not None
        assert sample_order.shift is not None

        print(f"\nSample Order:")
        print(f"  Check #: {sample_order.check_number}")
        print(f"  Category: {sample_order.category}")
        print(f"  Fulfillment: {sample_order.fulfillment_minutes:.1f} min")
        print(f"  Server: {sample_order.server}")
        print(f"  Shift: {sample_order.shift}")
        print(f"  Table: {sample_order.table}")

    def test_categorization_logging(self, categorization_stage, context_with_dataframes, caplog):
        """Test that categorization logs appropriate messages."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        # Check logs contain categorization info
        assert 'order_categorization_started' in caplog.text
        assert 'order_categorization_complete' in caplog.text

    def test_performance(self, categorization_stage, context_with_dataframes):
        """Test that categorization stage completes quickly."""
        import time

        start = time.time()
        result = categorization_stage.execute(context_with_dataframes)
        duration = time.time() - start

        assert result.is_ok()

        categorized_orders = context_with_dataframes.get('categorized_orders')

        print(f"\nPerformance:")
        print(f"  Orders: {len(categorized_orders)}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Orders/sec: {len(categorized_orders) / duration:.0f}")

        # Should process quickly (< 2 seconds for ~100 orders)
        assert duration < 2.0, f"Stage too slow: {duration:.3f}s"

    def test_custom_categorizer(self):
        """Test that stage can accept custom categorizer."""
        custom_config = {
            'lobby_table_threshold': 3,
            'drive_thru_time_kitchen_max': 5
        }
        custom_categorizer = OrderCategorizer(config=custom_config)

        stage = OrderCategorizationStage(categorizer=custom_categorizer)

        assert stage.categorizer is custom_categorizer
        assert stage.categorizer.lobby_table_threshold == 3
        assert stage.categorizer.drive_thru_time_kitchen_max == 5

    def test_service_mix_realistic_distribution(self, categorization_stage, context_with_dataframes):
        """Test that service mix has realistic distribution."""
        result = categorization_stage.execute(context_with_dataframes)
        assert result.is_ok()

        service_mix = context_with_dataframes.get('service_mix')

        print(f"\nService Mix Distribution:")
        print(f"  Lobby: {service_mix['Lobby']:.1f}%")
        print(f"  Drive-Thru: {service_mix['Drive-Thru']:.1f}%")
        print(f"  ToGo: {service_mix['ToGo']:.1f}%")

        # No category should dominate (>95%)
        assert service_mix['Lobby'] < 95, "Lobby too dominant"
        assert service_mix['Drive-Thru'] < 95, "Drive-Thru too dominant"
        assert service_mix['ToGo'] < 95, "ToGo too dominant"

        # At least 2 categories should have orders
        categories_with_orders = sum([
            service_mix['Lobby'] > 0,
            service_mix['Drive-Thru'] > 0,
            service_mix['ToGo'] > 0
        ])
        assert categories_with_orders >= 2, "Should have at least 2 categories with orders"
