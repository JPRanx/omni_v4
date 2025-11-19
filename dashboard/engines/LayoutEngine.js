/**
 * Dashboard V3 - Layout Engine
 *
 * Smart system that manages grid layouts and responsive behavior
 *
 * Responsibilities:
 * - Manage grid layouts from config
 * - Handle responsive breakpoints
 * - Return appropriate layout for current device
 * - Manage container widths and spacing
 * - Provide layout utilities and helpers
 *
 * Usage:
 * ```javascript
 * import LayoutEngine from './engines/LayoutEngine.js';
 * import config from './shared/config/index.js';
 *
 * const layoutEngine = new LayoutEngine(config);
 * const gridClasses = layoutEngine.getGridClasses('metrics'); // Returns responsive grid classes
 * ```
 */

class LayoutEngine {
  constructor(config) {
    if (!config) {
      throw new Error('LayoutEngine: config is required');
    }

    this.config = config;
    this.initialized = false;
    this.currentBreakpoint = null;
    this.currentDevice = null;
    this.resizeListener = null;

    // Layout configuration
    this.grids = config.layout.grids;
    this.containers = config.layout.containers;
    this.breakpoints = config.layout.breakpoints;
    this.zindex = config.layout.zindex;

    this.initialize();
  }

  /**
   * Initialize layout engine
   */
  initialize() {
    if (this.initialized) {
      console.warn('LayoutEngine: Already initialized');
      return;
    }

    console.log('[LayoutEngine] Initializing...');

    // Detect initial device and breakpoint
    this.detectDevice();
    this.detectBreakpoint();

    // Set up resize listener
    this.setupResizeListener();

    this.initialized = true;
    console.log('[LayoutEngine] Initialized successfully');
    console.log(`[LayoutEngine] Device: ${this.currentDevice}, Breakpoint: ${this.currentBreakpoint}`);
  }

  /**
   * Detect current device type
   */
  detectDevice() {
    if (typeof window === 'undefined') {
      this.currentDevice = 'desktop';
      return;
    }

    const width = window.innerWidth;
    const breakpointValues = this.breakpoints.breakpointValues;

    if (width < breakpointValues.sm) {
      this.currentDevice = 'mobile';
    } else if (width >= breakpointValues.sm && width < breakpointValues.lg) {
      this.currentDevice = 'tablet';
    } else {
      this.currentDevice = 'desktop';
    }

    // Check for iPad-specific range
    if (width >= breakpointValues.ipadMin && width <= breakpointValues.ipadMax) {
      this.currentDevice = 'ipad';
    }
  }

  /**
   * Detect current breakpoint
   */
  detectBreakpoint() {
    if (typeof window === 'undefined') {
      this.currentBreakpoint = 'lg';
      return;
    }

    const width = window.innerWidth;
    const breakpointValues = this.breakpoints.breakpointValues;

    if (width < breakpointValues.sm) {
      this.currentBreakpoint = 'xs';
    } else if (width < breakpointValues.md) {
      this.currentBreakpoint = 'sm';
    } else if (width < breakpointValues.lg) {
      this.currentBreakpoint = 'md';
    } else if (width < breakpointValues.xl) {
      this.currentBreakpoint = 'lg';
    } else if (width < breakpointValues['2xl']) {
      this.currentBreakpoint = 'xl';
    } else {
      this.currentBreakpoint = '2xl';
    }
  }

  /**
   * Set up window resize listener
   */
  setupResizeListener() {
    if (typeof window === 'undefined') return;

    this.resizeListener = () => {
      const oldDevice = this.currentDevice;
      const oldBreakpoint = this.currentBreakpoint;

      this.detectDevice();
      this.detectBreakpoint();

      // Log changes
      if (oldDevice !== this.currentDevice || oldBreakpoint !== this.currentBreakpoint) {
        console.log(`[LayoutEngine] Layout changed: ${oldDevice}/${oldBreakpoint} → ${this.currentDevice}/${this.currentBreakpoint}`);
      }
    };

    window.addEventListener('resize', this.resizeListener);
  }

  /**
   * Get current device type
   * @returns {string} Device type ('mobile', 'tablet', 'ipad', 'desktop')
   */
  getCurrentDevice() {
    return this.currentDevice;
  }

  /**
   * Get current breakpoint
   * @returns {string} Breakpoint name ('xs', 'sm', 'md', 'lg', 'xl', '2xl')
   */
  getCurrentBreakpoint() {
    return this.currentBreakpoint;
  }

