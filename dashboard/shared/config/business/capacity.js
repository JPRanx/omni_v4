/**
 * Dashboard V3 - Capacity & Demand Thresholds
 *
 * Service capacity and demand management configuration
 * Defines acceptable service stress levels and performance standards
 *
 * Based on: InvestigationModal.js capacity analysis logic
 * Source: DashboardV3_Audit_538_Configs
 */

// ============================================
// SERVICE CAPACITY THRESHOLDS
// ============================================

export const serviceStress = {
  // Service stress percentage thresholds
  excellent: 15,      // < 15% stress = excellent capacity
  good: 25,           // < 25% stress = good capacity
  acceptable: 35,     // < 35% stress = acceptable
  critical: 50,       // < 50% stress = warning zone
  severe: 75,         // 75%+ = severe understaffing

  // Get status from stress percentage
  getStatus: (stressPercent) => {
    if (stressPercent < 15) return 'excellent';
    if (stressPercent < 25) return 'good';
    if (stressPercent < 35) return 'acceptable';
    if (stressPercent < 50) return 'warning';
    if (stressPercent < 75) return 'critical';
    return 'severe';
  },

  // Get color for stress level
  getColor: (stressPercent) => {
    if (stressPercent < 25) return 'success';
    if (stressPercent < 50) return 'warning';
    return 'critical';
  },
};

// ============================================
// ORDER FULFILLMENT STANDARDS
// ============================================

export const fulfillmentStandards = {
  // Pass rate thresholds (percentage of orders meeting time standards)
  excellent: 90,      // 90%+ = excellent
  good: 85,           // 85-90% = good
  acceptable: 80,     // 80-85% = acceptable
  warning: 70,        // 70-80% = warning
  critical: 60,       // < 60% = critical

  // Get status from pass rate
  getStatus: (passRate) => {
    if (passRate >= 90) return 'excellent';
    if (passRate >= 85) return 'good';
    if (passRate >= 80) return 'acceptable';
    if (passRate >= 70) return 'warning';
    if (passRate >= 60) return 'poor';
    return 'critical';
  },

  // Get color for pass rate
  getColor: (passRate) => {
    if (passRate >= 85) return 'success';
    if (passRate >= 70) return 'warning';
    return 'critical';
  },
};

// ============================================
// SERVICE CHANNEL STANDARDS
// ============================================

export const channels = {
  // Tables (dine-in) service standards
  tables: {
    targetTime: 15,        // Minutes - ideal table service time
    maxTime: 20,           // Minutes - acceptable maximum
    criticalTime: 25,      // Minutes - critical threshold
  },

  // Drive-thru service standards
  driveThru: {
    targetTime: 3,         // Minutes - ideal drive-thru time
    maxTime: 5,            // Minutes - acceptable maximum
    criticalTime: 7,       // Minutes - critical threshold
  },

  // To-go orders service standards
  toGo: {
    targetTime: 10,        // Minutes - ideal to-go prep time
    maxTime: 15,           // Minutes - acceptable maximum
    criticalTime: 20,      // Minutes - critical threshold
  },

  // Get status for service time
  getStatus: (actualTime, channel) => {
    const standard = channels[channel];
    if (!standard) return 'unknown';

    if (actualTime <= standard.targetTime) return 'excellent';
    if (actualTime <= standard.maxTime) return 'good';
    if (actualTime <= standard.criticalTime) return 'acceptable';
    return 'critical';
  },
};

// ============================================
// SHIFT ANALYSIS
// ============================================

export const shifts = {
  // Shift definitions
  morning: {
    label: 'Morning Shift',
    startHour: 6,         // 6 AM
    endHour: 14,          // 2 PM
    peakHours: [11, 12, 13], // 11 AM - 1 PM
  },

  evening: {
    label: 'Evening Shift',
    startHour: 14,        // 2 PM
    endHour: 22,          // 10 PM
    peakHours: [17, 18, 19], // 5 PM - 7 PM
  },

  // Determine shift from hour
  getShift: (hour) => {
    if (hour >= 6 && hour < 14) return 'morning';
    if (hour >= 14 && hour < 22) return 'evening';
    return 'overnight';
  },

  // Check if hour is peak time
  isPeakHour: (hour, shift) => {
    const shiftConfig = shifts[shift];
    return shiftConfig && shiftConfig.peakHours.includes(hour);
  },
};

