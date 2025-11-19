/**
 * Cash Flow Inspector Component
 *
 * Side panel that displays detailed metrics when hovering over Sankey nodes.
 * Shows hierarchy, metrics, and contextual details for Owner, Restaurant, Shift, and Drawer levels.
 */

class CashFlowInspector {
  /**
   * @param {HTMLElement} container - Container element for the inspector
   * @param {Object} cashFlowData - Full cash flow data structure
   */
  constructor(container, cashFlowData) {
    this.container = container;
    this.cashFlowData = cashFlowData;
    this.currentNode = null;

    console.log('[CashFlowInspector] Constructor - Received cashFlowData:', cashFlowData);
    console.log('[CashFlowInspector] Constructor - Data structure:', {
      hasRestaurants: !!cashFlowData.restaurants,
      restaurantKeys: Object.keys(cashFlowData.restaurants || {}),
      totalCash: cashFlowData.total_cash,
      totalTips: cashFlowData.total_tips
    });

    this.render();
  }

  /**
   * Initial render of inspector panel
   */
  render() {
    this.container.innerHTML = `
      <div class="inspector-panel">
        <!-- Breadcrumb Trail -->
        <div class="inspector-breadcrumb" id="inspectorBreadcrumb">
          <span class="breadcrumb-home">Cash Flow</span>
        </div>

        <!-- Metrics Grid -->
        <div class="inspector-metrics" id="inspectorMetrics">
          <div class="metric-card metric-cash">
            <div class="metric-label">Total Cash</div>
            <div class="metric-value" id="metricCash">$0.00</div>
          </div>
          <div class="metric-card metric-tips">
            <div class="metric-label">Tips</div>
            <div class="metric-value" id="metricTips">$0.00</div>
          </div>
          <div class="metric-card metric-payouts">
            <div class="metric-label">Payouts</div>
            <div class="metric-value" id="metricPayouts">$0.00</div>
          </div>
          <div class="metric-card metric-net">
            <div class="metric-label">Net Cash</div>
            <div class="metric-value" id="metricNet">$0.00</div>
          </div>
        </div>

        <!-- Details Section -->
        <div class="inspector-details" id="inspectorDetails">
          <h3 class="details-title">Details</h3>
          <div class="details-content" id="detailsContent">
            <p class="details-placeholder">Hover over a node to see details</p>
          </div>
        </div>

        <!-- Mini Visualizations Placeholder -->
        <div class="inspector-viz" id="inspectorViz" style="display: none;">
          <h4>Breakdown</h4>
          <div id="miniVizContainer"></div>
        </div>

        <!-- Actions -->
        <div class="inspector-actions" id="inspectorActions" style="display: none;">
          <button class="btn-action" id="btnDrillDown">
            <span>Drill Down</span>
          </button>
          <button class="btn-action" id="btnExport">
            <span>Export</span>
          </button>
        </div>
      </div>
    `;

    // Show default state
    this.showDefault();
  }

  /**
   * Show default state (no node selected)
   */
  showDefault() {
    this.currentNode = null;

    // Reset breadcrumb
    const breadcrumb = this.container.querySelector('#inspectorBreadcrumb');
    breadcrumb.innerHTML = '<span class="breadcrumb-home">Cash Flow</span>';

    // Show overview metrics
    this.updateMetrics(
      this.cashFlowData.total_cash || 0,
      this.cashFlowData.total_tips || 0,
      this.cashFlowData.total_vendor_payouts || 0,
      this.cashFlowData.net_cash || 0
    );

    // Show default details
    const detailsContent = this.container.querySelector('#detailsContent');
    detailsContent.innerHTML = `
      <p class="details-placeholder">Hover over a node to see detailed metrics</p>
      <div class="overview-stats">
        <div class="stat-row">
          <span class="stat-label">Period:</span>
          <span class="stat-value">Weekly Summary</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Restaurants:</span>
          <span class="stat-value">${Object.keys(this.cashFlowData.restaurants || {}).length}</span>
        </div>
      </div>
    `;

    // Hide actions
    this.container.querySelector('#inspectorActions').style.display = 'none';
    this.container.querySelector('#inspectorViz').style.display = 'none';
  }

