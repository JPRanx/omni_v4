/**
 * Dashboard V3 - Status Definitions
 *
 * Complete status configuration based on comprehensive audit
 * Total Status Types: 9
 *
 * Breakdown:
 * - Performance Statuses: 5 (excellent, good, acceptable, poor, critical)
 * - Indicator Statuses: 3 (success, warning, critical)
 * - Special Statuses: 1 (info)
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (status badge assignments)
 * - Metric evaluation and coloring logic
 */

import { status as statusColors } from '../theme/colors.js';
import { badges } from '../theme/colors.js';

// ============================================
// STATUS DEFINITIONS (9 types)
// Complete status objects with styling
// ============================================

export const statuses = {
  // Performance Statuses
  excellent: {
    name: 'excellent',
    label: 'Excellent',
    description: 'Outstanding performance, exceeding targets',
    priority: 5,
    color: statusColors.success.rgb,
    bgColor: statusColors.success.bg,
    borderColor: statusColors.success.border,
    textColor: statusColors.success.text,
    badge: badges.success,
    icon: '🌟',
    cssClass: 'status-excellent',
    tailwind: 'border-green-600 bg-green-50 text-green-700',
  },

  good: {
    name: 'good',
    label: 'Good',
    description: 'Good performance, meeting targets',
    priority: 4,
    color: statusColors.success.rgb,
    bgColor: statusColors.success.bg,
    borderColor: statusColors.success.border,
    textColor: statusColors.success.text,
    badge: badges.success,
    icon: '✅',
    cssClass: 'status-good',
    tailwind: 'border-green-500 bg-green-50 text-green-600',
  },

  acceptable: {
    name: 'acceptable',
    label: 'Acceptable',
    description: 'Acceptable performance, within normal range',
    priority: 3,
    color: statusColors.normal.rgb,
    bgColor: statusColors.normal.bg,
    borderColor: statusColors.normal.border,
    textColor: statusColors.normal.text,
    badge: badges.normal,
    icon: '😐',
    cssClass: 'status-acceptable',
    tailwind: 'border-gray-300 bg-gray-50 text-gray-700',
  },

  average: {
    name: 'average',
    label: 'Average',
    description: 'Average performance, room for improvement',
    priority: 3,
    color: statusColors.normal.rgb,
    bgColor: statusColors.normal.bg,
    borderColor: statusColors.normal.border,
    textColor: statusColors.normal.text,
    badge: badges.normal,
    icon: '➖',
    cssClass: 'status-average',
    tailwind: 'border-gray-300 bg-gray-50 text-gray-600',
  },

  fair: {
    name: 'fair',
    label: 'Fair',
    description: 'Fair performance, needs attention',
    priority: 2,
    color: statusColors.warning.rgb,
    bgColor: statusColors.warning.bg,
    borderColor: statusColors.warning.border,
    textColor: statusColors.warning.text,
    badge: badges.warning,
    icon: '⚠️',
    cssClass: 'status-fair',
    tailwind: 'border-yellow-500 bg-yellow-50 text-yellow-700',
  },

  poor: {
    name: 'poor',
    label: 'Poor',
    description: 'Poor performance, requires immediate attention',
    priority: 1,
    color: statusColors.critical.rgb,
    bgColor: statusColors.critical.bg,
    borderColor: statusColors.critical.border,
    textColor: statusColors.critical.text,
    badge: badges.critical,
    icon: '⚠️',
    cssClass: 'status-poor',
    tailwind: 'border-red-500 bg-red-50 text-red-600',
  },

  // Indicator Statuses
  success: {
    name: 'success',
    label: 'Success',
    description: 'Positive outcome or achievement',
    priority: 5,
    color: statusColors.success.rgb,
    bgColor: statusColors.success.bg,
    borderColor: statusColors.success.border,
    textColor: statusColors.success.text,
    badge: badges.success,
    icon: '✅',
    cssClass: 'status-success',
    tailwind: 'border-green-600 bg-green-50 text-green-700',
  },

  warning: {
    name: 'warning',
    label: 'Warning',
    description: 'Caution advised, approaching threshold',
    priority: 2,
    color: statusColors.warning.rgb,
    bgColor: statusColors.warning.bg,
    borderColor: statusColors.warning.border,
    textColor: statusColors.warning.text,
    badge: badges.warning,
    icon: '⚠️',
    cssClass: 'status-warning',
    tailwind: 'border-yellow-600 bg-yellow-50 text-yellow-700',
  },

  critical: {
    name: 'critical',
    label: 'Critical',
    description: 'Critical issue, immediate action required',
    priority: 0,
    color: statusColors.critical.rgb,
    bgColor: statusColors.critical.bg,
    borderColor: statusColors.critical.border,
    textColor: statusColors.critical.text,
    badge: badges.critical,
    icon: '🚨',
    cssClass: 'status-critical',
    tailwind: 'border-red-600 bg-red-50 text-red-700',
  },

  // Special Statuses
  info: {
    name: 'info',
    label: 'Info',
    description: 'Informational status',
    priority: 3,
    color: statusColors.info.rgb,
    bgColor: statusColors.info.bg,
    borderColor: statusColors.info.border,
    textColor: statusColors.info.text,
    badge: badges.info,
    icon: 'ℹ️',
    cssClass: 'status-info',
    tailwind: 'border-blue-500 bg-blue-50 text-blue-700',
  },

  normal: {
    name: 'normal',
    label: 'Normal',
    description: 'Normal status, no action needed',
    priority: 3,
    color: statusColors.normal.rgb,
    bgColor: statusColors.normal.bg,
    borderColor: statusColors.normal.border,
    textColor: statusColors.normal.text,
    badge: badges.normal,
    icon: '➖',
    cssClass: 'status-normal',
    tailwind: 'border-gray-300 bg-gray-50 text-gray-700',
  },

  severe: {
    name: 'severe',
    label: 'Severe',
    description: 'Severe issue, urgent intervention required',
    priority: -1,
    color: statusColors.critical.rgb,
    bgColor: 'bg-red-100',
    borderColor: 'border-red-700',
    textColor: 'text-red-800',
    badge: badges.critical,
    icon: '🚨',
    cssClass: 'status-severe',
    tailwind: 'border-red-700 bg-red-100 text-red-800',
  },
};

