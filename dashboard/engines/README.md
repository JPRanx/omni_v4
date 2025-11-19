# Dashboard V3 - Engine Systems

## Overview

The Engine Systems are smart, independent modules that consume configurations from `/shared/config/` and provide high-level functionality for the Dashboard V3 application.

## Architecture

```
DashboardV3/
├── shared/config/          # Configuration source (538 configs)
└── engines/                # Smart systems (5 engines)
    ├── ThemeEngine.js      # Theme management
    ├── LayoutEngine.js     # Layout & responsive behavior
    ├── BusinessEngine.js   # Business logic & calculations
    ├── DeviceRouter.js     # Device detection & routing
    ├── ConfigValidator.js  # Configuration validation
    ├── index.js            # Central initialization
    ├── EXAMPLE_USAGE.js    # Complete usage examples
    └── README.md           # This file
```

## The 5 Engines

### 1. ThemeEngine.js

**Purpose:** Manages all visual styling and theming

**Capabilities:**
- Load theme configs (colors, shadows, typography, spacing, borders, animations)
- Generate CSS variables dynamically
- Apply theme to DOM
- Switch between themes (desert/ocean)
- Create stylesheets from config values
- Inject CSS into document

**Usage:**
```javascript
import ThemeEngine from './engines/ThemeEngine.js';
import config from './shared/config/index.js';

const themeEngine = new ThemeEngine(config);

// Apply theme
themeEngine.applyTheme('desert');

// Get colors
const primaryColor = themeEngine.getColor('desert.bronzeDust');

// Get shadows
const shadow = themeEngine.getComponentShadow('header', 'default');

// Get typography
const fontSize = themeEngine.getTypography('sizes', '2xl');
```

**Methods:**
- `applyTheme(themeName)` - Apply desert or ocean theme
- `getColor(path)` - Get color by dot-notation path
- `getShadow(name)` - Get shadow by name
- `getComponentShadow(component, state)` - Get component-specific shadow
- `getTypography(category, name)` - Get typography value
- `getSpacing(name)` - Get spacing value
- `getBorder(category, name)` - Get border value
- `getAnimation(name)` - Get animation config
- `exportThemeCSS()` - Export complete theme as CSS
- `getStats()` - Get theme statistics

---

### 2. LayoutEngine.js

**Purpose:** Manages responsive layouts and grid systems

**Capabilities:**
- Detect device type (mobile, tablet, iPad, desktop)
- Detect current breakpoint
- Return appropriate grid layouts for device
- Manage container widths and spacing
- Handle responsive breakpoints
- Provide layout recommendations

**Usage:**
```javascript
import LayoutEngine from './engines/LayoutEngine.js';
import config from './shared/config/index.js';

const layoutEngine = new LayoutEngine(config);

// Get device
const device = layoutEngine.getCurrentDevice(); // 'mobile' | 'tablet' | 'ipad' | 'desktop'

// Get grid classes
const gridClasses = layoutEngine.getGridClasses('metrics');

// Get grid columns
const columns = layoutEngine.getGridColumns('metrics');

// Get container classes
const containerClasses = layoutEngine.getContainerClasses('dashboard');

// Check device
const isMobile = layoutEngine.isMobile();
```

**Methods:**
- `getCurrentDevice()` - Get device type
- `getCurrentBreakpoint()` - Get current breakpoint
- `isMobile()` - Check if mobile
- `isTablet()` - Check if tablet
- `isIPad()` - Check if iPad
- `isDesktop()` - Check if desktop
- `getGrid(gridName)` - Get grid configuration
- `getGridClasses(gridName)` - Get responsive grid classes
- `getGridColumns(gridName)` - Get column count for device
- `getContainer(variant)` - Get container config
- `getContainerClasses(variant)` - Get container classes
- `getZIndex(layer)` - Get z-index value
- `getLayoutRecommendations()` - Get recommendations for device
- `onLayoutChange(callback)` - Subscribe to layout changes

---

### 3. BusinessEngine.js

**Purpose:** Handles all business logic and calculations

