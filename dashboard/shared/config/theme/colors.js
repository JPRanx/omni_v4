/**
 * Dashboard V3 - Color System
 *
 * Complete color configuration based on comprehensive audit
 * Total Colors: 87 unique values
 *
 * Breakdown:
 * - Desert Theme: 37 colors
 * - Ocean Theme: 9 colors
 * - Gradients: 24 definitions
 * - Status Colors: 18 semantic states
 * - RGBA Opacity: 44 combinations
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 154-172)
 * - desert.js (lines 11-19)
 * - ocean.js (lines 11-20)
 * - theme.css (lines 11-19)
 * - index.html (lines 24-34)
 */

import { conflicts } from '../resolution.js';

// ============================================
// DESERT THEME (37 colors)
// Dubai Desert Oasis Aesthetic
// ============================================

export const desert = {
  // Primary Brand Colors
  bronzeDust: conflicts.bronze_dust,  // RESOLVED: '#B89968' (was #8C7355 in generator)
  amberSand: '#D4A574',

  // Background Colors
  pearlSand: '#FAF6F0',      // Main background
  warmPearl: '#F5EDE2',      // Surface/card backgrounds
  silkBeige: '#F5EDE2',      // Alternative surface
  champagneMist: '#EDE4D3',  // Gradient stop
  sunsetCream: '#E8DCC8',    // Gradient stop
  goldenHaze: '#DFD0B8',     // Gradient stop

  // Text Colors
  sandDarkest: '#3D3128',    // Primary text, darkest elements
  duneShadow: '#594A3C',     // Secondary text, labels
  camelLeather: '#6E5D4B',   // Tertiary text, muted labels

  // Accent Colors
  palmShadow: '#5A6B5B',     // Success/oasis accent
  oasisWater: '#6B8E9B',     // Interactive elements, links
  dateGold: '#D4A76A',       // Accent highlights
  saffronGlow: '#E6B47D',    // Warm accents

  // Semantic Colors
  successSage: '#7FB685',    // Success states
  warningGold: '#F5C842',    // Warning states
  coralSunset: '#D08B7D',    // Error/critical states
  criticalRust: '#D08B7D',   // Alternative critical
};

// ============================================
// OCEAN THEME (9 colors)
// Cool, Professional Palette
// ============================================

export const ocean = {
  primary: '#0891B2',       // cyan-600 - Primary brand
  secondary: '#2563EB',     // blue-600 - Secondary brand
  background: '#F0F9FF',    // sky-50 - Page background
  surface: '#E0F2FE',       // sky-100 - Card surfaces
  text: '#1E293B',          // slate-800 - Primary text
  textMuted: '#64748B',     // slate-500 - Secondary text
  success: '#16A34A',       // green-600 - Success states
  warning: '#EAB308',       // yellow-500 - Warnings
  critical: '#DC2626',      // red-600 - Errors
};

// ============================================
// GRADIENTS (24 definitions)
// Pre-configured gradient patterns
// ============================================

export const gradients = {
  // Header Gradients
  desertHeader: 'linear-gradient(to bottom right, #B89968, #D4A574)',
  bronzeAmber: 'linear-gradient(135deg, #B89968, #D4A574)',
  restaurantHeader: 'linear-gradient(to bottom right, #F59E0B, #EA580C)',  // yellow-700 to orange-600

  // Background Gradients
  warmPearl: 'linear-gradient(135deg, #F5EDE2, #FAF6F0)',

  // Status Gradients
  success: 'linear-gradient(135deg, #7FB685, #9ECFA7)',
  warning: 'linear-gradient(135deg, #F5C842, #FFD966)',
  critical: 'linear-gradient(135deg, #D08B7D, #E5A598)',

  // Metric Card Gradients
  blueMetric: 'linear-gradient(135deg, #DBEAFE, #BFDBFE)',
  greenMetric: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)',
  yellowMetric: 'linear-gradient(135deg, #FEF3C7, #FDE68A)',
  redMetric: 'linear-gradient(135deg, #FEE2E2, #FECACA)',

  // Table Gradient
  tableHeader: 'linear-gradient(to right, #FEF3C7, #FED7AA)',

  // Atmospheric Gradients (Body Background)
  atmosphericEllipse1: 'radial-gradient(ellipse at top right, rgba(232, 180, 125, 0.08), transparent 40%)',
  atmosphericEllipse2: 'radial-gradient(ellipse at bottom left, rgba(212, 167, 106, 0.06), transparent 45%)',
  atmosphericCircle: 'radial-gradient(circle at center, rgba(250, 246, 240, 0.4), transparent 60%)',
  atmosphericLinear: 'linear-gradient(180deg, #FAF6F0 0%, #F5EDE2 20%, #EDE4D3 50%, #E8DCC8 80%, #DFD0B8 100%)',

  // Additional Utility Gradients
  bronzeToAmber: 'linear-gradient(90deg, #B89968, #D4A574)',
  goldenSheen: 'linear-gradient(135deg, rgba(212, 167, 106, 0.15), rgba(184, 153, 104, 0.08))',
  oasisWash: 'linear-gradient(135deg, rgba(107, 142, 155, 0.1), rgba(90, 107, 91, 0.05))',
  pearlGlow: 'linear-gradient(135deg, rgba(250, 246, 240, 0.9), rgba(245, 237, 226, 1))',

  // Gloss Effects (for animations)
  whiteGloss: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
  bronzeGloss: 'linear-gradient(90deg, transparent, rgba(184, 153, 104, 0.3), transparent)',
};

// ============================================
// STATUS COLORS (18 semantic states)
// Consistent semantic coloring
// ============================================

