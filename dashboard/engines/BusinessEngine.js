/**
 * Dashboard V3 - Business Engine
 *
 * Smart system that handles all business logic and calculations
 *
 * Responsibilities:
 * - Load all business logic (thresholds, formulas, grading, statuses)
 * - Evaluate data against thresholds
 * - Calculate grades and statuses
 * - Provide methods for all business calculations
 * - Format business data for display
 *
 * Usage:
 * ```javascript
 * import BusinessEngine from './engines/BusinessEngine.js';
 * import config from './shared/config/index.js';
 *
 * const businessEngine = new BusinessEngine(config);
 * const status = businessEngine.evaluateSales(45000); // Returns 'excellent'
 * const grade = businessEngine.calculateGrade({ sales: 45000, laborPercent: 28, profitMargin: 18 });
 * ```
 */

class BusinessEngine {
  constructor(config) {
    if (!config) {
      throw new Error('BusinessEngine: config is required');
    }

    this.config = config;
    this.initialized = false;

    // Business configuration
    this.thresholds = config.business.thresholds;
    this.formulas = config.business.formulas;
    this.grading = config.business.grading;
    this.statuses = config.business.statuses;
    this.capacity = config.business.capacity;

    // Content configuration (for formatting)
    this.formats = config.content.formats;

    this.initialize();
  }

  /**
   * Initialize business engine
   */
  initialize() {
    if (this.initialized) {
      console.warn('BusinessEngine: Already initialized');
      return;
    }

    console.log('[BusinessEngine] Initializing...');

    // Validate business configurations
    this.validateConfigurations();

    this.initialized = true;
    console.log('[BusinessEngine] Initialized successfully');
  }

  /**
   * Validate business configurations
   */
  validateConfigurations() {
    const errors = [];

    if (!this.thresholds) errors.push('Missing thresholds configuration');
    if (!this.formulas) errors.push('Missing formulas configuration');
    if (!this.grading) errors.push('Missing grading configuration');
    if (!this.statuses) errors.push('Missing statuses configuration');

    if (errors.length > 0) {
      console.error('[BusinessEngine] Configuration errors:', errors);
      throw new Error(`BusinessEngine: ${errors.join(', ')}`);
    }
  }

  // ============================================
  // THRESHOLD EVALUATION
  // ============================================

  /**
   * Evaluate sales value against thresholds
   * @param {number} sales - Sales value
   * @returns {string} Status name
   */
  evaluateSales(sales) {
    return this.thresholds.sales.getStatus(sales);
  }

  /**
   * Evaluate labor percentage against thresholds
   * @param {number} laborPercent - Labor cost percentage
   * @returns {string} Status name
   */
  evaluateLabor(laborPercent) {
    return this.thresholds.labor.getStatus(laborPercent);
  }

  /**
   * Evaluate COGS percentage against thresholds
   * @param {number} cogsPercent - COGS percentage
   * @returns {string} Status name
   */
  evaluateCOGS(cogsPercent) {
    return this.thresholds.cogs.getStatus(cogsPercent);
  }

  /**
   * Evaluate profit margin against thresholds
   * @param {number} profitPercent - Profit margin percentage
   * @returns {string} Status name
   */
  evaluateProfit(profitPercent) {
    return this.thresholds.profitLoss.getStatus(profitPercent);
  }

  /**
   * Evaluate variance against thresholds
   * @param {number} variance - Variance percentage
   * @param {string} type - Variance type ('day' or 'week')
   * @returns {string} Status name
   */
  evaluateVariance(variance, type = 'day') {
    return this.thresholds.variance.getStatus(variance, type);
  }

  // ============================================
  // FORMULA CALCULATIONS
  // ============================================

  /**
   * Calculate labor cost percentage
   * @param {number} laborCost - Labor cost in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} Labor percentage
   */
  calculateLaborPercent(laborCost, totalSales) {
    return this.formulas.percentages.laborCostPercent(laborCost, totalSales);
  }

  /**
   * Calculate COGS percentage
   * @param {number} cogs - COGS in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} COGS percentage
   */
  calculateCOGSPercent(cogs, totalSales) {
    return this.formulas.percentages.cogsPercent(cogs, totalSales);
  }

