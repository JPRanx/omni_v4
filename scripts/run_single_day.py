"""
Smoke Test: Run Full Pipeline for All Three Restaurants

Runs the complete pipeline (Ingestion -> Processing -> Pattern Learning -> Storage)
for SDR, T12, and TK9 restaurants on a single test date.

This is our standard smoke test - always validates all three restaurants
to catch restaurant-specific edge cases early.

Usage:
    python scripts/run_single_day.py

Expected test data:
    tests/fixtures/sample_data/2025-10-20/{SDR,T12,TK9}/
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.services.result import Result
from pipeline.orchestration.pipeline.context import PipelineContext
from pipeline.infrastructure.config.loader import ConfigLoader
from pipeline.infrastructure.database.in_memory_client import InMemoryDatabaseClient
from pipeline.services.patterns.in_memory_storage import InMemoryPatternStorage
from pipeline.services.patterns.manager import PatternManager
from pipeline.ingestion.data_validator import DataValidator
from pipeline.services.labor_calculator import LaborCalculator
from pipeline.stages.ingestion_stage import IngestionStage
from pipeline.stages.processing_stage import ProcessingStage
from pipeline.stages.pattern_learning_stage import PatternLearningStage
from pipeline.stages.storage_stage import StorageStage
from pipeline.models.labor_dto import LaborDTO
import pandas as pd


# Test configuration
TEST_DATE = "2025-10-20"
RESTAURANTS = [
    {"code": "SDR", "employees": 17, "orders": 168},
    {"code": "T12", "employees": 22, "orders": 330},
    {"code": "TK9", "employees": 9, "orders": 250},
]


class RestaurantResult:
    """Container for restaurant processing results"""

    def __init__(self, restaurant_code: str):
        self.restaurant_code = restaurant_code
        self.success = False
        self.failed_stage = None
        self.error_message = None
        self.ingestion_summary = None
        self.processing_summary = None
        self.pattern_summary = None
        self.storage_summary = None
        self.duration = 0.0

    def set_ingestion_success(self, employee_count: int, payroll_cost: float, sales: float):
        """Record successful ingestion"""
        self.ingestion_summary = {
            "employee_count": employee_count,
            "payroll_cost": payroll_cost,
            "sales": sales
        }

    def set_processing_success(self, labor_percentage: float, grade: str):
        """Record successful processing"""
        self.processing_summary = {
            "labor_percentage": labor_percentage,
            "grade": grade
        }

    def set_pattern_success(self, pattern_count: int):
        """Record successful pattern learning"""
        self.pattern_summary = {
            "pattern_count": pattern_count
        }

    def set_storage_success(self, tables_written: List[str], row_count: int):
        """Record successful storage"""
        self.storage_summary = {
            "tables_written": tables_written,
            "total_rows": row_count
        }

    def set_failure(self, stage: str, error_message: str):
        """Record failure at a specific stage"""
        self.failed_stage = stage
        self.error_message = error_message

    def mark_success(self):
        """Mark overall processing as successful"""
        self.success = True


def print_header(text: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_stage_result(stage_name: str, success: bool, details: str = ""):
    """Print stage result with checkmark or X"""
    symbol = "[OK]" if success else "[FAIL]"
    print(f"{symbol} {stage_name}: {'Success' if success else 'Failed'} {details}")


def cleanup_temp_files(restaurant_code: str, date: str):
    """
    Clean up temporary parquet files after processing.

    Args:
        restaurant_code: Restaurant code (SDR, T12, TK9)
        date: Business date (YYYY-MM-DD)
    """
    temp_dir = Path(f"C:/temp/omni/{restaurant_code}/{date}")
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            print(f"  [CLEANUP] Removed temp files: {temp_dir}")
        except Exception as e:
            print(f"  [WARNING] Failed to clean up {temp_dir}: {e}")


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


def run_restaurant_pipeline(
    restaurant_code: str,
    date: str,
    database_client: InMemoryDatabaseClient,
    pattern_manager: PatternManager
) -> RestaurantResult:
    """
    Run the complete pipeline for a single restaurant.

    Args:
        restaurant_code: Restaurant code (SDR, T12, TK9)
        date: Business date (YYYY-MM-DD)
        database_client: Shared database client
        pattern_manager: Shared pattern manager

    Returns:
        RestaurantResult: Processing results
    """
    result = RestaurantResult(restaurant_code)
    start_time = datetime.now()

    print_header(f"Running Pipeline for {restaurant_code}")

    try:
        # ============================================================
        # STAGE 1: CONFIGURATION
        # ============================================================
        print("\n[CONFIG] Stage 1: Configuration")
        config_loader = ConfigLoader()
        config = config_loader.load_config(restaurant_code=restaurant_code, env="dev")
        print(f"  [OK] Loaded configuration for {restaurant_code}")

        # Create pipeline context
        data_path = project_root / "tests" / "fixtures" / "sample_data" / date / restaurant_code

        context = PipelineContext(
            restaurant_code=restaurant_code,
            date=date,
            config=config,
            environment="dev"
        )

        # Set required context keys for ingestion stage
        context.set('date', date)
        context.set('restaurant', restaurant_code)
        context.set('data_path', str(data_path))

        # ============================================================
        # STAGE 2: INGESTION
        # ============================================================
        print("\n[INGEST] Stage 2: Ingestion")
        validator = DataValidator()
        ingestion_stage = IngestionStage(validator)

        ingestion_result = ingestion_stage.execute(context)

        if ingestion_result.is_err():
            error = ingestion_result.unwrap_err()
            result.set_failure("Ingestion", str(error))
            print_stage_result("Ingestion", False, f"({error})")
            return result

        context = ingestion_result.unwrap()

        # Extract ingestion metrics
        sales = context.get('sales')
        payroll_cost = context.get('total_payroll_cost', 0.0)
        raw_dfs = context.get('raw_dataframes')

        # Count employees from payroll data
        employee_count = 0
        if raw_dfs and 'payroll' in raw_dfs:
            employee_count = len(raw_dfs['payroll'])

        result.set_ingestion_success(employee_count, payroll_cost, sales)
        print_stage_result(
            "Ingestion",
            True,
            f"({employee_count} employees, ${payroll_cost:,.2f} payroll)"
        )

        # ============================================================
        # STAGE 3: CREATE LABOR DTO
        # ============================================================
        print("\n[LABOR] Stage 3: Labor DTO Creation")

        if 'payroll' not in raw_dfs:
            result.set_failure("Labor DTO", "PayrollExport data not found")
            print_stage_result("Labor DTO", False, "(PayrollExport missing)")
            return result

        labor_dto_result = extract_labor_dto_from_payroll(
            raw_dfs['payroll'],
            restaurant_code,
            date
        )

        if labor_dto_result.is_err():
            error = labor_dto_result.unwrap_err()
            result.set_failure("Labor DTO", str(error))
            print_stage_result("Labor DTO", False, f"({error})")
            return result

        labor_dto = labor_dto_result.unwrap()
        context.set('labor_dto', labor_dto)
        print_stage_result(
            "Labor DTO",
            True,
            f"({labor_dto.total_hours_worked:.1f}h, ${labor_dto.total_labor_cost:,.2f})"
        )

        # ============================================================
        # STAGE 4: PROCESSING
        # ============================================================
        print("\n[PROCESS] Stage 4: Processing")
        calculator = LaborCalculator(config)
        processing_stage = ProcessingStage(calculator)

        processing_result = processing_stage.execute(context)

        if processing_result.is_err():
            error = processing_result.unwrap_err()
            result.set_failure("Processing", str(error))
            print_stage_result("Processing", False, f"({error})")
            return result

        context = processing_result.unwrap()

        # Extract processing metrics
        labor_percentage = context.get('labor_percentage')
        labor_grade = context.get('labor_grade')

        result.set_processing_success(labor_percentage, labor_grade)
        print_stage_result(
            "Processing",
            True,
            f"(Labor: {labor_percentage:.1f}%, Grade: {labor_grade})"
        )

        # ============================================================
        # STAGE 5: PATTERN LEARNING
        # ============================================================
        print("\n[PATTERN] Stage 5: Pattern Learning")

        # Create pattern learning stage
        from pipeline.stages.pattern_learning_stage import PatternLearningStage
        pattern_learning_stage = PatternLearningStage(pattern_manager)

        pattern_result = pattern_learning_stage.execute(context)

        if pattern_result.is_err():
            error = pattern_result.unwrap_err()
            result.set_failure("Pattern Learning", str(error))
            print_stage_result("Pattern Learning", False, f"({error})")
            return result

        context = pattern_result.unwrap()

        # Get learned patterns
        learned_patterns = context.get('learned_patterns', [])
        pattern_warnings = context.get('pattern_warnings', [])

        result.set_pattern_success(len(learned_patterns))
        if pattern_warnings:
            print_stage_result("Pattern Learning", True, f"({len(learned_patterns)} patterns, {len(pattern_warnings)} warnings)")
        else:
            print_stage_result("Pattern Learning", True, f"({len(learned_patterns)} pattern learned)")

        # ============================================================
        # STAGE 6: STORAGE
        # ============================================================
        print("\n[STORAGE] Stage 6: Storage")

        # Create mock IngestionResult for storage
        from pipeline.models.ingestion_result import IngestionResult
        ingestion_dto = IngestionResult.create(
            restaurant_code=restaurant_code,
            business_date=date,
            quality_level=1,
            toast_data_path=f"C:/temp/omni/{restaurant_code}/{date}/sales.parquet"
        ).unwrap()

        context.set('ingestion_result', ingestion_dto)

        storage_stage = StorageStage(database_client)
        storage_result = storage_stage.execute(context)

        if storage_result.is_err():
            error = storage_result.unwrap_err()
            result.set_failure("Storage", str(error))
            print_stage_result("Storage", False, f"({error})")
            return result

        context = storage_result.unwrap()

        # Extract storage metrics
        storage_dto = context.get('storage_result')
        tables_written = storage_dto.tables_written if storage_dto else []
        total_rows = sum(storage_dto.row_counts.values()) if storage_dto else 0

        result.set_storage_success(tables_written, total_rows)
        print_stage_result(
            "Storage",
            True,
            f"({len(tables_written)} tables, {total_rows} rows)"
        )

        # ============================================================
        # SUCCESS
        # ============================================================
        result.mark_success()
        result.duration = (datetime.now() - start_time).total_seconds()

        print(f"\n[SUCCESS] {restaurant_code} pipeline completed in {result.duration:.2f}s")

    except Exception as e:
        # Unexpected error
        result.set_failure("Unexpected", str(e))
        result.duration = (datetime.now() - start_time).total_seconds()
        print(f"\n[FAIL] {restaurant_code} pipeline failed: {e}")

    finally:
        # ALWAYS clean up temp files
        cleanup_temp_files(restaurant_code, date)

    return result


def print_summary(results: List[RestaurantResult]):
    """
    Print summary comparison across all restaurants.

    Args:
        results: List of restaurant processing results
    """
    print_header("Summary")

    # Count successes and failures
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    print(f"\n[RESULTS] Overall Results:")
    print(f"  [OK] Successful: {len(successes)}/{len(results)}")
    print(f"  [FAIL] Failed: {len(failures)}/{len(results)}")

    # Print individual results
    print(f"\n[DETAILS] Restaurant Details:")
    for r in results:
        if r.success:
            print(f"  {r.restaurant_code}: [OK] Complete ({r.duration:.2f}s)")
            if r.processing_summary:
                print(f"      Labor: {r.processing_summary['labor_percentage']:.1f}% ({r.processing_summary['grade']})")
        else:
            print(f"  {r.restaurant_code}: [FAIL] Failed at {r.failed_stage}")
            print(f"      Error: {r.error_message}")

    # Compare metrics across successful restaurants
    if len(successes) > 1:
        print(f"\n[COMPARE] Cross-Restaurant Comparison:")
        print(f"  {'Restaurant':<12} {'Employees':<12} {'Payroll':<15} {'Labor %':<12} {'Grade':<8}")
        print(f"  {'-'*59}")

        for r in successes:
            employees = r.ingestion_summary['employee_count']
            payroll = r.ingestion_summary['payroll_cost']
            labor_pct = r.processing_summary['labor_percentage']
            grade = r.processing_summary['grade']

            print(f"  {r.restaurant_code:<12} {employees:<12} ${payroll:<14,.2f} {labor_pct:<11.1f}% {grade:<8}")

    # Flag restaurant-specific issues
    if failures:
        print(f"\n[ISSUES] Restaurant-Specific Issues:")
        for r in failures:
            print(f"  {r.restaurant_code}: {r.failed_stage} stage failed")
            print(f"    Reason: {r.error_message}")


def main():
    """Main entry point"""
    print(f"""
