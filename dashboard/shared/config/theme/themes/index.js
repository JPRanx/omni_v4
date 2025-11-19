/**
 * Dashboard V3 - Theme Registry
 *
 * Central export for all available themes
 * Makes it easy to add new themes without touching other code
 */

import { desertTheme } from './desert.js';
import { graphiteTheme } from './graphite.js';
import { charcoalTheme } from './charcoal.js';
import { fadedArchitectTheme } from './faded-architect.js';

// ============================================
// THEME REGISTRY
// All available themes in the system
// ============================================

export const themes = {
  desert: desertTheme,
  graphite: graphiteTheme,
  charcoal: charcoalTheme,
  'faded-architect': fadedArchitectTheme,
};

// ============================================
// THEME METADATA
// ============================================

export const themeMetadata = {
  desert: {
    id: 'desert',
    name: 'Desert Oasis',
    description: 'Warm, luxurious Dubai-inspired theme',
    category: 'warm',
    preview: {
      primary: '#B89968',
      background: '#FAF6F0',
      text: '#3D3128'
    }
  },
  graphite: {
    id: 'graphite',
    name: 'Graphite Professional',
    description: 'Monochrome ink on paper - reMarkable tablet aesthetic',
    category: 'cool',
    preview: {
      primary: '#1A1A1A',
      background: '#F8F8F6',
      text: '#1A1A1A'
    }
  },
  charcoal: {
    id: 'charcoal',
    name: 'Charcoal Artist',
    description: 'Hand-drawn sketchbook with paper texture and rough edges',
    category: 'artistic',
    preview: {
      primary: '#1A1A1A',
      background: '#F5F5F0',
      text: '#1A1A1A'
    }
  },
  'faded-architect': {
    id: 'faded-architect',
    name: 'Faded Architect',
    description: 'Soft charcoal studies on cool gray drafting paper - completely flat',
    category: 'artistic',
    preview: {
      primary: '#4A4A4A',
      background: '#E8E8E6',
      text: '#4A4A4A'
    }
  }
};

// ============================================
// THEME UTILITIES
// ============================================

/**
 * Get theme by ID
 * @param {string} themeId - Theme identifier
 * @returns {Object} Theme object
 */
export function getTheme(themeId) {
  const theme = themes[themeId];
  if (!theme) {
    console.warn(`[ThemeRegistry] Theme '${themeId}' not found, returning desert`);
    return themes.desert;
  }
  return theme;
}

/**
 * Get all available theme IDs
 * @returns {string[]} Array of theme IDs
 */
export function getAvailableThemes() {
  return Object.keys(themes);
}

/**
 * Validate theme ID exists
 * @param {string} themeId - Theme identifier to check
 * @returns {boolean} True if theme exists
 */
export function isValidTheme(themeId) {
  return themes.hasOwnProperty(themeId);
}

// ============================================
// DEFAULT EXPORTS
// ============================================

export default themes;
