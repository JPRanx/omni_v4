# OMNI V4 Configuration System

## Overview

OMNI V4 uses a hierarchical YAML-based configuration system that replaces V3's hardcoded values with a flexible, maintainable approach.

### Key Features

- **3-Layer Hierarchy**: Base defaults → Restaurant overrides → Environment overlays
- **Deep Merging**: Restaurant/environment configs override only specific values, not entire sections
- **Environment Variables**: Database credentials and secrets loaded from `.env`
- **Type Safety**: Validation ensures all required fields are present
- **Zero Code Changes**: Add new restaurants or modify settings without touching code

---

## Configuration Hierarchy

Configs are loaded in this order, with later layers overriding earlier ones:

```
1. config/base.yaml          (System defaults - all V3 hardcoded values)
2. config/restaurants/{code}.yaml  (Restaurant-specific costs, metadata)
3. config/environments/{env}.yaml  (dev/prod settings)
```

### Example

```python
from src.infrastructure.config.loader import load_config

# Load SDR restaurant configuration for development
config = load_config(restaurant_code="SDR", env="dev")

# Access configuration values
cutoff_hour = config["shifts"]["cutoff_hour"]  # 14 (from base.yaml)
icon = config["restaurant"]["icon"]             # 🌯 (from SDR.yaml)
log_level = config["logging"]["level"]          # DEBUG (from dev.yaml)
```

---

## File Structure

```
config/
├── base.yaml                    # System-wide defaults (DO NOT EDIT without approval)
├── restaurants/
│   ├── SDR.yaml                # Sandra's Mexican Cuisine
│   ├── T12.yaml                # Tink-A-Tako #12
│   └── TK9.yaml                # Tink-A-Tako #9
└── environments/
    ├── dev.yaml                # Development settings
    └── prod.yaml               # Production settings
```

---

## Configuration Files

### 1. base.yaml (System Defaults)

Contains all V3 hardcoded values extracted from the original codebase:

#### Business Standards
```yaml
business_standards:
  service_time_targets:
    Lobby: 15.0          # Max acceptable service time (minutes)
    Drive-Thru: 8.0
    ToGo: 10.0
```
**Source**: V3 `main_v3.py` lines 74-78

#### Shift Configuration
```yaml
shifts:
  cutoff_hour: 14        # 2 PM - morning/evening split
  manager_hierarchy:
    "general manager": 100
    "shift manager": 75
    # ... (see base.yaml for full hierarchy)
```
**Source**: V3 `shift_splitter.py` lines 7-27

#### Pattern Learning
```yaml
pattern_learning:
  learning_rates:
    early_observations: 0.3    # First 5 observations
    mature_observations: 0.2   # After 5 observations
  reliability_thresholds:
    min_confidence: 0.6
    min_observations: 4
  quality_thresholds:
    update_confidence: 0.8
    max_age_days: 14
```
**Source**: V3 `pattern_manager.py` lines 233, 477, 155, 264, 389

---

### 2. restaurants/{code}.yaml (Restaurant Configs)

Each restaurant has its own configuration file with:

- **Metadata**: Display name, icon, color, capacity, tables
- **Vendor Costs**: Weekly costs across 5 vendors (total: $8,400/week)
- **Overhead Costs**: Weekly overhead across 7 categories (total: $3,154/week)
- **Cash Percentages**: Percentage of wages paid in cash

#### Example: SDR.yaml
```yaml
restaurant:
  code: "SDR"
  display_name: "Sandra's Mexican Cuisine"
  icon: "🌯"
  color: "#C67B5C"

vendor_costs:
  Sysco: 2800
  "US Foods": 2200
  # ... (see SDR.yaml for full list)

overhead_costs:
  "Electric Company": 1200
  "Gas Service": 450
  # ... (see SDR.yaml for full list)
```

**Source**: V3 `restaurant_config.py`

---

### 3. environments/{env}.yaml (Environment Configs)

Environment-specific settings for dev vs prod:

| Setting | Dev | Prod |
|---------|-----|------|
| Logging Level | DEBUG | INFO |
| Shadow Mode | True (write to v4_* tables) | False (write to prod tables) |
| Parallel Workers | 2 (easier debugging) | 6 (full parallelization) |
| Quality Thresholds | Relaxed (0.5 confidence) | Strict (0.8 confidence) |
| Pattern Age | 365 days (historical testing) | 14 days (recent only) |

