/**
 * Dashboard V3 - Device Router
 *
 * Smart system that detects device type and routes to appropriate interface
 *
 * Responsibilities:
 * - Detect device type (iPad, iPhone, Desktop)
 * - Route to appropriate interface (/ipad or /mobile)
 * - Handle capability detection
 * - Manage feature availability per device
 * - Provide device-specific optimizations
 *
 * Usage:
 * ```javascript
 * import DeviceRouter from './engines/DeviceRouter.js';
 * import config from './shared/config/index.js';
 *
 * const router = new DeviceRouter(config);
 * const route = router.getRoute(); // Returns '/ipad' or '/mobile' or '/desktop'
 * router.navigate(); // Auto-navigate to appropriate interface
 * ```
 */

class DeviceRouter {
  constructor(config) {
    if (!config) {
      throw new Error('DeviceRouter: config is required');
    }

    this.config = config;
    this.initialized = false;

    // Feature configuration
    this.capabilities = config.features.capabilities;
    this.toggles = config.features.toggles;

    // Device info
    this.deviceType = null;
    this.capabilities = null;
    this.route = null;

    this.initialize();
  }

  /**
   * Initialize device router
   */
  initialize() {
    if (this.initialized) {
      console.warn('DeviceRouter: Already initialized');
      return;
    }

    console.log('[DeviceRouter] Initializing...');

    // Detect device and capabilities
    this.detectDevice();
    this.detectCapabilities();
    this.determineRoute();

    this.initialized = true;
    console.log('[DeviceRouter] Initialized successfully');
    console.log(`[DeviceRouter] Device: ${this.deviceType}, Route: ${this.route}`);
  }

  /**
   * Detect device type
   */
  detectDevice() {
    if (typeof window === 'undefined') {
      this.deviceType = 'desktop';
      return;
    }

    const capabilities = this.config.features.capabilities;

    // Use capability detection from config
    if (capabilities.device.isMobile()) {
      this.deviceType = 'mobile';
    } else if (capabilities.device.isIPad()) {
      this.deviceType = 'ipad';
    } else if (capabilities.device.isTablet()) {
      this.deviceType = 'tablet';
    } else {
      this.deviceType = 'desktop';
    }

    // Additional user agent checks for iOS devices
    const userAgent = navigator.userAgent || '';
    if (/iPad/i.test(userAgent)) {
      this.deviceType = 'ipad';
    } else if (/iPhone|iPod/i.test(userAgent)) {
      this.deviceType = 'mobile';
    }

    console.log(`[DeviceRouter] Detected device: ${this.deviceType}`);
  }

  /**
   * Detect device capabilities
   */
  detectCapabilities() {
    const capabilities = this.config.features.capabilities;

    this.capabilities = {
      // Device detection
      isMobile: capabilities.device.isMobile(),
      isTablet: capabilities.device.isTablet(),
      isIPad: capabilities.device.isIPad(),
      isDesktop: capabilities.device.isDesktop(),

      // Feature support
      hasTouch: capabilities.support.hasTouch(),
      hasHover: capabilities.support.hasHover(),
      hasAnimations: capabilities.support.hasAnimations(),
      orientation: capabilities.support.getOrientation(),

      // Performance
      hasGPU: capabilities.performance.hasGPU(),
      isHighDPI: capabilities.performance.isHighDPI(),
      connectionType: capabilities.performance.getConnectionType(),
      hasFastConnection: capabilities.performance.hasFastConnection(),
      deviceMemory: capabilities.performance.getDeviceMemory(),

      // Adaptations
      shouldEnableHover: capabilities.adaptation.shouldEnableHover(),
      shouldEnableAnimations: capabilities.adaptation.shouldEnableAnimations(),
      shouldUseLightweight: capabilities.adaptation.shouldUseLightweight(),
    };

    console.log('[DeviceRouter] Capabilities detected:', this.capabilities);
  }

  /**
   * Determine appropriate route based on device
   */
  determineRoute() {
    switch (this.deviceType) {
      case 'ipad':
      case 'tablet':
        this.route = '/ipad';
        break;

      case 'mobile':
        this.route = '/mobile';
        break;

      case 'desktop':
      default:
        this.route = '/ipad'; // Desktop uses iPad interface (full experience)
        break;
    }

    console.log(`[DeviceRouter] Route determined: ${this.route}`);
  }

  /**
   * Get current device type
   * @returns {string} Device type
   */
  getDeviceType() {
    return this.deviceType;
  }

  /**
   * Get current route
   * @returns {string} Route path
   */
  getRoute() {
    return this.route;
  }

  /**
   * Get device capabilities
   * @returns {Object} Capabilities object
   */
  getCapabilities() {
    return this.capabilities;
  }

  /**
   * Check if device is mobile
   * @returns {boolean} True if mobile
   */
  isMobile() {
    return this.deviceType === 'mobile';
  }

  /**
   * Check if device is iPad
   * @returns {boolean} True if iPad
   */
  isIPad() {
    return this.deviceType === 'ipad';
  }

  /**
   * Check if device is tablet
   * @returns {boolean} True if tablet
   */
  isTablet() {
    return this.deviceType === 'tablet';
  }

  /**
   * Check if device is desktop
   * @returns {boolean} True if desktop
   */
  isDesktop() {
    return this.deviceType === 'desktop';
  }

  /**
   * Check if feature is available on current device
   * @param {string} featureName - Feature name
   * @returns {boolean} True if available
   */
  isFeatureAvailable(featureName) {
    const toggles = this.config.features.toggles;

    // Check in core features
    if (toggles.core[featureName]) {
      return toggles.core[featureName].enabled;
    }

    // Check in optional features
    if (toggles.optional[featureName]) {
      const feature = toggles.optional[featureName];

      // Some features may be disabled on mobile for performance
      if (this.isMobile() && featureName === 'gradientAnimations') {
        return this.capabilities.hasFastConnection;
      }

      return feature.enabled;
    }

    // Check in experimental features
    if (toggles.experimental[featureName]) {
      return toggles.experimental[featureName].enabled;
    }

    return false;
  }

