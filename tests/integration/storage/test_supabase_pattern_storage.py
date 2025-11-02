"""
Integration tests for SupabasePatternStorage

Uses mock Supabase client to test storage operations without database dependency.
Real Supabase testing deferred to Week 9.

Tests:
- Connection and initialization
- CRUD operations (save, get, update, delete, list)
- Error handling (duplicate keys, not found, database errors)
- Data type conversions (Pattern DTO ↔ database row)
- Batch operations
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.infrastructure.storage.supabase_pattern_storage import SupabasePatternStorage
from src.models.pattern import Pattern
from src.core import PatternError, DatabaseError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_client():
    """Mock Supabase client for testing."""
    return Mock()


@pytest.fixture
def storage(mock_client):
    """SupabasePatternStorage instance with mock client."""
    return SupabasePatternStorage(client=mock_client)


@pytest.fixture
def sample_pattern():
    """Sample Pattern for testing."""
    return Pattern.create(
        restaurant_code="SDR",
        service_type="Lobby",
        hour=12,
        day_of_week=1,
        expected_volume=85.5,
        expected_staffing=3.2,
        confidence=0.75,
        observations=10
    ).unwrap()


@pytest.fixture
def sample_db_row():
    """Sample database row matching v4_patterns schema."""
    return {
        "restaurant_code": "SDR",
        "service_type": "Lobby",
        "hour": 12,
        "day_of_week": 1,
        "expected_volume": 85.5,
        "expected_staffing": 3.2,
        "confidence": 0.75,
        "observations": 10,
        "last_updated": "2025-01-02T14:30:00",
        "created_at": "2025-01-01T10:00:00",
        "metadata": {}
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestSupabaseStorageInit:
    """Test SupabasePatternStorage initialization."""

    def test_initialize_with_client(self, mock_client):
        """Test successful initialization with client."""
        storage = SupabasePatternStorage(client=mock_client)

        assert storage.client is mock_client
        assert storage.table_name == "v4_patterns"

    def test_initialize_with_custom_table_name(self, mock_client):
        """Test initialization with custom table name."""
        storage = SupabasePatternStorage(client=mock_client, table_name="custom_patterns")

        assert storage.table_name == "custom_patterns"


# ============================================================================
# GET PATTERN TESTS
# ============================================================================

class TestGetPattern:
    """Test pattern retrieval operations."""

    def test_get_existing_pattern(self, storage, mock_client, sample_db_row):
        """Test retrieving existing pattern returns Pattern object."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [sample_db_row]
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_select = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.get_pattern("SDR", "Lobby", 12, 1)

        # Verify
        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern is not None
        assert pattern.restaurant_code == "SDR"
        assert pattern.service_type == "Lobby"
        assert pattern.hour == 12
        assert pattern.expected_volume == 85.5

    def test_get_nonexistent_pattern_returns_none(self, storage, mock_client):
        """Test retrieving non-existent pattern returns None."""
        # Setup mock response (empty result)
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_select = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.get_pattern("SDR", "Lobby", 99, 1)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is None

    def test_get_pattern_database_error(self, storage, mock_client):
        """Test get_pattern handles database errors."""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = "Connection timeout"

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_select = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.get_pattern("SDR", "Lobby", 12, 1)

        # Verify
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, DatabaseError)
        assert "query failed" in error.message.lower()


# ============================================================================
# SAVE PATTERN TESTS
# ============================================================================

