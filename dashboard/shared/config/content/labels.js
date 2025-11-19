/**
 * Dashboard V3 - Text Labels
 *
 * Complete label configuration based on comprehensive audit
 * Total Labels: 73 text strings
 *
 * Breakdown:
 * - Header Labels: 5
 * - Metric Labels: 12
 * - Button Labels: 8
 * - Section Labels: 10
 * - Status Labels: 9
 * - Modal Labels: 12
 * - Table Labels: 8
 * - Misc Labels: 9
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (all text strings)
 * - Component files (button text, labels)
 */

// ============================================
// HEADER LABELS (5 strings)
// ============================================

export const header = {
  mainTitle: 'Restaurant Performance Dashboard',
  subtitle: 'Week',
  dateRange: (startDate, endDate) => `${startDate} - ${endDate}`,
  restaurantCount: (count) => `${count} Restaurants`,
  lastUpdated: (time) => `Last Updated: ${time}`,
};

// ============================================
// METRIC LABELS (12 strings)
// ============================================

export const metrics = {
  // Overview Metrics
  totalSales: 'Total Sales',
  avgDailySales: 'Avg Daily Sales',
  laborCost: 'Labor Cost',
  laborPercent: 'Labor %',
  cogs: 'COGS',
  cogsPercent: 'COGS %',
  netProfit: 'Net Profit',
  profitMargin: 'Profit Margin',

  // Restaurant Metrics
  weeklySales: 'Weekly Sales',
  dailyAverage: 'Daily Average',
  bestDay: 'Best Day',
  worstDay: 'Worst Day',
};

// ============================================
// BUTTON LABELS (8 strings)
// ============================================

export const buttons = {
  viewDetails: 'View Details',
  investigate: 'Investigate',
  close: 'Close',
  export: 'Export',
  filter: 'Filter',
  refresh: 'Refresh',
  apply: 'Apply',
  cancel: 'Cancel',
};

// ============================================
// SECTION LABELS (10 strings)
// ============================================

export const sections = {
  overview: 'Overview',
  metrics: 'Key Metrics',
  restaurants: 'Restaurants',
  profitLoss: 'Profit & Loss',
  autoClockout: 'Auto Clockout',
  investigation: 'Investigation',
  dailyBreakdown: 'Daily Breakdown',
  weeklyTrends: 'Weekly Trends',
  performance: 'Performance',
  analysis: 'Analysis',
};

// ============================================
// STATUS LABELS (9 strings)
// ============================================

export const status = {
  excellent: 'Excellent',
  good: 'Good',
  acceptable: 'Acceptable',
  average: 'Average',
  fair: 'Fair',
  poor: 'Poor',
  warning: 'Warning',
  critical: 'Critical',
  success: 'Success',
};

// ============================================
// MODAL LABELS (12 strings)
// ============================================

export const modal = {
  // Investigation Modal
  investigationTitle: (restaurantName) => `${restaurantName} - Investigation`,
  dailyBreakdownTab: 'Daily Breakdown',
  trendsTab: 'Trends',
  comparisonsTab: 'Comparisons',

  // Auto Clockout Modal
  autoClockoutTitle: 'Auto Clockout Warnings',
  employeeName: 'Employee Name',
  role: 'Role',
  hoursWorked: 'Hours Worked',
  action: 'Action',

  // Confirmation Modal
  confirmTitle: 'Confirm Action',
  confirmMessage: 'Are you sure you want to proceed?',
  confirmButton: 'Confirm',
  cancelButton: 'Cancel',
};

// ============================================
// TABLE LABELS (8 strings)
// ============================================

export const table = {
  // Column Headers
  name: 'Name',
  role: 'Role',
  hours: 'Hours',
  actions: 'Actions',
  date: 'Date',
  sales: 'Sales',
  labor: 'Labor',
  profit: 'Profit',
};

// ============================================
// DAY LABELS (7 strings)
// ============================================

export const days = {
  sunday: 'Sunday',
  monday: 'Monday',
  tuesday: 'Tuesday',
  wednesday: 'Wednesday',
  thursday: 'Thursday',
  friday: 'Friday',
  saturday: 'Saturday',
};

// Short day names
export const daysShort = {
  sun: 'Sun',
  mon: 'Mon',
  tue: 'Tue',
  wed: 'Wed',
  thu: 'Thu',
  fri: 'Fri',
  sat: 'Sat',
};

