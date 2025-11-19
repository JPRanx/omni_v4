/**
 * Dashboard V3 - Grid System
 *
 * Complete grid layout configuration based on comprehensive audit
 * Total Grid Patterns: 14
 *
 * Breakdown:
 * - CSS Grid Definitions: 14 layouts
 * - Responsive Variants: 8 breakpoint adaptations
 * - Gap Configurations: Integrated with spacing system
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 574-933, 1318-1683)
 * - WeekTabs.js
 * - OverviewCard.js
 */

import { components as spacing, gap } from '../theme/spacing.js';

// ============================================
// GRID DEFINITIONS (14 layouts)
// ============================================

export const grids = {
  // Metrics Grid (6 cards, 3 columns)
  metrics: {
    container: 'grid grid-cols-3 gap-[1.375rem] mt-6',
    columns: 3,
    gap: spacing.metricsGridGap,
    marginTop: spacing.metricsGridMarginTop,
    responsive: {
      mobile: 'grid-cols-1',
      tablet: 'grid-cols-2',
      desktop: 'grid-cols-3',
    },
    css: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '1.375rem',
      marginTop: '1.5rem',
    },
  },

  // Restaurant Cards Grid (flexible columns)
  restaurants: {
    container: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[1.625rem] mt-8',
    columns: {
      mobile: 1,
      tablet: 2,
      desktop: 3,
    },
    gap: spacing.restCardGridGap,
    marginTop: spacing.restCardGridMarginTop,
    responsive: {
      mobile: 'grid-cols-1',
      tablet: 'md:grid-cols-2',
      desktop: 'lg:grid-cols-3',
    },
    css: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '1.625rem',
      marginTop: '2rem',
    },
  },

  // P&L Quadrant Grid (2x2)
  pnlQuadrant: {
    container: 'grid grid-cols-2 gap-6',
    columns: 2,
    rows: 2,
    gap: spacing.pnlGridGap,
    marginTop: spacing.pnlGridMarginTop,
    responsive: {
      mobile: 'grid-cols-1',
      desktop: 'grid-cols-2',
    },
    css: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gridTemplateRows: 'repeat(2, 1fr)',
      gap: '1.5rem',
      marginTop: '1.5rem',
    },
  },

  // Restaurant Metrics Grid (inside card, 2 columns)
  restaurantMetrics: {
    container: 'grid grid-cols-2 gap-4',
    columns: 2,
    gap: spacing.restMetricsGap,
    padding: spacing.restMetricsPadding,
    responsive: {
      mobile: 'grid-cols-1',
      desktop: 'grid-cols-2',
    },
    css: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '1rem',
      padding: '1.625rem',
    },
  },

  // Days Grid (horizontal scroll, 7 day cards)
  days: {
    container: 'flex gap-4 overflow-x-auto pb-4',
    display: 'flex',
    direction: 'row',
    wrap: 'nowrap',
    gap: '1rem',
    responsive: {
      mobile: 'flex-nowrap overflow-x-auto',
      tablet: 'flex-wrap',
      desktop: 'grid grid-cols-7',
    },
    css: {
      display: 'flex',
      flexDirection: 'row',
      gap: '1rem',
      overflowX: 'auto',
      paddingBottom: '1rem',
    },
  },

  // Week Tabs Grid (horizontal flex)
  weekTabs: {
    container: 'flex gap-[0.875rem] justify-center flex-wrap',
    display: 'flex',
    direction: 'row',
    justify: 'center',
    wrap: 'wrap',
    gap: spacing.weekTabGap,
    responsive: {
      mobile: 'flex-col',
      tablet: 'flex-row',
    },
    css: {
      display: 'flex',
      flexDirection: 'row',
      justifyContent: 'center',
      flexWrap: 'wrap',
      gap: '0.875rem',
    },
  },

  // Auto Clockout Table Grid
  autoClockoutTable: {
    container: 'w-full',
    display: 'table',
    columns: ['Name', 'Role', 'Hours', 'Actions'],
    columnWidths: ['40%', '25%', '20%', '15%'],
    css: {
      display: 'table',
      width: '100%',
      tableLayout: 'fixed',
    },
  },

  // Investigation Modal Layout (tabs + content)
  investigationModal: {
    container: 'flex flex-col h-full',
    structure: {
      header: 'flex-shrink-0',
      tabs: 'flex-shrink-0',
      content: 'flex-1 overflow-y-auto',
    },
    css: {
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    },
  },

  // Metric Value Layout (icon + number + label)
  metricValue: {
    container: 'flex flex-col items-start',
    structure: {
      icon: 'w-12 h-12 mb-3',
      value: 'text-[2.375rem] font-light leading-none mb-1',
      label: 'text-sm font-semibold uppercase tracking-widest',
    },
    css: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
    },
  },

  // Restaurant Header Layout (name + sales)
  restaurantHeader: {
    container: 'flex justify-between items-center',
    structure: {
      name: 'flex-1',
      sales: 'flex-shrink-0',
    },
    css: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
  },

  // Badge Container (flex wrap)
  badges: {
    container: 'flex gap-2 flex-wrap',
    display: 'flex',
    wrap: 'wrap',
    gap: '0.5rem',
    css: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '0.5rem',
    },
  },

  // Day Card Layout (vertical stack)
  dayCard: {
    container: 'flex flex-col items-center p-4 w-72',
    structure: {
      date: 'text-base font-semibold mb-2',
      sales: 'text-2xl font-light mb-3',
      stats: 'grid grid-cols-2 gap-2 w-full',
    },
    width: spacing.dayCardWidth,
    css: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '1rem',
      width: '18rem',
    },
  },

  // Modal Content Layout
  modalContent: {
    container: 'flex flex-col max-h-[80vh]',
    structure: {
      header: 'px-8 py-7 flex-shrink-0',
      body: 'px-9 py-9 flex-1 overflow-y-auto',
      footer: 'px-8 py-6 flex-shrink-0',
    },
    css: {
      display: 'flex',
      flexDirection: 'column',
      maxHeight: '80vh',
    },
  },

  // Score Bar Layout (horizontal progress bar)
  scoreBar: {
    container: 'relative h-3 rounded-full overflow-hidden',
    structure: {
      background: 'absolute inset-0',
      fill: 'absolute left-0 top-0 bottom-0 transition-all duration-300',
      shine: 'absolute w-full h-full',
    },
    css: {
      position: 'relative',
      height: '0.75rem',
      borderRadius: '9999px',
      overflow: 'hidden',
    },
  },
};