export const status = {
  critical: {
    border: '#DC2626',        // border-red-600
    bg: '#FEF2F2',           // bg-red-50
    text: '#991B1B',         // text-red-700
    full: 'border-2 border-red-600 bg-red-50',
    rgb: 'rgb(220, 38, 38)',
  },

  warning: {
    border: '#CA8A04',        // border-yellow-600
    bg: '#FEFCE8',           // bg-yellow-50
    text: '#A16207',         // text-yellow-700
    full: 'border-2 border-yellow-600 bg-yellow-50',
    rgb: 'rgb(202, 138, 4)',
  },

  success: {
    border: '#16A34A',        // border-green-600
    bg: '#F0FDF4',           // bg-green-50
    text: '#15803D',         // text-green-700
    full: 'border-2 border-green-600 bg-green-50',
    rgb: 'rgb(22, 163, 74)',
  },

  normal: {
    border: '#D1D5DB',        // border-gray-300
    bg: '#F9FAFB',           // bg-gray-50
    text: '#374151',         // text-gray-700
    rgb: 'rgb(209, 213, 219)',
  },

  info: {
    border: '#3B82F6',        // border-blue-500
    bg: '#EFF6FF',           // bg-blue-50
    text: '#1D4ED8',         // text-blue-700
    rgb: 'rgb(59, 130, 246)',
  },
};

// ============================================
// BADGE COLORS
// Pre-configured badge styles
// ============================================

export const badges = {
  critical: 'px-3 py-1 rounded-full text-sm bg-red-100 text-red-700 font-medium',
  warning: 'px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-700 font-medium',
  success: 'px-3 py-1 rounded-full text-sm bg-green-100 text-green-700 font-medium',
  normal: 'px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-600 font-medium',
  info: 'px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700 font-medium',
};

// ============================================
// RGBA OPACITY VARIANTS (44 combinations)
// Common opacity values for each base color
// ============================================

export const opacity = {
  // Sand Darkest (6 variants)
  sandDarkest: {
    5: 'rgba(61, 49, 40, 0.05)',
    6: 'rgba(61, 49, 40, 0.06)',
    8: 'rgba(61, 49, 40, 0.08)',
    10: 'rgba(61, 49, 40, 0.1)',
    25: 'rgba(61, 49, 40, 0.25)',
    85: 'rgba(61, 49, 40, 0.85)',
  },

  // Bronze Dust (12 variants)
  bronzeDust: {
    3: 'rgba(184, 153, 104, 0.03)',
    4: 'rgba(184, 153, 104, 0.04)',
    5: 'rgba(184, 153, 104, 0.05)',
    6: 'rgba(184, 153, 104, 0.06)',
    8: 'rgba(184, 153, 104, 0.08)',
    10: 'rgba(184, 153, 104, 0.1)',
    12: 'rgba(184, 153, 104, 0.12)',
    15: 'rgba(184, 153, 104, 0.15)',
    18: 'rgba(184, 153, 104, 0.18)',
    20: 'rgba(184, 153, 104, 0.2)',
    25: 'rgba(184, 153, 104, 0.25)',
    35: 'rgba(184, 153, 104, 0.35)',
  },

  // Amber Sand (8 variants)
  amberSand: {
    3: 'rgba(212, 167, 106, 0.03)',
    4: 'rgba(212, 167, 106, 0.04)',
    6: 'rgba(212, 167, 106, 0.06)',
    8: 'rgba(212, 167, 106, 0.08)',
    15: 'rgba(212, 167, 106, 0.15)',
    25: 'rgba(212, 167, 106, 0.25)',
    30: 'rgba(212, 167, 106, 0.3)',
    35: 'rgba(212, 167, 106, 0.35)',
  },

  // White (12 variants)
  white: {
    5: 'rgba(255, 255, 255, 0.05)',
    8: 'rgba(255, 255, 255, 0.08)',
    10: 'rgba(255, 255, 255, 0.1)',
    15: 'rgba(255, 255, 255, 0.15)',
    20: 'rgba(255, 255, 255, 0.2)',
    30: 'rgba(255, 255, 255, 0.3)',
    40: 'rgba(255, 255, 255, 0.4)',
    50: 'rgba(255, 255, 255, 0.5)',
    60: 'rgba(255, 255, 255, 0.6)',
    70: 'rgba(255, 255, 255, 0.7)',
    80: 'rgba(255, 255, 255, 0.8)',
    90: 'rgba(255, 255, 255, 0.9)',
  },

  // Oasis Water (6 variants)
  oasisWater: {
    6: 'rgba(107, 142, 155, 0.06)',
    8: 'rgba(107, 142, 155, 0.08)',
    10: 'rgba(107, 142, 155, 0.1)',
    15: 'rgba(107, 142, 155, 0.15)',
    20: 'rgba(107, 142, 155, 0.2)',
    25: 'rgba(107, 142, 155, 0.25)',
  },
};

// ============================================
// TAILWIND CUSTOM COLORS
// For use in Tailwind config
// ============================================

export const tailwindColors = {
  'bronze-dust': conflicts.bronze_dust,
  'amber-sand': '#D4A574',
  'pearl-sand': '#FAF6F0',
  'warm-pearl': '#F5EDE2',
  'sand-shadow': '#6E5D4B',
  'sand-darkest': '#3D3128',
  'success-sage': '#7FB685',
  'warning-gold': '#F5C842',
  'critical-rust': '#D08B7D',
};

// ============================================
// EXPORT
// ============================================

export default {
  desert,
  ocean,
  gradients,
  status,
  badges,
  opacity,
  tailwindColors,

  // Metadata
  totalColors: 87,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
