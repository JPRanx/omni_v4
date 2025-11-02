"""
Unit tests for ConfigLoader

Tests the hierarchical configuration loading system with:
- Base configuration loading
- Restaurant-specific overrides
- Environment-specific overlays
- Deep merging logic
- Environment variable substitution
- Validation
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.config.loader import ConfigLoader, ConfigError


class TestConfigLoaderBasics:
    """Test basic ConfigLoader functionality."""

    def test_loader_initialization(self):
        """Test ConfigLoader can be initialized with default config dir."""
        loader = ConfigLoader()
        assert loader.config_dir.exists()
        assert (loader.config_dir / "base.yaml").exists()

    def test_loader_with_custom_dir(self, tmp_path):
        """Test ConfigLoader can be initialized with custom config dir."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = ConfigLoader(config_dir=config_dir)
        assert loader.config_dir == config_dir

    def test_loader_fails_with_missing_dir(self, tmp_path):
        """Test ConfigLoader raises error if config dir doesn't exist."""
        missing_dir = tmp_path / "nonexistent"

        with pytest.raises(ConfigError, match="Config directory not found"):
            ConfigLoader(config_dir=missing_dir)


class TestBaseConfigLoading:
    """Test loading base configuration."""

    def test_load_base_config_only(self):
        """Test loading only base.yaml without restaurant or environment."""
        loader = ConfigLoader()
        config = loader.load_config()

        # Verify base config structure
        assert "system" in config
        assert "business_standards" in config
        assert "shifts" in config
        assert "pattern_learning" in config

    def test_base_config_values(self):
        """Test base config contains expected V3-extracted values."""
        loader = ConfigLoader()
        config = loader.load_config()

        # Business standards from V3
        standards = config["business_standards"]["service_time_targets"]
        assert standards["Lobby"] == 15.0
        assert standards["Drive-Thru"] == 8.0
        assert standards["ToGo"] == 10.0

        # Shift cutoff from V3
        assert config["shifts"]["cutoff_hour"] == 14

        # Pattern learning rates from V3
        learning_rates = config["pattern_learning"]["learning_rates"]
        assert learning_rates["early_observations"] == 0.3
        assert learning_rates["mature_observations"] == 0.2

        # Reliability thresholds from V3
        reliability = config["pattern_learning"]["reliability_thresholds"]
        assert reliability["min_confidence"] == 0.6
        assert reliability["min_observations"] == 4


class TestRestaurantConfigOverrides:
    """Test restaurant-specific configuration overrides."""

    def test_load_sdr_config(self):
        """Test loading SDR restaurant configuration."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR")

        # Verify restaurant metadata
        assert config["restaurant"]["code"] == "SDR"
        assert config["restaurant"]["display_name"] == "Sandra's Mexican Cuisine"
        assert config["restaurant"]["icon"] == "🌯"
        assert config["restaurant"]["color"] == "#C67B5C"

        # Verify vendor costs are present
        assert "vendor_costs" in config
        assert config["vendor_costs"]["Sysco"] == 2800

        # Verify overhead costs are present
        assert "overhead_costs" in config
        assert config["overhead_costs"]["Electric Company"] == 1200

        # Verify base config still present
        assert config["shifts"]["cutoff_hour"] == 14

    def test_load_t12_config(self):
        """Test loading T12 restaurant configuration."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="T12")

        assert config["restaurant"]["code"] == "T12"
        assert config["restaurant"]["display_name"] == "Tink-A-Tako #12"
        assert config["restaurant"]["icon"] == "🌮"

    def test_load_tk9_config(self):
        """Test loading TK9 restaurant configuration."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="TK9")

        assert config["restaurant"]["code"] == "TK9"
        assert config["restaurant"]["display_name"] == "Tink-A-Tako #9"

    def test_invalid_restaurant_code(self):
        """Test loading fails with invalid restaurant code."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError, match="Restaurant config not found"):
            loader.load_config(restaurant_code="INVALID")


