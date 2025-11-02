"""Tests for DataValidator"""

import pytest
import pandas as pd
import numpy as np

from src.ingestion.data_validator import DataValidator
from src.core.errors import ValidationError


class TestDataValidator:
    """Test suite for DataValidator"""

    @pytest.fixture
    def validator(self):
        """Create DataValidator instance"""
        return DataValidator()

    @pytest.fixture
    def valid_labor_df(self):
        """Create valid labor DataFrame"""
        return pd.DataFrame({
            'Employee': ['Alice', 'Bob', 'Charlie'],
            'Job Title': ['Server', 'Cook', 'Server'],
            'In Date': ['01/15/25 9:00 AM', '01/15/25 10:00 AM', '01/15/25 11:00 AM'],
            'Out Date': ['01/15/25 5:00 PM', '01/15/25 6:00 PM', '01/15/25 7:00 PM'],
            'Total Hours': [8.0, 8.0, 8.0],
            'Payable Hours': [8.0, 8.0, 8.0]
        })

    @pytest.fixture
    def valid_sales_df(self):
        """Create valid sales DataFrame"""
        return pd.DataFrame({
            'Gross sales': [1000.0],
            'Sales discounts': [50.0],
            'Sales refunds': [25.0],
            'Net sales': [925.0]
        })

    @pytest.fixture
    def valid_orders_df(self):
        """Create valid orders DataFrame"""
        return pd.DataFrame({
            'Order #': ['001', '002', '003'],
            'Opened': ['01/15/25 12:00 PM', '01/15/25 1:00 PM', '01/15/25 2:00 PM'],
            'Server': ['Alice', 'Bob', 'Alice'],
            'Amount': [45.0, 67.5, 52.0]
        })

    # L1 Validation - Success cases

    def test_validate_l1_success(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test L1 validation with all valid data"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_ok()

    def test_validate_l1_extra_columns_allowed(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test that extra columns are allowed"""
        # Add extra column
        valid_labor_df['Extra Column'] = ['A', 'B', 'C']

        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_ok()

    def test_validate_l1_extra_dataframes_allowed(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test that extra DataFrames beyond required are allowed"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df,
            'extra': pd.DataFrame({'A': [1, 2]})  # Not in required columns map
        }

        result = validator.validate_l1(dfs)
        assert result.is_ok()

    # L1 Validation - Missing data type

    def test_validate_l1_missing_labor(self, validator, valid_sales_df, valid_orders_df):
        """Test L1 validation fails when labor data missing"""
        dfs = {
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert 'labor' in str(error).lower()

    def test_validate_l1_missing_sales(self, validator, valid_labor_df, valid_orders_df):
        """Test L1 validation fails when sales data missing"""
        dfs = {
            'labor': valid_labor_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        assert 'sales' in str(result.unwrap_err()).lower()

    def test_validate_l1_missing_orders(self, validator, valid_labor_df, valid_sales_df):
        """Test L1 validation fails when orders data missing"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        assert 'orders' in str(result.unwrap_err()).lower()

    def test_validate_l1_missing_all(self, validator):
        """Test L1 validation fails when all data missing"""
        result = validator.validate_l1({})
        assert result.is_err()

    # L1 Validation - Empty DataFrames

    def test_validate_l1_empty_labor(self, validator, valid_sales_df, valid_orders_df):
        """Test L1 validation fails when labor DataFrame is empty"""
        dfs = {
            'labor': pd.DataFrame(columns=['Employee', 'Job Title', 'In Date', 'Out Date', 'Total Hours', 'Payable Hours']),
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        error = result.unwrap_err()
        assert 'empty' in str(error).lower()
        assert 'labor' in str(error).lower()

    def test_validate_l1_empty_sales(self, validator, valid_labor_df, valid_orders_df):
        """Test L1 validation fails when sales DataFrame is empty"""
        dfs = {
            'labor': valid_labor_df,
            'sales': pd.DataFrame(columns=['Gross sales', 'Sales discounts', 'Sales refunds', 'Net sales']),
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        assert 'sales' in str(result.unwrap_err()).lower()

    # L1 Validation - Missing columns

    def test_validate_l1_missing_labor_column(self, validator, valid_sales_df, valid_orders_df):
        """Test L1 validation fails when labor is missing required column"""
        invalid_labor = pd.DataFrame({
            'Employee': ['Alice'],
            'Job Title': ['Server'],
            # Missing: In Date, Out Date, Total Hours, Payable Hours
        })

        dfs = {
            'labor': invalid_labor,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        error = result.unwrap_err()
        assert 'missing' in str(error).lower()
        assert 'columns' in str(error).lower()

    def test_validate_l1_missing_sales_column(self, validator, valid_labor_df, valid_orders_df):
        """Test L1 validation fails when sales is missing required column"""
        invalid_sales = pd.DataFrame({
            'Gross sales': [1000.0],
            # Missing: Sales discounts, Sales refunds, Net sales
        })

        dfs = {
            'labor': valid_labor_df,
            'sales': invalid_sales,
            'orders': valid_orders_df
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()
        assert 'net sales' in str(result.unwrap_err()).lower()

    def test_validate_l1_missing_orders_column(self, validator, valid_labor_df, valid_sales_df):
        """Test L1 validation fails when orders is missing required column"""
        invalid_orders = pd.DataFrame({
            'Order #': ['001'],
            # Missing: Opened, Server, Amount
        })

        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': invalid_orders
        }

        result = validator.validate_l1(dfs)
        assert result.is_err()

    # L2 Metrics - Basic functionality

    def test_calculate_l2_metrics_structure(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test L2 metrics returns correct structure"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)

        assert 'files_loaded' in metrics
        assert 'validation_level' in metrics
        assert 'parse_errors' in metrics
        assert 'warnings' in metrics
        assert 'row_counts' in metrics
        assert 'completeness' in metrics

    def test_calculate_l2_metrics_validation_level(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test L2 metrics reports correct validation level"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)
        assert metrics['validation_level'] == 'L2'

    def test_calculate_l2_metrics_files_loaded(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test L2 metrics tracks loaded files"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)
        assert set(metrics['files_loaded']) == {'labor', 'sales', 'orders'}

    def test_calculate_l2_metrics_row_counts(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test L2 metrics calculates row counts correctly"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)
        assert metrics['row_counts']['labor'] == 3
        assert metrics['row_counts']['sales'] == 1
        assert metrics['row_counts']['orders'] == 3

    # L2 Metrics - Completeness tracking

    def test_calculate_l2_metrics_completeness_perfect(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test completeness metrics with 100% complete data"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)

        # All required columns should have 100% completeness
        assert metrics['completeness']['labor']['Employee'] == 1.0
        assert metrics['completeness']['sales']['Net sales'] == 1.0
        assert metrics['overall_completeness'] == 1.0

    def test_calculate_l2_metrics_completeness_with_nulls(self, validator, valid_sales_df, valid_orders_df):
        """Test completeness metrics with missing values"""
        labor_with_nulls = pd.DataFrame({
            'Employee': ['Alice', None, 'Charlie'],
            'Job Title': ['Server', 'Cook', None],
            'In Date': ['01/15/25 9:00 AM', '01/15/25 10:00 AM', '01/15/25 11:00 AM'],
            'Out Date': ['01/15/25 5:00 PM', '01/15/25 6:00 PM', '01/15/25 7:00 PM'],
            'Total Hours': [8.0, 8.0, 8.0],
            'Payable Hours': [8.0, 8.0, 8.0]
        })

        dfs = {
            'labor': labor_with_nulls,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)

        # Employee: 2/3 complete = 0.667
        assert abs(metrics['completeness']['labor']['Employee'] - 0.667) < 0.01
        # Job Title: 2/3 complete = 0.667
        assert abs(metrics['completeness']['labor']['Job Title'] - 0.667) < 0.01

    def test_calculate_l2_metrics_warnings_low_completeness(self, validator, valid_sales_df, valid_orders_df):
        """Test warnings generated for low completeness"""
        labor_with_many_nulls = pd.DataFrame({
            'Employee': ['Alice', None, None, None, None],
            'Job Title': ['Server', 'Cook', 'Server', 'Cook', 'Server'],
            'In Date': [None, None, None, None, None],
            'Out Date': ['01/15/25 5:00 PM'] * 5,
            'Total Hours': [8.0] * 5,
            'Payable Hours': [8.0] * 5
        })

        dfs = {
            'labor': labor_with_many_nulls,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)

        # Should have warnings for low completeness (< 90%)
        assert len(metrics['warnings']) > 0
        warning_text = ' '.join(metrics['warnings']).lower()
        assert 'completeness' in warning_text

    # L2 Metrics - Timestamp quality

    def test_calculate_l2_metrics_timestamp_quality_perfect(self, validator, valid_labor_df, valid_sales_df, valid_orders_df):
        """Test timestamp quality with all valid timestamps"""
        dfs = {
            'labor': valid_labor_df,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)
        assert metrics['timestamp_quality'] == 1.0

    def test_calculate_l2_metrics_timestamp_quality_with_nulls(self, validator, valid_sales_df, valid_orders_df):
        """Test timestamp quality with missing timestamps"""
        labor_with_null_timestamps = pd.DataFrame({
            'Employee': ['Alice', 'Bob', 'Charlie'],
            'Job Title': ['Server', 'Cook', 'Server'],
            'In Date': ['01/15/25 9:00 AM', None, '01/15/25 11:00 AM'],
            'Out Date': ['01/15/25 5:00 PM', '01/15/25 6:00 PM', None],
            'Total Hours': [8.0, 8.0, 8.0],
            'Payable Hours': [8.0, 8.0, 8.0]
        })

        dfs = {
            'labor': labor_with_null_timestamps,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        metrics = validator.calculate_l2_metrics(dfs)

        # 4 valid timestamps out of 6 total = 0.667
        assert abs(metrics['timestamp_quality'] - 0.667) < 0.01

    def test_calculate_l2_metrics_timestamp_quality_empty_labor(self, validator, valid_sales_df, valid_orders_df):
        """Test timestamp quality with empty labor data"""
        empty_labor = pd.DataFrame(columns=['Employee', 'Job Title', 'In Date', 'Out Date', 'Total Hours', 'Payable Hours'])

        dfs = {
            'labor': empty_labor,
            'sales': valid_sales_df,
            'orders': valid_orders_df
        }

        # This will fail L1 validation, but test metrics calculation in isolation
        # Bypass L1 by only passing to calculate_l2_metrics
        metrics = validator.calculate_l2_metrics(dfs)

        # Empty DataFrame should have 0.0 timestamp quality
        assert metrics.get('timestamp_quality', 0.0) == 0.0

    # __repr__ test

    def test_repr(self, validator):
        """Test string representation"""
        repr_str = repr(validator)
        assert "DataValidator" in repr_str

    # Edge cases

    def test_calculate_l2_metrics_empty_dict(self, validator):
        """Test L2 metrics with empty input"""
        metrics = validator.calculate_l2_metrics({})

        assert metrics['files_loaded'] == []
        assert metrics['row_counts'] == {}
        assert metrics['overall_completeness'] == 0.0

    def test_calculate_l2_metrics_single_dataframe(self, validator, valid_labor_df):
        """Test L2 metrics with only one DataFrame"""
        dfs = {'labor': valid_labor_df}

        metrics = validator.calculate_l2_metrics(dfs)
        assert 'labor' in metrics['files_loaded']
        assert len(metrics['files_loaded']) == 1