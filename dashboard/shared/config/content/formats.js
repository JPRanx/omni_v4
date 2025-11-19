/**
 * Dashboard V3 - Data Formatting Functions
 *
 * Complete formatting configuration based on comprehensive audit
 * Total Formatters: 15
 *
 * Breakdown:
 * - Currency Formatting: 3 variants
 * - Number Formatting: 3 variants
 * - Percentage Formatting: 2 variants
 * - Date/Time Formatting: 4 variants
 * - Text Formatting: 3 variants
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (data formatting patterns)
 * - Display logic for metrics and values
 */

// ============================================
// CURRENCY FORMATTING (3 variants)
// ============================================

export const currency = {
  /**
   * Format as full currency with cents
   * Example: $12,345.67
   *
   * @param {number} value - Numeric value
   * @returns {string} Formatted currency string
   */
  full: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  },

  /**
   * Format as rounded currency (no cents)
   * Example: $12,346
   *
   * @param {number} value - Numeric value
   * @returns {string} Formatted currency string
   */
  rounded: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  },

  /**
   * Format as compact currency (K, M notation)
   * Example: $12.3K or $1.2M
   *
   * @param {number} value - Numeric value
   * @returns {string} Formatted compact currency string
   */
  compact: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '$0';

    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return currency.rounded(value);
  },
};

// ============================================
// NUMBER FORMATTING (3 variants)
// ============================================

export const number = {
  /**
   * Format as decimal number
   * Example: 1,234.56
   *
   * @param {number} value - Numeric value
   * @param {number} decimals - Decimal places (default: 2)
   * @returns {string} Formatted number string
   */
  decimal: (value, decimals = 2) => {
    if (value === null || value === undefined || isNaN(value)) return '0';
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  },

  /**
   * Format as integer (no decimals)
   * Example: 1,235
   *
   * @param {number} value - Numeric value
   * @returns {string} Formatted integer string
   */
  integer: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '0';
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.round(value));
  },

  /**
   * Format as compact number (K, M notation)
   * Example: 1.2K or 1.2M
   *
   * @param {number} value - Numeric value
   * @returns {string} Formatted compact number string
   */
  compact: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '0';

    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return number.integer(value);
  },
};

// ============================================
// PERCENTAGE FORMATTING (2 variants)
// ============================================

export const percentage = {
  /**
   * Format as percentage with decimals
   * Example: 12.34%
   *
   * @param {number} value - Numeric percentage (0-100)
   * @param {number} decimals - Decimal places (default: 1)
   * @returns {string} Formatted percentage string
   */
  decimal: (value, decimals = 1) => {
    if (value === null || value === undefined || isNaN(value)) return '0.0%';
    return `${value.toFixed(decimals)}%`;
  },

  /**
   * Format as integer percentage (no decimals)
   * Example: 12%
   *
   * @param {number} value - Numeric percentage (0-100)
   * @returns {string} Formatted percentage string
   */
  integer: (value) => {
    if (value === null || value === undefined || isNaN(value)) return '0%';
    return `${Math.round(value)}%`;
  },
};

// ============================================
// DATE/TIME FORMATTING (4 variants)
// ============================================

export const date = {
  /**
   * Format as full date
   * Example: January 15, 2025
   *
   * @param {Date|string} dateValue - Date object or ISO string
   * @returns {string} Formatted date string
   */
  full: (dateValue) => {
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return 'Invalid Date';

    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(d);
  },

  /**
   * Format as short date
   * Example: 01/15/2025
   *
   * @param {Date|string} dateValue - Date object or ISO string
   * @returns {string} Formatted date string
   */
  short: (dateValue) => {
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return 'Invalid Date';

    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(d);
  },

  /**
   * Format as date range
   * Example: Jan 15 - Jan 21, 2025
   *
   * @param {Date|string} startDate - Start date
   * @param {Date|string} endDate - End date
   * @returns {string} Formatted date range string
   */
  range: (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) return 'Invalid Date Range';

    const startFormatted = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(start);

    const endFormatted = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(end);

    return `${startFormatted} - ${endFormatted}`;
  },

  /**
   * Format as time
   * Example: 3:45 PM
   *
   * @param {Date|string} dateValue - Date object or ISO string
   * @returns {string} Formatted time string
   */
  time: (dateValue) => {
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return 'Invalid Time';

    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(d);
  },
};

// ============================================
// TEXT FORMATTING (3 variants)
// ============================================

