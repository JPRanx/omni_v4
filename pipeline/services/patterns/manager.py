"""
Pattern Manager - Core Pattern Learning and Retrieval

Implements V3's proven pattern learning algorithm with:
- Exponential moving average (EMA) for pattern updates
- Dynamic learning rates (fast early adaptation, then stability)
- Confidence calculation (asymptotic growth with observations)
- Fallback chain for pattern retrieval
- All thresholds configurable via YAML

Usage:
    from pipeline.services.patterns.manager import PatternManager
    from pipeline.services.patterns.in_memory_storage import InMemoryPatternStorage
    from pipeline.infrastructure.config.loader import load_config

    config = load_config(restaurant_code="SDR", env="dev")
    storage = InMemoryPatternStorage()
    manager = PatternManager(storage=storage, config=config)

    # Learn from observation
    result = manager.learn_pattern(
        restaurant_code="SDR",
        service_type="Lobby",
        hour=12,
        day_of_week=1,
        observed_volume=85.5,
        observed_staffing=3.2
    )

    # Retrieve pattern with fallbacks
    result = manager.get_pattern(
        restaurant_code="SDR",
        service_type="Lobby",
        hour=12,
        day_of_week=1
    )
"""

from typing import Optional, Dict, Any
from datetime import datetime

from pipeline.services import Result, PatternError
from pipeline.models.pattern import Pattern
from pipeline.services.patterns.storage import PatternStorage


