"""
Comprehensive Integration Tests for Full Pipeline

Tests the complete end-to-end pipeline execution with real data from
tests/fixtures/sample_data/2025-10-20/{SDR,T12,TK9}/

Test Categories:
1. Full Pipeline Execution (3 tests - one per restaurant)
2. Error Handling (5 tests)
3. Data Validation (4 tests)
4. Multi-Restaurant Batch Processing (1 test)
5. Pattern Accumulation (2 tests)

Total: 15 integration tests
"""

import pytest
import pandas as pd
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

from pipeline.services.result import Result
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.stages.ingestion_stage import IngestionStage
from pipeline.stages.processing_stage import ProcessingStage
from pipeline.stages.pattern_learning_stage import PatternLearningStage
from pipeline.stages.storage_stage import StorageStage
from pipeline.infrastructure.database.in_memory_client import InMemoryDatabaseClient
from pipeline.services.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage
from pipeline.services.patterns.daily_labor_manager import DailyLaborPatternManager
from pipeline.infrastructure.config.loader import ConfigLoader
from pipeline.ingestion.data_validator import DataValidator
from pipeline.services.labor_calculator import LaborCalculator
from pipeline.models.labor_dto import LaborDTO
from pipeline.models.ingestion_result import IngestionResult


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def test_data_path():
    """Path to test fixtures."""
    return Path(__file__).parent.parent / "fixtures" / "sample_data" / "2025-10-20"


@pytest.fixture
def database_client():
    """Fresh in-memory database for each test."""
    return InMemoryDatabaseClient()


@pytest.fixture
def pattern_storage():
    """Fresh in-memory daily labor pattern storage for each test."""
    return InMemoryDailyLaborPatternStorage()


@pytest.fixture
def pattern_manager(pattern_storage):
    """Daily labor pattern manager with in-memory storage."""
    config_loader = ConfigLoader()
    config = config_loader.load_config(restaurant_code="SDR", env="dev")
    return DailyLaborPatternManager(storage=pattern_storage, config=config)


@pytest.fixture
def config_loader():
    """Config loader for tests."""
    return ConfigLoader()