  /**
   * Check if current device matches type
   * @param {string} deviceType - Device type to check
   * @returns {boolean} True if matches
   */
  isDevice(deviceType) {
    return this.currentDevice === deviceType;
  }

  /**
   * Check if current viewport is mobile
   * @returns {boolean} True if mobile
   */
  isMobile() {
    return this.currentDevice === 'mobile';
  }

  /**
   * Check if current viewport is tablet
   * @returns {boolean} True if tablet
   */
  isTablet() {
    return this.currentDevice === 'tablet';
  }

  /**
   * Check if current viewport is iPad
   * @returns {boolean} True if iPad
   */
  isIPad() {
    return this.currentDevice === 'ipad';
  }

  /**
   * Check if current viewport is desktop
   * @returns {boolean} True if desktop
   */
  isDesktop() {
    return this.currentDevice === 'desktop';
  }

  /**
   * Get grid configuration
   * @param {string} gridName - Grid name (e.g., 'metrics', 'restaurants')
   * @returns {Object|null} Grid configuration or null
   */
  getGrid(gridName) {
    return this.grids.grids?.[gridName] || null;
  }

  /**
   * Get responsive grid classes for current device
   * @param {string} gridName - Grid name
   * @returns {string} Tailwind grid classes
   */
  getGridClasses(gridName) {
    const grid = this.getGrid(gridName);
    if (!grid) {
      console.warn(`LayoutEngine: Grid '${gridName}' not found`);
      return '';
    }

    // Return pre-configured responsive classes
    if (grid.container && typeof grid.container === 'string') {
      return grid.container;
    }

    // Build responsive classes based on current device
    const responsive = grid.responsive || {};
    let classes = [];

    if (this.isMobile() && responsive.mobile) {
      classes.push(responsive.mobile);
    } else if (this.isTablet() && responsive.tablet) {
      classes.push(responsive.tablet);
    } else if (responsive.desktop) {
      classes.push(responsive.desktop);
    }

    return classes.join(' ') || grid.container || '';
  }

  /**
   * Get grid columns for current device
   * @param {string} gridName - Grid name
   * @returns {number} Number of columns
   */
  getGridColumns(gridName) {
    const grid = this.getGrid(gridName);
    if (!grid) return 1;

    if (typeof grid.columns === 'number') {
      return grid.columns;
    }

    if (typeof grid.columns === 'object') {
      if (this.isMobile()) return grid.columns.mobile || 1;
      if (this.isTablet()) return grid.columns.tablet || 2;
      return grid.columns.desktop || 3;
    }

    return 1;
  }

  /**
   * Get container configuration
   * @param {string} variant - Container variant (e.g., 'dashboard', 'modal')
   * @returns {Object|null} Container configuration or null
   */
  getContainer(variant = 'dashboard') {
    return this.containers.variants?.[variant] || null;
  }

  /**
   * Get container classes
   * @param {string} variant - Container variant
   * @returns {string} Tailwind container classes
   */
  getContainerClasses(variant = 'dashboard') {
    const container = this.getContainer(variant);
    return container?.class || '';
  }

  /**
   * Get container max-width
   * @param {string} variant - Container variant
   * @returns {string} Max-width value
   */
  getContainerMaxWidth(variant = 'dashboard') {
    const container = this.getContainer(variant);
    return container?.maxWidth || this.containers.maxWidths.dashboard;
  }

  /**
   * Get z-index value
   * @param {string} layer - Layer name (e.g., 'modal', 'tooltip')
   * @returns {number} Z-index value
   */
  getZIndex(layer) {
    return this.zindex.layers?.[layer] || 0;
  }

  /**
   * Get component z-index
   * @param {string} component - Component name
   * @param {string} state - State name (optional)
   * @returns {number} Z-index value
   */
  getComponentZIndex(component, state = 'default') {
    const componentZ = this.zindex.components?.[component];
    if (!componentZ) return 0;

    if (typeof componentZ === 'number') return componentZ;
    return componentZ[state] || componentZ.default || 0;
  }

  /**
   * Get breakpoint value
   * @param {string} breakpoint - Breakpoint name
   * @returns {string} Breakpoint value (e.g., '768px')
   */
  getBreakpointValue(breakpoint) {
    return this.breakpoints.breakpoints?.[breakpoint] || null;
  }

