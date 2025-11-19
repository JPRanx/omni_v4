/**
 * Dashboard V3 - Theme Template
 *
 * Standard template for creating new themes
 * Ensures all themes have consistent structure and required colors
 */

import { validateThemeColors } from './colorRoles.js';

/**
 * Create a new theme with validation
 * @param {string} name - Display name for the theme
 * @param {Object} colors - Semantic color mappings
 * @param {Object} options - Optional theme enhancements
 * @returns {Object} Validated theme object
 */
export const createTheme = (name, colors, options = {}) => {
  // Validate theme has all required colors
  const validation = validateThemeColors(colors);

  if (!validation.isValid) {
    console.warn(`Theme '${name}' is missing colors:`, validation.missing);
    console.warn(`Coverage: ${validation.coverage}`);
  }

  return {
    name,

    // Required semantic colors (using underscore naming for consistency)
    colors: {
      // Text hierarchy
      text_primary: colors.text_primary,
      text_secondary: colors.text_secondary,
      text_muted: colors.text_muted,
      text_disabled: colors.text_disabled,

      // Backgrounds
      background_primary: colors.background_primary,
      background_card: colors.background_card,
      background_elevated: colors.background_elevated,
      background_hover: colors.background_hover,

      // Borders
      border_strong: colors.border_strong,
      border_default: colors.border_default,
      border_subtle: colors.border_subtle,

      // Accents
      accent_primary: colors.accent_primary,
      accent_secondary: colors.accent_secondary,
      accent_interactive: colors.accent_interactive,

      // Dashboard-specific
      dashboard_metric: colors.dashboard_metric,
      dashboard_metricLabel: colors.dashboard_metricLabel,
      dashboard_sectionHeader: colors.dashboard_sectionHeader,
      dashboard_tableHeader: colors.dashboard_tableHeader,
      dashboard_tableRow: colors.dashboard_tableRow,
      dashboard_gradientStart: colors.dashboard_gradientStart,
      dashboard_gradientEnd: colors.dashboard_gradientEnd,
    },

    // Status colors (can be theme-specific or use defaults)
    status: colors.status || {
      success: { bg: '#F0FDF4', text: '#15803D', border: '#86EFAC' },
      warning: { bg: '#FEF3C7', text: '#A16207', border: '#FDE047' },
      error: { bg: '#FEF2F2', text: '#B91C1C', border: '#FCA5A5' },
      info: { bg: '#F0F9FF', text: '#075985', border: '#7DD3FC' }
    },

    // Optional enhancements
    typography: options.typography || {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      scale: 1.0
    },

    animations: options.animations || {
      duration: 'normal',
      easing: 'ease'
    },

    effects: options.effects || {},

    // Metadata
    metadata: {
      version: '3.0.0',
      created: new Date().toISOString(),
      validation: validation
    }
  };
};

/**
 * Default status colors (can be overridden per theme)
 * These are sensible defaults that work in most themes
 */
export const defaultStatusColors = {
  success: {
    bg: '#F0FDF4',    // green-50
    text: '#15803D',  // green-700
    border: '#86EFAC' // green-300
  },
  warning: {
    bg: '#FEF3C7',    // yellow-50
    text: '#A16207',  // yellow-700
    border: '#FDE047' // yellow-300
  },
  error: {
    bg: '#FEF2F2',    // red-50
    text: '#B91C1C',  // red-700
    border: '#FCA5A5' // red-300
  },
  info: {
    bg: '#F0F9FF',    // blue-50
    text: '#075985',  // blue-700
    border: '#7DD3FC' // blue-300
  }
};

export default createTheme;
