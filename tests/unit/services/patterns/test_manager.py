"""
Unit tests for PatternManager

Tests:
- Manager initialization and configuration validation
- Pattern learning (create new + update existing)
- Dynamic learning rates (early vs mature)
- Pattern retrieval with fallbacks
- Reliability checks
- Bulk operations (get all patterns, clear patterns)
- Error handling and edge cases
"""

import pytest

from pipeline.services.patterns.manager import PatternManager
from pipeline.services.patterns.in_memory_storage import InMemoryPatternStorage
from pipeline.models.pattern import Pattern
from pipeline.services import PatternError


# Test configuration fixture
@pytest.fixture
def test_config():
    """Minimal valid configuration for testing."""
    return {
        "pattern_learning": {
            "enabled": True,
            "learning_rates": {
                "early_observations": 0.3,
                "mature_observations": 0.2,
                "observation_threshold": 5
            },
            "reliability_thresholds": {
                "min_confidence": 0.6,
                "min_observations": 4
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


@pytest.fixture
def storage():
    """Fresh in-memory storage for each test."""
    return InMemoryPatternStorage()


@pytest.fixture
def manager(storage, test_config):
    """PatternManager instance with test config and storage."""
    return PatternManager(storage=storage, config=test_config)


class TestPatternManagerInit:
    """Test PatternManager initialization."""

    def test_initialize_with_valid_config(self, storage, test_config):
        """Test successful initialization."""
        manager = PatternManager(storage=storage, config=test_config)

        assert manager.storage is storage
        assert manager.config == test_config
        assert manager._learning_rates["early_observations"] == 0.3

    def test_initialize_missing_pattern_learning_config(self, storage):
        """Test initialization fails with missing pattern_learning config."""
        invalid_config = {"other_config": {}}

        with pytest.raises(PatternError) as exc_info:
            PatternManager(storage=storage, config=invalid_config)

        assert "pattern_learning" in str(exc_info.value)

    def test_initialize_missing_learning_rates(self, storage):
        """Test initialization fails with missing learning_rates."""
        invalid_config = {
            "pattern_learning": {
                "reliability_thresholds": {},
                "quality_thresholds": {},
                "constraints": {}
            }
        }

        with pytest.raises(PatternError) as exc_info:
            PatternManager(storage=storage, config=invalid_config)

        assert "learning_rates" in str(exc_info.value)


class TestPatternLearningCreation:
    """Test creating new patterns via learning."""

    def test_learn_first_observation(self, manager, storage):
        """Test learning creates new pattern from first observation."""
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=85.5,
            observed_staffing=3.2
        )

        assert result.is_ok()
        pattern = result.unwrap()

        assert pattern.restaurant_code == "SDR"
        assert pattern.service_type == "Lobby"
        assert pattern.hour == 12
        assert pattern.day_of_week == 1
        assert pattern.expected_volume == 85.5
        assert pattern.expected_staffing == 3.2
        assert pattern.observations == 1
        assert pattern.confidence > 0.0

        # Verify pattern was saved to storage
        assert storage.count() == 1

    def test_learn_multiple_service_types(self, manager):
        """Test learning patterns for different service types."""
        for service_type in ["Lobby", "Drive-Thru", "ToGo"]:
            result = manager.learn_pattern(
                restaurant_code="SDR",
                service_type=service_type,
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )
            assert result.is_ok()

        # Should have 3 distinct patterns
        all_patterns = manager.get_all_patterns("SDR").unwrap()
        assert len(all_patterns) == 3

    def test_learn_pattern_different_hours(self, manager):
        """Test learning patterns for different hours."""
        for hour in [10, 12, 14, 16]:
            result = manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                observed_volume=float(hour * 10),
                observed_staffing=3.0
            )
            assert result.is_ok()

        all_patterns = manager.get_all_patterns("SDR").unwrap()
        assert len(all_patterns) == 4

    def test_learn_pattern_different_days(self, manager):
        """Test learning patterns for different days of week."""
        for day in range(7):  # Monday-Sunday
            result = manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=day,
                observed_volume=100.0,
                observed_staffing=4.0
            )
            assert result.is_ok()

        all_patterns = manager.get_all_patterns("SDR").unwrap()
        assert len(all_patterns) == 7


