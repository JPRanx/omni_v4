/**
 * Dashboard V3 - Conflict Resolution
 *
 * Documents and resolves inconsistencies found in comprehensive audit
 * of Dashboard V2 and original dashboard_generator.py
 *
 * Total Conflicts Identified: 8
 * Audit Date: 2025-11-01
 * Total Configs: 538
 */

export const conflicts = {
  // ========================================
  // COLOR CONFLICTS (1)
  // ========================================

  /**
   * bronze_dust Color Mismatch
   * - dashboard_generator.py uses: #8C7355
   * - DashboardV2 uses: #B89968
   * RESOLUTION: Use #B89968 (V2 value - more vibrant, better contrast)
   */
  bronze_dust: '#B89968',


  // ========================================
  // UNIT CONFLICTS (1)
  // ========================================

  /**
   * Font Size Units
   * - dashboard_generator.py uses: px (46px, 30px, 24px, etc.)
   * - theme.css uses: rem (0.75rem, 1rem, 1.5rem, etc.)
   * RESOLUTION: Standardize to rem (better accessibility, responsive)
   */
  preferredUnit: 'rem',


  // ========================================
  // SPACING CONFLICTS (1)
  // ========================================

  /**
   * Container Max Width
   * - index.html uses: 1280px
   * - dashboard_generator.py uses: 1600px
   * RESOLUTION: Use 1600px (accommodates more data, matches original design)
   */
  containerMaxWidth: '1600px',


  // ========================================
  // SHADOW CONFLICTS (1)
  // ========================================

  /**
   * Shadow Definition Method
   * - Some components use CSS variables: var(--shadow-xl)
   * - Others use inline rgba: rgba(61, 49, 40, 0.1)
   * RESOLUTION: Use rgba() with CSS variables for flexibility
   * Example: box-shadow: var(--shadow-xl);
   */
  shadowOpacity: 'rgba',


  // ========================================
  // GRADIENT CONFLICTS (1)
  // ========================================

  /**
   * Gradient Angle Syntax
   * - Some use: 135deg
   * - Some use: "to bottom right"
   * - Some use: 90deg
   * RESOLUTION: Standardize to 135deg (diagonal, consistent direction)
   */
  gradientAngle: '135deg',


  // ========================================
  // BORDER CONFLICTS (1)
  // ========================================

  /**
   * Border Opacity Range
   * - Found range: 0.08 to 0.35 with no clear pattern
   * RESOLUTION: Use component-based values
   * - Headers: 0.15
   * - Cards: 0.12
   * - Tables: 0.08
   * - Critical: 0.2+
   */
  borderOpacityPattern: 'component-based',


  // ========================================
  // TRANSITION CONFLICTS (1)
  // ========================================

  /**
   * Transition Duration Definition
   * - Some use CSS variables: var(--transition-smooth)
   * - Others hardcode: 300ms
   * RESOLUTION: Always use CSS variables for consistency
   */
  transitionSource: 'css-vars',


  // ========================================
  // GRID CONFLICTS (1)
  // ========================================

  /**
   * Grid Gap Units
   * - Mix of Tailwind classes: gap-4, gap-6
   * - Mix of CSS values: gap: 22px, gap: 26px
   * RESOLUTION: Use Tailwind classes for consistency with design system
   * Fallback to px only when exact custom value needed
   */
  gapUnit: 'tailwind',


  // ========================================
  // METADATA
  // ========================================

  resolutionDate: '2025-11-01',
  auditReference: 'DashboardV3_Audit_538_Configs.md',
  resolvedBy: 'Claude Code',
  totalConflicts: 8,
  impactedFiles: 12,


  // ========================================
  // USAGE NOTES
  // ========================================

  /**
   * How to use this file:
   *
   * import { conflicts } from '../resolution.js';
   *
   * // Use resolved values
   * const brandColor = conflicts.bronze_dust;  // '#B89968'
   * const maxWidth = conflicts.containerMaxWidth; // '1600px'
   *
   * // Check resolution approach
   * if (conflicts.preferredUnit === 'rem') {
   *   // Convert px to rem
   * }
   */
};

const resolution = {
  conflicts,
};

export default resolution;
