"""
Unit tests for Pattern DTO

Tests:
- Pattern creation and validation
- Service type validation
- Hour and day_of_week bounds
- Confidence and observations validation
- Serialization/deserialization
- Pattern key generation
- Reliability checks
- Pattern updates with exponential moving average
"""

import pytest
from datetime import datetime

from pipeline.models.pattern import Pattern
from pipeline.services import ValidationError


class TestPatternCreation:
    """Test Pattern creation and validation."""

    def test_create_basic_pattern(self):
        """Test creating basic traffic pattern."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.restaurant_code == "SDR"
        assert pattern.service_type == "Lobby"
        assert pattern.hour == 12
        assert pattern.day_of_week == 1
        assert pattern.expected_volume == 85.5
        assert pattern.expected_staffing == 3.2
        assert pattern.confidence == 0.75
        assert pattern.observations == 120

    def test_create_drive_thru_pattern(self):
        """Test creating Drive-Thru pattern."""
        result = Pattern.create(
            restaurant_code="T12",
            service_type="Drive-Thru",
            hour=18,
            day_of_week=5,
            expected_volume=150.0,
            expected_staffing=5.5,
            confidence=0.85,
            observations=200
        )

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.service_type == "Drive-Thru"
        assert pattern.expected_volume == 150.0

    def test_create_togo_pattern(self):
        """Test creating ToGo pattern."""
        result = Pattern.create(
            restaurant_code="TK9",
            service_type="ToGo",
            hour=7,
            day_of_week=0,
            expected_volume=25.0,
            expected_staffing=1.5,
            confidence=0.60,
            observations=50
        )

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.service_type == "ToGo"

    def test_create_with_metadata(self):
        """Test creating pattern with metadata."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120,
            metadata={"season": "summer", "notes": "Peak lunch hour"}
        )

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.metadata["season"] == "summer"
        assert pattern.metadata["notes"] == "Peak lunch hour"

    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        assert pattern.last_updated is not None
        assert pattern.created_at is not None
        assert "T" in pattern.last_updated  # ISO 8601 format
        assert "T" in pattern.created_at

    def test_immutability(self):
        """Test Pattern is immutable (frozen dataclass)."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        # Should not be able to modify frozen fields
        with pytest.raises(Exception):  # FrozenInstanceError
            pattern.expected_volume = 100.0  # type: ignore

        with pytest.raises(Exception):
            pattern.confidence = 0.9  # type: ignore


class TestPatternValidation:
    """Test Pattern validation logic."""

    def test_validate_missing_restaurant_code(self):
        """Test validation fails for missing restaurant_code."""
        result = Pattern.create(
            restaurant_code="",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "restaurant_code" in error.message

    def test_validate_invalid_service_type(self):
        """Test validation fails for invalid service_type."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="InvalidType",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "service_type" in error.message

    def test_validate_hour_negative(self):
        """Test validation fails for negative hour."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=-1,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "hour" in error.message

    def test_validate_hour_too_large(self):
        """Test validation fails for hour > 23."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=24,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "hour" in error.message

    def test_validate_day_of_week_negative(self):
        """Test validation fails for negative day_of_week."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=-1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "day_of_week" in error.message

    def test_validate_day_of_week_too_large(self):
        """Test validation fails for day_of_week > 6."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=7,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "day_of_week" in error.message

    def test_validate_negative_volume(self):
        """Test validation fails for negative expected_volume."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=-10.0,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "expected_volume" in error.message

    def test_validate_negative_staffing(self):
        """Test validation fails for negative expected_staffing."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=-1.0,
            confidence=0.75,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "expected_staffing" in error.message

    def test_validate_confidence_too_low(self):
        """Test validation fails for confidence < 0.0."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=-0.1,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "confidence" in error.message

    def test_validate_confidence_too_high(self):
        """Test validation fails for confidence > 1.0."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=1.5,
            observations=120
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "confidence" in error.message

    def test_validate_negative_observations(self):
        """Test validation fails for negative observations."""
        result = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=-5
        )

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "observations" in error.message