class TestSavePattern:
    """Test pattern save operations."""

    def test_save_new_pattern_success(self, storage, mock_client, sample_pattern):
        """Test saving new pattern succeeds."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"restaurant_code": "SDR"}]  # Success indicator
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_insert = Mock(execute=mock_execute)
        mock_client.table.return_value.insert.return_value = mock_insert

        # Execute
        result = storage.save_pattern(sample_pattern)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True

        # Verify insert was called with correct data
        mock_client.table.return_value.insert.assert_called_once()

    def test_save_duplicate_pattern_fails(self, storage, mock_client, sample_pattern):
        """Test saving duplicate pattern fails with PatternError."""
        # Setup mock response with duplicate key error
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = "duplicate key value violates unique constraint"

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_insert = Mock(execute=mock_execute)
        mock_client.table.return_value.insert.return_value = mock_insert

        # Execute
        result = storage.save_pattern(sample_pattern)

        # Verify
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, PatternError)
        assert "already exists" in error.message.lower()

    def test_save_pattern_database_error(self, storage, mock_client, sample_pattern):
        """Test save_pattern handles generic database errors."""
        # Setup mock response with generic error
        mock_response = Mock()
        mock_response.data = None
        mock_response.error = "Connection lost"

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_insert = Mock(execute=mock_execute)
        mock_client.table.return_value.insert.return_value = mock_insert

        # Execute
        result = storage.save_pattern(sample_pattern)

        # Verify
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, DatabaseError)


# ============================================================================
# UPDATE PATTERN TESTS
# ============================================================================

class TestUpdatePattern:
    """Test pattern update operations."""

    def test_update_existing_pattern_success(self, storage, mock_client, sample_pattern):
        """Test updating existing pattern succeeds."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"restaurant_code": "SDR"}]  # Success indicator
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_update = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.update.return_value = mock_update

        # Execute
        result = storage.update_pattern(sample_pattern)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True

    def test_update_nonexistent_pattern_fails(self, storage, mock_client, sample_pattern):
        """Test updating non-existent pattern fails with PatternError."""
        # Setup mock response (no rows updated)
        mock_response = Mock()
        mock_response.data = []  # Empty = no rows updated
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_update = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.update.return_value = mock_update

        # Execute
        result = storage.update_pattern(sample_pattern)

        # Verify
        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, PatternError)
        assert "not found" in error.message.lower()


# ============================================================================
# UPSERT PATTERN TESTS
# ============================================================================

class TestUpsertPattern:
    """Test pattern upsert operations."""

    def test_upsert_new_pattern(self, storage, mock_client, sample_pattern):
        """Test upsert creates new pattern if doesn't exist."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"restaurant_code": "SDR"}]
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_upsert = Mock(execute=mock_execute)
        mock_client.table.return_value.upsert.return_value = mock_upsert

        # Execute
        result = storage.upsert_pattern(sample_pattern)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True

    def test_upsert_existing_pattern(self, storage, mock_client, sample_pattern):
        """Test upsert updates existing pattern."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"restaurant_code": "SDR"}]
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_upsert = Mock(execute=mock_execute)
        mock_client.table.return_value.upsert.return_value = mock_upsert

        # Execute
        result = storage.upsert_pattern(sample_pattern)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True


# ============================================================================
# DELETE PATTERN TESTS
# ============================================================================

class TestDeletePattern:
    """Test pattern deletion operations."""

    def test_delete_existing_pattern(self, storage, mock_client):
        """Test deleting existing pattern succeeds."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"restaurant_code": "SDR"}]  # Row was deleted
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_delete = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.delete.return_value = mock_delete

        # Execute
        result = storage.delete_pattern("SDR", "Lobby", 12, 1)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True

    def test_delete_nonexistent_pattern(self, storage, mock_client):
        """Test deleting non-existent pattern returns False."""
        # Setup mock response (no rows deleted)
        mock_response = Mock()
        mock_response.data = []  # Empty = nothing deleted
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq4 = Mock(execute=mock_execute)
        mock_eq3 = Mock(eq=Mock(return_value=mock_eq4))
        mock_eq2 = Mock(eq=Mock(return_value=mock_eq3))
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_delete = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.delete.return_value = mock_delete

        # Execute
        result = storage.delete_pattern("SDR", "Lobby", 99, 1)

        # Verify
        assert result.is_ok()
        assert result.unwrap() is False


# ============================================================================
# LIST PATTERNS TESTS
# ============================================================================

class TestListPatterns:
    """Test pattern listing operations."""

    def test_list_patterns_for_restaurant(self, storage, mock_client, sample_db_row):
        """Test listing all patterns for a restaurant."""
        # Setup mock response with multiple patterns
        mock_response = Mock()
        mock_response.data = [
            sample_db_row,
            {**sample_db_row, "hour": 14},
            {**sample_db_row, "hour": 16}
        ]
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq = Mock(execute=mock_execute)
        mock_select = Mock(eq=Mock(return_value=mock_eq))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.list_patterns("SDR")

        # Verify
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 3
        assert all(p.restaurant_code == "SDR" for p in patterns)

    def test_list_patterns_filtered_by_service(self, storage, mock_client, sample_db_row):
        """Test listing patterns filtered by service type."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [sample_db_row]
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq2 = Mock(execute=mock_execute)
        mock_eq1 = Mock(eq=Mock(return_value=mock_eq2))
        mock_select = Mock(eq=Mock(return_value=mock_eq1))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.list_patterns("SDR", service_type="Lobby")

        # Verify
        assert result.is_ok()
        patterns = result.unwrap()
        assert len(patterns) == 1
        assert patterns[0].service_type == "Lobby"

    def test_list_patterns_empty_results(self, storage, mock_client):
        """Test listing patterns returns empty list if none found."""
        # Setup mock response (empty)
        mock_response = Mock()
        mock_response.data = []
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_eq = Mock(execute=mock_execute)
        mock_select = Mock(eq=Mock(return_value=mock_eq))
        mock_client.table.return_value.select.return_value = mock_select

        # Execute
        result = storage.list_patterns("NONEXISTENT")

        # Verify
        assert result.is_ok()
        assert result.unwrap() == []


