#!/usr/bin/env python
"""
Run pipeline with full metrics export.

This script runs the complete pipeline for a restaurant and date,
displaying structured logs and exporting metrics to JSON.

Usage:
    python scripts/run_pipeline_with_metrics.py SDR 2025-10-20
    python scripts/run_pipeline_with_metrics.py T12 2025-10-21 --output metrics.json
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.pipeline import PipelineContext
from src.processing.stages.ingestion_stage import IngestionStage
from src.processing.stages.processing_stage import ProcessingStage
from src.processing.stages.pattern_learning_stage import PatternLearningStage
from src.processing.stages.storage_stage import StorageStage
from src.ingestion.data_validator import DataValidator
from src.processing.labor_calculator import LaborCalculator
from src.core.patterns.daily_labor_manager import DailyLaborPatternManager
from src.core.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage
from src.infrastructure.database.in_memory_client import InMemoryDatabaseClient
from src.infrastructure.logging import setup_logging, PipelineMetrics
from src.infrastructure.config.loader import ConfigLoader


def run_pipeline(restaurant_code: str, business_date: str, data_path: str = None) -> PipelineMetrics:
    """
    Run complete pipeline for restaurant and date.

    Args:
        restaurant_code: Restaurant code (SDR, T12, TK9)
        business_date: Business date (YYYY-MM-DD)
        data_path: Path to Toast data directory (optional, auto-detected if not provided)

    Returns:
        PipelineMetrics: Metrics collected during pipeline execution
    """
    # Setup structured logging
    setup_logging(level="INFO")

    # Auto-detect data path if not provided
    if data_path is None:
        data_path = str(project_root / "tests" / "fixtures" / "sample_data" / business_date / restaurant_code)

    # Create metrics tracker
    metrics = PipelineMetrics()
    metrics.pipeline_started()

    # Load configuration
    config_loader = ConfigLoader(str(project_root / "config"))
    config = config_loader.load_config(restaurant_code, env="dev")

    # Initialize components
    validator = DataValidator()
    calculator = LaborCalculator()
    pattern_storage = InMemoryDailyLaborPatternStorage()
    pattern_manager = DailyLaborPatternManager(pattern_storage, config)
    database_client = InMemoryDatabaseClient()

    # Create stages
    ingestion_stage = IngestionStage(validator)
    processing_stage = ProcessingStage(calculator)
    pattern_learning_stage = PatternLearningStage(pattern_manager)
    storage_stage = StorageStage(database_client)

    # Create context
    context = PipelineContext(
        restaurant_code=restaurant_code,
        date=business_date,
        config=config
    )
    context.set('restaurant', restaurant_code)
    context.set('date', business_date)
    context.set('data_path', data_path)

    # Execute stages
    stages = [
        ("ingestion", ingestion_stage),
        ("processing", processing_stage),
        ("pattern_learning", pattern_learning_stage),
        ("storage", storage_stage)
    ]

    for stage_name, stage in stages:
        with metrics.time_stage(stage_name):
            result = stage.execute(context)

            if result.is_err():
                print(f"\n>>> Pipeline failed at {stage_name} stage: {result.unwrap_err()}")
                metrics.pipeline_failed()
                return metrics

    # Record business metrics
    labor_percentage = context.get('labor_percentage', 0.0)
    metrics.record_labor_percentage(labor_percentage)

    learned_patterns = context.get('learned_patterns', [])
    metrics.record_patterns_learned(len(learned_patterns))

    storage_result = context.get('storage_result')
    if storage_result:
        total_rows = sum(storage_result.row_counts.values())
        metrics.record_rows_written(total_rows)

    metrics.pipeline_completed()
    return metrics


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python run_pipeline_with_metrics.py <restaurant_code> <business_date> [--output <file.json>]")
        print("\nExample:")
        print("  python scripts/run_pipeline_with_metrics.py SDR 2025-10-20")
        print("  python scripts/run_pipeline_with_metrics.py T12 2025-10-21 --output metrics.json")
        sys.exit(1)

    restaurant_code = sys.argv[1]
    business_date = sys.argv[2]

    # Check for output file option
    output_file = None
    if len(sys.argv) > 3 and sys.argv[3] == "--output":
        if len(sys.argv) > 4:
            output_file = sys.argv[4]
        else:
            print("Error: --output requires a filename")
            sys.exit(1)

    print(f"\n>>> Running pipeline for {restaurant_code} on {business_date}")
    print("=" * 80)

    try:
        metrics = run_pipeline(restaurant_code, business_date)

        print("\n" + "=" * 80)
        print("PIPELINE METRICS")
        print("=" * 80)
        print(metrics.get_summary())

        # Export metrics to JSON if requested
        if output_file:
            metrics_dict = metrics.to_dict()
            metrics_dict['restaurant_code'] = restaurant_code
            metrics_dict['business_date'] = business_date

            with open(output_file, 'w') as f:
                json.dump(metrics_dict, f, indent=2)

            print(f"\n>>> Metrics exported to: {output_file}")

        # Return non-zero exit code if pipeline failed
        if metrics.pipelines_failed > 0:
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n>>> Error: Data not found")
        print(f"   {e}")
        print(f"\n>>> Make sure data exists at:")
        print(f"   tests/fixtures/sample_data/{business_date}/{restaurant_code}/")
        sys.exit(1)
    except Exception as e:
        print(f"\n>>> Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