**Capabilities:**
- Evaluate data against thresholds
- Calculate all business metrics (labor %, COGS %, profit margin)
- Calculate grades (A+ to F)
- Determine statuses (excellent, good, poor, critical)
- Calculate variances (day-over-day, week-over-week)
- Format business data for display
- Complete restaurant performance evaluation

**Usage:**
```javascript
import BusinessEngine from './engines/BusinessEngine.js';
import config from './shared/config/index.js';

const businessEngine = new BusinessEngine(config);

// Evaluate restaurant
const restaurantData = {
  sales: 45000,
  laborCost: 12000,
  laborHours: 320,
  cogs: 13500,
};

const evaluation = businessEngine.evaluateRestaurant(restaurantData);
// Returns: metrics, statuses, grade, isPassing, isExcellent, needsAttention

// Calculate specific metrics
const laborPercent = businessEngine.calculateLaborPercent(laborCost, sales);
const netProfit = businessEngine.calculateNetProfit(sales, laborCost, cogs);
const grade = businessEngine.calculateGrade({ sales, laborPercent, profitMargin });

// Format values
const formattedSales = businessEngine.formatCurrency(sales);
const formattedPercent = businessEngine.formatPercentage(laborPercent);
```

**Methods:**
- `evaluateRestaurant(data)` - Complete evaluation
- `evaluateDay(currentDay, previousDay)` - Day evaluation with variance
- `evaluateWeek(days)` - Week evaluation with summary
- `evaluateSales(sales)` - Get sales status
- `evaluateLabor(laborPercent)` - Get labor status
- `calculateLaborPercent(laborCost, sales)` - Calculate labor %
- `calculateCOGSPercent(cogs, sales)` - Calculate COGS %
- `calculateProfitMargin(netProfit, sales)` - Calculate profit margin
- `calculateNetProfit(sales, labor, cogs, other)` - Calculate net profit
- `calculateGrade(metrics)` - Calculate grade from metrics
- `formatCurrency(value)` - Format as currency
- `formatPercentage(value)` - Format as percentage
- `formatVariance(value)` - Format variance with color

---

### 4. DeviceRouter.js

**Purpose:** Detects device and routes to appropriate interface

**Capabilities:**
- Detect device type (iPad, iPhone, Desktop)
- Detect device capabilities (touch, hover, GPU, connection)
- Route to appropriate interface (/ipad or /mobile)
- Manage feature availability per device
- Provide device-specific optimizations
- Generate device reports

**Usage:**
```javascript
import DeviceRouter from './engines/DeviceRouter.js';
import config from './shared/config/index.js';

const deviceRouter = new DeviceRouter(config);

// Get device and route
const deviceType = deviceRouter.getDeviceType(); // 'mobile' | 'ipad' | 'desktop'
const route = deviceRouter.getRoute(); // '/mobile' | '/ipad'

// Navigate to appropriate interface
deviceRouter.navigate();

// Check capabilities
const capabilities = deviceRouter.getCapabilities();
// Returns: hasTouch, hasHover, hasAnimations, hasGPU, etc.

// Check feature availability
const isAvailable = deviceRouter.isFeatureAvailable('gradientAnimations');

// Get optimizations
const optimizations = deviceRouter.getOptimizations();
// Returns: useLightweightMode, enableAnimations, lazyLoadImages, etc.
```

**Methods:**
- `getDeviceType()` - Get device type
- `getRoute()` - Get recommended route
- `navigate(replace)` - Navigate to appropriate interface
- `shouldRedirect()` - Check if redirect needed
- `isMobile()` - Check if mobile
- `isIPad()` - Check if iPad
- `isTablet()` - Check if tablet
- `isDesktop()` - Check if desktop
- `getCapabilities()` - Get device capabilities
- `isFeatureAvailable(feature)` - Check feature availability
- `getEnabledFeatures()` - Get enabled features array
- `getOptimizations()` - Get device-specific optimizations
- `getInterfaceConfig()` - Get complete interface config
- `getDeviceReport()` - Get detailed device report
- `logDeviceInfo()` - Log device info to console

---

### 5. ConfigValidator.js

**Purpose:** Validates all configuration values