// ============================================
// GRADE LABELS (5 strings)
// ============================================

export const grades = {
  aPlus: 'A+',
  a: 'A',
  b: 'B',
  c: 'C',
  d: 'D',
  f: 'F',
};

// ============================================
// TOOLTIP LABELS (12 strings)
// ============================================

export const tooltips = {
  // Metrics
  totalSales: 'Total sales for the selected week across all restaurants',
  laborCost: 'Total labor cost including wages, benefits, and overtime',
  laborPercent: 'Labor cost as percentage of total sales (Target: 25-30%)',
  cogs: 'Cost of Goods Sold - raw materials and ingredients',
  cogsPercent: 'COGS as percentage of total sales (Target: ≤30%)',
  netProfit: 'Net profit after all expenses',
  profitMargin: 'Net profit as percentage of total sales',

  // Actions
  investigate: 'View detailed breakdown and daily trends',
  export: 'Export data to CSV or PDF',
  filter: 'Filter restaurants by performance',
  refresh: 'Refresh dashboard data',

  // Auto Clockout
  autoClockout: 'Employees who have worked 10+ hours without clocking out',
};

// ============================================
// BADGE LABELS (6 strings)
// ============================================

export const badges = {
  top: 'Top Performer',
  trending: 'Trending Up',
  attention: 'Needs Attention',
  critical: 'Critical',
  new: 'New',
  improved: 'Improved',
};

// ============================================
// EMPTY STATE LABELS (5 strings)
// ============================================

export const empty = {
  noData: 'No data available',
  noRestaurants: 'No restaurants found',
  noEmployees: 'No employees to display',
  noResults: 'No results found',
  selectWeek: 'Please select a week to view data',
};

// ============================================
// LOADING LABELS (3 strings)
// ============================================

export const loading = {
  default: 'Loading...',
  restaurants: 'Loading restaurants...',
  metrics: 'Loading metrics...',
};

// ============================================
// ERROR LABELS (4 strings)
// ============================================

export const error = {
  generic: 'An error occurred',
  loading: 'Failed to load data',
  network: 'Network connection error',
  retry: 'Please try again',
};

// ============================================
// MISC LABELS (9 strings)
// ============================================

export const misc = {
  // Units
  currency: '$',
  percent: '%',
  hours: 'hours',
  days: 'days',

  // Separators
  dash: '-',
  to: 'to',
  of: 'of',

  // Common
  all: 'All',
  none: 'None',
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

export const utils = {
  /**
   * Get label by key path (e.g., 'metrics.totalSales')
   * @param {string} path - Dot-notation path to label
   * @returns {string|null} Label or null if not found
   */
  getLabel: (path) => {
    const parts = path.split('.');
    let current = { header, metrics, buttons, sections, status, modal, table, days, daysShort, grades, tooltips, badges, empty, loading, error, misc };

    for (const part of parts) {
      if (current[part] === undefined) return null;
      current = current[part];
    }

    return current;
  },

  /**
   * Format label with variables
   * @param {Function|string} label - Label or label function
   * @param {Array} args - Arguments for label function
   * @returns {string} Formatted label
   */
  format: (label, ...args) => {
    if (typeof label === 'function') {
      return label(...args);
    }
    return label;
  },

  /**
   * Get day name from date
   * @param {Date} date - Date object
   * @param {boolean} short - Use short name (default: false)
   * @returns {string} Day name
   */
  getDayName: (date, short = false) => {
    const dayIndex = date.getDay();
    const dayNames = short ? Object.values(daysShort) : Object.values(days);
    return dayNames[dayIndex];
  },

  /**
   * Pluralize label
   * @param {number} count - Count value
   * @param {string} singular - Singular form
   * @param {string} plural - Plural form (optional, defaults to singular + 's')
   * @returns {string} Pluralized label
   */
  pluralize: (count, singular, plural = null) => {
    if (count === 1) return singular;
    return plural || `${singular}s`;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  header,
  metrics,
  buttons,
  sections,
  status,
  modal,
  table,
  days,
  daysShort,
  grades,
  tooltips,
  badges,
  empty,
  loading,
  error,
  misc,
  utils,

  // Metadata
  totalLabels: 73,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
