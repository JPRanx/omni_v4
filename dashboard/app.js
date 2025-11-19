/**
 * Dashboard V3 - iPad App Entry Point
 *
 * Initializes all engines and orchestrates components
 * NO hardcoded values - everything comes from engines
 */

// Import configuration and engines
import config from '../shared/config/index.js';
import { initializeEngines } from '../engines/index.js';

// Import components
import { renderHeader } from './components/Header.js';
import { renderWeekTabs } from './components/WeekTabs.js';
import { renderOverviewCard } from './components/OverviewCard.js';
import { renderRestaurantCards } from './components/RestaurantCards.js';
import { renderAutoClockoutTable } from './components/AutoClockoutTable.js';
import { initializeInvestigationModal } from './components/InvestigationModal.js';
import { initializeOvertimeDetailsModal } from './components/OvertimeDetailsModal.js';
import { initializeCashFlowModal } from './components/CashFlowModal.js';
import { ThemeSwitcher } from './components/ThemeSwitcher.js';

// Import utilities
import { DataValidator } from '../shared/utils/dataValidator.js';

// Import V4 data directly - no more services needed
import { v4Data } from './data/v4Data.js';

/**
 * Main App Class
 */
class DashboardApp {
  constructor() {
    this.engines = null;
    this.currentWeek = null; // Will be set to most recent week
    this.data = v4Data; // Just use the data directly!
    this.components = {};
    this.validationReport = null;

    console.log('[App] Dashboard initialized with local v4Data');
  }

  /**
   * Initialize the application - SIMPLIFIED VERSION
   */
  initialize() {
    try {
      console.log('[App] Initializing Dashboard V3 (Simple Mode)...');

      // Step 1: Initialize engines
      this.engines = initializeEngines(config);
      console.log('[App] ✅ Engines initialized');

      // Step 2: Validate configuration
      const validationReport = this.engines.validator.getReport();
      if (!validationReport.valid) {
        throw new Error('Configuration validation failed');
      }
      console.log('[App] ✅ Configuration validated');

      // Step 3: Apply theme (legacy)
      this.engines.themeEngine.applyTheme('desert');
      console.log('[App] ✅ Theme applied');

      // Step 3b: Load semantic theme (V3.0)
      const desertTheme = config.theme.getTheme('desert');
      this.engines.themeEngine.loadSemanticTheme(desertTheme);
      console.log('[App] ✅ Semantic theme loaded:', desertTheme.name);

      // Step 4: Check device routing
      const deviceType = this.engines.deviceRouter.getDeviceType();
      const route = this.engines.deviceRouter.getRoute();
      console.log(`[App] Device: ${deviceType}, Route: ${route}`);

      // Step 5: Data is already loaded (v4Data)
      console.log('[App] ✅ Data ready from v4Data.js');

      // Set current week to most recent week
      const allWeeks = Object.keys(this.data);
      const weekNumbers = allWeeks.map(w => parseInt(w.replace('week', ''))).sort((a, b) => b - a);
      this.currentWeek = `week${weekNumbers[0]}`; // Most recent week
      console.log(`[App] Default week set to: ${this.currentWeek}`);

      // Step 5b: Validate data consistency
      const weekData = this.data[this.currentWeek];
      const validator = new DataValidator();
      this.validationReport = validator.validateAll(weekData);

      if (!this.validationReport.valid) {
        validator.logReport(this.validationReport);
      } else {
        console.log('[App] ✅ Data consistency validated');
      }

      // Step 6: Render components
      this.renderApp();
      console.log('[App] ✅ Components rendered');

      // Step 7: Hide loading, show app
      this.showApp();
      console.log('[App] ✅ Dashboard ready!');

      // Log stats
      this.logStats();

    } catch (error) {
      console.error('[App] Initialization failed:', error);
      this.showError(error.message);
    }
  }

  /**
   * Render all components
   */
  renderApp() {
    const weekData = this.data[this.currentWeek];

    // Render header
    renderHeader(this.engines, {
      title: config.content.labels.header.mainTitle,
      subtitle: config.content.labels.header.subtitle,
      weekNumber: this.currentWeek.replace('week', ''),
    });

    // Render week tabs
    renderWeekTabs(this.engines, {
      weeks: Object.keys(this.data),
      currentWeek: this.currentWeek,
      weekData: this.data, // Pass full data for date extraction
      onWeekChange: (week) => this.onWeekChange(week),
    });

    // Render theme switcher (V3.0)
    if (!this.components.themeSwitcher) {
      this.components.themeSwitcher = new ThemeSwitcher(this.engines, config);
    }
    this.components.themeSwitcher.initialize();

    // Render data source toggle
    // Render overview card
    renderOverviewCard(this.engines, {
      data: weekData.overview,
    });

    // Render restaurant cards
    renderRestaurantCards(this.engines, {
      restaurants: weekData.restaurants,
      cashFlow: weekData.overview?.cashFlow,
      onInvestigate: (restaurant) => this.onInvestigate(restaurant),
    });

    // Render auto clockout table
    renderAutoClockoutTable(this.engines, {
      employees: weekData.autoClockoutAlerts,
    });

    // Initialize investigation modal
    initializeInvestigationModal(this.engines);

    // Initialize overtime details modal
    initializeOvertimeDetailsModal(this.engines);

    // Initialize cash flow modal
    initializeCashFlowModal(this.engines);
  }

