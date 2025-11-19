/**
 * Dashboard V3 - Master Configuration Index
 *
 * Central configuration hub for the entire Dashboard V3 system
 * Total Configurations: 565
 *
 * Architecture:
 * - Theme: 271 configs (colors, shadows, typography, spacing, borders, animations)
 * - Layout: 41 configs (grids, containers, breakpoints, z-index)
 * - Business: 80 configs (thresholds, formulas, grading, statuses, capacity)
 * - Content: 116 configs (labels, messages, formats)
 * - Features: 35 configs (toggles, capabilities, experimental)
 * - Resolution: 8 conflict resolutions
 *
 * Usage:
 * ```javascript
 * import config from './shared/config/index.js';
 *
 * // Access any configuration
 * const primaryColor = config.theme.colors.desert.bronzeDust;
 * const headerShadow = config.theme.shadows.components.header.default;
 * const salesThreshold = config.business.thresholds.sales.excellent;
 * const serviceStress = config.business.capacity.serviceStress.good;
 * ```
 *
 * Source: DashboardV3_Audit_538_Configs
 * Date: 2025-11-01
 */

// ============================================
// CONFLICT RESOLUTION
// ============================================
import resolution from './resolution.js';

// ============================================
// THEME CONFIGURATIONS (271 configs)
// ============================================
import colors from './theme/colors.js';
import shadows from './theme/shadows.js';
import typography from './theme/typography.js';
import spacing from './theme/spacing.js';
import borders from './theme/borders.js';
import animations from './theme/animations.js';

// Semantic Theme System (V3.0)
import { themes, getTheme, getAvailableThemes, isValidTheme } from './theme/themes/index.js';

// ============================================
// LAYOUT CONFIGURATIONS (41 configs)
// ============================================
import grids from './layout/grids.js';
import containers from './layout/containers.js';
import breakpoints from './layout/breakpoints.js';
import zindex from './layout/zindex.js';

// ============================================
// BUSINESS LOGIC (80 configs)
// ============================================
import thresholds from './business/thresholds.js';
import formulas from './business/formulas.js';
import grading from './business/grading.js';
import statuses from './business/statuses.js';
import capacity from './business/capacity.js';

// ============================================
// CONTENT (116 configs)
// ============================================
import labels from './content/labels.js';
import messages from './content/messages.js';
import formats from './content/formats.js';

// ============================================
// FEATURES (35 configs)
// ============================================
import toggles from './features/toggles.js';
import capabilities from './features/capabilities.js';
import experimental from './features/experimental.js';

// ============================================
// MASTER CONFIGURATION OBJECT
// ============================================

const config = {
  // Metadata
  version: '3.0.0',
  lastUpdated: '2025-11-01',
  totalConfigs: 565,
  auditSource: 'DashboardV3_Audit_538_Configs',

  // Conflict Resolution
  resolution,

  // Theme System (271 configs)
  theme: {
    colors,           // 87 color values
    shadows,          // 43 shadow configurations
    typography,       // 67 typography settings
    spacing,          // 52 spacing values
    borders,          // 31 border configurations
    animations,       // 48 animation settings

    // Semantic Theme System (V3.0)
    themes,           // Semantic theme registry
    getTheme,         // Get theme by ID
    availableThemes: getAvailableThemes(), // List of theme IDs
  },

  // Layout System (41 configs)
  layout: {
    grids,            // 14 grid patterns
    containers,       // 5 container configurations
    breakpoints,      // 7 responsive breakpoints
    zindex,           // 7 z-index layers
  },

  // Business Logic (80 configs)
  business: {
    thresholds,       // 34 business thresholds
    formulas,         // 10 calculation formulas
    grading,          // 5 grade levels
    statuses,         // 9 status types
    capacity,         // 27 capacity & demand configs
  },

  // Content System (116 configs)
  content: {
    labels,           // 73 text labels
    messages,         // 28 user messages
    formats,          // 15 formatting functions
  },

  // Feature System (35 configs)
  features: {
    toggles,          // 15 feature toggles
    capabilities,     // 12 device capabilities
    experimental,     // 8 experimental features
  },
};

