/**
 * Dashboard V3 - Container System
 *
 * Complete container configuration based on comprehensive audit
 * Total Container Configurations: 5
 *
 * Breakdown:
 * - Max Width Definitions: 5 breakpoints
 * - Padding Configurations: 3 responsive scales
 * - Margin Utilities: 2 centering patterns
 *
 * Source Files Analyzed:
 * - index.html (line 33: max-width: 1600px)
 * - dashboard_generator.py (container patterns)
 * - theme.css (container utilities)
 */

import { conflicts } from '../resolution.js';
import { scale, padding } from '../theme/spacing.js';

// ============================================
// CONTAINER MAX WIDTHS (5 breakpoints)
// ============================================

export const maxWidths = {
  // Primary dashboard container (RESOLVED conflict)
  dashboard: conflicts.containerMaxWidth,  // '1600px' (not 1280px)

  // Alternative container sizes
  sm: '640px',      // Small container
  md: '768px',      // Medium container
  lg: '1024px',     // Large container
  xl: '1280px',     // Extra large container
  '2xl': '1536px',  // 2X large container
  full: '100%',     // Full width
};

// ============================================
// CONTAINER PADDING (3 responsive scales)
// ============================================

export const containerPadding = {
  // Default padding for all containers
  default: {
    mobile: padding.px4,      // 16px
    tablet: padding.px6,      // 24px
    desktop: padding.px8,     // 32px
  },

  // Tight padding (for compact layouts)
  tight: {
    mobile: padding.px2,      // 8px
    tablet: padding.px3,      // 12px
    desktop: padding.px4,     // 16px
  },

  // Loose padding (for spacious layouts)
  loose: {
    mobile: padding.px6,      // 24px
    tablet: padding.px8,      // 32px
    desktop: '3rem',          // 48px
  },

  // CSS values
  css: {
    default: {
      mobile: '1rem',
      tablet: '1.5rem',
      desktop: '2rem',
    },
    tight: {
      mobile: '0.5rem',
      tablet: '0.75rem',
      desktop: '1rem',
    },
    loose: {
      mobile: '1.5rem',
      tablet: '2rem',
      desktop: '3rem',
    },
  },
};

// ============================================
// CONTAINER VARIANTS (5 pre-configured)
// ============================================

export const variants = {
  // Main dashboard container
  dashboard: {
    maxWidth: maxWidths.dashboard,
    padding: containerPadding.default,
    margin: '0 auto',
    class: 'max-w-[1600px] mx-auto px-4 md:px-6 lg:px-8',
    css: {
      maxWidth: '1600px',
      margin: '0 auto',
      paddingLeft: '1rem',
      paddingRight: '1rem',
      '@media (min-width: 768px)': {
        paddingLeft: '1.5rem',
        paddingRight: '1.5rem',
      },
      '@media (min-width: 1024px)': {
        paddingLeft: '2rem',
        paddingRight: '2rem',
      },
    },
  },

  // Modal container
  modal: {
    maxWidth: maxWidths.lg,
    padding: '0',
    margin: '0 auto',
    class: 'max-w-4xl mx-auto',
    css: {
      maxWidth: '1024px',
      margin: '0 auto',
    },
  },

  // Card container (no max-width, inherits from parent)
  card: {
    maxWidth: 'none',
    padding: containerPadding.default,
    class: 'px-4 md:px-6 lg:px-8',
    css: {
      paddingLeft: '1rem',
      paddingRight: '1rem',
      '@media (min-width: 768px)': {
        paddingLeft: '1.5rem',
        paddingRight: '1.5rem',
      },
      '@media (min-width: 1024px)': {
        paddingLeft: '2rem',
        paddingRight: '2rem',
      },
    },
  },

  // Section container (tight padding)
  section: {
    maxWidth: maxWidths.dashboard,
    padding: containerPadding.tight,
    margin: '0 auto',
    class: 'max-w-[1600px] mx-auto px-2 md:px-3 lg:px-4',
    css: {
      maxWidth: '1600px',
      margin: '0 auto',
      paddingLeft: '0.5rem',
      paddingRight: '0.5rem',
      '@media (min-width: 768px)': {
        paddingLeft: '0.75rem',
        paddingRight: '0.75rem',
      },
      '@media (min-width: 1024px)': {
        paddingLeft: '1rem',
        paddingRight: '1rem',
      },
    },
  },

  // Full-width container (for backgrounds)
  fullWidth: {
    maxWidth: maxWidths.full,
    padding: '0',
    margin: '0',
    class: 'w-full',
    css: {
      width: '100%',
    },
  },
};

// ============================================
// MARGIN UTILITIES
// ============================================

export const margins = {
  // Centering
  auto: 'mx-auto',
  center: {
    horizontal: 'mx-auto',
    vertical: 'my-auto',
    both: 'm-auto',
  },

  // Vertical spacing
  vertical: {
    tight: 'my-2',     // 8px
    default: 'my-4',   // 16px
    loose: 'my-8',     // 32px
  },
};

// ============================================
// TAILWIND CONTAINER CONFIG
// ============================================

export const tailwindContainer = {
  center: true,
  padding: {
    DEFAULT: '1rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '2rem',
    '2xl': '2rem',
  },
  screens: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1600px',  // RESOLVED: Using correct max-width
  },
};

// ============================================
// UTILITY CLASSES
// Pre-configured container combinations
// ============================================

export const containerClasses = {
  dashboard: 'max-w-[1600px] mx-auto px-4 md:px-6 lg:px-8',
  modal: 'max-w-4xl mx-auto',
  card: 'px-4 md:px-6 lg:px-8',
  section: 'max-w-[1600px] mx-auto px-2 md:px-3 lg:px-4',
  fullWidth: 'w-full',
  centered: 'mx-auto',
  verticalSpaced: 'my-4',
};

// ============================================
// EXPORT
// ============================================

export default {
  maxWidths,
  containerPadding,
  variants,
  margins,
  tailwindContainer,
  containerClasses,

  // Metadata
  totalConfigs: 5,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
  resolvedMaxWidth: conflicts.containerMaxWidth,
};
