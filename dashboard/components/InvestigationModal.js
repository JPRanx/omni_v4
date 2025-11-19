/**
 * Dashboard V3 - Investigation Modal Component
 * Enhanced version matching V2 development structure with theme engine integration
 *
 * THREE LEVELS:
 * - Level 1: Executive P&L Breakdown (4 quadrants)
 * - Level 2: Daily Performance (7 day cards with manager names, streaks, horizontal scroll)
 * - Level 3: Timeslot Analysis (populated when day card clicked)
 *
 * Progressive disclosure with stacked hierarchy
 */

/**
 * InvestigationModal Class
 */
class InvestigationModal {
  constructor(engines) {
    this.engines = engines;
    this.modal = null;
    this.currentData = null;
  }

  /**
   * Get theme colors from ThemeEngine
   * Replaces the old THEME_COLORS constant
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

  render() {
    return `
      <div class="modal-overlay hidden">
        <div class="modal-container">

          <!-- Modal Header with Gradient -->
          <div class="modal-header">
            <div class="modal-header-content">
              <h2 id="modalTitle" class="modal-title">
                Restaurant Investigation
              </h2>
            </div>
            <button onclick="window.closeInvestigationModal()" class="modal-close-btn">
              ×
            </button>
          </div>

          <!-- Modal Body with 3 Levels -->
          <div id="modalBody" class="modal-body">
            <!-- Level 1: Executive P&L -->
            <div id="level1-container"></div>

            <!-- Visual Separator -->
            <div class="level-separator"></div>

            <!-- Level 2: Daily Performance -->
            <div id="level2-container"></div>

            <!-- Level 3: Timeslot Analysis (populated on day click) -->
            <div id="level3-container"></div>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button onclick="window.closeInvestigationModal()" class="modal-footer-btn">
              Close
            </button>
          </div>
        </div>
      </div>
    `;
  }

  open(restaurantName, restaurantData) {
    console.log('[InvestigationModal] Opening modal for:', restaurantName);
    console.log('[InvestigationModal] Restaurant data:', restaurantData);

    this.currentData = restaurantData;

    const modalContainer = document.getElementById('investigation-modal');
    const modal = modalContainer ? modalContainer.querySelector('.modal-overlay') : null;
    console.log('[InvestigationModal] Modal element:', modal);

    if (modal) {
      // Remove hidden from BOTH outer container and inner modal
      modalContainer.classList.remove('hidden');
      modal.classList.remove('hidden');
      document.getElementById('modalTitle').innerHTML = `${restaurantName} - Investigation`;
      this.loadAllLevels();
      document.getElementById('modalBody').scrollTop = 0;
    } else {
      console.error('[InvestigationModal] Modal element not found!');
    }
  }

  loadAllLevels() {
    const data = this.currentData;

    if (!data) {
      console.error('No data available for restaurant');
      this.showErrorState();
      return;
    }

    // Load Level 1: P&L Breakdown
    const level1Container = document.getElementById('level1-container');
    if (level1Container) {
      level1Container.innerHTML = this.buildLevel1HTML(data);
    }

    // Load Level 2: Daily Performance
    const level2Container = document.getElementById('level2-container');
    if (level2Container) {
      level2Container.innerHTML = this.buildLevel2HTML(data);
    }

    // Level 3 starts empty
    const level3Container = document.getElementById('level3-container');
    if (level3Container) {
      level3Container.innerHTML = '';
    }
  }

  buildLevel1HTML(data) {
    const { businessEngine } = this.engines;

    const sales = data.sales || 0;
    const laborCost = data.laborCost || data.labor_cost || 0;
    const vendorCost = data.cogs || data.vendor_cost || 0;
    const overheadCost = data.overhead_cost || (sales * 0.15);

    // Get actual cash flow data
    const cashFlowData = data.cashFlow || {};

    // The field names are misleading in the backend:
    // - net_cash = GROSS cash collected from customers (before deductions)
    // - total_cash = NET cash remaining (after tips/payouts deducted)
    // - total_tips = negative value (outflow)
    // - total_vendor_payouts = negative value (outflow)

    const grossCashCollected = cashFlowData.net_cash || 0;  // GROSS from customers
    const totalTips = Math.abs(cashFlowData.total_tips || 0);  // Tips distributed (positive for display)
    const totalVendorPayouts = Math.abs(cashFlowData.total_vendor_payouts || 0);  // Payouts (positive for display)
    const netCashAvailable = cashFlowData.total_cash || 0;  // NET remaining in drawer

    // Calculate profit using actual data
    const totalCosts = laborCost + vendorCost + overheadCost;
    const profit = sales - totalCosts;

    // Calculate percentages
    const laborPct = sales > 0 ? (laborCost / sales * 100).toFixed(1) : 0;
    const vendorPct = sales > 0 ? (vendorCost / sales * 100).toFixed(1) : 0;
    const overheadPct = sales > 0 ? (overheadCost / sales * 100).toFixed(1) : 0;
    const profitPct = sales > 0 ? (profit / sales * 100).toFixed(1) : 0;
    const cashPct = sales > 0 ? (grossCashCollected / sales * 100).toFixed(1) : 0;

    // Cash employee calculations
    const cashEmployeesTotal = laborCost * 0.05;
    const cashEmployeesOT = cashEmployeesTotal * 0.2;

    // Get vendor payouts from cash flow data and sort alphabetically by vendor name
    const vendorPayouts = (data.cashFlow?.vendor_payouts || []).sort((a, b) => {
      const nameA = a.vendor_name || a.reason || 'Unknown Vendor';
      const nameB = b.vendor_name || b.reason || 'Unknown Vendor';
      return nameA.localeCompare(nameB);
    });

    return `
      <div class="level-section">
        <h3 class="level-title">
          Level 1: Executive P&L Breakdown
        </h3>

        <!-- Sales Banner -->
        <div class="pnl-banner">
          <div class="pnl-banner-value">${businessEngine.formatCurrency(sales)}</div>
          <div class="pnl-banner-label">Total Sales</div>
        </div>

        <!-- P&L Grid -->
        <div class="pnl-grid">

          <!-- Payroll Quadrant -->
          <div class="pnl-quadrant pnl-quadrant-payroll">
            <h4 class="quadrant-title">
              <span>PAYROLL (${businessEngine.formatCurrency(laborCost)})</span>
              <span class="quadrant-pct">${laborPct}%</span>
            </h4>
            <div class="quadrant-body">
              <div class="pnl-line">
                <span>Check Employees</span>
                <span>${businessEngine.formatCurrency(laborCost * 0.90)}</span>
              </div>
              <div class="pnl-line">
                <span>Check Overtime</span>
                <span>${businessEngine.formatCurrency(laborCost * 0.05)}</span>
              </div>
              <div class="pnl-line">
                <span>Cash Employees</span>
                <span>${businessEngine.formatCurrency(cashEmployeesTotal)}</span>
              </div>
              <div class="pnl-line">
                <span>Cash Overtime</span>
                <span>${businessEngine.formatCurrency(cashEmployeesOT)}</span>
              </div>
              <div class="pnl-total">
                <span>Total Payroll</span>
                <span>${businessEngine.formatCurrency(laborCost)}</span>
              </div>
            </div>
          </div>

          <!-- Vendor Quadrant -->
          <div class="pnl-quadrant pnl-quadrant-vendors">
            <h4 class="quadrant-title">
              <span>VENDORS (${businessEngine.formatCurrency(vendorCost)})</span>
              <span class="quadrant-pct">${vendorPct}%</span>
            </h4>
            <div class="quadrant-body">
              ${vendorPayouts.length > 0 ? `
                <div style="max-height: 180px; overflow-y: auto; margin-bottom: 0.75rem; padding-right: 0.5rem;">
                  ${vendorPayouts.map(payout => {
                    const vendorName = payout.vendor_name || payout.reason || 'Unknown Vendor';
                    const reason = payout.reason || '';
                    const comments = payout.comments || '';
                    const details = [reason, comments].filter(d => d && d.trim()).join(' • ');

                    return `
                      <div style="margin-bottom: 0.5rem;">
                        <div class="pnl-line" style="margin-bottom: 0;">
                          <span>${vendorName}</span>
                          <span>${businessEngine.formatCurrency(Math.abs(payout.amount || 0))}</span>
                        </div>
                        ${details ? `
                          <div style="
                            font-size: 0.75rem;
                            color: #8B7355;
                            padding-left: 1rem;
                            margin-top: 0.25rem;
                            line-height: 1.3;
                          ">
                            ${details}
                          </div>
                        ` : ''}
                      </div>
                    `;
                  }).join('')}
                </div>
              ` : `
                <div class="pnl-line">
                  <span style="color: #8B7355; font-style: italic;">No vendor payouts recorded</span>
                  <span>—</span>
                </div>
              `}
              <div class="pnl-total">
                <span>Total Vendors</span>
                <span>${businessEngine.formatCurrency(vendorCost)}</span>
              </div>
            </div>
          </div>

          <!-- Overhead Quadrant -->
          <div class="pnl-quadrant pnl-quadrant-overhead">
            <h4 class="quadrant-title">
              <span>OVERHEAD (${businessEngine.formatCurrency(overheadCost)})</span>
              <span class="quadrant-pct">${overheadPct}%</span>
            </h4>
            <div class="quadrant-body">
              <div class="pnl-line">
                <span>Rent</span>
                <span>${businessEngine.formatCurrency(overheadCost * 0.50)}</span>
              </div>
              <div class="pnl-line">
                <span>Utilities</span>
                <span>${businessEngine.formatCurrency(overheadCost * 0.20)}</span>
              </div>
              <div class="pnl-line">
                <span>Marketing</span>
                <span>${businessEngine.formatCurrency(overheadCost * 0.15)}</span>
              </div>
              <div class="pnl-line">
                <span>Other</span>
                <span>${businessEngine.formatCurrency(overheadCost * 0.15)}</span>
              </div>
              <div class="pnl-total">
                <span>Total Overhead</span>
                <span>${businessEngine.formatCurrency(overheadCost)}</span>
              </div>
            </div>
          </div>

          <!-- Cash & Profit Quadrant -->
          <div class="pnl-quadrant ${profit >= 0 ? 'pnl-quadrant-profit-positive' : 'pnl-quadrant-profit-negative'}">
            <h4 class="quadrant-title">
              <span>CASH & PROFIT</span>
              ${grossCashCollected > 0 ? `<span class="quadrant-pct">${cashPct}% cash sales</span>` : ''}
            </h4>
            <div class="quadrant-body">
              ${grossCashCollected > 0 ? `
                <!-- Cash Flow Breakdown -->
                <div class="pnl-line" style="font-weight: 600; color: #2D5016;">
                  <span>Total Cash Collected</span>
                  <span>${businessEngine.formatCurrency(grossCashCollected)}</span>
                </div>
                <div class="pnl-line" style="padding-left: 1rem; font-size: 0.9rem; color: #8B7355;">
                  <span>Tips Distributed</span>
                  <span>-${businessEngine.formatCurrency(totalTips)}</span>
                </div>
                <div class="pnl-line" style="padding-left: 1rem; font-size: 0.9rem; color: #8B7355;">
                  <span>Vendor Payouts (Cash)</span>
                  <span>-${businessEngine.formatCurrency(totalVendorPayouts)}</span>
                </div>
                <div class="pnl-line" style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #E5DDD0; font-weight: 600; color: #2D5016;">
                  <span>Net Cash Available</span>
                  <span>${businessEngine.formatCurrency(netCashAvailable)}</span>
                </div>

                <!-- P&L Summary -->
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #E5DDD0;">
                  <div class="pnl-line" style="font-size: 0.875rem; color: #8B7355;">
                    <span>Total Revenue</span>
                    <span>${businessEngine.formatCurrency(sales)}</span>
                  </div>
                  <div class="pnl-line" style="font-size: 0.875rem; color: #8B7355;">
                    <span>Total Expenses</span>
                    <span>${businessEngine.formatCurrency(totalCosts)}</span>
                  </div>
                </div>
              ` : `
                <!-- P&L Only (No Cash Data) -->
                <div class="pnl-line">
                  <span>Total Revenue</span>
                  <span>${businessEngine.formatCurrency(sales)}</span>
                </div>
                <div class="pnl-line">
                  <span>Total Expenses</span>
                  <span>${businessEngine.formatCurrency(totalCosts)}</span>
                </div>
              `}
              <div class="pnl-total ${profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                <span>Net Profit</span>
                <span>${businessEngine.formatCurrency(profit)} (${profitPct}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  buildLevel2HTML(data) {
    // Support both naming conventions: daily_breakdown and dailyBreakdown
    const dailyData = data.daily_breakdown || data.dailyBreakdown || [];

    if (dailyData.length === 0) {
      return `
        <div class="level-section">
          <h3 class="level-title">
            Level 2: Daily Performance Breakdown
          </h3>
          <div class="warning-box">
            <div class="warning-icon">⚠️</div>
            <div>
              <h4 class="warning-title">Daily Data Unavailable</h4>
              <p class="warning-text">Detailed daily breakdown with shift information is not available for this restaurant.</p>
            </div>
          </div>
        </div>
      `;
    }

    // Build enhanced day cards
    const dailyCards = dailyData.map(day => this.buildEnhancedDayCard(day)).join('');

    return `
      <div class="level-section">
        <h3 class="level-title">
          Level 2: Daily Performance Breakdown
        </h3>

        <!-- Horizontal scroll container -->
        <div class="scroll-container-wrapper">
          <!-- Scroll indicators -->
          <div class="scroll-fade-left"></div>
          <div class="scroll-fade-right"></div>

          <!-- Scrollable cards container -->
          <div class="days-scroll-container">
            <div class="days-flex-container">
              ${dailyCards}
            </div>
          </div>

          <!-- Scroll hint -->
          <div class="scroll-hint">
            <span>← Scroll horizontally to see all days →</span>
          </div>
        </div>
      </div>
    `;
  }

  buildEnhancedDayCard(day) {
    const { businessEngine } = this.engines;

    // Calculate metrics
    const morningShift = day.shifts?.morning || day.shifts?.Morning || {};
    const eveningShift = day.shifts?.evening || day.shifts?.Evening || {};

    // Handle case where shifts aren't broken down - use total day sales
    const morningSales = morningShift.sales || (day.sales ? day.sales * 0.45 : 0);
    const eveningSales = eveningShift.sales || (day.sales ? day.sales * 0.55 : 0);
    const totalSales = day.sales || (morningSales + eveningSales);

    // Calculate shift percentages for visual bars
    const morningPct = totalSales > 0 ? (morningSales / totalSales * 100).toFixed(0) : 0;
    const eveningPct = totalSales > 0 ? (eveningSales / totalSales * 100).toFixed(0) : 0;

    // Get manager names
    const morningManager = morningShift.manager || 'Not Assigned';
    const eveningManager = eveningShift.manager || 'Not Assigned';

    // Get void counts
    const morningVoids = morningShift.voids || 0;
    const eveningVoids = eveningShift.voids || 0;

    // CALCULATE STREAK DATA
    const morningSlots = day.efficiency_analysis?.morning_slots || [];
    const eveningSlots = day.efficiency_analysis?.evening_slots || [];

    // Count hot/cold streaks and passes/fails
    let morningHot = 0, morningCold = 0, morningPass = 0, morningFail = 0;
    let eveningHot = 0, eveningCold = 0, eveningPass = 0, eveningFail = 0;

    morningSlots.forEach(slot => {
      if (slot.streak?.hot_streak) morningHot++;
      if (slot.streak?.cold_streak) morningCold++;
      // Check if slot passed based on status or grading
      if (slot.status === 'Normal' || slot.status === 'Good') {
        morningPass++;
      } else {
        morningFail++;
      }
    });

    eveningSlots.forEach(slot => {
      if (slot.streak?.hot_streak) eveningHot++;
      if (slot.streak?.cold_streak) eveningCold++;
      // Check if slot passed based on status
      if (slot.status === 'Normal' || slot.status === 'Good') {
        eveningPass++;
      } else {
        eveningFail++;
      }
    });

    // Calculate totals
    const totalHot = morningHot + eveningHot;
    const totalCold = morningCold + eveningCold;
    const totalPass = morningPass + eveningPass;
    const totalFail = morningFail + eveningFail;
    const totalSlots = morningSlots.length + eveningSlots.length;
    const passRate = totalSlots > 0 ? Math.round((totalPass / totalSlots) * 100) : 0;

    // Format date nicely
    const dayName = day.day_name || day.day || 'Day';
    const dayDate = day.date || '';
    const shortDate = dayDate ? (() => {
      const dateObj = new Date(dayDate);
      return `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
    })() : '';

    return `
      <div class="day-card enhanced-day-card" onclick="window.investigationModal.loadLevel3('${dayName}')">

        <!-- Header gradient bar -->
        <div class="day-card-header-gradient"></div>

        <div class="day-card-content">
          <!-- Header with date -->
          <div class="day-card-header">
            <div>
              <h4 class="day-card-day-name">
                ${dayName}
              </h4>
              <p class="day-card-date">
                ${shortDate}
              </p>
            </div>
          </div>

          <!-- Main sales highlight -->
          <div class="day-card-sales-box">
            <div class="day-card-sales-value">
              $${totalSales.toLocaleString()}
            </div>
            <div class="day-card-sales-label">
              Total Sales
            </div>
          </div>

          <!-- Shift breakdown with manager names -->
          <div class="day-card-shifts">
            <!-- Morning shift -->
            <div class="shift-info">
              <div class="shift-header">
                <span class="shift-label shift-label-morning">Morning</span>
                <span class="shift-manager">${morningManager}</span>
              </div>
              <div class="shift-progress-container">
                <div class="shift-progress-bg">
                  <div class="shift-progress-bar shift-progress-morning" style="width: ${morningPct}%"></div>
                </div>
                <span class="shift-sales-value">
                  $${morningSales.toLocaleString()}
                </span>
              </div>
            </div>

            <!-- Evening shift -->
            <div class="shift-info">
              <div class="shift-header">
                <span class="shift-label shift-label-evening">Evening</span>
                <span class="shift-manager">${eveningManager}</span>
              </div>
              <div class="shift-progress-container">
                <div class="shift-progress-bg">
                  <div class="shift-progress-bar shift-progress-evening" style="width: ${eveningPct}%"></div>
                </div>
                <span class="shift-sales-value">
                  $${eveningSales.toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          <!-- STREAK METRICS (bottom metrics only) -->
          <div class="streak-metrics-grid">
            <!-- Hot Streaks -->
            <div class="streak-metric-card">
              <div class="streak-metric-value streak-hot">
                ${totalHot > 0 ? `🔥${totalHot}` : '—'}
              </div>
              <div class="streak-metric-label">Hot</div>
            </div>

            <!-- Cold Streaks -->
            <div class="streak-metric-card">
              <div class="streak-metric-value streak-cold">
                ${totalCold > 0 ? `🧊${totalCold}` : '—'}
              </div>
              <div class="streak-metric-label">Cold</div>
            </div>

            <!-- Pass Rate -->
            <div class="streak-metric-card">
              <div class="streak-metric-value ${passRate >= 80 ? 'streak-pass-good' : passRate >= 60 ? 'streak-pass-medium' : 'streak-pass-bad'}">
                ${passRate}%
              </div>
              <div class="streak-metric-label">Pass</div>
            </div>
          </div>

          <!-- Hover action hint -->
          <div class="day-card-hint">
            <span>Click for detailed timeslot analysis →</span>
          </div>
        </div>
      </div>
    `;
  }

  loadLevel3(dayName) {
    console.log('[InvestigationModal] loadLevel3 called with dayName:', dayName);

    const data = this.currentData;
    console.log('[InvestigationModal] currentData:', data);

    if (!data) {
      console.error('[InvestigationModal] No current data available');
      return;
    }

    // Support both naming conventions
    const dailyBreakdown = data.daily_breakdown || data.dailyBreakdown || [];
    console.log('[InvestigationModal] Daily breakdown:', dailyBreakdown);

    if (dailyBreakdown.length === 0) {
      console.error('[InvestigationModal] No daily breakdown data');
      return;
    }

    // Match by day name (e.g., "Monday", "Tuesday") instead of date
    const dayData = dailyBreakdown.find(d => {
      const dayNameInData = d.day_name || d.day || '';
      return dayNameInData === dayName;
    });
    console.log('[InvestigationModal] Found day data:', dayData);

    if (!dayData) {
      console.error('[InvestigationModal] Could not find day data for dayName:', dayName);
      return;
    }

    const level3Container = document.getElementById('level3-container');
    console.log('[InvestigationModal] Level 3 container:', level3Container);

    if (!level3Container) {
      console.error('[InvestigationModal] Level 3 container not found in DOM');
      return;
    }

    // Visual separator before Level 3
    const separatorHtml = `<div class="level-separator level-separator-3"></div>`;

    // Build Level 3 content
    const level3Html = this.buildLevel3HTML(dayData);
    console.log('[InvestigationModal] Generated Level 3 HTML length:', level3Html.length);

    // Insert with separator
    level3Container.innerHTML = separatorHtml + level3Html;

    // Scroll to Level 3
    setTimeout(() => {
      level3Container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    console.log('[InvestigationModal] Level 3 loaded successfully');
  }

  buildLevel3HTML(dayData) {
    const dayName = dayData.day_name || dayData.day || 'Day';
    const date = dayData.date || '';

    // Get real 15-minute timeslots from backend data
    const morningSlots = this.getRealTimeslots('morning', dayData);
    const eveningSlots = this.getRealTimeslots('evening', dayData);

    // Calculate capacity analysis
    const capacityAnalysis = this.calculateCapacityAnalysis(morningSlots, eveningSlots, dayData);

    return `
      <div class="level-section">
        <h3 class="level-title">
          Level 3: 15-Minute Timeslot Analysis - ${dayName}${date ? ', ' + date : ''}
        </h3>

        <!-- Capacity Analysis Summary -->
        ${this.renderCapacityAnalysis(capacityAnalysis)}

        <!-- Morning Shift -->
        <div class="shift-timeslots mb-8">
          <h4 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-primary, #3D3128);">
            ☀️ Morning Shift (7:00 AM - 1:00 PM)
          </h4>
          <div class="timeslot-table-container">
            <table class="timeslot-table">
              <thead>
                ${this.renderTimeslotTableHeaders()}
              </thead>
              <tbody>
                ${morningSlots.map(slot => this.renderTimeslotRow(slot)).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Evening Shift -->
        <div class="shift-timeslots">
          <h4 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-primary, #3D3128);">
            🌙 Evening Shift (4:00 PM - 9:00 PM)
          </h4>
          <div class="timeslot-table-container">
            <table class="timeslot-table">
              <thead>
                ${this.renderTimeslotTableHeaders()}
              </thead>
              <tbody>
                ${eveningSlots.map(slot => this.renderTimeslotRow(slot)).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Legend -->
        <div style="margin-top: 1.5rem; padding: 1rem; background: #F9FAFB; border-radius: 0.5rem; border-left: 4px solid var(--color-bronze, #B89968);">
          <div style="font-size: 0.875rem; color: #594A3C; display: flex; gap: 2rem; flex-wrap: wrap;">
            <div><strong>🔥</strong> Hot Streak (Pass Rate ≥ 85%)</div>
            <div><strong>🧊</strong> Cold Streak (Pass Rate < 70%)</div>
            <div><strong>✓</strong> Passing (≥ 85%)</div>
            <div><strong>⚠</strong> Warning (70-84%)</div>
            <div><strong>✗</strong> Failing (< 70%)</div>
          </div>
        </div>
      </div>
    `;
  }

  getRealTimeslots(shift, dayData) {
    // Extract real timeslot data from backend instead of generating fake data
    const timeslots = dayData.timeslots || [];

    // Filter by shift and transform to format expected by renderTimeslotRow
    return timeslots
      .filter(ts => ts.shift === shift)
      .map(ts => {
        // Extract category counts from byCategory object
        const byCategory = ts.byCategory || {};
        const lobbyCount = byCategory.Lobby?.total || 0;
        const driveThruCount = byCategory['Drive-Thru']?.total || 0;
        const toGoCount = byCategory.ToGo?.total || 0;

        // Extract just the start time from timeWindow (e.g., "11:30-11:45" -> "11:30")
        const timeWindow = ts.timeWindow || '';
        const time = timeWindow.split('-')[0] || timeWindow;

        return {
          time: time,
          orders: ts.totalOrders || 0,
          tables: lobbyCount,         // "Tables" = Lobby orders
          driveThru: driveThruCount,  // Drive-Thru orders
          toGo: toGoCount,            // ToGo orders
          streak: ts.streakType || 'none',
          passRate: ts.passRate || 0,
          status: ts.status || 'unknown'
        };
      });
  }

  renderTimeslotTableHeaders() {
    return `
      <tr>
        <th style="padding: 0.75rem 0.5rem; text-align: left; font-weight: 600;">Time</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;">Orders</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;">Tables</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;" class="timeslot-col-drive">Drive</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;" class="timeslot-col-togo">ToGo</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;">Streak</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;">Pass Rate</th>
        <th style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 600;">Status</th>
      </tr>
    `;
  }

  generate15MinuteTimeslots(shift, dayData) {
    const slots = [];
    const startHour = shift === 'morning' ? 7 : 16;
    const endHour = shift === 'morning' ? 13 : 21;

    // Get base sales to calculate proportional orders
    const shiftData = dayData.shifts?.[shift] || dayData.shifts?.[shift.charAt(0).toUpperCase() + shift.slice(1)] || {};
    const baseSales = shiftData.sales || (dayData.sales ? dayData.sales * (shift === 'morning' ? 0.45 : 0.55) : 10000);

    for (let hour = startHour; hour < endHour; hour++) {
      for (let minute = 0; minute < 60; minute += 15) {
        const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;

        // Determine if it's peak time (lunch 11:30-13:00 or dinner 17:30-19:30)
        const isPeak = (shift === 'morning' && hour >= 11 && (hour < 13 || (hour === 11 && minute >= 30))) ||
                       (shift === 'evening' && hour >= 17 && (hour < 20 || (hour === 17 && minute >= 30)));

        // Generate realistic order volumes based on peak times
        const baseOrders = isPeak ? 25 : 12;
        const variance = Math.floor(Math.random() * 8) - 4; // -4 to +4
        const orders = Math.max(5, baseOrders + variance);

        // Distribute orders across channels
        const tables = Math.floor(orders * (0.35 + Math.random() * 0.1)); // 35-45%
        const driveThru = Math.floor(orders * (0.30 + Math.random() * 0.1)); // 30-40%
        const toGo = Math.max(1, orders - tables - driveThru); // Remainder

        // Calculate performance metrics
        // Peak times should have higher pass rates (85-95%)
        // Off-peak can vary more (60-90%)
        const basePassRate = isPeak ? 85 : 70;
        const passRateVariance = Math.floor(Math.random() * 15);
        const passRate = Math.min(100, basePassRate + passRateVariance);

        // Determine status based on pass rate
        const status = passRate >= 85 ? 'pass' :
                       passRate >= 70 ? 'warning' : 'fail';

        // Determine streak
        const streak = passRate >= 85 ? 'hot' :
                       passRate < 70 ? 'cold' : 'none';

        slots.push({
          time: timeStr,
          orders,
          tables,
          driveThru,
          toGo,
          streak,
          passRate,
          status
        });
      }
    }

    return slots;
  }

  renderTimeslotRow(slot) {
    const THEME_COLORS = this.getColors();

    // Determine row background based on status
    let rowBg = 'background: white;';
    if (slot.status === 'pass') {
      rowBg = `background: ${THEME_COLORS.status.success.bg};`;
    } else if (slot.status === 'warning') {
      rowBg = `background: ${THEME_COLORS.status.warning.bg};`;
    } else if (slot.status === 'fail') {
      rowBg = `background: ${THEME_COLORS.status.critical.bg};`;
    }

    // Format streak indicator
    const streakIcon = slot.streak === 'hot' ? '🔥' :
                       slot.streak === 'cold' ? '🧊' : '-';

    // Format status icon and color
    let statusIcon = '';
    let statusColor = '';
    if (slot.status === 'pass') {
      statusIcon = '✓';
      statusColor = `color: ${THEME_COLORS.status.success.text};`;
    } else if (slot.status === 'warning') {
      statusIcon = '⚠';
      statusColor = `color: ${THEME_COLORS.status.warning.text};`;
    } else {
      statusIcon = '✗';
      statusColor = `color: ${THEME_COLORS.status.critical.text};`;
    }

    // Format pass rate color
    let rateColor = '';
    if (slot.passRate >= 85) {
      rateColor = `color: ${THEME_COLORS.status.success.text}; font-weight: 600;`;
    } else if (slot.passRate >= 70) {
      rateColor = `color: ${THEME_COLORS.status.warning.text}; font-weight: 600;`;
    } else {
      rateColor = `color: ${THEME_COLORS.status.critical.text}; font-weight: 600;`;
    }

    return `
      <tr style="${rowBg} transition: background 0.2s ease;" onmouseover="this.style.background='rgba(184, 153, 104, 0.05)'" onmouseout="this.style.background='${rowBg.split(':')[1].trim().slice(0, -1)}'">
        <td style="padding: 0.5rem; font-weight: 500;">${this.formatTime(slot.time)}</td>
        <td style="padding: 0.5rem; text-align: center;">${slot.orders}</td>
        <td style="padding: 0.5rem; text-align: center;">${slot.tables}</td>
        <td style="padding: 0.5rem; text-align: center;" class="timeslot-col-drive">${slot.driveThru}</td>
        <td style="padding: 0.5rem; text-align: center;" class="timeslot-col-togo">${slot.toGo}</td>
        <td style="padding: 0.5rem; text-align: center; font-size: 1.125rem;">${streakIcon}</td>
        <td style="padding: 0.5rem; text-align: center; ${rateColor}">${slot.passRate}%</td>
        <td style="padding: 0.5rem; text-align: center; font-size: 1.125rem; ${statusColor}">${statusIcon}</td>
      </tr>
    `;
  }

  calculateCapacityAnalysis(morningSlots, eveningSlots, dayData) {
    return {
      morningSlots,
      eveningSlots,
      dayData  // Pass dayData for unique order counts
    };
  }

  aggregateCategoryStats(morningSlots, eveningSlots, dayData) {
    // SIMPLIFIED VERSION - JUST USE THE DAMN CATEGORY_STATS DIRECTLY!
    console.log('[SIMPLIFIED] Getting category_stats from dayData:', dayData);

    const shifts = dayData.shifts || dayData.Shifts || {};
    const morningShift = shifts.Morning || shifts.morning || {};
    const eveningShift = shifts.Evening || shifts.evening || {};

    // Get the actual category_stats from the data - NO CALCULATIONS!
    const morningStats = morningShift.category_stats || morningShift.categoryStats || {};
    const eveningStats = eveningShift.category_stats || eveningShift.categoryStats || {};

    console.log('[SIMPLIFIED] Morning category_stats found:', morningStats);
    console.log('[SIMPLIFIED] Evening category_stats found:', eveningStats);

    // Just return the actual data structure as-is
    const result = {
      morning: {
        'Lobby': morningStats.Lobby || morningStats.lobby || { total: 0, passed: 0, failed: 0 },
        'Drive-Thru': morningStats['Drive-Thru'] || morningStats.driveThru || { total: 0, passed: 0, failed: 0 },
        'ToGo': morningStats.ToGo || morningStats.togo || { total: 0, passed: 0, failed: 0 }
      },
      evening: {
        'Lobby': eveningStats.Lobby || eveningStats.lobby || { total: 0, passed: 0, failed: 0 },
        'Drive-Thru': eveningStats['Drive-Thru'] || eveningStats.driveThru || { total: 0, passed: 0, failed: 0 },
        'ToGo': eveningStats.ToGo || eveningStats.togo || { total: 0, passed: 0, failed: 0 }
      }
    };

    console.log('[SIMPLIFIED] Returning stats:', result);
    return result;
  }

  renderCapacityAnalysis(analysis) {
    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();
    const dayData = analysis.dayData || {};

    // Get UNIQUE order counts from shift data
    const shifts = dayData.shifts || dayData.Shifts || {};
    const morningShift = shifts.Morning || shifts.morning || {};
    const eveningShift = shifts.Evening || shifts.evening || {};

    // Get unique order counts from shifts
    const morningOrderCount = morningShift.order_count || morningShift.orderCount || 0;
    const eveningOrderCount = eveningShift.order_count || eveningShift.orderCount || 0;
    const totalOrders = morningOrderCount + eveningOrderCount;

    // Get service mix from parent restaurant data
    // Note: serviceMix is at restaurant level, not day level
    const serviceMix = this.currentData?.service_mix || this.currentData?.serviceMix ||
                       dayData.service_mix || dayData.serviceMix || {};

    // Calculate unique orders by category for the full day
    const totalLobby = Math.round(totalOrders * (serviceMix.Lobby / 100 || 0));
    const totalDrive = Math.round(totalOrders * (serviceMix['Drive-Thru'] / 100 || 0));
    const totalToGo = Math.round(totalOrders * (serviceMix.ToGo / 100 || 0));

    // Split category counts proportionally between shifts
    const morningPct = totalOrders > 0 ? morningOrderCount / totalOrders : 0.6;
    const eveningPct = totalOrders > 0 ? eveningOrderCount / totalOrders : 0.4;

    const morningTables = Math.round(totalLobby * morningPct);
    const eveningTables = Math.round(totalLobby * eveningPct);

    const morningDrive = Math.round(totalDrive * morningPct);
    const eveningDrive = Math.round(totalDrive * eveningPct);

    const morningToGo = Math.round(totalToGo * morningPct);
    const eveningToGo = Math.round(totalToGo * eveningPct);

    // FIX 3: Find peak concurrent load from timeslots
    const morningPeakSlot = analysis.morningSlots.reduce((max, s) => (s.orders || s.totalOrders || 0) > (max.orders || max.totalOrders || 0) ? s : max, analysis.morningSlots[0] || {orders: 0, totalOrders: 0, time: '', timeWindow: ''});
    const eveningPeakSlot = analysis.eveningSlots.reduce((max, s) => (s.orders || s.totalOrders || 0) > (max.orders || max.totalOrders || 0) ? s : max, analysis.eveningSlots[0] || {orders: 0, totalOrders: 0, time: '', timeWindow: ''});

    // Calculate ACTUAL per-category pass rates from timeslot data
    // Each timeslot has by_category field with detailed metrics per category
    const categoryStats = this.aggregateCategoryStats(analysis.morningSlots, analysis.eveningSlots, dayData);

    // Morning category stats
    const morningTablesPassed = categoryStats.morning.Lobby.passed;
    const morningTablesFailed = categoryStats.morning.Lobby.failed;

    const morningDrivePassed = categoryStats.morning['Drive-Thru'].passed;
    const morningDriveFailed = categoryStats.morning['Drive-Thru'].failed;

    const morningToGoPassed = categoryStats.morning.ToGo.passed;
    const morningToGoFailed = categoryStats.morning.ToGo.failed;

    // Evening category stats
    const eveningTablesPassed = categoryStats.evening.Lobby.passed;
    const eveningTablesFailed = categoryStats.evening.Lobby.failed;

    const eveningDrivePassed = categoryStats.evening['Drive-Thru'].passed;
    const eveningDriveFailed = categoryStats.evening['Drive-Thru'].failed;

    const eveningToGoPassed = categoryStats.evening.ToGo.passed;
    const eveningToGoFailed = categoryStats.evening.ToGo.failed;

    return `
      <div style="background: white; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem; border: 2px solid ${THEME_COLORS.border}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid ${THEME_COLORS.border};">
          <span style="font-size: 1.5rem;">⚠️</span>
          <h4 style="font-size: 1.5rem; font-weight: 600; color: ${THEME_COLORS.text.primary}; margin: 0;">Capacity vs Demand Analysis</h4>
        </div>

        <!-- Two-column shift breakdown -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 1.5rem;">

          <!-- Morning Shift -->
          <div>
            <h5 style="font-size: 1rem; font-weight: 600; color: ${THEME_COLORS.text.secondary}; margin: 0 0 1rem 0;">Morning Shift</h5>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">

              <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
                <span style="color: ${THEME_COLORS.text.secondary}; font-size: 0.875rem;">Total Tables</span>
                <span style="font-weight: 600; color: ${THEME_COLORS.text.primary};">${morningTables}</span>
              </div>

              <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
                <span style="color: ${THEME_COLORS.text.secondary}; font-size: 0.875rem;">Kitchen Peak</span>
                <span style="font-weight: 600; color: ${THEME_COLORS.text.primary};">${morningPeakSlot.orders || morningPeakSlot.totalOrders || 0} concurrent at ${this.formatTime(morningPeakSlot.time || morningPeakSlot.timeWindow)}</span>
              </div>

              <!-- Orders Meeting Standard -->
              <div style="margin-top: 1rem; padding: 1rem; background: ${THEME_COLORS.status.normal.bg}; border-radius: 0.5rem;">
                <div style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.secondary}; margin-bottom: 0.75rem;">Orders Meeting Standard</div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">Tables</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${morningTablesPassed}✓ / ${morningTablesFailed}✗ (${morningTablesPassed + morningTablesFailed} total)
                  </span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">Drive-Thru</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${morningDrivePassed}✓ / ${morningDriveFailed}✗ (${morningDrivePassed + morningDriveFailed} total)
                  </span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">ToGo</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${morningToGoPassed}✓ / ${morningToGoFailed}✗ (${morningToGoPassed + morningToGoFailed} total)
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Evening Shift -->
          <div>
            <h5 style="font-size: 1rem; font-weight: 600; color: ${THEME_COLORS.text.secondary}; margin: 0 0 1rem 0;">Evening Shift</h5>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">

              <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
                <span style="color: ${THEME_COLORS.text.secondary}; font-size: 0.875rem;">Total Tables</span>
                <span style="font-weight: 600; color: ${THEME_COLORS.text.primary};">${eveningTables}</span>
              </div>

              <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
                <span style="color: ${THEME_COLORS.text.secondary}; font-size: 0.875rem;">Kitchen Peak</span>
                <span style="font-weight: 600; color: ${THEME_COLORS.text.primary};">${eveningPeakSlot.orders || eveningPeakSlot.totalOrders || 0} concurrent at ${this.formatTime(eveningPeakSlot.time || eveningPeakSlot.timeWindow)}</span>
              </div>

              <!-- Orders Meeting Standard -->
              <div style="margin-top: 1rem; padding: 1rem; background: ${THEME_COLORS.status.normal.bg}; border-radius: 0.5rem;">
                <div style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.secondary}; margin-bottom: 0.75rem;">Orders Meeting Standard</div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">Tables</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${eveningTablesPassed}✓ / ${eveningTablesFailed}✗ (${eveningTablesPassed + eveningTablesFailed} total)
                  </span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">Drive-Thru</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${eveningDrivePassed}✓ / ${eveningDriveFailed}✗ (${eveningDrivePassed + eveningDriveFailed} total)
                  </span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">ToGo</span>
                  <span style="font-size: 0.875rem; font-weight: 600;">
                    ${eveningToGoPassed}✓ / ${eveningToGoFailed}✗ (${eveningToGoPassed + eveningToGoFailed} total)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  formatTime(time24) {
    if (!time24) return 'N/A';

    // Handle time window format like "06:00-06:15" by extracting start time
    if (time24.includes('-')) {
      time24 = time24.split('-')[0];
    }

    const parts = time24.split(':');
    if (parts.length < 2) return 'N/A';

    const [hours, minutes] = parts.map(Number);
    if (isNaN(hours) || isNaN(minutes)) return 'N/A';

    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;
    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
  }

  showErrorState() {
    const level1Container = document.getElementById('level1-container');
    if (level1Container) {
      level1Container.innerHTML = `
        <div class="error-box">
          <div class="error-title">Error Loading Data</div>
          <div>Unable to load restaurant data. Please try again.</div>
        </div>
      `;
    }
  }
}

// ============================================
// Global Functions (Window Scope)
// ============================================

window.closeInvestigationModal = function() {
  const modalContainer = document.getElementById('investigation-modal');
  const modal = modalContainer ? modalContainer.querySelector('.modal-overlay') : null;
  if (modal) {
    // Add hidden to BOTH inner modal and outer container
    modal.classList.add('hidden');
    modalContainer.classList.add('hidden');
  }
};

// ============================================
// Initialization Function (ES6 Export)
// ============================================

/**
 * Initialize the investigation modal
 * Called from app.js with engines
 */
export function initializeInvestigationModal(engines) {
  // Create modal instance and attach to window for onclick handlers
  window.investigationModal = new InvestigationModal(engines);

  // Find or create modal container
  let modalContainer = document.getElementById('investigation-modal');

  // If the modal container doesn't exist, create it
  if (!modalContainer) {
    modalContainer = document.createElement('div');
    modalContainer.id = 'investigation-modal';
    document.body.appendChild(modalContainer);
  }

  // Render modal HTML into container
  modalContainer.innerHTML = window.investigationModal.render();

  // Set up event listener for opening modal
  modalContainer.addEventListener('open-investigation', (e) => {
    const { restaurant } = e.detail;
    window.investigationModal.open(restaurant.name, restaurant);
  });

  console.log('[InvestigationModal] Initialized successfully');
}
