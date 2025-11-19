/**
 * Dashboard V3 - Device Capabilities
 *
 * Device capability detection and feature adaptation
 * Total Capabilities: 12
 *
 * Breakdown:
 * - Device Detection: 4 (mobile, tablet, desktop, iPad)
 * - Feature Support: 4 (touch, hover, animations, orientation)
 * - Performance: 4 (GPU, high-DPI, connection, memory)
 *
 * Source Files Analyzed:
 * - Responsive breakpoints and device targeting
 * - Animation and interaction patterns
 */

// ============================================
// DEVICE DETECTION (4 capabilities)
// ============================================

export const device = {
  /**
   * Check if device is mobile
   * @returns {boolean} True if mobile device
   */
  isMobile: () => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth < 768;
  },

  /**
   * Check if device is tablet
   * @returns {boolean} True if tablet device
   */
  isTablet: () => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth >= 768 && window.innerWidth < 1024;
  },

  /**
   * Check if device is desktop
   * @returns {boolean} True if desktop device
   */
  isDesktop: () => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth >= 1024;
  },

  /**
   * Check if device is iPad (specific range)
   * @returns {boolean} True if iPad range
   */
  isIPad: () => {
    if (typeof window === 'undefined') return false;
    const width = window.innerWidth;
    return width >= 768 && width <= 1024;
  },

  /**
   * Get current device type
   * @returns {string} Device type: 'mobile', 'tablet', 'desktop'
   */
  getDeviceType: () => {
    if (device.isMobile()) return 'mobile';
    if (device.isTablet()) return 'tablet';
    return 'desktop';
  },
};

// ============================================
// FEATURE SUPPORT (4 capabilities)
// ============================================

export const support = {
  /**
   * Check if device supports touch events
   * @returns {boolean} True if touch supported
   */
  hasTouch: () => {
    if (typeof window === 'undefined') return false;
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      navigator.msMaxTouchPoints > 0
    );
  },

  /**
   * Check if device supports hover
   * @returns {boolean} True if hover supported
   */
  hasHover: () => {
    if (typeof window === 'undefined') return true;
    return window.matchMedia('(hover: hover)').matches;
  },

  /**
   * Check if animations should be enabled
   * Respects prefers-reduced-motion
   * @returns {boolean} True if animations supported
   */
  hasAnimations: () => {
    if (typeof window === 'undefined') return true;
    return !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Check current orientation
   * @returns {string} 'portrait' or 'landscape'
   */
  getOrientation: () => {
    if (typeof window === 'undefined') return 'landscape';
    return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
  },

  /**
   * Check if orientation is portrait
   * @returns {boolean} True if portrait
   */
  isPortrait: () => {
    return support.getOrientation() === 'portrait';
  },

  /**
   * Check if orientation is landscape
   * @returns {boolean} True if landscape
   */
  isLandscape: () => {
    return support.getOrientation() === 'landscape';
  },
};

// ============================================
// PERFORMANCE CAPABILITIES (4 capabilities)
// ============================================

export const performance = {
  /**
   * Check if device has GPU acceleration
   * @returns {boolean} True if GPU available
   */
  hasGPU: () => {
    if (typeof window === 'undefined') return true;
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    return !!gl;
  },

  /**
   * Check if device is high-DPI (Retina)
   * @returns {boolean} True if high-DPI
   */
  isHighDPI: () => {
    if (typeof window === 'undefined') return false;
    return window.devicePixelRatio > 1;
  },

  /**
   * Check connection type (if available)
   * @returns {string|null} Connection type or null
   */
  getConnectionType: () => {
    if (typeof navigator === 'undefined' || !navigator.connection) return null;
    return navigator.connection.effectiveType || null;
  },

  /**
   * Check if connection is fast (4g or better)
   * @returns {boolean} True if fast connection
   */
  hasFastConnection: () => {
    const connType = performance.getConnectionType();
    if (!connType) return true; // Assume fast if unknown
    return connType === '4g' || connType === '5g';
  },

  /**
   * Estimate device memory (GB)
   * @returns {number|null} Memory in GB or null
   */
  getDeviceMemory: () => {
    if (typeof navigator === 'undefined' || !navigator.deviceMemory) return null;
    return navigator.deviceMemory;
  },

  /**
   * Check if device has sufficient memory (4GB+)
   * @returns {boolean} True if sufficient memory
   */
  hasSufficientMemory: () => {
    const memory = performance.getDeviceMemory();
    if (!memory) return true; // Assume sufficient if unknown
    return memory >= 4;
  },
};

// ============================================
// CAPABILITY-BASED FEATURE ADAPTATION
// ============================================