class TestPatternSerialization:
    """Test Pattern serialization and deserialization."""

    def test_to_dict(self):
        """Test serializing Pattern to dictionary."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120,
            metadata={"season": "summer"}
        ).unwrap()

        data = pattern.to_dict()

        assert data["restaurant_code"] == "SDR"
        assert data["service_type"] == "Lobby"
        assert data["hour"] == 12
        assert data["day_of_week"] == 1
        assert data["expected_volume"] == 85.5
        assert data["expected_staffing"] == 3.2
        assert data["confidence"] == 0.75
        assert data["observations"] == 120
        assert data["metadata"]["season"] == "summer"

    def test_from_dict_success(self):
        """Test deserializing Pattern from dictionary."""
        data = {
            "restaurant_code": "T12",
            "service_type": "Drive-Thru",
            "hour": 18,
            "day_of_week": 5,
            "expected_volume": 150.0,
            "expected_staffing": 5.5,
            "confidence": 0.85,
            "observations": 200,
            "last_updated": "2024-01-15T10:30:00",
            "created_at": "2024-01-01T00:00:00",
            "metadata": {"notes": "Peak dinner"}
        }

        result = Pattern.from_dict(data)

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.restaurant_code == "T12"
        assert pattern.service_type == "Drive-Thru"
        assert pattern.expected_volume == 150.0
        assert pattern.metadata["notes"] == "Peak dinner"

    def test_from_dict_missing_field(self):
        """Test deserialization fails with missing required field."""
        data = {
            "restaurant_code": "SDR",
            "service_type": "Lobby",
            # Missing hour
            "day_of_week": 1,
            "expected_volume": 85.5,
            "expected_staffing": 3.2,
            "confidence": 0.75,
            "observations": 120
        }

        result = Pattern.from_dict(data)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, ValidationError)
        assert "Missing required field" in error.message

    def test_roundtrip_serialization(self):
        """Test roundtrip: to_dict -> from_dict."""
        original = Pattern.create(
            restaurant_code="TK9",
            service_type="ToGo",
            hour=7,
            day_of_week=3,
            expected_volume=42.5,
            expected_staffing=2.0,
            confidence=0.68,
            observations=75,
            metadata={"shift": "morning"}
        ).unwrap()

        data = original.to_dict()
        restored = Pattern.from_dict(data).unwrap()

        assert restored.restaurant_code == original.restaurant_code
        assert restored.service_type == original.service_type
        assert restored.hour == original.hour
        assert restored.day_of_week == original.day_of_week
        assert restored.expected_volume == original.expected_volume
        assert restored.expected_staffing == original.expected_staffing
        assert restored.confidence == original.confidence
        assert restored.observations == original.observations
        assert restored.metadata["shift"] == "morning"


class TestPatternHelpers:
    """Test Pattern helper methods."""

    def test_get_key(self):
        """Test get_key() generates unique pattern key."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        key = pattern.get_key()
        assert key == "SDR:Lobby:12:1"

    def test_get_key_uniqueness(self):
        """Test different patterns have different keys."""
        pattern1 = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        pattern2 = Pattern.create(
            restaurant_code="SDR",
            service_type="Drive-Thru",  # Different service type
            hour=12,
            day_of_week=1,
            expected_volume=100.0,
            expected_staffing=4.0,
            confidence=0.80,
            observations=150
        ).unwrap()

        assert pattern1.get_key() != pattern2.get_key()

    def test_is_reliable_true(self):
        """Test is_reliable() returns True for reliable pattern."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,  # > 0.6 default
            observations=120  # > 10 default
        ).unwrap()

        assert pattern.is_reliable() is True

    def test_is_reliable_false_low_confidence(self):
        """Test is_reliable() returns False for low confidence."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.5,  # < 0.6 default
            observations=120
        ).unwrap()

        assert pattern.is_reliable() is False

    def test_is_reliable_false_low_observations(self):
        """Test is_reliable() returns False for low observations."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=5  # < 10 default
        ).unwrap()

        assert pattern.is_reliable() is False

    def test_is_reliable_custom_thresholds(self):
        """Test is_reliable() with custom thresholds."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.70,
            observations=25
        ).unwrap()

        # Strict thresholds
        assert pattern.is_reliable(min_confidence=0.8, min_observations=30) is False

        # Lenient thresholds
        assert pattern.is_reliable(min_confidence=0.6, min_observations=20) is True

    def test_repr(self):
        """Test __repr__ method."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        repr_str = repr(pattern)
        assert "Pattern(" in repr_str
        assert "restaurant=SDR" in repr_str
        assert "service=Lobby" in repr_str
        assert "hour=12" in repr_str
        assert "dow=1" in repr_str
        assert "vol=85.5" in repr_str
        assert "staff=3.2" in repr_str
        assert "conf=0.75" in repr_str
        assert "obs=120" in repr_str


class TestPatternUpdates:
    """Test Pattern update logic with exponential moving average."""

    def test_with_updated_prediction(self):
        """Test updating pattern with new observation."""
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.70,
            observations=100
        ).unwrap()

        # New observation: higher volume and staffing
        updated = original.with_updated_prediction(
            new_volume=100.0,
            new_staffing=4.0,
            learning_rate=0.3
        )

        # Check exponential moving average applied
        # expected = (1 - 0.3) * 80.0 + 0.3 * 100.0 = 56.0 + 30.0 = 86.0
        assert updated.expected_volume == pytest.approx(86.0, rel=0.01)
        # expected = (1 - 0.3) * 3.0 + 0.3 * 4.0 = 2.1 + 1.2 = 3.3
        assert updated.expected_staffing == pytest.approx(3.3, rel=0.01)

        # Observations incremented
        assert updated.observations == 101

        # Confidence increased (but capped at 1.0)
        assert updated.confidence > original.confidence
        assert updated.confidence <= 1.0

        # Original pattern unchanged (immutable)
        assert original.expected_volume == 80.0
        assert original.observations == 100

    def test_with_updated_prediction_low_learning_rate(self):
        """Test pattern update with low learning rate (slow adaptation)."""
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.70,
            observations=100
        ).unwrap()

        updated = original.with_updated_prediction(
            new_volume=100.0,
            new_staffing=4.0,
            learning_rate=0.1  # Low learning rate = slow adaptation
        )

        # Less change with lower learning rate
        # expected = (1 - 0.1) * 80.0 + 0.1 * 100.0 = 72.0 + 10.0 = 82.0
        assert updated.expected_volume == pytest.approx(82.0, rel=0.01)

    def test_with_updated_prediction_high_learning_rate(self):
        """Test pattern update with high learning rate (fast adaptation)."""
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.70,
            observations=100
        ).unwrap()

        updated = original.with_updated_prediction(
            new_volume=100.0,
            new_staffing=4.0,
            learning_rate=0.5  # High learning rate = fast adaptation
        )

        # More change with higher learning rate
        # expected = (1 - 0.5) * 80.0 + 0.5 * 100.0 = 40.0 + 50.0 = 90.0
        assert updated.expected_volume == pytest.approx(90.0, rel=0.01)

    def test_with_updated_prediction_preserves_identity(self):
        """Test that pattern updates preserve restaurant/service/hour/day."""
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.70,
            observations=100
        ).unwrap()

        updated = original.with_updated_prediction(
            new_volume=100.0,
            new_staffing=4.0
        )

        # Identity fields preserved
        assert updated.restaurant_code == original.restaurant_code
        assert updated.service_type == original.service_type
        assert updated.hour == original.hour
        assert updated.day_of_week == original.day_of_week
        assert updated.get_key() == original.get_key()

        # Created timestamp preserved
        assert updated.created_at == original.created_at

        # Last updated changed (or same if created in same microsecond - check it exists)
        assert updated.last_updated is not None

    def test_confidence_growth(self):
        """Test that confidence grows asymptotically with observations."""
        pattern = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.50,
            observations=1  # Very few observations
        ).unwrap()

        # Update multiple times
        for _ in range(10):
            pattern = pattern.with_updated_prediction(
                new_volume=80.0,
                new_staffing=3.0
            )

        # Confidence should have grown
        assert pattern.confidence > 0.50
        # But shouldn't exceed 1.0
        assert pattern.confidence <= 1.0
        # Observations incremented
        assert pattern.observations == 11
