"""
Unit tests for Result[T] type

Tests functional result type in src/core/result.py:
- Result.ok() and Result.fail()
- unwrap() and unwrap_err()
- unwrap_or() and unwrap_or_else()
- map() and map_err()
- and_then() and or_else()
- Utility functions (from_optional, from_exception, collect, partition)
"""

import pytest
from src.core.result import (
    Result,
    from_optional,
    from_exception,
    collect,
    partition,
)


class TestResultBasics:
    """Test basic Result creation and checking."""

    def test_create_ok_result(self):
        """Test creating Ok result."""
        result = Result.ok(42)

        assert result.is_ok()
        assert not result.is_err()
        assert result.unwrap() == 42

    def test_create_err_result(self):
        """Test creating Err result."""
        error = ValueError("Something went wrong")
        result = Result.fail(error)

        assert result.is_err()
        assert not result.is_ok()
        assert result.unwrap_err() == error

    def test_ok_with_none(self):
        """Test Ok result can contain None."""
        result = Result.ok(None)

        assert result.is_ok()
        assert result.unwrap() is None

    def test_ok_with_different_types(self):
        """Test Ok result with various types."""
        # String
        result = Result.ok("hello")
        assert result.unwrap() == "hello"

        # List
        result = Result.ok([1, 2, 3])
        assert result.unwrap() == [1, 2, 3]

        # Dict
        result = Result.ok({"key": "value"})
        assert result.unwrap() == {"key": "value"}

        # Object
        class Person:
            def __init__(self, name):
                self.name = name

        person = Person("Alice")
        result = Result.ok(person)
        assert result.unwrap().name == "Alice"


class TestUnwrap:
    """Test unwrap() and unwrap_err() methods."""

    def test_unwrap_ok_result(self):
        """Test unwrapping Ok result."""
        result = Result.ok(42)
        value = result.unwrap()

        assert value == 42

    def test_unwrap_err_result_raises(self):
        """Test unwrapping Err result raises."""
        result = Result.fail(ValueError("Oops"))

        with pytest.raises(RuntimeError, match="Called unwrap.*on Err"):
            result.unwrap()

    def test_unwrap_err_ok_result_raises(self):
        """Test unwrap_err on Ok result raises."""
        result = Result.ok(42)

        with pytest.raises(RuntimeError, match="Called unwrap_err.*on Ok"):
            result.unwrap_err()

    def test_unwrap_err_err_result(self):
        """Test unwrapping error from Err result."""
        error = ValueError("Something bad")
        result = Result.fail(error)

        unwrapped_error = result.unwrap_err()
        assert unwrapped_error == error
        assert isinstance(unwrapped_error, ValueError)


class TestUnwrapOr:
    """Test unwrap_or() and unwrap_or_else() methods."""

    def test_unwrap_or_ok_result(self):
        """Test unwrap_or on Ok result returns value."""
        result = Result.ok(42)
        value = result.unwrap_or(0)

        assert value == 42

    def test_unwrap_or_err_result(self):
        """Test unwrap_or on Err result returns default."""
        result = Result.fail(ValueError("Oops"))
        value = result.unwrap_or(0)

        assert value == 0

    def test_unwrap_or_else_ok_result(self):
        """Test unwrap_or_else on Ok result returns value."""
        result = Result.ok(42)
        value = result.unwrap_or_else(lambda e: 0)

        assert value == 42

    def test_unwrap_or_else_err_result(self):
        """Test unwrap_or_else on Err result computes default."""
        result = Result.fail(ValueError("Error: 5"))
        value = result.unwrap_or_else(lambda e: 0)

        assert value == 0

    def test_unwrap_or_else_uses_error(self):
        """Test unwrap_or_else can use error value."""
        result = Result.fail(ValueError("123"))

        # Extract number from error message
        value = result.unwrap_or_else(
            lambda e: int(str(e).split(":")[0]) if ":" in str(e) else 0
        )

        # Falls back to 0 since error message doesn't have ":"
        assert value == 0