  /**
   * Calculate profit margin
   * @param {number} netProfit - Net profit in dollars
   * @param {number} totalSales - Total sales in dollars
   * @returns {number} Profit margin percentage
   */
  calculateProfitMargin(netProfit, totalSales) {
    return this.formulas.percentages.profitMargin(netProfit, totalSales);
  }

  /**
   * Calculate day-over-day variance
   * @param {number} current - Current day value
   * @param {number} previous - Previous day value
   * @returns {number} Variance percentage
   */
  calculateDayOverDay(current, previous) {
    return this.formulas.variance.dayOverDay(current, previous);
  }

  /**
   * Calculate week-over-week variance
   * @param {number} currentWeek - Current week value
   * @param {number} previousWeek - Previous week value
   * @returns {number} Variance percentage
   */
  calculateWeekOverWeek(currentWeek, previousWeek) {
    return this.formulas.variance.weekOverWeek(currentWeek, previousWeek);
  }

  /**
   * Calculate net profit
   * @param {number} totalSales - Total sales
   * @param {number} laborCost - Labor cost
   * @param {number} cogs - COGS
   * @param {number} otherExpenses - Other expenses (optional)
   * @returns {number} Net profit
   */
  calculateNetProfit(totalSales, laborCost, cogs, otherExpenses = 0) {
    return this.formulas.derived.netProfit(totalSales, laborCost, cogs, otherExpenses);
  }

  /**
   * Calculate sales per hour
   * @param {number} totalSales - Total sales
   * @param {number} laborHours - Total labor hours
   * @returns {number} Sales per hour
   */
  calculateSalesPerHour(totalSales, laborHours) {
    return this.formulas.derived.salesPerHour(totalSales, laborHours);
  }

  /**
   * Calculate efficiency score
   * @param {number} totalSales - Total sales
   * @param {number} laborCost - Labor cost
   * @param {number} cogs - COGS
   * @returns {number} Efficiency score
   */
  calculateEfficiency(totalSales, laborCost, cogs) {
    return this.formulas.derived.efficiencyScore(totalSales, laborCost, cogs);
  }

  /**
   * Calculate complete P&L breakdown
   * @param {Object} data - Input data
   * @returns {Object} Complete P&L with all calculations
   */
  calculateProfitLoss(data) {
    return this.formulas.composite.profitLoss(data);
  }

  /**
   * Calculate weekly summary
   * @param {Array<Object>} days - Array of daily data
   * @returns {Object} Weekly summary
   */
  calculateWeeklySummary(days) {
    return this.formulas.composite.weeklySummary(days);
  }

  // ============================================
  // GRADING
  // ============================================

  /**
   * Calculate grade from score
   * @param {number} score - Numeric score (0-100)
   * @returns {Object} Grade object
   */
  calculateGradeFromScore(score) {
    return this.grading.calculate.fromScore(score);
  }

  /**
   * Calculate grade from metrics
   * @param {Object} metrics - Metrics object
   * @returns {Object} Grade object
   */
  calculateGrade(metrics) {
    return this.grading.calculate.fromMetrics(metrics);
  }

  /**
   * Calculate weighted grade
   * @param {Object} scores - Scores with weights
   * @returns {Object} Grade object
   */
  calculateWeightedGrade(scores) {
    return this.grading.calculate.weighted(scores);
  }

  /**
   * Check if grade is passing
   * @param {Object} grade - Grade object
   * @returns {boolean} True if passing
   */
  isGradePassing(grade) {
    return this.grading.compare.isPassing(grade);
  }

  /**
   * Check if grade is excellent
   * @param {Object} grade - Grade object
   * @returns {boolean} True if excellent
   */
  isGradeExcellent(grade) {
    return this.grading.compare.isExcellent(grade);
  }

  // ============================================
  // STATUS MANAGEMENT
  // ============================================

  /**
   * Get status object by name
   * @param {string} statusName - Status name
   * @returns {Object|null} Status object or null
   */
  getStatus(statusName) {
    return this.statuses.getters.byName(statusName);
  }

  /**
   * Get status badge class
   * @param {string} statusName - Status name
   * @returns {string} Badge CSS class
   */
  getStatusBadgeClass(statusName) {
    return this.statuses.getters.getBadgeClass(statusName);
  }

