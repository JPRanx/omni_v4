/**
 * Dashboard V3 - Semantic Color Roles
 *
 * Defines WHAT each color is used for (semantic purpose)
 * Not HOW it looks (aesthetic appearance)
 *
 * This enables theme portability - components request colors by PURPOSE,
 * not by appearance (e.g., 'text_primary' not 'sandDarkest')
 */

export const COLOR_ROLES = {
  // Text hierarchy (4 levels)
  // Components should use these for all text content
  text: {
    primary: 'Main content, headers, important text',
    secondary: 'Subheadings, descriptions',
    muted: 'Labels, metadata, helper text',
    disabled: 'Inactive or unavailable elements'
  },

  // Backgrounds (4 types)
  // Used for layering and elevation
  background: {
    primary: 'Main page background',
    card: 'Card and section backgrounds',
    elevated: 'Modals, dropdowns, overlays',
    hover: 'Hover states for interactive elements'
  },

  // Borders (3 strengths)
  // Used for visual separation
  border: {
    strong: 'Major section dividers, emphasized borders',
    default: 'Standard card borders, dividers',
    subtle: 'Light separators, table lines'
  },

  // Accents (3 purposes)
  // Brand and interactive colors
  accent: {
    primary: 'Main brand color, primary actions',
    secondary: 'Supporting accent, secondary actions',
    interactive: 'Links, clickable elements'
  },

  // Status (fixed across all themes for consistency)
  // Used for user feedback and states
  status: {
    success: { bg: 'Success background', text: 'Success text', border: 'Success border' },
    warning: { bg: 'Warning background', text: 'Warning text', border: 'Warning border' },
    error: { bg: 'Error background', text: 'Error text', border: 'Error border' },
    info: { bg: 'Info background', text: 'Info text', border: 'Info border' }
  },

  // Dashboard-specific roles
  // Specialized semantic roles for dashboard components
  dashboard: {
    metric: 'Metric values and numbers',
    metricLabel: 'Metric labels',
    sectionHeader: 'Section headers',
    tableHeader: 'Table header backgrounds',
    tableRow: 'Table row backgrounds',
    gradientStart: 'Gradient start color (headers, banners)',
    gradientEnd: 'Gradient end color (headers, banners)'
  }
};

/**
 * Validate that a theme provides all required semantic colors
 * @param {Object} themeColors - Theme color object to validate
 * @returns {Object} Validation result with required, missing, and isValid
 */
export function validateThemeColors(themeColors) {
  const required = [];
  const missing = [];

  // Text colors
  ['primary', 'secondary', 'muted', 'disabled'].forEach(level => {
    const key = `text_${level}`;
    required.push(key);
    if (!themeColors[key]) missing.push(key);
  });

  // Background colors
  ['primary', 'card', 'elevated', 'hover'].forEach(type => {
    const key = `background_${type}`;
    required.push(key);
    if (!themeColors[key]) missing.push(key);
  });

  // Border colors
  ['strong', 'default', 'subtle'].forEach(strength => {
    const key = `border_${strength}`;
    required.push(key);
    if (!themeColors[key]) missing.push(key);
  });

  // Accent colors
  ['primary', 'secondary', 'interactive'].forEach(purpose => {
    const key = `accent_${purpose}`;
    required.push(key);
    if (!themeColors[key]) missing.push(key);
  });

  // Dashboard colors
  ['metric', 'metricLabel', 'sectionHeader', 'tableHeader', 'tableRow', 'gradientStart', 'gradientEnd'].forEach(element => {
    const key = `dashboard_${element}`;
    required.push(key);
    if (!themeColors[key]) missing.push(key);
  });

  return {
    required,
    missing,
    isValid: missing.length === 0,
    coverage: ((required.length - missing.length) / required.length * 100).toFixed(1) + '%'
  };
}

/**
 * Get a flat list of all required color keys
 * Useful for documentation and theme creation
 */
export function getRequiredColorKeys() {
  const keys = [];

  ['primary', 'secondary', 'muted', 'disabled'].forEach(level =>
    keys.push(`text_${level}`)
  );

  ['primary', 'card', 'elevated', 'hover'].forEach(type =>
    keys.push(`background_${type}`)
  );

  ['strong', 'default', 'subtle'].forEach(strength =>
    keys.push(`border_${strength}`)
  );

  ['primary', 'secondary', 'interactive'].forEach(purpose =>
    keys.push(`accent_${purpose}`)
  );

  ['metric', 'metricLabel', 'sectionHeader', 'tableHeader', 'tableRow', 'gradientStart', 'gradientEnd'].forEach(element =>
    keys.push(`dashboard_${element}`)
  );

  return keys;
}

export default COLOR_ROLES;