class TestPatternLearningUpdates:
    """Test updating existing patterns via learning."""

    def test_learn_second_observation_updates_pattern(self, manager):
        """Test second observation updates existing pattern with EMA."""
        # First observation
        manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=80.0,
            observed_staffing=3.0
        )

        # Second observation
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=100.0,
            observed_staffing=4.0
        )

        assert result.is_ok()
        pattern = result.unwrap()

        # With learning_rate=0.3 (early observations):
        # expected = (1-0.3)*80 + 0.3*100 = 56 + 30 = 86.0
        assert pattern.expected_volume == pytest.approx(86.0, rel=0.01)
        # expected = (1-0.3)*3 + 0.3*4 = 2.1 + 1.2 = 3.3
        assert pattern.expected_staffing == pytest.approx(3.3, rel=0.01)
        assert pattern.observations == 2

        # Still only 1 pattern in storage (updated, not created)
        all_patterns = manager.get_all_patterns("SDR").unwrap()
        assert len(all_patterns) == 1

    def test_learn_confidence_increases_with_observations(self, manager):
        """Test confidence increases asymptotically with observations."""
        confidences = []

        for i in range(10):
            result = manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )
            pattern = result.unwrap()
            confidences.append(pattern.confidence)

        # Confidence should increase with each observation
        for i in range(len(confidences) - 1):
            assert confidences[i] < confidences[i + 1]

        # But never exceed max_confidence (0.95)
        assert all(c <= 0.95 for c in confidences)


class TestDynamicLearningRates:
    """Test dynamic learning rate based on observation count."""

    def test_early_observations_use_high_learning_rate(self, manager):
        """Test observations < 5 use early_observations rate (0.3)."""
        # First observation
        manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=80.0,
            observed_staffing=3.0
        )

        # Second observation (still early)
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=100.0,
            observed_staffing=4.0
        )

        pattern = result.unwrap()

        # With early rate (0.3): 80*0.7 + 100*0.3 = 86.0
        assert pattern.expected_volume == pytest.approx(86.0, rel=0.01)

    def test_mature_observations_use_low_learning_rate(self, manager):
        """Test observations >= 5 use mature_observations rate (0.2)."""
        # Create pattern with 5 observations
        for i in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        # Get current state (all observations = 100)
        pattern_before = manager.storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        assert pattern_before.expected_volume == pytest.approx(100.0, rel=0.01)

        # 6th observation (mature rate should apply)
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=80.0,  # Different value
            observed_staffing=3.0
        )

        pattern = result.unwrap()

        # With mature rate (0.2): 100*0.8 + 80*0.2 = 80 + 16 = 96.0
        assert pattern.expected_volume == pytest.approx(96.0, rel=0.01)
        assert pattern.observations == 6

    def test_learning_rate_threshold_configurable(self, storage):
        """Test learning rate threshold respects config."""
        custom_config = {
            "pattern_learning": {
                "learning_rates": {
                    "early_observations": 0.5,
                    "mature_observations": 0.1,
                    "observation_threshold": 3  # Lower threshold
                },
                "reliability_thresholds": {"min_confidence": 0.6, "min_observations": 4},
                "quality_thresholds": {"update_confidence": 0.8, "max_age_days": 14},
                "constraints": {"min_variance": 0.5, "max_confidence": 0.95}
            }
        }

        manager = PatternManager(storage=storage, config=custom_config)

        # Create pattern with 3 observations (at threshold)
        for _ in range(3):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        pattern_before = manager.storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()

        # 4th observation should use mature rate (0.1)
        manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=80.0,
            observed_staffing=3.0
        )

        pattern_after = manager.storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()

        # With mature rate (0.1): 100*0.9 + 80*0.1 = 90 + 8 = 98.0
        assert pattern_after.expected_volume == pytest.approx(98.0, rel=0.01)


class TestPatternRetrieval:
    """Test pattern retrieval with exact match."""

    def test_get_existing_reliable_pattern(self, manager):
        """Test retrieving existing reliable pattern."""
        # Create reliable pattern (4+ observations, confidence >= 0.6)
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        result = manager.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern is not None
        assert pattern.restaurant_code == "SDR"
        assert pattern.hour == 12

    def test_get_nonexistent_pattern_returns_none(self, manager):
        """Test retrieving non-existent pattern returns None."""
        result = manager.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        assert result.unwrap() is None

    def test_get_unreliable_pattern_returns_none(self, manager):
        """Test retrieving unreliable pattern returns None."""
        # Create pattern with only 1 observation (below min_observations=4)
        manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=100.0,
            observed_staffing=4.0
        )

        result = manager.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        assert result.unwrap() is None  # Not reliable yet

    def test_get_pattern_without_fallbacks(self, manager):
        """Test get_pattern with use_fallbacks=False."""
        # Create pattern for hour 12, day 1
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        # Try to get pattern for different day (no exact match)
        result = manager.get_pattern(
            "SDR", "Lobby", 12, 2,  # day=2 doesn't exist
            use_fallbacks=False
        )

        assert result.is_ok()
        assert result.unwrap() is None  # No fallback attempted


