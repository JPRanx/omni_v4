/**
 * Dashboard V3 - User Messages
 *
 * Complete message configuration for user feedback
 * Total Messages: 28
 *
 * Breakdown:
 * - Success Messages: 5
 * - Error Messages: 8
 * - Warning Messages: 5
 * - Info Messages: 5
 * - Empty State Messages: 5
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (error handling, user feedback)
 * - Modal interactions and data loading states
 */

// ============================================
// SUCCESS MESSAGES (5 messages)
// ============================================

export const success = {
  dataLoaded: 'Dashboard data loaded successfully',
  dataExported: 'Data exported successfully',
  actionCompleted: 'Action completed successfully',
  settingsSaved: 'Settings saved successfully',
  refreshComplete: 'Dashboard refreshed successfully',
};

// ============================================
// ERROR MESSAGES (8 messages)
// ============================================

export const error = {
  // Generic errors
  generic: 'An unexpected error occurred. Please try again.',
  unknown: 'Unknown error. Please contact support if this persists.',

  // Loading errors
  loadFailed: 'Failed to load dashboard data. Please refresh the page.',
  networkError: 'Network connection error. Please check your internet connection.',
  serverError: 'Server error. Please try again later.',

  // Action errors
  exportFailed: 'Failed to export data. Please try again.',
  invalidData: 'Invalid data format. Please check your input.',
  permissionDenied: 'Permission denied. You do not have access to this resource.',
};

// ============================================
// WARNING MESSAGES (5 messages)
// ============================================

export const warning = {
  // Performance warnings
  highLabor: (percent) => `Labor cost is ${percent}% - above target range of 25-30%`,
  highCogs: (percent) => `COGS is ${percent}% - above recommended 30% threshold`,
  lowProfit: (percent) => `Profit margin is only ${percent}% - below healthy threshold`,

  // Data warnings
  incompleteData: 'Some data is incomplete or missing',
  outdatedData: 'Data may be outdated. Consider refreshing the dashboard.',
};

// ============================================
// INFO MESSAGES (5 messages)
// ============================================

export const info = {
  // General information
  selectWeek: 'Select a week from the tabs above to view data',
  noChanges: 'No changes detected',
  processing: 'Processing your request...',

  // Feature information
  newFeature: 'New feature available! Check out the Investigation modal for detailed insights.',
  betaFeature: 'This is a beta feature. Your feedback is appreciated.',
};

// ============================================
// EMPTY STATE MESSAGES (5 messages)
// ============================================

export const empty = {
  // No data messages
  noData: 'No data available for the selected period',
  noRestaurants: 'No restaurants found. Please add restaurants to view data.',
  noEmployees: 'No employees with auto-clockout warnings',
  noResults: 'No results match your filters. Try adjusting your criteria.',
  noDailyData: (restaurantName) => `No daily breakdown available for ${restaurantName}`,
};

// ============================================
// LOADING MESSAGES (3 messages)
// ============================================

export const loading = {
  default: 'Loading...',
  fetchingData: 'Fetching dashboard data...',
  processing: 'Processing data...',
};

// ============================================
// CONFIRMATION MESSAGES (5 messages)
// ============================================

export const confirm = {
  // Action confirmations
  export: 'Are you sure you want to export this data?',
  refresh: 'Are you sure you want to refresh? Any unsaved changes will be lost.',
  delete: 'Are you sure you want to delete this item? This action cannot be undone.',
  logout: 'Are you sure you want to log out?',
  cancel: 'Are you sure you want to cancel? Any changes will be lost.',
};

// ============================================
// TOOLTIP MESSAGES (12 messages)
// ============================================

export const tooltips = {
  // Metric tooltips
  totalSales: 'Sum of all restaurant sales for the selected week',
  laborCost: 'Total labor expenses including wages, benefits, and overtime',
  laborPercent: 'Labor cost as a percentage of total sales. Target: 25-30%',
  cogs: 'Cost of Goods Sold - raw materials, ingredients, and supplies',
  cogsPercent: 'COGS as a percentage of total sales. Target: ≤30%',
  netProfit: 'Total sales minus labor, COGS, and other expenses',
  profitMargin: 'Net profit as a percentage of total sales. Target: ≥15%',

  // Action tooltips
  investigate: 'View detailed daily breakdown and performance trends',
  export: 'Export dashboard data to CSV or PDF format',
  filter: 'Filter restaurants by performance status',
  refresh: 'Reload dashboard with latest data',

  // Auto clockout tooltip
  autoClockout: 'Employees who have worked 10+ hours without clocking out. Automatic clock-out will occur at midnight.',
};

