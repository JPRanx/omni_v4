"""
Integration tests for multi-restaurant Toast data ingestion.

Tests that IngestionStage handles variations across all three restaurants:
- SDR (Sandra's Mexican Cuisine)
- T12 (Tink-A-Tako #12)
- TK9 (Tink-A-Tako #9)
"""

import pytest
import pandas as pd
from pathlib import Path
import json

from pipeline.ingestion.csv_data_source import CSVDataSource
from pipeline.ingestion.data_validator import DataValidator
from pipeline.stages.ingestion_stage import IngestionStage
from pipeline.orchestration.pipeline.context import PipelineContext


class TestMultiRestaurantIngestion:
    """Test suite for multi-restaurant ingestion"""

    @pytest.fixture
    def sample_data_path(self):
        """Path to sample data directory"""
        return Path("tests/fixtures/sample_data/2025-10-20")

    @pytest.mark.parametrize("restaurant", ["SDR", "T12", "TK9"])
    def test_ingestion_handles_all_restaurants(self, restaurant, sample_data_path):
        """Test IngestionStage handles each restaurant's Toast configuration"""
        data_path = sample_data_path / restaurant

        # Skip if data not available
        if not data_path.exists():
            pytest.skip(f"Sample data not available for {restaurant}")

        # Create stage
        validator = DataValidator()
        stage = IngestionStage(validator)

        # Create context
        context = PipelineContext(
            restaurant_code=restaurant,
            date='2025-10-20',
            config={}
        )
        context.set('date', '2025-10-20')
        context.set('restaurant', restaurant)
        context.set('data_path', str(data_path))

        # Execute
        result = stage.execute(context)

        # Should handle restaurant-specific variations
        assert result.is_ok(), f"Failed for {restaurant}: {result.unwrap_err()}"

        # Verify ingestion result
        context = result.unwrap()
        ingestion_result = context.get('ingestion_result')
        assert ingestion_result is not None
        assert ingestion_result.restaurant_code == restaurant

    def test_document_restaurant_schema_differences(self, sample_data_path):
        """Document schema differences between restaurants"""
        differences = {}

        for restaurant in ["SDR", "T12", "TK9"]:
            path = sample_data_path / restaurant

            if not path.exists():
                continue

            # Get all CSV files
            csv_files = sorted([f.name for f in path.glob("*.csv")])

            differences[restaurant] = {
                'file_count': len(csv_files),
                'files': csv_files,
                'schemas': {}
            }

            # Check schemas for key files
            key_files = {
                'TimeEntries': 'TimeEntries_2025_10_20.csv',
                'OrderDetails': 'OrderDetails_2025_10_20.csv',
                'Net_sales': 'Net sales summary.csv'
            }

            for file_type, filename in key_files.items():
                file_path = path / filename
                if file_path.exists():
                    try:
                        df = pd.read_csv(file_path, nrows=1)
                        differences[restaurant]['schemas'][file_type] = df.columns.tolist()
                    except Exception as e:
                        differences[restaurant]['schemas'][file_type] = f"Error: {str(e)}"

        # Print comparison report
        print("\n" + "="*80)
        print("RESTAURANT CONFIGURATION COMPARISON")
        print("="*80)
        print(json.dumps(differences, indent=2))
        print("="*80)

        # Verify all restaurants have data
        assert len(differences) == 3, "Expected data for all 3 restaurants"

    def test_all_restaurants_have_required_files(self, sample_data_path):
        """Verify all restaurants have the required CSV files"""
        required_files = [
            'TimeEntries_2025_10_20.csv',
            'Net sales summary.csv',
            'OrderDetails_2025_10_20.csv'
        ]

        for restaurant in ["SDR", "T12", "TK9"]:
            path = sample_data_path / restaurant

            if not path.exists():
                pytest.skip(f"Sample data not available for {restaurant}")

            for required_file in required_files:
                file_path = path / required_file
                assert file_path.exists(), f"{restaurant} missing {required_file}"

    @pytest.mark.parametrize("restaurant", ["SDR", "T12", "TK9"])
    def test_time_entries_schema_consistency(self, restaurant, sample_data_path):
        """Test that TimeEntries has consistent schema across restaurants"""
        data_path = sample_data_path / restaurant
        time_entries_path = data_path / 'TimeEntries_2025_10_20.csv'

        if not time_entries_path.exists():
            pytest.skip(f"TimeEntries not available for {restaurant}")

        df = pd.read_csv(time_entries_path)

        # Check for required columns
        required_columns = ['Employee', 'Job Title', 'Total Hours', 'Payable Hours']
        for col in required_columns:
            assert col in df.columns, f"{restaurant} TimeEntries missing {col}"

    @pytest.mark.parametrize("restaurant", ["SDR", "T12", "TK9"])
    def test_sales_summary_schema_consistency(self, restaurant, sample_data_path):
        """Test that Net sales summary has consistent schema"""
        data_path = sample_data_path / restaurant
        sales_path = data_path / 'Net sales summary.csv'

        if not sales_path.exists():
            pytest.skip(f"Net sales summary not available for {restaurant}")

        df = pd.read_csv(sales_path)

        # Check for required columns
        required_columns = ['Gross sales', 'Net sales']
        for col in required_columns:
            assert col in df.columns, f"{restaurant} Net sales summary missing {col}"

    @pytest.mark.parametrize("restaurant", ["SDR", "T12", "TK9"])
    def test_order_details_schema_consistency(self, restaurant, sample_data_path):
        """Test that OrderDetails has consistent schema"""
        data_path = sample_data_path / restaurant
        orders_path = data_path / 'OrderDetails_2025_10_20.csv'

        if not orders_path.exists():
            pytest.skip(f"OrderDetails not available for {restaurant}")

        df = pd.read_csv(orders_path)

        # Check for required columns
        required_columns = ['Order #', 'Opened', 'Amount']
        for col in required_columns:
            assert col in df.columns, f"{restaurant} OrderDetails missing {col}"

    def test_cross_restaurant_data_volume_comparison(self, sample_data_path):
        """Compare data volume across restaurants"""
        volumes = {}

        for restaurant in ["SDR", "T12", "TK9"]:
            path = sample_data_path / restaurant

            if not path.exists():
                continue

            volumes[restaurant] = {}

            # Count rows in key files
            key_files = {
                'TimeEntries': 'TimeEntries_2025_10_20.csv',
                'OrderDetails': 'OrderDetails_2025_10_20.csv',
            }

            for file_type, filename in key_files.items():
                file_path = path / filename
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    volumes[restaurant][file_type] = len(df)

        print("\n" + "="*80)
        print("DATA VOLUME COMPARISON")
        print("="*80)
        print(json.dumps(volumes, indent=2))
        print("="*80)

        # Verify we have data for all restaurants
        assert len(volumes) == 3, "Expected volume data for all 3 restaurants"