  /**
   * Get status Tailwind classes
   * @param {string} statusName - Status name
   * @returns {string} Tailwind CSS classes
   */
  getStatusClasses(statusName) {
    return this.statuses.getters.getTailwindClass(statusName);
  }

  /**
   * Determine status from sales
   * @param {number} sales - Sales value
   * @returns {string} Status name
   */
  determineStatusFromSales(sales) {
    return this.statuses.determine.fromSales(sales);
  }

  /**
   * Determine status from labor percentage
   * @param {number} laborPercent - Labor percentage
   * @returns {string} Status name
   */
  determineStatusFromLabor(laborPercent) {
    return this.statuses.determine.fromLabor(laborPercent);
  }

  /**
   * Determine status from profit margin
   * @param {number} profitMargin - Profit margin
   * @returns {string} Status name
   */
  determineStatusFromProfit(profitMargin) {
    return this.statuses.determine.fromProfit(profitMargin);
  }

  /**
   * Check if status is positive
   * @param {string} statusName - Status name
   * @returns {boolean} True if positive
   */
  isStatusPositive(statusName) {
    return this.statuses.compare.isPositive(statusName);
  }

  /**
   * Check if status is negative
   * @param {string} statusName - Status name
   * @returns {boolean} True if negative
   */
  isStatusNegative(statusName) {
    return this.statuses.compare.isNegative(statusName);
  }

  // ============================================
  // COMPREHENSIVE EVALUATION
  // ============================================

  /**
   * Evaluate complete restaurant performance
   * @param {Object} data - Restaurant data
   * @returns {Object} Complete evaluation
   */
  evaluateRestaurant(data) {
    const {
      sales,
      laborCost,
      laborHours,
      cogs,
      otherExpenses = 0,
    } = data;

    // Calculate all metrics
    const laborPercent = this.calculateLaborPercent(laborCost, sales);
    const cogsPercent = this.calculateCOGSPercent(cogs, sales);
    const netProfit = this.calculateNetProfit(sales, laborCost, cogs, otherExpenses);
    const profitMargin = this.calculateProfitMargin(netProfit, sales);
    const salesPerHour = laborHours ? this.calculateSalesPerHour(sales, laborHours) : 0;
    const efficiency = this.calculateEfficiency(sales, laborCost, cogs);

    // Evaluate against thresholds
    const salesStatus = this.evaluateSales(sales);
    const laborStatus = this.evaluateLabor(laborPercent);
    const cogsStatus = this.evaluateCOGS(cogsPercent);
    const profitStatus = this.evaluateProfit(profitMargin);

    // Calculate grade
    const grade = this.calculateGrade({
      sales,
      laborPercent,
      profitMargin,
    });

    // Determine overall status (worst of all statuses)
    const allStatuses = [salesStatus, laborStatus, cogsStatus, profitStatus];
    const statusPriorities = allStatuses.map(s => this.getStatus(s)?.priority || 0);
    const lowestPriority = Math.min(...statusPriorities);
    const overallStatus = allStatuses.find(s => this.getStatus(s)?.priority === lowestPriority);

    return {
      metrics: {
        sales,
        laborCost,
        laborPercent,
        cogs,
        cogsPercent,
        netProfit,
        profitMargin,
        salesPerHour,
        efficiency,
      },
      statuses: {
        sales: salesStatus,
        labor: laborStatus,
        cogs: cogsStatus,
        profit: profitStatus,
        overall: overallStatus,
      },
      grade,
      isPassing: this.isGradePassing(grade),
      isExcellent: this.isGradeExcellent(grade),
      needsAttention: this.isStatusNegative(overallStatus),
    };
  }

  /**
   * Evaluate day performance
   * @param {Object} currentDay - Current day data
   * @param {Object} previousDay - Previous day data (optional)
   * @returns {Object} Day evaluation
   */
  evaluateDay(currentDay, previousDay = null) {
    const evaluation = this.evaluateRestaurant(currentDay);

    // Add variance if previous day provided
    if (previousDay) {
      const salesVariance = this.calculateDayOverDay(currentDay.sales, previousDay.sales);
      const varianceStatus = this.evaluateVariance(salesVariance, 'day');

      evaluation.variance = {
        sales: salesVariance,
        status: varianceStatus,
        isSignificant: Math.abs(salesVariance) >= this.thresholds.variance.dayOverDay.significant,
      };
    }

    return evaluation;
  }

