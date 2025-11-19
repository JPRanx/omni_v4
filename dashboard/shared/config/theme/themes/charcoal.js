/**
 * Dashboard V3 - Charcoal Artist Theme
 *
 * A theme that transforms your dashboard into a charcoal artist's workspace
 * Every element feels hand-drawn on textured paper
 *
 * Design Philosophy:
 * - Rough, artistic edges like charcoal strokes
 * - Textured paper backgrounds with grain
 * - Smudged, organic borders
 * - No smooth transitions - immediate, tactile feel
 * - Pure monochrome - no color distractions
 * - Physical, analog aesthetic in a digital space
 *
 * Inspiration:
 * - Artist's sketchbook
 * - Charcoal figure drawing
 * - Architectural drafting paper
 * - Hand-drawn wireframes
 *
 * Version: 3.0.0
 * Date: 2025-11-01
 */

import { createTheme } from '../themeTemplate.js';

export const charcoalTheme = createTheme(
  // ============================================
  // THEME NAME
  // ============================================
  'Charcoal Artist',  // Transform your dashboard into an artist's sketchbook

  // ============================================
  // SEMANTIC COLORS - Pure Monochrome
  // ============================================
  {
    // ==========================================
    // TEXT HIERARCHY - Charcoal gradations
    // ==========================================

    text_primary: '#1A1A1A',
    // Deep charcoal black - Like pressed charcoal on paper
    // Main headers, important content
    // Maximum contrast for readability

    text_secondary: '#3A3A3A',
    // Medium charcoal - Like light charcoal strokes
    // Subheadings, descriptions
    // Clear hierarchy from primary

    text_muted: '#5A5A5A',
    // Light charcoal - Like smudged edges
    // Labels, metadata, annotations
    // Visible but not dominant

    text_disabled: '#9A9A9A',
    // Faded charcoal - Like erased marks
    // Inactive elements
    // Clearly non-interactive

    // ==========================================
    // BACKGROUNDS - Paper surfaces
    // ==========================================

    background_primary: '#F5F5F0',
    // Cream drawing paper - Natural, warm tone
    // Main canvas background
    // Reduces eye strain vs pure white

    background_card: '#FAFAF5',
    // Bright sketch paper - Clean sheets
    // Individual card backgrounds
    // Slightly brighter than main background

    background_elevated: '#FFFFFF',
    // Pure white - Fresh paper on top
    // Modals, overlays
    // Maximum contrast for focus

    background_hover: 'rgba(0, 0, 0, 0.03)',
    // Charcoal smudge - Subtle shading
    // Hover states
    // Barely visible, tactile feedback

    // ==========================================
    // BORDERS - Charcoal strokes
    // ==========================================

    border_strong: '#0A0A0A',
    // Dense charcoal - Heavy pressure stroke
    // Major divisions, emphasis
    // Near-black for maximum impact

    border_default: '#3A3A3A',
    // Medium charcoal - Normal pressure stroke
    // Standard borders, dividers
    // Most common border weight

    border_subtle: 'rgba(0, 0, 0, 0.15)',
    // Light charcoal - Barely-there line
    // Table rows, subtle separators
    // Provides structure without dominating

    // ==========================================
    // ACCENTS - Monochrome emphasis
    // ==========================================

    accent_primary: '#1A1A1A',
    // Deep charcoal - Primary brand stays monochrome
    // Buttons, active states
    // Maintains pure grayscale aesthetic

    accent_secondary: '#4A4A4A',
    // Mid-tone charcoal - Supporting accent
    // Secondary actions
    // Provides variety in grayscale

    accent_interactive: '#2A2A2A',
    // Dark charcoal - Clickable elements
    // Links, interactive text
    // Underlined for clarity

    // ==========================================
    // DASHBOARD-SPECIFIC - Data visualization
    // ==========================================

    dashboard_metric: '#0A0A0A',
    // Near-black charcoal - Important numbers
    // Revenue, KPIs, critical data
    // Maximum readability and emphasis

    dashboard_metricLabel: '#4A4A4A',
    // Medium gray - Labels don't compete
    // Metric descriptions
    // Clear hierarchy with values

    dashboard_sectionHeader: '#1A1A1A',
    // Deep charcoal - Section titles
    // Major divisions
    // Commands attention

    dashboard_tableHeader: '#2A2A2A',
    // Dark charcoal - Table headers
    // Column titles
    // Distinguished from data

    dashboard_tableRow: 'rgba(0, 0, 0, 0.02)',
    // Ultra-subtle shading - Zebra stripes
    // Alternating rows
    // Just enough to guide the eye

    dashboard_gradientStart: 'transparent',
    // No gradients - flat like paper
    // Maintains sketch aesthetic

    dashboard_gradientEnd: 'transparent',
    // No gradients - pure texture
    // Paper-like flatness

    // ==========================================
    // STATUS COLORS - Monochrome indicators
    // ==========================================
    // Status uses different charcoal densities instead of colors

    status: {
      success: {
        bg: 'rgba(50, 50, 50, 0.08)',     // Light charcoal shade
        text: '#2A2A2A',                   // Dark charcoal
        border: '#3A3A3A',                 // Medium charcoal
      },
      // Success uses medium-light charcoal tone

      warning: {
        bg: 'rgba(70, 70, 70, 0.08)',     // Slightly darker shade
        text: '#4A4A4A',                   // Medium charcoal
        border: '#5A5A5A',                 // Light charcoal
      },
      // Warning uses mid-tone charcoal

      error: {
        bg: 'rgba(30, 30, 30, 0.12)',     // Darker shade for emphasis
        text: '#1A1A1A',                   // Deep charcoal
        border: '#2A2A2A',                 // Dark charcoal
      },
      // Error uses darker charcoal for severity

      critical: {
        bg: 'rgba(20, 20, 20, 0.15)',     // Darkest shade
        text: '#0A0A0A',                   // Near-black charcoal
        border: '#1A1A1A',                 // Deep charcoal
      },
      // Critical uses deepest charcoal tones

      info: {
        bg: 'rgba(40, 40, 40, 0.06)',     // Subtle shade
        text: '#3A3A3A',                   // Medium-dark charcoal
        border: '#4A4A4A',                 // Medium charcoal
      },
      // Info uses neutral mid-tones

      normal: {
        bg: 'rgba(50, 50, 50, 0.04)',     // Very light shade
        text: '#3A3A3A',                   // Medium charcoal
        border: '#6A6A6A',                 // Light charcoal
      }
      // Normal uses lightest charcoal tones
    }
  },

  // ============================================
  // OPTIONAL ENHANCEMENTS
  // ============================================
  {
    // ==========================================
    // TYPOGRAPHY - Hand-drawn feel
    // ==========================================
    typography: {
      fontFamily: '"Courier Prime", "Courier New", "Courier", monospace',
      // Typewriter/hand-drawn aesthetic
      // Monospace mimics hand-lettering consistency
      // Available via Google Fonts

      scale: 1.0,
      // Standard scale - no enlargement needed
      // Courier Prime is naturally readable
    },

    // ==========================================
    // ANIMATIONS - Instant response
    // ==========================================
    animations: {
      duration: '0ms',
      // Zero animation - instant transitions
      // Physical, immediate feedback
      // No smooth digital polish

      easing: 'step-end',
      // Immediate step - no easing curves
      // On/off states, no in-between
      // Tactile, physical feel
    },

    // ==========================================
    // EFFECTS - Charcoal characteristics
    // ==========================================
    effects: {
      shadow: 'none',
      // No clean shadows - use rough borders instead
      // Shadows added via CSS effects file

      shadowElevated: '2px 2px 8px rgba(0, 0, 0, 0.3)',
      // Smudged shadow for modals
      // Multiple offset shadows in CSS

      borderRadius: '0',
      // Sharp corners - like paper edges
      // No rounded corners - pure geometry

      // Custom charcoal effect flags
      // These trigger special CSS in charcoal-effects.css
      charcoalMode: true,
      // Activates charcoal-specific CSS effects

      paperTexture: 'heavy',
      // Heavy paper grain overlay

      roughEdges: true,
      // SVG displacement for organic borders

      smudgeEffects: true,
      // Multiple shadows for charcoal depth
    }
  }
);

// ============================================
// EXPORT
// ============================================
export default charcoalTheme;