class TestEnvironmentConfigOverrides:
    """Test environment-specific configuration overlays."""

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "SUPABASE_SERVICE_KEY": "test-service-key"
    })
    def test_load_dev_environment(self):
        """Test loading dev environment configuration."""
        loader = ConfigLoader()
        config = loader.load_config(env="dev")

        # Verify environment
        assert config["environment"] == "dev"

        # Verify dev-specific settings
        assert config["logging"]["level"] == "DEBUG"
        assert config["features"]["shadow_mode"] is True
        assert config["features"]["verbose_logging"] is True

        # Verify relaxed quality thresholds
        quality = config["pattern_learning"]["quality_thresholds"]
        assert quality["update_confidence"] == 0.5  # Lower than base (0.8)
        assert quality["max_age_days"] == 365  # Higher than base (14)

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://prod.supabase.co",
        "SUPABASE_KEY": "prod-key",
        "SUPABASE_SERVICE_KEY": "prod-service-key"
    })
    def test_load_prod_environment(self):
        """Test loading prod environment configuration."""
        loader = ConfigLoader()
        config = loader.load_config(env="prod")

        # Verify environment
        assert config["environment"] == "prod"

        # Verify prod-specific settings
        assert config["logging"]["level"] == "INFO"
        assert config["features"]["shadow_mode"] is False
        assert config["features"]["verbose_logging"] is False

        # Verify strict quality thresholds
        quality = config["pattern_learning"]["quality_thresholds"]
        assert quality["update_confidence"] == 0.8  # Same as base
        assert quality["max_age_days"] == 14  # Same as base

    def test_invalid_environment(self):
        """Test loading fails with invalid environment."""
        loader = ConfigLoader()

        with pytest.raises(ConfigError, match="Environment config not found"):
            loader.load_config(env="invalid")


class TestFullConfigMerge:
    """Test full 3-layer configuration merge."""

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "SUPABASE_SERVICE_KEY": "test-service-key"
    })
    def test_full_merge_sdr_dev(self):
        """Test full merge: base + SDR + dev."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="dev")

        # Verify all layers present
        assert config["system"]["version"] == "4.0.0"  # From base
        assert config["restaurant"]["code"] == "SDR"  # From SDR
        assert config["environment"] == "dev"  # From dev

        # Verify deep merge worked (dev overrides base, but doesn't replace entire sections)
        assert config["pattern_learning"]["enabled"] is True  # From base
        assert config["pattern_learning"]["quality_thresholds"]["update_confidence"] == 0.5  # From dev

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://prod.supabase.co",
        "SUPABASE_KEY": "prod-key",
        "SUPABASE_SERVICE_KEY": "prod-service-key"
    })
    def test_full_merge_t12_prod(self):
        """Test full merge: base + T12 + prod."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="T12", env="prod")

        assert config["restaurant"]["code"] == "T12"
        assert config["environment"] == "prod"
        assert config["logging"]["level"] == "INFO"


class TestDeepMerge:
    """Test deep merge logic."""

    def test_deep_merge_nested_dicts(self):
        """Test deep merge preserves nested structure."""
        loader = ConfigLoader()

        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }

        override = {
            "b": {
                "d": 4,
                "e": 5
            },
            "f": 6
        }

        result = loader._deep_merge(base, override)

        # Verify deep merge
        assert result["a"] == 1  # From base
        assert result["b"]["c"] == 2  # From base (preserved)
        assert result["b"]["d"] == 4  # From override (replaced)
        assert result["b"]["e"] == 5  # From override (added)
        assert result["f"] == 6  # From override (added)

    def test_deep_merge_replaces_primitives(self):
        """Test deep merge replaces primitives (not merge)."""
        loader = ConfigLoader()

        base = {"value": 10}
        override = {"value": 20}

        result = loader._deep_merge(base, override)
        assert result["value"] == 20

    def test_deep_merge_replaces_lists(self):
        """Test deep merge replaces lists (not merge)."""
        loader = ConfigLoader()

        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}

        result = loader._deep_merge(base, override)
        assert result["items"] == [4, 5]  # Replaced, not merged