  /**
   * Update inspector with node data
   * @param {Object} nodeData - Node information
   */
  updateNode(nodeData) {
    console.log('[CashFlowInspector] updateNode called with:', nodeData);

    if (!nodeData) {
      console.log('[CashFlowInspector] No nodeData, showing default');
      this.showDefault();
      return;
    }

    this.currentNode = nodeData;
    console.log('[CashFlowInspector] Node type:', nodeData.type);

    // Update breadcrumb
    this.updateBreadcrumb(nodeData);

    // Update metrics based on node type
    switch (nodeData.type) {
      case 'total':
        console.log('[CashFlowInspector] Showing total node');
        this.showTotalNode(nodeData);
        break;
      case 'restaurant':
        console.log('[CashFlowInspector] Showing restaurant node:', nodeData.code);
        this.showRestaurantNode(nodeData);
        break;
      case 'shift':
        console.log('[CashFlowInspector] Showing shift node:', nodeData.code, nodeData.shift);
        this.showShiftNode(nodeData);
        break;
      case 'drawer':
        console.log('[CashFlowInspector] Showing drawer node:', nodeData.drawer);
        this.showDrawerNode(nodeData);
        break;
      default:
        console.warn('[CashFlowInspector] Unknown node type, showing default');
        this.showDefault();
    }
  }

  /**
   * Update breadcrumb trail
   */
  updateBreadcrumb(nodeData) {
    const breadcrumb = this.container.querySelector('#inspectorBreadcrumb');
    let trail = '<span class="breadcrumb-home">Cash Flow</span>';

    if (nodeData.type === 'restaurant' || nodeData.type === 'shift' || nodeData.type === 'drawer') {
      trail += ` <span class="breadcrumb-sep">›</span> <span class="breadcrumb-item">${nodeData.code}</span>`;
    }

    if (nodeData.type === 'shift' || nodeData.type === 'drawer') {
      trail += ` <span class="breadcrumb-sep">›</span> <span class="breadcrumb-item">${nodeData.shift}</span>`;
    }

    if (nodeData.type === 'drawer') {
      trail += ` <span class="breadcrumb-sep">›</span> <span class="breadcrumb-item">${nodeData.drawer}</span>`;
    }

    breadcrumb.innerHTML = trail;
  }

  /**
   * Update metrics cards
   */
  updateMetrics(cash, tips, payouts, net) {
    this.container.querySelector('#metricCash').textContent = this.formatCurrency(cash);
    this.container.querySelector('#metricTips').textContent = this.formatCurrency(tips);
    this.container.querySelector('#metricPayouts').textContent = this.formatCurrency(payouts);
    this.container.querySelector('#metricNet').textContent = this.formatCurrency(net);
  }

  /**
   * Show total/owner level node
   */
  showTotalNode(nodeData) {
    this.updateMetrics(
      this.cashFlowData.total_cash,
      this.cashFlowData.total_tips,
      this.cashFlowData.total_vendor_payouts,
      this.cashFlowData.net_cash
    );

    const detailsContent = this.container.querySelector('#detailsContent');
    detailsContent.innerHTML = `
      <div class="details-section">
        <h4>Owner Total</h4>
        <div class="stat-row">
          <span class="stat-label">Restaurants:</span>
          <span class="stat-value">${Object.keys(this.cashFlowData.restaurants || {}).length}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Period:</span>
          <span class="stat-value">Weekly Summary</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Vendor Payouts:</span>
          <span class="stat-value">${(this.cashFlowData.vendor_payouts || []).length} transactions</span>
        </div>
      </div>
    `;

    this.container.querySelector('#inspectorActions').style.display = 'none';
  }

