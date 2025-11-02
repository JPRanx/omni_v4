"""
Pipeline Context - State Management for Pipeline Execution

Carries state, metadata, and configuration through pipeline stages.
Prevents coupling between stages while enabling state sharing.

Usage:
    from src.orchestration.pipeline import PipelineContext

    # Create context for processing
    context = PipelineContext(
        restaurant_code="SDR",
        date="2025-01-15",
        config=config_dict
    )

    # Stages can read/write state
    context.set("ingestion_result", result)
    ingestion = context.get("ingestion_result")

    # Track stage progress
    context.mark_stage_complete("ingestion")
    if context.is_stage_complete("ingestion"):
        # Proceed to next stage
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class PipelineContext:
    """
    Pipeline execution context.

    Carries state, metadata, and configuration through pipeline stages.
    Each stage can read from and write to the context without coupling.

    Thread Safety: NOT thread-safe (use one context per pipeline execution)
    Immutability: Mutable (stages modify state as they execute)
    """

    # ========================================================================
    # REQUIRED FIELDS (Pipeline Identity)
    # ========================================================================
    restaurant_code: str
    """Restaurant being processed (SDR, T12, TK9)"""

    date: str
    """Date being processed (YYYY-MM-DD format)"""

    config: Dict[str, Any]
    """Configuration dictionary (from ConfigLoader)"""

    # ========================================================================
    # OPTIONAL FIELDS (Execution Metadata)
    # ========================================================================
    pipeline_id: Optional[str] = None
    """Unique pipeline execution ID (for logging/tracing)"""

    environment: str = "dev"
    """Environment (dev, prod) - affects logging, validation"""

    dry_run: bool = False
    """If True, skip actual writes (useful for testing)"""

    # ========================================================================
    # STATE STORAGE (Shared Between Stages)
    # ========================================================================
    _state: Dict[str, Any] = field(default_factory=dict)
    """Internal state storage (use get/set methods)"""

    _completed_stages: List[str] = field(default_factory=list)
    """Stages that have completed successfully"""

    _stage_timings: Dict[str, float] = field(default_factory=dict)
    """Execution time for each stage (seconds)"""

    _metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata (tags, notes, etc.)"""

    # ========================================================================
    # STATE MANAGEMENT METHODS
    # ========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from pipeline state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            Value if found, otherwise default

        Example:
            ingestion_result = context.get("ingestion_result")
        """
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set value in pipeline state.

        Args:
            key: State key
            value: Value to store

        Example:
            context.set("ingestion_result", result)
        """
        self._state[key] = value

    def has(self, key: str) -> bool:
        """
        Check if key exists in pipeline state.

        Args:
            key: State key

        Returns:
            True if key exists, False otherwise

        Example:
            if context.has("ingestion_result"):
                # Process ingestion result
        """
        return key in self._state

    def get_all_state(self) -> Dict[str, Any]:
        """
        Get all pipeline state (for debugging/checkpointing).

        Returns:
            Dictionary of all state keys and values
        """
        return self._state.copy()

    # ========================================================================
    # STAGE TRACKING METHODS
    # ========================================================================

    def mark_stage_complete(self, stage_name: str, duration_seconds: float = 0.0) -> None:
        """
        Mark a stage as completed.

        Args:
            stage_name: Name of completed stage
            duration_seconds: How long stage took to execute

        Example:
            context.mark_stage_complete("ingestion", duration_seconds=2.5)
        """
        if stage_name not in self._completed_stages:
            self._completed_stages.append(stage_name)

        if duration_seconds > 0:
            self._stage_timings[stage_name] = duration_seconds

    def is_stage_complete(self, stage_name: str) -> bool:
        """
        Check if a stage has completed.

        Args:
            stage_name: Name of stage to check

        Returns:
            True if stage completed, False otherwise

        Example:
            if context.is_stage_complete("ingestion"):
                # Proceed to processing
        """
        return stage_name in self._completed_stages

    def get_completed_stages(self) -> List[str]:
        """
        Get list of completed stages (in order).

        Returns:
            List of stage names

        Example:
            completed = context.get_completed_stages()
            # ["ingestion", "processing"]
        """
        return self._completed_stages.copy()

    def get_stage_timing(self, stage_name: str) -> Optional[float]:
        """
        Get execution time for a stage.

        Args:
            stage_name: Name of stage

        Returns:
            Duration in seconds, or None if stage hasn't run

        Example:
            duration = context.get_stage_timing("ingestion")
            print(f"Ingestion took {duration}s")
        """
        return self._stage_timings.get(stage_name)

    def get_total_duration(self) -> float:
        """
        Get total pipeline execution time.

        Returns:
            Total seconds across all stages

        Example:
            total = context.get_total_duration()
            print(f"Pipeline took {total}s")
        """
        return sum(self._stage_timings.values())

    # ========================================================================
    # METADATA METHODS
    # ========================================================================

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value.

        Metadata is for tracking/debugging, not for stage communication.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            context.set_metadata("source", "manual_trigger")
            context.set_metadata("user", "admin")
        """
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.

        Args:
            key: Metadata key
            default: Default value if not found

        Returns:
            Metadata value or default
        """
        return self._metadata.get(key, default)

    def get_all_metadata(self) -> Dict[str, Any]:
        """Get all metadata (for logging/checkpointing)."""
        return self._metadata.copy()

    # ========================================================================
    # CHECKPOINT SUPPORT
    # ========================================================================

    def to_checkpoint(self) -> Dict[str, Any]:
        """
        Serialize context to checkpoint dictionary.

        Used for saving pipeline state to resume later.

        Returns:
            Dictionary with all context data

        Example:
            checkpoint = context.to_checkpoint()
            save_to_database(checkpoint)
        """
        return {
            "restaurant_code": self.restaurant_code,
            "date": self.date,
            "pipeline_id": self.pipeline_id,
            "environment": self.environment,
            "dry_run": self.dry_run,
            "state": self._state.copy(),
            "completed_stages": self._completed_stages.copy(),
            "stage_timings": self._stage_timings.copy(),
            "metadata": self._metadata.copy(),
            # Note: config not included (reload from YAML on resume)
        }

    @classmethod
    def from_checkpoint(cls, checkpoint: Dict[str, Any], config: Dict[str, Any]) -> "PipelineContext":
        """
        Restore context from checkpoint dictionary.

        Used for resuming pipeline from saved state.

        Args:
            checkpoint: Checkpoint dictionary (from to_checkpoint)
            config: Configuration dictionary (reload from YAML)

        Returns:
            Restored PipelineContext

        Example:
            checkpoint = load_from_database(pipeline_id)
            config = load_config(restaurant_code="SDR", env="dev")
            context = PipelineContext.from_checkpoint(checkpoint, config)
            # Resume from where we left off
        """
        context = cls(
            restaurant_code=checkpoint["restaurant_code"],
            date=checkpoint["date"],
            config=config,
            pipeline_id=checkpoint.get("pipeline_id"),
            environment=checkpoint.get("environment", "dev"),
            dry_run=checkpoint.get("dry_run", False),
        )

        # Restore state
        context._state = checkpoint.get("state", {})
        context._completed_stages = checkpoint.get("completed_stages", [])
        context._stage_timings = checkpoint.get("stage_timings", {})
        context._metadata = checkpoint.get("metadata", {})

        return context

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def __repr__(self) -> str:
        """String representation for debugging."""
        stages = ", ".join(self._completed_stages) or "none"
        return (
            f"PipelineContext(restaurant={self.restaurant_code}, "
            f"date={self.date}, "
            f"completed_stages=[{stages}])"
        )

    def summary(self) -> Dict[str, Any]:
        """
        Get pipeline execution summary.

        Returns:
            Dictionary with execution metrics

        Example:
            summary = context.summary()
            print(f"Processed {summary['restaurant_code']} on {summary['date']}")
            print(f"Completed stages: {summary['completed_stages']}")
            print(f"Total duration: {summary['total_duration']}s")
        """
        return {
            "restaurant_code": self.restaurant_code,
            "date": self.date,
            "pipeline_id": self.pipeline_id,
            "environment": self.environment,
            "completed_stages": self._completed_stages.copy(),
            "stage_count": len(self._completed_stages),
            "total_duration": self.get_total_duration(),
            "state_keys": list(self._state.keys()),
            "metadata": self._metadata.copy(),
        }