  /**
   * Handle week change
   */
  onWeekChange(week) {
    console.log(`[App] Week changed to: ${week}`);
    this.currentWeek = week;

    // Re-render components with new data
    this.renderApp();
  }

  /**
   * Handle restaurant investigation
   */
  onInvestigate(restaurant) {
    console.log(`[App] Investigating restaurant:`, restaurant.name);

    // Get modal element
    const modal = document.getElementById('investigation-modal');
    const event = new CustomEvent('open-investigation', {
      detail: { restaurant }
    });
    modal.dispatchEvent(event);
  }

  /**
   * Show app, hide loading
   */
  showApp() {
    const loading = document.getElementById('loading');
    const app = document.getElementById('app');

    setTimeout(() => {
      loading.classList.add('hidden');
      app.classList.add('loaded');
    }, 500);
  }

  /**
   * Show error message
   */
  showError(message) {
    const loading = document.getElementById('loading');
    loading.innerHTML = `
      <div style="text-align: center; color: #DC2626;">
        <h2 style="font-size: 24px; margin-bottom: 16px;">⚠️ Error</h2>
        <p style="margin-bottom: 16px;">${message}</p>
        <button onclick="location.reload()" style="padding: 8px 16px; background: #B89968; color: white; border: none; border-radius: 8px; cursor: pointer;">
          Reload Dashboard
        </button>
      </div>
    `;
  }

  /**
   * Log application statistics
   */
  logStats() {
    console.group('[App] Dashboard Statistics');

    // Engine stats
    console.log('Theme:', this.engines.themeEngine.getStats());
    console.log('Layout:', this.engines.layoutEngine.getStats());
    console.log('Business:', this.engines.businessEngine.getStats());
    console.log('Device:', this.engines.deviceRouter.getStats());

    // Data stats
    console.log('Weeks Loaded:', Object.keys(this.data).length);
    console.log('Current Week:', this.currentWeek);

    // Configuration stats
    console.log('Total Configs:', config.totalConfigs);
    console.log('Version:', config.version);

    console.groupEnd();
  }

  /**
   * Get engine instance
   */
  getEngine(engineName) {
    return this.engines[engineName];
  }

  /**
   * Get current data
   */
  getCurrentData() {
    return this.data[this.currentWeek];
  }

  /**
   * Get validation report
   */
  getValidationReport() {
    return this.validationReport;
  }

  /**
   * Toggle data source mode (local file vs Supabase)
   *
   * @param {'local' | 'supabase'} mode - Data source mode
   */
  // Data source methods removed - we're using simple mode now!
}

// ============================================
// Initialize App
// ============================================

// Create app instance
const app = new DashboardApp();

// Start initialization when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    app.initialize();
  });
} else {
  app.initialize();
}

// Expose app globally for debugging
window.dashboardApp = app;

// Expose data consistency checker to console
window.checkDataConsistency = function() {
  const report = window.dashboardApp?.getValidationReport();

  if (!report) {
    console.warn('No validation report available yet. Dashboard may still be loading.');
    return null;
  }

  if (report.valid) {
    console.log('%c✅ All data consistency checks passed!', 'color: #10B981; font-weight: bold; font-size: 14px;');
    console.log(`${report.summary.totalChecks} checks completed successfully.`);
  } else {
    console.group('%c❌ Data Consistency Issues', 'color: #EF4444; font-weight: bold; font-size: 14px;');
    console.log(`${report.summary.passed}/${report.summary.totalChecks} checks passed (${report.summary.passRate}%)`);
    console.log('');

    report.errors.forEach((error, index) => {
      console.group(`%c${index + 1}. ${error.field}`, 'font-weight: bold;');
      console.log('Overview value:', error.overview);
      console.log('Calculated sum:', error.calculated);
      console.log('%cDifference:', 'font-weight: bold; color: #EF4444;', error.diff.toFixed(2));
      if (error.restaurants) {
        console.table(error.restaurants);
      }
      console.groupEnd();
    });

    console.groupEnd();
  }

  return report;
};

console.log('%cℹ️ Tip: Run window.checkDataConsistency() to validate dashboard data', 'color: #3B82F6; font-style: italic;');

// Expose renderDashboard globally for theme switching (V3.0)
window.renderDashboard = () => {
  app.renderApp();
};

// Export for module usage
export default app;
