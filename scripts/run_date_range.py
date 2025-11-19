#!/usr/bin/env python
"""
Batch process multiple days of restaurant data.

This script runs the complete pipeline for a date range and restaurant(s),
collecting metrics and generating summary reports.

Usage:
    python scripts/run_date_range.py SDR 2025-08-20 2025-08-31
    python scripts/run_date_range.py ALL 2025-08-20 2025-08-25 --output report.json
    python scripts/run_date_range.py "SDR,T12" 2025-08-20 2025-08-31 --verbose
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.pipeline import PipelineContext
from src.processing.stages.ingestion_stage import IngestionStage
from src.processing.stages.order_categorization_stage import OrderCategorizationStage
from src.processing.stages.timeslot_grading_stage import TimeslotGradingStage
from src.processing.stages.processing_stage import ProcessingStage
from src.processing.stages.pattern_learning_stage import PatternLearningStage
from src.processing.stages.storage_stage import StorageStage
from src.processing.stages.supabase_storage_stage import SupabaseStorageStage
from src.ingestion.data_validator import DataValidator
from src.processing.labor_calculator import LaborCalculator
from src.processing.order_categorizer import OrderCategorizer
from src.processing.timeslot_windower import TimeslotWindower
from src.processing.timeslot_grader import TimeslotGrader
from src.core.patterns.daily_labor_manager import DailyLaborPatternManager
from src.core.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage
from src.core.patterns.timeslot_pattern_manager import TimeslotPatternManager
from src.infrastructure.database.in_memory_client import InMemoryDatabaseClient
from src.infrastructure.logging import setup_logging, PipelineMetrics
from src.infrastructure.config.loader import ConfigLoader
from src.models.labor_dto import LaborDTO
from src.processing.cash_flow_extractor import CashFlowExtractor
from src.core.result import Result


def discover_available_dates(data_dir: Path) -> List[str]:
    """
    Scan data directory for available date folders.

    Args:
        data_dir: Path to data directory

    Returns:
        List of date strings (YYYY-MM-DD) sorted chronologically
    """
    available_dates = []

    if not data_dir.exists():
        return available_dates

    # Scan for directories matching YYYY-MM-DD pattern
    for item in data_dir.iterdir():
        if item.is_dir():
            dir_name = item.name
            # Validate date format YYYY-MM-DD
            try:
                datetime.strptime(dir_name, '%Y-%m-%d')
                available_dates.append(dir_name)
            except ValueError:
                # Not a valid date folder, skip
                continue

    # Sort chronologically
    available_dates.sort()

    return available_dates


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


def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Generate list of dates between start and end (inclusive).

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of date strings in YYYY-MM-DD format
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


def run_pipeline_for_date(
    restaurant_code: str,
    business_date: str,
    validator: DataValidator,
    calculator: LaborCalculator,
    pattern_manager: DailyLaborPatternManager,
    timeslot_pattern_manager: TimeslotPatternManager,
    database_client: InMemoryDatabaseClient,
    config_loader: ConfigLoader,
    verbose: bool = False,
    use_supabase: bool = False
) -> tuple[bool, PipelineMetrics]:
    """
    Run pipeline for a single restaurant and date.

    Args:
        restaurant_code: Restaurant code
        business_date: Business date (YYYY-MM-DD)
        validator: DataValidator instance
        calculator: LaborCalculator instance
        pattern_manager: DailyLaborPatternManager instance
        timeslot_pattern_manager: TimeslotPatternManager instance
        database_client: DatabaseClient instance
        config_loader: ConfigLoader instance
        verbose: Whether to print verbose output
        use_supabase: Whether to use Supabase storage (Investigation Modal data)

    Returns:
        Tuple of (success, metrics)
    """
    # Auto-detect data path - use V4's data directory
    data_path = str(project_root / "data" / business_date / restaurant_code)

    # Check if data exists
    if not Path(data_path).exists():
        if verbose:
            print(f"  [SKIP] {restaurant_code} {business_date}: Data not found")
        return False, None

    # Load configuration
    config = config_loader.load_config(restaurant_code, env="dev")

    # Create metrics tracker
    metrics = PipelineMetrics()
    metrics.pipeline_started()

    # Create stages
    ingestion_stage = IngestionStage(validator)
    categorizer = OrderCategorizer()
    categorization_stage = OrderCategorizationStage(categorizer)
    windower = TimeslotWindower()
    grader = TimeslotGrader()
    timeslot_grading_stage = TimeslotGradingStage(windower, grader, timeslot_pattern_manager)
    processing_stage = ProcessingStage(calculator)
    pattern_learning_stage = PatternLearningStage(pattern_manager, timeslot_pattern_manager)

    # Choose storage stage based on flag
    if use_supabase:
        storage_stage = SupabaseStorageStage()
    else:
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

    # STAGE 1: Ingestion
    with metrics.time_stage("ingestion"):
        result = ingestion_stage.execute(context)
        if result.is_err():
            if verbose:
                print(f"  [FAIL] {restaurant_code} {business_date}: ingestion stage failed: {result.unwrap_err()}")
            metrics.pipeline_failed()
            return False, (metrics, context)

    # STAGE 1.5: Extract LaborDTO from raw dataframes
    raw_dfs = context.get('raw_dataframes')
    if raw_dfs and 'payroll' in raw_dfs:
        labor_dto_result = extract_labor_dto_from_payroll(
            raw_dfs['payroll'],
            restaurant_code,
            business_date
        )
        if labor_dto_result.is_err():
            if verbose:
                print(f"  [FAIL] {restaurant_code} {business_date}: labor_dto extraction failed: {labor_dto_result.unwrap_err()}")
            metrics.pipeline_failed()
            return False, (metrics, context)
        context.set('labor_dto', labor_dto_result.unwrap())

    # STAGE 2: Order Categorization
    with metrics.time_stage("categorization"):
        result = categorization_stage.execute(context)
        if result.is_err():
            if verbose:
                print(f"  [FAIL] {restaurant_code} {business_date}: categorization stage failed: {result.unwrap_err()}")
            metrics.pipeline_failed()
            return False, (metrics, context)

    # STAGE 3: Timeslot Grading
    with metrics.time_stage("timeslot_grading"):
        result = timeslot_grading_stage.execute(context)
        if result.is_err():
            if verbose:
                print(f"  [FAIL] {restaurant_code} {business_date}: timeslot_grading stage failed: {result.unwrap_err()}")
            metrics.pipeline_failed()
            return False, (metrics, context)

    # STAGE 4-6: Processing, Pattern Learning, Storage
    stages = [
        ("processing", processing_stage),
        ("pattern_learning", pattern_learning_stage),
        ("storage", storage_stage)
    ]

    for stage_name, stage in stages:
        with metrics.time_stage(stage_name):
            result = stage.execute(context)

            if result.is_err():
                if verbose:
                    print(f"  [FAIL] {restaurant_code} {business_date}: {stage_name} stage failed: {result.unwrap_err()}")
                metrics.pipeline_failed()
                return False, (metrics, context)

    # Record business metrics
    labor_percentage = context.get('labor_percentage', 0.0)
    metrics.record_labor_percentage(labor_percentage)

    learned_patterns = context.get('learned_patterns', [])
    metrics.record_patterns_learned(len(learned_patterns))

    storage_result = context.get('storage_result')
    if storage_result:
        # Handle both object with row_counts attribute and dict
        if hasattr(storage_result, 'row_counts'):
            total_rows = sum(storage_result.row_counts.values())
        elif isinstance(storage_result, dict) and 'row_counts' in storage_result:
            total_rows = sum(storage_result['row_counts'].values())
        else:
            total_rows = 0
        metrics.record_rows_written(total_rows)

    metrics.pipeline_completed()

    if verbose:
        grade = context.get('labor_grade', '?')
        service_mix = context.get('service_mix')
        categorized_orders = context.get('categorization_metadata', {}).get('categorized_orders', 0)
        timeslot_metrics = context.get('timeslot_metrics')

        output_parts = [f"Labor={labor_percentage:.1f}% Grade={grade}"]

        if service_mix:
            output_parts.append(f"Orders={categorized_orders} (L:{service_mix['Lobby']:.0f}% D:{service_mix['Drive-Thru']:.0f}% T:{service_mix['ToGo']:.0f}%)")

        if timeslot_metrics:
            morning_pass = timeslot_metrics.get('morning_pass_rate', 0)
            evening_pass = timeslot_metrics.get('evening_pass_rate', 0)
            active_slots = timeslot_metrics.get('active_slots', 0)
            output_parts.append(f"Slots={active_slots} (M:{morning_pass:.0f}% E:{evening_pass:.0f}%)")

        print(f"  [OK] {restaurant_code} {business_date}: {' | '.join(output_parts)}")

    # Return metrics along with context data for additional fields
    return True, (metrics, context)


def run_batch_processing(
    restaurant_codes: List[str],
    start_date: str,
    end_date: str,
    verbose: bool = False,
    use_supabase: bool = False
) -> Dict[str, Any]:
    """
    Run batch processing for multiple restaurants and dates.

    Args:
        restaurant_codes: List of restaurant codes to process
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        verbose: Whether to print verbose output
        use_supabase: Whether to use Supabase storage (Investigation Modal data)

    Returns:
        Dictionary with batch results and summary
    """
    # Generate date range
    dates = generate_date_range(start_date, end_date)

    print(f"\n>>> Batch Processing")
    print(f"    Restaurants: {', '.join(restaurant_codes)}")
    print(f"    Date Range: {start_date} to {end_date} ({len(dates)} days)")
    print("=" * 80)

    # Initialize shared components
    validator = DataValidator()
    calculator = LaborCalculator()
    config_loader = ConfigLoader(str(project_root / "config"))

    # Create separate pattern managers per restaurant (they maintain state)
    pattern_managers = {}
    timeslot_pattern_managers = {}
    for restaurant_code in restaurant_codes:
        pattern_storage = InMemoryDailyLaborPatternStorage()
        config = config_loader.load_config(restaurant_code, env="dev")
        pattern_managers[restaurant_code] = DailyLaborPatternManager(pattern_storage, config)
        timeslot_pattern_managers[restaurant_code] = TimeslotPatternManager()

    # Shared database client (accumulates all data)
    database_client = InMemoryDatabaseClient()

    # Track results
    results = {
        'restaurants': restaurant_codes,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': len(dates),
        'pipeline_runs': [],
        'summary': {
            'total_processed': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'by_restaurant': {}
        }
    }

    # Process each restaurant and date
    for restaurant_code in restaurant_codes:
        if verbose:
            print(f"\n{restaurant_code}:")

        restaurant_summary = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'labor_percentages': [],
            'grades': [],
            'patterns_learned': 0
        }

        for business_date in dates:
            result = run_pipeline_for_date(
                restaurant_code=restaurant_code,
                business_date=business_date,
                validator=validator,
                calculator=calculator,
                pattern_manager=pattern_managers[restaurant_code],
                timeslot_pattern_manager=timeslot_pattern_managers[restaurant_code],
                database_client=database_client,
                config_loader=config_loader,
                verbose=verbose,
                use_supabase=use_supabase
            )

            if result is None or result[0] is None:
                # Skipped (data not found)
                restaurant_summary['skipped'] += 1
                results['summary']['total_skipped'] += 1
            else:
                # Process result - unpack tuple
                success, (metrics, context) = result

                if success:
                    # Success
                    restaurant_summary['processed'] += 1
                    results['summary']['total_processed'] += 1

                    # Extract metrics
                    metrics_dict = metrics.to_dict()
                    if 'current_labor_percentage' in metrics_dict:
                        restaurant_summary['labor_percentages'].append(metrics_dict['current_labor_percentage'])

                    restaurant_summary['patterns_learned'] += metrics_dict.get('patterns_learned', 0)

                    # Store run details with complete data
                    run_data = {
                        'restaurant': restaurant_code,
                        'date': business_date,
                        'success': True,
                        'labor_percentage': metrics_dict.get('current_labor_percentage', 0.0),
                        'duration_ms': metrics_dict.get('total_duration_ms', 0.0)
                    }

                    # Add additional metrics from context
                    labor_dto = context.get('labor_dto')
                    if labor_dto:
                        run_data['labor_cost'] = float(labor_dto.total_labor_cost)
                        run_data['overtime_hours'] = float(labor_dto.total_overtime_hours)
                        run_data['overtime_cost'] = float(labor_dto.total_overtime_cost)
                        run_data['regular_hours'] = float(labor_dto.total_regular_hours)

                    # Extract cash flow data
                    cash_flow_extractor = CashFlowExtractor()
                    # Construct data path (same as in run_pipeline_for_date)
                    csv_dir = project_root / "data" / business_date / restaurant_code
                    cash_flow_result = cash_flow_extractor.extract_from_csvs(
                        csv_dir=csv_dir,
                        business_date=business_date,
                        restaurant_code=restaurant_code
                    )

                    if cash_flow_result.is_ok():
                        cash_flow = cash_flow_result.unwrap()
                        run_data['cash_flow'] = cash_flow.to_dict()
                    else:
                        logger.warning(f"[{restaurant_code}] [{business_date}] Cash flow extraction failed: {cash_flow_result.unwrap_err()}")

                    # Get sales from raw dataframes
                    raw_dfs = context.get('raw_dataframes')
                    if raw_dfs and 'sales' in raw_dfs:
                        sales_df = raw_dfs['sales']
                        if 'Net sales' in sales_df.columns:
                            net_sales = sales_df['Net sales'].iloc[0] if len(sales_df) > 0 else 0
                            run_data['sales'] = float(net_sales)

                    labor_grade = context.get('labor_grade')
                    if labor_grade:
                        run_data['grade'] = labor_grade

                    # Add service mix from categorization
                    service_mix = context.get('service_mix')
                    if service_mix:
                        run_data['service_mix'] = service_mix

                    categorization_metadata = context.get('categorization_metadata')
                    if categorization_metadata:
                        run_data['categorized_orders'] = categorization_metadata.get('categorized_orders', 0)

                    # Add shift metrics if available
                    shift_metrics = context.get('shift_metrics')
                    if shift_metrics:
                        # ShiftMetricsDTO has to_dict() method
                        run_data['shift_metrics'] = shift_metrics.to_dict()

                    # Add shift-level category statistics (unique orders only)
                    shift_category_stats = context.get('shift_category_stats')
                    if shift_category_stats:
                        run_data['shift_category_stats'] = shift_category_stats

                    # Add full timeslot data for Investigation Modal
                    timeslots = context.get('timeslots')
                    if timeslots:
                        # Serialize all timeslots (morning + evening) using to_dict()
                        timeslot_list = []
                        for shift in ['morning', 'evening']:
                            for timeslot in timeslots.get(shift, []):
                                timeslot_list.append(timeslot.to_dict())
                        run_data['timeslot_metrics'] = timeslot_list

                    # Add timeslot summary metrics
                    timeslot_summary = context.get('timeslot_metrics')
                    if timeslot_summary:
                        run_data['timeslot_summary'] = {
                            'total_slots': timeslot_summary.get('total_slots', 0),
                            'active_slots': timeslot_summary.get('active_slots', 0),
                            'passed_standards': timeslot_summary.get('passed_standards', 0),
                            'overall_pass_rate': timeslot_summary.get('overall_pass_rate', 0.0),
                            'morning_pass_rate': timeslot_summary.get('morning_pass_rate', 0.0),
                            'evening_pass_rate': timeslot_summary.get('evening_pass_rate', 0.0),
                            'morning_hot_streaks': timeslot_summary.get('morning_hot_streaks', 0),
                            'morning_cold_streaks': timeslot_summary.get('morning_cold_streaks', 0),
                            'evening_hot_streaks': timeslot_summary.get('evening_hot_streaks', 0),
                            'evening_cold_streaks': timeslot_summary.get('evening_cold_streaks', 0)
                        }

                    # Add auto-clockout summary if available
                    auto_clockout_summary = context.get('auto_clockout_summary')
                    if auto_clockout_summary:
                        run_data['auto_clockout_summary'] = auto_clockout_summary.to_dict()

                    # Add time entries for weekly overtime calculation
                    time_entries = context.get('time_entries')
                    if time_entries:
                        # Serialize TimeEntry list
                        run_data['time_entries'] = [entry.to_dict() for entry in time_entries]

                    results['pipeline_runs'].append(run_data)
                else:
                    # Failed
                    restaurant_summary['failed'] += 1
                    results['summary']['total_failed'] += 1

                    results['pipeline_runs'].append({
                        'restaurant': restaurant_code,
                        'date': business_date,
                        'success': False
                    })

        # Calculate restaurant averages
        if restaurant_summary['labor_percentages']:
            restaurant_summary['avg_labor_percentage'] = sum(restaurant_summary['labor_percentages']) / len(restaurant_summary['labor_percentages'])
            restaurant_summary['min_labor_percentage'] = min(restaurant_summary['labor_percentages'])
            restaurant_summary['max_labor_percentage'] = max(restaurant_summary['labor_percentages'])

        results['summary']['by_restaurant'][restaurant_code] = restaurant_summary

    return results


def print_summary_report(results: Dict[str, Any]):
    """Print human-readable summary report."""
    print("\n" + "=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)

    print(f"\nDate Range: {results['start_date']} to {results['end_date']} ({results['total_days']} days)")
    print(f"Restaurants: {', '.join(results['restaurants'])}")

    print(f"\nOverall Results:")
    print(f"  Processed: {results['summary']['total_processed']}")
    print(f"  Failed:    {results['summary']['total_failed']}")
    print(f"  Skipped:   {results['summary']['total_skipped']}")

    print(f"\nPer-Restaurant Summary:")
    print("-" * 80)
    print(f"{'Restaurant':<12} {'Processed':<10} {'Failed':<8} {'Avg Labor %':<12} {'Min':<8} {'Max':<8} {'Patterns':<10}")
    print("-" * 80)

    for restaurant_code in results['restaurants']:
        summary = results['summary']['by_restaurant'][restaurant_code]

        avg_labor = summary.get('avg_labor_percentage', 0.0)
        min_labor = summary.get('min_labor_percentage', 0.0)
        max_labor = summary.get('max_labor_percentage', 0.0)

        print(f"{restaurant_code:<12} {summary['processed']:<10} {summary['failed']:<8} "
              f"{avg_labor:<12.1f} {min_labor:<8.1f} {max_labor:<8.1f} {summary['patterns_learned']:<10}")

    print("-" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_date_range.py <restaurant_codes> [start_date] [end_date] [--output <file.json>] [--verbose] [--supabase]")
        print("\nExamples:")
        print("  python scripts/run_date_range.py ALL                          # Auto-detect all dates")
        print("  python scripts/run_date_range.py SDR AUTO AUTO                # Auto-detect all dates for SDR")
        print("  python scripts/run_date_range.py SDR 2025-08-20 2025-08-31    # Explicit date range")
        print("  python scripts/run_date_range.py ALL --supabase               # Auto-detect dates, store to Supabase")
        print("  python scripts/run_date_range.py \"SDR,T12\" --verbose          # Multiple restaurants, auto-detect dates")
        print("\nRestaurant Codes:")
        print("  ALL        - Process all restaurants (SDR, T12, TK9)")
        print("  SDR        - Single restaurant")
        print("  SDR,T12    - Comma-separated list")
        print("\nDate Arguments:")
        print("  AUTO       - Auto-detect available dates in data/ directory")
        print("  (omit)     - Auto-detect if not provided")
        print("  YYYY-MM-DD - Explicit start/end dates")
        print("\nFlags:")
        print("  --supabase - Store data to Supabase (Investigation Modal compatible format)")
        print("  --verbose  - Print detailed progress information")
        print("  --output   - Export batch results to JSON file")
        sys.exit(1)

    # Parse arguments
    restaurant_input = sys.argv[1]

    # Determine if dates are provided or if we should auto-detect
    # Check if argument 2 looks like a date or a flag
    start_date = None
    end_date = None
    arg_index = 2

    if len(sys.argv) > arg_index and not sys.argv[arg_index].startswith('--'):
        start_date = sys.argv[arg_index]
        arg_index += 1

        if len(sys.argv) > arg_index and not sys.argv[arg_index].startswith('--'):
            end_date = sys.argv[arg_index]
            arg_index += 1

    # Parse restaurant codes
    if restaurant_input.upper() == "ALL":
        restaurant_codes = ["SDR", "T12", "TK9"]
    else:
        restaurant_codes = [code.strip() for code in restaurant_input.split(",")]

    # Auto-detect dates if not provided or if AUTO is specified
    if not start_date or not end_date or start_date.upper() == "AUTO" or end_date.upper() == "AUTO":
        data_dir = project_root / "data"
        available_dates = discover_available_dates(data_dir)

        if not available_dates:
            print(f"\n[ERROR] No date folders found in {data_dir}")
            print("Please copy your date folders (YYYY-MM-DD) to the data/ directory.")
            sys.exit(1)

        start_date = available_dates[0]
        end_date = available_dates[-1]

        print(f"\n[AUTO-DETECT] Found {len(available_dates)} dates: {start_date} to {end_date}")
        print(f"              Available dates: {', '.join(available_dates)}")

    # Parse optional flags
    output_file = None
    verbose = False
    use_supabase = False

    i = arg_index
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--verbose":
            verbose = True
            i += 1
        elif sys.argv[i] == "--supabase":
            use_supabase = True
            i += 1
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            sys.exit(1)

    # Setup logging (INFO for verbose, WARNING otherwise)
    setup_logging(level="INFO" if verbose else "WARNING")

    try:
        # Print mode indicator
        if use_supabase:
            print("\n[SUPABASE MODE] Data will be stored to Supabase (Investigation Modal format)")
        else:
            print("\n[LOCAL MODE] Data will be stored in-memory only")

        # Run batch processing
        results = run_batch_processing(
            restaurant_codes=restaurant_codes,
            start_date=start_date,
            end_date=end_date,
            verbose=verbose,
            use_supabase=use_supabase
        )

        # Print summary
        print_summary_report(results)

        # Export to JSON if requested (default to outputs/pipeline_runs/)
        if output_file:
            output_path = Path(output_file)
            # If relative path without directory, put in outputs/pipeline_runs/
            if not output_path.is_absolute() and output_path.parent == Path('.'):
                output_path = project_root / "outputs" / "pipeline_runs" / output_file

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n>>> Results exported to: {output_path}")

        # Return non-zero exit code if any failures
        if results['summary']['total_failed'] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"\n>>> Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
