"""Tests for IngestionStage"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.processing.stages.ingestion_stage import IngestionStage
from src.ingestion.data_validator import DataValidator
from src.ingestion.csv_data_source import CSVDataSource
from src.orchestration.pipeline.context import PipelineContext
from src.core.errors import IngestionError, ValidationError
from src.models.ingestion_result import IngestionResult


class TestIngestionStage:
    """Test suite for IngestionStage"""

    @pytest.fixture
    def validator(self):
        """Create DataValidator instance"""
        return DataValidator()

    @pytest.fixture
    def stage(self, validator):
        """Create IngestionStage instance"""
        return IngestionStage(validator)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test CSV files"""
        temp_path = tempfile.mkdtemp()
        temp_dir = Path(temp_path)

        # Create valid test CSV files
        labor_df = pd.DataFrame({
            'Employee': ['Alice', 'Bob'],
            'Job Title': ['Server', 'Cook'],
            'In Date': ['01/15/25 9:00 AM', '01/15/25 10:00 AM'],
            'Out Date': ['01/15/25 5:00 PM', '01/15/25 6:00 PM'],
            'Total Hours': [8.0, 8.0],
            'Payable Hours': [8.0, 8.0]
        })
        labor_df.to_csv(temp_dir / 'TimeEntries.csv', index=False)

        sales_df = pd.DataFrame({
            'Gross sales': [1000.0],
            'Sales discounts': [50.0],
            'Sales refunds': [25.0],
            'Net sales': [925.0]
        })
        sales_df.to_csv(temp_dir / 'Net_sales_summary.csv', index=False)

        orders_df = pd.DataFrame({
            'Order #': ['001', '002'],
            'Opened': ['01/15/25 12:00 PM', '01/15/25 1:00 PM'],
            'Server': ['Alice', 'Bob'],
            'Amount': [45.0, 67.5]
        })
        orders_df.to_csv(temp_dir / 'OrderDetails.csv', index=False)

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_path)

    @pytest.fixture
    def valid_context(self, temp_dir):
        """Create PipelineContext with valid inputs"""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}  # Empty config for testing
        )
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))
        return context

    # Initialization tests

    def test_init(self, validator):
        """Test IngestionStage initialization"""
        stage = IngestionStage(validator)
        assert stage.validator == validator

    def test_required_files_defined(self, stage):
        """Test that REQUIRED_FILES are properly defined"""
        assert 'labor' in stage.REQUIRED_FILES
        assert 'sales' in stage.REQUIRED_FILES
        assert 'orders' in stage.REQUIRED_FILES
        assert stage.REQUIRED_FILES['labor'] == 'TimeEntries.csv'
        assert stage.REQUIRED_FILES['sales'] == 'Net_sales_summary.csv'
        assert stage.REQUIRED_FILES['orders'] == 'OrderDetails.csv'

    # Happy path tests

    def test_execute_success(self, stage, valid_context):
        """Test successful execution of ingestion stage"""
        result = stage.execute(valid_context)

        assert result.is_ok()
        context = result.unwrap()

        # Check outputs are in context
        assert context.has('ingestion_result')
        assert context.has('sales')
        assert context.has('raw_dataframes')

    def test_execute_produces_ingestion_result(self, stage, valid_context):
        """Test that execution produces valid IngestionResult"""
        result = stage.execute(valid_context)
        context = result.unwrap()

        ingestion_result = context.get('ingestion_result')
        assert isinstance(ingestion_result, IngestionResult)
        assert ingestion_result.business_date == '2025-01-15'
        assert ingestion_result.restaurant_code == 'SDR'
        assert ingestion_result.quality_level == 1

    def test_execute_extracts_sales_correctly(self, stage, valid_context):
        """Test that sales amount is extracted correctly"""
        result = stage.execute(valid_context)
        context = result.unwrap()

        sales = context.get('sales')
        assert sales == 925.0

    def test_execute_stores_raw_dataframes(self, stage, valid_context):
        """Test that raw DataFrames are stored in context"""
        result = stage.execute(valid_context)
        context = result.unwrap()

        dfs = context.get('raw_dataframes')
        assert 'labor' in dfs
        assert 'sales' in dfs
        assert 'orders' in dfs
        assert isinstance(dfs['labor'], pd.DataFrame)
        assert len(dfs['labor']) == 2  # 2 employees

    def test_execute_quality_metrics_included(self, stage, valid_context):
        """Test that quality metrics are calculated and included"""
        result = stage.execute(valid_context)
        context = result.unwrap()

        ingestion_result = context.get('ingestion_result')
        metadata = ingestion_result.metadata

        assert 'files_loaded' in metadata
        assert 'validation_level' in metadata
        assert metadata['validation_level'] == 'L2'

    # Missing context input tests

    def test_execute_missing_date(self, stage, temp_dir):
        """Test error when 'date' is missing from context"""
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))
        # Don't set 'date'

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert 'date' in str(error).lower()

    def test_execute_missing_restaurant(self, stage, temp_dir):
        """Test error when 'restaurant' is missing from context"""
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('data_path', str(temp_dir))
        # Don't set 'restaurant'

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'restaurant' in str(error).lower()

    def test_execute_missing_data_path(self, stage):
        """Test error when 'data_path' is missing from context"""
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        # Don't set 'data_path'

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert 'data_path' in str(error).lower()

    # Missing file tests

    def test_execute_missing_labor_file(self, stage, temp_dir):
        """Test error when TimeEntries.csv is missing"""
        # Remove labor file
        (temp_dir / 'TimeEntries.csv').unlink()

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert 'timeentries' in str(error).lower()

    def test_execute_missing_sales_file(self, stage, temp_dir):
        """Test error when Net_sales_summary.csv is missing"""
        (temp_dir / 'Net_sales_summary.csv').unlink()

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        assert 'net_sales_summary' in str(result.unwrap_err()).lower()

    def test_execute_missing_orders_file(self, stage, temp_dir):
        """Test error when OrderDetails.csv is missing"""
        (temp_dir / 'OrderDetails.csv').unlink()

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        assert 'orderdetails' in str(result.unwrap_err()).lower()

    # L1 Validation failure tests

    def test_execute_l1_validation_failure_missing_column(self, stage, temp_dir):
        """Test L1 validation failure when required column is missing"""
        # Create invalid labor file (missing required columns)
        invalid_labor = pd.DataFrame({
            'Employee': ['Alice'],
            'Job Title': ['Server']
            # Missing: In Date, Out Date, Total Hours, Payable Hours
        })
        invalid_labor.to_csv(temp_dir / 'TimeEntries.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)

    def test_execute_l1_validation_failure_empty_dataframe(self, stage, temp_dir):
        """Test L1 validation failure when DataFrame is empty"""
        # Create empty labor file
        empty_labor = pd.DataFrame(columns=['Employee', 'Job Title', 'In Date', 'Out Date', 'Total Hours', 'Payable Hours'])
        empty_labor.to_csv(temp_dir / 'TimeEntries.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert 'empty' in str(error).lower()

    # Sales extraction tests

    def test_execute_sales_extraction_error_missing_column(self, stage, temp_dir):
        """Test error when Net sales column is missing"""
        invalid_sales = pd.DataFrame({
            'Gross sales': [1000.0]
            # Missing: Net sales
        })
        invalid_sales.to_csv(temp_dir / 'Net_sales_summary.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        # This should fail L1 validation first
        assert result.is_err()

    def test_execute_sales_extraction_non_numeric(self, stage, temp_dir):
        """Test error when sales value is not numeric"""
        invalid_sales = pd.DataFrame({
            'Gross sales': [1000.0],
            'Sales discounts': [50.0],
            'Sales refunds': [25.0],
            'Net sales': ['invalid']  # Non-numeric value
        })
        invalid_sales.to_csv(temp_dir / 'Net_sales_summary.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)

    # Temp file creation tests

    @patch('src.processing.stages.ingestion_stage.Path.mkdir')
    def test_execute_temp_dir_creation_failure(self, mock_mkdir, stage, valid_context):
        """Test error when temp directory creation fails"""
        mock_mkdir.side_effect = PermissionError("Permission denied")

        result = stage.execute(valid_context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)

    # Integration with PipelineContext

    def test_execute_context_unchanged_on_error(self, stage, temp_dir):
        """Test that context is not modified when execution fails"""
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))
        context.set('existing_key', 'existing_value')

        # Remove a required file to cause failure
        (temp_dir / 'TimeEntries.csv').unlink()

        result = stage.execute(context)

        # Execution should fail
        assert result.is_err()

        # Existing key should still be there
        assert context.get('existing_key') == 'existing_value'
        # New keys should not be added
        assert not context.has('ingestion_result')
        assert not context.has('sales')

    def test_execute_preserves_existing_context_data(self, stage, valid_context):
        """Test that existing context data is preserved after execution"""
        valid_context.set('existing_key', 'existing_value')

        result = stage.execute(valid_context)
        context = result.unwrap()

        # New data should be added
        assert context.has('ingestion_result')
        assert context.has('sales')

        # Existing data should be preserved
        assert context.get('existing_key') == 'existing_value'

    # Edge cases

    def test_execute_with_large_csv_files(self, stage, temp_dir):
        """Test execution with large CSV files"""
        # Create large DataFrames
        large_labor = pd.DataFrame({
            'Employee': [f'Employee_{i}' for i in range(1000)],
            'Job Title': ['Server'] * 1000,
            'In Date': ['01/15/25 9:00 AM'] * 1000,
            'Out Date': ['01/15/25 5:00 PM'] * 1000,
            'Total Hours': [8.0] * 1000,
            'Payable Hours': [8.0] * 1000
        })
        large_labor.to_csv(temp_dir / 'TimeEntries.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_ok()
        context = result.unwrap()
        dfs = context.get('raw_dataframes')
        assert len(dfs['labor']) == 1000

    def test_execute_with_special_characters_in_data(self, stage, temp_dir):
        """Test execution with special characters in CSV data"""
        special_labor = pd.DataFrame({
            'Employee': ['José García', 'François Müller'],
            'Job Title': ['Server', 'Cook'],
            'In Date': ['01/15/25 9:00 AM', '01/15/25 10:00 AM'],
            'Out Date': ['01/15/25 5:00 PM', '01/15/25 6:00 PM'],
            'Total Hours': [8.0, 8.0],
            'Payable Hours': [8.0, 8.0]
        })
        special_labor.to_csv(temp_dir / 'TimeEntries.csv', index=False)

        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(temp_dir))

        result = stage.execute(context)

        assert result.is_ok()

    # __repr__ test

    def test_repr(self, stage):
        """Test string representation"""
        repr_str = repr(stage)
        assert "IngestionStage" in repr_str
        assert "validator" in repr_str.lower()

    # Protocol compliance test

    def test_pipeline_stage_protocol_compliance(self, stage):
        """Test that IngestionStage has execute method with correct signature"""
        assert hasattr(stage, 'execute')
        assert callable(stage.execute)

        # Test that execute returns Result[PipelineContext]
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        context.set('date', '2025-01-15')
        context.set('restaurant', 'SDR')
        context.set('data_path', '/invalid/path')

        result = stage.execute(context)
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')