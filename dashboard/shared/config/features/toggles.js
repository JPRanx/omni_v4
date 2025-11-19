/**
 * Dashboard V3 - Feature Toggles
 *
 * Feature flag configuration for enabling/disabling features
 * Total Toggles: 15
 *
 * Breakdown:
 * - Core Features: 5 (always enabled)
 * - Optional Features: 5 (can be toggled)
 * - Experimental Features: 5 (beta/testing)
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (feature implementations)
 * - Component architecture patterns
 */

// ============================================
// CORE FEATURES (5 toggles)
// Essential features - typically always enabled
// ============================================

export const core = {
  /**
   * Week navigation tabs
   * Allows users to switch between different weeks
   */
  weekTabs: {
    enabled: true,
    name: 'Week Tabs',
    description: 'Navigate between different weeks of data',
    required: true,
    category: 'navigation',
  },

  /**
   * Overview card with key metrics
   * Displays high-level summary metrics
   */
  overviewCard: {
    enabled: true,
    name: 'Overview Card',
    description: 'Display summary metrics for selected week',
    required: true,
    category: 'metrics',
  },

  /**
   * Restaurant cards grid
   * Displays individual restaurant performance cards
   */
  restaurantCards: {
    enabled: true,
    name: 'Restaurant Cards',
    description: 'Individual restaurant performance cards',
    required: true,
    category: 'restaurants',
  },

  /**
   * Metric cards (6 key metrics)
   * Displays individual metric cards with values
   */
  metricCards: {
    enabled: true,
    name: 'Metric Cards',
    description: 'Individual metric cards with key performance indicators',
    required: true,
    category: 'metrics',
  },

  /**
   * Investigation modal
   * Detailed breakdown and analysis modal
   */
  investigationModal: {
    enabled: true,
    name: 'Investigation Modal',
    description: 'Detailed daily breakdown and trends analysis',
    required: true,
    category: 'analysis',
  },
};

// ============================================
// OPTIONAL FEATURES (5 toggles)
// Features that can be enabled/disabled
// ============================================

export const optional = {
  /**
   * Auto clockout section
   * Displays employees approaching auto-clockout
   */
  autoClockout: {
    enabled: true,
    name: 'Auto Clockout',
    description: 'Display employees approaching auto-clockout threshold',
    required: false,
    category: 'labor',
  },

  /**
   * P&L quadrant display
   * Shows profit and loss breakdown in quadrants
   */
  pnlQuadrant: {
    enabled: true,
    name: 'P&L Quadrant',
    description: 'Profit and loss quadrant visualization',
    required: false,
    category: 'financial',
  },

  /**
   * Gradient animations on headers
   * Visual polish with animated gradients
   */
  gradientAnimations: {
    enabled: true,
    name: 'Gradient Animations',
    description: 'Animated gradient effects on headers and cards',
    required: false,
    category: 'visual',
  },

  /**
   * Hover effects on interactive elements
   * Transform and shadow animations on hover
   */
  hoverEffects: {
    enabled: true,
    name: 'Hover Effects',
    description: 'Interactive hover animations and effects',
    required: false,
    category: 'visual',
  },

  /**
   * Export functionality
   * Export dashboard data to CSV/PDF
   */
  export: {
    enabled: false,
    name: 'Export',
    description: 'Export dashboard data to CSV or PDF format',
    required: false,
    category: 'data',
  },
};

// ============================================
// EXPERIMENTAL FEATURES (5 toggles)
// Beta features under development
// ============================================

export const experimental = {
  /**
   * Iceberg analysis section
   * Epic center detection for operational issues
   */
  icebergAnalysis: {
    enabled: false,
    name: 'Iceberg Analysis',
    description: 'Epic center detection for hidden operational issues',
    required: false,
    category: 'analysis',
    beta: true,
  },

  /**
   * Real-time data updates
   * Auto-refresh dashboard with live data
   */
  realTimeUpdates: {
    enabled: false,
    name: 'Real-Time Updates',
    description: 'Automatic data refresh at regular intervals',
    required: false,
    category: 'data',
    beta: true,
  },

  /**
   * Advanced filtering
   * Filter restaurants by multiple criteria
   */
  advancedFiltering: {
    enabled: false,
    name: 'Advanced Filtering',
    description: 'Filter restaurants by performance, status, and custom criteria',
    required: false,
    category: 'navigation',
    beta: true,
  },

  /**
   * Predictive analytics
   * AI-powered sales and labor predictions
   */
  predictiveAnalytics: {
    enabled: false,
    name: 'Predictive Analytics',
    description: 'AI-powered predictions for sales and labor costs',
    required: false,
    category: 'analysis',
    beta: true,
  },

  /**
   * Custom dashboards
   * User-configurable dashboard layouts
   */
  customDashboards: {
    enabled: false,
    name: 'Custom Dashboards',
    description: 'Create custom dashboard layouts and metric selections',
    required: false,
    category: 'customization',
    beta: true,
  },
};

// ============================================
// FEATURE MANAGEMENT (utility functions)
// ============================================