  /**
   * Show restaurant level node
   */
  showRestaurantNode(nodeData) {
    console.log('[CashFlowInspector] showRestaurantNode - nodeData:', nodeData);
    console.log('[CashFlowInspector] showRestaurantNode - cashFlowData structure:', {
      hasRestaurants: !!this.cashFlowData.restaurants,
      restaurantKeys: Object.keys(this.cashFlowData.restaurants || {})
    });

    const restaurantData = this.cashFlowData.restaurants[nodeData.code];
    if (!restaurantData) {
      console.error('[CashFlowInspector] showRestaurantNode - Restaurant not found:', nodeData.code);
      this.showDefault();
      return;
    }

    console.log('[CashFlowInspector] showRestaurantNode - Restaurant data:', restaurantData);

    this.updateMetrics(
      restaurantData.total_cash,
      restaurantData.total_tips,
      restaurantData.total_vendor_payouts,
      restaurantData.net_cash
    );

    const shifts = restaurantData.shifts || {};
    const vendorPayouts = restaurantData.vendor_payouts || [];

    // Sort vendor payouts
    const sortedPayouts = this.sortVendorPayouts(vendorPayouts);

    const detailsContent = this.container.querySelector('#detailsContent');
    detailsContent.innerHTML = `
      <div class="details-section">
        <h4>${nodeData.code} Restaurant</h4>
        <div class="stat-row">
          <span class="stat-label">Shifts:</span>
          <span class="stat-value">${Object.keys(shifts).length}</span>
        </div>
        <div class="shift-breakdown">
          ${Object.entries(shifts).map(([shiftName, shiftData]) => `
            <div class="shift-row">
              <span class="shift-name">${shiftName}:</span>
              <span class="shift-value">${this.formatCurrency(shiftData.cash)}</span>
            </div>
          `).join('')}
        </div>

        ${sortedPayouts.length > 0 ? `
          <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E5DDD0;">
            <h4 style="font-size: 0.875rem; font-weight: 600; color: #8B7355; margin-bottom: 0.75rem;">
              🏪 Vendor Payouts (${sortedPayouts.length})
            </h4>
            <div style="max-height: 250px; overflow-y: auto;">
              ${sortedPayouts.map(payout => `
                <div style="
                  padding: 0.625rem;
                  margin-bottom: 0.5rem;
                  background: #FFF9F0;
                  border-left: 3px solid #C44536;
                  border-radius: 0.25rem;
                  font-size: 0.8125rem;
                ">
                  <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; color: #C44536;">${this.formatCurrency(Math.abs(payout.amount))}</span>
                    <span style="color: #8B7355; font-size: 0.75rem;">${payout.date || ''}</span>
                  </div>
                  <div style="color: #5D4E37; font-weight: 500; margin-bottom: 0.125rem;">
                    ${payout.vendor_name || payout.reason}
                  </div>
                  <div style="color: #8B7355; font-size: 0.75rem;">
                    ${payout.shift} • ${payout.manager} • ${payout.drawer}
                  </div>
                  ${payout.comments ? `
                    <div style="color: #8B7355; font-size: 0.75rem; font-style: italic; margin-top: 0.25rem;">
                      "${payout.comments}"
                    </div>
                  ` : ''}
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    // Hide action buttons for restaurant level
    this.container.querySelector('#inspectorActions').style.display = 'none';
  }

  /**
   * Show shift level node
   */
  showShiftNode(nodeData) {
    console.log('[CashFlowInspector] showShiftNode - Looking for restaurant:', nodeData.code);
    console.log('[CashFlowInspector] showShiftNode - Available restaurants:', Object.keys(this.cashFlowData.restaurants || {}));

    const restaurantData = this.cashFlowData.restaurants[nodeData.code];
    if (!restaurantData) {
      console.error('[CashFlowInspector] showShiftNode - Restaurant not found:', nodeData.code);
      this.showDefault();
      return;
    }

    console.log('[CashFlowInspector] showShiftNode - Restaurant found, shifts:', Object.keys(restaurantData.shifts || {}));
    console.log('[CashFlowInspector] showShiftNode - Looking for shift:', nodeData.shift);

    const shiftData = restaurantData.shifts[nodeData.shift];
    if (!shiftData) {
      console.error('[CashFlowInspector] showShiftNode - Shift not found:', nodeData.shift);
      console.log('[CashFlowInspector] showShiftNode - Shift data structure:', restaurantData.shifts);
      this.showDefault();
      return;
    }

    console.log('[CashFlowInspector] showShiftNode - Shift data:', shiftData);
    console.log('[CashFlowInspector] showShiftNode - Shift data keys:', Object.keys(shiftData));
    console.log('[CashFlowInspector] showShiftNode - Drawers array:', shiftData.drawers);

    this.updateMetrics(
      shiftData.cash,
      shiftData.tips,
      shiftData.payouts,
      shiftData.net
    );

    const drawers = shiftData.drawers || [];
    console.log('[CashFlowInspector] showShiftNode - Drawers count:', drawers.length);

    // Get vendor payouts for this specific shift
    const allPayouts = restaurantData.vendor_payouts || [];
    const shiftPayouts = allPayouts.filter(p => p.shift === nodeData.shift);
    const sortedPayouts = this.sortVendorPayouts(shiftPayouts);

    const detailsContent = this.container.querySelector('#detailsContent');
    detailsContent.innerHTML = `
      <div class="details-section">
        <h4>${nodeData.code} - ${nodeData.shift} Shift</h4>
        <div class="stat-row">
          <span class="stat-label">Drawers:</span>
          <span class="stat-value">${drawers.length}</span>
        </div>
        ${drawers.length > 0 ? `
          <div class="drawer-breakdown">
            ${drawers.map(drawer => `
              <div class="drawer-row">
                <span class="drawer-name">${drawer.name}:</span>
                <span class="drawer-value">${this.formatCurrency(drawer.cash)}</span>
              </div>
            `).join('')}
          </div>
        ` : '<p class="details-note">No drawer detail available</p>'}

        ${sortedPayouts.length > 0 ? `
          <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E5DDD0;">
            <h4 style="font-size: 0.875rem; font-weight: 600; color: #8B7355; margin-bottom: 0.75rem;">
              🏪 Vendor Payouts (${sortedPayouts.length})
            </h4>
            <div style="max-height: 200px; overflow-y: auto;">
              ${sortedPayouts.map(payout => `
                <div style="
                  padding: 0.625rem;
                  margin-bottom: 0.5rem;
                  background: #FFF9F0;
                  border-left: 3px solid #C44536;
                  border-radius: 0.25rem;
                  font-size: 0.8125rem;
                ">
                  <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; color: #C44536;">${this.formatCurrency(Math.abs(payout.amount))}</span>
                    <span style="color: #8B7355; font-size: 0.75rem;">${payout.time || ''}</span>
                  </div>
                  <div style="color: #5D4E37; font-weight: 500; margin-bottom: 0.125rem;">
                    ${payout.vendor_name || payout.reason}
                  </div>
                  <div style="color: #8B7355; font-size: 0.75rem;">
                    ${payout.manager} • ${payout.drawer}
                  </div>
                  ${payout.comments ? `
                    <div style="color: #8B7355; font-size: 0.75rem; font-style: italic; margin-top: 0.25rem;">
                      "${payout.comments}"
                    </div>
                  ` : ''}
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    // Hide action buttons for shift level
    this.container.querySelector('#inspectorActions').style.display = 'none';
  }

  /**
   * Show drawer level node
   */
  showDrawerNode(nodeData) {
    const restaurantData = this.cashFlowData.restaurants[nodeData.code];
    if (!restaurantData) {
      this.showDefault();
      return;
    }

    const shiftData = restaurantData.shifts[nodeData.shift];
    if (!shiftData) {
      this.showDefault();
      return;
    }

    const drawer = (shiftData.drawers || []).find(d => d.name === nodeData.drawer);
    if (!drawer) {
      this.showDefault();
      return;
    }

    this.updateMetrics(drawer.cash, 0, 0, drawer.cash);

    const detailsContent = this.container.querySelector('#detailsContent');
    detailsContent.innerHTML = `
      <div class="details-section">
        <h4>${drawer.name}</h4>
        <div class="stat-row">
          <span class="stat-label">Restaurant:</span>
          <span class="stat-value">${nodeData.code}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Shift:</span>
          <span class="stat-value">${nodeData.shift}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Transactions:</span>
          <span class="stat-value">${drawer.transactions || 0}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Cash Collected:</span>
          <span class="stat-value">${this.formatCurrency(drawer.cash)}</span>
        </div>
      </div>
    `;

    this.container.querySelector('#inspectorActions').style.display = 'none';
  }

  /**
   * Sort vendor payouts for organized display
   * @param {Array} payouts - Array of vendor payout objects
   * @returns {Array} Sorted payouts
   */
  sortVendorPayouts(payouts) {
    if (!payouts || payouts.length === 0) {
      return [];
    }

    // Create a copy to avoid mutating original
    const sorted = [...payouts];

    // Sort by: 1) Date (chronological), 2) Shift (Morning before Evening), 3) Amount (largest first)
    sorted.sort((a, b) => {
      // Primary: Sort by date
      const dateA = a.date || '';
      const dateB = b.date || '';
      if (dateA !== dateB) {
        return dateA.localeCompare(dateB);
      }

      // Secondary: Sort by shift (Morning before Evening)
      const shiftOrder = { 'Morning': 0, 'Evening': 1 };
      const shiftA = shiftOrder[a.shift] ?? 2;
      const shiftB = shiftOrder[b.shift] ?? 2;
      if (shiftA !== shiftB) {
        return shiftA - shiftB;
      }

      // Tertiary: Sort by amount (largest first)
      const amountA = Math.abs(a.amount || 0);
      const amountB = Math.abs(b.amount || 0);
      return amountB - amountA;
    });

    return sorted;
  }

  /**
   * Format currency values
   */
  formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) {
      return '$0.00';
    }
    return '$' + parseFloat(value).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
}

// Export for use in CashFlowModal
window.CashFlowInspector = CashFlowInspector;