// ============================================
// STATUS GETTERS (5 helper functions)
// ============================================

export const getters = {
  /**
   * Get status by name
   * @param {string} name - Status name
   * @returns {Object|null} Status object or null
   */
  byName: (name) => {
    return statuses[name] || null;
  },

  /**
   * Get status label
   * @param {string} name - Status name
   * @returns {string} Status label or empty string
   */
  getLabel: (name) => {
    const status = getters.byName(name);
    return status ? status.label : '';
  },

  /**
   * Get status icon
   * @param {string} name - Status name
   * @returns {string} Status icon or empty string
   */
  getIcon: (name) => {
    const status = getters.byName(name);
    return status ? status.icon : '';
  },

  /**
   * Get status badge class
   * @param {string} name - Status name
   * @returns {string} Badge CSS class
   */
  getBadgeClass: (name) => {
    const status = getters.byName(name);
    return status ? status.badge : badges.normal;
  },

  /**
   * Get status Tailwind classes
   * @param {string} name - Status name
   * @returns {string} Tailwind CSS classes
   */
  getTailwindClass: (name) => {
    const status = getters.byName(name);
    return status ? status.tailwind : statuses.normal.tailwind;
  },
};

// ============================================
// STATUS DETERMINATION (4 evaluators)
// Business logic to determine status
// ============================================

