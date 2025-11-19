/**
 * Dashboard V3 - Theme Switcher Component
 *
 * Allows users to switch between available themes in real-time
 * Demonstrates the power of semantic theme portability
 */

export class ThemeSwitcher {
  constructor(engines, config) {
    this.engines = engines;
    this.config = config;
    this.currentThemeId = 'desert'; // Default theme
  }

  /**
   * Switch to a different theme
   * @param {string} themeId - Theme identifier (desert, graphite, etc.)
   */
  switchTheme(themeId) {
    const { themeEngine } = this.engines;

    // Validate theme exists
    if (!this.config.theme.availableThemes.includes(themeId)) {
      console.error(`[ThemeSwitcher] Invalid theme: ${themeId}`);
      return;
    }

    // Load the new theme
    const newTheme = this.config.theme.getTheme(themeId);
    themeEngine.loadSemanticTheme(newTheme);

    // CRITICAL: Also apply legacy theme to update CSS variables
    // This updates the generated CSS stylesheet
    themeEngine.applyTheme(themeId === 'graphite' ? 'ocean' : 'desert');
    console.log(`[ThemeSwitcher] Applied legacy theme: ${themeId === 'graphite' ? 'ocean' : 'desert'}`);

    // V3.0: Apply theme-specific effects (charcoal effects, paper texture, etc.)
    themeEngine.applyThemeEffects();
    console.log('[ThemeSwitcher] Applied theme effects');

    // Update current theme ID
    this.currentThemeId = themeId;

    // Log theme switch
    console.log(`[ThemeSwitcher] Switched to ${newTheme.name} theme`);

    // Trigger re-render (application-specific)
    if (window.renderDashboard) {
      window.renderDashboard();
    }

    // Update UI to show active theme
    this.updateActiveState();
  }

  /**
   * Update active state in the UI
   */
  updateActiveState() {
    // Remove active class from all buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.classList.remove('active');
    });

    // Add active class to current theme button
    const activeBtn = document.querySelector(`[data-theme="${this.currentThemeId}"]`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }
  }

  /**
   * Render theme switcher UI
   * @returns {string} HTML string
   */
  render() {
    const { themeEngine } = this.engines;

    // Get current theme colors for styling the switcher
    const textPrimary = themeEngine.getSemanticTextColor('primary');
    const textSecondary = themeEngine.getSemanticTextColor('secondary');
    const borderColor = themeEngine.getSemanticBorderColor('default');
    const accentPrimary = themeEngine.getSemanticAccentColor('primary');
    const backgroundCard = themeEngine.getSemanticBackgroundColor('card');
    const backgroundHover = themeEngine.getSemanticBackgroundColor('hover');

    // Get available themes
    const themes = this.config.theme.availableThemes;

    // Generate theme buttons
    const themeButtons = themes.map(themeId => {
      const theme = this.config.theme.getTheme(themeId);
      const isActive = themeId === this.currentThemeId;

      return `
        <button
          class="theme-btn ${isActive ? 'active' : ''}"
          data-theme="${themeId}"
          onclick="window.themeSwitcher && window.themeSwitcher.switchTheme('${themeId}')"
          style="
            padding: 0.75rem 1.5rem;
            border: 2px solid ${isActive ? accentPrimary : borderColor};
            border-radius: 0.5rem;
            background: ${isActive ? accentPrimary : backgroundCard};
            color: ${isActive ? '#FFFFFF' : textPrimary};
            font-weight: ${isActive ? '600' : '500'};
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.875rem;
          "
          onmouseover="if (!this.classList.contains('active')) { this.style.background='${backgroundHover}'; this.style.borderColor='${accentPrimary}'; }"
          onmouseout="if (!this.classList.contains('active')) { this.style.background='${backgroundCard}'; this.style.borderColor='${borderColor}'; }"
        >
          ${theme.name}
        </button>
      `;
    }).join('');

    const html = `
      <div class="theme-switcher-container" style="
        background: ${backgroundCard};
        border: 1px solid ${borderColor};
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
      ">
        <div style="margin-bottom: 1rem;">
          <h3 style="
            font-size: 1rem;
            font-weight: 600;
            color: ${textPrimary};
            margin: 0 0 0.25rem 0;
          ">
            🎨 Theme Switcher
          </h3>
          <p style="
            font-size: 0.875rem;
            color: ${textSecondary};
            margin: 0;
          ">
            Switch themes in real-time to see semantic color system in action
          </p>
        </div>

        <div style="
          display: flex;
          gap: 0.75rem;
          flex-wrap: wrap;
        ">
          ${themeButtons}
        </div>

        <!-- Theme Info -->
        <div style="
          margin-top: 1rem;
          padding: 0.75rem;
          background: ${backgroundHover};
          border-radius: 0.5rem;
          border-left: 3px solid ${accentPrimary};
        ">
          <div style="font-size: 0.75rem; color: ${textSecondary};">
            <strong>Current Theme:</strong> ${this.config.theme.getTheme(this.currentThemeId).name}
          </div>
        </div>
      </div>
    `;

    return html;
  }

  /**
   * Initialize theme switcher in the DOM
   */
  initialize() {
    const container = document.getElementById('theme-switcher');
    if (container) {
      container.innerHTML = this.render();
      this.updateActiveState();
    }

    // Make switcher globally accessible
    window.themeSwitcher = this;

    console.log('[ThemeSwitcher] Initialized');
  }
}

export default ThemeSwitcher;
