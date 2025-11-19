/**
 * Dashboard V3 - Theme Engine
 *
 * Smart system that consumes theme configurations and applies them to the DOM
 *
 * Responsibilities:
 * - Load all theme configs (colors, shadows, typography, spacing, borders, animations)
 * - Generate CSS variables dynamically
 * - Apply theme to DOM on initialization
 * - Provide methods to switch themes (desert/ocean)
 * - Create style sheet from config values
 * - Manage CSS injection and cleanup
 *
 * Usage:
 * ```javascript
 * import ThemeEngine from './engines/ThemeEngine.js';
 * import config from './shared/config/index.js';
 *
 * const themeEngine = new ThemeEngine(config);
 * themeEngine.applyTheme('desert'); // Apply desert theme
 * ```
 */

class ThemeEngine {
  constructor(config) {
    if (!config) {
      throw new Error('ThemeEngine: config is required');
    }

    this.config = config;
    this.currentTheme = 'desert';
    this.styleElement = null;
    this.initialized = false;

    // Theme configuration
    this.colors = config.theme.colors;
    this.shadows = config.theme.shadows;
    this.typography = config.theme.typography;
    this.spacing = config.theme.spacing;
    this.borders = config.theme.borders;
    this.animations = config.theme.animations;

    this.initialize();
  }

  /**
   * Initialize theme engine
   */
  initialize() {
    if (this.initialized) {
      console.warn('ThemeEngine: Already initialized');
      return;
    }

    console.log('[ThemeEngine] Initializing...');

    // Apply default theme
    this.applyTheme(this.currentTheme);

    this.initialized = true;
    console.log('[ThemeEngine] Initialized successfully');
  }

  /**
   * Apply theme to DOM
   * @param {string} themeName - Theme name ('desert' or 'ocean')
   */
  applyTheme(themeName = 'desert') {
    if (!['desert', 'ocean'].includes(themeName)) {
      console.error(`ThemeEngine: Invalid theme name: ${themeName}`);
      return;
    }

    console.log(`[ThemeEngine] Applying ${themeName} theme...`);

    this.currentTheme = themeName;

    // Generate and inject CSS
    // ENHANCED: Use semantic theme colors if available
    const cssVariables = this.hasSemanticTheme() ?  this.generateSemanticCSSVariables() : this.generateCSSVariables();
    const keyframes = this.generateKeyframes();
    const utilityClasses = this.generateUtilityClasses();

    const fullCSS = `
/* Dashboard V3 - Theme Engine Generated Styles */
/* Theme: ${themeName} */
/* Generated: ${new Date().toISOString()} */

/* ========================================== */
/* CSS VARIABLES */
/* ========================================== */
${cssVariables}

/* ========================================== */
/* KEYFRAME ANIMATIONS */
/* ========================================== */
${keyframes}

/* ========================================== */
/* UTILITY CLASSES */
/* ========================================== */
${utilityClasses}
`;

    this.injectCSS(fullCSS);

    console.log(`[ThemeEngine] ${themeName} theme applied successfully`);
  }