export const adaptation = {
  /**
   * Should enable hover effects
   * Only on devices with hover capability
   */
  shouldEnableHover: () => {
    return support.hasHover();
  },

  /**
   * Should enable animations
   * Based on user preference and device capability
   */
  shouldEnableAnimations: () => {
    return support.hasAnimations() && performance.hasGPU();
  },

  /**
   * Should enable GPU acceleration
   * Only if GPU available and fast connection
   */
  shouldEnableGPU: () => {
    return performance.hasGPU() && performance.hasFastConnection();
  },

  /**
   * Should use lightweight mode
   * For low-performance devices
   */
  shouldUseLightweight: () => {
    return (
      !performance.hasFastConnection() ||
      !performance.hasSufficientMemory() ||
      !performance.hasGPU()
    );
  },

  /**
   * Get recommended grid columns
   * Based on device type
   */
  getRecommendedColumns: () => {
    if (device.isMobile()) return 1;
    if (device.isTablet()) return 2;
    return 3;
  },

  /**
   * Get recommended animation duration
   * Faster on mobile for better perceived performance
   */
  getAnimationDuration: () => {
    if (device.isMobile()) return 200; // 200ms
    return 300; // 300ms
  },

  /**
   * Should lazy load images
   * Enable on slow connections or mobile
   */
  shouldLazyLoad: () => {
    return device.isMobile() || !performance.hasFastConnection();
  },
};

// ============================================
// ENVIRONMENT DETECTION
// ============================================

export const environment = {
  /**
   * Check if running in browser
   * @returns {boolean} True if browser environment
   */
  isBrowser: () => {
    return typeof window !== 'undefined' && typeof document !== 'undefined';
  },

  /**
   * Check if running in development mode
   * @returns {boolean} True if development
   */
  isDevelopment: () => {
    return process.env.NODE_ENV === 'development';
  },

  /**
   * Check if running in production
   * @returns {boolean} True if production
   */
  isProduction: () => {
    return process.env.NODE_ENV === 'production';
  },

  /**
   * Check if running in standalone mode (PWA)
   * @returns {boolean} True if standalone
   */
  isStandalone: () => {
    if (!environment.isBrowser()) return false;
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    );
  },
};

// ============================================
// CAPABILITY MATRIX
// Device-specific feature recommendations
// ============================================

export const matrix = {
  mobile: {
    device: 'mobile',
    gridColumns: 1,
    hoverEffects: false,
    animations: true,
    animationDuration: 200,
    lazyLoad: true,
    gpuAcceleration: false,
    reducedMotion: false,
  },

  tablet: {
    device: 'tablet',
    gridColumns: 2,
    hoverEffects: true,
    animations: true,
    animationDuration: 250,
    lazyLoad: false,
    gpuAcceleration: true,
    reducedMotion: false,
  },

  desktop: {
    device: 'desktop',
    gridColumns: 3,
    hoverEffects: true,
    animations: true,
    animationDuration: 300,
    lazyLoad: false,
    gpuAcceleration: true,
    reducedMotion: false,
  },

  /**
   * Get capability matrix for current device
   * @returns {Object} Capability matrix
   */
  getCurrent: () => {
    const deviceType = device.getDeviceType();
    const base = matrix[deviceType];

    return {
      ...base,
      hasTouch: support.hasTouch(),
      hasHover: support.hasHover(),
      hasAnimations: support.hasAnimations(),
      orientation: support.getOrientation(),
      hasGPU: performance.hasGPU(),
      isHighDPI: performance.isHighDPI(),
      connectionType: performance.getConnectionType(),
      deviceMemory: performance.getDeviceMemory(),
      lightweight: adaptation.shouldUseLightweight(),
    };
  },
};

// ============================================
// EVENT LISTENERS
// Capability change detection
// ============================================

export const listeners = {
  /**
   * Listen for orientation changes
   * @param {Function} callback - Callback function
   */
  onOrientationChange: (callback) => {
    if (!environment.isBrowser()) return;
    window.addEventListener('orientationchange', callback);
    window.addEventListener('resize', callback);
  },

  /**
   * Listen for connection changes
   * @param {Function} callback - Callback function
   */
  onConnectionChange: (callback) => {
    if (!environment.isBrowser() || !navigator.connection) return;
    navigator.connection.addEventListener('change', callback);
  },

  /**
   * Remove orientation listeners
   * @param {Function} callback - Callback function
   */
  removeOrientationListener: (callback) => {
    if (!environment.isBrowser()) return;
    window.removeEventListener('orientationchange', callback);
    window.removeEventListener('resize', callback);
  },

  /**
   * Remove connection listeners
   * @param {Function} callback - Callback function
   */
  removeConnectionListener: (callback) => {
    if (!environment.isBrowser() || !navigator.connection) return;
    navigator.connection.removeEventListener('change', callback);
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  device,
  support,
  performance,
  adaptation,
  environment,
  matrix,
  listeners,

  // Metadata
  totalCapabilities: 12,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