class TestMap:
    """Test map() and map_err() transformations."""

    def test_map_ok_result(self):
        """Test map transforms Ok value."""
        result = Result.ok(5)
        doubled = result.map(lambda x: x * 2)

        assert doubled.is_ok()
        assert doubled.unwrap() == 10

    def test_map_err_result(self):
        """Test map preserves Err."""
        result = Result.fail(ValueError("Oops"))
        doubled = result.map(lambda x: x * 2)

        assert doubled.is_err()
        assert isinstance(doubled.unwrap_err(), ValueError)

    def test_map_chain(self):
        """Test chaining map operations."""
        result = Result.ok(5)
        transformed = (
            result
            .map(lambda x: x * 2)
            .map(lambda x: x + 1)
            .map(lambda x: str(x))
        )

        assert transformed.unwrap() == "11"

    def test_map_err_ok_result(self):
        """Test map_err preserves Ok."""
        result = Result.ok(42)
        transformed = result.map_err(lambda e: RuntimeError(str(e)))

        assert transformed.is_ok()
        assert transformed.unwrap() == 42

    def test_map_err_err_result(self):
        """Test map_err transforms error."""
        result = Result.fail(ValueError("Original"))
        transformed = result.map_err(lambda e: RuntimeError(f"Wrapped: {e}"))

        assert transformed.is_err()
        error = transformed.unwrap_err()
        assert isinstance(error, RuntimeError)
        assert "Wrapped" in str(error)


class TestAndThen:
    """Test and_then() for chaining operations."""

    def test_and_then_ok_to_ok(self):
        """Test and_then with two Ok results."""
        def double(x: int) -> Result[int]:
            return Result.ok(x * 2)

        result = Result.ok(5)
        chained = result.and_then(double)

        assert chained.is_ok()
        assert chained.unwrap() == 10

    def test_and_then_ok_to_err(self):
        """Test and_then where operation fails."""
        def divide_by_zero(x: int) -> Result[float]:
            return Result.fail(ValueError("Cannot divide by zero"))

        result = Result.ok(5)
        chained = result.and_then(divide_by_zero)

        assert chained.is_err()
        assert isinstance(chained.unwrap_err(), ValueError)

    def test_and_then_err_skipped(self):
        """Test and_then skipped if already Err."""
        def double(x: int) -> Result[int]:
            return Result.ok(x * 2)

        result = Result.fail(ValueError("Original error"))
        chained = result.and_then(double)

        assert chained.is_err()
        assert "Original error" in str(chained.unwrap_err())

    def test_and_then_chain(self):
        """Test chaining multiple and_then operations."""
        def parse_int(s: str) -> Result[int]:
            try:
                return Result.ok(int(s))
            except ValueError as e:
                return Result.fail(e)

        def double(x: int) -> Result[int]:
            return Result.ok(x * 2)

        def is_positive(x: int) -> Result[int]:
            if x > 0:
                return Result.ok(x)
            return Result.fail(ValueError("Not positive"))

        # Success case
        result = (
            parse_int("5")
            .and_then(double)
            .and_then(is_positive)
        )
        assert result.unwrap() == 10

        # Failure in parse
        result = (
            parse_int("invalid")
            .and_then(double)
            .and_then(is_positive)
        )
        assert result.is_err()

        # Failure in positive check
        result = (
            parse_int("-5")
            .and_then(double)
            .and_then(is_positive)
        )
        assert result.is_err()
        assert "Not positive" in str(result.unwrap_err())


class TestOrElse:
    """Test or_else() for error recovery."""

    def test_or_else_ok_unchanged(self):
        """Test or_else preserves Ok result."""
        def backup() -> Result[int]:
            return Result.ok(999)

        result = Result.ok(42)
        recovered = result.or_else(lambda e: backup())

        assert recovered.is_ok()
        assert recovered.unwrap() == 42

    def test_or_else_err_recovers(self):
        """Test or_else recovers from Err."""
        def backup(error: Exception) -> Result[int]:
            return Result.ok(999)

        result = Result.fail(ValueError("Failed"))
        recovered = result.or_else(backup)

        assert recovered.is_ok()
        assert recovered.unwrap() == 999

    def test_or_else_err_to_err(self):
        """Test or_else where backup also fails."""
        def backup(error: Exception) -> Result[int]:
            return Result.fail(RuntimeError("Backup also failed"))

        result = Result.fail(ValueError("Primary failed"))
        recovered = result.or_else(backup)

        assert recovered.is_err()
        assert isinstance(recovered.unwrap_err(), RuntimeError)