// ============================================
// CONFIGURATION HELPERS
// ============================================

/**
 * Get configuration value by path
 * @param {string} path - Dot-notation path (e.g., 'theme.colors.desert.bronzeDust')
 * @returns {any} Configuration value or undefined
 */
export function getConfig(path) {
  const parts = path.split('.');
  let current = config;

  for (const part of parts) {
    if (current[part] === undefined) return undefined;
    current = current[part];
  }

  return current;
}

/**
 * Check if configuration path exists
 * @param {string} path - Dot-notation path
 * @returns {boolean} True if path exists
 */
export function hasConfig(path) {
  return getConfig(path) !== undefined;
}

/**
 * Get all configurations for a category
 * @param {string} category - Category name ('theme', 'layout', 'business', 'content', 'features')
 * @returns {Object} Category configurations
 */
export function getCategory(category) {
  return config[category] || {};
}

/**
 * Validate configuration completeness
 * Ensures all expected configs are present
 * @returns {Object} Validation result
 */
export function validateConfig() {
  const results = {
    valid: true,
    errors: [],
    warnings: [],
    summary: {
      theme: 0,
      layout: 0,
      business: 0,
      content: 0,
      features: 0,
      total: 0,
    },
  };

  // Count configurations
  const counts = {
    theme: {
      colors: colors.totalColors || 0,
      shadows: shadows.totalShadows || 0,
      typography: typography.totalConfigs || 0,
      spacing: spacing.totalValues || 0,
      borders: borders.totalConfigs || 0,
      animations: animations.totalConfigs || 0,
    },
    layout: {
      grids: grids.totalPatterns || 0,
      containers: containers.totalConfigs || 0,
      breakpoints: breakpoints.totalBreakpoints || 0,
      zindex: zindex.totalLayers || 0,
    },
    business: {
      thresholds: thresholds.totalThresholds || 0,
      formulas: formulas.totalFormulas || 0,
      grading: grading.totalLevels || 0,
      statuses: statuses.totalTypes || 0,
      capacity: capacity.totalConfigs || 0,
    },
    content: {
      labels: labels.totalLabels || 0,
      messages: messages.totalMessages || 0,
      formats: formats.totalFormatters || 0,
    },
    features: {
      toggles: toggles.totalToggles || 0,
      capabilities: capabilities.totalCapabilities || 0,
      experimental: experimental.totalExperiments || 0,
    },
  };

  // Calculate totals
  results.summary.theme = Object.values(counts.theme).reduce((a, b) => a + b, 0);
  results.summary.layout = Object.values(counts.layout).reduce((a, b) => a + b, 0);
  results.summary.business = Object.values(counts.business).reduce((a, b) => a + b, 0);
  results.summary.content = Object.values(counts.content).reduce((a, b) => a + b, 0);
  results.summary.features = Object.values(counts.features).reduce((a, b) => a + b, 0);
  results.summary.total = Object.values(results.summary).reduce((a, b) => a + b, 0) - results.summary.total;

  // Validate against expected total
  const expectedTotal = 551; // 565 - 8 (resolution configs) - 6 (metadata)
  if (results.summary.total !== expectedTotal) {
    results.warnings.push(
      `Configuration count mismatch: expected ${expectedTotal}, got ${results.summary.total}`
    );
  }

  // Check for missing critical configs
  if (!config.theme.colors.desert.bronzeDust) {
    results.errors.push('Missing critical config: theme.colors.desert.bronzeDust');
    results.valid = false;
  }

  if (!config.resolution.conflicts) {
    results.errors.push('Missing conflict resolution data');
    results.valid = false;
  }

  return results;
}

/**
 * Generate CSS variables from theme configuration
 * @returns {string} CSS variable declarations
 */