export const management = {
  /**
   * Check if feature is enabled
   * @param {string} category - Feature category (core, optional, experimental)
   * @param {string} feature - Feature key
   * @returns {boolean} True if enabled
   */
  isEnabled: (category, feature) => {
    const categories = { core, optional, experimental };
    return categories[category]?.[feature]?.enabled ?? false;
  },

  /**
   * Enable a feature
   * @param {string} category - Feature category
   * @param {string} feature - Feature key
   */
  enable: (category, feature) => {
    const categories = { core, optional, experimental };
    if (categories[category]?.[feature]) {
      categories[category][feature].enabled = true;
    }
  },

  /**
   * Disable a feature (only if not required)
   * @param {string} category - Feature category
   * @param {string} feature - Feature key
   * @returns {boolean} True if disabled, false if required
   */
  disable: (category, feature) => {
    const categories = { core, optional, experimental };
    const featureObj = categories[category]?.[feature];

    if (featureObj && !featureObj.required) {
      featureObj.enabled = false;
      return true;
    }
    return false;
  },

  /**
   * Get all enabled features
   * @returns {Array<Object>} Array of enabled features
   */
  getEnabled: () => {
    const allFeatures = [
      ...Object.entries(core),
      ...Object.entries(optional),
      ...Object.entries(experimental),
    ];

    return allFeatures
      .filter(([_, feature]) => feature.enabled)
      .map(([key, feature]) => ({ key, ...feature }));
  },

  /**
   * Get features by category
   * @param {string} categoryName - Category name
   * @returns {Array<Object>} Array of features in category
   */
  getByCategory: (categoryName) => {
    const allFeatures = [
      ...Object.entries(core).map(([key, f]) => ({ key, ...f, group: 'core' })),
      ...Object.entries(optional).map(([key, f]) => ({ key, ...f, group: 'optional' })),
      ...Object.entries(experimental).map(([key, f]) => ({ key, ...f, group: 'experimental' })),
    ];

    return allFeatures.filter(feature => feature.category === categoryName);
  },

  /**
   * Get all beta features
   * @returns {Array<Object>} Array of beta features
   */
  getBetaFeatures: () => {
    return Object.entries(experimental)
      .filter(([_, feature]) => feature.beta)
      .map(([key, feature]) => ({ key, ...feature }));
  },
};

// ============================================
// FEATURE DEPENDENCIES
// Features that depend on other features
// ============================================

export const dependencies = {
  /**
   * Iceberg analysis requires investigation modal
   */
  icebergAnalysis: ['investigationModal'],

  /**
   * Advanced filtering requires restaurant cards
   */
  advancedFiltering: ['restaurantCards'],

  /**
   * Predictive analytics requires metric cards
   */
  predictiveAnalytics: ['metricCards', 'investigationModal'],

  /**
   * Check if all dependencies are enabled
   * @param {string} featureName - Feature to check
   * @returns {boolean} True if all dependencies enabled
   */
  areDependenciesMet: (featureName) => {
    const deps = dependencies[featureName];
    if (!deps) return true;

    return deps.every(dep => {
      return (
        management.isEnabled('core', dep) ||
        management.isEnabled('optional', dep) ||
        management.isEnabled('experimental', dep)
      );
    });
  },
};

// ============================================
// FEATURE PRESETS
// Pre-configured feature sets
// ============================================

export const presets = {
  /**
   * Minimal preset - only required features
   */
  minimal: {
    name: 'Minimal',
    description: 'Only essential features enabled',
    features: {
      core: { ...core },
      optional: Object.fromEntries(
        Object.entries(optional).map(([key, f]) => [key, { ...f, enabled: false }])
      ),
      experimental: Object.fromEntries(
        Object.entries(experimental).map(([key, f]) => [key, { ...f, enabled: false }])
      ),
    },
  },

  /**
   * Standard preset - core + recommended optional features
   */
  standard: {
    name: 'Standard',
    description: 'Recommended feature set for most users',
    features: {
      core: { ...core },
      optional: {
        ...optional,
        export: { ...optional.export, enabled: false },
      },
      experimental: Object.fromEntries(
        Object.entries(experimental).map(([key, f]) => [key, { ...f, enabled: false }])
      ),
    },
  },

  /**
   * Full preset - all features enabled
   */
  full: {
    name: 'Full',
    description: 'All features including experimental',
    features: {
      core: { ...core },
      optional: Object.fromEntries(
        Object.entries(optional).map(([key, f]) => [key, { ...f, enabled: true }])
      ),
      experimental: Object.fromEntries(
        Object.entries(experimental).map(([key, f]) => [key, { ...f, enabled: true }])
      ),
    },
  },

  /**
   * Apply preset
   * @param {string} presetName - Preset name ('minimal', 'standard', 'full')
   */
  apply: (presetName) => {
    const preset = presets[presetName];
    if (!preset) return;

    Object.assign(core, preset.features.core);
    Object.assign(optional, preset.features.optional);
    Object.assign(experimental, preset.features.experimental);
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  core,
  optional,
  experimental,
  management,
  dependencies,
  presets,

  // Metadata
  totalToggles: 15,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