class TestBooleanContext:
    """Test using Result in boolean context."""

    def test_ok_result_is_truthy(self):
        """Test Ok result is truthy."""
        result = Result.ok(42)

        assert result
        assert bool(result) is True

    def test_err_result_is_falsy(self):
        """Test Err result is falsy."""
        result = Result.fail(ValueError("Oops"))

        assert not result
        assert bool(result) is False

    def test_if_result(self):
        """Test using result in if statement."""
        ok_result = Result.ok(42)
        err_result = Result.fail(ValueError("Oops"))

        if ok_result:
            assert True
        else:
            pytest.fail("Ok result should be truthy")

        if err_result:
            pytest.fail("Err result should be falsy")
        else:
            assert True


class TestStringRepresentation:
    """Test __repr__ and __str__ methods."""

    def test_ok_repr(self):
        """Test repr of Ok result."""
        result = Result.ok(42)
        repr_str = repr(result)

        assert "Result.ok" in repr_str
        assert "42" in repr_str

    def test_err_repr(self):
        """Test repr of Err result."""
        error = ValueError("Oops")
        result = Result.fail(error)
        repr_str = repr(result)

        assert "Result.fail" in repr_str
        assert "ValueError" in repr_str

    def test_ok_str(self):
        """Test str of Ok result."""
        result = Result.ok(42)
        str_repr = str(result)

        assert "Ok" in str_repr
        assert "42" in str_repr

    def test_err_str(self):
        """Test str of Err result."""
        result = Result.fail(ValueError("Oops"))
        str_repr = str(result)

        assert "Err" in str_repr
        assert "Oops" in str_repr


class TestFromOptional:
    """Test from_optional() utility function."""

    def test_from_optional_with_value(self):
        """Test from_optional with Some value."""
        value = "hello"
        result = from_optional(value, ValueError("Not found"))

        assert result.is_ok()
        assert result.unwrap() == "hello"

    def test_from_optional_with_none(self):
        """Test from_optional with None."""
        value = None
        result = from_optional(value, ValueError("Not found"))

        assert result.is_err()
        assert "Not found" in str(result.unwrap_err())

    def test_from_optional_realistic_usage(self):
        """Test from_optional with dict.get() pattern."""
        data = {"key1": "value1"}

        # Key exists
        result = from_optional(
            data.get("key1"),
            ValueError("Key not found")
        )
        assert result.unwrap() == "value1"

        # Key missing
        result = from_optional(
            data.get("key2"),
            ValueError("Key not found")
        )
        assert result.is_err()


class TestFromException:
    """Test from_exception() utility function."""

    def test_from_exception_success(self):
        """Test from_exception with successful operation."""
        result = from_exception(lambda: int("42"))

        assert result.is_ok()
        assert result.unwrap() == 42

    def test_from_exception_failure(self):
        """Test from_exception with failing operation."""
        result = from_exception(lambda: int("invalid"))

        assert result.is_err()
        assert isinstance(result.unwrap_err(), ValueError)

    def test_from_exception_specific_error_type(self):
        """Test from_exception catching specific error type."""
        # Catches ValueError
        result = from_exception(
            lambda: int("invalid"),
            error_type=ValueError
        )
        assert result.is_err()

        # Doesn't catch KeyError (re-raises)
        with pytest.raises(KeyError):
            result = from_exception(
                lambda: {"a": 1}["b"],
                error_type=ValueError
            )

    def test_from_exception_division(self):
        """Test from_exception with division by zero."""
        result = from_exception(
            lambda: 10 / 0,
            error_type=ZeroDivisionError
        )

        assert result.is_err()
        assert isinstance(result.unwrap_err(), ZeroDivisionError)


