/**
 * Dashboard V3 - Spacing System
 *
 * Complete spacing configuration based on comprehensive audit
 * Total Values: 52
 *
 * Breakdown:
 * - CSS Variable Scale: 7 values
 * - Tailwind Padding: 40 classes
 * - Tailwind Margin: 21 classes
 * - Component-Specific: 12 values
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 175-181)
 * - desert.js (lines 332-381)
 * - ocean.js (lines 318-367)
 */

// ============================================
// CSS VARIABLE SCALE (7 base values)
// ============================================

export const scale = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
};

// ============================================
// TAILWIND PADDING CLASSES (40 classes)
// ============================================

export const padding = {
  // All sides
  p0: 'p-0',
  p1: 'p-1',      // 4px
  p2: 'p-2',      // 8px
  p3: 'p-3',      // 12px
  p4: 'p-4',      // 16px
  p5: 'p-5',      // 20px
  p6: 'p-6',      // 24px
  p8: 'p-8',      // 32px

  // Horizontal (left + right)
  px2: 'px-2',    // 8px
  px3: 'px-3',    // 12px
  px4: 'px-4',    // 16px
  px5: 'px-5',    // 20px
  px6: 'px-6',    // 24px

  // Vertical (top + bottom)
  py1: 'py-1',    // 4px
  py2: 'py-2',    // 8px
  py3: 'py-3',    // 12px
  py4: 'py-4',    // 16px
  py6: 'py-6',    // 24px

  // Top
  pt2: 'pt-2',    // 8px
  pt3: 'pt-3',    // 12px
  pt4: 'pt-4',    // 16px

  // Bottom
  pb2: 'pb-2',    // 8px
  pb3: 'pb-3',    // 12px
  pb4: 'pb-4',    // 16px
  pb6: 'pb-6',    // 24px
};

// ============================================
// TAILWIND MARGIN CLASSES (21 classes)
// ============================================

export const margin = {
  // All sides
  m0: 'm-0',
  m1: 'm-1',      // 4px
  m2: 'm-2',      // 8px
  m3: 'm-3',      // 12px
  m4: 'm-4',      // 16px
  m6: 'm-6',      // 24px
  m8: 'm-8',      // 32px

  // Bottom
  mb1: 'mb-1',    // 4px
  mb2: 'mb-2',    // 8px
  mb3: 'mb-3',    // 12px
  mb4: 'mb-4',    // 16px
  mb6: 'mb-6',    // 24px

  // Top
  mt1: 'mt-1',    // 4px
  mt2: 'mt-2',    // 8px
  mt3: 'mt-3',    // 12px
  mt4: 'mt-4',    // 16px
  mt6: 'mt-6',    // 24px

  // Left
  ml2: 'ml-2',    // 8px

  // Horizontal
  mxAuto: 'mx-auto',

  // Vertical
  my6: 'my-6',    // 24px
};

// ============================================
// COMPONENT-SPECIFIC SPACING (12 values)
// Custom spacing for specific components
// ============================================

export const components = {
  // Header
  headerPadding: '2.8125rem',     // 45px
  headerMarginBottom: '2rem',      // 32px

  // Week Tabs
  weekTabPadding: '0.9375rem 1.875rem',  // 15px 30px
  weekTabGap: '0.875rem',          // 14px

  // Overview Card
  overviewPadding: '2.5rem',       // 40px
  overviewMarginBottom: '2rem',    // 32px

  // Metric Card
  metricPadding: '1.625rem',       // 26px
  metricsGridGap: '1.375rem',      // 22px
  metricsGridMarginTop: '1.5rem',  // 24px

  // Restaurant Cards
  restCardGridGap: '1.625rem',     // 26px
  restCardGridMarginTop: '2rem',   // 32px
  restMetricsPadding: '1.625rem',  // 26px
  restMetricsGap: '1rem',          // 16px

  // Auto Clockout
  autoClockoutPadding: '2.375rem', // 38px
  autoClockoutMargin: '2rem 0',    // 32px 0

  // Modal
  modalHeaderPadding: '1.75rem 2rem',  // 28px 32px
  modalBodyPadding: '2.25rem',     // 36px

  // P&L Grid
  pnlGridGap: '1.5rem',            // 24px
  pnlGridMarginTop: '1.5rem',      // 24px

  // Day Card
  dayCardPadding: '1rem',          // 16px
  dayCardWidth: '18rem',           // 288px (w-72)
};

// ============================================
// GAP UTILITIES (for Flexbox/Grid)
// ============================================

export const gap = {
  0: 'gap-0',
  1: 'gap-1',      // 4px
  2: 'gap-2',      // 8px
  3: 'gap-3',      // 12px
  4: 'gap-4',      // 16px
  5: 'gap-5',      // 20px
  6: 'gap-6',      // 24px
  8: 'gap-8',      // 32px
  10: 'gap-10',    // 40px
  12: 'gap-12',    // 48px
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  '--space-xs': scale.xs,
  '--space-sm': scale.sm,
  '--space-md': scale.md,
  '--space-lg': scale.lg,
  '--space-xl': scale.xl,
  '--space-2xl': scale['2xl'],
  '--space-3xl': scale['3xl'],
};

// ============================================
// TAILWIND SPACING CONFIG
// ============================================

export const tailwindSpacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
  24: '6rem',
  32: '8rem',
  40: '10rem',
  48: '12rem',
  56: '14rem',
  64: '16rem',
};

// ============================================
// EXPORT
// ============================================

export default {
  scale,
  padding,
  margin,
  components,
  gap,
  cssVariables,
  tailwindSpacing,

  // Metadata
  totalValues: 52,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
