/**
 * Dashboard V3 - Desert Oasis Theme
 *
 * Dubai-inspired warm, luxurious theme with semantic color roles
 * Migrated from aesthetic naming to semantic role-based naming
 */

import { createTheme } from '../themeTemplate.js';

export const desertTheme = createTheme('Desert Oasis', {
  // ============================================
  // TEXT HIERARCHY
  // ============================================
  text_primary: '#3D3128',        // sandDarkest - Main content, headers
  text_secondary: '#594A3C',      // duneShadow - Subheadings, descriptions
  text_muted: '#6E5D4B',          // camelLeather - Labels, metadata
  text_disabled: '#A0938B',       // New - Inactive elements

  // ============================================
  // BACKGROUNDS
  // ============================================
  background_primary: '#FAF6F0',   // pearlSand - Main page background
  background_card: '#FFFFFF',      // Clean white - Card backgrounds
  background_elevated: '#F5EDE2',  // warmPearl - Modals, dropdowns
  background_hover: '#FEF9F3',     // Subtle hover state

  // ============================================
  // BORDERS
  // ============================================
  border_strong: '#B89968',        // bronzeDust - Major section dividers
  border_default: '#E5DDD0',       // Softer border for cards
  border_subtle: '#F0E8DC',        // Light separators

  // ============================================
  // ACCENTS
  // ============================================
  accent_primary: '#B89968',       // bronzeDust - Main brand color
  accent_secondary: '#D4A574',     // amberSand - Supporting accent
  accent_interactive: '#6B8E9B',   // oasisWater - Links, clickable elements

  // ============================================
  // DASHBOARD-SPECIFIC
  // ============================================
  dashboard_metric: '#3D3128',           // sandDarkest - Metric values
  dashboard_metricLabel: '#6E5D4B',      // camelLeather - Metric labels
  dashboard_sectionHeader: '#3D3128',    // sandDarkest - Section headers
  dashboard_tableHeader: '#594A3C',      // duneShadow - Table headers
  dashboard_tableRow: '#FAFAFA',         // Alternating row color
  dashboard_gradientStart: '#B89968',    // bronzeDust - Gradient start
  dashboard_gradientEnd: '#D4A574',      // amberSand - Gradient end

  // ============================================
  // STATUS COLORS
  // ============================================
  status: {
    success: {
      bg: '#F0FDF4',      // green-50
      text: '#15803D',    // green-700
      border: '#16A34A',  // green-600
    },
    warning: {
      bg: '#FEFCE8',      // yellow-50
      text: '#A16207',    // yellow-700
      border: '#CA8A04',  // yellow-600
    },
    error: {
      bg: '#FEF2F2',      // red-50
      text: '#991B1B',    // red-700
      border: '#DC2626',  // red-600
    },
    critical: {
      bg: '#FEF2F2',      // red-50
      text: '#991B1B',    // red-700
      border: '#DC2626',  // red-600
    },
    info: {
      bg: '#EFF6FF',      // blue-50
      text: '#1D4ED8',    // blue-700
      border: '#3B82F6',  // blue-500
    },
    normal: {
      bg: '#F9FAFB',      // gray-50
      text: '#374151',    // gray-700
      border: '#D1D5DB',  // gray-300
    }
  }
}, {
  // ============================================
  // TYPOGRAPHY OPTIONS
  // ============================================
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    scale: 1.0
  },

  // ============================================
  // ANIMATION OPTIONS
  // ============================================
  animations: {
    duration: 'normal',
    easing: 'ease'
  },

  // ============================================
  // EFFECTS OPTIONS
  // ============================================
  effects: {
    shadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    shadowElevated: '0 10px 15px rgba(0, 0, 0, 0.1)',
    borderRadius: '0.5rem'
  }
});

export default desertTheme;
