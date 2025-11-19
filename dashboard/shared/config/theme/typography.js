/**
 * Dashboard V3 - Typography System
 *
 * Complete typography configuration based on comprehensive audit
 * Total Configurations: 67
 *
 * Breakdown:
 * - Font Families: 3
 * - Font Sizes: 28 (14 scale + 14 component-specific)
 * - Font Weights: 5
 * - Line Heights: 4
 * - Letter Spacing: 6
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 133, 217-246)
 * - theme.css
 * - desert.js (lines 387-389)
 */

import { conflicts } from '../resolution.js';

// ============================================
// FONT FAMILIES (3 fonts)
// ============================================

export const families = {
  primary: "'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",
  secondary: "'Crimson Text', serif",
  fallback: "'Inter', sans-serif",
  mono: "'Monaco', 'Courier New', monospace",
};

// Google Fonts Import URL
export const googleFontsUrl = 'https://fonts.googleapis.com/css2?family=Crimson+Text:wght@300;400;600&family=Source+Sans+3:wght@300;400;500;600;700&display=swap';

// ============================================
// FONT SIZE SCALE (14 base sizes in rem)
// ============================================

export const sizes = {
  xs: '0.75rem',      // 12px - Labels, tiny text
  sm: '0.875rem',     // 14px - Body small, secondary
  base: '1rem',       // 16px - Body text
  lg: '1.125rem',     // 18px - Emphasized text
  xl: '1.25rem',      // 20px - Small headings
  '2xl': '1.5rem',    // 24px - Metric values
  '3xl': '1.875rem',  // 30px - Section titles
  '4xl': '2.25rem',   // 36px - Large values
  '5xl': '3rem',      // 48px - Hero text
  '6xl': '3.75rem',   // 60px - Extra large
  '7xl': '4.5rem',    // 72px - Massive
  '8xl': '6rem',      // 96px - Display
  '9xl': '8rem',      // 128px - Huge
};

// ============================================
// COMPONENT-SPECIFIC SIZES (14 px values)
// Converted to rem for accessibility
// ============================================

export const componentSizes = {
  headerH1: '2.875rem',         // 46px
  restaurantName: '1.4375rem',   // 23px
  restaurantSales: '1.875rem',   // 30px
  metricValue: '2.375rem',       // 38px
  restMetricValue: '1.5rem',     // 24px
  modalTitle: '2.125rem',        // 34px
  autoClockoutTitle: '1.875rem', // 30px
  autoClockoutValue: '2.625rem', // 42px
  pnlValue: '2.5rem',            // 40px
  daySales: '1.5rem',            // 24px
  dayCardWidth: '18rem',         // 288px
  tableHeaderText: '0.875rem',   // 14px
  buttonText: '0.9375rem',       // 15px
  badgeText: '0.875rem',         // 14px
};

// Mobile overrides (responsive)
export const mobileSizes = {
  '@768px': {
    headerH1: '1.75rem',        // 28px
    metricValue: '1.75rem',     // 28px
    restaurantSales: '1.5rem',  // 24px
    pnlValue: '2.5rem',         // 40px
  },
  '@414px': {
    headerH1: '1.5rem',         // 24px
    metricValue: '1.5rem',      // 24px
    restaurantSales: '1.25rem', // 20px
    dayCardWidth: '7.5rem',     // 120px
  },
  '@768-1024px': {
    daySales: '1.5rem',         // 24px
  },
};

// ============================================
// FONT WEIGHTS (5 weights)
// ============================================

export const weights = {
  light: 300,      // Large numbers, elegant text
  normal: 400,     // Body text, titles
  medium: 500,     // Emphasized text
  semibold: 600,   // Labels, headings
  bold: 700,       // Important headings
};

// ============================================
// LINE HEIGHTS (4 scales)
// ============================================

export const lineHeights = {
  tight: 1.25,     // Headlines, compact text
  normal: 1.5,     // Body text
  relaxed: 1.625,  // Readable paragraphs
  loose: 2,        // Spaced content
};