export const text = {
  /**
   * Capitalize first letter
   * Example: "hello" → "Hello"
   *
   * @param {string} str - Input string
   * @returns {string} Capitalized string
   */
  capitalize: (str) => {
    if (!str || typeof str !== 'string') return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },

  /**
   * Convert to title case
   * Example: "hello world" → "Hello World"
   *
   * @param {string} str - Input string
   * @returns {string} Title case string
   */
  titleCase: (str) => {
    if (!str || typeof str !== 'string') return '';
    return str
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  },

  /**
   * Truncate with ellipsis
   * Example: "Hello World" → "Hello..." (maxLength: 8)
   *
   * @param {string} str - Input string
   * @param {number} maxLength - Maximum length
   * @returns {string} Truncated string
   */
  truncate: (str, maxLength = 50) => {
    if (!str || typeof str !== 'string') return '';
    if (str.length <= maxLength) return str;
    return str.slice(0, maxLength - 3) + '...';
  },
};

// ============================================
// VARIANCE FORMATTING (1 special formatter)
// ============================================

export const variance = {
  /**
   * Format variance with sign, color, and icon
   * Example: +12.3% ↑ (success) or -5.2% ↓ (critical)
   *
   * @param {number} value - Variance percentage (can be negative)
   * @param {boolean} includeIcon - Include arrow icon (default: true)
   * @returns {Object} { text, color, icon, sign }
   */
  format: (value, includeIcon = true) => {
    if (value === null || value === undefined || isNaN(value)) {
      return {
        text: '0.0%',
        color: 'normal',
        icon: '',
        sign: '',
      };
    }

    const sign = value > 0 ? '+' : '';
    const color = value > 0 ? 'success' : value < 0 ? 'critical' : 'normal';
    const icon = includeIcon
      ? value > 0
        ? '↑'
        : value < 0
        ? '↓'
        : '→'
      : '';

    const text = `${sign}${value.toFixed(1)}%`;

    return {
      text,
      color,
      icon,
      sign,
      value,
    };
  },
};

// ============================================
// UTILITY FORMATTERS
// ============================================

export const utils = {
  /**
   * Format value based on type detection
   * Auto-detects currency, percentage, or number
   *
   * @param {number} value - Numeric value
   * @param {string} type - Value type hint ('currency', 'percentage', 'number')
   * @returns {string} Formatted value
   */
  auto: (value, type = 'number') => {
    if (value === null || value === undefined || isNaN(value)) return '—';

    switch (type) {
      case 'currency':
        return currency.rounded(value);
      case 'percentage':
        return percentage.decimal(value);
      case 'number':
      default:
        return number.decimal(value, 0);
    }
  },

  /**
   * Format with unit suffix
   * Example: (10, 'hours') → "10 hours"
   *
   * @param {number} value - Numeric value
   * @param {string} unit - Unit label
   * @param {boolean} pluralize - Auto-pluralize unit (default: true)
   * @returns {string} Formatted value with unit
   */
  withUnit: (value, unit, pluralize = true) => {
    if (value === null || value === undefined || isNaN(value)) return `0 ${unit}`;

    const formattedValue = number.integer(value);
    const displayUnit = pluralize && value !== 1 ? `${unit}s` : unit;

    return `${formattedValue} ${displayUnit}`;
  },

  /**
   * Format null/undefined/NaN values
   *
   * @param {any} value - Input value
   * @param {string} fallback - Fallback string (default: '—')
   * @returns {string} Value or fallback
   */
  fallback: (value, fallback = '—') => {
    if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
      return fallback;
    }
    return value.toString();
  },

  /**
   * Sanitize numeric input
   *
   * @param {any} value - Input value
   * @param {number} defaultValue - Default if invalid (default: 0)
   * @returns {number} Sanitized number
   */
  sanitize: (value, defaultValue = 0) => {
    const num = parseFloat(value);
    return isNaN(num) ? defaultValue : num;
  },
};

// ============================================
// FORMAT PRESETS
// Common formatting combinations
// ============================================

export const presets = {
  // Sales formatting
  sales: (value) => currency.rounded(value),

  // Labor cost formatting
  labor: (value) => currency.rounded(value),
  laborPercent: (value) => percentage.decimal(value, 1),

  // COGS formatting
  cogs: (value) => currency.rounded(value),
  cogsPercent: (value) => percentage.decimal(value, 1),

  // Profit formatting
  profit: (value) => currency.rounded(value),
  profitMargin: (value) => percentage.decimal(value, 1),

  // Hours formatting
  hours: (value) => utils.withUnit(value, 'hour', true),

  // Day of week
  dayOfWeek: (date) => {
    const d = new Date(date);
    return new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(d);
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  currency,
  number,
  percentage,
  date,
  text,
  variance,
  utils,
  presets,

  // Metadata
  totalFormatters: 15,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