class TestCollect:
    """Test collect() utility function."""

    def test_collect_all_ok(self):
        """Test collect with all Ok results."""
        results = [
            Result.ok(1),
            Result.ok(2),
            Result.ok(3)
        ]

        combined = collect(results)

        assert combined.is_ok()
        assert combined.unwrap() == [1, 2, 3]

    def test_collect_with_err(self):
        """Test collect with one Err result."""
        results = [
            Result.ok(1),
            Result.fail(ValueError("Oops")),
            Result.ok(3)
        ]

        combined = collect(results)

        assert combined.is_err()
        assert "Oops" in str(combined.unwrap_err())

    def test_collect_returns_first_err(self):
        """Test collect returns first error encountered."""
        results = [
            Result.ok(1),
            Result.fail(ValueError("First error")),
            Result.fail(TypeError("Second error"))
        ]

        combined = collect(results)

        assert combined.is_err()
        assert "First error" in str(combined.unwrap_err())

    def test_collect_empty_list(self):
        """Test collect with empty list."""
        results = []
        combined = collect(results)

        assert combined.is_ok()
        assert combined.unwrap() == []


class TestPartition:
    """Test partition() utility function."""

    def test_partition_mixed_results(self):
        """Test partition with mixed Ok and Err results."""
        results = [
            Result.ok(1),
            Result.fail(ValueError("Error 1")),
            Result.ok(3),
            Result.fail(TypeError("Error 2")),
            Result.ok(5)
        ]

        successes, errors = partition(results)

        assert successes == [1, 3, 5]
        assert len(errors) == 2
        assert isinstance(errors[0], ValueError)
        assert isinstance(errors[1], TypeError)

    def test_partition_all_ok(self):
        """Test partition with all Ok results."""
        results = [Result.ok(i) for i in range(5)]

        successes, errors = partition(results)

        assert successes == [0, 1, 2, 3, 4]
        assert errors == []

    def test_partition_all_err(self):
        """Test partition with all Err results."""
        results = [Result.fail(ValueError(f"Error {i}")) for i in range(3)]

        successes, errors = partition(results)

        assert successes == []
        assert len(errors) == 3

    def test_partition_empty(self):
        """Test partition with empty list."""
        results = []

        successes, errors = partition(results)

        assert successes == []
        assert errors == []


class TestRealisticUsage:
    """Test realistic usage patterns."""

    def test_database_query_pattern(self):
        """Test Result for database query that might fail."""
        def query_user(user_id: int) -> Result[dict]:
            if user_id == 1:
                return Result.ok({"id": 1, "name": "Alice"})
            return Result.fail(ValueError("User not found"))

        # Success case
        result = query_user(1)
        if result.is_ok():
            user = result.unwrap()
            assert user["name"] == "Alice"

        # Failure case
        result = query_user(999)
        if result.is_err():
            error = result.unwrap_err()
            assert "not found" in str(error)

    def test_pipeline_pattern(self):
        """Test Result for processing pipeline."""
        def load_data(path: str) -> Result[str]:
            if path.endswith(".csv"):
                return Result.ok("data,data,data")
            return Result.fail(ValueError("Invalid file type"))

        def parse_csv(data: str) -> Result[list]:
            rows = data.split("\n")
            return Result.ok([row.split(",") for row in rows])

        def validate(rows: list) -> Result[list]:
            if len(rows) > 0:
                return Result.ok(rows)
            return Result.fail(ValueError("Empty data"))

        # Success pipeline
        result = (
            load_data("data.csv")
            .and_then(parse_csv)
            .and_then(validate)
        )
        assert result.is_ok()

        # Failure in load
        result = (
            load_data("data.txt")
            .and_then(parse_csv)
            .and_then(validate)
        )
        assert result.is_err()

    def test_parallel_processing_pattern(self):
        """Test Result for parallel processing results."""
        def process_item(item: int) -> Result[int]:
            if item < 0:
                return Result.fail(ValueError(f"Negative: {item}"))
            return Result.ok(item * 2)

        items = [1, 2, -3, 4, 5]
        results = [process_item(item) for item in items]

        # Collect successes and errors
        successes, errors = partition(results)

        assert successes == [2, 4, 8, 10]
        assert len(errors) == 1
        assert "Negative" in str(errors[0])
