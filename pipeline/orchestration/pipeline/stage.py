"""
Pipeline Stage Protocol - Standard Interface for Pipeline Stages

Defines the contract that all pipeline stages must implement.
Enables testing stages in isolation and composing pipelines.

Usage:
    from pipeline.orchestration.pipeline import PipelineStage, PipelineContext
    from pipeline.services import Result

    class IngestionStage(PipelineStage):
        def execute(self, context: PipelineContext) -> Result[PipelineContext]:
            # Read data, process, store in context
            context.set("ingestion_result", result)
            return Result.ok(context)

    # Execute stage
    stage = IngestionStage()
    result = stage.execute(context)
"""

from typing import Protocol, Any, Dict
from dataclasses import dataclass

from pipeline.services import Result
from pipeline.orchestration.pipeline.context import PipelineContext


@dataclass
class PipelineStageResult:
    """
    Result from executing a pipeline stage.

    Wraps the Result[PipelineContext] with additional stage metadata.
    This allows stages to report metrics, warnings, etc.
    """

    # Core result
    context_result: Result[PipelineContext]
    """Result containing updated PipelineContext or error"""

    # Stage metadata
    stage_name: str
    """Name of stage that executed"""

    duration_seconds: float = 0.0
    """How long stage took to execute"""

    warnings: list[str] = None
    """Non-fatal warnings from stage execution"""

    metrics: Dict[str, Any] = None
    """Stage-specific metrics (records processed, errors, etc.)"""

    def __post_init__(self):
        """Initialize optional fields."""
        if self.warnings is None:
            self.warnings = []
        if self.metrics is None:
            self.metrics = {}

    def is_success(self) -> bool:
        """Check if stage succeeded."""
        return self.context_result.is_ok()

    def is_failure(self) -> bool:
        """Check if stage failed."""
        return self.context_result.is_err()

    def unwrap_context(self) -> PipelineContext:
        """
        Unwrap successful context.

        Returns:
            PipelineContext if stage succeeded

        Raises:
            Exception if stage failed
        """
        return self.context_result.unwrap()

    def summary(self) -> Dict[str, Any]:
        """
        Get stage execution summary.

        Returns:
            Dictionary with stage metrics
        """
        return {
            "stage_name": self.stage_name,
            "success": self.is_success(),
            "duration_seconds": self.duration_seconds,
            "warnings_count": len(self.warnings),
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


class PipelineStage(Protocol):
    """
    Protocol defining pipeline stage contract.

    All pipeline stages must implement this interface.
    This allows:
    - Testing stages in isolation
    - Composing pipelines from stages
    - Mocking stages for testing
    - Swapping stage implementations

    Example Implementation:
        class IngestionStage:
            def __init__(self, data_source: DataSource):
                self.data_source = data_source

            def execute(self, context: PipelineContext) -> Result[PipelineContext]:
                # 1. Read data from source
                data = self.data_source.read(context.date)

                # 2. Process data
                result = process_data(data)

                # 3. Store in context
                context.set("ingestion_result", result)

                # 4. Mark stage complete
                context.mark_stage_complete("ingestion")

                # 5. Return updated context
                return Result.ok(context)

        # Usage
        stage = IngestionStage(data_source)
        result = stage.execute(context)

        if result.is_ok():
            context = result.unwrap()
            # Proceed to next stage
        else:
            error = result.unwrap_err()
            # Handle error
    """

    def execute(self, context: PipelineContext) -> Result[PipelineContext]:
        """
        Execute pipeline stage.

        Takes PipelineContext as input, performs stage logic,
        updates context with results, returns updated context.

        Args:
            context: Pipeline execution context

        Returns:
            Result[PipelineContext]:
                - Success with updated context if stage succeeds
                - Failure with error if stage fails

        Stage Contract:
        1. Read inputs from context (context.get("input_key"))
        2. Perform stage logic
        3. Store outputs in context (context.set("output_key", value))
        4. Mark stage complete (context.mark_stage_complete("stage_name"))
        5. Return Result.ok(context) or Result.fail(error)

        Error Handling:
        - Return Result.fail(error) for fatal errors
        - Use context.set_metadata("warnings", [...]) for non-fatal warnings
        - Include context in error for debugging

        Example:
            def execute(self, context: PipelineContext) -> Result[PipelineContext]:
                try:
                    # Get input from previous stage
                    data = context.get("previous_stage_output")
                    if not data:
                        return Result.fail(PipelineError("Missing input data"))

                    # Perform stage logic
                    result = self.process(data)

                    # Store output for next stage
                    context.set("my_stage_output", result)

                    # Mark complete
                    context.mark_stage_complete("my_stage")

                    return Result.ok(context)

                except Exception as e:
                    return Result.fail(PipelineError(
                        message=f"Stage failed: {e}",
                        context={"stage": "my_stage", "error": str(e)}
                    ))
        """
        ...


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def execute_stage_with_timing(
    stage: PipelineStage,
    context: PipelineContext,
    stage_name: str
) -> PipelineStageResult:
    """
    Execute a stage and capture timing/metrics.

    Convenience function that wraps stage execution with timing,
    automatic stage completion marking, and metric collection.

    Args:
        stage: Pipeline stage to execute
        context: Pipeline context
        stage_name: Name of stage (for logging/metrics)

    Returns:
        PipelineStageResult with timing and metrics

    Example:
        stage = IngestionStage()
        result = execute_stage_with_timing(stage, context, "ingestion")

        if result.is_success():
            print(f"Ingestion took {result.duration_seconds}s")
            context = result.unwrap_context()
        else:
            print(f"Ingestion failed: {result.context_result.unwrap_err()}")
    """
    import time

    start_time = time.time()

    # Execute stage
    context_result = stage.execute(context)

    duration = time.time() - start_time

    # Mark stage complete if successful
    if context_result.is_ok():
        updated_context = context_result.unwrap()
        updated_context.mark_stage_complete(stage_name, duration)

    return PipelineStageResult(
        context_result=context_result,
        stage_name=stage_name,
        duration_seconds=duration
    )


def execute_pipeline(
    stages: list[tuple[str, PipelineStage]],
    context: PipelineContext
) -> Result[PipelineContext]:
    """
    Execute a pipeline of stages sequentially.

    Runs each stage in order, stopping if any stage fails.
    Automatically handles timing and stage completion marking.

    Args:
        stages: List of (stage_name, stage_instance) tuples
        context: Initial pipeline context

    Returns:
        Result[PipelineContext]:
            - Success with final context if all stages succeed
            - Failure with error from first failing stage

    Example:
        stages = [
            ("ingestion", IngestionStage(data_source)),
            ("processing", ProcessingStage(calculator)),
            ("storage", StorageStage(database)),
        ]

        result = execute_pipeline(stages, context)

        if result.is_ok():
            final_context = result.unwrap()
            print(f"Pipeline completed: {final_context.get_completed_stages()}")
            print(f"Total duration: {final_context.get_total_duration()}s")
        else:
            error = result.unwrap_err()
            print(f"Pipeline failed: {error}")
    """
    current_context = context

    for stage_name, stage in stages:
        # Execute stage with timing
        stage_result = execute_stage_with_timing(stage, current_context, stage_name)

        # Check if stage failed
        if stage_result.is_failure():
            return stage_result.context_result

        # Update context for next stage
        current_context = stage_result.unwrap_context()

    return Result.ok(current_context)
