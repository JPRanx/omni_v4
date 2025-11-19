"""
Integration test for timeslot windowing and grading with real sample data.

Verifies that TimeSlotWindower and TimeslotGrader work together correctly
with actual order data from SDR 2025-08-20.
"""

import pytest
from pathlib import Path

from src.ingestion.csv_data_source import CSVDataSource
from src.ingestion.data_validator import DataValidator
from src.processing.stages.ingestion_stage import IngestionStage
from src.processing.stages.order_categorization_stage import OrderCategorizationStage
from src.processing.order_categorizer import OrderCategorizer
from src.processing.timeslot_windower import TimeslotWindower
from src.processing.timeslot_grader import TimeslotGrader
from src.orchestration.pipeline.context import PipelineContext


class TestTimeslotIntegration:
    """Test timeslot windowing and grading with real sample data."""

    @pytest.fixture
    def sample_data_path(self):
        """Path to SDR sample data."""
        return Path("C:/Users/Jorge Alexander/omni_v4/tests/fixtures/sample_data/2025-08-20/SDR")

    @pytest.fixture
    def categorized_orders(self, sample_data_path):
        """Load and categorize orders from sample data."""
        # Run ingestion
        validator = DataValidator()
        ingestion_stage = IngestionStage(validator)

        context = PipelineContext(
            restaurant_code='SDR',
            date='2025-08-20',
            config={}
        )
        context.set('date', '2025-08-20')
        context.set('restaurant', 'SDR')
        context.set('data_path', str(sample_data_path))

        result = ingestion_stage.execute(context)
        assert result.is_ok(), f"Ingestion failed: {result.unwrap_err()}"

        # Run categorization
        categorizer = OrderCategorizer()
        categorization_stage = OrderCategorizationStage(categorizer)

        result = categorization_stage.execute(context)
        assert result.is_ok(), f"Categorization failed: {result.unwrap_err()}"

        return context.get('categorized_orders')

    def test_create_timeslots_from_real_data(self, categorized_orders):
        """Test creating timeslots from real sample data."""
        windower = TimeslotWindower()

        result = windower.create_timeslots(categorized_orders, '2025-08-20')

        assert result.is_ok(), f"Failed to create timeslots: {result.unwrap_err()}"

        timeslots = result.unwrap()

        # Should have both shifts
        assert 'morning' in timeslots
        assert 'evening' in timeslots

        # Morning: 6 AM to 2 PM = 8 hours × 4 slots = 32 slots
        assert len(timeslots['morning']) == 32

        # Evening: 2 PM to 10 PM = 8 hours × 4 slots = 32 slots
        assert len(timeslots['evening']) == 32

        # Total should be 64 slots (not 96, as we only track two shifts)
        total_slots = len(timeslots['morning']) + len(timeslots['evening'])
        assert total_slots == 64

        print(f"\n=== Timeslot Creation Results ===")
        print(f"Morning slots: {len(timeslots['morning'])}")
        print(f"Evening slots: {len(timeslots['evening'])}")

        # Count non-empty slots
        morning_active = sum(1 for s in timeslots['morning'] if not s.is_empty)
        evening_active = sum(1 for s in timeslots['evening'] if not s.is_empty)

        print(f"Morning active: {morning_active}/{len(timeslots['morning'])}")
        print(f"Evening active: {evening_active}/{len(timeslots['evening'])}")

        # Total order counts in timeslots (with overlap) should be >= original orders
        # because orders can span multiple 15-minute windows during preparation
        morning_orders = sum(s.total_orders for s in timeslots['morning'])
        evening_orders = sum(s.total_orders for s in timeslots['evening'])
        total_timeslot_orders = morning_orders + evening_orders

        print(f"Orders in timeslots: {total_timeslot_orders}")
        print(f"Original orders: {len(categorized_orders)}")

        # With overlap counting (matching V3 behavior), total timeslot orders >= original orders
        assert total_timeslot_orders >= len(categorized_orders), \
            f"Order count should be >= original due to overlap: {total_timeslot_orders} >= {len(categorized_orders)}"

    def test_grade_timeslots(self, categorized_orders):
        """Test grading timeslots with real data."""
        windower = TimeslotWindower()
        grader = TimeslotGrader()

        # Create timeslots
        result = windower.create_timeslots(categorized_orders, '2025-08-20')
        assert result.is_ok()
        timeslots = result.unwrap()

        # Grade all timeslots (without historical patterns first time)
        graded_timeslots = grader.grade_all_timeslots(timeslots)

        print(f"\n=== Timeslot Grading Results ===")

        # Morning shift analysis
        morning_slots = graded_timeslots['morning']
        morning_non_empty = [s for s in morning_slots if not s.is_empty]
        morning_passed = sum(1 for s in morning_non_empty if s.passed_standards)

        print(f"\nMorning Shift:")
        print(f"  Non-empty slots: {len(morning_non_empty)}")
        print(f"  Passed standards: {morning_passed}/{len(morning_non_empty)}")
        if morning_non_empty:
            morning_pass_rate = morning_passed / len(morning_non_empty) * 100
            print(f"  Pass rate: {morning_pass_rate:.1f}%")

        # Evening shift analysis
        evening_slots = graded_timeslots['evening']
        evening_non_empty = [s for s in evening_slots if not s.is_empty]
        evening_passed = sum(1 for s in evening_non_empty if s.passed_standards)

        print(f"\nEvening Shift:")
        print(f"  Non-empty slots: {len(evening_non_empty)}")
        print(f"  Passed standards: {evening_passed}/{len(evening_non_empty)}")
        if evening_non_empty:
            evening_pass_rate = evening_passed / len(evening_non_empty) * 100
            print(f"  Pass rate: {evening_pass_rate:.1f}%")

        # Check streak tracking
        morning_hot_streaks = [s for s in morning_non_empty if s.streak_type == 'hot']
        morning_cold_streaks = [s for s in morning_non_empty if s.streak_type == 'cold']

        print(f"\nStreak Analysis:")
        print(f"  Morning hot streaks: {len(morning_hot_streaks)}")
        print(f"  Morning cold streaks: {len(morning_cold_streaks)}")

        # Sample a few timeslots
        print(f"\n=== Sample Timeslots ===")
        sample_morning = [s for s in morning_slots if not s.is_empty][:3]
        for slot in sample_morning:
            print(f"\n{slot.time_window} ({slot.shift}):")
            print(f"  Orders: {slot.total_orders} (L:{slot.lobby_count} D:{slot.drive_thru_count} T:{slot.togo_count})")
            print(f"  Avg fulfillment: {slot.avg_fulfillment:.1f} min")
            print(f"  Passed: {slot.passed_standards}")
            print(f"  Pass rate: {slot.pass_rate_standards:.1f}%")
            print(f"  Streak: {slot.streak_type or 'none'}")
            print(f"  Failures: {len(slot.failures)}")

    def test_capacity_metrics(self, categorized_orders):
        """Test capacity utilization metrics."""
        windower = TimeslotWindower()

        result = windower.create_timeslots(categorized_orders, '2025-08-20')
        assert result.is_ok()
        timeslots = result.unwrap()

        # Calculate capacity metrics
        capacity = windower.calculate_capacity_metrics(timeslots)

        print(f"\n=== Capacity Analysis ===")
        print(f"\nMorning Shift:")
        print(f"  Total slots: {capacity['morning']['total_slots']}")
        print(f"  Active slots: {capacity['morning']['active_slots']}")
        print(f"  Utilization: {capacity['morning']['utilization_pct']}%")
        print(f"  Total orders: {capacity['morning']['total_orders']}")
        print(f"  Peak orders: {capacity['morning']['peak_orders']}")

        print(f"\nEvening Shift:")
        print(f"  Total slots: {capacity['evening']['total_slots']}")
        print(f"  Active slots: {capacity['evening']['active_slots']}")
        print(f"  Utilization: {capacity['evening']['utilization_pct']}%")
        print(f"  Total orders: {capacity['evening']['total_orders']}")
        print(f"  Peak orders: {capacity['evening']['peak_orders']}")

        # Verify metrics make sense
        assert capacity['morning']['total_slots'] == 32
        assert capacity['evening']['total_slots'] == 32
        assert capacity['morning']['active_slots'] <= capacity['morning']['total_slots']
        assert capacity['evening']['active_slots'] <= capacity['evening']['total_slots']

    def test_peak_timeslots(self, categorized_orders):
        """Test peak timeslot identification."""
        windower = TimeslotWindower()

        result = windower.create_timeslots(categorized_orders, '2025-08-20')
        assert result.is_ok()
        timeslots = result.unwrap()

        # Get peak timeslots
        peak_slots = windower.get_peak_timeslots(timeslots)

        print(f"\n=== Peak Timeslots ===")
        print(f"Total peak slots: {len(peak_slots)}")

        # Peak times should be:
        # - Lunch: 11:30 AM - 1:00 PM (6 slots)
        # - Dinner: 5:30 PM - 7:30 PM (8 slots)
        # Total: 14 slots

        for slot in peak_slots[:5]:
            print(f"  {slot.time_window} ({slot.shift}): {slot.total_orders} orders")

        # Verify we found peak times
        assert len(peak_slots) > 0, "Should have identified some peak timeslots"

    def test_timeslot_to_dict(self, categorized_orders):
        """Test TimeslotDTO serialization."""
        windower = TimeslotWindower()
        grader = TimeslotGrader()

        result = windower.create_timeslots(categorized_orders, '2025-08-20')
        assert result.is_ok()
        timeslots = result.unwrap()

        # Grade timeslots
        graded = grader.grade_all_timeslots(timeslots)

        # Get a non-empty slot
        sample_slot = next(s for s in graded['morning'] if not s.is_empty)

        # Convert to dict
        slot_dict = sample_slot.to_dict()

        # Verify required fields
        assert 'time_window' in slot_dict
        assert 'shift' in slot_dict
        assert 'orders' in slot_dict
        assert 'lobby' in slot_dict
        assert 'drive_thru' in slot_dict
        assert 'togo' in slot_dict
        assert 'avg_fulfillment' in slot_dict
        assert 'passed_standards' in slot_dict
        assert 'pass_rate_standards' in slot_dict

        print(f"\n=== Sample Timeslot Dict ===")
        print(f"Time: {slot_dict['time_window']}")
        print(f"Orders: {slot_dict['orders']}")
        print(f"Passed: {slot_dict['passed_standards']}")
        print(f"Pass rate: {slot_dict['pass_rate_standards']}%")
