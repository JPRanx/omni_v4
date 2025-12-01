"""
Pipeline Metrics Tracker

Collects and tracks metrics during pipeline execution.
Provides performance insights, business metrics, and operational data.

Metrics Categories:
1. Counters: pipelines_started, pipelines_completed, pipelines_failed
2. Timers: stage_duration_ms (per stage)
3. Gauges: labor_percentage, files_processed, rows_written
4. Business: labor_cost_alerts, patterns_learned

Usage:
    from pipeline.infrastructure.logging.pipeline_metrics import PipelineMetrics

    metrics = PipelineMetrics()
    metrics.pipeline_started()

    with metrics.time_stage("ingestion"):
        # Execute stage
        pass

    metrics.record_labor_percentage(46.9)
    metrics.pipeline_completed()

    # Export metrics
    data = metrics.to_dict()
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from contextlib import contextmanager
import time


@dataclass
class PipelineMetrics:
    """
    Metrics collected during pipeline execution.

    Thread Safety: NOT thread-safe (use per-pipeline instance)
    """

    # Counters
    pipelines_started: int = 0
    pipelines_completed: int = 0
    pipelines_failed: int = 0

    # Stage timers (ms)
    ingestion_duration_ms: float = 0.0
    processing_duration_ms: float = 0.0
    pattern_learning_duration_ms: float = 0.0
    storage_duration_ms: float = 0.0
    total_duration_ms: float = 0.0

    # Gauges (latest values)
    current_labor_percentage: float = 0.0
    files_processed: int = 0
    rows_written: int = 0
    employees_processed: int = 0

    # Business metrics
    labor_cost_alerts: int = 0
    patterns_learned: int = 0

    # Timestamps
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Internal state
    _stage_start_time: Optional[float] = field(default=None, repr=False)
    _pipeline_start_time: Optional[float] = field(default=None, repr=False)

    def pipeline_started(self):
        """Mark pipeline start."""
        self.pipelines_started += 1
        self.started_at = datetime.utcnow().isoformat()
        self._pipeline_start_time = time.time()

    def pipeline_completed(self):
        """Mark pipeline completion."""
        self.pipelines_completed += 1
        self.completed_at = datetime.utcnow().isoformat()

        if self._pipeline_start_time:
            self.total_duration_ms = (time.time() - self._pipeline_start_time) * 1000

    def pipeline_failed(self):
        """Mark pipeline failure."""
        self.pipelines_failed += 1
        self.completed_at = datetime.utcnow().isoformat()

        if self._pipeline_start_time:
            self.total_duration_ms = (time.time() - self._pipeline_start_time) * 1000

    @contextmanager
    def time_stage(self, stage_name: str):
        """
        Context manager for timing a stage.

        Args:
            stage_name: Stage name (ingestion, processing, pattern_learning, storage)

        Usage:
            with metrics.time_stage("ingestion"):
                # Execute stage
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000

            # Store duration
            if stage_name == "ingestion":
                self.ingestion_duration_ms = duration_ms
            elif stage_name == "processing":
                self.processing_duration_ms = duration_ms
            elif stage_name == "pattern_learning":
                self.pattern_learning_duration_ms = duration_ms
            elif stage_name == "storage":
                self.storage_duration_ms = duration_ms

    def record_labor_percentage(self, labor_pct: float):
        """Record labor percentage."""
        self.current_labor_percentage = labor_pct

        # Check for alerts (labor > 35%)
        if labor_pct > 35.0:
            self.labor_cost_alerts += 1

    def record_files_processed(self, count: int):
        """Record number of files processed."""
        self.files_processed = count

    def record_rows_written(self, count: int):
        """Record number of rows written to database."""
        self.rows_written += count

    def record_employees_processed(self, count: int):
        """Record number of employees processed."""
        self.employees_processed = count

    def record_patterns_learned(self, count: int):
        """Record number of patterns learned."""
        self.patterns_learned = count

    def to_dict(self) -> Dict[str, any]:
        """
        Export metrics as dictionary.

        Returns:
            Dict with all metrics
        """
        return {
            # Counters
            "pipelines_started": self.pipelines_started,
            "pipelines_completed": self.pipelines_completed,
            "pipelines_failed": self.pipelines_failed,

            # Timers
            "ingestion_duration_ms": round(self.ingestion_duration_ms, 2),
            "processing_duration_ms": round(self.processing_duration_ms, 2),
            "pattern_learning_duration_ms": round(self.pattern_learning_duration_ms, 2),
            "storage_duration_ms": round(self.storage_duration_ms, 2),
            "total_duration_ms": round(self.total_duration_ms, 2),

            # Gauges
            "current_labor_percentage": round(self.current_labor_percentage, 2),
            "files_processed": self.files_processed,
            "rows_written": self.rows_written,
            "employees_processed": self.employees_processed,

            # Business metrics
            "labor_cost_alerts": self.labor_cost_alerts,
            "patterns_learned": self.patterns_learned,

            # Timestamps
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    def get_summary(self) -> str:
        """
        Get human-readable summary.

        Returns:
            Summary string
        """
        if self.pipelines_completed > 0:
            status = "COMPLETED"
        elif self.pipelines_failed > 0:
            status = "FAILED"
        else:
            status = "IN PROGRESS"

        lines = [
            f"Pipeline Status: {status}",
            f"Total Duration: {self.total_duration_ms:.0f}ms",
            f"",
            f"Stage Timings:",
            f"  Ingestion:       {self.ingestion_duration_ms:7.0f}ms",
            f"  Processing:      {self.processing_duration_ms:7.0f}ms",
            f"  Pattern Learning:{self.pattern_learning_duration_ms:7.0f}ms",
            f"  Storage:         {self.storage_duration_ms:7.0f}ms",
            f"",
            f"Data Processed:",
            f"  Files:           {self.files_processed}",
            f"  Employees:       {self.employees_processed}",
            f"  Rows Written:    {self.rows_written}",
            f"",
            f"Business Metrics:",
            f"  Labor %:         {self.current_labor_percentage:.1f}%",
            f"  Patterns Learned:{self.patterns_learned}",
            f"  Cost Alerts:     {self.labor_cost_alerts}",
        ]

        return "\n".join(lines)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"PipelineMetrics("
            f"completed={self.pipelines_completed}, "
            f"failed={self.pipelines_failed}, "
            f"duration={self.total_duration_ms:.0f}ms, "
            f"labor={self.current_labor_percentage:.1f}%)"
        )
