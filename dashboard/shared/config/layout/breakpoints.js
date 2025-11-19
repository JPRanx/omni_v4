/**
 * Dashboard V3 - Responsive Breakpoints
 *
 * Complete breakpoint configuration based on comprehensive audit
 * Total Breakpoints: 7
 *
 * Breakdown:
 * - Standard Breakpoints: 5 (sm, md, lg, xl, 2xl)
 * - Custom Breakpoints: 2 (iPad range, mobile specific)
 * - Media Query Helpers: 7 query builders
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines with @media queries)
 * - typography.js (mobile size overrides)
 * - All component files (responsive classes)
 */

// ============================================
// BREAKPOINT VALUES (7 breakpoints)
// ============================================

export const breakpoints = {
  // Standard Tailwind breakpoints
  xs: '0px',        // Extra small (mobile first)
  sm: '640px',      // Small devices (landscape phones)
  md: '768px',      // Medium devices (tablets)
  lg: '1024px',     // Large devices (laptops)
  xl: '1280px',     // Extra large devices (desktops)
  '2xl': '1536px',  // 2X large devices (large desktops)

  // Custom breakpoints (from audit)
  mobile: '414px',      // iPhone specific
  tablet: '768px',      // iPad portrait
  desktop: '1024px',    // iPad landscape / Desktop
  ipadMin: '768px',     // iPad range start
  ipadMax: '1024px',    // iPad range end
};

// Numeric values (for JavaScript comparisons)
export const breakpointValues = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
  mobile: 414,
  tablet: 768,
  desktop: 1024,
  ipadMin: 768,
  ipadMax: 1024,
};

// ============================================
// MEDIA QUERY BUILDERS (7 helpers)
// ============================================

export const mediaQueries = {
  // Min-width queries (mobile-first)
  up: (breakpoint) => `@media (min-width: ${breakpoints[breakpoint]})`,

  // Max-width queries (desktop-first)
  down: (breakpoint) => `@media (max-width: ${breakpoints[breakpoint]})`,

  // Range queries (between two breakpoints)
  between: (min, max) => `@media (min-width: ${breakpoints[min]}) and (max-width: ${breakpoints[max]})`,

  // Specific device queries
  mobile: '@media (max-width: 640px)',
  tablet: '@media (min-width: 641px) and (max-width: 1024px)',
  desktop: '@media (min-width: 1025px)',

  // iPad-specific range (from audit)
  ipad: '@media (min-width: 768px) and (max-width: 1024px)',

  // Orientation queries
  landscape: '@media (orientation: landscape)',
  portrait: '@media (orientation: portrait)',

  // High DPI displays
  retina: '@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)',

  // Accessibility
  reducedMotion: '@media (prefers-reduced-motion: reduce)',
  darkMode: '@media (prefers-color-scheme: dark)',
};

// ============================================
// RESPONSIVE PATTERNS (7 common patterns)
// From audit analysis
// ============================================

export const patterns = {
  // Typography scaling
  typography: {
    headerH1: {
      default: '2.875rem',    // 46px
      tablet: '1.75rem',      // 28px (at 768px)
      mobile: '1.5rem',       // 24px (at 414px)
    },
    metricValue: {
      default: '2.375rem',    // 38px
      tablet: '1.75rem',      // 28px (at 768px)
      mobile: '1.5rem',       // 24px (at 414px)
    },
    restaurantSales: {
      default: '1.875rem',    // 30px
      tablet: '1.5rem',       // 24px (at 768px)
      mobile: '1.25rem',      // 20px (at 414px)
    },
  },

  // Layout changes
  layout: {
    metrics: {
      mobile: 'grid-cols-1',
      tablet: 'grid-cols-2',
      desktop: 'grid-cols-3',
    },
    restaurants: {
      mobile: 'grid-cols-1',
      tablet: 'grid-cols-2',
      desktop: 'grid-cols-3',
    },
    pnlQuadrant: {
      mobile: 'grid-cols-1',
      desktop: 'grid-cols-2',
    },
  },

  // Spacing adjustments
  spacing: {
    containerPadding: {
      mobile: '1rem',
      tablet: '1.5rem',
      desktop: '2rem',
    },
    sectionMargin: {
      mobile: '1rem',
      tablet: '1.5rem',
      desktop: '2rem',
    },
  },

  // Visibility toggles
  visibility: {
    mobileOnly: 'block sm:hidden',
    tabletOnly: 'hidden sm:block lg:hidden',
    desktopOnly: 'hidden lg:block',
    hideOnMobile: 'hidden sm:block',
    hideOnDesktop: 'block lg:hidden',
  },

  // Flex direction changes
  flex: {
    weekTabs: {
      mobile: 'flex-col',
      tablet: 'flex-row',
    },
    restaurantHeader: {
      mobile: 'flex-col items-start',
      tablet: 'flex-row items-center',
    },
  },

  // Day card width (from audit)
  dayCard: {
    width: {
      default: '18rem',      // 288px
      mobile: '7.5rem',      // 120px (at 414px)
      tablet: '18rem',       // 288px (768-1024px)
    },
  },

  // Modal sizing
  modal: {
    width: {
      mobile: '95%',
      tablet: '90%',
      desktop: '1024px',
    },
    maxHeight: {
      mobile: '90vh',
      desktop: '80vh',
    },
  },
};

