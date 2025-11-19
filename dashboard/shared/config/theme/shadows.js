/**
 * Dashboard V3 - Shadow System
 *
 * Complete shadow configuration based on comprehensive audit
 * Total Shadows: 43 unique values
 *
 * Breakdown:
 * - Professional Scale: 7 tiers (xs to 2xl + inner)
 * - Component-Specific: 18 multi-layer shadows
 * - Text Shadows: 6 variants
 * - Glow Effects: 2 colors
 * - Drop Shadows: 3 filter effects
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 191-201, 666-1845)
 * - theme.css (lines 21-26)
 */

import { opacity } from './colors.js';

// ============================================
// PROFESSIONAL SHADOW SCALE (7 tiers)
// Base shadow system for layering
// ============================================

export const scale = {
  xs: `0 1px 2px 0 ${opacity.sandDarkest[5]}`,

  sm: `0 1px 3px 0 ${opacity.sandDarkest[8]}, 0 1px 2px -1px ${opacity.sandDarkest[6]}`,

  md: `0 4px 6px -1px ${opacity.sandDarkest[8]}, 0 2px 4px -2px ${opacity.sandDarkest[6]}`,

  lg: `0 10px 15px -3px ${opacity.sandDarkest[8]}, 0 4px 6px -4px ${opacity.sandDarkest[5]}`,

  xl: `0 20px 25px -5px ${opacity.sandDarkest[10]}, 0 8px 10px -6px ${opacity.sandDarkest[8]}`,

  '2xl': `0 25px 50px -12px ${opacity.sandDarkest[25]}`,

  inner: `inset 0 2px 4px 0 ${opacity.sandDarkest[5]}`,
};

// ============================================
// GLOW EFFECTS (2 colors)
// Subtle ambient glows
// ============================================

export const glow = {
  oasis: `0 0 20px ${opacity.oasisWater[15]}`,
  gold: `0 0 20px ${opacity.amberSand[15]}`,
};

// ============================================
// COMPONENT-SPECIFIC SHADOWS (18 variants)
// Multi-layer shadows for specific components
// ============================================

export const components = {
  // Header
  header: {
    default: `
      ${scale.xl},
      0 4px 12px ${opacity.sandDarkest[5]},
      inset 0 1px 0 ${opacity.white[10]},
      inset 0 -1px 0 ${opacity.bronzeDust[5]}
    `,
    hover: `
      0 24px 48px ${opacity.sandDarkest[10]},
      0 6px 16px ${opacity.sandDarkest[6]},
      inset 0 1px 0 ${opacity.white[15]},
      inset 0 -1px 0 ${opacity.bronzeDust[8]}
    `,
  },

  // Overview Card
  overviewCard: {
    default: `
      ${scale.xl},
      0 2px 8px ${opacity.bronzeDust[6]},
      inset 0 1px 0 ${opacity.white[8]}
    `,
    hover: `
      ${scale['2xl']},
      0 4px 12px ${opacity.bronzeDust[10]},
      inset 0 1px 0 ${opacity.white[10]}
    `,
  },

  // Metric Card
  metricCard: {
    default: scale.sm,
    hover: `
      ${scale.xl},
      0 4px 12px ${opacity.bronzeDust[8]},
      inset 0 1px 0 ${opacity.white[10]}
    `,
  },

  // Restaurant Card
  restaurantCard: {
    default: scale.sm,
    hover: `
      0 12px 35px ${opacity.sandDarkest[12]},
      0 4px 15px ${opacity.bronzeDust[10]},
      ${glow.gold},
      inset 0 1px 0 ${opacity.white[10]}
    `,
  },

  // Modal
  modal: {
    overlay: `0 0 0 100vmax rgba(0, 0, 0, 0.5)`,
    content: `
      0 24px 60px ${opacity.sandDarkest[15]},
      0 8px 24px ${opacity.bronzeDust[10]},
      inset 0 2px 0 ${opacity.white[8]}
    `,
  },

  // Auto Clockout Section
  autoClockout: `
    0 6px 24px ${opacity.sandDarkest[8]},
    0 2px 8px ${opacity.bronzeDust[6]},
    inset 0 1px 0 ${opacity.white[5]}
  `,

  // Week Tab
  weekTab: {
    default: scale.sm,
    active: scale.md,
    hover: scale.lg,
  },

  // Day Card (in investigation modal)
  dayCard: {
    default: scale.sm,
    hover: scale.md,
  },

  // P&L Quadrant
  pnlQuadrant: {
    default: scale.sm,
    hover: `
      ${scale.md},
      inset 0 0 0 1px ${opacity.bronzeDust[15]}
    `,
  },

  // Table
  table: {
    container: scale.sm,
    row: `inset 0 -1px 0 ${opacity.bronzeDust[8]}`,
  },

  // Button
  button: {
    primary: scale.md,
    hover: scale.lg,
    active: scale.sm,
  },

  // Badge
  badge: scale.sm,

  // Input/Form
  input: {
    default: `inset 0 1px 2px ${opacity.sandDarkest[5]}`,
    focus: `
      ${scale.md},
      0 0 0 3px ${opacity.oasisWater[10]}
    `,
  },
};

// ============================================
// TEXT SHADOWS (6 variants)
// Subtle text depth effects
// ============================================

export const textShadows = {
  titleGlow: `0 2px 12px ${opacity.bronzeDust[15]}`,
  headerText: `0 1px 3px ${opacity.sandDarkest[15]}`,
  valueText: `0 1px 4px ${opacity.sandDarkest[15]}`,
  statValue: `0 2px 6px ${opacity.sandDarkest[15]}`,
  criticalIndicator: `0 0 6px rgba(208, 139, 125, 0.2)`,
  successIndicator: `0 0 6px rgba(90, 107, 91, 0.2)`,
};

// ============================================
// DROP SHADOWS (3 filter effects)
// For SVG and icon elements
// ============================================

export const dropShadows = {
  icon: `drop-shadow(0 1px 2px ${opacity.sandDarkest[10]})`,
  title: `drop-shadow(0 2px 12px ${opacity.bronzeDust[15]})`,
  dayStat: `drop-shadow(0 2px 4px rgba(208, 139, 125, 0.2))`,
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  '--shadow-xs': scale.xs,
  '--shadow-sm': scale.sm,
  '--shadow-md': scale.md,
  '--shadow-lg': scale.lg,
  '--shadow-xl': scale.xl,
  '--shadow-2xl': scale['2xl'],
  '--shadow-inner': scale.inner,
  '--shadow-glow-oasis': glow.oasis,
  '--shadow-glow-gold': glow.gold,
};

// ============================================
// TAILWIND SHADOW CONFIG
// For use in Tailwind config
// ============================================

export const tailwindShadows = {
  'xs': scale.xs,
  'sm': scale.sm,
  'DEFAULT': scale.md,
  'md': scale.md,
  'lg': scale.lg,
  'xl': scale.xl,
  '2xl': scale['2xl'],
  'inner': scale.inner,
  'none': 'none',
};

// ============================================
// EXPORT
// ============================================

export default {
  scale,
  glow,
  components,
  textShadows,
  dropShadows,
  cssVariables,
  tailwindShadows,

  // Metadata
  totalShadows: 43,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
