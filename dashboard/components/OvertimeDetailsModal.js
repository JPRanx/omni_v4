/**
 * OvertimeDetailsModal.js
 *
 * Interactive modal for displaying detailed overtime analysis.
 * Opens when user clicks "Overtime Hours" metric in Overview Card.
 *
 * Features:
 * - Employee-level overtime breakdown
 * - Restaurant grouping
 * - Severity indicators (Normal/Warning/Critical)
 * - Summary statistics
 * - Sortable table
 *
 * @version 3.0
 * @follows InvestigationModal patterns
 */

class OvertimeDetailsModal {
  constructor(engines) {
    this.engines = engines;
    this.modal = null;
    this.currentData = null;
  }

  /**
   * Get theme colors from ThemeEngine
   * Replaces hardcoded colors with semantic theme extraction
   *
   * @returns {Object} Theme color object
   */
  getColors() {
    const { themeEngine } = this.engines;

    // V3.0 Semantic color extraction
    return {
      text: {
        primary: themeEngine.getSemanticTextColor('primary'),
        secondary: themeEngine.getSemanticTextColor('secondary'),
        muted: themeEngine.getSemanticTextColor('muted'),
      },
      status: {
        success: {
          bg: themeEngine.getSemanticStatusColor('success', 'bg'),
          text: themeEngine.getSemanticStatusColor('success', 'text'),
          border: themeEngine.getSemanticStatusColor('success', 'border'),
        },
        warning: {
          bg: themeEngine.getSemanticStatusColor('warning', 'bg'),
          text: themeEngine.getSemanticStatusColor('warning', 'text'),
          border: themeEngine.getSemanticStatusColor('warning', 'border'),
        },
        critical: {
          bg: themeEngine.getSemanticStatusColor('critical', 'bg'),
          text: themeEngine.getSemanticStatusColor('critical', 'text'),
          border: themeEngine.getSemanticStatusColor('critical', 'border'),
        },
        normal: {
          bg: themeEngine.getSemanticStatusColor('normal', 'bg'),
          text: themeEngine.getSemanticStatusColor('normal', 'text'),
          border: themeEngine.getSemanticStatusColor('normal', 'border'),
        },
      },
      border: themeEngine.getSemanticBorderColor('default'),
      accent: themeEngine.getSemanticAccentColor('primary'),
    };
  }

