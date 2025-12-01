"""
YAML Configuration Loader with Overlay Support

Implements hierarchical configuration loading:
1. base.yaml (system defaults)
2. restaurants/{restaurant_code}.yaml (restaurant-specific overrides)
3. environments/{env}.yaml (environment-specific overrides)

Supports:
- Deep merging of nested dictionaries
- Environment variable substitution (${VAR_NAME})
- Validation of required fields
- Type safety with proper typing
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration loading or validation fails."""
    pass


class ConfigLoader:
    """
    Hierarchical YAML configuration loader with overlay support.

    Usage:
        loader = ConfigLoader()
        config = loader.load_config(restaurant_code="SDR", env="dev")

        # Access nested values
        cutoff = config["shifts"]["cutoff_hour"]  # 14
        db_url = config["database"]["url"]  # Resolved from ${SUPABASE_URL}
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the ConfigLoader.

        Args:
            config_dir: Root config directory. Defaults to project_root/config/
        """
        if config_dir is None:
            # Default to project_root/config/
            project_root = Path(__file__).parent.parent.parent.parent
            config_dir = project_root / "config"

        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise ConfigError(f"Config directory not found: {self.config_dir}")

        # Load environment variables from .env file
        load_dotenv()

    def load_config(
        self,
        restaurant_code: Optional[str] = None,
        env: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load and merge configuration from multiple layers.

        Args:
            restaurant_code: Restaurant code (SDR, T12, TK9). If None, only base config.
            env: Environment name (dev, prod). If None, no environment overlay.

        Returns:
            Merged configuration dictionary

        Raises:
            ConfigError: If required config files are missing or invalid
        """
        # Start with base configuration
        config = self._load_yaml(self.config_dir / "base.yaml")

        # Merge restaurant-specific config
        if restaurant_code:
            restaurant_path = self.config_dir / "restaurants" / f"{restaurant_code}.yaml"
            if restaurant_path.exists():
                restaurant_config = self._load_yaml(restaurant_path)
                config = self._deep_merge(config, restaurant_config)
            else:
                raise ConfigError(
                    f"Restaurant config not found: {restaurant_path}. "
                    f"Valid codes: SDR, T12, TK9"
                )

        # Merge environment-specific config
        if env:
            env_path = self.config_dir / "environments" / f"{env}.yaml"
            if env_path.exists():
                env_config = self._load_yaml(env_path)
                config = self._deep_merge(config, env_config)
            else:
                raise ConfigError(
                    f"Environment config not found: {env_path}. "
                    f"Valid environments: dev, prod"
                )

        # Substitute environment variables
        config = self._substitute_env_vars(config)

        # Validate the final configuration
        self._validate(config)

        return config

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """
        Load a YAML file and return as dictionary.

        Args:
            path: Path to YAML file

        Returns:
            Dictionary representation of YAML

        Raises:
            ConfigError: If file cannot be loaded or parsed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigError(f"Invalid YAML structure in {path}: expected dict, got {type(data)}")
                return data
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {path}")
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML in {path}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config from {path}: {e}")

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries. Override values take precedence.

        For nested dictionaries, merge recursively instead of replacing.
        For other types (lists, primitives), override replaces base.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override replaces base (for primitives, lists, etc.)
                result[key] = value

        return result

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively substitute environment variables in configuration values.

        Replaces ${VAR_NAME} with os.environ.get("VAR_NAME").
        If the variable is not set, raises ConfigError.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with substituted values

        Raises:
            ConfigError: If required environment variable is not set
        """
        result = {}

        for key, value in config.items():
            if isinstance(value, dict):
                # Recursively substitute in nested dicts
                result[key] = self._substitute_env_vars(value)
            elif isinstance(value, str):
                # Check for ${VAR_NAME} pattern
                result[key] = self._substitute_string(value)
            else:
                # Leave other types unchanged
                result[key] = value

        return result

    def _substitute_string(self, value: str) -> str:
        """
        Substitute environment variables in a string.

        Args:
            value: String potentially containing ${VAR_NAME}

        Returns:
            String with substitutions

        Raises:
            ConfigError: If required environment variable is not set
        """
        # Pattern: ${VAR_NAME}
        pattern = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')

        def replacer(match):
            var_name = match.group(1)
            var_value = os.environ.get(var_name)
            if var_value is None:
                raise ConfigError(
                    f"Environment variable not set: {var_name}. "
                    f"Please set {var_name} in your .env file."
                )
            return var_value

        return pattern.sub(replacer, value)

    def _validate(self, config: Dict[str, Any]) -> None:
        """
        Validate the final merged configuration.

        Checks for required top-level keys and basic structure.

        Args:
            config: Configuration to validate

        Raises:
            ConfigError: If configuration is invalid
        """
        # Required top-level keys from base.yaml
        required_keys = [
            "system",
            "business_standards",
            "shifts",
            "pattern_learning",
            "overtime",
            "data_quality",
            "logging"
        ]

        for key in required_keys:
            if key not in config:
                raise ConfigError(f"Missing required configuration key: {key}")

        # Validate business_standards structure
        if "service_time_targets" not in config["business_standards"]:
            raise ConfigError("Missing business_standards.service_time_targets")

        required_targets = ["Lobby", "Drive-Thru", "ToGo"]
        for target in required_targets:
            if target not in config["business_standards"]["service_time_targets"]:
                raise ConfigError(
                    f"Missing required service time target: {target}"
                )

        # Validate shifts configuration
        if "cutoff_hour" not in config["shifts"]:
            raise ConfigError("Missing shifts.cutoff_hour")

        cutoff = config["shifts"]["cutoff_hour"]
        if not isinstance(cutoff, int) or not (0 <= cutoff <= 23):
            raise ConfigError(
                f"Invalid shifts.cutoff_hour: {cutoff}. Must be integer 0-23"
            )

        # Validate pattern_learning configuration
        if "learning_rates" not in config["pattern_learning"]:
            raise ConfigError("Missing pattern_learning.learning_rates")

        if "reliability_thresholds" not in config["pattern_learning"]:
            raise ConfigError("Missing pattern_learning.reliability_thresholds")

    def get_restaurant_codes(self) -> list[str]:
        """
        Get list of available restaurant codes.

        Returns:
            List of restaurant codes (e.g., ["SDR", "T12", "TK9"])
        """
        restaurant_dir = self.config_dir / "restaurants"
        if not restaurant_dir.exists():
            return []

        codes = []
        for path in restaurant_dir.glob("*.yaml"):
            codes.append(path.stem)

        return sorted(codes)

    def get_environments(self) -> list[str]:
        """
        Get list of available environments.

        Returns:
            List of environment names (e.g., ["dev", "prod"])
        """
        env_dir = self.config_dir / "environments"
        if not env_dir.exists():
            return []

        envs = []
        for path in env_dir.glob("*.yaml"):
            envs.append(path.stem)

        return sorted(envs)


# Convenience function for quick loading
def load_config(restaurant_code: Optional[str] = None, env: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        restaurant_code: Restaurant code (SDR, T12, TK9)
        env: Environment name (dev, prod)

    Returns:
        Merged configuration dictionary
    """
    loader = ConfigLoader()
    return loader.load_config(restaurant_code=restaurant_code, env=env)
