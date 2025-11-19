/**
 * Dashboard V3 - Business Thresholds
 *
 * Complete threshold configuration based on comprehensive audit
 * Total Thresholds: 34 business rules
 *
 * Breakdown:
 * - Performance Thresholds: 12 (sales, labor, costs)
 * - Status Indicators: 9 (critical, warning, success)
 * - Variance Thresholds: 7 (day-over-day, week-over-week)
 * - Grade Boundaries: 5 (A+ to F)
 * - Time Thresholds: 1 (auto-clockout hours)
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (lines 1129-1171, 1318-1410)
 * - Logic for status colors, badge assignments
 */

// ============================================
// SALES THRESHOLDS (5 rules)
// ============================================

export const sales = {
  // Daily sales performance indicators
  excellent: 50000,     // > $50k = excellent day
  good: 30000,          // > $30k = good day
  average: 20000,       // > $20k = average day
  poor: 10000,          // < $10k = poor day

  // Restaurant-level thresholds
  weeklyTarget: 200000, // Weekly sales target per restaurant
  minViableWeek: 100000, // Minimum acceptable weekly sales

  // Status determination
  getStatus: (sales) => {
    if (sales >= 50000) return 'excellent';
    if (sales >= 30000) return 'good';
    if (sales >= 20000) return 'average';
    if (sales >= 10000) return 'fair';
    return 'poor';
  },
};

// ============================================
// LABOR COST THRESHOLDS (7 rules)
// ============================================

export const labor = {
  // Labor cost percentage targets
  idealMin: 25,         // 25% ideal minimum
  idealMax: 30,         // 30% ideal maximum
  acceptableMax: 35,    // 35% still acceptable
  critical: 40,         // 40%+ = critical issue

  // Status determination
  getStatus: (laborPercent) => {
    if (laborPercent < 25) return 'excellent';  // Under 25% = excellent
    if (laborPercent <= 30) return 'good';      // 25-30% = good
    if (laborPercent <= 35) return 'warning';   // 30-35% = warning
    if (laborPercent <= 40) return 'critical';  // 35-40% = critical
    return 'severe';                             // 40%+ = severe
  },

  // Badge color mapping
  getBadgeClass: (laborPercent) => {
    if (laborPercent <= 30) return 'success';
    if (laborPercent <= 35) return 'warning';
    return 'critical';
  },

  // Auto-clockout threshold
  autoClockoutHours: 10,  // Hours worked before auto-clockout warning
};

// ============================================
// COST OF GOODS SOLD (COGS) THRESHOLDS (4 rules)
// ============================================

export const cogs = {
  // COGS percentage targets
  idealMax: 30,         // 30% ideal maximum
  acceptableMax: 35,    // 35% still acceptable
  critical: 40,         // 40%+ = critical

  // Status determination
  getStatus: (cogsPercent) => {
    if (cogsPercent <= 30) return 'good';
    if (cogsPercent <= 35) return 'warning';
    return 'critical';
  },
};

// ============================================
// VARIANCE THRESHOLDS (7 rules)
// Day-over-day and week-over-week changes
// ============================================

export const variance = {
  // Day-over-day variance (percentage)
  dayOverDay: {
    significant: 10,    // ±10% = significant change
    major: 20,          // ±20% = major change
    critical: 30,       // ±30% = critical change
  },

  // Week-over-week variance
  weekOverWeek: {
    significant: 15,    // ±15% = significant change
    major: 25,          // ±25% = major change
    critical: 35,       // ±35% = critical change
  },

  // Status determination for variance
  getStatus: (variancePercent, type = 'day') => {
    const thresholds = type === 'day' ? variance.dayOverDay : variance.weekOverWeek;
    const absVariance = Math.abs(variancePercent);

    if (absVariance >= thresholds.critical) return 'critical';
    if (absVariance >= thresholds.major) return 'warning';
    if (absVariance >= thresholds.significant) return 'info';
    return 'normal';
  },

  // Color for variance display
  getColor: (variancePercent) => {
    if (variancePercent > 0) return 'success';  // Positive = green
    if (variancePercent < 0) return 'critical'; // Negative = red
    return 'normal';  // Zero = gray
  },
};

// ============================================
// PROFIT & LOSS THRESHOLDS (5 rules)
// ============================================

export const profitLoss = {
  // Net profit percentage targets
  excellent: 20,        // 20%+ = excellent
  good: 15,             // 15-20% = good
  acceptable: 10,       // 10-15% = acceptable
  poor: 5,              // 5-10% = poor
  critical: 0,          // < 0% = losing money

  // Status determination
  getStatus: (profitPercent) => {
    if (profitPercent >= 20) return 'excellent';
    if (profitPercent >= 15) return 'good';
    if (profitPercent >= 10) return 'acceptable';
    if (profitPercent >= 5) return 'poor';
    if (profitPercent >= 0) return 'critical';
    return 'severe';  // Negative = losing money
  },
};