class TestPatternFallbacks:
    """Test pattern fallback chain."""

    def test_fallback_to_hourly_average(self, manager):
        """Test fallback returns hourly average across all days."""
        # Create patterns for same hour (12) across multiple days
        for day in range(3):  # Days 0, 1, 2
            for _ in range(5):  # Make them reliable
                manager.learn_pattern(
                    restaurant_code="SDR",
                    service_type="Lobby",
                    hour=12,
                    day_of_week=day,
                    observed_volume=100.0 + (day * 10),  # 100, 110, 120
                    observed_staffing=4.0
                )

        # Request pattern for day that doesn't exist (day 3)
        result = manager.get_pattern("SDR", "Lobby", 12, 3, use_fallbacks=True)

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern is not None

        # Should be average: (100 + 110 + 120) / 3 = 110.0
        assert pattern.expected_volume == pytest.approx(110.0, rel=0.01)
        assert pattern.metadata.get("is_fallback") is True
        assert pattern.metadata.get("days_averaged") == 3
        # Fallback uses day_of_week=0 (Monday) as marker
        assert pattern.day_of_week == 0

    def test_fallback_returns_none_if_no_patterns_exist(self, manager):
        """Test fallback returns None if no patterns for that hour."""
        result = manager.get_pattern("SDR", "Lobby", 12, 1, use_fallbacks=True)

        assert result.is_ok()
        assert result.unwrap() is None

    def test_fallback_only_uses_same_hour(self, manager):
        """Test fallback averages same hour only, not other hours."""
        # Create patterns for different hours
        for hour in [10, 12, 14]:
            for _ in range(5):
                manager.learn_pattern(
                    restaurant_code="SDR",
                    service_type="Lobby",
                    hour=hour,
                    day_of_week=0,
                    observed_volume=float(hour * 10),  # 100, 120, 140
                    observed_staffing=4.0
                )

        # Request hour 12, day that doesn't exist
        result = manager.get_pattern("SDR", "Lobby", 12, 5, use_fallbacks=True)

        pattern = result.unwrap()

        # Should only average hour 12 patterns (only 1 exists with volume=120)
        assert pattern.expected_volume == pytest.approx(120.0, rel=0.01)

    def test_fallback_respects_service_type(self, manager):
        """Test fallback only averages same service type."""
        # Create Lobby pattern
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=0,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        # Create Drive-Thru pattern
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Drive-Thru",
                hour=12,
                day_of_week=0,
                observed_volume=200.0,
                observed_staffing=5.0
            )

        # Request Lobby fallback
        result = manager.get_pattern("SDR", "Lobby", 12, 5, use_fallbacks=True)
        lobby_pattern = result.unwrap()

        # Should only use Lobby patterns (volume=100)
        assert lobby_pattern.expected_volume == pytest.approx(100.0, rel=0.01)


