/**
 * Dashboard V3 - Business Formulas
 *
 * Complete formula configuration based on comprehensive audit
 * Total Formulas: 10
 *
 * Breakdown:
 * - Percentage Calculations: 3 (labor%, COGS%, profit%)
 * - Variance Calculations: 2 (day-over-day, week-over-week)
 * - Aggregations: 2 (total sales, average)
 * - Derived Metrics: 3 (net profit, sales per hour, efficiency)
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 1129-1410, 1767-1845)
 * - Business logic for metric calculations
 */

// ============================================
// PERCENTAGE CALCULATIONS (3 formulas)
// ============================================

export const percentages = {
  /**
   * Calculate labor cost percentage
   * Formula: (Labor Cost / Total Sales) × 100
   *
   * @param {number} laborCost - Total labor cost in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} Labor cost as percentage (0-100)
   */
  laborCostPercent: (laborCost, totalSales) => {
    if (!totalSales || totalSales === 0) return 0;
    return (laborCost / totalSales) * 100;
  },

  /**
   * Calculate COGS (Cost of Goods Sold) percentage
   * Formula: (COGS / Total Sales) × 100
   *
   * @param {number} cogs - Cost of goods sold in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} COGS as percentage (0-100)
   */
  cogsPercent: (cogs, totalSales) => {
    if (!totalSales || totalSales === 0) return 0;
    return (cogs / totalSales) * 100;
  },

  /**
   * Calculate profit margin percentage
   * Formula: (Net Profit / Total Sales) × 100
   *
   * @param {number} netProfit - Net profit in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} Profit margin as percentage (0-100)
   */
  profitMargin: (netProfit, totalSales) => {
    if (!totalSales || totalSales === 0) return 0;
    return (netProfit / totalSales) * 100;
  },
};

// ============================================
// VARIANCE CALCULATIONS (2 formulas)
// ============================================

export const variance = {
  /**
   * Calculate day-over-day variance
   * Formula: ((Current - Previous) / Previous) × 100
   *
   * @param {number} current - Current day's value
   * @param {number} previous - Previous day's value
   * @returns {number} Percentage change (can be negative)
   */
  dayOverDay: (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  },

  /**
   * Calculate week-over-week variance
   * Formula: ((Current Week - Previous Week) / Previous Week) × 100
   *
   * @param {number} currentWeek - Current week's value
   * @param {number} previousWeek - Previous week's value
   * @returns {number} Percentage change (can be negative)
   */
  weekOverWeek: (currentWeek, previousWeek) => {
    if (!previousWeek || previousWeek === 0) return 0;
    return ((currentWeek - previousWeek) / previousWeek) * 100;
  },
};

// ============================================
// AGGREGATION CALCULATIONS (2 formulas)
// ============================================

export const aggregations = {
  /**
   * Calculate total sales from daily breakdown
   * Formula: Sum of all daily sales
   *
   * @param {Array<Object>} days - Array of day objects with sales property
   * @returns {number} Total sales across all days
   */
  totalSales: (days) => {
    if (!Array.isArray(days)) return 0;
    return days.reduce((sum, day) => sum + (day.sales || 0), 0);
  },

  /**
   * Calculate average from array of values
   * Formula: Sum / Count
   *
   * @param {Array<number>} values - Array of numeric values
   * @returns {number} Average value
   */
  average: (values) => {
    if (!Array.isArray(values) || values.length === 0) return 0;
    const sum = values.reduce((acc, val) => acc + val, 0);
    return sum / values.length;
  },
};

// ============================================
// DERIVED METRICS (3 formulas)
// ============================================

export const derived = {
  /**
   * Calculate net profit
   * Formula: Total Sales - Labor Cost - COGS - Other Expenses
   *
   * @param {number} totalSales - Total sales in dollars
   * @param {number} laborCost - Labor cost in dollars
   * @param {number} cogs - Cost of goods sold in dollars
   * @param {number} otherExpenses - Other expenses in dollars (default 0)
   * @returns {number} Net profit in dollars
   */
  netProfit: (totalSales, laborCost, cogs, otherExpenses = 0) => {
    return totalSales - laborCost - cogs - otherExpenses;
  },

  /**
   * Calculate sales per labor hour
   * Formula: Total Sales / Total Labor Hours
   *
   * @param {number} totalSales - Total sales in dollars
   * @param {number} laborHours - Total labor hours worked
   * @returns {number} Sales per hour in dollars
   */
  salesPerHour: (totalSales, laborHours) => {
    if (!laborHours || laborHours === 0) return 0;
    return totalSales / laborHours;
  },

  /**
   * Calculate operational efficiency score
   * Formula: (Sales / (Labor Cost + COGS)) × 100
   * Higher = more efficient operations
   *
   * @param {number} totalSales - Total sales in dollars
   * @param {number} laborCost - Labor cost in dollars
   * @param {number} cogs - Cost of goods sold in dollars
   * @returns {number} Efficiency score (typically 100-300)
   */
  efficiencyScore: (totalSales, laborCost, cogs) => {
    const totalCosts = laborCost + cogs;
    if (!totalCosts || totalCosts === 0) return 0;
    return (totalSales / totalCosts) * 100;
  },
};