  /**
   * Check if viewport is above breakpoint
   * @param {string} breakpoint - Breakpoint name
   * @returns {boolean} True if above breakpoint
   */
  isAboveBreakpoint(breakpoint) {
    if (typeof window === 'undefined') return false;

    const breakpointValue = this.breakpoints.breakpointValues?.[breakpoint];
    if (!breakpointValue) return false;

    return window.innerWidth >= breakpointValue;
  }

  /**
   * Check if viewport is below breakpoint
   * @param {string} breakpoint - Breakpoint name
   * @returns {boolean} True if below breakpoint
   */
  isBelowBreakpoint(breakpoint) {
    if (typeof window === 'undefined') return false;

    const breakpointValue = this.breakpoints.breakpointValues?.[breakpoint];
    if (!breakpointValue) return false;

    return window.innerWidth < breakpointValue;
  }

  /**
   * Get responsive pattern value
   * @param {string} pattern - Pattern name (e.g., 'typography.headerH1')
   * @returns {any} Pattern value for current device
   */
  getResponsivePattern(pattern) {
    const parts = pattern.split('.');
    let current = this.breakpoints.patterns;

    for (const part of parts) {
      if (current[part] === undefined) return null;
      current = current[part];
    }

    if (typeof current === 'object' && !Array.isArray(current)) {
      if (this.isMobile() && current.mobile) return current.mobile;
      if (this.isTablet() && current.tablet) return current.tablet;
      return current.default || current.desktop || null;
    }

    return current;
  }

  /**
   * Get media query string
   * @param {string} type - Query type ('mobile', 'tablet', 'desktop', 'ipad')
   * @returns {string} Media query string
   */
  getMediaQuery(type) {
    return this.breakpoints.mediaQueries?.[type] || '';
  }

  /**
   * Apply layout to element
   * @param {HTMLElement} element - DOM element
   * @param {string} gridName - Grid name to apply
   */
  applyLayout(element, gridName) {
    if (!element || typeof element.classList === 'undefined') {
      console.error('LayoutEngine: Invalid element provided');
      return;
    }

    const classes = this.getGridClasses(gridName);
    const classArray = classes.split(' ').filter(c => c.trim());

    classArray.forEach(className => {
      element.classList.add(className);
    });

    console.log(`[LayoutEngine] Applied ${gridName} layout to element`);
  }

  /**
   * Get layout recommendations for current device
   * @returns {Object} Layout recommendations
   */
  getLayoutRecommendations() {
    return {
      device: this.currentDevice,
      breakpoint: this.currentBreakpoint,
      gridColumns: {
        metrics: this.getGridColumns('metrics'),
        restaurants: this.getGridColumns('restaurants'),
        pnlQuadrant: this.getGridColumns('pnlQuadrant'),
      },
      containerMaxWidth: this.getContainerMaxWidth('dashboard'),
      recommendations: {
        useMobileLayout: this.isMobile(),
        useTabletLayout: this.isTablet(),
        useDesktopLayout: this.isDesktop(),
        stackCards: this.isMobile(),
        showSidebar: this.isDesktop(),
      },
    };
  }

  /**
   * Get layout statistics
   * @returns {Object} Layout stats
   */
  getStats() {
    return {
      currentDevice: this.currentDevice,
      currentBreakpoint: this.currentBreakpoint,
      totalGrids: Object.keys(this.grids.grids || {}).length,
      totalContainers: Object.keys(this.containers.variants || {}).length,
      totalBreakpoints: Object.keys(this.breakpoints.breakpoints || {}).length,
      totalZLayers: Object.keys(this.zindex.layers || {}).length,
      initialized: this.initialized,
    };
  }

  /**
   * Subscribe to layout changes
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  onLayoutChange(callback) {
    const listener = () => {
      callback({
        device: this.currentDevice,
        breakpoint: this.currentBreakpoint,
      });
    };

    window.addEventListener('resize', listener);

    // Return unsubscribe function
    return () => {
      window.removeEventListener('resize', listener);
    };
  }

  /**
   * Cleanup and remove listeners
   */
  destroy() {
    console.log('[LayoutEngine] Destroying...');

    if (this.resizeListener) {
      window.removeEventListener('resize', this.resizeListener);
      this.resizeListener = null;
    }

    this.initialized = false;
    console.log('[LayoutEngine] Destroyed');
  }
}

export default LayoutEngine;