// ============================================
// RESPONSIVE BREAKPOINT OVERRIDES
// ============================================

export const responsive = {
  // Mobile (< 640px)
  mobile: {
    metrics: 'grid-cols-1 gap-4',
    restaurants: 'grid-cols-1 gap-4',
    pnlQuadrant: 'grid-cols-1',
    restaurantMetrics: 'grid-cols-1',
    days: 'flex-nowrap overflow-x-auto',
    weekTabs: 'flex-col items-stretch',
  },

  // Tablet (640px - 1024px)
  tablet: {
    metrics: 'grid-cols-2 gap-5',
    restaurants: 'grid-cols-2 gap-5',
    pnlQuadrant: 'grid-cols-2',
    restaurantMetrics: 'grid-cols-2',
    days: 'flex-wrap justify-center',
    weekTabs: 'flex-row justify-center',
  },

  // Desktop (> 1024px)
  desktop: {
    metrics: 'grid-cols-3 gap-[1.375rem]',
    restaurants: 'grid-cols-3 gap-[1.625rem]',
    pnlQuadrant: 'grid-cols-2',
    restaurantMetrics: 'grid-cols-2',
    days: 'grid grid-cols-7 gap-4',
    weekTabs: 'flex-row justify-center',
  },
};

// ============================================
// TAILWIND GRID UTILITIES
// ============================================

export const tailwindGrids = {
  // Grid Template Columns
  gridTemplateColumns: {
    1: 'repeat(1, minmax(0, 1fr))',
    2: 'repeat(2, minmax(0, 1fr))',
    3: 'repeat(3, minmax(0, 1fr))',
    7: 'repeat(7, minmax(0, 1fr))',
    'auto-fit': 'repeat(auto-fit, minmax(280px, 1fr))',
  },

  // Grid Auto Rows
  gridAutoRows: {
    min: 'min-content',
    max: 'max-content',
    fr: 'minmax(0, 1fr)',
  },

  // Gap Utilities (from spacing system)
  gap: {
    metrics: '1.375rem',
    restaurants: '1.625rem',
    pnl: '1.5rem',
    restMetrics: '1rem',
    days: '1rem',
    weekTabs: '0.875rem',
  },
};

// ============================================
// UTILITY CLASSES
// Pre-configured grid combinations
// ============================================

export const gridClasses = {
  metrics: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[1.375rem] mt-6',
  restaurants: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[1.625rem] mt-8',
  pnlQuadrant: 'grid grid-cols-1 md:grid-cols-2 gap-6 mt-6',
  restaurantMetrics: 'grid grid-cols-1 sm:grid-cols-2 gap-4',
  days: 'flex gap-4 overflow-x-auto md:overflow-visible md:flex-wrap lg:grid lg:grid-cols-7',
  weekTabs: 'flex flex-col sm:flex-row gap-[0.875rem] justify-center flex-wrap',
  badges: 'flex gap-2 flex-wrap',
  dayCard: 'flex flex-col items-center p-4 w-72',
  scoreBar: 'relative h-3 rounded-full overflow-hidden',
};

// ============================================
// EXPORT
// ============================================

export default {
  grids,
  responsive,
  tailwindGrids,
  gridClasses,

  // Metadata
  totalPatterns: 14,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
