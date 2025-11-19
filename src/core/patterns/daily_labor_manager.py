"""
Daily Labor Pattern Manager - Pattern learning for daily labor costs

This manager specializes in learning daily labor cost patterns:
- Labor percentage (labor cost / sales revenue)
- Total hours worked
- Patterns by day of week (Monday vs Friday)

Uses exponential moving average (EMA) with dynamic learning rates.
Implements the same proven algorithm as V3.

Usage:
    from src.core.patterns.daily_labor_manager import DailyLaborPatternManager
    from src.core.patterns.daily_labor_storage import DailyLaborPatternStorage
    from src.infrastructure.config.loader import ConfigLoader

    config_loader = ConfigLoader()
    config = config_loader.load_config(restaurant_code="SDR", env="dev")
    storage = InMemoryDailyLaborPatternStorage()
    manager = DailyLaborPatternManager(storage=storage, config=config)

    # Learn from observation
    result = manager.learn_pattern(
        restaurant_code="SDR",
        day_of_week=0,  # Monday
        observed_labor_percentage=28.5,
        observed_total_hours=245.0
    )

    # Retrieve pattern
    result = manager.get_pattern(
        restaurant_code="SDR",
        day_of_week=0
    )

Architecture Note:
    This replaces the hack in PatternManager where we were using
    Pattern(service_type="Lobby", hour=12) for daily patterns.
    Now we have a dedicated manager for DailyLaborPattern.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from src.core import Result, PatternError
from src.models.daily_labor_pattern import DailyLaborPattern


class DailyLaborPatternManager:
    """
    Pattern learning and retrieval engine for daily labor patterns.

    Implements V3's Bayesian pattern learning with exponential moving average.
    All thresholds are configurable via dependency-injected config dictionary.

    Thread Safety: NOT thread-safe (delegates to storage implementation)
    """

    def __init__(self, storage: "DailyLaborPatternStorage", config: Dict[str, Any]):
        """
        Initialize DailyLaborPatternManager with storage backend and configuration.

        Args:
            storage: Pattern storage backend (any object implementing DailyLaborPatternStorage protocol)
            config: Configuration dictionary (loaded from YAML via ConfigLoader)

        Raises:
            PatternError: If config is missing required keys
        """
        self.storage = storage
        self._validate_config(config)
        self.config = config

        # Extract pattern learning config for easy access
        pl_config = config["pattern_learning"]
        self._learning_rates = pl_config["learning_rates"]
        self._reliability = pl_config["reliability_thresholds"]
        self._quality = pl_config["quality_thresholds"]
        self._constraints = pl_config["constraints"]

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate that config contains all required pattern learning parameters.

        Args:
            config: Configuration dictionary

        Raises:
            PatternError: If required keys are missing
        """
        if "pattern_learning" not in config:
            raise PatternError(
                message="Missing required config: pattern_learning",
                context={"available_keys": list(config.keys())}
            )

        pl_config = config["pattern_learning"]
        required_keys = ["learning_rates", "reliability_thresholds", "quality_thresholds", "constraints"]

        for key in required_keys:
            if key not in pl_config:
                raise PatternError(
                    message=f"Missing required pattern_learning config: {key}",
                    context={"available_keys": list(pl_config.keys())}
                )

    def learn_pattern(
        self,
        restaurant_code: str,
        day_of_week: int,
        observed_labor_percentage: float,
        observed_total_hours: float
    ) -> Result[DailyLaborPattern]:
        """
        Learn or update a daily labor pattern from a new observation.

        Implements exponential moving average with dynamic learning rates:
        - Early observations (< 5): Fast adaptation (learning_rate = 0.3)
        - Mature observations (≥ 5): Stability (learning_rate = 0.2)

        Args:
            restaurant_code: Restaurant identifier (e.g., "SDR")
            day_of_week: Day of week (0=Monday, 6=Sunday)
            observed_labor_percentage: Observed labor cost percentage
            observed_total_hours: Observed total hours worked

        Returns:
            Result[DailyLaborPattern]:
                - Success with updated/created pattern
                - Failure with PatternError if storage operation fails
        """
        try:
            # Check if pattern exists
            existing_result = self.storage.get_pattern(
                restaurant_code, day_of_week
            )

            if existing_result.is_err():
                return Result.fail(existing_result.unwrap_err())

            existing = existing_result.unwrap()

            if existing is None:
                # Create new pattern (first observation)
                pattern_result = DailyLaborPattern.create(
                    restaurant_code=restaurant_code,
                    day_of_week=day_of_week,
                    expected_labor_percentage=observed_labor_percentage,
                    expected_total_hours=observed_total_hours,
                    confidence=self._calculate_confidence(1),
                    observations=1
                )

                if pattern_result.is_err():
                    return pattern_result

                pattern = pattern_result.unwrap()
                save_result = self.storage.save_pattern(pattern)

                if save_result.is_err():
                    return Result.fail(save_result.unwrap_err())

                return Result.ok(pattern)

            else:
                # Update existing pattern with EMA
                learning_rate = self._get_learning_rate(existing.observations)

                updated = existing.with_updated_prediction(
                    new_labor_percentage=observed_labor_percentage,
                    new_total_hours=observed_total_hours,
                    learning_rate=learning_rate
                )

                # Update in storage
                update_result = self.storage.update_pattern(updated)

                if update_result.is_err():
                    return Result.fail(update_result.unwrap_err())

                return Result.ok(updated)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to learn daily labor pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def get_pattern(
        self,
        restaurant_code: str,
        day_of_week: int,
        use_fallbacks: bool = True
    ) -> Result[Optional[DailyLaborPattern]]:
        """
        Retrieve a daily labor pattern with optional fallback.

        Fallback chain (if use_fallbacks=True):
        1. Exact match (restaurant, day_of_week)
        2. Averaged across all days (weekly average)
        3. None (caller should use business standards)

        Args:
            restaurant_code: Restaurant identifier
            day_of_week: Day of week (0=Monday, 6=Sunday)
            use_fallbacks: Enable fallback chain if exact match not found

        Returns:
            Result[Optional[DailyLaborPattern]]:
                - Success with pattern if found (and reliable)
                - Success with None if not found or unreliable
                - Failure with PatternError if storage operation fails
        """
        try:
            # Try exact match first
            result = self.storage.get_pattern(restaurant_code, day_of_week)

            if result.is_err():
                return result

            pattern = result.unwrap()

            if pattern is not None and self._is_pattern_reliable(pattern):
                return Result.ok(pattern)

            # If no fallbacks requested, stop here
            if not use_fallbacks:
                return Result.ok(None)

            # Fallback: Average across all days
            fallback_result = self._get_weekly_average_fallback(restaurant_code)

            if fallback_result.is_err():
                return fallback_result

            fallback = fallback_result.unwrap()

            if fallback is not None and self._is_pattern_reliable(fallback):
                return Result.ok(fallback)

            # No reliable pattern found
            return Result.ok(None)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to retrieve daily labor pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def _get_weekly_average_fallback(
        self,
        restaurant_code: str
    ) -> Result[Optional[DailyLaborPattern]]:
        """
        Get fallback pattern by averaging across all days of week.

        Returns a reliable averaged pattern if any reliable patterns exist.

        Args:
            restaurant_code: Restaurant identifier

        Returns:
            Result[Optional[DailyLaborPattern]]:
                - Success with averaged pattern if patterns exist
                - Success with None if no reliable patterns
                - Failure with PatternError if storage operation fails
        """
        try:
            # Get all patterns for this restaurant
            list_result = self.storage.list_patterns(restaurant_code)

            if list_result.is_err():
                return Result.fail(list_result.unwrap_err())

            all_patterns = list_result.unwrap()

            # Filter to reliable patterns only
            reliable_patterns = [
                p for p in all_patterns
                if self._is_pattern_reliable(p)
            ]

            if not reliable_patterns:
                return Result.ok(None)

            # If only one reliable pattern, return it directly
            if len(reliable_patterns) == 1:
                return Result.ok(reliable_patterns[0])

            # If multiple reliable patterns, return averaged one
            avg_labor_pct = sum(p.expected_labor_percentage for p in reliable_patterns) / len(reliable_patterns)
            avg_total_hours = sum(p.expected_total_hours for p in reliable_patterns) / len(reliable_patterns)
            avg_confidence = sum(p.confidence for p in reliable_patterns) / len(reliable_patterns)
            total_obs = sum(p.observations for p in reliable_patterns)

            # Create synthetic fallback pattern using day_of_week=0 (Monday) as marker
            fallback_result = DailyLaborPattern.create(
                restaurant_code=restaurant_code,
                day_of_week=0,  # Use Monday as marker for weekly average
                expected_labor_percentage=avg_labor_pct,
                expected_total_hours=avg_total_hours,
                confidence=avg_confidence,
                observations=total_obs,
                metadata={"is_fallback": True, "days_averaged": len(reliable_patterns)}
            )

            if fallback_result.is_err():
                # If we can't create fallback, return first reliable pattern
                return Result.ok(reliable_patterns[0])

            return Result.ok(fallback_result.unwrap())

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to compute weekly average fallback: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "error": str(e)
                    }
                )
            )

    def _get_learning_rate(self, observations: int) -> float:
        """
        Get dynamic learning rate based on observation count.

        Early observations get higher learning rate for fast adaptation.
        Mature patterns get lower learning rate for stability.

        Args:
            observations: Number of observations so far

        Returns:
            Learning rate (0.0-1.0)
        """
        threshold = self._learning_rates["observation_threshold"]

        if observations < threshold:
            return self._learning_rates["early_observations"]
        else:
            return self._learning_rates["mature_observations"]

    def _calculate_confidence(self, observations: int) -> float:
        """
        Calculate pattern confidence based on observation count.

        Uses asymptotic formula: confidence = 1 - 1/(observations + 1)
        Capped at max_confidence from config.

        Args:
            observations: Number of observations

        Returns:
            Confidence score (0.0-1.0)
        """
        # Asymptotic growth: approaches 1.0 but never reaches it
        confidence = 1.0 - (1.0 / (observations + 1))

        # Apply ceiling from config
        max_confidence = self._constraints["max_confidence"]
        return min(confidence, max_confidence)

    def _is_pattern_reliable(self, pattern: DailyLaborPattern) -> bool:
        """
        Check if pattern meets reliability thresholds.

        Pattern is reliable if:
        - confidence >= min_confidence (from config)
        - observations >= min_observations (from config)

        Args:
            pattern: Pattern to check

        Returns:
            True if pattern is reliable, False otherwise
        """
        return pattern.is_reliable(
            min_confidence=self._reliability["min_confidence"],
            min_observations=self._reliability["min_observations"]
        )

    def get_all_patterns(self, restaurant_code: str) -> Result[list[DailyLaborPattern]]:
        """
        Get all daily labor patterns for a restaurant.

        Args:
            restaurant_code: Restaurant identifier

        Returns:
            Result[list[DailyLaborPattern]]:
                - Success with list of patterns (empty if none found)
                - Failure with PatternError if storage operation fails
        """
        return self.storage.list_patterns(restaurant_code)

    def clear_patterns(self, restaurant_code: str) -> Result[int]:
        """
        Clear all daily labor patterns for a restaurant (for testing/reset).

        Args:
            restaurant_code: Restaurant identifier

        Returns:
            Result[int]:
                - Success with count of patterns deleted
                - Failure with PatternError if storage operation fails
        """
        try:
            # Get all patterns
            list_result = self.storage.list_patterns(restaurant_code)

            if list_result.is_err():
                return Result.fail(list_result.unwrap_err())

            patterns = list_result.unwrap()
            count = len(patterns)

            # Delete each pattern
            for pattern in patterns:
                delete_result = self.storage.delete_pattern(
                    pattern.restaurant_code,
                    pattern.day_of_week
                )

                if delete_result.is_err():
                    return Result.fail(delete_result.unwrap_err())

            return Result.ok(count)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to clear daily labor patterns: {e}",
                    context={"restaurant_code": restaurant_code, "error": str(e)}
                )
            )