  /**
   * Evaluate week performance
   * @param {Array<Object>} days - Array of day data
   * @returns {Object} Week evaluation
   */
  evaluateWeek(days) {
    const summary = this.calculateWeeklySummary(days);
    const evaluation = this.evaluateRestaurant({
      sales: summary.totalSales,
      laborCost: summary.totalLaborCost,
      cogs: summary.totalCogs,
    });

    evaluation.summary = summary;
    evaluation.dayCount = days.length;

    return evaluation;
  }

  // ============================================
  // FORMATTING HELPERS
  // ============================================

  /**
   * Format currency value
   * @param {number} value - Numeric value
   * @returns {string} Formatted currency
   */
  formatCurrency(value) {
    return this.formats.currency.rounded(value);
  }

  /**
   * Format percentage value
   * @param {number} value - Percentage value
   * @returns {string} Formatted percentage
   */
  formatPercentage(value) {
    return this.formats.percentage.decimal(value, 1);
  }

  /**
   * Format variance with color
   * @param {number} value - Variance percentage
   * @returns {Object} Formatted variance
   */
  formatVariance(value) {
    return this.formats.variance.format(value);
  }

  // ============================================
  // CAPACITY & DEMAND HELPERS
  // ============================================

  /**
   * Get service stress status
   * @param {number} stressPercent - Service stress percentage
   * @returns {string} Status (excellent, good, acceptable, warning, critical, severe)
   */
  getServiceStressStatus(stressPercent) {
    return this.capacity.serviceStress.getStatus(stressPercent);
  }

  /**
   * Get service stress color
   * @param {number} stressPercent - Service stress percentage
   * @returns {string} Color (success, warning, critical)
   */
  getServiceStressColor(stressPercent) {
    return this.capacity.serviceStress.getColor(stressPercent);
  }

  /**
   * Get fulfillment status from pass rate
   * @param {number} passRate - Pass rate percentage
   * @returns {string} Status (excellent, good, acceptable, warning, poor, critical)
   */
  getFulfillmentStatus(passRate) {
    return this.capacity.fulfillmentStandards.getStatus(passRate);
  }

  /**
   * Get fulfillment color from pass rate
   * @param {number} passRate - Pass rate percentage
   * @returns {string} Color (success, warning, critical)
   */
  getFulfillmentColor(passRate) {
    return this.capacity.fulfillmentStandards.getColor(passRate);
  }

  /**
   * Calculate service stress percentage
   * @param {number} orders - Number of orders
   * @param {number} capacity - Service capacity
   * @returns {number} Stress percentage
   */
  calculateServiceStress(orders, capacity) {
    return this.capacity.calculations.calculateStress(orders, capacity);
  }

  /**
   * Calculate pass rate from passed/total
   * @param {number} passed - Orders meeting standard
   * @param {number} total - Total orders
   * @returns {number} Pass rate percentage
   */
  calculatePassRate(passed, total) {
    return this.capacity.calculations.calculatePassRate(passed, total);
  }

  /**
   * Check if order meets time standard
   * @param {number} actualTime - Actual service time
   * @param {string} channel - Service channel (tables, driveThru, toGo)
   * @returns {boolean} True if meets standard
   */
  meetsTimeStandard(actualTime, channel) {
    return this.capacity.calculations.meetsStandard(actualTime, channel);
  }

  /**
   * Get shift from hour
   * @param {number} hour - Hour (0-23)
   * @returns {string} Shift name (morning, evening, overnight)
   */
  getShiftFromHour(hour) {
    return this.capacity.shifts.getShift(hour);
  }

  /**
   * Check if hour is peak time
   * @param {number} hour - Hour (0-23)
   * @param {string} shift - Shift name
   * @returns {boolean} True if peak hour
   */
  isPeakHour(hour, shift) {
    return this.capacity.shifts.isPeakHour(hour, shift);
  }

