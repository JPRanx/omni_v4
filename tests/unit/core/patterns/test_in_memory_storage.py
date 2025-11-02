"""
Unit tests for InMemoryPatternStorage

Tests:
- Pattern save/retrieve operations
- Pattern update/upsert operations
- Pattern deletion
- Pattern listing and filtering
- Error handling
- Storage state management
"""

import pytest

from src.core.patterns.in_memory_storage import InMemoryPatternStorage
from src.models.pattern import Pattern
from src.core import PatternError


class TestInMemoryStorageBasics:
    """Test basic InMemoryPatternStorage operations."""

    def test_initialize_empty_storage(self):
        """Test initializing empty storage."""
        storage = InMemoryPatternStorage()
        assert storage.count() == 0

    def test_save_pattern_success(self):
        """Test saving a new pattern."""
        storage = InMemoryPatternStorage()

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

        result = storage.save_pattern(pattern)

        assert result.is_ok()
        assert result.unwrap() is True
        assert storage.count() == 1

    def test_save_duplicate_pattern_fails(self):
        """Test saving duplicate pattern fails."""
        storage = InMemoryPatternStorage()

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

        # Save first time - should succeed
        storage.save_pattern(pattern)

        # Save again - should fail
        result = storage.save_pattern(pattern)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, PatternError)
        assert "already exists" in error.message

    def test_get_pattern_success(self):
        """Test retrieving existing pattern."""
        storage = InMemoryPatternStorage()

        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()

        storage.save_pattern(original)

        result = storage.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        retrieved = result.unwrap()
        assert retrieved is not None
        assert retrieved.restaurant_code == "SDR"
        assert retrieved.service_type == "Lobby"
        assert retrieved.hour == 12
        assert retrieved.expected_volume == 85.5

    def test_get_pattern_not_found(self):
        """Test retrieving non-existent pattern returns None."""
        storage = InMemoryPatternStorage()

        result = storage.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        assert result.unwrap() is None

    def test_get_pattern_after_multiple_saves(self):
        """Test retrieving specific pattern among multiple."""
        storage = InMemoryPatternStorage()

        # Save multiple patterns
        for hour in range(10, 15):
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=float(hour / 4),
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # Retrieve specific pattern
        result = storage.get_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern is not None
        assert pattern.hour == 12
        assert pattern.expected_volume == 120.0


class TestInMemoryStorageUpdates:
    """Test pattern update operations."""

    def test_update_pattern_success(self):
        """Test updating existing pattern."""
        storage = InMemoryPatternStorage()

        # Save original
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()
        storage.save_pattern(original)

        # Update with new values
        updated = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=95.0,  # Changed
            expected_staffing=4.0,  # Changed
            confidence=0.85,  # Changed
            observations=150  # Changed
        ).unwrap()

        result = storage.update_pattern(updated)

        assert result.is_ok()
        assert result.unwrap() is True

        # Verify updated values
        retrieved = storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        assert retrieved.expected_volume == 95.0
        assert retrieved.expected_staffing == 4.0
        assert retrieved.confidence == 0.85
        assert retrieved.observations == 150

    def test_update_nonexistent_pattern_fails(self):
        """Test updating non-existent pattern fails."""
        storage = InMemoryPatternStorage()

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

        result = storage.update_pattern(pattern)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, PatternError)
        assert "not found" in error.message

    def test_upsert_new_pattern(self):
        """Test upsert creates new pattern if doesn't exist."""
        storage = InMemoryPatternStorage()

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

        result = storage.upsert_pattern(pattern)

        assert result.is_ok()
        assert result.unwrap() is True
        assert storage.count() == 1

    def test_upsert_existing_pattern(self):
        """Test upsert updates existing pattern."""
        storage = InMemoryPatternStorage()

        # Save original
        original = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=85.5,
            expected_staffing=3.2,
            confidence=0.75,
            observations=120
        ).unwrap()
        storage.save_pattern(original)

        # Upsert with new values
        updated = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=1,
            expected_volume=95.0,
            expected_staffing=4.0,
            confidence=0.85,
            observations=150
        ).unwrap()

        result = storage.upsert_pattern(updated)

        assert result.is_ok()
        assert storage.count() == 1  # Still only 1 pattern

        # Verify updated
        retrieved = storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        assert retrieved.expected_volume == 95.0


class TestInMemoryStorageDeletion:
    """Test pattern deletion operations."""

    def test_delete_existing_pattern(self):
        """Test deleting existing pattern."""
        storage = InMemoryPatternStorage()

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
        storage.save_pattern(pattern)

        result = storage.delete_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        assert result.unwrap() is True
        assert storage.count() == 0

        # Verify deleted
        retrieved = storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        assert retrieved is None

    def test_delete_nonexistent_pattern(self):
        """Test deleting non-existent pattern returns False."""
        storage = InMemoryPatternStorage()

        result = storage.delete_pattern("SDR", "Lobby", 12, 1)

        assert result.is_ok()
        assert result.unwrap() is False

    def test_clear_all_patterns(self):
        """Test clearing all patterns."""
        storage = InMemoryPatternStorage()

        # Add multiple patterns
        for hour in range(10, 15):
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=float(hour / 4),
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        assert storage.count() == 5

        result = storage.clear_all()

        assert result.is_ok()
        assert result.unwrap() is True
        assert storage.count() == 0