**Capabilities:**
- Validate all 538 config values on load
- Check for missing required configs
- Validate data types and ranges
- Report errors/warnings to console
- Provide config health check
- Generate validation reports

**Usage:**
```javascript
import ConfigValidator from './engines/ConfigValidator.js';
import config from './shared/config/index.js';

const validator = new ConfigValidator(config);

// Get validation report
const report = validator.getReport();
// Returns: valid, stats, errors, warnings, info

// Get health check
const health = validator.getHealthCheck();
// Returns: status, score, issues

// Check validity
if (report.valid) {
  console.log('✅ All 538 configurations valid');
} else {
  console.error('❌ Configuration errors found:', report.errors);
}
```

**Methods:**
- `validate()` - Run validation on all configs
- `getReport()` - Get detailed validation report
- `getHealthCheck()` - Get health check (status, score)
- `exportReport()` - Export report as JSON string

---

## Quick Start

### Initialize All Engines

```javascript
import { initializeEngines } from './engines/index.js';
import config from './shared/config/index.js';

// Initialize all engines at once
const engines = initializeEngines(config);

// Access individual engines
const { themeEngine, layoutEngine, businessEngine, deviceRouter, validator } = engines;

// All engines are now ready to use!
```

### Real-World Example: Render Restaurant Card

```javascript
const restaurant = {
  name: 'Downtown Bistro',
  sales: 52000,
  laborCost: 14000,
  cogs: 15000,
};

// 1. Evaluate performance
const evaluation = businessEngine.evaluateRestaurant(restaurant);

// 2. Get styling
const shadow = themeEngine.getComponentShadow('restaurantCard', 'default');
const borderRadius = themeEngine.getBorder('radius', 'lg');

// 3. Get layout
const gridClasses = layoutEngine.getGridClasses('restaurants');

// 4. Get device optimizations
const { lazyLoadImages } = deviceRouter.getOptimizations();

// 5. Format values
const formattedSales = businessEngine.formatCurrency(restaurant.sales);
const statusClasses = businessEngine.getStatusClasses(evaluation.statuses.overall);

// Now render card with all this data!
```

## Key Features

### ✅ Configuration-Driven
All engines consume configs from `/shared/config/` - no hardcoded values

### ✅ Independent Operation
Each engine can be used standalone or together - no tight coupling

### ✅ Comprehensive Coverage
538 configurations managed across 5 specialized engines

### ✅ Type Safety Ready
Clear interfaces and return types - ready for TypeScript conversion

### ✅ Performance Optimized
Device-specific optimizations and lazy evaluation

### ✅ Developer-Friendly
Clear APIs, comprehensive examples, detailed documentation

## Configuration Breakdown

- **Theme:** 271 configs (colors, shadows, typography, spacing, borders, animations)
- **Layout:** 41 configs (grids, containers, breakpoints, z-index)
- **Business:** 53 configs (thresholds, formulas, grading, statuses)
- **Content:** 116 configs (labels, messages, formats)
- **Features:** 35 configs (toggles, capabilities, experimental)
- **Resolution:** 8 conflict resolutions

**Total:** 538 configurations

## Testing

Run the example file to see all engines in action:

```javascript
// This will demonstrate all engine capabilities
import './engines/EXAMPLE_USAGE.js';
```

## Next Steps

With the engines complete, you're ready to build:

1. **iPad Interface** (`/ipad`) - Full dashboard experience
2. **Mobile Interface** (`/mobile`) - Simplified companion app

Both interfaces will consume these engines for:
- Theming (ThemeEngine)
- Responsive layouts (LayoutEngine)
- Business calculations (BusinessEngine)
- Device optimization (DeviceRouter)
- Configuration validation (ConfigValidator)

## Philosophy

**"Smart engines, dumb components"**

Engines contain all the intelligence and business logic. Components simply render what the engines provide. This architecture ensures:
- Single source of truth (configs)
- Easy testing (engines are independent)
- Consistent behavior (same logic everywhere)
- Maintainability (change configs, not code)

---

**Status:** ✅ Phase 2 Complete - All 5 engines ready for production use!