#### Database Connection (Both Envs)
```yaml
database:
  url: "${SUPABASE_URL}"      # Loaded from .env
  key: "${SUPABASE_KEY}"
  service_key: "${SUPABASE_SERVICE_KEY}"
```

---

## Usage Guide

### Loading Configuration

```python
from src.infrastructure.config.loader import ConfigLoader, load_config

# Method 1: Using the loader class
loader = ConfigLoader()
config = loader.load_config(restaurant_code="SDR", env="dev")

# Method 2: Using the convenience function
config = load_config(restaurant_code="SDR", env="dev")

# Load only base config (system defaults)
config = load_config()  # No restaurant or environment
```

### Accessing Values

```python
# Access nested values
cutoff_hour = config["shifts"]["cutoff_hour"]
lobby_target = config["business_standards"]["service_time_targets"]["Lobby"]
early_rate = config["pattern_learning"]["learning_rates"]["early_observations"]

# Restaurant-specific values
display_name = config["restaurant"]["display_name"]
vendor_total = sum(config["vendor_costs"].values())
```

### Available Restaurants and Environments

```python
loader = ConfigLoader()

# Get list of restaurant codes
codes = loader.get_restaurant_codes()  # ["SDR", "T12", "TK9"]

# Get list of environments
envs = loader.get_environments()  # ["dev", "prod"]
```

---

## Adding a New Restaurant

1. **Create YAML file**: `config/restaurants/NEW.yaml`
   ```yaml
   restaurant:
     code: "NEW"
     display_name: "New Restaurant Name"
     short_name: "New"
     type: "Fast Casual"
     icon: "🍔"
     color: "#FF5733"

   vendor_costs:
     Sysco: 2800
     # ... (copy structure from SDR.yaml)

   overhead_costs:
     "Electric Company": 1200
     # ... (copy structure from SDR.yaml)

   cash_percentages:
     regular_wages: 0.12
     overtime_wages: 0.03
   ```

2. **Test the configuration**:
   ```python
   config = load_config(restaurant_code="NEW", env="dev")
   assert config["restaurant"]["code"] == "NEW"
   ```

3. **Done!** No code changes needed.

---

## Modifying Configuration

### When to Edit base.yaml

**IMPORTANT**: `base.yaml` contains business logic extracted from V3. Changes require team approval.

**Edit base.yaml when**:
- Changing business performance standards (e.g., service time targets)
- Adjusting pattern learning algorithms (learning rates, thresholds)
- Modifying shift cutoff times system-wide

**Example**:
```yaml
# Change Drive-Thru target from 8.0 to 7.5 minutes
business_standards:
  service_time_targets:
    Drive-Thru: 7.5  # Updated requirement
```

### When to Edit Restaurant YAML

Edit restaurant YAML files for:
- Updated vendor or overhead costs
- Changed restaurant metadata (name, icon, color)
- Restaurant-specific business standards

**Example**:
```yaml
# SDR.yaml - Override lobby service time
business_standards:
  service_time_targets:
    Lobby: 16.0  # Sandra's allows slightly longer
```

### When to Edit Environment YAML

Edit environment files for:
- Adjusting logging verbosity
- Changing parallelization settings
- Modifying quality thresholds for testing

**Example**:
```yaml
# dev.yaml - Lower quality threshold for testing old data
pattern_learning:
  quality_thresholds:
    update_confidence: 0.3  # Very lenient for testing
```

---

## Environment Variables

Required variables in `.env` file:

```env
# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Environment
ENVIRONMENT=dev  # or prod
```

Variables are automatically substituted in YAML files:

```yaml
database:
  url: "${SUPABASE_URL}"  # Replaced with actual value from .env
```

---

## Validation

The ConfigLoader validates all configurations on load:

### Required Keys

- `system`, `business_standards`, `shifts`, `pattern_learning`
- `overtime`, `data_quality`, `logging`

### Required Nested Values

- `business_standards.service_time_targets` must have: `Lobby`, `Drive-Thru`, `ToGo`
- `shifts.cutoff_hour` must be integer 0-23
- `pattern_learning` must have `learning_rates` and `reliability_thresholds`

### Validation Errors

```python
# Missing environment variable
ConfigError: Environment variable not set: SUPABASE_URL

# Invalid restaurant code
ConfigError: Restaurant config not found: config/restaurants/INVALID.yaml

# Missing required field
ConfigError: Missing required configuration key: business_standards
```

