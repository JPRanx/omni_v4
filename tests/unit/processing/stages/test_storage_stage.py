"""Tests for StorageStage"""

import pytest
from unittest.mock import Mock
from src.processing.stages.storage_stage import StorageStage
from src.infrastructure.database.in_memory_client import InMemoryDatabaseClient
from src.orchestration.pipeline.context import PipelineContext
from src.models.ingestion_result import IngestionResult
from src.models.processing_result import ProcessingResult
from src.models.storage_result import StorageResult
from src.core.errors import StorageError
from src.core.result import Result


class TestStorageStage:
    """Test suite for StorageStage"""

    @pytest.fixture
    def database_client(self):
        """Create InMemoryDatabaseClient instance"""
        return InMemoryDatabaseClient()

    @pytest.fixture
    def stage(self, database_client):
        """Create StorageStage instance"""
        return StorageStage(database_client)

    @pytest.fixture
    def ingestion_result(self):
        """Create valid IngestionResult"""
        result = IngestionResult.create(
            restaurant_code='SDR',
            business_date='2025-01-15',
            quality_level=1,
            toast_data_path='/tmp/sales.parquet',
            employee_data_path='/tmp/labor.parquet'
        )
        return result.unwrap()

    @pytest.fixture
    def processing_result(self):
        """Create valid ProcessingResult"""
        result = ProcessingResult.create(
            restaurant_code='SDR',
            business_date='2025-01-15',
            graded_timeslots_path='/tmp/graded_timeslots.parquet',
            shift_assignments_path='/tmp/shift_assignments.parquet',
            timeslot_count=2,
            shift_summary={'morning': 1, 'evening': 1}
        )
        return result.unwrap()

    @pytest.fixture
    def valid_context(self, ingestion_result):
        """Create PipelineContext with valid ingestion result"""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}
        )
        context.set('ingestion_result', ingestion_result)
        return context

    # Initialization tests

    def test_init(self, database_client):
        """Test StorageStage initialization"""
        stage = StorageStage(database_client)
        assert stage.database_client == database_client

    def test_repr(self, stage):
        """Test string representation"""
        repr_str = repr(stage)
        assert "StorageStage" in repr_str
        assert "database_client" in repr_str.lower()

    # Happy path tests

    def test_execute_success_ingestion_only(self, stage, database_client, valid_context):
        """Test successful execution with ingestion data only"""
        result = stage.execute(valid_context)

        assert result.is_ok()
        context = result.unwrap()

        # Check storage result is in context
        assert context.has('storage_result')
        storage_result = context.get('storage_result')
        assert isinstance(storage_result, StorageResult)
        assert storage_result.success is True

        # Check data was written to database
        assert database_client.get_row_count('daily_performance') == 1
        daily_perf = database_client.get_table_data('daily_performance')[0]
        assert daily_perf['restaurant_code'] == 'SDR'
        assert daily_perf['business_date'] == '2025-01-15'

    def test_execute_success_with_processing_result(
        self, stage, database_client, valid_context, processing_result
    ):
        """Test successful execution with processing data"""
        valid_context.set('processing_result', processing_result)

        result = stage.execute(valid_context)

        assert result.is_ok()
        context = result.unwrap()

        storage_result = context.get('storage_result')
        assert storage_result.success is True

        # Check all tables written
        assert 'daily_performance' in storage_result.tables_written
        assert 'processing_summary' in storage_result.tables_written

        # Check row counts
        assert storage_result.row_counts['daily_performance'] == 1
        assert storage_result.row_counts['processing_summary'] == 1

        # Verify database state
        assert database_client.get_row_count('daily_performance') == 1
        assert database_client.get_row_count('processing_summary') == 1

    def test_execute_with_learned_patterns(self, stage, database_client, valid_context):
        """Test execution with learned patterns"""
        # Create mock patterns
        mock_pattern_1 = Mock()
        mock_pattern_1.pattern_id = 'pattern_1'
        mock_pattern_1.restaurant_code = 'SDR'
        mock_pattern_1.pattern_type = 'rush_hour'
        mock_pattern_1.confidence = 0.95
        mock_pattern_1.last_updated = '2025-01-15T12:00:00'

        mock_pattern_2 = Mock()
        mock_pattern_2.pattern_id = 'pattern_2'
        mock_pattern_2.restaurant_code = 'SDR'
        mock_pattern_2.pattern_type = 'slow_period'
        mock_pattern_2.confidence = 0.88
        mock_pattern_2.last_updated = '2025-01-15T14:00:00'

        valid_context.set('learned_patterns', [mock_pattern_1, mock_pattern_2])

        result = stage.execute(valid_context)

        assert result.is_ok()
        context = result.unwrap()

        storage_result = context.get('storage_result')
        assert 'learned_patterns' in storage_result.tables_written
        assert storage_result.row_counts['learned_patterns'] == 2

        # Verify database state
        assert database_client.get_row_count('learned_patterns') == 2
        patterns = database_client.get_table_data('learned_patterns')
        assert patterns[0]['pattern_id'] == 'pattern_1'
        assert patterns[1]['pattern_id'] == 'pattern_2'

    def test_execute_all_data_types(
        self, stage, database_client, valid_context, processing_result
    ):
        """Test execution with all data types (ingestion + processing + patterns)"""
        valid_context.set('processing_result', processing_result)

        mock_pattern = Mock()
        mock_pattern.pattern_id = 'pattern_1'
        mock_pattern.restaurant_code = 'SDR'
        mock_pattern.pattern_type = 'test'
        mock_pattern.confidence = 0.9
        mock_pattern.last_updated = '2025-01-15T12:00:00'

        valid_context.set('learned_patterns', [mock_pattern])

        result = stage.execute(valid_context)

        assert result.is_ok()
        storage_result = result.unwrap().get('storage_result')

        # Check all tables written
        assert len(storage_result.tables_written) == 3
        assert 'daily_performance' in storage_result.tables_written
        assert 'processing_summary' in storage_result.tables_written
        assert 'learned_patterns' in storage_result.tables_written

        # Verify total rows
        assert storage_result.get_total_rows() == 3  # 1 + 1 + 1

    # Missing context tests

    def test_execute_missing_ingestion_result(self, stage):
        """Test error when ingestion_result is missing"""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}
        )
        # Don't set ingestion_result

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, StorageError)
        assert 'ingestion_result' in str(error).lower()

    def test_execute_invalid_ingestion_result_type(self, stage):
        """Test error when ingestion_result has wrong type"""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}
        )
        context.set('ingestion_result', 'not_a_dto')

        result = stage.execute(context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, StorageError)
        assert 'invalid type' in str(error).lower()

    # Transaction tests

    def test_transaction_commit_on_success(self, stage, database_client, valid_context):
        """Test that transaction is committed on success"""
        result = stage.execute(valid_context)

        assert result.is_ok()
        storage_result = result.unwrap().get('storage_result')

        # Transaction should be completed (not in active transactions)
        assert storage_result.transaction_id not in database_client.active_transactions

        # Data should be persisted
        assert database_client.get_row_count('daily_performance') == 1

    def test_transaction_rollback_on_error(self, stage, valid_context):
        """Test that transaction is rolled back on error"""
        # Create mock client that fails on insert
        mock_client = Mock()
        mock_client.begin_transaction.return_value = Result.ok('txn_123')
        mock_client.insert.return_value = Result.fail(
            StorageError("Insert failed")
        )
        mock_client.rollback_transaction.return_value = Result.ok(None)

        stage.database_client = mock_client

        result = stage.execute(valid_context)

        assert result.is_err()
        # Rollback should have been called
        mock_client.rollback_transaction.assert_called_once_with('txn_123')

    def test_begin_transaction_failure(self, stage, valid_context):
        """Test error when begin_transaction fails"""
        mock_client = Mock()
        mock_client.begin_transaction.return_value = Result.fail(
            StorageError("Failed to begin transaction")
        )

        stage.database_client = mock_client

        result = stage.execute(valid_context)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, StorageError)

    def test_commit_transaction_failure(self, stage, valid_context):
        """Test error when commit_transaction fails"""
        mock_client = Mock()
        mock_client.begin_transaction.return_value = Result.ok('txn_123')
        mock_client.insert.return_value = Result.ok(1)
        mock_client.commit_transaction.return_value = Result.fail(
            StorageError("Commit failed")
        )
        mock_client.rollback_transaction.return_value = Result.ok(None)

        stage.database_client = mock_client

        result = stage.execute(valid_context)

        assert result.is_err()
        # Rollback should be attempted after commit failure
        mock_client.rollback_transaction.assert_called_once_with('txn_123')

    # Database error tests

    def test_insert_failure_ingestion_data(self, stage, valid_context):
        """Test error when inserting ingestion data fails"""
        mock_client = Mock()
        mock_client.begin_transaction.return_value = Result.ok('txn_123')
        mock_client.insert.return_value = Result.fail(
            StorageError("Insert failed")
        )
        mock_client.rollback_transaction.return_value = Result.ok(None)

        stage.database_client = mock_client

        result = stage.execute(valid_context)

        assert result.is_err()
        mock_client.rollback_transaction.assert_called_once()

    def test_insert_failure_processing_data(
        self, stage, valid_context, processing_result
    ):
        """Test error when inserting processing data fails"""
        valid_context.set('processing_result', processing_result)

        mock_client = Mock()
        mock_client.begin_transaction.return_value = Result.ok('txn_123')
        # First insert (ingestion) succeeds
        mock_client.insert.return_value = Result.ok(1)
        # Second insert (processing) fails
        mock_client.insert_many.return_value = Result.fail(
            StorageError("Insert many failed")
        )
        mock_client.rollback_transaction.return_value = Result.ok(None)

        stage.database_client = mock_client

        result = stage.execute(valid_context)

        assert result.is_err()
        mock_client.rollback_transaction.assert_called_once()

    # Edge cases

    def test_empty_learned_patterns_list(self, stage, database_client, valid_context):
        """Test execution with empty learned_patterns list"""
        valid_context.set('learned_patterns', [])

        result = stage.execute(valid_context)

        assert result.is_ok()
        storage_result = result.unwrap().get('storage_result')

        # Learned patterns should not be in tables_written
        assert 'learned_patterns' not in storage_result.tables_written
        assert database_client.get_row_count('learned_patterns') == 0

    def test_processing_result_minimal(self, stage, database_client, valid_context):
        """Test execution with minimal processing result"""
        minimal_processing_result = ProcessingResult.create(
            restaurant_code='SDR',
            business_date='2025-01-15',
            graded_timeslots_path='/tmp/empty_timeslots.parquet',
            shift_assignments_path='/tmp/empty_shifts.parquet',
            timeslot_count=0
        ).unwrap()

        valid_context.set('processing_result', minimal_processing_result)

        result = stage.execute(valid_context)

        assert result.is_ok()
        storage_result = result.unwrap().get('storage_result')

        # Both ingestion and processing summary should be written
        assert len(storage_result.tables_written) == 2
        assert 'daily_performance' in storage_result.tables_written
        assert 'processing_summary' in storage_result.tables_written

    def test_multiple_executions_same_stage(
        self, stage, database_client, ingestion_result
    ):
        """Test multiple executions with same stage instance"""
        # First execution
        context1 = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}
        )
        context1.set('ingestion_result', ingestion_result)

        result1 = stage.execute(context1)
        assert result1.is_ok()

        # Second execution (different context)
        ingestion_result2 = IngestionResult.create(
            restaurant_code='T12',
            business_date='2025-01-16',
            quality_level=1,
            toast_data_path='/tmp/sales2.parquet'
        ).unwrap()

        context2 = PipelineContext(
            restaurant_code='T12',
            date='2025-01-16',
            config={}
        )
        context2.set('ingestion_result', ingestion_result2)

        result2 = stage.execute(context2)
        assert result2.is_ok()

        # Both should be in database
        assert database_client.get_row_count('daily_performance') == 2

    def test_storage_result_metadata(self, stage, valid_context):
        """Test StorageResult contains correct metadata"""
        result = stage.execute(valid_context)

        assert result.is_ok()
        storage_result = result.unwrap().get('storage_result')

        # Check DTO fields
        assert storage_result.restaurant_code == 'SDR'
        assert storage_result.business_date == '2025-01-15'
        assert storage_result.success is True
        assert storage_result.transaction_id is not None
        assert storage_result.storage_timestamp is not None

    def test_context_preserved_on_success(self, stage, valid_context):
        """Test that existing context data is preserved after success"""
        valid_context.set('existing_key', 'existing_value')

        result = stage.execute(valid_context)

        assert result.is_ok()
        context = result.unwrap()

        # New data added
        assert context.has('storage_result')

        # Existing data preserved
        assert context.get('existing_key') == 'existing_value'
        assert context.get('ingestion_result') is not None

    def test_context_unchanged_on_error(self, stage):
        """Test that context is not modified when execution fails"""
        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-01-15',
            config={}
        )
        context.set('existing_key', 'existing_value')
        # Missing ingestion_result will cause error

        result = stage.execute(context)

        assert result.is_err()
        # storage_result should not be added
        assert not context.has('storage_result')
        # Existing data preserved
        assert context.get('existing_key') == 'existing_value'

    # Protocol compliance test

    def test_pipeline_stage_protocol_compliance(self, stage):
        """Test that StorageStage has execute method with correct signature"""
        assert hasattr(stage, 'execute')
        assert callable(stage.execute)

        # Test that execute returns Result[PipelineContext]
        context = PipelineContext(restaurant_code='SDR', date='2025-01-15', config={})
        result = stage.execute(context)
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')