// ============================================
// COMPOSITE CALCULATIONS
// Complex formulas using multiple inputs
// ============================================

export const composite = {
  /**
   * Calculate complete P&L breakdown
   *
   * @param {Object} data - Input data object
   * @param {number} data.sales - Total sales
   * @param {number} data.laborCost - Labor cost
   * @param {number} data.cogs - Cost of goods sold
   * @param {number} data.otherExpenses - Other expenses
   * @returns {Object} Complete P&L breakdown
   */
  profitLoss: (data) => {
    const { sales, laborCost, cogs, otherExpenses = 0 } = data;

    const netProfit = derived.netProfit(sales, laborCost, cogs, otherExpenses);
    const laborPercent = percentages.laborCostPercent(laborCost, sales);
    const cogsPercent = percentages.cogsPercent(cogs, sales);
    const profitMargin = percentages.profitMargin(netProfit, sales);

    return {
      sales,
      laborCost,
      laborPercent,
      cogs,
      cogsPercent,
      otherExpenses,
      netProfit,
      profitMargin,
    };
  },

  /**
   * Calculate weekly summary metrics
   *
   * @param {Array<Object>} days - Array of daily data objects
   * @returns {Object} Weekly summary
   */
  weeklySummary: (days) => {
    if (!Array.isArray(days) || days.length === 0) {
      return {
        totalSales: 0,
        avgDailySales: 0,
        totalLaborCost: 0,
        totalCogs: 0,
        netProfit: 0,
        profitMargin: 0,
      };
    }

    const totalSales = aggregations.totalSales(days);
    const avgDailySales = aggregations.average(days.map(d => d.sales || 0));
    const totalLaborCost = days.reduce((sum, d) => sum + (d.labor || 0), 0);
    const totalCogs = days.reduce((sum, d) => sum + (d.cogs || 0), 0);
    const netProfit = derived.netProfit(totalSales, totalLaborCost, totalCogs);
    const profitMargin = percentages.profitMargin(netProfit, totalSales);

    return {
      totalSales,
      avgDailySales,
      totalLaborCost,
      totalCogs,
      netProfit,
      profitMargin,
    };
  },
};

// ============================================
// FORMATTING HELPERS
// Pair formulas with formatting
// ============================================

export const formatters = {
  /**
   * Format currency value
   * @param {number} value - Numeric value
   * @returns {string} Formatted as "$X,XXX.XX"
   */
  currency: (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  },

  /**
   * Format percentage value
   * @param {number} value - Numeric percentage (0-100)
   * @param {number} decimals - Decimal places (default 1)
   * @returns {string} Formatted as "X.X%"
   */
  percentage: (value, decimals = 1) => {
    return `${value.toFixed(decimals)}%`;
  },

  /**
   * Format variance with sign and color
   * @param {number} value - Variance percentage
   * @returns {Object} { text, color, sign }
   */
  variance: (value) => {
    const sign = value > 0 ? '+' : '';
    const color = value > 0 ? 'success' : value < 0 ? 'critical' : 'normal';
    const text = `${sign}${value.toFixed(1)}%`;

    return { text, color, sign };
  },
};

// ============================================
// VALIDATION HELPERS
// Ensure valid inputs
// ============================================

export const validators = {
  /**
   * Validate numeric input
   * @param {any} value - Value to validate
   * @returns {boolean} True if valid number
   */
  isValidNumber: (value) => {
    return typeof value === 'number' && !isNaN(value) && isFinite(value);
  },

  /**
   * Validate percentage range
   * @param {number} value - Percentage value
   * @returns {boolean} True if in valid range (0-100)
   */
  isValidPercent: (value) => {
    return validators.isValidNumber(value) && value >= 0 && value <= 100;
  },

  /**
   * Validate positive number
   * @param {number} value - Numeric value
   * @returns {boolean} True if positive
   */
  isPositive: (value) => {
    return validators.isValidNumber(value) && value >= 0;
  },

  /**
   * Sanitize numeric input
   * @param {any} value - Input value
   * @param {number} fallback - Fallback value if invalid (default 0)
   * @returns {number} Sanitized number
   */
  sanitizeNumber: (value, fallback = 0) => {
    const num = parseFloat(value);
    return validators.isValidNumber(num) ? num : fallback;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  percentages,
  variance,
  aggregations,
  derived,
  composite,
  formatters,
  validators,

  // Metadata
  totalFormulas: 10,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
