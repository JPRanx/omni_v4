"""
OMNI V4 Result Type

Functional result type for handling expected errors without exceptions.

Replaces exception-based error handling with explicit Result[T] values:
- Result.ok(value) for success
- Result.fail(error) for expected failures

Benefits:
- Explicit error handling in function signatures
- No hidden control flow from exceptions
- Forces callers to handle errors
- Easier to test and reason about

Usage:
    from pipeline.services.result import Result
    from pipeline.services.errors import PatternError

    # Function returns Result instead of raising
    def load_pattern(restaurant: str, hour: int) -> Result[Pattern]:
        try:
            pattern = db.query(...)
            return Result.ok(pattern)
        except Exception as e:
            return Result.fail(PatternError("Pattern not found"))

    # Caller must handle both cases
    result = load_pattern("SDR", 12)
    if result.is_ok():
        pattern = result.unwrap()
        print(f"Loaded: {pattern}")
    else:
        error = result.unwrap_err()
        logger.error(f"Failed: {error}")

    # Or use functional style
    result.map(lambda p: p.confidence).unwrap_or(0.0)
"""

from __future__ import annotations
from typing import TypeVar, Generic, Callable, Optional, Union, cast
from dataclasses import dataclass


T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type
U = TypeVar('U')  # Mapped type