// ============================================
// CAPACITY CALCULATIONS
// ============================================

export const calculations = {
  /**
   * Calculate service stress percentage
   * @param {number} orders - Number of orders
   * @param {number} capacity - Service capacity
   * @returns {number} Stress percentage (0-100+)
   */
  calculateStress: (orders, capacity) => {
    if (capacity === 0) return 100;
    return ((orders / capacity) * 100).toFixed(1);
  },

  /**
   * Calculate pass rate from passed/failed counts
   * @param {number} passed - Orders meeting standard
   * @param {number} total - Total orders
   * @returns {number} Pass rate percentage (0-100)
   */
  calculatePassRate: (passed, total) => {
    if (total === 0) return 0;
    return ((passed / total) * 100).toFixed(1);
  },

  /**
   * Determine if order meets time standard
   * @param {number} actualTime - Actual service time
   * @param {string} channel - Service channel (tables, driveThru, toGo)
   * @returns {boolean} True if meets standard
   */
  meetsStandard: (actualTime, channel) => {
    const standard = channels[channel];
    return standard ? actualTime <= standard.maxTime : false;
  },
};

// ============================================
// TIMESLOT CONFIGURATION
// ============================================

export const timeslots = {
  // Hourly slot duration
  slotDuration: 60,     // Minutes

  // Analysis window
  hoursPerDay: 24,

  // Default capacity per hour (can be overridden per restaurant)
  defaultCapacity: {
    tables: 50,         // 50 table orders per hour
    driveThru: 100,     // 100 drive-thru orders per hour
    toGo: 30,           // 30 to-go orders per hour
  },

  // Generate hourly slots for a day
  generateSlots: () => {
    return Array.from({ length: 24 }, (_, hour) => ({
      hour,
      label: `${hour === 0 ? 12 : hour > 12 ? hour - 12 : hour}${hour < 12 ? 'AM' : 'PM'}`,
      shift: shifts.getShift(hour),
    }));
  },
};

// ============================================
// COMPOSITE CAPACITY SCORE
// ============================================

export const capacityScore = {
  // Weights for capacity health calculation
  weights: {
    passRate: 0.50,       // 50% - Most important
    serviceStress: 0.30,  // 30% - Second most important
    channelBalance: 0.20, // 20% - Channel distribution
  },

  /**
   * Calculate overall capacity health score (0-100)
   * @param {Object} metrics - Capacity metrics
   * @returns {number} Health score
   */
  calculate: (metrics) => {
    const passRateScore = metrics.passRate || 0;

    // Invert stress (lower stress = higher score)
    const stressScore = Math.max(0, 100 - metrics.serviceStress);

    // Channel balance (how evenly distributed orders are)
    const channelScore = metrics.channelBalance || 75; // Default to 75

    return (
      passRateScore * capacityScore.weights.passRate +
      stressScore * capacityScore.weights.serviceStress +
      channelScore * capacityScore.weights.channelBalance
    );
  },

  // Get grade from capacity score
  getGrade: (score) => {
    if (score >= 90) return { label: 'A+', status: 'excellent' };
    if (score >= 85) return { label: 'A', status: 'excellent' };
    if (score >= 80) return { label: 'B', status: 'good' };
    if (score >= 70) return { label: 'C', status: 'acceptable' };
    if (score >= 60) return { label: 'D', status: 'poor' };
    return { label: 'F', status: 'critical' };
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  serviceStress,
  fulfillmentStandards,
  channels,
  shifts,
  calculations,
  timeslots,
  capacityScore,

  // Metadata
  totalConfigs: 27,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
