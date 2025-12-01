"""
Integration tests for ConfigLoader

Tests all real restaurant/environment combinations to ensure:
- All config files load correctly
- All V3 values are properly extracted
- Environment overlays work in practice
- No missing keys or values in production configs
"""

import os
import pytest
from unittest.mock import patch

from pipeline.infrastructure.config.loader import ConfigLoader


# Mock environment variables for testing
TEST_ENV_VARS = {
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-anon-key-12345",
    "SUPABASE_SERVICE_KEY": "test-service-key-67890"
}


@pytest.mark.integration
class TestAllRestaurantEnvironmentCombinations:
    """Test all 6 combinations of restaurants × environments."""

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_sdr_dev(self):
        """Test SDR + dev environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="dev")

        # Verify all layers merged correctly
        assert config["system"]["version"] == "4.0.0"
        assert config["restaurant"]["code"] == "SDR"
        assert config["environment"] == "dev"

        # Verify critical values
        assert config["database"]["url"] == "https://test.supabase.co"
        assert config["shifts"]["cutoff_hour"] == 14
        assert config["features"]["shadow_mode"] is True

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_sdr_prod(self):
        """Test SDR + prod environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="prod")

        assert config["restaurant"]["code"] == "SDR"
        assert config["environment"] == "prod"
        assert config["logging"]["level"] == "INFO"
        assert config["features"]["shadow_mode"] is False

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_t12_dev(self):
        """Test T12 + dev environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="T12", env="dev")

        assert config["restaurant"]["code"] == "T12"
        assert config["restaurant"]["display_name"] == "Tink-A-Tako #12"
        assert config["environment"] == "dev"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_t12_prod(self):
        """Test T12 + prod environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="T12", env="prod")

        assert config["restaurant"]["code"] == "T12"
        assert config["environment"] == "prod"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_tk9_dev(self):
        """Test TK9 + dev environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="TK9", env="dev")

        assert config["restaurant"]["code"] == "TK9"
        assert config["restaurant"]["display_name"] == "Tink-A-Tako #9"
        assert config["environment"] == "dev"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_tk9_prod(self):
        """Test TK9 + prod environment."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="TK9", env="prod")

        assert config["restaurant"]["code"] == "TK9"
        assert config["environment"] == "prod"


@pytest.mark.integration
class TestV3ValueExtraction:
    """Verify all V3 hardcoded values are properly extracted."""

    def test_business_standards_extracted(self):
        """Test V3 business standards are in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        standards = config["business_standards"]["service_time_targets"]

        # From V3 main_v3.py lines 74-78
        assert standards["Lobby"] == 15.0
        assert standards["Drive-Thru"] == 8.0
        assert standards["ToGo"] == 10.0

    def test_shift_cutoff_extracted(self):
        """Test V3 shift cutoff hour is in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        # From V3 shift_splitter.py line 7
        assert config["shifts"]["cutoff_hour"] == 14

    def test_learning_rates_extracted(self):
        """Test V3 pattern learning rates are in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        # From V3 pattern_manager.py lines 233 & 477
        rates = config["pattern_learning"]["learning_rates"]
        assert rates["early_observations"] == 0.3
        assert rates["mature_observations"] == 0.2
        assert rates["observation_threshold"] == 5

    def test_reliability_thresholds_extracted(self):
        """Test V3 reliability thresholds are in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        # From V3 pattern_manager.py lines 155 & 264
        thresholds = config["pattern_learning"]["reliability_thresholds"]
        assert thresholds["min_confidence"] == 0.6
        assert thresholds["min_observations"] == 4

    def test_quality_thresholds_extracted(self):
        """Test V3 quality thresholds are in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        # From V3 pattern_manager.py lines 384 & 389
        quality = config["pattern_learning"]["quality_thresholds"]
        assert quality["update_confidence"] == 0.8
        assert quality["max_age_days"] == 14

    def test_manager_hierarchy_extracted(self):
        """Test V3 manager hierarchy is in config."""
        loader = ConfigLoader()
        config = loader.load_config()

        # From V3 shift_splitter.py lines 8-27
        hierarchy = config["shifts"]["manager_hierarchy"]
        assert hierarchy["general manager"] == 100
        assert hierarchy["shift manager"] == 75
        assert hierarchy["assistant manager"] == 70

    def test_restaurant_costs_extracted(self):
        """Test V3 restaurant costs are in config."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR")

        # From V3 restaurant_config.py
        vendor_costs = config["vendor_costs"]
        assert vendor_costs["Sysco"] == 2800
        assert vendor_costs["US Foods"] == 2200
        assert sum(vendor_costs.values()) == 8400

        overhead_costs = config["overhead_costs"]
        assert overhead_costs["Electric Company"] == 1200
        assert overhead_costs["Gas Service"] == 450
        assert sum(overhead_costs.values()) == 3154

    def test_cash_percentages_extracted(self):
        """Test V3 cash percentages are in config."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR")

        # From V3 restaurant_config.py
        cash = config["cash_percentages"]
        assert cash["regular_wages"] == 0.12
        assert cash["overtime_wages"] == 0.03


@pytest.mark.integration
class TestConfigCompleteness:
    """Verify production configs have all required keys."""

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_prod_config_has_all_sections(self):
        """Test prod config has all required sections."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="prod")

        required_sections = [
            "system",
            "business_standards",
            "shifts",
            "pattern_learning",
            "overtime",
            "data_quality",
            "confidence_levels",
            "quality_levels",
            "logging",
            "database",
            "features",
            "restaurant",
            "vendor_costs",
            "overhead_costs",
            "cash_percentages"
        ]

        for section in required_sections:
            assert section in config, f"Missing section: {section}"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_all_restaurants_have_metadata(self):
        """Test all restaurants have required metadata."""
        loader = ConfigLoader()

        for code in ["SDR", "T12", "TK9"]:
            config = loader.load_config(restaurant_code=code, env="dev")

            restaurant = config["restaurant"]
            assert restaurant["code"] == code
            assert "display_name" in restaurant
            assert "icon" in restaurant
            assert "color" in restaurant

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_all_restaurants_have_costs(self):
        """Test all restaurants have vendor and overhead costs."""
        loader = ConfigLoader()

        for code in ["SDR", "T12", "TK9"]:
            config = loader.load_config(restaurant_code=code, env="dev")

            # Check vendor costs
            assert "vendor_costs" in config
            vendor_total = sum(config["vendor_costs"].values())
            assert vendor_total == 8400, f"{code} vendor costs don't sum to $8400"

            # Check overhead costs
            assert "overhead_costs" in config
            overhead_total = sum(config["overhead_costs"].values())
            assert overhead_total == 3154, f"{code} overhead costs don't sum to $3154"


