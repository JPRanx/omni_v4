/**
 * Dashboard V3 - Border System
 *
 * Complete border configuration based on comprehensive audit
 * Total Configurations: 31
 *
 * Breakdown:
 * - Border Radius: 4 scales
 * - Border Widths: 8 patterns
 * - Border Colors: 15 contexts
 * - Border Styles: 4 options
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 184-187)
 * - Various component files
 */

import { opacity } from './colors.js';
import { conflicts } from '../resolution.js';

// ============================================
// BORDER RADIUS SCALE (4 scales)
// ============================================

export const radius = {
  xs: '0.5rem',    // 8px - Tiny corners
  sm: '0.75rem',   // 12px - Small elements
  md: '1.125rem',  // 18px - Medium cards
  lg: '1.5rem',    // 24px - Large containers
};

// Tailwind radius classes
export const radiusClasses = {
  sm: 'rounded-sm',
  DEFAULT: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  '3xl': 'rounded-3xl',
  full: 'rounded-full',
};

// ============================================
// BORDER WIDTHS & STYLES (8 patterns)
// ============================================

export const widths = {
  none: '0',
  thin: '1px',
  DEFAULT: '1px',
  medium: '2px',
  thick: '3px',
  accent: '4px',  // For left/right accent lines
};

export const styles = {
  none: 'border-none',
  solid: 'border-solid',
  dashed: 'border-dashed',
  dotted: 'border-dotted',
};

// Common border patterns
export const patterns = {
  default: `1px solid`,              // Standard border
  emphasized: `2px solid`,           // Thicker border
  accentLeft: `border-left: 3px`,   // Left accent
  accentLeftThick: `border-left: 4px solid`,  // Metric card accent
  dividerBottom: `border-bottom: 1px solid`,  // Horizontal divider
  dividerThick: `border-bottom: 2px solid`,   // Thick divider
  separatorTop: `border-top: 2px solid`,      // Footer separator
  tailwind: `border`,                 // Tailwind default (1px all sides)
};

// ============================================
// BORDER COLORS BY COMPONENT (15 contexts)
// Component-specific border opacity
// ============================================

export const colors = {
  // Header
  header: opacity.bronzeDust[15],

  // Week Tabs
  weekTabInactive: opacity.bronzeDust[18],
  weekTabActive: opacity.oasisWater[30],

  // Overview Card
  overviewCard: opacity.bronzeDust[15],

  // Metric Cards
  metricCard: opacity.bronzeDust[12],

  // Restaurant Card
  restaurantCard: opacity.bronzeDust[15],

  // Individual Restaurant Metrics
  restaurantMetric: opacity.bronzeDust[10],

  // Modal
  modal: opacity.bronzeDust[12],

  // P&L Lines
  pnlDividerThin: opacity.bronzeDust[15],
  pnlDividerLight: opacity.bronzeDust[8],

  // Tables
  tableHeader: opacity.bronzeDust[15],
  tableRow: opacity.bronzeDust[8],

  // Auto Clockout
  autoClockout: 'rgba(208, 139, 125, 0.2)',  // Warning tint

  // Status-based (from colors.js status)
  critical: '#DC2626',   // border-red-600
  warning: '#CA8A04',    // border-yellow-600
  success: '#16A34A',    // border-green-600
  normal: '#D1D5DB',     // border-gray-300
};

// ============================================
// COMPONENT BORDER CONFIGS
// Pre-configured border combinations
// ============================================

export const components = {
  // Cards
  card: {
    default: `1px solid ${colors.metricCard}`,
    hover: `1px solid ${opacity.bronzeDust[20]}`,
  },

  // Metric Cards with Left Accent
  metricCard: {
    blue: `border-left: 4px solid #3B82F6`,     // blue-500
    green: `border-left: 4px solid #10B981`,    // green-500
    yellow: `border-left: 4px solid #F59E0B`,   // yellow-500
    red: `border-left: 4px solid #EF4444`,      // red-500
  },

  // Tables
  table: {
    header: `border-bottom: 2px solid ${colors.tableHeader}`,
    row: `border-bottom: 1px solid ${colors.tableRow}`,
  },

  // Modal
  modal: {
    container: `1px solid ${colors.modal}`,
    separator: `border-top: 1px solid ${opacity.bronzeDust[12]}`,
  },

  // Forms
  input: {
    default: `1px solid ${opacity.bronzeDust[15]}`,
    focus: `2px solid ${opacity.oasisWater[25]}`,
    error: `2px solid ${colors.critical}`,
  },

  // Buttons
  button: {
    primary: 'border-transparent',
    secondary: `1px solid ${opacity.bronzeDust[18]}`,
  },
};

// ============================================
// TAILWIND BORDER CLASSES
// Quick reference for common patterns
// ============================================

export const tailwindClasses = {
  // Border sides
  all: 'border',
  top: 'border-t',
  right: 'border-r',
  bottom: 'border-b',
  left: 'border-l',
  x: 'border-x',  // left + right
  y: 'border-y',  // top + bottom

  // Border widths
  0: 'border-0',
  2: 'border-2',
  4: 'border-4',
  8: 'border-8',

  // Common colors
  transparent: 'border-transparent',
  gray200: 'border-gray-200',
  gray300: 'border-gray-300',
  bronze: 'border-[#B89968]',
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  '--radius-xs': radius.xs,
  '--radius-sm': radius.sm,
  '--radius-md': radius.md,
  '--radius-lg': radius.lg,

  '--border-width-thin': widths.thin,
  '--border-width-medium': widths.medium,
  '--border-width-thick': widths.thick,
};

// ============================================
// EXPORT
// ============================================

export default {
  radius,
  radiusClasses,
  widths,
  styles,
  patterns,
  colors,
  components,
  tailwindClasses,
  cssVariables,

  // Metadata
  totalConfigs: 31,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
  opacityPattern: conflicts.borderOpacityPattern, // 'component-based'
};