class TestBulkOperations:
    """Test bulk pattern operations."""

    def test_get_patterns_for_service(self, manager):
        """Test getting all patterns for a service type."""
        # Create patterns for Lobby
        for hour in [10, 12, 14]:
            for _ in range(5):
                manager.learn_pattern(
                    restaurant_code="SDR",
                    service_type="Lobby",
                    hour=hour,
                    day_of_week=1,
                    observed_volume=100.0,
                    observed_staffing=4.0
                )

        # Create patterns for Drive-Thru
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Drive-Thru",
                hour=12,
                day_of_week=1,
                observed_volume=200.0,
                observed_staffing=5.0
            )

        result = manager.get_patterns_for_service("SDR", "Lobby")

        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 3
        assert all(p.service_type == "Lobby" for p in patterns)

    def test_get_all_patterns(self, manager):
        """Test getting all patterns for a restaurant."""
        # Create patterns across multiple service types
        for service in ["Lobby", "Drive-Thru", "ToGo"]:
            for hour in [10, 12]:
                manager.learn_pattern(
                    restaurant_code="SDR",
                    service_type=service,
                    hour=hour,
                    day_of_week=1,
                    observed_volume=100.0,
                    observed_staffing=4.0
                )

        result = manager.get_all_patterns("SDR")

        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 6  # 3 services * 2 hours

    def test_clear_patterns(self, manager):
        """Test clearing all patterns for a restaurant."""
        # Create multiple patterns
        for hour in range(10, 15):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        assert manager.get_all_patterns("SDR").unwrap() != []

        result = manager.clear_patterns("SDR")

        assert result.is_ok()
        count = result.unwrap()
        assert count == 5  # 5 patterns deleted

        # Verify all cleared
        assert manager.get_all_patterns("SDR").unwrap() == []

    def test_clear_patterns_empty_restaurant(self, manager):
        """Test clearing patterns when none exist."""
        result = manager.clear_patterns("SDR")

        assert result.is_ok()
        assert result.unwrap() == 0


class TestReliabilityThresholds:
    """Test reliability threshold configuration."""

    def test_reliability_threshold_from_config(self, storage):
        """Test reliability thresholds respect config values."""
        custom_config = {
            "pattern_learning": {
                "learning_rates": {
                    "early_observations": 0.3,
                    "mature_observations": 0.2,
                    "observation_threshold": 5
                },
                "reliability_thresholds": {
                    "min_confidence": 0.8,  # Higher threshold
                    "min_observations": 10  # Higher threshold
                },
                "quality_thresholds": {"update_confidence": 0.8, "max_age_days": 14},
                "constraints": {"min_variance": 0.5, "max_confidence": 0.95}
            }
        }

        manager = PatternManager(storage=storage, config=custom_config)

        # Create pattern with 5 observations (below new min_observations=10)
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        result = manager.get_pattern("SDR", "Lobby", 12, 1)

        # Should be unreliable (observations=5 < min_observations=10)
        assert result.unwrap() is None

    def test_pattern_becomes_reliable_after_threshold(self, manager):
        """Test pattern becomes available after reaching reliability threshold."""
        # Add observations one at a time
        for i in range(1, 6):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

            result = manager.get_pattern("SDR", "Lobby", 12, 1)

            if i < 4:  # Below min_observations=4
                assert result.unwrap() is None
            else:  # >= min_observations=4
                assert result.unwrap() is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_learn_pattern_with_zero_values(self, manager):
        """Test learning pattern with zero volume/staffing."""
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            observed_volume=0.0,
            observed_staffing=0.0
        )

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.expected_volume == 0.0
        assert pattern.expected_staffing == 0.0

    def test_learn_pattern_with_negative_hour_fails(self, manager):
        """Test learning pattern with invalid hour fails."""
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=-1,  # Invalid
            day_of_week=1,
            observed_volume=100.0,
            observed_staffing=4.0
        )

        assert result.is_err()

    def test_learn_pattern_with_invalid_day_fails(self, manager):
        """Test learning pattern with invalid day_of_week fails."""
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=7,  # Invalid (must be 0-6)
            observed_volume=100.0,
            observed_staffing=4.0
        )

        assert result.is_err()

    def test_learn_pattern_with_invalid_service_type_fails(self, manager):
        """Test learning pattern with invalid service type fails."""
        result = manager.learn_pattern(
            restaurant_code="SDR",
            service_type="InvalidService",
            hour=12,
            day_of_week=1,
            observed_volume=100.0,
            observed_staffing=4.0
        )

        assert result.is_err()

    def test_multiple_restaurants_isolated(self, manager):
        """Test patterns for different restaurants don't interfere."""
        # Create pattern for SDR
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=100.0,
                observed_staffing=4.0
            )

        # Create pattern for T12
        for _ in range(5):
            manager.learn_pattern(
                restaurant_code="T12",
                service_type="Lobby",
                hour=12,
                day_of_week=1,
                observed_volume=200.0,
                observed_staffing=5.0
            )

        # Verify isolation
        sdr_pattern = manager.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        t12_pattern = manager.get_pattern("T12", "Lobby", 12, 1).unwrap()

        assert sdr_pattern.expected_volume == pytest.approx(100.0, rel=0.01)
        assert t12_pattern.expected_volume == pytest.approx(200.0, rel=0.01)
