/**
 * Dashboard V3 - Engine System Index
 *
 * Central hub for all engine systems
 *
 * Usage:
 * ```javascript
 * import { initializeEngines } from './engines/index.js';
 * import config from './shared/config/index.js';
 *
 * const engines = initializeEngines(config);
 * // All engines are now ready to use
 * ```
 */

import ThemeEngine from './ThemeEngine.js';
import LayoutEngine from './LayoutEngine.js';
import BusinessEngine from './BusinessEngine.js';
import DeviceRouter from './DeviceRouter.js';
import ConfigValidator from './ConfigValidator.js';

/**
 * Initialize all engines
 * @param {Object} config - Configuration object
 * @returns {Object} Initialized engines
 */
export function initializeEngines(config) {
  console.log('[Engines] Initializing all engines...');

  // Validate configuration first
  const validator = new ConfigValidator(config);
  const validationReport = validator.getReport();

  if (!validationReport.valid) {
    console.error('[Engines] Configuration validation failed!');
    console.error('Errors:', validationReport.errors);
    throw new Error('Configuration validation failed. Cannot initialize engines.');
  }

  console.log('[Engines] Configuration validated successfully ✅');

  // Initialize all engines
  const themeEngine = new ThemeEngine(config);
  const layoutEngine = new LayoutEngine(config);
  const businessEngine = new BusinessEngine(config);
  const deviceRouter = new DeviceRouter(config);

  console.log('[Engines] All engines initialized successfully ✅');

  // Return engine instances
  return {
    validator,
    themeEngine,
    layoutEngine,
    businessEngine,
    deviceRouter,
  };
}

/**
 * Get engine statistics
 * @param {Object} engines - Engines object from initializeEngines
 * @returns {Object} Combined statistics
 */
export function getEngineStats(engines) {
  return {
    validator: engines.validator.getStats ? engines.validator.getStats() : null,
    theme: engines.themeEngine.getStats(),
    layout: engines.layoutEngine.getStats(),
    business: engines.businessEngine.getStats(),
    device: engines.deviceRouter.getStats(),
  };
}

/**
 * Destroy all engines
 * @param {Object} engines - Engines object from initializeEngines
 */
export function destroyEngines(engines) {
  console.log('[Engines] Destroying all engines...');

  if (engines.themeEngine) engines.themeEngine.destroy();
  if (engines.layoutEngine) engines.layoutEngine.destroy();
  if (engines.businessEngine) engines.businessEngine.destroy();
  if (engines.deviceRouter) engines.deviceRouter.destroy();
  if (engines.validator) engines.validator.destroy();

  console.log('[Engines] All engines destroyed');
}

// Export individual engines
export {
  ThemeEngine,
  LayoutEngine,
  BusinessEngine,
  DeviceRouter,
  ConfigValidator,
};

// Default export
export default {
  initializeEngines,
  getEngineStats,
  destroyEngines,
  ThemeEngine,
  LayoutEngine,
  BusinessEngine,
  DeviceRouter,
  ConfigValidator,
};