===================================================================

              OMNI V4 - THREE RESTAURANT SMOKE TEST

  Date: {TEST_DATE}
  Restaurants: SDR, T12, TK9
  Stages: Ingestion -> Processing -> Patterns -> Storage

===================================================================
    """)

    # Create shared infrastructure
    database_client = InMemoryDatabaseClient()
    pattern_storage = InMemoryPatternStorage()

    # Load base config for pattern manager (will use first restaurant's config)
    config_loader = ConfigLoader()
    base_config = config_loader.load_config(restaurant_code="SDR", env="dev")
    pattern_manager = PatternManager(pattern_storage, base_config)

    results = []

    # Run pipeline for each restaurant (isolated - one failure doesn't stop others)
    for restaurant in RESTAURANTS:
        code = restaurant['code']

        try:
            result = run_restaurant_pipeline(
                code,
                TEST_DATE,
                database_client,
                pattern_manager
            )
            results.append(result)

        except Exception as e:
            # Catch any unexpected errors and continue to next restaurant
            print(f"\n[FAIL] Critical error processing {code}: {e}")
            result = RestaurantResult(code)
            result.set_failure("Critical", str(e))
            results.append(result)

    # Print summary comparison
    print_summary(results)

    # Exit with error code if any restaurant failed
    failed_count = len([r for r in results if not r.success])
    if failed_count > 0:
        print(f"\n[FAIL] {failed_count} restaurant(s) failed. See errors above.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] All restaurants processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