  /**
   * Calculate capacity health score
   * @param {Object} metrics - Capacity metrics
   * @returns {number} Health score (0-100)
   */
  calculateCapacityScore(metrics) {
    return this.capacity.capacityScore.calculate(metrics);
  }

  /**
   * Get capacity grade from score
   * @param {number} score - Capacity score
   * @returns {Object} Grade object with label and status
   */
  getCapacityGrade(score) {
    return this.capacity.capacityScore.getGrade(score);
  }

  /**
   * Get service channel standards
   * @param {string} channel - Channel name (tables, driveThru, toGo)
   * @returns {Object} Channel standards (targetTime, maxTime, criticalTime)
   */
  getChannelStandards(channel) {
    return this.capacity.channels[channel] || null;
  }

  // ============================================
  // ADVANCED CAPACITY CALCULATIONS
  // ============================================

  /**
   * Calculate shift stress percentage from timeslot data
   * @param {Array} slots - Array of timeslot objects with orders property
   * @returns {string} Stress percentage as string (e.g., "25.5")
   */
  calculateShiftStress(slots) {
    if (!slots || slots.length === 0) return '0.0';

    const capacity = this.capacity;
    const maxOrdersPer15Min = 35; // TODO: Move to capacity config
    const stressThreshold = 0.85; // TODO: Move to capacity config

    const stressedSlots = slots.filter(s =>
      (s.orders / maxOrdersPer15Min) > stressThreshold
    );

    return ((stressedSlots.length / slots.length) * 100).toFixed(1);
  }

  /**
   * Determine performance status from pass rate
   * @param {number} passRate - Pass rate percentage (0-100)
   * @returns {string} 'pass', 'warning', or 'fail'
   */
  getPerformanceStatus(passRate) {
    const passThreshold = 85;
    const warningThreshold = 70;

    if (passRate >= passThreshold) return 'pass';
    if (passRate >= warningThreshold) return 'warning';
    return 'fail';
  }

  /**
   * Determine streak status from pass rate
   * @param {number} passRate - Pass rate percentage (0-100)
   * @returns {string} 'hot', 'cold', or 'none'
   */
  getStreakStatus(passRate) {
    const hotStreakThreshold = 85;
    const coldStreakThreshold = 70;

    if (passRate >= hotStreakThreshold) return 'hot';
    if (passRate < coldStreakThreshold) return 'cold';
    return 'none';
  }

  /**
   * Calculate channel performance with status and color
   * @param {number} successRate - Success rate percentage (0-100)
   * @returns {Object} {status: string, color: string, rate: number}
   */
  getChannelPerformance(successRate) {
    const excellentThreshold = 80;
    const acceptableThreshold = 60;

    let status, color;

    if (successRate >= excellentThreshold) {
      status = 'excellent';
      color = '#047857'; // green-700
    } else if (successRate >= acceptableThreshold) {
      status = 'acceptable';
      color = '#CA8A04'; // yellow-700
    } else {
      status = 'poor';
      color = '#DC2626'; // red-600
    }

    return { status, color, rate: successRate };
  }

  /**
   * Get timeslot configuration for a shift
   * @param {string} shift - 'morning' or 'evening'
   * @returns {Object} {start: number, end: number, interval: number}
   */
  getTimeslotConfig(shift) {
    if (shift === 'morning') {
      return { start: 7, end: 13, interval: 15 };
    } else if (shift === 'evening') {
      return { start: 16, end: 21, interval: 15 };
    }
    return { start: 0, end: 24, interval: 15 };
  }

  // ============================================
  // BUSINESS STATISTICS
  // ============================================

  /**
   * Get business statistics
   * @returns {Object} Business stats
   */
  getStats() {
    return {
      totalThresholds: this.thresholds.totalThresholds || 0,
      totalFormulas: this.formulas.totalFormulas || 0,
      totalGradeLevels: this.grading.totalLevels || 0,
      totalStatuses: this.statuses.totalTypes || 0,
      totalCapacityConfigs: this.capacity.totalConfigs || 0,
      initialized: this.initialized,
    };
  }

  /**
   * Cleanup
   */
  destroy() {
    console.log('[BusinessEngine] Destroying...');
    this.initialized = false;
    console.log('[BusinessEngine] Destroyed');
  }
}

export default BusinessEngine;