// ============================================
// TAILWIND SCREENS CONFIG
// ============================================

export const tailwindScreens = {
  xs: '0px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// ============================================
// UTILITY CLASSES
// Pre-configured responsive combinations
// ============================================

export const responsiveClasses = {
  // Hide/Show utilities
  mobileOnly: 'block sm:hidden',
  tabletOnly: 'hidden sm:block lg:hidden',
  desktopOnly: 'hidden lg:block',
  hideOnMobile: 'hidden sm:block',
  hideOnTablet: 'block lg:hidden',
  hideOnDesktop: 'block lg:hidden',

  // Container responsive
  container: 'px-4 md:px-6 lg:px-8',

  // Grid responsive
  gridMetrics: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  gridRestaurants: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  gridPnl: 'grid-cols-1 md:grid-cols-2',

  // Flex responsive
  flexWeekTabs: 'flex-col sm:flex-row',
  flexHeader: 'flex-col sm:flex-row items-start sm:items-center',

  // Text size responsive
  textHeaderH1: 'text-[1.5rem] md:text-[1.75rem] lg:text-[2.875rem]',
  textMetricValue: 'text-[1.5rem] md:text-[1.75rem] lg:text-[2.375rem]',
  textRestaurantSales: 'text-[1.25rem] md:text-[1.5rem] lg:text-[1.875rem]',

  // Gap responsive
  gapMetrics: 'gap-4 md:gap-5 lg:gap-[1.375rem]',
  gapRestaurants: 'gap-4 md:gap-5 lg:gap-[1.625rem]',
};

// ============================================
// DEVICE DETECTION HELPERS
// For use in JavaScript
// ============================================

export const deviceHelpers = {
  // Check if viewport is mobile
  isMobile: () => window.innerWidth < breakpointValues.sm,

  // Check if viewport is tablet
  isTablet: () => window.innerWidth >= breakpointValues.sm && window.innerWidth < breakpointValues.lg,

  // Check if viewport is desktop
  isDesktop: () => window.innerWidth >= breakpointValues.lg,

  // Check if viewport is iPad range
  isIPad: () => window.innerWidth >= breakpointValues.ipadMin && window.innerWidth <= breakpointValues.ipadMax,

  // Get current breakpoint
  getCurrentBreakpoint: () => {
    const width = window.innerWidth;
    if (width < breakpointValues.sm) return 'xs';
    if (width < breakpointValues.md) return 'sm';
    if (width < breakpointValues.lg) return 'md';
    if (width < breakpointValues.xl) return 'lg';
    if (width < breakpointValues['2xl']) return 'xl';
    return '2xl';
  },

  // Match media query
  matchMedia: (breakpoint) => {
    return window.matchMedia(`(min-width: ${breakpoints[breakpoint]})`).matches;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  breakpoints,
  breakpointValues,
  mediaQueries,
  patterns,
  tailwindScreens,
  responsiveClasses,
  deviceHelpers,

  // Metadata
  totalBreakpoints: 7,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