class TestEnvironmentVariableSubstitution:
    """Test environment variable substitution."""

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_substitute_single_var(self):
        """Test substituting a single environment variable."""
        loader = ConfigLoader()

        config = {
            "key": "${TEST_VAR}"
        }

        result = loader._substitute_env_vars(config)
        assert result["key"] == "test_value"

    @patch.dict(os.environ, {
        "VAR1": "value1",
        "VAR2": "value2"
    })
    def test_substitute_multiple_vars(self):
        """Test substituting multiple environment variables."""
        loader = ConfigLoader()

        config = {
            "key1": "${VAR1}",
            "key2": "${VAR2}"
        }

        result = loader._substitute_env_vars(config)
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    @patch.dict(os.environ, {"VAR": "value"})
    def test_substitute_nested_vars(self):
        """Test substituting variables in nested dicts."""
        loader = ConfigLoader()

        config = {
            "outer": {
                "inner": "${VAR}"
            }
        }

        result = loader._substitute_env_vars(config)
        assert result["outer"]["inner"] == "value"

    def test_substitute_missing_var_raises_error(self):
        """Test substitution fails with missing environment variable."""
        loader = ConfigLoader()

        config = {
            "key": "${NONEXISTENT_VAR}"
        }

        with pytest.raises(ConfigError, match="Environment variable not set: NONEXISTENT_VAR"):
            loader._substitute_env_vars(config)

    @patch.dict(os.environ, {"VAR": "value"})
    def test_substitute_preserves_non_string_types(self):
        """Test substitution preserves non-string types."""
        loader = ConfigLoader()

        config = {
            "string": "${VAR}",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3]
        }

        result = loader._substitute_env_vars(config)
        assert result["string"] == "value"
        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["list"] == [1, 2, 3]


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_requires_system(self):
        """Test validation fails without system key."""
        loader = ConfigLoader()

        invalid_config = {}

        with pytest.raises(ConfigError, match="Missing required configuration key: system"):
            loader._validate(invalid_config)

    def test_validate_requires_business_standards(self):
        """Test validation fails without business_standards."""
        loader = ConfigLoader()

        invalid_config = {
            "system": {},
            "shifts": {},
            "pattern_learning": {},
            "overtime": {},
            "data_quality": {},
            "logging": {}
        }

        with pytest.raises(ConfigError, match="Missing required configuration key: business_standards"):
            loader._validate(invalid_config)

    def test_validate_requires_service_time_targets(self):
        """Test validation fails without service_time_targets."""
        loader = ConfigLoader()

        invalid_config = {
            "system": {},
            "business_standards": {},
            "shifts": {"cutoff_hour": 14},
            "pattern_learning": {
                "learning_rates": {},
                "reliability_thresholds": {}
            },
            "overtime": {},
            "data_quality": {},
            "logging": {}
        }

        with pytest.raises(ConfigError, match="Missing business_standards.service_time_targets"):
            loader._validate(invalid_config)

    def test_validate_requires_all_service_targets(self):
        """Test validation fails without all service targets."""
        loader = ConfigLoader()

        invalid_config = {
            "system": {},
            "business_standards": {
                "service_time_targets": {
                    "Lobby": 15.0
                    # Missing Drive-Thru and ToGo
                }
            },
            "shifts": {"cutoff_hour": 14},
            "pattern_learning": {
                "learning_rates": {},
                "reliability_thresholds": {}
            },
            "overtime": {},
            "data_quality": {},
            "logging": {}
        }

        with pytest.raises(ConfigError, match="Missing required service time target"):
            loader._validate(invalid_config)

    def test_validate_shift_cutoff_hour(self):
        """Test validation fails with invalid cutoff_hour."""
        loader = ConfigLoader()

        invalid_config = {
            "system": {},
            "business_standards": {
                "service_time_targets": {
                    "Lobby": 15.0,
                    "Drive-Thru": 8.0,
                    "ToGo": 10.0
                }
            },
            "shifts": {"cutoff_hour": 25},  # Invalid: > 23
            "pattern_learning": {
                "learning_rates": {},
                "reliability_thresholds": {}
            },
            "overtime": {},
            "data_quality": {},
            "logging": {}
        }

        with pytest.raises(ConfigError, match="Invalid shifts.cutoff_hour"):
            loader._validate(invalid_config)


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_restaurant_codes(self):
        """Test getting list of available restaurant codes."""
        loader = ConfigLoader()
        codes = loader.get_restaurant_codes()

        assert "SDR" in codes
        assert "T12" in codes
        assert "TK9" in codes
        assert len(codes) == 3

    def test_get_environments(self):
        """Test getting list of available environments."""
        loader = ConfigLoader()
        envs = loader.get_environments()

        assert "dev" in envs
        assert "prod" in envs
        assert len(envs) == 2


class TestConvenienceFunction:
    """Test convenience load_config function."""

    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "SUPABASE_SERVICE_KEY": "test-service-key"
    })
    def test_load_config_convenience_function(self):
        """Test convenience function works."""
        from src.infrastructure.config.loader import load_config

        config = load_config(restaurant_code="SDR", env="dev")

        assert config["restaurant"]["code"] == "SDR"
        assert config["environment"] == "dev"
