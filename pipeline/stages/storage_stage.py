"""
StorageStage - Pipeline stage for persisting data to database.

Handles writing ingestion results, processing results, and learned patterns
to the Supabase database with transactional support.
"""

from typing import Optional
import time

from pipeline.services.result import Result
from pipeline.services.errors import StorageError
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.infrastructure.database.database_client import DatabaseClient
from pipeline.models.storage_result import StorageResult
from pipeline.models.ingestion_result import IngestionResult
from pipeline.models.processing_result import ProcessingResult
from pipeline.infrastructure.logging import get_logger

logger = get_logger(__name__)


class StorageStage:
    """
    Pipeline stage for storing data to database.

    Reads ingestion and processing results from context, writes to database
    with transaction support, and produces a StorageResult DTO.
    """

    def __init__(self, database_client: DatabaseClient):
        """
        Initialize storage stage.

        Args:
            database_client: DatabaseClient implementation for storage operations
        """
        self.database_client = database_client

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute storage stage.

        Expected context inputs:
        - ingestion_result: IngestionResult DTO (required)
        - processing_result: ProcessingResult DTO (optional)
        - learned_patterns: List[Pattern] (optional)

        Context outputs:
        - storage_result: StorageResult DTO

        Args:
            context: Pipeline context with results to store

        Returns:
            Result[PipelineContext]: Updated context or error
        """
        start_time = time.time()

        # Bind context
        restaurant = context.get('restaurant', 'UNKNOWN')
        date = context.get('date', 'UNKNOWN')
        bound_logger = logger.bind(restaurant=restaurant, date=date)
        bound_logger.info("storage_started")

        # Extract required inputs
        ingestion_result = context.get('ingestion_result')

        if ingestion_result is None:
            bound_logger.error("storage_failed", reason="ingestion_result not found in context")
            return Result.fail(
                StorageError(
                    "Missing required context key: 'ingestion_result'",
                    context={'available_keys': list(context._state.keys())}
                )
            )

        if not isinstance(ingestion_result, IngestionResult):
            bound_logger.error("storage_failed",
                             reason=f"ingestion_result has wrong type ({type(ingestion_result).__name__})")
            return Result.fail(
                StorageError(
                    "Invalid type for 'ingestion_result': expected IngestionResult",
                    context={'actual_type': type(ingestion_result).__name__}
                )
            )

        # Extract optional inputs
        processing_result = context.get('processing_result')
        learned_patterns = context.get('learned_patterns')

        # Begin transaction
        transaction_result = self.database_client.begin_transaction()
        if transaction_result.is_err():
            bound_logger.error("storage_failed", reason="Failed to begin transaction")
            return Result.fail(transaction_result.unwrap_err())

        transaction_id = transaction_result.unwrap()
        bound_logger.info("transaction_started", transaction_id=transaction_id)

        # Track what we've written
        tables_written = []
        row_counts = {}
        errors = []

        try:
            # Write ingestion data
            ingestion_write_result = self._write_ingestion_data(ingestion_result)
            if ingestion_write_result.is_err():
                # Rollback and fail
                bound_logger.warning("transaction_rollback", reason="Ingestion write failed", transaction_id=transaction_id)
                self.database_client.rollback_transaction(transaction_id)
                return Result.fail(ingestion_write_result.unwrap_err())

            ingestion_tables, ingestion_counts = ingestion_write_result.unwrap()
            tables_written.extend(ingestion_tables)
            row_counts.update(ingestion_counts)

            # Write processing data if present
            if processing_result is not None:
                processing_write_result = self._write_processing_data(processing_result)
                if processing_write_result.is_err():
                    # Rollback and fail
                    bound_logger.warning("transaction_rollback", reason="Processing write failed", transaction_id=transaction_id)
                    self.database_client.rollback_transaction(transaction_id)
                    return Result.fail(processing_write_result.unwrap_err())

                processing_tables, processing_counts = processing_write_result.unwrap()
                tables_written.extend(processing_tables)
                row_counts.update(processing_counts)

            # Write learned patterns if present
            if learned_patterns is not None and len(learned_patterns) > 0:
                patterns_write_result = self._write_learned_patterns(learned_patterns)
                if patterns_write_result.is_err():
                    # Rollback and fail
                    bound_logger.warning("transaction_rollback", reason="Pattern write failed", transaction_id=transaction_id)
                    self.database_client.rollback_transaction(transaction_id)
                    return Result.fail(patterns_write_result.unwrap_err())

                pattern_tables, pattern_counts = patterns_write_result.unwrap()
                tables_written.extend(pattern_tables)
                row_counts.update(pattern_counts)

            # Commit transaction
            commit_result = self.database_client.commit_transaction(transaction_id)
            if commit_result.is_err():
                # Try to rollback
                bound_logger.warning("transaction_rollback", reason="Commit failed", transaction_id=transaction_id)
                self.database_client.rollback_transaction(transaction_id)
                return Result.fail(commit_result.unwrap_err())

        except Exception as e:
            # Unexpected error - rollback
            bound_logger.error("transaction_rollback", reason=f"Unexpected error: {str(e)}", transaction_id=transaction_id)
            self.database_client.rollback_transaction(transaction_id)
            return Result.fail(
                StorageError(
                    f"Unexpected error during storage: {str(e)}",
                    context={'transaction_id': transaction_id, 'error': str(e)}
                )
            )

        # Create StorageResult DTO
        storage_result_create = StorageResult.create(
            restaurant_code=ingestion_result.restaurant_code,
            business_date=ingestion_result.business_date,
            tables_written=tables_written,
            row_counts=row_counts,
            transaction_id=transaction_id,
            success=True,
            errors=errors
        )

        if storage_result_create.is_err():
            return Result.fail(storage_result_create.unwrap_err())

        storage_result = storage_result_create.unwrap()

        # Store result in context
        context.set('storage_result', storage_result)

        # Calculate duration and log success
        duration_ms = (time.time() - start_time) * 1000
        total_rows = sum(row_counts.values())

        bound_logger.info("storage_complete",
                         transaction_id=transaction_id,
                         tables_written=len(tables_written),
                         total_rows=total_rows,
                         duration_ms=round(duration_ms, 0))

        return Result.ok(context)

    def _write_ingestion_data(
        self,
        ingestion_result: IngestionResult
    ) -> Result[tuple[list[str], dict[str, int]]]:
        """
        Write ingestion data to database.

        Args:
            ingestion_result: IngestionResult DTO

        Returns:
            Result[tuple]: (tables_written, row_counts) or error
        """
        tables_written = []
        row_counts = {}

        # Write daily_performance table
        daily_performance_data = {
            'restaurant_code': ingestion_result.restaurant_code,
            'business_date': ingestion_result.business_date,
            'quality_level': ingestion_result.quality_level,
            'toast_data_path': ingestion_result.toast_data_path or '',
            'employee_data_path': ingestion_result.employee_data_path or '',
        }

        insert_result = self.database_client.insert('daily_performance', daily_performance_data)
        if insert_result.is_err():
            return Result.fail(insert_result.unwrap_err())

        tables_written.append('daily_performance')
        row_counts['daily_performance'] = insert_result.unwrap()

        return Result.ok((tables_written, row_counts))

    def _write_processing_data(
        self,
        processing_result: ProcessingResult
    ) -> Result[tuple[list[str], dict[str, int]]]:
        """
        Write processing data to database.

        Note: ProcessingResult uses file paths. For now, we store the metadata
        about the processing rather than loading and re-storing the actual data.
        In Week 9+, we'll implement proper file loading and storage.

        Args:
            processing_result: ProcessingResult DTO

        Returns:
            Result[tuple]: (tables_written, row_counts) or error
        """
        tables_written = []
        row_counts = {}

        # Write processing summary data
        processing_summary_data = {
            'restaurant_code': processing_result.restaurant_code,
            'business_date': processing_result.business_date,
            'graded_timeslots_path': processing_result.graded_timeslots_path,
            'shift_assignments_path': processing_result.shift_assignments_path,
            'timeslot_count': processing_result.timeslot_count,
            'processing_timestamp': processing_result.processing_timestamp
        }

        insert_result = self.database_client.insert('processing_summary', processing_summary_data)
        if insert_result.is_err():
            return Result.fail(insert_result.unwrap_err())

        tables_written.append('processing_summary')
        row_counts['processing_summary'] = insert_result.unwrap()

        return Result.ok((tables_written, row_counts))

    def _write_learned_patterns(
        self,
        learned_patterns: list
    ) -> Result[tuple[list[str], dict[str, int]]]:
        """
        Write learned patterns to database.

        Args:
            learned_patterns: List of Pattern objects

        Returns:
            Result[tuple]: (tables_written, row_counts) or error
        """
        tables_written = []
        row_counts = {}

        # Convert patterns to database format using to_dict() method
        # This works for both DailyLaborPattern and HourlyServicePattern (future)
        pattern_data = [
            pattern.to_dict()
            for pattern in learned_patterns
        ]

        insert_result = self.database_client.insert_many('learned_patterns', pattern_data)
        if insert_result.is_err():
            return Result.fail(insert_result.unwrap_err())

        tables_written.append('learned_patterns')
        row_counts['learned_patterns'] = insert_result.unwrap()

        return Result.ok((tables_written, row_counts))

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"StorageStage(database_client={self.database_client})"