export const determine = {
  /**
   * Determine status from sales value
   * @param {number} sales - Sales value in dollars
   * @returns {string} Status name
   */
  fromSales: (sales) => {
    if (sales >= 50000) return 'excellent';
    if (sales >= 30000) return 'good';
    if (sales >= 20000) return 'average';
    if (sales >= 10000) return 'fair';
    return 'poor';
  },

  /**
   * Determine status from labor percentage
   * @param {number} laborPercent - Labor cost as percentage (0-100)
   * @returns {string} Status name
   */
  fromLabor: (laborPercent) => {
    if (laborPercent <= 25) return 'excellent';
    if (laborPercent <= 30) return 'good';
    if (laborPercent <= 35) return 'warning';
    if (laborPercent <= 40) return 'critical';
    return 'severe';
  },

  /**
   * Determine status from profit margin
   * @param {number} profitMargin - Profit margin as percentage (0-100)
   * @returns {string} Status name
   */
  fromProfit: (profitMargin) => {
    if (profitMargin >= 20) return 'excellent';
    if (profitMargin >= 15) return 'good';
    if (profitMargin >= 10) return 'acceptable';
    if (profitMargin >= 5) return 'poor';
    if (profitMargin >= 0) return 'critical';
    return 'severe';
  },

  /**
   * Determine status from variance
   * @param {number} variance - Variance percentage (can be negative)
   * @returns {string} Status name
   */
  fromVariance: (variance) => {
    const absVariance = Math.abs(variance);
    if (absVariance >= 30) return 'critical';
    if (absVariance >= 20) return 'warning';
    if (absVariance >= 10) return 'info';
    return 'normal';
  },
};

// ============================================
// STATUS COMPARISONS (3 comparison methods)
// ============================================

export const compare = {
  /**
   * Check if status is positive (excellent, good, success)
   * @param {string} statusName - Status name
   * @returns {boolean} True if positive
   */
  isPositive: (statusName) => {
    return ['excellent', 'good', 'success'].includes(statusName);
  },

  /**
   * Check if status is negative (poor, critical, severe)
   * @param {string} statusName - Status name
   * @returns {boolean} True if negative
   */
  isNegative: (statusName) => {
    return ['poor', 'critical', 'severe'].includes(statusName);
  },

  /**
   * Compare status priorities (higher priority = better)
   * @param {string} status1 - First status name
   * @param {string} status2 - Second status name
   * @returns {number} -1, 0, or 1
   */
  comparePriority: (status1, status2) => {
    const s1 = getters.byName(status1);
    const s2 = getters.byName(status2);
    if (!s1 || !s2) return 0;

    if (s1.priority > s2.priority) return 1;
    if (s1.priority < s2.priority) return -1;
    return 0;
  },
};

// ============================================
// STATUS UTILITIES
// ============================================

export const utils = {
  /**
   * Get all statuses as array
   * @returns {Array<Object>} Array of all status objects
   */
  getAllStatuses: () => {
    return Object.values(statuses);
  },

  /**
   * Get statuses by priority (highest first)
   * @returns {Array<Object>} Sorted array of status objects
   */
  getByPriority: () => {
    return utils.getAllStatuses().sort((a, b) => b.priority - a.priority);
  },

  /**
   * Get only performance statuses
   * @returns {Array<Object>} Array of performance status objects
   */
  getPerformanceStatuses: () => {
    return [
      statuses.excellent,
      statuses.good,
      statuses.acceptable,
      statuses.average,
      statuses.fair,
      statuses.poor,
    ];
  },

  /**
   * Get only indicator statuses
   * @returns {Array<Object>} Array of indicator status objects
   */
  getIndicatorStatuses: () => {
    return [
      statuses.success,
      statuses.warning,
      statuses.critical,
      statuses.info,
    ];
  },

  /**
   * Create status badge HTML
   * @param {string} statusName - Status name
   * @param {string} text - Optional custom text
   * @returns {string} HTML string for badge
   */
  createBadge: (statusName, text = null) => {
    const status = getters.byName(statusName);
    if (!status) return '';

    const displayText = text || status.label;
    return `<span class="${status.badge}">${status.icon} ${displayText}</span>`;
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  statuses,
  getters,
  determine,
  compare,
  utils,

  // Metadata
  totalTypes: 9,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