@pytest.fixture
def data_validator():
    """Data validator for tests."""
    return DataValidator()


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temp files after each test."""
    yield
    # Clean up any temp directories created during tests
    temp_root = Path("C:/temp/omni")
    if temp_root.exists():
        try:
            shutil.rmtree(temp_root)
        except Exception:
            pass  # Best effort cleanup


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def extract_labor_dto_from_payroll(
    payroll_df: pd.DataFrame,
    restaurant_code: str,
    business_date: str
) -> Result[LaborDTO]:
    """
    Extract LaborDTO from PayrollExport DataFrame.

    Args:
        payroll_df: PayrollExport DataFrame with employee payroll data
        restaurant_code: Restaurant code
        business_date: Business date

    Returns:
        Result[LaborDTO]: Labor DTO or error
    """
    try:
        # Validate required columns
        required_cols = ['Regular Hours', 'Overtime Hours', 'Total Pay']
        missing_cols = [col for col in required_cols if col not in payroll_df.columns]
        if missing_cols:
            return Result.fail(
                ValueError(f"Missing required columns: {missing_cols}")
            )

        # Calculate totals
        total_regular_hours = payroll_df['Regular Hours'].fillna(0).sum()
        total_overtime_hours = payroll_df['Overtime Hours'].fillna(0).sum()
        total_hours = total_regular_hours + total_overtime_hours
        total_cost = payroll_df['Total Pay'].fillna(0).sum()
        employee_count = len(payroll_df)

        # Get breakdown if available
        total_regular_cost = payroll_df.get('Regular Pay', pd.Series([0])).fillna(0).sum()
        total_overtime_cost = payroll_df.get('Overtime Pay', pd.Series([0])).fillna(0).sum()

        # Calculate average hourly rate
        avg_hourly_rate = total_cost / total_hours if total_hours > 0 else 0.0

        # Create LaborDTO
        return LaborDTO.create(
            restaurant_code=restaurant_code,
            business_date=business_date,
            total_hours_worked=float(total_hours),
            total_labor_cost=float(total_cost),
            employee_count=employee_count,
            total_regular_hours=float(total_regular_hours),
            total_overtime_hours=float(total_overtime_hours),
            total_regular_cost=float(total_regular_cost),
            total_overtime_cost=float(total_overtime_cost),
            average_hourly_rate=float(avg_hourly_rate)
        )

    except Exception as e:
        return Result.fail(ValueError(f"Failed to extract LaborDTO: {e}"))


def run_full_pipeline(
    restaurant_code: str,
    date: str,
    data_path: Path,
    database_client: InMemoryDatabaseClient,
    pattern_manager: DailyLaborPatternManager,
    config_loader: ConfigLoader,
    data_validator: DataValidator
) -> Result[PipelineContext]:
    """
    Run the complete pipeline for a single restaurant.

    Returns:
        Result[PipelineContext]: Final context with all results or error
    """
    try:
        # Load configuration
        config = config_loader.load_config(restaurant_code=restaurant_code, env="dev")

        # Create pipeline context
        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config=config,
            environment="dev"
        )

        # Set required context keys
        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(data_path / restaurant_code))

        # STAGE 1: INGESTION
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)

        if result.is_err():
            return result

        context = result.unwrap()

        # STAGE 2: CREATE LABOR DTO
        raw_dfs = context.get('raw_dataframes')
        if raw_dfs and 'payroll' in raw_dfs:
            labor_dto_result = extract_labor_dto_from_payroll(
                raw_dfs['payroll'],
                restaurant_code,
                date
            )

            if labor_dto_result.is_err():
                return labor_dto_result

            labor_dto = labor_dto_result.unwrap()
            context.set('labor_dto', labor_dto)

        # STAGE 3: PROCESSING
        calculator = LaborCalculator(config)
        processing_stage = ProcessingStage(calculator)

        result = processing_stage.execute(context)

        if result.is_err():
            return result

        context = result.unwrap()

        # STAGE 4: PATTERN LEARNING
        pattern_learning_stage = PatternLearningStage(pattern_manager)

        result = pattern_learning_stage.execute(context)

        if result.is_err():
            return result

        context = result.unwrap()

        # STAGE 5: STORAGE
        # Create mock IngestionResult for storage
        ingestion_dto = IngestionResult.create(
            restaurant_code=restaurant_code,
            business_date=date,
            quality_level=1,
            toast_data_path=f"C:/temp/omni/{restaurant_code}/{date}/sales.parquet"
        ).unwrap()

        context.set('ingestion_result', ingestion_dto)

        storage_stage = StorageStage(database_client)
        result = storage_stage.execute(context)

        if result.is_err():
            return result

        context = result.unwrap()

        return Result.ok(context)

    except Exception as e:
        return Result.fail(Exception(f"Pipeline failed: {e}"))


# ==============================================================================
# TEST CLASS 1: FULL PIPELINE EXECUTION
# ==============================================================================

class TestFullPipelineExecution:
    """Test complete pipeline execution with real data."""

    def test_sdr_full_pipeline(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Test complete pipeline for SDR restaurant."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        # Verify success
        assert result.is_ok(), f"Pipeline failed: {result.unwrap_err()}"

        context = result.unwrap()

        # Verify ingestion outputs
        assert context.get('sales') > 0, "Sales should be positive"
        assert context.get('total_payroll_cost') > 0, "Payroll cost should be positive"

        raw_dfs = context.get('raw_dataframes')
        assert raw_dfs is not None, "Raw dataframes should exist"
        assert 'payroll' in raw_dfs, "Payroll data should exist"
        assert len(raw_dfs['payroll']) == 17, "SDR should have 17 employees"

        # Verify processing outputs
        labor_metrics = context.get('labor_metrics')
        assert labor_metrics is not None, "Labor metrics should exist"
        assert labor_metrics.labor_percentage > 0, "Labor percentage should be positive"
        assert 40 < labor_metrics.labor_percentage < 50, "SDR labor should be ~46.9%"

        # Verify pattern learning outputs
        learned_patterns = context.get('learned_patterns')
        assert learned_patterns is not None, "Learned patterns should exist"
        assert len(learned_patterns) > 0, "Should have at least one pattern"

        # Verify storage outputs
        storage_result = context.get('storage_result')
        assert storage_result is not None, "Storage result should exist"
        assert storage_result.get_total_rows() > 0, "Should have written rows"

    def test_t12_full_pipeline(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Test complete pipeline for T12 restaurant."""
        restaurant_code = "T12"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        # Verify success
        assert result.is_ok(), f"Pipeline failed: {result.unwrap_err()}"

        context = result.unwrap()

        # Verify ingestion outputs
        assert context.get('sales') > 0, "Sales should be positive"
        assert context.get('total_payroll_cost') > 0, "Payroll cost should be positive"

        raw_dfs = context.get('raw_dataframes')
        assert raw_dfs is not None, "Raw dataframes should exist"
        assert 'payroll' in raw_dfs, "Payroll data should exist"
        assert len(raw_dfs['payroll']) == 20, "T12 should have 20 employees"

        # Verify processing outputs
        labor_metrics = context.get('labor_metrics')
        assert labor_metrics is not None, "Labor metrics should exist"
        assert labor_metrics.labor_percentage > 0, "Labor percentage should be positive"

        # Verify pattern learning outputs
        learned_patterns = context.get('learned_patterns')
        assert learned_patterns is not None, "Learned patterns should exist"
        assert len(learned_patterns) > 0, "Should have at least one pattern"

        # Verify storage outputs
        storage_result = context.get('storage_result')
        assert storage_result is not None, "Storage result should exist"
        assert storage_result.get_total_rows() > 0, "Should have written rows"

    def test_tk9_full_pipeline(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Test complete pipeline for TK9 restaurant."""
        restaurant_code = "TK9"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        # Verify success
        assert result.is_ok(), f"Pipeline failed: {result.unwrap_err()}"

        context = result.unwrap()

        # Verify ingestion outputs
        assert context.get('sales') > 0, "Sales should be positive"
        assert context.get('total_payroll_cost') > 0, "Payroll cost should be positive"

        raw_dfs = context.get('raw_dataframes')
        assert raw_dfs is not None, "Raw dataframes should exist"
        assert 'payroll' in raw_dfs, "Payroll data should exist"
        assert len(raw_dfs['payroll']) == 9, "TK9 should have 9 employees"

        # Verify processing outputs
        labor_metrics = context.get('labor_metrics')
        assert labor_metrics is not None, "Labor metrics should exist"
        assert labor_metrics.labor_percentage > 0, "Labor percentage should be positive"

        # Verify pattern learning outputs
        learned_patterns = context.get('learned_patterns')
        assert learned_patterns is not None, "Learned patterns should exist"
        assert len(learned_patterns) > 0, "Should have at least one pattern"

        # Verify storage outputs
        storage_result = context.get('storage_result')
        assert storage_result is not None, "Storage result should exist"
        assert storage_result.get_total_rows() > 0, "Should have written rows"


# ==============================================================================
# TEST CLASS 2: ERROR HANDLING
# ==============================================================================

class TestErrorHandling:
    """Test error handling and resilience."""

    def test_missing_csv_files(self, database_client, data_validator):
        """Test pipeline handles missing CSV files gracefully."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create context with non-existent path
        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config={},
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', "/nonexistent/path/to/data")

        # Run ingestion stage
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)

        # Should fail with appropriate error
        assert result.is_err(), "Should fail when CSV files are missing"
        error = result.unwrap_err()
        error_str = str(error).lower()
        assert "not found" in error_str or "does not exist" in error_str or "could not find" in error_str

    def test_invalid_csv_data(self, tmp_path, database_client, data_validator):
        """Test pipeline handles invalid CSV data."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create directory with invalid CSV
        data_dir = tmp_path / restaurant_code
        data_dir.mkdir()

        # Create TimeEntries CSV with missing required columns
        invalid_csv = data_dir / "TimeEntries_2025_10_20.csv"
        invalid_csv.write_text("InvalidColumn1,InvalidColumn2\nvalue1,value2\n")

        # Create Net sales summary (minimal valid)
        sales_csv = data_dir / "Net sales summary.csv"
        sales_csv.write_text("Net sales\n100.00\n")

        # Create OrderDetails (minimal valid)
        orders_csv = data_dir / "OrderDetails_2025_10_20.csv"
        orders_csv.write_text("Order #,Opened,Amount\n1,2025-10-20,10.00\n")

        # Create context
        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config={},
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(data_dir))

        # Run ingestion stage
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)

        # Should fail validation
        assert result.is_err(), "Should fail validation with invalid CSV"
        error = result.unwrap_err()
        assert "missing" in str(error).lower() or "required" in str(error).lower()

    def test_missing_payroll_export(
        self,
        tmp_path,
        database_client,
        data_validator,
        test_data_path
    ):
        """Test pipeline continues when PayrollExport is missing."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Copy SDR data to temp directory
        source_dir = test_data_path / restaurant_code
        dest_dir = tmp_path / restaurant_code
        dest_dir.mkdir()

        # Copy all files except PayrollExport
        for file in source_dir.glob("*.csv"):
            if "PayrollExport" not in file.name:
                shutil.copy(file, dest_dir / file.name)

        # Create context
        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config={},
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(dest_dir))

        # Run ingestion stage
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)

        # Should succeed but with zero payroll cost
        assert result.is_ok(), f"Should succeed without PayrollExport: {result.unwrap_err() if result.is_err() else ''}"

        context = result.unwrap()
        payroll_cost = context.get('total_payroll_cost', 0.0)
        assert payroll_cost == 0.0, "Payroll cost should be 0 when PayrollExport missing"

    def test_database_write_failure(
        self,
        test_data_path,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Test storage handles database failures."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create mock database that fails on write
        mock_db = Mock(spec=InMemoryDatabaseClient)
        mock_db.insert.side_effect = Exception("Database write failed")
        mock_db.insert_many.side_effect = Exception("Database write failed")
        mock_db.begin_transaction.return_value = Result.ok("txn_123")
        mock_db.rollback_transaction.return_value = Result.ok(None)

        # Run pipeline until storage stage
        config = config_loader.load_config(restaurant_code=restaurant_code, env="dev")

        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config=config,
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(test_data_path / restaurant_code))

        # Run ingestion
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)
        assert result.is_ok()
        context = result.unwrap()

        # Create labor DTO
        raw_dfs = context.get('raw_dataframes')
        if raw_dfs and 'payroll' in raw_dfs:
            labor_dto_result = extract_labor_dto_from_payroll(
                raw_dfs['payroll'],
                restaurant_code,
                date
            )
            assert labor_dto_result.is_ok()
            context.set('labor_dto', labor_dto_result.unwrap())

        # Run processing
        calculator = LaborCalculator(config)
        processing_stage = ProcessingStage(calculator)
        result = processing_stage.execute(context)
        assert result.is_ok()
        context = result.unwrap()

        # Add ingestion result for storage
        ingestion_dto = IngestionResult.create(
            restaurant_code=restaurant_code,
            business_date=date,
            quality_level=1,
            toast_data_path=f"C:/temp/omni/{restaurant_code}/{date}/sales.parquet"
        ).unwrap()
        context.set('ingestion_result', ingestion_dto)

        # Run storage with mock database
        storage_stage = StorageStage(mock_db)
        result = storage_stage.execute(context)

        # Should return error
        assert result.is_err(), "Storage should fail when database write fails"
        error = result.unwrap_err()
        error_str = str(error).lower()
        assert "write" in error_str or "database" in error_str or "insert" in error_str or "failed" in error_str

    def test_pattern_learning_failure(
        self,
        test_data_path,
        database_client,
        config_loader,
        data_validator
    ):
        """Test pipeline continues when pattern learning fails."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create mock pattern manager that fails
        mock_pattern_manager = Mock(spec=DailyLaborPatternManager)
        # Return a failure Result instead of raising an exception
        from pipeline.services.errors import PatternError
        mock_pattern_manager.learn_pattern.return_value = Result.fail(
            PatternError(message="Pattern learning failed", context={})
        )

        # Run pipeline until pattern learning
        config = config_loader.load_config(restaurant_code=restaurant_code, env="dev")

        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config=config,
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(test_data_path / restaurant_code))

        # Run ingestion
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)
        assert result.is_ok()
        context = result.unwrap()

        # Create labor DTO
        raw_dfs = context.get('raw_dataframes')
        if raw_dfs and 'payroll' in raw_dfs:
            labor_dto_result = extract_labor_dto_from_payroll(
                raw_dfs['payroll'],
                restaurant_code,
                date
            )
            assert labor_dto_result.is_ok()
            context.set('labor_dto', labor_dto_result.unwrap())

        # Run processing
        calculator = LaborCalculator(config)
        processing_stage = ProcessingStage(calculator)
        result = processing_stage.execute(context)
        assert result.is_ok()
        context = result.unwrap()

        # Run pattern learning with mock that fails
        pattern_learning_stage = PatternLearningStage(mock_pattern_manager)
        result = pattern_learning_stage.execute(context)

        # Pattern learning stage is resilient - it continues with warnings instead of failing
        assert result.is_ok(), "Pattern learning stage should be resilient and continue"

        context = result.unwrap()
        warnings = context.get('pattern_warnings', [])
        learned_patterns = context.get('learned_patterns', [])

        # Should have warnings about the failure
        assert len(warnings) > 0, "Should have warnings about pattern learning failure"
        assert any("failed" in w.lower() for w in warnings), f"Warnings should mention failure: {warnings}"

        # Should have no learned patterns since mock failed
        assert len(learned_patterns) == 0, "Should have no learned patterns when manager fails"


# ==============================================================================
# TEST CLASS 3: DATA VALIDATION
# ==============================================================================

class TestDataValidation:
    """Test data validation throughout pipeline."""

    def test_correct_employee_count(self, test_data_path, data_validator):
        """Verify correct employee count extracted."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create context
        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config={},
            environment="dev"
        )

        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(test_data_path / restaurant_code))

        # Run ingestion
        ingestion_stage = IngestionStage(data_validator)
        result = ingestion_stage.execute(context)

        assert result.is_ok()
        context = result.unwrap()

        # Verify employee count
        raw_dfs = context.get('raw_dataframes')
        assert raw_dfs is not None
        assert 'payroll' in raw_dfs

        employee_count = len(raw_dfs['payroll'])
        assert employee_count == 17, f"SDR should have 17 employees, got {employee_count}"

    def test_correct_labor_percentage(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Verify correct labor percentage calculation."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        assert result.is_ok()
        context = result.unwrap()

        # Verify labor percentage
        labor_metrics = context.get('labor_metrics')
        assert labor_metrics is not None

        labor_percentage = labor_metrics.labor_percentage

        # Allow 1% tolerance for floating point and rounding
        assert 45.9 <= labor_percentage <= 47.9, \
            f"SDR labor should be ~46.9%, got {labor_percentage:.1f}%"

    def test_valid_pattern_objects(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Verify patterns have valid attributes."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        assert result.is_ok()
        context = result.unwrap()

        # Verify patterns
        learned_patterns = context.get('learned_patterns')
        assert learned_patterns is not None
        assert len(learned_patterns) > 0

        # Check first pattern has required attributes (DailyLaborPattern)
        pattern = learned_patterns[0]
        assert hasattr(pattern, 'restaurant_code')
        assert hasattr(pattern, 'day_of_week')
        assert hasattr(pattern, 'expected_labor_percentage')
        assert hasattr(pattern, 'expected_total_hours')
        assert hasattr(pattern, 'observations')
        assert hasattr(pattern, 'confidence')

        # Verify values are valid
        assert pattern.restaurant_code == restaurant_code
        assert pattern.observations > 0
        assert 0 <= pattern.confidence <= 1
        assert pattern.expected_labor_percentage > 0
        assert pattern.expected_total_hours > 0

    def test_correct_storage_row_counts(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Verify correct row counts in storage."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Run full pipeline
        result = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        assert result.is_ok()
        context = result.unwrap()

        # Verify storage result
        storage_result = context.get('storage_result')
        assert storage_result is not None

        # Check row counts
        row_counts = storage_result.row_counts
        assert len(row_counts) > 0, "Should have written to at least one table"

        total_rows = storage_result.get_total_rows()
        assert total_rows > 0, "Should have written at least one row"

        # Verify specific tables were written
        tables_written = storage_result.tables_written
        # Just verify we wrote to some tables (names may vary)
        assert len(tables_written) > 0, "Should write to at least one table"


# ==============================================================================
# TEST CLASS 4: MULTI-RESTAURANT BATCH PROCESSING
# ==============================================================================

class TestMultiRestaurantProcessing:
    """Test batch processing multiple restaurants."""

    def test_process_all_restaurants(
        self,
        test_data_path,
        database_client,
        pattern_manager,
        config_loader,
        data_validator
    ):
        """Process all 3 restaurants in batch."""
        restaurants = ['SDR', 'T12', 'TK9']
        date = "2025-10-20"
        results = {}

        # Process each restaurant
        for restaurant in restaurants:
            result = run_full_pipeline(
                restaurant,
                date,
                test_data_path,
                database_client,
                pattern_manager,
                config_loader,
                data_validator
            )

            results[restaurant] = {
                'success': result.is_ok(),
                'context': result.unwrap() if result.is_ok() else None,
                'error': result.unwrap_err() if result.is_err() else None
            }

        # Verify all 3 succeeded
        assert len(results) == 3, "Should process all 3 restaurants"

        for restaurant, result in results.items():
            assert result['success'], f"{restaurant} failed: {result['error']}"

        # Verify isolation - each restaurant has its own data
        employee_counts = {}
        for restaurant, result in results.items():
            context = result['context']
            raw_dfs = context.get('raw_dataframes')
            employee_counts[restaurant] = len(raw_dfs['payroll'])

        # Verify expected employee counts
        assert employee_counts['SDR'] == 17, "SDR should have 17 employees"
        assert employee_counts['T12'] == 20, "T12 should have 20 employees"
        assert employee_counts['TK9'] == 9, "TK9 should have 9 employees"

        # Verify all patterns are stored without conflicts
        # Get patterns for each restaurant
        all_patterns = []
        for restaurant in restaurants:
            patterns_result = pattern_manager.storage.list_patterns(restaurant_code=restaurant)
            assert patterns_result.is_ok(), f"Failed to list patterns for {restaurant}"
            all_patterns.extend(patterns_result.unwrap())

        # Should have patterns from all 3 restaurants
        pattern_restaurants = set(p.restaurant_code for p in all_patterns)
        assert len(pattern_restaurants) == 3, f"Should have patterns from all 3 restaurants, got {pattern_restaurants}"
        assert pattern_restaurants == {'SDR', 'T12', 'TK9'}


# ==============================================================================
# TEST CLASS 5: PATTERN ACCUMULATION
# ==============================================================================

class TestPatternAccumulation:
    """Test pattern learning over multiple days."""

    def test_pattern_updates_on_second_observation(
        self,
        test_data_path,
        database_client,
        pattern_storage,
        config_loader,
        data_validator
    ):
        """Verify pattern updates when observed twice."""
        restaurant_code = "SDR"
        date = "2025-10-20"

        # Create pattern manager with shared storage
        config = config_loader.load_config(restaurant_code=restaurant_code, env="dev")
        pattern_manager = DailyLaborPatternManager(storage=pattern_storage, config=config)

        # Run pipeline first time
        result1 = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        assert result1.is_ok()
        context1 = result1.unwrap()

        patterns1 = context1.get('learned_patterns')
        assert len(patterns1) > 0

        # Get first pattern details
        pattern1 = patterns1[0]
        observations1 = pattern1.observations
        confidence1 = pattern1.confidence

        # Run pipeline second time (same data to simulate pattern accumulation)
        result2 = run_full_pipeline(
            restaurant_code,
            date,
            test_data_path,
            database_client,
            pattern_manager,
            config_loader,
            data_validator
        )

        assert result2.is_ok()
        context2 = result2.unwrap()

        patterns2 = context2.get('learned_patterns')
        assert len(patterns2) > 0

        # Get same pattern after second observation
        pattern2 = patterns2[0]
        observations2 = pattern2.observations
        confidence2 = pattern2.confidence

        # Verify observations increased
        assert observations2 > observations1, \
            f"Observations should increase: {observations1} -> {observations2}"

        # Verify confidence increased (or stayed at 1.0 if already max)
        assert confidence2 >= confidence1, \
            f"Confidence should increase or stay same: {confidence1} -> {confidence2}"

    def test_ema_calculation(
        self,
        test_data_path,
        pattern_storage,
        config_loader
    ):
        """Verify exponential moving average works."""
        from pipeline.models.pattern import Pattern

        restaurant_code = "SDR"

        # Create initial pattern with known values using proper field names
        initial_pattern_result = Pattern.create(
            restaurant_code=restaurant_code,
            service_type="Lobby",
            day_of_week=0,  # Monday
            hour=18,  # 6 PM
            expected_volume=100.0,
            expected_staffing=10.0,
            observations=1,
            confidence=0.1
        )

        assert initial_pattern_result.is_ok()
        initial_pattern = initial_pattern_result.unwrap()

        # Store it
        pattern_storage.save_pattern(initial_pattern)

        # Use with_updated_prediction to test EMA
        new_volume = 150.0  # Different from initial 100.0
        new_staffing = 15.0  # Different from initial 10.0

        updated_pattern = initial_pattern.with_updated_prediction(
            new_volume=new_volume,
            new_staffing=new_staffing,
            learning_rate=0.3
        )

        # Verify EMA calculation
        # New value should be between old and new (weighted average)
        assert initial_pattern.expected_volume < updated_pattern.expected_volume < new_volume, \
            f"Volume should be EMA between old ({initial_pattern.expected_volume}) and new ({new_volume}), got {updated_pattern.expected_volume}"

        assert initial_pattern.expected_staffing < updated_pattern.expected_staffing < new_staffing, \
            f"Staffing should be EMA between old ({initial_pattern.expected_staffing}) and new ({new_staffing}), got {updated_pattern.expected_staffing}"

        # Verify observations increased
        assert updated_pattern.observations == 2, "Observations should increase to 2"

        # Verify confidence increased
        assert updated_pattern.confidence > initial_pattern.confidence, \
            "Confidence should increase with more observations"
