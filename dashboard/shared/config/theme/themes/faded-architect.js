/**
 * Dashboard V3 - Faded Architect Theme
 *
 * Like discovering old architectural charcoal studies
 * Everything is soft, blended, and lives ON the paper
 *
 * Design Philosophy:
 * - Cool gray paper with heavy texture
 * - Thick, gradient borders that fade into background
 * - All elements feel drawn and then softly smudged
 * - Completely flat - no elevation or shadows
 * - Like pressing different weights of charcoal
 * - Nothing is harsh - everything is contemplative
 *
 * Inspiration:
 * - Architectural preliminary sketches
 * - Charcoal figure studies
 * - Drafting paper studies
 * - Smudged charcoal drawings
 * - Graphite powder on textured paper
 *
 * Version: 3.0.0
 * Date: 2025-11-01
 */

import { createTheme } from '../themeTemplate.js';

export const fadedArchitectTheme = createTheme(
  // ============================================
  // THEME NAME
  // ============================================
  'Faded Architect',  // Soft architectural charcoal studies on cool gray paper

  // ============================================
  // SEMANTIC COLORS - Cool Gray Tones
  // ============================================
  {
    // ==========================================
    // TEXT HIERARCHY - Soft charcoal tones
    // ==========================================

    text_primary: '#4A4A4A',
    // Dark gray, not black - Like medium-pressure charcoal
    // Main content, headers, important text
    // Soft enough to feel hand-drawn, dark enough to read

    text_secondary: '#6A6A6A',
    // Medium gray - Like light charcoal strokes
    // Subheadings, descriptions
    // Clearly secondary but still readable

    text_muted: '#8A8A8A',
    // Light gray - Like graphite powder
    // Labels, metadata, annotations
    // Barely there but provides context

    text_disabled: '#AAAAAA',
    // Very light gray - Like faded charcoal
    // Inactive elements
    // Almost blends with background

    // ==========================================
    // BACKGROUNDS - Cool drafting paper
    // ==========================================

    background_primary: '#E8E8E6',
    // Cool gray paper - Architectural drafting paper
    // Main canvas background
    // Cool tone reduces eye strain

    background_card: '#EDEDEB',
    // Slightly lighter - Fresh paper sheet
    // Card backgrounds
    // Subtle difference from main background

    background_elevated: '#EDEDEB',
    // SAME as card - NO elevation in this theme!
    // Modals, overlays
    // Everything lives ON the paper, nothing floats

    background_hover: '#E0E0DE',
    // Slightly darker - Like pressed charcoal
    // Hover states
    // Darker = more pressure on charcoal

    // ==========================================
    // BORDERS - Soft, faded edges
    // ==========================================

    border_strong: 'rgba(100, 100, 100, 0.3)',
    // Faded dark gray - Like soft charcoal line
    // Major divisions
    // Visible but not harsh

    border_default: 'rgba(120, 120, 120, 0.2)',
    // Faded medium gray - Standard divider
    // Card edges, standard borders
    // Soft and contemplative

    border_subtle: 'rgba(140, 140, 140, 0.1)',
    // Almost invisible - Like smudged graphite
    // Table rows, subtle separators
    // Barely perceptible structure

    // ==========================================
    // ACCENTS - Muted tones
    // ==========================================

    accent_primary: '#5A5A5A',
    // Muted dark gray - Primary brand stays soft
    // Buttons, active states
    // No harsh colors, all contemplative

    accent_secondary: '#7A7A7A',
    // Muted medium gray - Supporting accent
    // Secondary actions
    // Variety in grayscale

    accent_interactive: '#6A6A6A',
    // Muted gray - Clickable elements
    // Links, interactive text
    // Subtly distinguishable

    // ==========================================
    // DASHBOARD-SPECIFIC - All soft tones
    // ==========================================

    dashboard_metric: '#3A3A3A',
    // Darkest gray for numbers - Hand-drawn figures
    // Revenue, KPIs, important data
    // Emphasis through contrast, not harshness

    dashboard_metricLabel: '#7A7A7A',
    // Faded labels - Don't compete with values
    // Metric descriptions
    // Soft hierarchy

    dashboard_sectionHeader: '#4A4A4A',
    // Section headers - Architectural labels
    // Major section titles
    // Clear but not loud

    dashboard_tableHeader: '#6A6A6A',
    // Table headers - Column titles
    // Data grid headers
    // Distinguished but soft

    dashboard_tableRow: 'rgba(100, 100, 100, 0.05)',
    // Barely visible - Zebra stripes
    // Alternating rows
    // Just enough for structure

    dashboard_gradientStart: 'transparent',
    // No gradients - flat like paper
    // Everything is drawn on the surface

    dashboard_gradientEnd: 'transparent',
    // No gradients - pure flatness
    // Architectural study aesthetic

    // ==========================================
    // STATUS COLORS - Muted colored chalk dust
    // ==========================================
    // Status uses very subtle tints, like colored chalk on gray paper

    status: {
      success: {
        bg: 'rgba(130, 140, 130, 0.15)',     // Faded green-gray
        text: '#5A6A5A',                     // Muted green-tinted gray
        border: 'rgba(130, 140, 130, 0.3)',  // Soft green-gray border
      },
      // Success is barely green - like green chalk dust on gray

      warning: {
        bg: 'rgba(140, 135, 120, 0.15)',     // Faded warm-gray
        text: '#6A655A',                     // Muted warm-tinted gray
        border: 'rgba(140, 135, 120, 0.3)',  // Soft warm-gray border
      },
      // Warning is barely warm - like sepia on gray

      error: {
        bg: 'rgba(140, 130, 130, 0.15)',     // Faded red-gray
        text: '#6A5A5A',                     // Muted red-tinted gray
        border: 'rgba(140, 130, 130, 0.3)',  // Soft red-gray border
      },
      // Error is barely red - like red chalk dust

      critical: {
        bg: 'rgba(120, 120, 120, 0.2)',      // Just darker gray
        text: '#4A4A4A',                     // Darker neutral gray
        border: 'rgba(120, 120, 120, 0.35)', // Stronger gray border
      },
      // Critical is just darker, no color

      info: {
        bg: 'rgba(130, 130, 140, 0.15)',     // Faded blue-gray
        text: '#5A5A6A',                     // Muted blue-tinted gray
        border: 'rgba(130, 130, 140, 0.3)',  // Soft blue-gray border
      },
      // Info is barely blue - like blue chalk dust

      normal: {
        bg: 'transparent',                   // No background
        text: '#6A6A6A',                     // Medium gray
        border: 'rgba(120, 120, 120, 0.2)', // Soft gray border
      }
      // Normal is neutral gray
    }
  },

  // ============================================
  // OPTIONAL ENHANCEMENTS
  // ============================================
  {
    // ==========================================
    // TYPOGRAPHY - Architectural hand-lettering
    // ==========================================
    typography: {
      fontFamily: '"Architects Daughter", "Courier Prime", "Courier New", monospace',
      // Hand-drawn architectural lettering style
      // Architects Daughter is gentle, personal
      // Falls back to Courier for consistency

      scale: 1.0,
      // Standard scale
      // Architectural drawings use consistent sizing
    },

    // ==========================================
    // ANIMATIONS - Minimal, soft transitions
    // ==========================================
    animations: {
      duration: 'fast',
      // 150ms - Quick but not instant
      // Soft fades, not jarring changes

      easing: 'ease-out',
      // Natural deceleration
      // Like charcoal settling on paper
    },

    // ==========================================
    // EFFECTS - Soft, blended qualities
    // ==========================================
    effects: {
      shadow: 'none',
      // No shadows - completely flat
      // Everything lives ON the paper surface

      shadowElevated: 'none',
      // No elevation shadows either
      // Even modals are on the same plane

      borderRadius: '0',
      // Sharp corners - paper edges
      // No rounded corners in architectural drawings

      // Custom faded architect effect flags
      fadedArchitectMode: true,
      // Activates faded architect CSS effects

      heavyTexture: true,
      // Multiple layers of paper texture

      gradientBorders: true,
      // Borders fade from center to edges

      softEdges: true,
      // Slight blur on all elements

      flatDesign: true,
      // Absolutely no depth or elevation
    }
  }
);

// ============================================
// EXPORT
// ============================================
export default fadedArchitectTheme;
