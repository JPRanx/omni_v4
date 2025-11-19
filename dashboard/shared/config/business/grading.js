/**
 * Dashboard V3 - Grading System
 *
 * Complete grading configuration based on comprehensive audit
 * Total Grade Levels: 5 (A+ to F)
 *
 * Breakdown:
 * - Grade Definitions: 5 levels with thresholds
 * - Visual Styling: 5 color/badge mappings
 * - Score Calculations: 4 scoring methods
 * - Performance Labels: 5 descriptive labels
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (implicit grading logic)
 * - Metric evaluation and status assignment
 */

import { statusColors } from './thresholds.js';

// ============================================
// GRADE DEFINITIONS (5 levels)
// A+ to F with score ranges and properties
// ============================================

export const grades = {
  aPlus: {
    label: 'A+',
    min: 95,
    max: 100,
    status: 'excellent',
    description: 'Outstanding Performance',
    color: '#16A34A',         // green-600
    bgColor: '#F0FDF4',       // green-50
    borderColor: '#16A34A',   // green-600
    textColor: '#15803D',     // green-700
    badge: 'success',
    emoji: '🌟',
  },

  a: {
    label: 'A',
    min: 90,
    max: 94,
    status: 'excellent',
    description: 'Excellent Performance',
    color: '#16A34A',         // green-600
    bgColor: '#F0FDF4',       // green-50
    borderColor: '#22C55E',   // green-500
    textColor: '#15803D',     // green-700
    badge: 'success',
    emoji: '✨',
  },

  b: {
    label: 'B',
    min: 80,
    max: 89,
    status: 'good',
    description: 'Good Performance',
    color: '#0891B2',         // cyan-600
    bgColor: '#ECFEFF',       // cyan-50
    borderColor: '#06B6D4',   // cyan-500
    textColor: '#0E7490',     // cyan-700
    badge: 'info',
    emoji: '👍',
  },

  c: {
    label: 'C',
    min: 70,
    max: 79,
    status: 'acceptable',
    description: 'Acceptable Performance',
    color: '#6B7280',         // gray-500
    bgColor: '#F9FAFB',       // gray-50
    borderColor: '#9CA3AF',   // gray-400
    textColor: '#374151',     // gray-700
    badge: 'normal',
    emoji: '😐',
  },

  d: {
    label: 'D',
    min: 60,
    max: 69,
    status: 'poor',
    description: 'Below Average Performance',
    color: '#F59E0B',         // amber-500
    bgColor: '#FFFBEB',       // amber-50
    borderColor: '#F59E0B',   // amber-500
    textColor: '#B45309',     // amber-700
    badge: 'warning',
    emoji: '⚠️',
  },

  f: {
    label: 'F',
    min: 0,
    max: 59,
    status: 'critical',
    description: 'Failing Performance',
    color: '#DC2626',         // red-600
    bgColor: '#FEF2F2',       // red-50
    borderColor: '#DC2626',   // red-600
    textColor: '#991B1B',     // red-800
    badge: 'critical',
    emoji: '🚨',
  },
};

// ============================================
// GRADE CALCULATION METHODS (4 methods)
// ============================================

export const calculate = {
  /**
   * Get grade from numeric score
   * @param {number} score - Score value (0-100)
   * @returns {Object} Grade object with all properties
   */
  fromScore: (score) => {
    if (score >= 95) return grades.aPlus;
    if (score >= 90) return grades.a;
    if (score >= 80) return grades.b;
    if (score >= 70) return grades.c;
    if (score >= 60) return grades.d;
    return grades.f;
  },

  /**
   * Calculate grade from metrics (sales-focused)
   * @param {Object} metrics - Metrics object
   * @param {number} metrics.sales - Sales value
   * @param {number} metrics.laborPercent - Labor cost percentage
   * @param {number} metrics.profitMargin - Profit margin percentage
   * @returns {Object} Grade object
   */
  fromMetrics: (metrics) => {
    const { sales, laborPercent, profitMargin } = metrics;

    // Sales score (0-40 points)
    let salesScore = 0;
    if (sales >= 50000) salesScore = 40;
    else if (sales >= 30000) salesScore = 32;
    else if (sales >= 20000) salesScore = 24;
    else if (sales >= 10000) salesScore = 16;
    else salesScore = 8;

    // Labor score (0-30 points, inverted - lower is better)
    let laborScore = 0;
    if (laborPercent <= 25) laborScore = 30;
    else if (laborPercent <= 30) laborScore = 24;
    else if (laborPercent <= 35) laborScore = 18;
    else if (laborPercent <= 40) laborScore = 12;
    else laborScore = 6;

    // Profit score (0-30 points)
    let profitScore = 0;
    if (profitMargin >= 20) profitScore = 30;
    else if (profitMargin >= 15) profitScore = 24;
    else if (profitMargin >= 10) profitScore = 18;
    else if (profitMargin >= 5) profitScore = 12;
    else profitScore = 6;

    const totalScore = salesScore + laborScore + profitScore;
    return calculate.fromScore(totalScore);
  },

  /**
   * Calculate grade from percentage (simple conversion)
   * @param {number} percentage - Percentage value (0-100)
   * @returns {Object} Grade object
   */
  fromPercentage: (percentage) => {
    return calculate.fromScore(percentage);
  },

  /**
   * Calculate weighted grade from multiple scores
   * @param {Object} scores - Score object with weights
   * @returns {Object} Grade object
   */
  weighted: (scores) => {
    const {
      sales = { value: 0, weight: 0.4 },
      labor = { value: 0, weight: 0.3 },
      profit = { value: 0, weight: 0.3 },
    } = scores;

    const totalScore =
      sales.value * sales.weight +
      labor.value * labor.weight +
      profit.value * profit.weight;

    return calculate.fromScore(totalScore);
  },
};