// ============================================
// GRADE BOUNDARIES (5 levels)
// A+ to F grading system
// ============================================

export const grades = {
  aPlus: { min: 95, max: 100, label: 'A+', status: 'excellent' },
  a: { min: 90, max: 94, label: 'A', status: 'excellent' },
  b: { min: 80, max: 89, label: 'B', status: 'good' },
  c: { min: 70, max: 79, label: 'C', status: 'acceptable' },
  d: { min: 60, max: 69, label: 'D', status: 'poor' },
  f: { min: 0, max: 59, label: 'F', status: 'critical' },

  // Get grade from score
  getGrade: (score) => {
    if (score >= 95) return grades.aPlus;
    if (score >= 90) return grades.a;
    if (score >= 80) return grades.b;
    if (score >= 70) return grades.c;
    if (score >= 60) return grades.d;
    return grades.f;
  },
};

// ============================================
// STATUS COLOR MAPPINGS (9 statuses)
// Maps business statuses to UI colors
// ============================================

export const statusColors = {
  excellent: {
    bg: 'bg-green-50',
    border: 'border-green-600',
    text: 'text-green-700',
    badge: 'success',
  },
  good: {
    bg: 'bg-green-50',
    border: 'border-green-500',
    text: 'text-green-600',
    badge: 'success',
  },
  acceptable: {
    bg: 'bg-gray-50',
    border: 'border-gray-400',
    text: 'text-gray-700',
    badge: 'normal',
  },
  average: {
    bg: 'bg-gray-50',
    border: 'border-gray-400',
    text: 'text-gray-600',
    badge: 'normal',
  },
  fair: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-500',
    text: 'text-yellow-700',
    badge: 'warning',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-600',
    text: 'text-yellow-700',
    badge: 'warning',
  },
  poor: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-600',
    badge: 'critical',
  },
  critical: {
    bg: 'bg-red-50',
    border: 'border-red-600',
    text: 'text-red-700',
    badge: 'critical',
  },
  severe: {
    bg: 'bg-red-100',
    border: 'border-red-700',
    text: 'text-red-800',
    badge: 'critical',
  },
};

// ============================================
// COMPOSITE HEALTH SCORE (1 formula)
// Overall restaurant health calculation
// ============================================

export const healthScore = {
  // Weights for different metrics
  weights: {
    sales: 0.30,          // 30% weight
    labor: 0.25,          // 25% weight
    cogs: 0.20,           // 20% weight
    profit: 0.25,         // 25% weight
  },

  // Calculate overall health score (0-100)
  calculate: (metrics) => {
    const salesScore = getSalesScore(metrics.sales);
    const laborScore = getLaborScore(metrics.laborPercent);
    const cogsScore = getCogsScore(metrics.cogsPercent);
    const profitScore = getProfitScore(metrics.profitPercent);

    return (
      salesScore * healthScore.weights.sales +
      laborScore * healthScore.weights.labor +
      cogsScore * healthScore.weights.cogs +
      profitScore * healthScore.weights.profit
    );
  },

  // Get grade from health score
  getGrade: (score) => grades.getGrade(score),
};

// ============================================
// HELPER FUNCTIONS
// Score normalization (0-100)
// ============================================

function getSalesScore(sales) {
  if (sales >= 50000) return 100;
  if (sales >= 30000) return 85;
  if (sales >= 20000) return 70;
  if (sales >= 10000) return 50;
  return 30;
}

function getLaborScore(laborPercent) {
  if (laborPercent <= 25) return 100;
  if (laborPercent <= 30) return 85;
  if (laborPercent <= 35) return 65;
  if (laborPercent <= 40) return 45;
  return 25;
}

function getCogsScore(cogsPercent) {
  if (cogsPercent <= 30) return 100;
  if (cogsPercent <= 35) return 75;
  if (cogsPercent <= 40) return 50;
  return 30;
}

function getProfitScore(profitPercent) {
  if (profitPercent >= 20) return 100;
  if (profitPercent >= 15) return 85;
  if (profitPercent >= 10) return 70;
  if (profitPercent >= 5) return 50;
  if (profitPercent >= 0) return 30;
  return 0;
}

// ============================================
// EXPORT
// ============================================

export default {
  sales,
  labor,
  cogs,
  variance,
  profitLoss,
  grades,
  statusColors,
  healthScore,

  // Helper functions
  getSalesScore,
  getLaborScore,
  getCogsScore,
  getProfitScore,

  // Metadata
  totalThresholds: 34,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