@pytest.mark.integration
class TestEnvironmentDifferences:
    """Test dev vs prod environment differences work correctly."""

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_logging_differs_by_environment(self):
        """Test logging level differs between dev and prod."""
        loader = ConfigLoader()

        dev_config = loader.load_config(restaurant_code="SDR", env="dev")
        prod_config = loader.load_config(restaurant_code="SDR", env="prod")

        assert dev_config["logging"]["level"] == "DEBUG"
        assert prod_config["logging"]["level"] == "INFO"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_shadow_mode_differs_by_environment(self):
        """Test shadow_mode differs between dev and prod."""
        loader = ConfigLoader()

        dev_config = loader.load_config(restaurant_code="SDR", env="dev")
        prod_config = loader.load_config(restaurant_code="SDR", env="prod")

        assert dev_config["features"]["shadow_mode"] is True
        assert prod_config["features"]["shadow_mode"] is False

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_quality_thresholds_differ_by_environment(self):
        """Test quality thresholds are relaxed in dev."""
        loader = ConfigLoader()

        dev_config = loader.load_config(restaurant_code="SDR", env="dev")
        prod_config = loader.load_config(restaurant_code="SDR", env="prod")

        dev_quality = dev_config["pattern_learning"]["quality_thresholds"]
        prod_quality = prod_config["pattern_learning"]["quality_thresholds"]

        # Dev should be more lenient
        assert dev_quality["update_confidence"] < prod_quality["update_confidence"]
        assert dev_quality["max_age_days"] > prod_quality["max_age_days"]

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_parallelization_differs_by_environment(self):
        """Test parallelization settings differ."""
        loader = ConfigLoader()

        dev_config = loader.load_config(restaurant_code="SDR", env="dev")
        prod_config = loader.load_config(restaurant_code="SDR", env="prod")

        # Dev should use fewer workers for debugging
        assert dev_config["processing"]["parallel_workers"] == 2
        assert prod_config["processing"]["parallel_workers"] == 6


@pytest.mark.integration
class TestRealWorldUsage:
    """Test realistic usage patterns."""

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_convenience_function_works(self):
        """Test convenience function for quick loading."""
        from pipeline.infrastructure.config.loader import load_config

        config = load_config(restaurant_code="SDR", env="dev")
        assert config["restaurant"]["code"] == "SDR"

    @patch.dict(os.environ, TEST_ENV_VARS)
    def test_accessing_nested_values(self):
        """Test accessing deeply nested configuration values."""
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="dev")

        # Test accessing nested values (common usage pattern)
        cutoff_hour = config["shifts"]["cutoff_hour"]
        assert cutoff_hour == 14

        early_rate = config["pattern_learning"]["learning_rates"]["early_observations"]
        assert early_rate == 0.3

        lobby_target = config["business_standards"]["service_time_targets"]["Lobby"]
        assert lobby_target == 15.0

    def test_loading_base_only_for_defaults(self):
        """Test loading only base config for system defaults."""
        loader = ConfigLoader()
        config = loader.load_config()

        # Should have system defaults but no restaurant-specific data
        assert "business_standards" in config
        assert "restaurant" not in config
        assert "vendor_costs" not in config