// ============================================
// GRADE STYLING (5 style generators)
// ============================================

export const styling = {
  /**
   * Get badge class for grade
   * @param {Object} grade - Grade object
   * @returns {string} Tailwind badge classes
   */
  getBadgeClass: (grade) => {
    return `px-3 py-1 rounded-full text-sm font-medium ${grade.bgColor} ${grade.textColor}`;
  },

  /**
   * Get border class for grade
   * @param {Object} grade - Grade object
   * @returns {string} Tailwind border classes
   */
  getBorderClass: (grade) => {
    return `border-2 border-[${grade.borderColor}]`;
  },

  /**
   * Get background class for grade
   * @param {Object} grade - Grade object
   * @returns {string} Tailwind background classes
   */
  getBackgroundClass: (grade) => {
    return `bg-[${grade.bgColor}]`;
  },

  /**
   * Get text color class for grade
   * @param {Object} grade - Grade object
   * @returns {string} Tailwind text color classes
   */
  getTextClass: (grade) => {
    return `text-[${grade.textColor}]`;
  },

  /**
   * Get complete card styling for grade
   * @param {Object} grade - Grade object
   * @returns {Object} Complete style object
   */
  getCardStyle: (grade) => {
    return {
      backgroundColor: grade.bgColor,
      borderColor: grade.borderColor,
      color: grade.textColor,
      borderWidth: '2px',
      borderStyle: 'solid',
    };
  },
};

// ============================================
// GRADE DISPLAY (5 display formats)
// ============================================

export const display = {
  /**
   * Get grade label with emoji
   * @param {Object} grade - Grade object
   * @returns {string} "A+ 🌟"
   */
  withEmoji: (grade) => {
    return `${grade.label} ${grade.emoji}`;
  },

  /**
   * Get grade with description
   * @param {Object} grade - Grade object
   * @returns {string} "A+ - Outstanding Performance"
   */
  withDescription: (grade) => {
    return `${grade.label} - ${grade.description}`;
  },

  /**
   * Get grade with score range
   * @param {Object} grade - Grade object
   * @returns {string} "A+ (95-100)"
   */
  withRange: (grade) => {
    return `${grade.label} (${grade.min}-${grade.max})`;
  },

  /**
   * Get full grade display
   * @param {Object} grade - Grade object
   * @param {number} score - Actual score
   * @returns {string} "A+ 🌟 (97) - Outstanding Performance"
   */
  full: (grade, score) => {
    return `${grade.label} ${grade.emoji} (${score}) - ${grade.description}`;
  },

  /**
   * Get badge HTML
   * @param {Object} grade - Grade object
   * @returns {string} HTML string for badge
   */
  badge: (grade) => {
    const badgeClass = styling.getBadgeClass(grade);
    return `<span class="${badgeClass}">${grade.label}</span>`;
  },
};

// ============================================
// GRADE COMPARISONS (4 comparison methods)
// ============================================

export const compare = {
  /**
   * Check if grade is passing (C or better)
   * @param {Object} grade - Grade object
   * @returns {boolean} True if passing
   */
  isPassing: (grade) => {
    return grade.min >= grades.c.min;
  },

  /**
   * Check if grade is excellent (A or A+)
   * @param {Object} grade - Grade object
   * @returns {boolean} True if excellent
   */
  isExcellent: (grade) => {
    return grade.min >= grades.a.min;
  },

  /**
   * Check if grade is failing (F)
   * @param {Object} grade - Grade object
   * @returns {boolean} True if failing
   */
  isFailing: (grade) => {
    return grade.label === 'F';
  },

  /**
   * Compare two grades
   * @param {Object} grade1 - First grade
   * @param {Object} grade2 - Second grade
   * @returns {number} -1 if grade1 < grade2, 0 if equal, 1 if grade1 > grade2
   */
  compareTo: (grade1, grade2) => {
    if (grade1.min > grade2.min) return 1;
    if (grade1.min < grade2.min) return -1;
    return 0;
  },
};

// ============================================
// GRADE UTILITIES
// ============================================

export const utils = {
  /**
   * Get all grades as array
   * @returns {Array<Object>} Array of all grade objects
   */
  getAllGrades: () => {
    return [grades.aPlus, grades.a, grades.b, grades.c, grades.d, grades.f];
  },

  /**
   * Get grade by label
   * @param {string} label - Grade label ('A+', 'A', 'B', 'C', 'D', 'F')
   * @returns {Object|null} Grade object or null
   */
  getByLabel: (label) => {
    return utils.getAllGrades().find(g => g.label === label) || null;
  },

  /**
   * Get passing grades only
   * @returns {Array<Object>} Array of passing grades
   */
  getPassingGrades: () => {
    return utils.getAllGrades().filter(g => compare.isPassing(g));
  },

  /**
   * Calculate grade distribution from scores
   * @param {Array<number>} scores - Array of scores
   * @returns {Object} Distribution object { A+: count, A: count, ... }
   */
  getDistribution: (scores) => {
    const distribution = {
      'A+': 0,
      'A': 0,
      'B': 0,
      'C': 0,
      'D': 0,
      'F': 0,
    };

    scores.forEach(score => {
      const grade = calculate.fromScore(score);
      distribution[grade.label]++;
    });

    return distribution;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  grades,
  calculate,
  styling,
  display,
  compare,
  utils,

  // Metadata
  totalLevels: 5,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