// ============================================
// LETTER SPACING (6 values)
// ============================================

export const letterSpacing = {
  tighter: '-0.05em',   // Tight headlines
  tight: '-0.025em',    // Compact text
  normal: '0em',        // Standard
  wide: '0.025em',      // Slight spread
  wider: '0.05em',      // More spread
  widest: '0.1em',      // Labels, uppercase
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  // Families
  '--font-primary': families.primary,
  '--font-secondary': families.secondary,
  '--font-fallback': families.fallback,

  // Sizes
  '--text-xs': sizes.xs,
  '--text-sm': sizes.sm,
  '--text-base': sizes.base,
  '--text-lg': sizes.lg,
  '--text-xl': sizes.xl,
  '--text-2xl': sizes['2xl'],
  '--text-3xl': sizes['3xl'],
  '--text-4xl': sizes['4xl'],
  '--text-5xl': sizes['5xl'],

  // Weights
  '--font-light': weights.light,
  '--font-normal': weights.normal,
  '--font-medium': weights.medium,
  '--font-semibold': weights.semibold,
  '--font-bold': weights.bold,

  // Line Heights
  '--leading-tight': lineHeights.tight,
  '--leading-normal': lineHeights.normal,
  '--leading-relaxed': lineHeights.relaxed,
  '--leading-loose': lineHeights.loose,

  // Letter Spacing
  '--tracking-tighter': letterSpacing.tighter,
  '--tracking-tight': letterSpacing.tight,
  '--tracking-normal': letterSpacing.normal,
  '--tracking-wide': letterSpacing.wide,
  '--tracking-wider': letterSpacing.wider,
  '--tracking-widest': letterSpacing.widest,
};

// ============================================
// TAILWIND TYPOGRAPHY CONFIG
// ============================================

export const tailwindTypography = {
  fontFamily: {
    primary: families.primary.split(',').map(f => f.trim().replace(/['"]/g, '')),
    secondary: families.secondary.split(',').map(f => f.trim().replace(/['"]/g, '')),
    sans: families.primary.split(',').map(f => f.trim().replace(/['"]/g, '')),
    serif: families.secondary.split(',').map(f => f.trim().replace(/['"]/g, '')),
    mono: families.mono.split(',').map(f => f.trim().replace(/['"]/g, '')),
  },
  fontSize: sizes,
  fontWeight: weights,
  lineHeight: lineHeights,
  letterSpacing,
};

// ============================================
// UTILITY CLASSES
// Pre-configured text combinations
// ============================================

export const textClasses = {
  // Headers
  h1: `font-semibold text-4xl leading-tight tracking-tight`,
  h2: `font-semibold text-3xl leading-tight tracking-tight`,
  h3: `font-semibold text-2xl leading-tight`,
  h4: `font-medium text-xl leading-normal`,
  h5: `font-medium text-lg leading-normal`,
  h6: `font-medium text-base leading-normal`,

  // Body
  bodyLarge: `font-normal text-lg leading-relaxed`,
  body: `font-normal text-base leading-normal`,
  bodySmall: `font-normal text-sm leading-normal`,

  // Labels
  label: `font-semibold text-xs uppercase tracking-widest`,
  labelLarge: `font-semibold text-sm uppercase tracking-wider`,

  // Values/Numbers
  valueLarge: `font-bold text-4xl leading-tight`,
  value: `font-bold text-2xl leading-tight`,
  valueSmall: `font-semibold text-xl leading-tight`,

  // Special
  caption: `font-normal text-xs leading-normal tracking-wide`,
  overline: `font-medium text-xs uppercase tracking-widest`,
};

// ============================================
// EXPORT
// ============================================

export default {
  families,
  googleFontsUrl,
  sizes,
  componentSizes,
  mobileSizes,
  weights,
  lineHeights,
  letterSpacing,
  cssVariables,
  tailwindTypography,
  textClasses,

  // Metadata
  totalConfigs: 67,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
  preferredUnit: conflicts.preferredUnit, // 'rem'
};