  /**
   * Generate CSS variables from theme config
   * @returns {string} CSS variable declarations
   */
  generateCSSVariables() {
    const vars = [];

    vars.push(':root {');

    // Color variables
    if (this.colors.cssVariables) {
      vars.push('  /* Colors */');
      Object.entries(this.colors.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    // Typography variables
    if (this.typography.cssVariables) {
      vars.push('\n  /* Typography */');
      Object.entries(this.typography.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    // Spacing variables
    if (this.spacing.cssVariables) {
      vars.push('\n  /* Spacing */');
      Object.entries(this.spacing.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    // Shadow variables
    if (this.shadows.cssVariables) {
      vars.push('\n  /* Shadows */');
      Object.entries(this.shadows.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    // Border variables
    if (this.borders.cssVariables) {
      vars.push('\n  /* Borders */');
      Object.entries(this.borders.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    // Animation variables
    if (this.animations.cssVariables) {
      vars.push('\n  /* Animations */');
      Object.entries(this.animations.cssVariables).forEach(([key, value]) => {
        vars.push(`  ${key}: ${value};`);
      });
    }

    vars.push('}');

    return vars.join('\n');
  }

  /**
   * Generate keyframe animations from config
   * @returns {string} Keyframe CSS
   */
  generateKeyframes() {
    if (!this.animations.keyframes) return '';

    const keyframeCSS = [];

    Object.entries(this.animations.keyframes).forEach(([key, anim]) => {
      keyframeCSS.push(`@keyframes ${anim.name} {`);

      Object.entries(anim.keyframes).forEach(([step, styles]) => {
        keyframeCSS.push(`  ${step} {`);
        Object.entries(styles).forEach(([prop, value]) => {
          const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
          keyframeCSS.push(`    ${cssProp}: ${value};`);
        });
        keyframeCSS.push('  }');
      });

      keyframeCSS.push('}\n');
    });

    return keyframeCSS.join('\n');
  }

  /**
   * Generate utility classes from config
   * @returns {string} Utility class CSS
   */
  generateUtilityClasses() {
    const classes = [];

    // Shadow utility classes
    if (this.shadows.scale) {
      classes.push('/* Shadow Utilities */');
      Object.entries(this.shadows.scale).forEach(([key, value]) => {
        classes.push(`.shadow-${key} {`);
        classes.push(`  box-shadow: ${value};`);
        classes.push('}\n');
      });
    }

    // Border radius utilities
    if (this.borders.radius) {
      classes.push('/* Border Radius Utilities */');
      Object.entries(this.borders.radius).forEach(([key, value]) => {
        classes.push(`.rounded-${key} {`);
        classes.push(`  border-radius: ${value};`);
        classes.push('}\n');
      });
    }

    // Animation utilities
    if (this.animations.keyframes) {
      classes.push('/* Animation Utilities */');
      Object.entries(this.animations.keyframes).forEach(([key, anim]) => {
        classes.push(`.animate-${key} {`);
        classes.push(`  animation: ${anim.name} ${anim.duration || '1s'} ${anim.timing || 'ease'} ${anim.iteration || '1'};`);
        classes.push('}\n');
      });
    }

    // Reduced motion utilities
    if (this.animations.reducedMotion && this.animations.reducedMotion.enabled) {
      classes.push('/* Reduced Motion */');
      classes.push('@media (prefers-reduced-motion: reduce) {');
      classes.push('  * {');
      classes.push('    animation-duration: 0.01ms !important;');
      classes.push('    animation-iteration-count: 1 !important;');
      classes.push('    transition-duration: 0.01ms !important;');
      classes.push('  }');
      classes.push('}\n');
    }

    return classes.join('\n');
  }

  /**
   * Inject CSS into DOM
   * @param {string} css - CSS string to inject
   */
  injectCSS(css) {
    // Remove existing style element if present
    if (this.styleElement && this.styleElement.parentNode) {
      this.styleElement.parentNode.removeChild(this.styleElement);
    }

    // Create new style element
    this.styleElement = document.createElement('style');
    this.styleElement.id = 'dashboardv3-theme-engine';
    this.styleElement.textContent = css;

    // Inject into document head
    document.head.appendChild(this.styleElement);
  }

  /**
   * Get current theme name
   * @returns {string} Current theme name
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get theme color by path
   * @param {string} path - Dot notation path (e.g., 'desert.bronzeDust')
   * @returns {string|null} Color value or null
   */
  getColor(path) {
    const parts = path.split('.');
    let current = this.colors;

    for (const part of parts) {
      if (current[part] === undefined) return null;
      current = current[part];
    }

    return current;
  }

  /**
   * Get shadow by name
   * @param {string} name - Shadow name (e.g., 'lg', 'xl')
   * @returns {string|null} Shadow CSS value or null
   */
  getShadow(name) {
    return this.shadows.scale?.[name] || null;
  }

  /**
   * Get component shadow
   * @param {string} component - Component name (e.g., 'header', 'modal')
   * @param {string} state - State name (e.g., 'default', 'hover')
   * @returns {string|null} Shadow CSS value or null
   */
  getComponentShadow(component, state = 'default') {
    const componentShadows = this.shadows.components?.[component];
    if (!componentShadows) return null;

    if (typeof componentShadows === 'string') return componentShadows;
    return componentShadows[state] || null;
  }

  /**
   * Get typography value
   * @param {string} category - Category (e.g., 'sizes', 'weights')
   * @param {string} name - Value name
   * @returns {string|number|null} Typography value or null
   */
  getTypography(category, name) {
    return this.typography[category]?.[name] || null;
  }

  /**
   * Get spacing value
   * @param {string} name - Spacing name (e.g., 'md', 'xl')
   * @returns {string|null} Spacing value or null
   */
  getSpacing(name) {
    return this.spacing.scale?.[name] || null;
  }

  /**
   * Get border value
   * @param {string} category - Category (e.g., 'radius', 'width')
   * @param {string} name - Value name
   * @returns {string|null} Border value or null
   */
  getBorder(category, name) {
    return this.borders[category]?.[name] || null;
  }

  /**
   * Get animation
   * @param {string} name - Animation name
   * @returns {Object|null} Animation config or null
   */
  getAnimation(name) {
    return this.animations.keyframes?.[name] || null;
  }

  /**
   * Apply custom theme overrides
   * @param {Object} overrides - Theme override object
   */
  applyOverrides(overrides) {
    console.log('[ThemeEngine] Applying custom overrides...');

    if (overrides.colors) {
      Object.assign(this.colors, overrides.colors);
    }
    if (overrides.typography) {
      Object.assign(this.typography, overrides.typography);
    }
    if (overrides.spacing) {
      Object.assign(this.spacing, overrides.spacing);
    }

    // Reapply theme with overrides
    this.applyTheme(this.currentTheme);
  }

  /**
   * Export current theme as CSS file
   * @returns {string} Complete CSS string
   */
  exportThemeCSS() {
    const cssVariables = this.generateCSSVariables();
    const keyframes = this.generateKeyframes();
    const utilityClasses = this.generateUtilityClasses();

    return `
/* Dashboard V3 - Exported Theme */
/* Theme: ${this.currentTheme} */
/* Exported: ${new Date().toISOString()} */

${cssVariables}

${keyframes}

${utilityClasses}
`;
  }

  // ============================================
  // COLOR ACCESS METHODS
  // ============================================

  /**
   * Get desert palette color by shade name
   * @param {string} shade - Color shade (bronzeDust, amberSand, pearlSand, etc.)
   * @returns {string} Hex color value
   */
  getDesertColor(shade) {
    return this.colors.desert[shade] || this.colors.desert.bronzeDust;
  }

  /**
   * Get status color by type
   * @param {string} status - Status type (success, warning, critical, normal, info)
   * @param {string} variant - Color variant (bg, text, border, rgb)
   * @returns {string} Color value
   */
  getStatusColor(status, variant = 'bg') {
    const statusConfig = this.colors.status[status];
    if (!statusConfig) {
      console.warn(`[ThemeEngine] Status '${status}' not found`);
      return this.colors.status.normal[variant];
    }
    return statusConfig[variant] || statusConfig.bg;
  }

  /**
   * Get text color by level
   * @param {string} level - Text level (primary, secondary, muted)
   * @returns {string} Hex color value
   */
  getTextColor(level = 'primary') {
    const colorMap = {
      primary: this.colors.desert.sandDarkest,
      secondary: this.colors.desert.duneShadow,
      muted: this.colors.desert.camelLeather,
    };
    return colorMap[level] || colorMap.primary;
  }

  /**
   * Get all status colors
   * @returns {Object} All status color configurations
   */
  getAllStatusColors() {
    return this.colors.status;
  }

  /**
   * Get bronze accent color with optional opacity
   * @param {number} opacity - Optional opacity (0-1)
   * @returns {string} Color value
   */
  getBronzeColor(opacity = 1) {
    if (opacity === 1) {
      return this.colors.desert.bronzeDust;
    }
    // Convert hex to rgba
    const hex = this.colors.desert.bronzeDust;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }

  /**
   * Get border color (bronze with low opacity)
   * @returns {string} RGBA color value
   */
  getBorderColor() {
    return this.getBronzeColor(0.1);
  }

  // ============================================
  // TYPOGRAPHY ACCESS METHODS
  // ============================================

  /**
   * Get typography style for a component element
   * @param {string} component - Component name (metric, section, card, etc.)
   * @param {string} element - Element type (label, heading, value, etc.)
   * @returns {string} Inline CSS style string
   */
  getTypographyStyle(component, element) {
    const key = `${component}${element.charAt(0).toUpperCase() + element.slice(1)}`;
    const config = this.typography.componentSizes?.[key];

    if (!config) {
      console.warn(`[ThemeEngine] Typography not found: ${key}`);
      return '';
    }

    let styles = `font-size: ${config.fontSize}; font-weight: ${config.fontWeight};`;

    if (config.transform) {
      styles += ` text-transform: ${config.transform};`;
    }

    if (config.letterSpacing) {
      styles += ` letter-spacing: ${config.letterSpacing};`;
    }

    if (config.lineHeight) {
      styles += ` line-height: ${config.lineHeight};`;
    }

    return styles.trim();
  }

  /**
   * Get font size value
   * @param {string} size - Size name (xs, sm, base, lg, xl, 2xl, etc.)
   * @returns {string} Font size value (e.g., "0.875rem")
   */
  getFontSize(size) {
    const sizeMap = {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '2rem',
    };
    return sizeMap[size] || sizeMap.base;
  }

  /**
   * Get font weight value
   * @param {string} weight - Weight name (light, normal, medium, semibold, bold)
   * @returns {number} Font weight value
   */
  getFontWeight(weight) {
    const weightMap = {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    };
    return weightMap[weight] || weightMap.normal;
  }

  // ============================================
  // ANIMATION ACCESS METHODS
  // ============================================

  /**
   * Get animation duration
   * @param {string} speed - Speed name (fast, normal, slow)
   * @returns {string} Duration value (e.g., "0.3s")
   */
  getAnimationDuration(speed = 'normal') {
    const durationMap = {
      fast: '0.15s',
      normal: '0.3s',
      slow: '0.5s',
    };
    return durationMap[speed] || durationMap.normal;
  }

  /**
   * Get animation easing function
   * @param {string} type - Easing type (ease, smooth, bounce, etc.)
   * @returns {string} Timing function value
   */
  getAnimationEasing(type = 'ease') {
    const easingMap = {
      ease: 'ease',
      smooth: 'ease-in-out',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    };
    return easingMap[type] || easingMap.ease;
  }

  /**
   * Get transform value for animations
   * @param {string} name - Transform name (cardLift, cardPress, etc.)
   * @returns {string} Transform value
   */
  getTransform(name) {
    const transformMap = {
      cardLift: 'translateY(-4px)',
      cardPress: 'translateY(2px)',
      hoverLift: 'translateY(-2px)',
      none: 'translateY(0)',
    };
    return transformMap[name] || transformMap.none;
  }

  // ============================================
  // SEMANTIC COLOR ACCESS METHODS (V3.0)
  // New methods for semantic theme system
  // ============================================

  /**
   * Load semantic theme from theme registry
   * @param {Object} themeObject - Theme object from themes registry
   */
  loadSemanticTheme(themeObject) {
    if (!themeObject || !themeObject.colors) {
      console.error('[ThemeEngine] Invalid theme object');
      return;
    }

    this.semanticTheme = themeObject;
    console.log(`[ThemeEngine] Loaded semantic theme: ${themeObject.name}`);
  }

  /**
   * Get semantic text color by role
   * @param {string} role - Text role (primary, secondary, muted, disabled)
   * @returns {string} Hex color value
   */
  getSemanticTextColor(role = 'primary') {
    if (this.semanticTheme?.colors) {
      const key = `text_${role}`;
      const color = this.semanticTheme.colors[key] || this.semanticTheme.colors.text_primary;
      console.log(`[ThemeEngine] getSemanticTextColor('${role}') from "${this.semanticTheme.name}" → ${color}`);
      return color;
    }
    // Fallback to old method
    console.warn(`[ThemeEngine] No semantic theme loaded, falling back to getTextColor('${role}')`);
    return this.getTextColor(role);
  }

  /**
   * Get semantic background color by role
   * @param {string} role - Background role (primary, card, elevated, hover)
   * @returns {string} Hex color value
   */
  getSemanticBackgroundColor(role = 'primary') {
    if (this.semanticTheme?.colors) {
      const key = `background_${role}`;
      return this.semanticTheme.colors[key] || this.semanticTheme.colors.background_primary;
    }
    // Fallback
    return role === 'primary' ? this.colors.desert.pearlSand : '#FFFFFF';
  }

  /**
   * Get semantic border color by role
   * @param {string} role - Border role (strong, default, subtle)
   * @returns {string} Hex color value
   */
  getSemanticBorderColor(role = 'default') {
    if (this.semanticTheme?.colors) {
      const key = `border_${role}`;
      const color = this.semanticTheme.colors[key] || this.semanticTheme.colors.border_default;
      console.log(`[ThemeEngine] getSemanticBorderColor('${role}') from "${this.semanticTheme.name}" → ${color}`);
      return color;
    }
    // Fallback
    console.warn(`[ThemeEngine] No semantic theme, falling back to getBorderColor()`);
    return this.getBorderColor();
  }

  /**
   * Get semantic accent color by role
   * @param {string} role - Accent role (primary, secondary, interactive)
   * @returns {string} Hex color value
   */
  getSemanticAccentColor(role = 'primary') {
    if (this.semanticTheme?.colors) {
      const key = `accent_${role}`;
      const color = this.semanticTheme.colors[key] || this.semanticTheme.colors.accent_primary;
      console.log(`[ThemeEngine] getSemanticAccentColor('${role}') from "${this.semanticTheme.name}" → ${color}`);
      return color;
    }
    // Fallback
    console.warn(`[ThemeEngine] No semantic theme, falling back to desert.bronzeDust`);
    return this.colors.desert.bronzeDust;
  }

  /**
   * Get semantic dashboard color by role
   * @param {string} role - Dashboard role (metric, metricLabel, sectionHeader, etc.)
   * @returns {string} Hex color value
   */
  getSemanticDashboardColor(role) {
    if (this.semanticTheme?.colors) {
      const key = `dashboard_${role}`;
      return this.semanticTheme.colors[key] || this.semanticTheme.colors.text_primary;
    }
    // Fallback
    return this.getTextColor('primary');
  }

  /**
   * Get semantic status color
   * @param {string} status - Status type (success, warning, error, critical, info, normal)
   * @param {string} variant - Color variant (bg, text, border)
   * @returns {string} Color value
   */
  getSemanticStatusColor(status, variant = 'bg') {
    if (this.semanticTheme?.status?.[status]) {
      return this.semanticTheme.status[status][variant] || this.semanticTheme.status[status].bg;
    }
    // Fallback to old method
    return this.getStatusColor(status, variant);
  }

  /**
   * Check if semantic theme is loaded
   * @returns {boolean} True if semantic theme is active
   */
  hasSemanticTheme() {
    return !!this.semanticTheme;
  }

  /**
   * Get current theme metadata
   * @returns {Object} Theme metadata
   */
  getThemeMetadata() {
    if (this.semanticTheme) {
      return {
        name: this.semanticTheme.name,
        version: this.semanticTheme.metadata?.version,
        created: this.semanticTheme.metadata?.created,
        validation: this.semanticTheme.metadata?.validation,
      };
    }
    return { name: this.currentTheme, version: 'legacy' };
  }

  /**
   * Generate CSS variables from semantic theme
   * @returns {string} CSS variable declarations
   */
  generateSemanticCSSVariables() {
    if (!this.semanticTheme) return this.generateCSSVariables();

    const theme = this.semanticTheme;
    console.log('[ThemeEngine] Generating CSS variables from semantic theme:', theme.name);

    return `:root {
  /* Semantic Text Colors */
  --text-primary: ${theme.colors.text_primary};
  --text-secondary: ${theme.colors.text_secondary};
  --text-muted: ${theme.colors.text_muted};
  --text-disabled: ${theme.colors.text_disabled};

  /* Semantic Background Colors */
  --bg-primary: ${theme.colors.background_primary};
  --bg-card: ${theme.colors.background_card};
  --bg-elevated: ${theme.colors.background_elevated};
  --bg-hover: ${theme.colors.background_hover};

  /* Semantic Border Colors */
  --border-strong: ${theme.colors.border_strong};
  --border-default: ${theme.colors.border_default};
  --border-subtle: ${theme.colors.border_subtle};

  /* Semantic Accent Colors */
  --accent-primary: ${theme.colors.accent_primary};
  --accent-secondary: ${theme.colors.accent_secondary};
  --accent-interactive: ${theme.colors.accent_interactive};

  /* Dashboard Colors */
  --dashboard-metric: ${theme.colors.dashboard_metric};
  --dashboard-metric-label: ${theme.colors.dashboard_metricLabel};
  --dashboard-section-header: ${theme.colors.dashboard_sectionHeader};
  --dashboard-table-header: ${theme.colors.dashboard_tableHeader};
  --dashboard-table-row: ${theme.colors.dashboard_tableRow};

  /* Status Colors */
  --status-success-bg: ${theme.status.success.bg};
  --status-success-text: ${theme.status.success.text};
  --status-success-border: ${theme.status.success.border};

  --status-warning-bg: ${theme.status.warning.bg};
  --status-warning-text: ${theme.status.warning.text};
  --status-warning-border: ${theme.status.warning.border};

  --status-error-bg: ${theme.status.error.bg};
  --status-error-text: ${theme.status.error.text};
  --status-error-border: ${theme.status.error.border};

  /* Legacy Color Mappings for main.css compatibility */
  --color-bronze: ${theme.colors.accent_primary};
  --color-amber: ${theme.colors.accent_secondary};

  /* Tailwind-like color overrides mapped to semantic colors */
  /* Blue (primary accent) */
  --color-blue-500: ${theme.colors.accent_primary};
  --color-blue-600: ${theme.colors.accent_primary};

  /* Orange (secondary accent) */
  --color-orange-500: ${theme.colors.accent_secondary};
  --color-orange-600: ${theme.colors.accent_secondary};

  /* Purple (interactive) */
  --color-purple-500: ${theme.colors.accent_interactive};
  --color-purple-600: ${theme.colors.accent_interactive};

  /* Green (success) */
  --color-green-500: ${theme.status.success.text};
  --color-green-600: ${theme.status.success.text};
  --color-green-50: ${theme.status.success.bg};

  /* Red (error) */
  --color-red-500: ${theme.status.error.text};
  --color-red-600: ${theme.status.error.text};
  --color-red-50: ${theme.status.error.bg};

  /* Yellow/Amber (warning) */
  --color-yellow-100: ${theme.status.warning.bg};
  --color-yellow-800: ${theme.status.warning.text};
  --color-orange-100: ${theme.status.warning.bg};
  --color-orange-800: ${theme.status.warning.text};

  /* Gradient support colors */
  --gradient-start: ${theme.colors.accent_primary};
  --gradient-end: ${theme.colors.accent_secondary};
}`;
  }

  // ============================================
  // THEME EFFECTS (V3.0)
  // ============================================

  /**
   * Apply theme-specific effects (CSS files, attributes, etc.)
   * Automatically loads effect stylesheets for themes with custom effects
   */
  applyThemeEffects() {
    const theme = this.semanticTheme;

    if (!theme) {
      console.warn('[ThemeEngine] No semantic theme loaded, skipping effects');
      return;
    }

    // Set data-theme attribute on body for CSS targeting
    const themeId = this.getThemeIdFromName(theme.name);
    document.body.setAttribute('data-theme', themeId);
    console.log(`[ThemeEngine] Set data-theme="${themeId}" on body`);

    // Load theme-specific CSS if it has custom effects
    if (theme.effects?.charcoalMode) {
      this.loadThemeCSS('charcoal-effects.css', themeId);
      // Remove other effect sheets
      this.removeThemeCSS('faded-architect-effects.css');
    } else if (theme.effects?.fadedArchitectMode) {
      this.loadThemeCSS('faded-architect-effects.css', themeId);
      // Remove other effect sheets
      this.removeThemeCSS('charcoal-effects.css');
    } else {
      // Remove all effect sheets if no custom effects
      this.removeThemeCSS('charcoal-effects.css');
      this.removeThemeCSS('faded-architect-effects.css');
    }

    // Log applied effects
    if (theme.effects) {
      console.log('[ThemeEngine] Theme effects applied:', {
        charcoalMode: theme.effects.charcoalMode || false,
        fadedArchitectMode: theme.effects.fadedArchitectMode || false,
        paperTexture: theme.effects.paperTexture || false,
        heavyTexture: theme.effects.heavyTexture || false,
        roughEdges: theme.effects.roughEdges || false,
        gradientBorders: theme.effects.gradientBorders || false,
        softEdges: theme.effects.softEdges || false,
        flatDesign: theme.effects.flatDesign || false,
        smudgeEffects: theme.effects.smudgeEffects || false,
      });
    }
  }

  /**
   * Load theme-specific CSS file
   * @param {string} filename - CSS filename (e.g., 'charcoal-effects.css')
   * @param {string} themeId - Theme identifier for tracking
   */
  loadThemeCSS(filename, themeId) {
    // Check if already loaded
    const existingLink = document.querySelector(`link[data-theme-css="${filename}"]`);
    if (existingLink) {
      console.log(`[ThemeEngine] ${filename} already loaded`);
      return;
    }

    // Create link element
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `/shared/config/theme/themes/${filename}`;
    link.setAttribute('data-theme-css', filename);
    link.setAttribute('data-theme-id', themeId);

    // Add to head
    document.head.appendChild(link);
    console.log(`[ThemeEngine] Loaded theme CSS: ${filename}`);
  }

  /**
   * Remove theme-specific CSS file
   * @param {string} filename - CSS filename to remove
   */
  removeThemeCSS(filename) {
    const link = document.querySelector(`link[data-theme-css="${filename}"]`);
    if (link) {
      link.remove();
      console.log(`[ThemeEngine] Removed theme CSS: ${filename}`);
    }
  }

  /**
   * Get theme ID from theme name
   * @param {string} themeName - Theme display name
   * @returns {string} Theme ID
   */
  getThemeIdFromName(themeName) {
    const nameMap = {
      'Desert Oasis': 'desert',
      'Graphite Professional': 'graphite',
      'Charcoal Artist': 'charcoal',
      'Faded Architect': 'faded-architect',
    };
    return nameMap[themeName] || themeName.toLowerCase().replace(/\s+/g, '-');
  }

  // ============================================
  // THEME STATISTICS
  // ============================================

  /**
   * Get theme statistics
   * @returns {Object} Theme stats
   */
  getStats() {
    return {
      currentTheme: this.currentTheme,
      semanticTheme: this.semanticTheme?.name || 'none',
      totalColors: this.colors.totalColors || 0,
      totalShadows: this.shadows.totalShadows || 0,
      totalTypography: this.typography.totalConfigs || 0,
      totalSpacing: this.spacing.totalValues || 0,
      totalBorders: this.borders.totalConfigs || 0,
      totalAnimations: this.animations.totalConfigs || 0,
      initialized: this.initialized,
    };
  }

  /**
   * Cleanup and remove injected styles
   */
  destroy() {
    console.log('[ThemeEngine] Destroying...');

    if (this.styleElement && this.styleElement.parentNode) {
      this.styleElement.parentNode.removeChild(this.styleElement);
      this.styleElement = null;
    }

    this.initialized = false;
    console.log('[ThemeEngine] Destroyed');
  }
}

export default ThemeEngine;