---

## Deep Merge Behavior

When merging configurations, nested dictionaries are **deep merged** (not replaced):

```yaml
# base.yaml
pattern_learning:
  enabled: true
  learning_rates:
    early_observations: 0.3
    mature_observations: 0.2

# dev.yaml (override)
pattern_learning:
  quality_thresholds:
    update_confidence: 0.5

# Result (merged)
pattern_learning:
  enabled: true                    # From base (preserved)
  learning_rates:                  # From base (preserved)
    early_observations: 0.3
    mature_observations: 0.2
  quality_thresholds:              # From dev (added)
    update_confidence: 0.5
```

**Non-dict types are replaced**:
- Lists: Replaced entirely (not merged)
- Primitives (int, str, bool): Replaced entirely

---

## Best Practices

### 1. Use Base Config for Business Logic

Keep all business logic (service time targets, learning rates) in `base.yaml` for consistency across restaurants.

### 2. Override Sparingly

Only override values when truly restaurant-specific or environment-specific.

### 3. Document Overrides

Add comments explaining **why** you're overriding a base value:

```yaml
# SDR.yaml
business_standards:
  service_time_targets:
    Lobby: 16.0  # Sandra's has larger dining area, allows more time
```

### 4. Test After Changes

Run integration tests after modifying configs:

```bash
pytest tests/integration/test_config_integration.py -v
```

### 5. Keep Secrets in .env

Never commit credentials to YAML files. Use environment variable substitution:

```yaml
# Good
database:
  url: "${SUPABASE_URL}"

# Bad
database:
  url: "https://actual-project.supabase.co"  # DON'T DO THIS
```

---

## Testing

### Run All Config Tests

```bash
# Unit tests (30 tests)
pytest tests/unit/infrastructure/test_config_loader.py -v

# Integration tests (24 tests)
pytest tests/integration/test_config_integration.py -v -m integration

# All tests (54 tests)
pytest tests/ -v
```

### Test Specific Restaurant/Environment

```python
# Test SDR + dev combination
def test_my_config():
    config = load_config(restaurant_code="SDR", env="dev")
    assert config["restaurant"]["code"] == "SDR"
    assert config["environment"] == "dev"
```

### Validate Config Before Deployment

```bash
# Create validation script
python scripts/validate_config.py --restaurant SDR --env prod
```

---

## Troubleshooting

### Error: "Environment variable not set"

**Solution**: Add missing variable to `.env` file:
```bash
echo "SUPABASE_URL=https://your-project.supabase.co" >> .env
```

### Error: "Restaurant config not found"

**Solution**: Check restaurant code spelling. Valid codes: SDR, T12, TK9

### Error: "Missing required configuration key"

**Solution**: Ensure `base.yaml` has all required sections. Compare with original if needed.

### Values Not Updating

**Issue**: Changes to YAML not reflected in running code.

**Solution**: Restart the application. Configs are loaded once on startup.

---

## Migration from V3

V4 configuration replaces these V3 patterns:

| V3 Pattern | V4 Replacement |
|------------|----------------|
| Hardcoded in `main_v3.py` | `config/base.yaml` |
| Hardcoded in `shift_splitter.py` | `config/base.yaml` |
| Hardcoded in `pattern_manager.py` | `config/base.yaml` |
| Hardcoded in `restaurant_config.py` | `config/restaurants/{code}.yaml` |
| if/else for environment | `config/environments/{env}.yaml` |

### Example Migration

**V3 Code**:
```python
# main_v3.py
self.BUSINESS_STANDARDS = {
    'Lobby': 15.0,
    'Drive-Thru': 8.0,
    'ToGo': 10.0
}
```

**V4 Replacement**:
```python
# Component receives config via dependency injection
def __init__(self, config: Dict):
    self.standards = config["business_standards"]["service_time_targets"]
    # self.standards["Lobby"] == 15.0 (loaded from YAML)
```

---

## See Also

- [README.md](README.md) - V4 architecture overview
- [PROGRESS.md](PROGRESS.md) - Implementation roadmap
- [VENV_SETUP.md](VENV_SETUP.md) - Development environment setup
- V3 Codebase: `C:\Users\Jorge Alexander\restaurant_analytics_v3\Modules\`

---

**Last Updated**: 2025-01-02
**Maintained By**: OMNI V4 Development Team
**Questions?**: Review integration tests in `tests/integration/test_config_integration.py` for usage examples