  /**
   * Get enabled features for current device
   * @returns {Array<string>} Array of enabled feature names
   */
  getEnabledFeatures() {
    const toggles = this.config.features.toggles;
    const enabled = [];

    // Core features
    Object.entries(toggles.core).forEach(([key, feature]) => {
      if (feature.enabled) enabled.push(key);
    });

    // Optional features (with device-specific checks)
    Object.entries(toggles.optional).forEach(([key, feature]) => {
      if (this.isFeatureAvailable(key)) {
        enabled.push(key);
      }
    });

    // Experimental features
    Object.entries(toggles.experimental).forEach(([key, feature]) => {
      if (feature.enabled) enabled.push(key);
    });

    return enabled;
  }

  /**
   * Get device-specific optimizations
   * @returns {Object} Optimization settings
   */
  getOptimizations() {
    return {
      // Use lightweight mode for low-end devices
      useLightweightMode: this.capabilities.shouldUseLightweight,

      // Enable/disable animations
      enableAnimations: this.capabilities.shouldEnableAnimations,

      // Enable/disable hover effects
      enableHover: this.capabilities.shouldEnableHover,

      // Lazy load images on mobile or slow connections
      lazyLoadImages: this.isMobile() || !this.capabilities.hasFastConnection,

      // Reduce image quality on mobile
      reduceImageQuality: this.isMobile(),

      // Use smaller font sizes on mobile
      useMobileFonts: this.isMobile(),

      // Reduce grid complexity on mobile
      simplifyGrids: this.isMobile(),

      // GPU acceleration
      enableGPU: this.capabilities.hasGPU,

      // Preload critical resources
      preloadResources: this.capabilities.hasFastConnection,
    };
  }

  /**
   * Navigate to appropriate interface
   * @param {boolean} replace - Replace history instead of push (default: false)
   */
  navigate(replace = false) {
    if (typeof window === 'undefined') {
      console.warn('[DeviceRouter] Cannot navigate in non-browser environment');
      return;
    }

    // Check if already on correct route
    const currentPath = window.location.pathname;
    if (currentPath.startsWith(this.route)) {
      console.log(`[DeviceRouter] Already on correct route: ${this.route}`);
      return;
    }

    console.log(`[DeviceRouter] Navigating from ${currentPath} to ${this.route}`);

    if (replace) {
      window.location.replace(this.route);
    } else {
      window.location.href = this.route;
    }
  }

  /**
   * Check if should redirect (not on correct route)
   * @returns {boolean} True if redirect needed
   */
  shouldRedirect() {
    if (typeof window === 'undefined') return false;

    const currentPath = window.location.pathname;
    return !currentPath.startsWith(this.route);
  }

  /**
   * Get interface configuration for current device
   * @returns {Object} Interface config
   */
  getInterfaceConfig() {
    const layout = this.config.layout;

    return {
      deviceType: this.deviceType,
      route: this.route,

      // Layout settings
      gridColumns: {
        metrics: this.isMobile() ? 1 : this.isIPad() ? 2 : 3,
        restaurants: this.isMobile() ? 1 : this.isIPad() ? 2 : 3,
      },

      // Container settings
      containerMaxWidth: this.isMobile() ? '100%' : layout.containers.maxWidths.dashboard,

      // Features
      enabledFeatures: this.getEnabledFeatures(),

      // Optimizations
      optimizations: this.getOptimizations(),

      // Capabilities
      capabilities: this.capabilities,
    };
  }

  /**
   * Generate device report
   * @returns {Object} Complete device report
   */
  getDeviceReport() {
    return {
      device: {
        type: this.deviceType,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'N/A',
        platform: typeof navigator !== 'undefined' ? navigator.platform : 'N/A',
        screenSize: typeof window !== 'undefined'
          ? `${window.innerWidth}x${window.innerHeight}`
          : 'N/A',
      },
      routing: {
        route: this.route,
        shouldRedirect: this.shouldRedirect(),
        currentPath: typeof window !== 'undefined' ? window.location.pathname : 'N/A',
      },
      capabilities: this.capabilities,
      features: {
        enabled: this.getEnabledFeatures(),
        total: this.getEnabledFeatures().length,
      },
      optimizations: this.getOptimizations(),
      interfaceConfig: this.getInterfaceConfig(),
    };
  }

  /**
   * Log device information to console
   */
  logDeviceInfo() {
    const report = this.getDeviceReport();
    console.group('[DeviceRouter] Device Information');
    console.log('Device Type:', report.device.type);
    console.log('Route:', report.routing.route);
    console.log('Screen Size:', report.device.screenSize);
    console.log('Capabilities:', report.capabilities);
    console.log('Enabled Features:', report.features.enabled);
    console.log('Optimizations:', report.optimizations);
    console.groupEnd();
  }

  /**
   * Get router statistics
   * @returns {Object} Router stats
   */
  getStats() {
    return {
      deviceType: this.deviceType,
      route: this.route,
      enabledFeatures: this.getEnabledFeatures().length,
      hasTouch: this.capabilities?.hasTouch || false,
      hasHover: this.capabilities?.hasHover || false,
      initialized: this.initialized,
    };
  }

  /**
   * Cleanup
   */
  destroy() {
    console.log('[DeviceRouter] Destroying...');
    this.initialized = false;
    console.log('[DeviceRouter] Destroyed');
  }
}

export default DeviceRouter;