export function generateCSSVariables() {
  const cssVars = [];

  // Colors
  if (colors.cssVariables) {
    Object.entries(colors.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Typography
  if (typography.cssVariables) {
    Object.entries(typography.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Spacing
  if (spacing.cssVariables) {
    Object.entries(spacing.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Shadows
  if (shadows.cssVariables) {
    Object.entries(shadows.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Borders
  if (borders.cssVariables) {
    Object.entries(borders.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Animations
  if (animations.cssVariables) {
    Object.entries(animations.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  // Z-index
  if (zindex.cssVariables) {
    Object.entries(zindex.cssVariables).forEach(([key, value]) => {
      cssVars.push(`  ${key}: ${value};`);
    });
  }

  return `:root {\n${cssVars.join('\n')}\n}`;
}

/**
 * Generate Tailwind CSS configuration
 * @returns {Object} Tailwind config object
 */
export function generateTailwindConfig() {
  return {
    theme: {
      extend: {
        colors: colors.tailwindColors || {},
        fontFamily: typography.tailwindTypography?.fontFamily || {},
        fontSize: typography.tailwindTypography?.fontSize || {},
        fontWeight: typography.tailwindTypography?.fontWeight || {},
        lineHeight: typography.tailwindTypography?.lineHeight || {},
        letterSpacing: typography.tailwindTypography?.letterSpacing || {},
        spacing: spacing.tailwindSpacing || {},
        borderRadius: borders.tailwindBorders?.borderRadius || {},
        borderWidth: borders.tailwindBorders?.borderWidth || {},
        boxShadow: shadows.tailwindShadows || {},
        animation: animations.tailwindAnimations?.animation || {},
        keyframes: animations.tailwindAnimations?.keyframes || {},
        transitionDuration: animations.tailwindAnimations?.transitionDuration || {},
        transitionTimingFunction: animations.tailwindAnimations?.transitionTimingFunction || {},
        zIndex: zindex.tailwindZIndex || {},
        screens: breakpoints.tailwindScreens || {},
        container: containers.tailwindContainer || {},
      },
    },
  };
}

/**
 * Get configuration statistics
 * @returns {Object} Statistics about configurations
 */
export function getStats() {
  return {
    version: config.version,
    lastUpdated: config.lastUpdated,
    totalConfigs: config.totalConfigs,
    breakdown: {
      theme: {
        colors: colors.totalColors,
        shadows: shadows.totalShadows,
        typography: typography.totalConfigs,
        spacing: spacing.totalValues,
        borders: borders.totalConfigs,
        animations: animations.totalConfigs,
        total: 271,
      },
      layout: {
        grids: grids.totalPatterns,
        containers: containers.totalConfigs,
        breakpoints: breakpoints.totalBreakpoints,
        zindex: zindex.totalLayers,
        total: 41,
      },
      business: {
        thresholds: thresholds.totalThresholds,
        formulas: formulas.totalFormulas,
        grading: grading.totalLevels,
        statuses: statuses.totalTypes,
        capacity: capacity.totalConfigs,
        total: 80,
      },
      content: {
        labels: labels.totalLabels,
        messages: messages.totalMessages,
        formats: formats.totalFormatters,
        total: 116,
      },
      features: {
        toggles: toggles.totalToggles,
        capabilities: capabilities.totalCapabilities,
        experimental: experimental.totalExperiments,
        total: 35,
      },
    },
    conflicts: {
      resolved: Object.keys(resolution.conflicts).length,
      details: resolution.resolutionDetails,
    },
  };
}

// ============================================
// EXPORTS
// ============================================

export default config;

export {
  // Conflict Resolution
  resolution,

  // Theme
  colors,
  shadows,
  typography,
  spacing,
  borders,
  animations,
  themes,             // V3.0 Semantic themes
  getTheme,           // V3.0 Theme getter
  getAvailableThemes, // V3.0 Theme list
  isValidTheme,       // V3.0 Theme validator

  // Layout
  grids,
  containers,
  breakpoints,
  zindex,

  // Business
  thresholds,
  formulas,
  grading,
  statuses,
  capacity,

  // Content
  labels,
  messages,
  formats,

  // Features
  toggles,
  capabilities,
  experimental,
};