class TestInMemoryStorageListing:
    """Test pattern listing operations."""

    def test_list_patterns_single_restaurant(self):
        """Test listing all patterns for a restaurant."""
        storage = InMemoryPatternStorage()

        # Add patterns for SDR
        for hour in [10, 12, 14]:
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        result = storage.list_patterns("SDR")

        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 3
        assert all(p.restaurant_code == "SDR" for p in patterns)

    def test_list_patterns_multiple_restaurants(self):
        """Test listing patterns filters by restaurant."""
        storage = InMemoryPatternStorage()

        # Add patterns for SDR
        for hour in [10, 12]:
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # Add patterns for T12
        for hour in [14, 16, 18]:
            pattern = Pattern.create(
                restaurant_code="T12",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # List SDR patterns only
        result = storage.list_patterns("SDR")
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 2
        assert all(p.restaurant_code == "SDR" for p in patterns)

        # List T12 patterns only
        result = storage.list_patterns("T12")
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 3
        assert all(p.restaurant_code == "T12" for p in patterns)

    def test_list_patterns_filtered_by_service_type(self):
        """Test listing patterns filtered by service type."""
        storage = InMemoryPatternStorage()

        # Add Lobby patterns
        for hour in [10, 12]:
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # Add Drive-Thru patterns
        for hour in [14, 16, 18]:
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Drive-Thru",
                hour=hour,
                day_of_week=1,
                expected_volume=float(hour * 10),
                expected_staffing=4.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # List Lobby patterns only
        result = storage.list_patterns("SDR", service_type="Lobby")
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 2
        assert all(p.service_type == "Lobby" for p in patterns)

        # List Drive-Thru patterns only
        result = storage.list_patterns("SDR", service_type="Drive-Thru")
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 3
        assert all(p.service_type == "Drive-Thru" for p in patterns)

    def test_list_patterns_empty_results(self):
        """Test listing patterns returns empty list if none found."""
        storage = InMemoryPatternStorage()

        result = storage.list_patterns("NONEXISTENT")

        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 0
        assert patterns == []


class TestInMemoryStorageMultipleServiceTypes:
    """Test storage with multiple service types."""

    def test_save_patterns_all_service_types(self):
        """Test saving patterns for all service types."""
        storage = InMemoryPatternStorage()

        for service_type in ["Lobby", "Drive-Thru", "ToGo"]:
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type=service_type,
                hour=12,
                day_of_week=1,
                expected_volume=100.0,
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        assert storage.count() == 3

        # Verify each pattern is distinct
        lobby = storage.get_pattern("SDR", "Lobby", 12, 1).unwrap()
        drive_thru = storage.get_pattern("SDR", "Drive-Thru", 12, 1).unwrap()
        togo = storage.get_pattern("SDR", "ToGo", 12, 1).unwrap()

        assert lobby is not None
        assert drive_thru is not None
        assert togo is not None
        assert lobby.get_key() != drive_thru.get_key()
        assert drive_thru.get_key() != togo.get_key()

    def test_patterns_unique_by_all_dimensions(self):
        """Test patterns are uniquely identified by all 4 dimensions."""
        storage = InMemoryPatternStorage()

        # Same restaurant, service, hour but different day_of_week
        pattern1 = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=0,  # Monday
            expected_volume=80.0,
            expected_staffing=3.0,
            confidence=0.75,
            observations=100
        ).unwrap()

        pattern2 = Pattern.create(
            restaurant_code="SDR",
            service_type="Lobby",
            hour=12,
            day_of_week=6,  # Sunday
            expected_volume=120.0,
            expected_staffing=4.0,
            confidence=0.75,
            observations=100
        ).unwrap()

        storage.save_pattern(pattern1)
        storage.save_pattern(pattern2)

        assert storage.count() == 2

        # Verify both exist with different values
        monday = storage.get_pattern("SDR", "Lobby", 12, 0).unwrap()
        sunday = storage.get_pattern("SDR", "Lobby", 12, 6).unwrap()

        assert monday.expected_volume == 80.0
        assert sunday.expected_volume == 120.0


class TestInMemoryStorageHelpers:
    """Test storage helper methods."""

    def test_count_empty_storage(self):
        """Test count on empty storage."""
        storage = InMemoryPatternStorage()
        assert storage.count() == 0

    def test_count_after_adds(self):
        """Test count increases with additions."""
        storage = InMemoryPatternStorage()

        for i in range(5):
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=10 + i,
                day_of_week=1,
                expected_volume=100.0,
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        assert storage.count() == 5

    def test_count_after_delete(self):
        """Test count decreases with deletions."""
        storage = InMemoryPatternStorage()

        # Add patterns
        for i in range(5):
            pattern = Pattern.create(
                restaurant_code="SDR",
                service_type="Lobby",
                hour=10 + i,
                day_of_week=1,
                expected_volume=100.0,
                expected_staffing=3.0,
                confidence=0.75,
                observations=100
            ).unwrap()
            storage.save_pattern(pattern)

        # Delete one
        storage.delete_pattern("SDR", "Lobby", 12, 1)

        assert storage.count() == 4