class PatternManager:
    """
    Pattern learning and retrieval engine.

    Implements V3's Bayesian pattern learning with exponential moving average.
    All thresholds are configurable via dependency-injected config dictionary.

    Thread Safety: NOT thread-safe (delegates to storage implementation)
    """

    def __init__(self, storage: PatternStorage, config: Dict[str, Any]):
        """
        Initialize PatternManager with storage backend and configuration.

        Args:
            storage: Pattern storage backend (any object implementing PatternStorage protocol)
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
        service_type: str,
        hour: int,
        day_of_week: int,
        observed_volume: float,
        observed_staffing: float
    ) -> Result[Pattern]:
        """
        Learn or update a pattern from a new observation.

        Implements exponential moving average with dynamic learning rates:
        - Early observations (< 5): Fast adaptation (learning_rate = 0.3)
        - Mature observations (≥ 5): Stability (learning_rate = 0.2)

        Args:
            restaurant_code: Restaurant identifier (e.g., "SDR")
            service_type: Service type (Lobby, Drive-Thru, ToGo)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            observed_volume: Observed transaction volume for this hour
            observed_staffing: Observed staffing level for this hour

        Returns:
            Result[Pattern]:
                - Success with updated/created Pattern
                - Failure with PatternError if storage operation fails
        """
        try:
            # Check if pattern exists
            existing_result = self.storage.get_pattern(
                restaurant_code, service_type, hour, day_of_week
            )

            if existing_result.is_err():
                return Result.fail(existing_result.unwrap_err())

            existing = existing_result.unwrap()

            if existing is None:
                # Create new pattern (first observation)
                pattern_result = Pattern.create(
                    restaurant_code=restaurant_code,
                    service_type=service_type,
                    hour=hour,
                    day_of_week=day_of_week,
                    expected_volume=observed_volume,
                    expected_staffing=observed_staffing,
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
                    new_volume=observed_volume,
                    new_staffing=observed_staffing,
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
                    message=f"Failed to learn pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def get_pattern(
        self,
        restaurant_code: str,
        service_type: str,
        hour: int,
        day_of_week: int,
        use_fallbacks: bool = True
    ) -> Result[Optional[Pattern]]:
        """
        Retrieve a pattern with optional fallback chain.

        Fallback chain (if use_fallbacks=True):
        1. Exact match (restaurant, service_type, hour, day_of_week)
        2. Same hour across all days (average weekday pattern)
        3. None (caller should use business standards)

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type (Lobby, Drive-Thru, ToGo)
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            use_fallbacks: Enable fallback chain if exact match not found

        Returns:
            Result[Optional[Pattern]]:
                - Success with Pattern if found (and reliable)
                - Success with None if not found or unreliable
                - Failure with PatternError if storage operation fails
        """
        try:
            # Try exact match first
            result = self.storage.get_pattern(
                restaurant_code, service_type, hour, day_of_week
            )

            if result.is_err():
                return result

            pattern = result.unwrap()

            if pattern is not None and self._is_pattern_reliable(pattern):
                return Result.ok(pattern)

            # If no fallbacks requested, stop here
            if not use_fallbacks:
                return Result.ok(None)

            # Fallback: Try same hour across all days (average pattern)
            fallback_result = self._get_hourly_fallback(
                restaurant_code, service_type, hour
            )

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
                    message=f"Failed to retrieve pattern: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "error": str(e)
                    }
                )
            )

    def _get_hourly_fallback(
        self,
        restaurant_code: str,
        service_type: str,
        hour: int
    ) -> Result[Optional[Pattern]]:
        """
        Get fallback pattern by averaging same hour across all days.

        Returns a reliable pattern from the same hour if any exist,
        or an averaged synthetic pattern if multiple reliable patterns exist.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type
            hour: Hour of day

        Returns:
            Result[Optional[Pattern]]:
                - Success with Pattern (reliable one or averaged) if patterns exist
                - Success with None if no reliable patterns for this hour
                - Failure with PatternError if storage operation fails
        """
        try:
            # Get all patterns for this restaurant/service
            list_result = self.storage.list_patterns(restaurant_code, service_type)

            if list_result.is_err():
                return Result.fail(list_result.unwrap_err())

            all_patterns = list_result.unwrap()

            # Filter to same hour only AND reliable patterns
            hour_patterns = [
                p for p in all_patterns
                if p.hour == hour and self._is_pattern_reliable(p)
            ]

            if not hour_patterns:
                return Result.ok(None)

            # If only one reliable pattern, return it directly
            if len(hour_patterns) == 1:
                return Result.ok(hour_patterns[0])

            # If multiple reliable patterns, return averaged one
            # Use day_of_week=0 (Monday) as default for averaged pattern
            avg_volume = sum(p.expected_volume for p in hour_patterns) / len(hour_patterns)
            avg_staffing = sum(p.expected_staffing for p in hour_patterns) / len(hour_patterns)
            avg_confidence = sum(p.confidence for p in hour_patterns) / len(hour_patterns)
            total_obs = sum(p.observations for p in hour_patterns)

            # Create synthetic fallback pattern using day_of_week=0
            # (we're averaging across days, so pick a valid marker)
            fallback_result = Pattern.create(
                restaurant_code=restaurant_code,
                service_type=service_type,
                hour=hour,
                day_of_week=0,  # Use Monday as marker (valid day_of_week)
                expected_volume=avg_volume,
                expected_staffing=avg_staffing,
                confidence=avg_confidence,
                observations=total_obs,
                metadata={"is_fallback": True, "days_averaged": len(hour_patterns)}
            )

            if fallback_result.is_err():
                # If we can't create fallback, return first reliable pattern
                return Result.ok(hour_patterns[0])

            return Result.ok(fallback_result.unwrap())

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to compute hourly fallback: {e}",
                    context={
                        "restaurant_code": restaurant_code,
                        "service_type": service_type,
                        "hour": hour,
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

    def _is_pattern_reliable(self, pattern: Pattern) -> bool:
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

    def get_patterns_for_service(
        self,
        restaurant_code: str,
        service_type: str
    ) -> Result[list[Pattern]]:
        """
        Get all patterns for a specific service type.

        Useful for bulk retrieval and analysis.

        Args:
            restaurant_code: Restaurant identifier
            service_type: Service type to filter by

        Returns:
            Result[list[Pattern]]:
                - Success with list of patterns (empty if none found)
                - Failure with PatternError if storage operation fails
        """
        return self.storage.list_patterns(restaurant_code, service_type)

    def get_all_patterns(self, restaurant_code: str) -> Result[list[Pattern]]:
        """
        Get all patterns for a restaurant (all service types).

        Args:
            restaurant_code: Restaurant identifier

        Returns:
            Result[list[Pattern]]:
                - Success with list of patterns (empty if none found)
                - Failure with PatternError if storage operation fails
        """
        return self.storage.list_patterns(restaurant_code)

    def clear_patterns(self, restaurant_code: str) -> Result[int]:
        """
        Clear all patterns for a restaurant (for testing/reset).

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
                    pattern.service_type,
                    pattern.hour,
                    pattern.day_of_week
                )

                if delete_result.is_err():
                    return Result.fail(delete_result.unwrap_err())

            return Result.ok(count)

        except Exception as e:
            return Result.fail(
                PatternError(
                    message=f"Failed to clear patterns: {e}",
                    context={"restaurant_code": restaurant_code, "error": str(e)}
                )
            )