@dataclass(frozen=True)
class Result(Generic[T]):
    """
    Functional result type representing success or failure.

    A Result is either:
    - Ok(value): Successful result containing a value
    - Err(error): Failed result containing an error

    This is a discriminated union - exactly one of _value or _error is set.

    Examples:
        # Create success result
        result = Result.ok(42)
        assert result.is_ok()
        assert result.unwrap() == 42

        # Create failure result
        result = Result.fail(ValueError("Invalid"))
        assert result.is_err()
        assert isinstance(result.unwrap_err(), ValueError)

        # Pattern match
        match result:
            case Result(is_ok=True):
                print(f"Success: {result.unwrap()}")
            case Result(is_ok=False):
                print(f"Error: {result.unwrap_err()}")
    """

    _value: Optional[T] = None
    _error: Optional[Exception] = None
    _is_ok: bool = False

    @staticmethod
    def ok(value: T) -> Result[T]:
        """
        Create a successful result.

        Args:
            value: The success value

        Returns:
            Result containing the value

        Example:
            result = Result.ok(42)
            assert result.unwrap() == 42
        """
        return Result(_value=value, _error=None, _is_ok=True)

    @staticmethod
    def fail(error: Exception) -> Result[T]:
        """
        Create a failed result.

        Args:
            error: The error that occurred

        Returns:
            Result containing the error

        Example:
            result = Result.fail(ValueError("Invalid"))
            assert isinstance(result.unwrap_err(), ValueError)
        """
        return Result(_value=None, _error=error, _is_ok=False)

    def is_ok(self) -> bool:
        """
        Check if result is Ok.

        Returns:
            True if Ok, False if Err

        Example:
            if result.is_ok():
                value = result.unwrap()
        """
        return self._is_ok

    def is_err(self) -> bool:
        """
        Check if result is Err.

        Returns:
            True if Err, False if Ok

        Example:
            if result.is_err():
                error = result.unwrap_err()
        """
        return not self._is_ok

    def unwrap(self) -> T:
        """
        Extract the success value or panic.

        Returns:
            The success value if Ok

        Raises:
            RuntimeError: If result is Err

        Example:
            result = Result.ok(42)
            value = result.unwrap()  # 42

            result = Result.fail(ValueError("Oops"))
            value = result.unwrap()  # RuntimeError!

        Warning:
            Only use when you are certain the result is Ok.
            Prefer unwrap_or() or pattern matching for production code.
        """
        if self._is_ok:
            return cast(T, self._value)
        raise RuntimeError(f"Called unwrap() on Err result: {self._error}")

    def unwrap_err(self) -> Exception:
        """
        Extract the error or panic.

        Returns:
            The error if Err

        Raises:
            RuntimeError: If result is Ok

        Example:
            result = Result.fail(ValueError("Oops"))
            error = result.unwrap_err()  # ValueError("Oops")

            result = Result.ok(42)
            error = result.unwrap_err()  # RuntimeError!
        """
        if not self._is_ok:
            return cast(Exception, self._error)
        raise RuntimeError(f"Called unwrap_err() on Ok result: {self._value}")

    def unwrap_or(self, default: T) -> T:
        """
        Extract value or return default.

        Args:
            default: Value to return if Err

        Returns:
            Value if Ok, default if Err

        Example:
            result = Result.ok(42)
            value = result.unwrap_or(0)  # 42

            result = Result.fail(ValueError("Oops"))
            value = result.unwrap_or(0)  # 0
        """
        if self._is_ok:
            return cast(T, self._value)
        return default

    def unwrap_or_else(self, f: Callable[[Exception], T]) -> T:
        """
        Extract value or compute default from error.

        Args:
            f: Function to compute default from error

        Returns:
            Value if Ok, f(error) if Err

        Example:
            result = Result.fail(ValueError("Invalid: 5"))
            value = result.unwrap_or_else(lambda e: 0)  # 0

            result = Result.ok(42)
            value = result.unwrap_or_else(lambda e: 0)  # 42
        """
        if self._is_ok:
            return cast(T, self._value)
        return f(cast(Exception, self._error))

    def map(self, f: Callable[[T], U]) -> Result[U]:
        """
        Transform the success value.

        Args:
            f: Function to transform value

        Returns:
            Result.ok(f(value)) if Ok, Result.fail(error) if Err

        Example:
            result = Result.ok(42)
            doubled = result.map(lambda x: x * 2)
            assert doubled.unwrap() == 84

            result = Result.fail(ValueError("Oops"))
            doubled = result.map(lambda x: x * 2)
            assert doubled.is_err()  # Error propagates
        """
        if self._is_ok:
            return Result.ok(f(cast(T, self._value)))
        return Result.fail(cast(Exception, self._error))

    def map_err(self, f: Callable[[Exception], Exception]) -> Result[T]:
        """
        Transform the error.

        Args:
            f: Function to transform error

        Returns:
            Result.ok(value) if Ok, Result.fail(f(error)) if Err

        Example:
            result = Result.fail(ValueError("Oops"))
            wrapped = result.map_err(lambda e: RuntimeError(str(e)))
            assert isinstance(wrapped.unwrap_err(), RuntimeError)

            result = Result.ok(42)
            wrapped = result.map_err(lambda e: RuntimeError(str(e)))
            assert wrapped.unwrap() == 42  # Ok unchanged
        """
        if self._is_ok:
            return Result.ok(cast(T, self._value))
        return Result.fail(f(cast(Exception, self._error)))

    def and_then(self, f: Callable[[T], Result[U]]) -> Result[U]:
        """
        Chain computations that may fail (flatMap/bind).

        Args:
            f: Function that takes value and returns Result

        Returns:
            f(value) if Ok, Result.fail(error) if Err

        Example:
            def parse_int(s: str) -> Result[int]:
                try:
                    return Result.ok(int(s))
                except ValueError as e:
                    return Result.fail(e)

            def divide(x: int) -> Result[float]:
                if x == 0:
                    return Result.fail(ValueError("Division by zero"))
                return Result.ok(100.0 / x)

            # Chain operations
            result = parse_int("5").and_then(divide)
            assert result.unwrap() == 20.0

            result = parse_int("0").and_then(divide)
            assert result.is_err()  # Division by zero

            result = parse_int("invalid").and_then(divide)
            assert result.is_err()  # Parse error
        """
        if self._is_ok:
            return f(cast(T, self._value))
        return Result.fail(cast(Exception, self._error))

    def or_else(self, f: Callable[[Exception], Result[T]]) -> Result[T]:
        """
        Recover from error with alternative computation.

        Args:
            f: Function to recover from error

        Returns:
            Result.ok(value) if Ok, f(error) if Err

        Example:
            def try_backup() -> Result[int]:
                return Result.ok(999)

            result = Result.fail(ValueError("Primary failed"))
            recovered = result.or_else(lambda e: try_backup())
            assert recovered.unwrap() == 999

            result = Result.ok(42)
            recovered = result.or_else(lambda e: try_backup())
            assert recovered.unwrap() == 42  # No recovery needed
        """
        if self._is_ok:
            return Result.ok(cast(T, self._value))
        return f(cast(Exception, self._error))

    def __bool__(self) -> bool:
        """
        Allow Result to be used in boolean context.

        Returns:
            True if Ok, False if Err

        Example:
            result = Result.ok(42)
            if result:
                print("Success!")
        """
        return self._is_ok

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if self._is_ok:
            return f"Result.ok({self._value!r})"
        return f"Result.fail({self._error!r})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        if self._is_ok:
            return f"Ok({self._value})"
        return f"Err({self._error})"