// ============================================
// VALIDATION MESSAGES (5 messages)
// ============================================

export const validation = {
  required: (field) => `${field} is required`,
  invalid: (field) => `${field} is invalid`,
  tooShort: (field, min) => `${field} must be at least ${min} characters`,
  tooLong: (field, max) => `${field} must be no more than ${max} characters`,
  outOfRange: (field, min, max) => `${field} must be between ${min} and ${max}`,
};

// ============================================
// NOTIFICATION MESSAGES (8 messages)
// ============================================

export const notification = {
  // Performance notifications
  excellentDay: (restaurantName, sales) => `🌟 ${restaurantName} had an excellent day with $${sales.toLocaleString()} in sales!`,
  criticalLabor: (restaurantName, percent) => `🚨 ${restaurantName} labor cost is critical at ${percent}%`,
  lowSales: (restaurantName, sales) => `⚠️ ${restaurantName} sales are low at $${sales.toLocaleString()}`,

  // System notifications
  dataRefreshed: 'Dashboard data has been refreshed',
  newWeekAvailable: 'New week data is now available',
  systemUpdate: 'System will update in 5 minutes. Please save your work.',

  // Auto clockout notifications
  autoClockoutWarning: (count) => `⚠️ ${count} employee${count > 1 ? 's' : ''} approaching auto-clockout`,
  autoClockoutTriggered: (employeeName) => `🔔 ${employeeName} has been automatically clocked out`,
};

// ============================================
// BADGE MESSAGES (6 messages)
// ============================================

export const badges = {
  topPerformer: 'Top Performer',
  trendingUp: '📈 Trending Up',
  needsAttention: '⚠️ Needs Attention',
  critical: '🚨 Critical',
  improved: '✨ Improved',
  newData: '🆕 New',
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

export const utils = {
  /**
   * Get message by key path (e.g., 'error.loadFailed')
   * @param {string} path - Dot-notation path to message
   * @returns {string|Function|null} Message or null if not found
   */
  getMessage: (path) => {
    const parts = path.split('.');
    let current = { success, error, warning, info, empty, loading, confirm, tooltips, validation, notification, badges };

    for (const part of parts) {
      if (current[part] === undefined) return null;
      current = current[part];
    }

    return current;
  },

  /**
   * Format message with variables
   * @param {Function|string} message - Message or message function
   * @param {Array} args - Arguments for message function
   * @returns {string} Formatted message
   */
  format: (message, ...args) => {
    if (typeof message === 'function') {
      return message(...args);
    }
    return message;
  },

  /**
   * Create notification object
   * @param {string} type - Message type (success, error, warning, info)
   * @param {string} message - Message text
   * @param {number} duration - Display duration in ms (default: 5000)
   * @returns {Object} Notification object
   */
  createNotification: (type, message, duration = 5000) => {
    return {
      type,
      message,
      duration,
      timestamp: Date.now(),
      id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
  },

  /**
   * Get message type icon
   * @param {string} type - Message type
   * @returns {string} Icon emoji
   */
  getIcon: (type) => {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
      loading: '⏳',
    };
    return icons[type] || '';
  },

  /**
   * Get message type color
   * @param {string} type - Message type
   * @returns {string} Tailwind color class
   */
  getColor: (type) => {
    const colors = {
      success: 'text-green-700 bg-green-50 border-green-600',
      error: 'text-red-700 bg-red-50 border-red-600',
      warning: 'text-yellow-700 bg-yellow-50 border-yellow-600',
      info: 'text-blue-700 bg-blue-50 border-blue-500',
      loading: 'text-gray-700 bg-gray-50 border-gray-400',
    };
    return colors[type] || colors.info;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  success,
  error,
  warning,
  info,
  empty,
  loading,
  confirm,
  tooltips,
  validation,
  notification,
  badges,
  utils,

  // Metadata
  totalMessages: 28,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
