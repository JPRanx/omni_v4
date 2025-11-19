/**
 * Dashboard V3 - Graphite Professional Theme
 *
 * Inspired by reMarkable tablets and legal documents
 * A monochrome professional theme with paper-like qualities
 *
 * Design Philosophy:
 * - Mimics the elegance of ink on paper
 * - Professional legal document aesthetic
 * - High readability with subtle depth
 * - Minimal color, maximum clarity
 *
 * Version: 3.0.0
 * Date: 2025-11-01
 */

import { createTheme } from '../themeTemplate.js';

export const graphiteTheme = createTheme(
  // ============================================
  // THEME NAME
  // ============================================
  'Graphite Professional',  // Like writing on a reMarkable tablet

  // ============================================
  // SEMANTIC COLORS
  // ============================================
  {
    // ==========================================
    // TEXT HIERARCHY - Ink gradations
    // ==========================================

    text_primary: '#1A1A1A',
    // Deep ink black - Like fountain pen ink on paper
    // Main headers, important values, primary content
    // Mimics the rich black of professional legal documents

    text_secondary: '#2D2D2D',
    // Charcoal gray - Like pencil lead on paper
    // Subheadings, descriptions, supporting content
    // The color of typewriter ribbon text

    text_muted: '#6B6B6B',
    // Pencil gray - Like a 2H pencil marking
    // Labels, metadata, annotations
    // Soft enough to not dominate but clear enough to read

    text_disabled: '#A8A8A8',
    // Faded graphite - Like erased pencil marks
    // Inactive elements, disabled states
    // Clearly indicates non-interactive elements

    // ==========================================
    // BACKGROUNDS - Paper textures
    // ==========================================

    background_primary: '#F8F8F6',
    // Off-white paper - Like high-quality legal pad paper
    // Not pure white to reduce eye strain
    // Mimics the warm tone of premium paper

    background_card: '#FAFAF8',
    // Bright paper white - Like fresh printer paper
    // Individual cards stand out slightly from background
    // Clean, professional appearance

    background_elevated: '#FFFFFF',
    // Pure white - Like a new document
    // Modals and overlays pop forward
    // Maximum contrast for important dialogs

    background_hover: 'rgba(26, 26, 26, 0.02)',
    // Subtle ink shadow - Like paper slightly shaded
    // Barely visible hover effect
    // Maintains minimalist aesthetic

    // ==========================================
    // BORDERS - Ruled lines
    // ==========================================

    border_strong: '#1A1A1A',
    // Ink line - Like a pen-drawn border
    // Strong emphasis, section dividers
    // Used sparingly for maximum impact

    border_default: '#4A4A4A',
    // Graphite line - Like pencil-drawn borders
    // Standard dividers and card edges
    // Professional without being heavy

    border_subtle: 'rgba(0, 0, 0, 0.08)',
    // Faint pencil line - Like ruled paper lines
    // Table rows, subtle separators
    // Almost invisible but provides structure

    // ==========================================
    // ACCENTS - Minimal color touches
    // ==========================================

    accent_primary: '#2D2D2D',
    // Charcoal - Primary brand color stays monochrome
    // Buttons, active states, selections
    // Maintains the grayscale aesthetic

    accent_secondary: '#4A4A4A',
    // Medium graphite - Supporting accent
    // Secondary actions, alternative states
    // Provides variety without introducing color

    accent_interactive: '#1A1A1A',
    // Deep ink - Links and clickable elements
    // Underlined like traditional hyperlinks
    // Classic, professional appearance

    // ==========================================
    // DASHBOARD-SPECIFIC - Data presentation
    // ==========================================

    dashboard_metric: '#0F0F0F',
    // Near-black - Important numbers pop
    // Revenue, percentages, KPIs
    // Maximum readability for critical data

    dashboard_metricLabel: '#4A4A4A',
    // Medium gray - Labels don't compete with values
    // "Total Revenue", "Average Order"
    // Clear hierarchy between label and value

    dashboard_sectionHeader: '#1A1A1A',
    // Ink black - Major section divisions
    // "Week Overview", "P&L Summary"
    // Commands attention like document headers

    dashboard_tableHeader: '#2D2D2D',
    // Charcoal - Table column headers
    // Slightly lighter than content for distinction
    // Professional data presentation

    dashboard_tableRow: 'rgba(0, 0, 0, 0.015)',
    // Ultra-subtle gray - Zebra striping
    // Just enough to guide the eye
    // Maintains clean aesthetic

    dashboard_gradientStart: '#E8E8E8',
    // Light silver - Subtle gradient beginnings
    // Header backgrounds, gentle emphasis
    // Professional without being flashy

    dashboard_gradientEnd: '#F5F5F5',
    // Near white - Gradient fade out
    // Creates subtle depth
    // Paper-like quality

    // ==========================================
    // STATUS COLORS - Minimal color system
    // ==========================================
    // Using muted, professional tones like colored ink annotations

    status: {
      success: {
        bg: 'rgba(47, 79, 47, 0.06)',      // Very light forest green
        text: '#2F4F2F',                   // Dark forest green - like green ink
        border: '#4A7C4A',                 // Medium forest green
      },
      // Success uses green like a checkmark in green pen

      warning: {
        bg: 'rgba(184, 134, 11, 0.06)',    // Very light gold
        text: '#B8860B',                   // Dark goldenrod - like gold ink
        border: '#DAA520',                 // Goldenrod
      },
      // Warning uses gold like a notary seal

      error: {
        bg: 'rgba(139, 0, 0, 0.06)',       // Very light burgundy
        text: '#8B0000',                   // Dark red - like red ink corrections
        border: '#A52A2A',                 // Brown-red
      },
      // Error uses deep red like editor's marks

      critical: {
        bg: 'rgba(139, 0, 0, 0.08)',       // Slightly darker burgundy
        text: '#8B0000',                   // Same dark red
        border: '#8B0000',                 // Stronger red border
      },
      // Critical uses same red but more intense

      info: {
        bg: 'rgba(25, 25, 112, 0.06)',     // Very light midnight blue
        text: '#191970',                   // Midnight blue - like blue ink
        border: '#4169E1',                 // Royal blue
      },
      // Info uses blue like margin notes in blue pen

      normal: {
        bg: '#F9F9F9',                     // Light gray
        text: '#2D2D2D',                   // Charcoal
        border: '#D1D1D1',                 // Light gray border
      }
      // Normal stays in grayscale theme
    }
  },

  // ============================================
  // OPTIONAL ENHANCEMENTS
  // ============================================
  {
    // ==========================================
    // TYPOGRAPHY - Legal document style
    // ==========================================
    typography: {
      fontFamily: '"Crimson Text", "Georgia", "Times New Roman", serif',
      // Classic serif for that legal document feel
      // Crimson Text is elegant and highly readable

      scale: 1.05,
      // Slightly larger for better readability
      // Mimics the larger type of legal documents
    },

    // ==========================================
    // ANIMATIONS - Subtle and professional
    // ==========================================
    animations: {
      duration: 'normal',
      // 300ms - not too fast, not too slow

      easing: 'ease-out',
      // Natural deceleration like paper settling
    },

    // ==========================================
    // EFFECTS - Paper-like qualities
    // ==========================================
    effects: {
      shadow: '0 1px 2px rgba(0, 0, 0, 0.08)',
      // Very subtle shadow like paper on paper

      shadowElevated: '0 4px 6px rgba(0, 0, 0, 0.12)',
      // Slightly stronger for modals

      borderRadius: '0.125rem',
      // Minimal rounding (2px) - like paper corners
    }
  }
);

// ============================================
// EXPORT
// ============================================
export default graphiteTheme;