# ============================================================================
# Utility Functions
# ============================================================================

def from_optional(value: Optional[T], error: Exception) -> Result[T]:
    """
    Convert Optional[T] to Result[T].

    Args:
        value: Optional value
        error: Error to use if value is None

    Returns:
        Result.ok(value) if value is not None, Result.fail(error) if None

    Example:
        value = db.query(...)  # Returns Optional[User]
        result = from_optional(value, ValueError("User not found"))

        if result.is_ok():
            user = result.unwrap()
    """
    if value is not None:
        return Result.ok(value)
    return Result.fail(error)


def from_exception(f: Callable[[], T], error_type: type[Exception] = Exception) -> Result[T]:
    """
    Execute function and convert exception to Result.

    Args:
        f: Function to execute
        error_type: Type of exception to catch (default: Exception)

    Returns:
        Result.ok(value) if successful, Result.fail(error) if exception

    Example:
        result = from_exception(lambda: int("42"))
        assert result.unwrap() == 42

        result = from_exception(lambda: int("invalid"))
        assert result.is_err()

        # Catch specific exception type
        result = from_exception(
            lambda: json.loads("{invalid}"),
            error_type=json.JSONDecodeError
        )
    """
    try:
        value = f()
        return Result.ok(value)
    except error_type as e:
        return Result.fail(e)


def collect(results: list[Result[T]]) -> Result[list[T]]:
    """
    Collect list of Results into Result of list.

    Succeeds only if all results are Ok.
    Returns first error encountered.

    Args:
        results: List of Results

    Returns:
        Result.ok(list of values) if all Ok, Result.fail(first error) if any Err

    Example:
        results = [
            Result.ok(1),
            Result.ok(2),
            Result.ok(3)
        ]
        combined = collect(results)
        assert combined.unwrap() == [1, 2, 3]

        results = [
            Result.ok(1),
            Result.fail(ValueError("Oops")),
            Result.ok(3)
        ]
        combined = collect(results)
        assert combined.is_err()
    """
    values: list[T] = []
    for result in results:
        if result.is_err():
            return Result.fail(result.unwrap_err())
        values.append(result.unwrap())

    return Result.ok(values)


def partition(results: list[Result[T]]) -> tuple[list[T], list[Exception]]:
    """
    Partition list of Results into successes and failures.

    Args:
        results: List of Results

    Returns:
        Tuple of (success values, errors)

    Example:
        results = [
            Result.ok(1),
            Result.fail(ValueError("Bad")),
            Result.ok(3),
            Result.fail(TypeError("Wrong"))
        ]

        successes, errors = partition(results)
        assert successes == [1, 3]
        assert len(errors) == 2
    """
    successes: list[T] = []
    errors: list[Exception] = []

    for result in results:
        if result.is_ok():
            successes.append(result.unwrap())
        else:
            errors.append(result.unwrap_err())

    return successes, errors