  /**
   * Render modal HTML structure
   * Follows InvestigationModal pattern
   *
   * @returns {string} Modal HTML
   */
  render() {
    return `
      <div class="modal-overlay hidden">
        <div class="modal-container">

          <!-- Modal Header with Gradient -->
          <div class="modal-header">
            <div class="modal-header-content">
              <h2 id="overtimeModalTitle" class="modal-title">
                ⏰ Overtime Details
              </h2>
            </div>
            <button onclick="window.closeOvertimeModal()" class="modal-close-btn">
              ×
            </button>
          </div>

          <!-- Modal Body -->
          <div id="overtimeModalBody" class="modal-body">
            <!-- Content populated by buildContentHTML() -->
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button onclick="window.closeOvertimeModal()" class="modal-footer-btn">
              Close
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Open modal with employee overtime data
   *
   * @param {Array} employees - Array of employee overtime records
   */
  open(employees) {
    this.currentData = employees || [];

    // VALIDATION: Check if modal total matches overview
    const modalTotal = employees.reduce((sum, e) => sum + (e.overtime_hours || 0), 0);
    const weekData = window.dashboardApp?.getCurrentData();
    const overviewTotal = weekData?.overview?.overtimeHours || 0;

    if (Math.abs(modalTotal - overviewTotal) > 0.1) {
      console.warn(`⚠️ OVERTIME HOURS MISMATCH DETECTED:
  Overview Card shows:     ${overviewTotal.toFixed(1)}h
  Modal calculated total:  ${modalTotal.toFixed(1)}h
  Difference:              ${(modalTotal - overviewTotal).toFixed(1)}h

  This indicates a data consistency issue. The numbers should match.
  Check sampleData.js overview.overtimeHours value.`);
    }

    const modalContainer = document.getElementById('overtime-modal');
    const modal = modalContainer ? modalContainer.querySelector('.modal-overlay') : null;

    if (modal) {
      modalContainer.classList.remove('hidden');
      modal.classList.remove('hidden');
      this.loadContent();
    }
  }

  /**
   * Load content into modal body
   */
  loadContent() {
    const container = document.getElementById('overtimeModalBody');
    if (container) {
      container.innerHTML = this.buildContentHTML();
    }
  }

  /**
   * Calculate overtime totals from employee data
   *
   * @param {Array} employees - Employee overtime records
   * @returns {Object} Aggregated totals
   */
  calculateOvertimeTotals(employees) {
    const totalOTHours = employees.reduce((sum, e) => sum + (e.overtime_hours || 0), 0);
    const totalOTCost = employees.reduce((sum, e) => sum + (e.overtime_cost || 0), 0);

    return {
      totalEmployees: employees.length,
      totalOTHours: totalOTHours,
      totalOTCost: totalOTCost,
      avgOTHours: employees.length > 0 ? totalOTHours / employees.length : 0
    };
  }

  /**
   * Get hierarchy order for position-based sorting
   * Based on manager identification system in main_v3.py
   *
   * @param {string} jobTitle - Employee job title
   * @returns {number} Hierarchy level (1 = highest)
   */
  getHierarchyOrder(jobTitle) {
    const hierarchyMap = {
      'General Manager': 1,
      'Kitchen Manager': 2,
      'Sous Chef': 3,
      'Manager': 3,
      'Supervisor': 4,
      'Bartender': 5,
      'Line Cook': 5,
      'Server': 5,
      'Prep Cook': 5,
      'Dishwasher': 6,
      'Staff': 7,
    };

    // Return hierarchy level or default to 999 for unknown positions
    return hierarchyMap[jobTitle] || 999;
  }

  /**
   * Sort employees by: Restaurant → Hierarchy → Overtime Hours (descending)
   *
   * @param {Array} employees - Employee overtime records
   * @returns {Array} Sorted employees
   */
  sortEmployees(employees) {
    return [...employees].sort((a, b) => {
      // 1. Sort by restaurant (alphabetical)
      const restA = a.restaurant || '';
      const restB = b.restaurant || '';
      if (restA !== restB) {
        return restA.localeCompare(restB);
      }

      // 2. Sort by hierarchy (GM first, then managers, then staff)
      const hierA = this.getHierarchyOrder(a.job_title || '');
      const hierB = this.getHierarchyOrder(b.job_title || '');
      if (hierA !== hierB) {
        return hierA - hierB;
      }

      // 3. Sort by overtime hours (highest first within same position)
      return (b.overtime_hours || 0) - (a.overtime_hours || 0);
    });
  }

  /**
   * Group employees by restaurant
   *
   * @param {Array} employees - Employee overtime records
   * @returns {Object} Employees grouped by restaurant
   */
  groupByRestaurant(employees) {
    const grouped = {};

    employees.forEach(emp => {
      const restaurant = emp.restaurant || 'Unknown';
      if (!grouped[restaurant]) {
        grouped[restaurant] = [];
      }
      grouped[restaurant].push(emp);
    });

    return grouped;
  }

  /**
   * Build complete modal content HTML
   * Includes summary card and employee table grouped by restaurant
   *
   * @returns {string} Modal content HTML
   */
  buildContentHTML() {
    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();
    const employees = this.currentData || [];

    // Handle empty state
    if (employees.length === 0) {
      return `
        <div style="text-align: center; padding: 3rem; color: ${THEME_COLORS.text.muted};">
          <div style="font-size: 3rem; margin-bottom: 1rem;">✓</div>
          <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
            No Overtime This Week
          </div>
          <div style="font-size: 0.875rem;">
            All employees stayed within their regular 40-hour work week.
          </div>
        </div>
      `;
    }

    // Sort employees by restaurant → hierarchy → OT hours
    const sorted = this.sortEmployees(employees);

    // Group by restaurant
    const groupedByRestaurant = this.groupByRestaurant(sorted);

    // Calculate totals
    const totals = this.calculateOvertimeTotals(sorted);

    // Build summary card
    const summaryHTML = `
      <div class="overtime-summary-card" style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: ${THEME_COLORS.status.normal.bg};
        border: 1px solid ${THEME_COLORS.border};
        border-radius: 0.75rem;
      ">
        <div>
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">
            👥 Employees
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.text.primary};">
            ${totals.totalEmployees}
          </div>
        </div>