# ============================================================================
# CLEAR ALL TESTS
# ============================================================================

class TestClearAll:
    """Test clearing all patterns."""

    def test_clear_all_success(self, storage, mock_client):
        """Test clearing all patterns succeeds."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"count": 10}]  # Success indicator
        mock_response.error = None

        # Setup mock query chain
        mock_execute = Mock(return_value=mock_response)
        mock_neq = Mock(execute=mock_execute)
        mock_delete = Mock(neq=Mock(return_value=mock_neq))
        mock_client.table.return_value.delete.return_value = mock_delete

        # Execute
        result = storage.clear_all()

        # Verify
        assert result.is_ok()
        assert result.unwrap() is True


# ============================================================================
# DATA CONVERSION TESTS
# ============================================================================

class TestDataConversion:
    """Test Pattern ↔ database row conversions."""

    def test_pattern_to_row_conversion(self, storage, sample_pattern):
        """Test Pattern DTO converts correctly to database row."""
        row = storage._pattern_to_row(sample_pattern)

        assert row["restaurant_code"] == "SDR"
        assert row["service_type"] == "Lobby"
        assert row["hour"] == 12
        assert row["day_of_week"] == 1
        assert row["expected_volume"] == 85.5
        assert row["expected_staffing"] == 3.2
        assert row["confidence"] == 0.75
        assert row["observations"] == 10
        assert "last_updated" in row
        assert "created_at" in row
        assert row["metadata"] == {}

    def test_row_to_pattern_conversion(self, storage, sample_db_row):
        """Test database row converts correctly to Pattern DTO."""
        result = storage._row_to_pattern(sample_db_row)

        assert result.is_ok()
        pattern = result.unwrap()
        assert pattern.restaurant_code == "SDR"
        assert pattern.service_type == "Lobby"
        assert pattern.hour == 12
        assert pattern.day_of_week == 1
        assert pattern.expected_volume == 85.5
        assert pattern.expected_staffing == 3.2
        assert pattern.confidence == 0.75
        assert pattern.observations == 10

    def test_row_to_pattern_missing_field(self, storage):
        """Test row_to_pattern handles missing required fields."""
        invalid_row = {"restaurant_code": "SDR"}  # Missing required fields

        result = storage._row_to_pattern(invalid_row)

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, PatternError)
        assert "missing" in error.message.lower()

    def test_row_to_pattern_datetime_objects(self, storage, sample_db_row):
        """Test row_to_pattern handles datetime objects (not just strings)."""
        # Modify row to use datetime objects instead of strings
        row_with_datetimes = {
            **sample_db_row,
            "last_updated": datetime(2025, 1, 2, 14, 30, 0),
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        result = storage._row_to_pattern(row_with_datetimes)

        assert result.is_ok()
        pattern = result.unwrap()
        # Verify timestamps were converted to ISO strings
        assert "2025-01-02" in pattern.last_updated
        assert "2025-01-01" in pattern.created_at
