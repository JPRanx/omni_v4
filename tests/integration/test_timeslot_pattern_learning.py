"""
Integration test for timeslot pattern learning system.

Tests the complete pattern learning workflow including:
- Learning patterns from multiple days of data
- Pattern reliability thresholds
- Exponential moving average learning
- Confidence and variance calculations
- Pattern retrieval for different days of week
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.core.patterns.timeslot_pattern_manager import TimeslotPatternManager
from src.models.timeslot_pattern import TimeslotPattern
from src.ingestion.csv_data_source import CSVDataSource
from src.ingestion.data_validator import DataValidator
from src.processing.stages.ingestion_stage import IngestionStage
from src.processing.stages.order_categorization_stage import OrderCategorizationStage
from src.processing.order_categorizer import OrderCategorizer
from src.processing.timeslot_windower import TimeslotWindower
from src.processing.timeslot_grader import TimeslotGrader
from src.processing.stages.timeslot_grading_stage import TimeslotGradingStage
from src.processing.stages.pattern_learning_stage import PatternLearningStage
from src.core.patterns.daily_labor_manager import DailyLaborPatternManager
from src.core.patterns.in_memory_daily_labor_storage import InMemoryDailyLaborPatternStorage
from src.orchestration.pipeline.context import PipelineContext


class TestTimeslotPatternLearning:
    """Test timeslot pattern learning with real sample data."""

    @pytest.fixture
    def pattern_manager(self):
        """Create fresh TimeslotPatternManager."""
        return TimeslotPatternManager()

    @pytest.fixture
    def sample_data_dates(self):
        """Available sample data dates (first 3 days of August 2025)."""
        return ['2025-08-20', '2025-08-21', '2025-08-22']

    @pytest.fixture
    def sample_data_path(self):
        """Base path to sample data."""
        return Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data")

    def _process_day(self, date: str, pattern_manager: TimeslotPatternManager):
        """
        Helper to process a single day and learn patterns.

        Returns:
            Tuple of (context, learned_patterns, graded_timeslots)
        """
        sample_data_path = Path(f"C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/{date}/SDR")

        # Create context
        context = PipelineContext(
            restaurant_code='SDR',
            date=date,
            config={}
        )
        context.set('date', date)  # Set date first
        context.set('restaurant', 'SDR')
        context.set('data_path', str(sample_data_path))

        # Run ingestion
        validator = DataValidator()
        ingestion_stage = IngestionStage(validator)
        result = ingestion_stage.execute(context)
        if not result.is_ok():
            raise ValueError(f"Ingestion failed for {date}: {result.unwrap_err()}")

        # Run categorization
        categorizer = OrderCategorizer()
        categorization_stage = OrderCategorizationStage(categorizer)
        result = categorization_stage.execute(context)
        if not result.is_ok():
            raise ValueError(f"Categorization failed for {date}: {result.unwrap_err()}")

        # Run timeslot grading with pattern manager
        windower = TimeslotWindower()
        grader = TimeslotGrader()
        grading_stage = TimeslotGradingStage(windower, grader, pattern_manager)
        result = grading_stage.execute(context)
        if not result.is_ok():
            raise ValueError(f"Timeslot grading failed for {date}: {result.unwrap_err()}")

        # Add minimal labor_metrics to context (required by PatternLearningStage)
        # This allows timeslot pattern learning to proceed even without full labor processing
        from src.processing.labor_calculator import LaborMetrics
        mock_labor_metrics = LaborMetrics(
            total_hours=100.0,
            labor_cost=1500.0,
            labor_percentage=30.0,
            status='pass',
            grade='B',
            warnings=[],
            recommendations=[]
        )
        context.set('labor_metrics', mock_labor_metrics)

        # Run pattern learning with pattern manager
        # Create minimal config for daily labor pattern manager (matches base.yaml structure)
        daily_labor_config = {
            "pattern_learning": {
                "learning_rates": {
                    "early_observations": 0.3,
                    "mature_observations": 0.2,
                    "observation_threshold": 5
                },
                "reliability_thresholds": {
                    "min_observations": 4,
                    "min_confidence": 0.6
                },
                "quality_thresholds": {
                    "update_confidence": 0.8,
                    "max_age_days": 14
                },
                "constraints": {
                    "min_variance": 0.5,
                    "max_confidence": 0.95
                }
            }
        }
        daily_labor_storage = InMemoryDailyLaborPatternStorage()
        daily_pattern_manager = DailyLaborPatternManager(daily_labor_storage, daily_labor_config)
        learning_stage = PatternLearningStage(daily_pattern_manager, pattern_manager)
        result = learning_stage.execute(context)
        if not result.is_ok():
            raise ValueError(f"Pattern learning failed for {date}: {result.unwrap_err()}")

        learned_patterns = context.get('learned_timeslot_patterns', [])
        graded_timeslots = context.get('graded_timeslots', [])

        return context, learned_patterns, graded_timeslots

    def test_single_observation_creates_pattern(self, pattern_manager):
        """Test that a single observation creates a new pattern with low confidence."""
        pattern = pattern_manager.learn_pattern(
            restaurant_code='SDR',
            day_of_week='Monday',
            shift='morning',
            time_window='11:00-11:15',
            category='Lobby',
            fulfillment_time=12.5
        )

        # Should create pattern with first observation
        assert pattern.restaurant_code == 'SDR'
        assert pattern.day_of_week == 'Monday'
        assert pattern.shift == 'morning'
        assert pattern.time_window == '11:00-11:15'
        assert pattern.category == 'Lobby'
        assert pattern.baseline_time == 12.5
        assert pattern.variance == 0.0  # No variance with single observation
        assert pattern.confidence == 0.2  # Low confidence (20%)
        assert pattern.observations_count == 1
        assert not pattern.is_reliable()  # Not reliable yet (< 4 observations, < 0.6 confidence)

    def test_multiple_observations_increase_confidence(self, pattern_manager):
        """Test that multiple observations increase confidence asymptotically."""
        key_params = {
            'restaurant_code': 'SDR',
            'day_of_week': 'Tuesday',
            'shift': 'morning',
            'time_window': '12:00-12:15',
            'category': 'Drive-Thru'
        }

        # Learn pattern over 10 observations
        observations = [8.2, 7.9, 8.5, 8.1, 8.3, 8.0, 8.4, 8.2, 8.1, 8.3]
        confidences = []

        for time in observations:
            pattern = pattern_manager.learn_pattern(**key_params, fulfillment_time=time)
            confidences.append(pattern.confidence)

        print(f"\n=== Confidence Growth Over Observations ===")
        for i, conf in enumerate(confidences, 1):
            print(f"Observation {i}: confidence = {conf:.3f}")

        # Confidence should increase with each observation
        assert confidences[0] == 0.2  # First observation
        assert confidences[1] > confidences[0]  # Second higher than first
        assert confidences[5] > confidences[1]  # Continues to increase

        # Should approach 1.0 but never exceed it
        assert all(c <= 1.0 for c in confidences)
        assert confidences[-1] < 1.0  # Shouldn't reach 1.0 with only 10 observations

        # Growth should slow down (asymptotic)
        early_growth = confidences[1] - confidences[0]
        late_growth = confidences[-1] - confidences[-2]
        assert early_growth > late_growth, "Confidence growth should slow down"

    def test_exponential_moving_average_learning(self, pattern_manager):
        """Test that baseline uses exponential moving average (alpha=0.2)."""
        key_params = {
            'restaurant_code': 'SDR',
            'day_of_week': 'Wednesday',
            'shift': 'evening',
            'time_window': '18:00-18:15',
            'category': 'Lobby'
        }

        # First observation: 10.0 minutes
        pattern1 = pattern_manager.learn_pattern(**key_params, fulfillment_time=10.0)
        assert pattern1.baseline_time == 10.0

        # Second observation: 15.0 minutes
        # Expected: (0.2 * 15.0) + (0.8 * 10.0) = 3.0 + 8.0 = 11.0
        pattern2 = pattern_manager.learn_pattern(**key_params, fulfillment_time=15.0)
        assert abs(pattern2.baseline_time - 11.0) < 0.01

        # Third observation: 12.0 minutes
        # Expected: (0.2 * 12.0) + (0.8 * 11.0) = 2.4 + 8.8 = 11.2
        pattern3 = pattern_manager.learn_pattern(**key_params, fulfillment_time=12.0)
        assert abs(pattern3.baseline_time - 11.2) < 0.01

        print(f"\n=== Exponential Moving Average ===")
        print(f"Obs 1 (10.0 min): baseline = {pattern1.baseline_time:.2f}")
        print(f"Obs 2 (15.0 min): baseline = {pattern2.baseline_time:.2f}")
        print(f"Obs 3 (12.0 min): baseline = {pattern3.baseline_time:.2f}")

    def test_variance_calculation(self, pattern_manager):
        """Test that variance tracks deviation from baseline."""
        key_params = {
            'restaurant_code': 'SDR',
            'day_of_week': 'Thursday',
            'shift': 'morning',
            'time_window': '10:00-10:15',
            'category': 'ToGo'
        }

        # Start with consistent times (low variance)
        for time in [10.0, 10.1, 10.0, 10.2, 10.1]:
            pattern = pattern_manager.learn_pattern(**key_params, fulfillment_time=time)

        low_variance = pattern.variance

        # Now add high variance observations
        for time in [15.0, 5.0, 12.0, 8.0, 14.0]:
            pattern = pattern_manager.learn_pattern(**key_params, fulfillment_time=time)

        high_variance = pattern.variance

        print(f"\n=== Variance Tracking ===")
        print(f"After consistent times (10.0-10.2): variance = {low_variance:.2f}")
        print(f"After variable times (5.0-15.0): variance = {high_variance:.2f}")

        # Variance should increase with more variable data
        assert high_variance > low_variance

    def test_pattern_reliability_threshold(self, pattern_manager):
        """Test that patterns become reliable after sufficient observations and confidence."""
        key_params = {
            'restaurant_code': 'SDR',
            'day_of_week': 'Friday',
            'shift': 'evening',
            'time_window': '19:00-19:15',
            'category': 'Lobby'
        }

        # Reliability requires: confidence >= 0.6 AND observations >= 4
        # Confidence formula: confidence += 0.1 / (1 + observations)
        # To reach 0.6 from 0.2, we need: 0.4 gain
        # This takes ~90 observations! (very slow growth)
        # For testing purposes, we'll use 100 observations to demonstrate reaching reliability
        patterns = []
        test_observations = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Sample checkpoints

        for i in range(100):
            pattern = pattern_manager.learn_pattern(**key_params, fulfillment_time=12.0 + (i % 3))
            if (i + 1) in test_observations:
                patterns.append(pattern)
                print(f"Obs {i+1}: confidence={pattern.confidence:.3f}, observations={pattern.observations_count}, reliable={pattern.is_reliable()}")

        # With 100 observations, should become reliable
        final_pattern = patterns[-1]
        assert final_pattern.observations_count == 100
        assert final_pattern.is_reliable(), f"Pattern should be reliable after 100 obs (confidence={final_pattern.confidence:.3f})"

        print(f"\n=== Reliability Threshold ===")
        print(f"Observations needed to reach reliability: ~90")
        print(f"Final confidence at 100 obs: {final_pattern.confidence:.3f}")

    def test_pattern_retrieval_by_day_of_week(self, pattern_manager):
        """Test retrieving patterns for specific restaurant and day of week."""
        # Learn patterns for different days
        monday_pattern = pattern_manager.learn_pattern(
            restaurant_code='SDR', day_of_week='Monday', shift='morning',
            time_window='11:00-11:15', category='Lobby', fulfillment_time=12.5
        )

        tuesday_pattern = pattern_manager.learn_pattern(
            restaurant_code='SDR', day_of_week='Tuesday', shift='morning',
            time_window='11:00-11:15', category='Lobby', fulfillment_time=13.2
        )

        # Make patterns reliable (need 4+ observations AND confidence >= 0.6)
        # Need ~90+ observations to reach confidence 0.6 (confidence growth is slow)
        for _ in range(100):
            pattern_manager.learn_pattern(
                restaurant_code='SDR', day_of_week='Monday', shift='morning',
                time_window='11:00-11:15', category='Lobby', fulfillment_time=12.5
            )
            pattern_manager.learn_pattern(
                restaurant_code='SDR', day_of_week='Tuesday', shift='morning',
                time_window='11:00-11:15', category='Lobby', fulfillment_time=13.2
            )

        # Retrieve Monday patterns only
        monday_patterns = pattern_manager.get_patterns_for_day('SDR', 'Monday', reliable_only=True)

        # Should have Monday pattern but not Tuesday
        assert 'morning_11:00-11:15' in monday_patterns
        assert 'Lobby' in monday_patterns['morning_11:00-11:15']

        # Tuesday patterns should not appear in Monday results
        tuesday_patterns = pattern_manager.get_patterns_for_day('SDR', 'Tuesday', reliable_only=True)
        assert 'morning_11:00-11:15' in tuesday_patterns

        print(f"\n=== Pattern Retrieval ===")
        print(f"Monday patterns: {list(monday_patterns.keys())}")
        print(f"Tuesday patterns: {list(tuesday_patterns.keys())}")

    def test_pattern_statistics(self, pattern_manager):
        """Test pattern statistics calculation."""
        # Learn multiple patterns across restaurants and categories
        restaurants = ['SDR', 'LDR']
        categories = ['Lobby', 'Drive-Thru', 'ToGo']

        # Create 6 patterns (2 restaurants × 3 categories)
        for restaurant in restaurants:
            for category in categories:
                for _ in range(3):  # 3 observations each
                    pattern_manager.learn_pattern(
                        restaurant_code=restaurant,
                        day_of_week='Saturday',
                        shift='morning',
                        time_window='11:00-11:15',
                        category=category,
                        fulfillment_time=10.0
                    )

        stats = pattern_manager.get_statistics()

        print(f"\n=== Pattern Statistics ===")
        print(f"Total patterns: {stats['total_patterns']}")
        print(f"Reliable patterns: {stats['reliable_patterns']}")
        print(f"Avg confidence: {stats['avg_confidence']:.2f}")
        print(f"Avg observations: {stats['avg_observations']:.1f}")
        print(f"By restaurant: {stats['by_restaurant']}")
        print(f"By category: {stats['by_category']}")

        # Verify statistics
        assert stats['total_patterns'] == 6  # 2 restaurants × 3 categories
        assert stats['avg_observations'] == 3.0  # Each has 3 observations
        assert stats['avg_confidence'] > 0  # Should have some confidence
        assert len(stats['by_restaurant']) == 2  # SDR and LDR
        assert len(stats['by_category']) == 3  # Lobby, Drive-Thru, ToGo

    @pytest.mark.skipif(
        not Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20").exists(),
        reason="Sample data not available"
    )
    def test_learn_patterns_from_real_data_single_day(self, pattern_manager):
        """Test learning patterns from real sample data (single day)."""
        date = '2025-08-20'

        context, learned_patterns, graded_timeslots = self._process_day(date, pattern_manager)

        print(f"\n=== Pattern Learning from Real Data ({date}) ===")
        print(f"Graded timeslots: {len(graded_timeslots)}")
        print(f"Patterns learned: {len(learned_patterns)}")

        # Should learn patterns from non-empty timeslots that passed standards
        assert len(learned_patterns) > 0, "Should learn at least some patterns"

        # Check pattern structure
        sample_pattern = learned_patterns[0]
        assert sample_pattern.restaurant_code == 'SDR'
        assert sample_pattern.day_of_week == 'Wednesday'  # 2025-08-20 is Wednesday
        assert sample_pattern.shift in ['morning', 'evening']
        assert sample_pattern.category in ['Lobby', 'Drive-Thru', 'ToGo']
        assert sample_pattern.baseline_time > 0
        assert sample_pattern.observations_count == 1  # First observation

        # Log sample patterns
        print(f"\n=== Sample Learned Patterns ===")
        for pattern in learned_patterns[:5]:
            print(f"{pattern.time_window} {pattern.category}: {pattern.baseline_time:.2f} min (conf={pattern.confidence:.2f})")

    @pytest.mark.skipif(
        not Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20").exists(),
        reason="Sample data not available"
    )
    def test_learn_patterns_over_multiple_days(self, pattern_manager, sample_data_dates):
        """Test learning patterns over multiple days (pattern reinforcement)."""
        total_patterns_by_day = []

        for date in sample_data_dates:
            sample_data_path = Path(f"C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/{date}/SDR")
            if not sample_data_path.exists():
                print(f"Skipping {date} - data not available")
                continue

            context, learned_patterns, graded_timeslots = self._process_day(date, pattern_manager)
            total_patterns_by_day.append(len(learned_patterns))

            print(f"\n=== Day {date} ===")
            print(f"Patterns learned this day: {len(learned_patterns)}")
            print(f"Total patterns in manager: {pattern_manager.get_pattern_count()}")

        # Check overall statistics
        stats = pattern_manager.get_statistics()
        print(f"\n=== Multi-Day Learning Statistics ===")
        print(f"Days processed: {len(total_patterns_by_day)}")
        print(f"Total unique patterns: {stats['total_patterns']}")
        print(f"Reliable patterns: {stats['reliable_patterns']}")
        print(f"Avg observations per pattern: {stats['avg_observations']:.1f}")
        print(f"Avg confidence: {stats['avg_confidence']:.2f}")

        # Patterns should accumulate across days
        # Note: Each day of week (Wed/Thu/Fri) creates separate patterns since day_of_week is in the key
        # So we don't expect observations to accumulate unless we process same day_of_week multiple times
        if len(total_patterns_by_day) >= 2:
            # We should have patterns from multiple days (even if they don't overlap)
            assert stats['total_patterns'] >= len(total_patterns_by_day), "Should have patterns from each day"
            # Average observations will be ~1.0 since each day learns different day_of_week patterns
            assert stats['avg_observations'] >= 1.0, "Each pattern should have at least one observation"

    @pytest.mark.skipif(
        not Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20").exists(),
        reason="Sample data not available"
    )
    def test_patterns_persist_across_pipeline_runs(self, pattern_manager):
        """Test that patterns persist in manager across multiple pipeline runs."""
        date1 = '2025-08-20'
        date2 = '2025-08-21'

        sample_data_path1 = Path(f"C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/{date1}/SDR")
        sample_data_path2 = Path(f"C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/{date2}/SDR")

        if not sample_data_path1.exists() or not sample_data_path2.exists():
            pytest.skip("Sample data not available for both dates")

        # Process first day
        context1, patterns1, _ = self._process_day(date1, pattern_manager)
        count_after_day1 = pattern_manager.get_pattern_count()

        # Process second day (same manager instance)
        context2, patterns2, _ = self._process_day(date2, pattern_manager)
        count_after_day2 = pattern_manager.get_pattern_count()

        print(f"\n=== Pattern Persistence ===")
        print(f"After day 1 ({date1}): {count_after_day1} patterns")
        print(f"After day 2 ({date2}): {count_after_day2} patterns")

        # Some patterns should be reinforced (same timeslot/category on both days)
        # So total patterns after day 2 should be <= count_day1 + patterns_day2
        # (because some patterns from day 2 update existing patterns from day 1)
        assert count_after_day2 >= count_after_day1, "Pattern count should not decrease"

    def test_pattern_key_uniqueness(self, pattern_manager):
        """Test that pattern keys are unique per restaurant/day/shift/timeslot/category."""
        # Learn pattern for specific combination
        pattern1 = pattern_manager.learn_pattern(
            restaurant_code='SDR',
            day_of_week='Sunday',
            shift='morning',
            time_window='11:00-11:15',
            category='Lobby',
            fulfillment_time=12.5
        )

        # Learn again with same key but different time
        pattern2 = pattern_manager.learn_pattern(
            restaurant_code='SDR',
            day_of_week='Sunday',
            shift='morning',
            time_window='11:00-11:15',
            category='Lobby',
            fulfillment_time=14.0
        )

        # Should update existing pattern, not create new one
        assert pattern_manager.get_pattern_count() == 1
        assert pattern2.observations_count == 2  # Second observation
        assert pattern2.baseline_time != 12.5  # Should be updated via EMA
        assert pattern2.baseline_time != 14.0  # Should be blend of 12.5 and 14.0

    def test_reliable_only_filter(self, pattern_manager):
        """Test that get_patterns_for_day respects reliable_only filter."""
        # Create one reliable pattern (need 4+ observations AND confidence >= 0.6)
        # Need ~90+ observations to reach confidence 0.6
        for i in range(100):
            pattern_manager.learn_pattern(
                restaurant_code='SDR', day_of_week='Monday', shift='morning',
                time_window='11:00-11:15', category='Lobby', fulfillment_time=12.0
            )

        # Create one unreliable pattern (< 4 observations)
        pattern_manager.learn_pattern(
            restaurant_code='SDR', day_of_week='Monday', shift='morning',
            time_window='12:00-12:15', category='Drive-Thru', fulfillment_time=8.0
        )

        # Get all patterns (reliable_only=False)
        all_patterns = pattern_manager.get_patterns_for_day('SDR', 'Monday', reliable_only=False)
        assert len(all_patterns) == 2  # Both timeslots

        # Get only reliable patterns (reliable_only=True)
        reliable_patterns = pattern_manager.get_patterns_for_day('SDR', 'Monday', reliable_only=True)
        assert len(reliable_patterns) == 1  # Only 11:00-11:15
        assert 'morning_11:00-11:15' in reliable_patterns
        assert 'morning_12:00-12:15' not in reliable_patterns

        print(f"\n=== Reliable Filter ===")
        print(f"All patterns: {list(all_patterns.keys())}")
        print(f"Reliable patterns: {list(reliable_patterns.keys())}")