        <div>
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">
            ⏰ Total OT Hours
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.text.primary};">
            ${totals.totalOTHours.toFixed(1)}h
          </div>
        </div>

        <div>
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">
            💰 Total OT Cost
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.text.primary};">
            ${businessEngine.formatCurrency(totals.totalOTCost)}
          </div>
        </div>

        <div>
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">
            📊 Avg OT per Employee
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.text.primary};">
            ${totals.avgOTHours.toFixed(1)}h
          </div>
        </div>
      </div>
    `;

    // Build table with restaurant groupings
    const tableHTML = this.buildGroupedTable(groupedByRestaurant, THEME_COLORS);

    return summaryHTML + tableHTML;
  }

  /**
   * Build grouped table with restaurant sections
   *
   * @param {Object} groupedByRestaurant - Employees grouped by restaurant
   * @param {Object} THEME_COLORS - Theme colors
   * @returns {string} Table HTML
   */
  buildGroupedTable(groupedByRestaurant, THEME_COLORS) {
    const restaurants = Object.keys(groupedByRestaurant).sort();

    let tableHTML = '<div style="overflow-x: auto;">';

    restaurants.forEach((restaurant, restaurantIndex) => {
      const employees = groupedByRestaurant[restaurant];
      const restaurantOTHours = employees.reduce((sum, e) => sum + (e.overtime_hours || 0), 0);
      const restaurantOTCost = employees.reduce((sum, e) => sum + (e.overtime_cost || 0), 0);

      // Restaurant header section
      tableHTML += `
        <div style="
          margin-top: ${restaurantIndex > 0 ? '2rem' : '0'};
          margin-bottom: 0.75rem;
          padding: 0.75rem 1rem;
          background: linear-gradient(135deg, ${THEME_COLORS.accent} 0%, ${THEME_COLORS.status.normal.bg} 100%);
          border-left: 4px solid ${THEME_COLORS.accent};
          border-radius: 0.5rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <div>
            <span style="
              font-size: 1.125rem;
              font-weight: 700;
              color: ${THEME_COLORS.text.primary};
            ">
              🏪 ${restaurant}
            </span>
            <span style="
              font-size: 0.875rem;
              color: ${THEME_COLORS.text.muted};
              margin-left: 0.75rem;
            ">
              ${employees.length} employee${employees.length !== 1 ? 's' : ''}
            </span>
          </div>
          <div style="display: flex; gap: 1.5rem;">
            <div style="text-align: right;">
              <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted};">Total OT Hours</div>
              <div style="font-size: 1rem; font-weight: 600; color: ${THEME_COLORS.text.primary};">
                ${restaurantOTHours.toFixed(1)}h
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted};">Total OT Cost</div>
              <div style="font-size: 1rem; font-weight: 600; color: ${THEME_COLORS.status.critical.text};">
                ${this.engines.businessEngine.formatCurrency(restaurantOTCost)}
              </div>
            </div>
          </div>
        </div>
      `;

      // Restaurant table
      tableHTML += `
        <table class="overtime-table" style="
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
          margin-bottom: 0;
        ">
          <thead>
            <tr style="
              background: linear-gradient(to right, var(--color-bronze, #B89968), var(--color-amber, #D4A574));
              color: white;
            ">
              <th style="padding: 0.75rem; text-align: left; font-weight: 600; width: 30%;">Employee</th>
              <th style="padding: 0.75rem; text-align: left; font-weight: 600; width: 20%;">Position</th>
              <th style="padding: 0.75rem; text-align: right; font-weight: 600; width: 12%;">Regular Hrs</th>
              <th style="padding: 0.75rem; text-align: right; font-weight: 600; width: 12%;">OT Hours</th>
              <th style="padding: 0.75rem; text-align: right; font-weight: 600; width: 14%;">OT Cost</th>
              <th style="padding: 0.75rem; text-align: center; font-weight: 600; width: 12%;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${employees.map((emp, index) => this.buildEmployeeRow(emp, THEME_COLORS, index, false)).join('')}
          </tbody>
        </table>
      `;
    });

    tableHTML += '</div>';
    return tableHTML;
  }

  /**
   * Build individual employee table row
   *
   * @param {Object} emp - Employee overtime record
   * @param {Object} THEME_COLORS - Theme color object
   * @param {number} index - Row index for alternating colors
   * @param {boolean} showRestaurant - Whether to show restaurant column (default: false)
   * @returns {string} Table row HTML
   */
  buildEmployeeRow(emp, THEME_COLORS, index, showRestaurant = false) {
    const { businessEngine } = this.engines;

    // Extract fields (support multiple field name formats)
    const restaurant = emp.restaurant || emp.restaurant_code || 'N/A';
    const employeeName = emp.employee_name || emp.name || 'Unknown';
    const position = emp.job_title || emp.role || emp.position || 'N/A';
    const regularHours = emp.regular_hours || 0;
    const overtimeHours = emp.overtime_hours || 0;
    const overtimeCost = emp.overtime_cost || 0;

    // Determine severity and badge
    let badgeHTML = '';
    let badgeStyle = '';

    if (overtimeHours >= 20) {
      // Critical: 20+ hours
      badgeStyle = `
        background: ${THEME_COLORS.status.critical.bg};
        color: ${THEME_COLORS.status.critical.text};
        border: 1px solid ${THEME_COLORS.status.critical.border};
      `;
      badgeHTML = `<span style="${badgeStyle} padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">Critical</span>`;
    } else if (overtimeHours >= 10) {
      // Warning: 10-20 hours
      badgeStyle = `
        background: ${THEME_COLORS.status.warning.bg};
        color: ${THEME_COLORS.status.warning.text};
        border: 1px solid ${THEME_COLORS.status.warning.border};
      `;
      badgeHTML = `<span style="${badgeStyle} padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">Warning</span>`;
    } else {
      // Normal: 1-10 hours
      badgeStyle = `
        background: ${THEME_COLORS.status.normal.bg};
        color: ${THEME_COLORS.status.normal.text};
        border: 1px solid ${THEME_COLORS.status.normal.border};
      `;
      badgeHTML = `<span style="${badgeStyle} padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">Normal</span>`;
    }

    // Alternating row background
    const rowBg = index % 2 === 0 ? 'white' : 'rgba(250, 246, 240, 0.5)';

    // Restaurant column (optional)
    const restaurantColumn = showRestaurant ? `
      <td style="padding: 0.75rem; color: ${THEME_COLORS.text.primary}; font-weight: 600;">
        ${restaurant}
      </td>
    ` : '';

    return `
      <tr style="
        background: ${rowBg};
        transition: background-color 0.2s ease;
      " onmouseover="this.style.backgroundColor='rgba(184, 153, 104, 0.1)'" onmouseout="this.style.backgroundColor='${rowBg}'">
        ${restaurantColumn}
        <td style="padding: 0.75rem; color: ${THEME_COLORS.text.primary};">
          ${employeeName}
        </td>
        <td style="padding: 0.75rem; color: ${THEME_COLORS.text.secondary};">
          ${position}
        </td>
        <td style="padding: 0.75rem; text-align: right; color: ${THEME_COLORS.text.primary};">
          ${regularHours.toFixed(1)}h
        </td>
        <td style="padding: 0.75rem; text-align: right; color: ${THEME_COLORS.text.primary}; font-weight: 600;">
          ${overtimeHours.toFixed(1)}h
        </td>
        <td style="padding: 0.75rem; text-align: right; color: ${THEME_COLORS.status.critical.text}; font-weight: 600;">
          ${businessEngine.formatCurrency(overtimeCost)}
        </td>
        <td style="padding: 0.75rem; text-align: center;">
          ${badgeHTML}
        </td>
      </tr>
    `;
  }
}

// ============================================
// Global Functions (Window Scope)
// ============================================

/**
 * Close overtime modal
 * Called from onclick handlers in HTML
 */
window.closeOvertimeModal = function() {
  const modalContainer = document.getElementById('overtime-modal');
  const modal = modalContainer ? modalContainer.querySelector('.modal-overlay') : null;
  if (modal) {
    // Add hidden to BOTH inner modal and outer container
    modal.classList.add('hidden');
    modalContainer.classList.add('hidden');
  }
};

/**
 * Show overtime details modal
 * Called from OverviewCard onclick
 */
window.showOvertimeDetails = function() {
  const weekData = window.dashboardApp?.getCurrentData();
  const employees = weekData?.autoClockout || [];
  window.overtimeModal?.open(employees);
};

// ============================================
// Initialization
// ============================================

/**
 * Initialize overtime details modal
 *
 * @param {Object} engines - Dashboard engines (businessEngine, themeEngine, layoutEngine)
 */
export function initializeOvertimeDetailsModal(engines) {
  // Create modal instance and attach to window for onclick handlers
  window.overtimeModal = new OvertimeDetailsModal(engines);

  // Find or create modal container
  let modalContainer = document.getElementById('overtime-modal');

  // If the modal container doesn't exist, create it
  if (!modalContainer) {
    modalContainer = document.createElement('div');
    modalContainer.id = 'overtime-modal';
    document.body.appendChild(modalContainer);
  }

  // Render modal HTML into container
  modalContainer.innerHTML = window.overtimeModal.render();

  console.log('[OvertimeDetailsModal] Initialized successfully');
}
