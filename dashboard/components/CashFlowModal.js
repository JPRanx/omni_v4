/**
 * CashFlowModal.js
 *
 * Interactive Sankey diagram modal for cash flow visualization.
 * Opens when user clicks "Total Cash" metric in Overview Card.
 *
 * Features:
 * - Hierarchical Plotly.js Sankey: Total → Restaurants → Shifts → Drawers
 * - iPad-optimized: No hover tooltips, tap/click to explore
 * - Click-to-drill-down: Tap any node to see detailed breakdown
 * - Restaurant view: Shift comparisons, drawer details, tips & payouts
 * - Shift view: Individual drawer breakdowns with percentages
 * - Drawer view: Simple summary with week total
 * - Aesthetic V3 Desert theme styling with smooth animations
 *
 * @version 3.1
 * @follows InvestigationModal patterns
 */

class CashFlowModal {
  constructor(engines) {
    this.engines = engines;
    this.modal = null;
    this.currentData = null;
    this.inspector = null; // Inspector panel component
    this.plotlyDiv = null; // Reference to Plotly element
    this.unhoverTimeout = null; // Timeout reference for debouncing unhover
  }

  /**
   * Get theme colors from ThemeEngine
   *
   * @returns {Object} Theme color object
   */
  getColors() {
    const { themeEngine } = this.engines;

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
   *
   * @returns {string} Modal HTML
   */
  render() {
    return `
      <div class="modal-overlay hidden">
        <div class="modal-container" style="max-width: 1400px;">

          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-header-content">
              <h2 id="cashFlowModalTitle" class="modal-title">
                💵 Cash Flow Analysis - Week Overview
              </h2>
              <div style="margin-top: 0.25rem; font-size: 0.875rem; opacity: 0.9;">
                Owner View - All Restaurants
              </div>
            </div>
            <button onclick="window.closeCashFlowModal()" class="modal-close-btn">
              ×
            </button>
          </div>

          <!-- Modal Body -->
          <div id="cashFlowModalBody" class="modal-body" style="padding: 2rem; max-height: 75vh; overflow-y: auto;">
            <!-- Content populated by loadContent() -->
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button onclick="window.closeCashFlowModal()" class="modal-footer-btn">
              Close
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Open modal with cash flow data
   *
   * @param {Object} cashFlowData - Cash flow data from dashboard
   */
  open(cashFlowData) {
    this.currentData = cashFlowData || {};

    // Validate data structure
    if (!cashFlowData || typeof cashFlowData !== 'object' || !cashFlowData.total_cash) {
      console.log('[CashFlowModal] No cash flow data, showing empty state');
      this.currentData = { total_cash: 0, total_tips: 0, total_vendor_payouts: 0, net_cash: 0 };
    }

    const modalContainer = document.getElementById('cash-flow-modal');
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
    const container = document.getElementById('cashFlowModalBody');
    if (container) {
      container.innerHTML = this.buildContentHTML();
      // Render Plotly Sankey after DOM is ready
      setTimeout(() => this.renderSankeyDiagram(), 100);
    }
  }

  /**
   * Build modal content HTML
   *
   * @returns {string} Content HTML
   */
  buildContentHTML() {
    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();
    const data = this.currentData;

    // Handle empty state
    if (!data.total_cash || data.total_cash === 0) {
      return `
        <div style="text-align: center; padding: 3rem; color: ${THEME_COLORS.text.muted};">
          <div style="font-size: 3rem; margin-bottom: 1rem;">💵</div>
          <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
            No Cash Flow Data Available
          </div>
          <div style="font-size: 0.875rem;">
            Cash flow data has not been extracted yet for this time period.
          </div>
        </div>
      `;
    }

    // Build summary bar
    const summaryHTML = `
      <div style="
        display: flex;
        justify-content: space-around;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(144, 238, 144, 0.08) 0%, rgba(250, 246, 240, 0.5) 100%);
        border: 1px solid ${THEME_COLORS.border};
        border-radius: 0.75rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      ">
        <div style="text-align: center;">
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
            💰 Cash In
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.status.success.text};">
            ${businessEngine.formatCurrency(data.total_cash || 0)}
          </div>
        </div>

        <div style="text-align: center;">
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
            🎯 Tips Out
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: #1976D2;">
            ${businessEngine.formatCurrency(data.total_tips || 0)}
          </div>
        </div>

        <div style="text-align: center;">
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
            🏪 Payouts
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.status.critical.text};">
            ${businessEngine.formatCurrency(data.total_vendor_payouts || 0)}
          </div>
        </div>

        <div style="text-align: center;">
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
            💵 Net Cash
          </div>
          <div style="font-size: 1.875rem; font-weight: 300; color: ${THEME_COLORS.status.success.text};">
            ${businessEngine.formatCurrency(data.net_cash || 0)}
          </div>
        </div>
      </div>
    `;

    // Grid layout with Sankey + Inspector
    const gridHTML = `
      <div style="
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 1.5rem;
        height: 600px;
      ">
        <!-- Sankey Container -->
        <div id="cashFlowSankey" style="
          background: white;
          border: 1px solid ${THEME_COLORS.border};
          border-radius: 0.75rem;
          padding: 1rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          overflow: hidden;
        "></div>

        <!-- Inspector Container -->
        <div id="cashFlowInspector" style="
          background: white;
          border: 1px solid ${THEME_COLORS.border};
          border-radius: 0.75rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          overflow-y: auto;
        "></div>
      </div>
    `;

    return summaryHTML + gridHTML;
  }

  /**
   * Render Plotly.js Sankey diagram with full hierarchy
   * Total Cash → Restaurants → Shifts → Drawers
   */
  renderSankeyDiagram() {
    const data = this.currentData;
    const { businessEngine } = this.engines;

    // Check if Plotly is loaded
    if (typeof Plotly === 'undefined') {
      console.error('[CashFlowModal] Plotly.js is not loaded');
      document.getElementById('cashFlowSankey').innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #8B7355; flex-direction: column;">
          <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
          <div style="font-size: 1rem;">Loading visualization library...</div>
          <div style="font-size: 0.875rem; margin-top: 0.5rem;">Please ensure Plotly.js is loaded</div>
        </div>
      `;
      return;
    }

    // Build hierarchical Sankey data
    const nodes = [];
    const links = [];
    const nodeColors = [];
    const nodeMetadata = {}; // NEW: Store metadata for each node
    let nodeIndex = 0;

    // Node 0: Total Cash (root)
    nodes.push(`Total Cash<br>${businessEngine.formatCurrency(data.total_cash || 0)}`);
    nodeColors.push('#2E7D32'); // Green
    nodeMetadata[nodeIndex] = { type: 'total' };
    const totalCashIndex = nodeIndex++;

    // Get restaurants data
    const restaurants = data.restaurants || {};
    const restaurantNames = Object.keys(restaurants).sort();

    console.log('[CashFlowModal] Building Sankey with restaurants:', restaurantNames);
    console.log('[CashFlowModal] Restaurant data keys:', Object.keys(restaurants));

    // Level 1: Restaurants
    const restaurantIndices = {};
    restaurantNames.forEach(restCode => {
      const restData = restaurants[restCode];
      nodes.push(`${restCode}<br>${businessEngine.formatCurrency(restData.total_cash || 0)}`);
      nodeColors.push('#1976D2'); // Blue for restaurants
      restaurantIndices[restCode] = nodeIndex;
      nodeMetadata[nodeIndex] = { type: 'restaurant', code: restCode }; // NEW: Store metadata

      console.log(`[CashFlowModal] Created restaurant node ${nodeIndex}: ${restCode}`);

      // Link: Total Cash → Restaurant
      links.push({
        source: totalCashIndex,
        target: nodeIndex,
        value: restData.total_cash || 0,
        color: 'rgba(25, 118, 210, 0.3)'
      });

      nodeIndex++;
    });

    // Level 2 & 3: Shifts and Drawers per Restaurant
    console.log('[CashFlowModal] Starting shift node creation...');
    restaurantNames.forEach(restCode => {
      const restData = restaurants[restCode];
      const restIndex = restaurantIndices[restCode];
      const shifts = restData.shifts || {};

      console.log(`[CashFlowModal] Processing shifts for ${restCode}, restIndex=${restIndex}, shifts:`, Object.keys(shifts));

      Object.keys(shifts).sort().forEach(shiftName => {
        const shiftData = shifts[shiftName];

        // Add shift node
        const shiftLabel = `${restCode} ${shiftName}`;
        nodes.push(`${shiftLabel}<br>${businessEngine.formatCurrency(shiftData.cash || 0)}`);
        nodeColors.push('#FFA726'); // Orange for shifts
        const shiftIndex = nodeIndex;
        nodeMetadata[shiftIndex] = { type: 'shift', code: restCode, shift: shiftName }; // NEW: Store metadata
        nodeIndex++;

        // Debug log
        console.log(`[CashFlowModal] Created shift node ${shiftIndex}: "${shiftLabel}" with metadata:`, nodeMetadata[shiftIndex]);

        // Link: Restaurant → Shift
        links.push({
          source: restIndex,
          target: shiftIndex,
          value: shiftData.cash || 0,
          color: 'rgba(255, 167, 38, 0.3)'
        });

        // Level 3: Drawers
        const drawers = shiftData.drawers || [];
        drawers.forEach(drawer => {
          nodes.push(`${drawer.name}<br>${businessEngine.formatCurrency(drawer.cash || 0)}`);
          nodeColors.push('#66BB6A'); // Light green for drawers
          const drawerIndex = nodeIndex;
          nodeMetadata[drawerIndex] = { type: 'drawer', code: restCode, shift: shiftName, drawer: drawer.name }; // NEW
          nodeIndex++;

          // Link: Shift → Drawer
          links.push({
            source: shiftIndex,
            target: drawerIndex,
            value: drawer.cash || 0,
            color: 'rgba(102, 187, 106, 0.3)'
          });
        });
      });
    });

    // DEBUG: Log all nodes with their indices
    console.log('[CashFlowModal] === NODE MAPPING ===');
    nodes.forEach((label, idx) => {
      console.log(`  Node ${idx}: "${label}" | metadata:`, nodeMetadata[idx]);
    });
    console.log('[CashFlowModal] Total nodes created:', nodes.length);

    // Build Plotly Sankey data with fixed positioning to prevent scrambling
    const sankeyData = [{
      type: "sankey",
      orientation: "h",
      arrangement: "fixed", // Use fixed arrangement to control node positioning
      node: {
        pad: 25, // Increased padding for better spacing
        thickness: 20,
        line: {
          color: "#3D3128",
          width: 1
        },
        label: nodes,
        color: nodeColors,
        hoverinfo: 'all',  // Enable hover events for inspector panel
        font: {
          family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          size: 12,
          color: '#3D3128'
        },
        // Specify X positions to keep hierarchy organized
        x: nodes.map((_, idx) => {
          const meta = nodeMetadata[idx];
          if (meta.type === 'total') return 0.05;
          if (meta.type === 'restaurant') return 0.25;
          if (meta.type === 'shift') return 0.55;
          if (meta.type === 'drawer') return 0.85;
          return 0.5;
        }),
        // Specify Y positions to keep restaurants grouped with their children
        y: nodes.map((_, idx) => {
          const meta = nodeMetadata[idx];
          if (meta.type === 'total') return 0.5;

          // Count nodes per restaurant to distribute evenly
          const restaurantOrder = { 'SDR': 0, 'T12': 1, 'TK9': 2 };
          const restaurantIndex = restaurantOrder[meta.code] ?? 0;

          // Each restaurant gets a section of the canvas
          const numRestaurants = Object.keys(restaurantOrder).length;
          const sectionHeight = 1.0 / numRestaurants;
          const sectionStart = restaurantIndex * sectionHeight;

          if (meta.type === 'restaurant') {
            // Restaurant node at center of its section
            return sectionStart + (sectionHeight / 2);
          }

          if (meta.type === 'shift') {
            // Each restaurant has 2 shifts - distribute them evenly in section
            // Morning at 33% of section, Evening at 67% of section
            const shiftPosition = meta.shift === 'Morning' ? 0.33 : 0.67;
            return sectionStart + (sectionHeight * shiftPosition);
          }

          if (meta.type === 'drawer') {
            // Drawers distributed within their shift's sub-section
            // Get all drawers for this restaurant and shift to calculate position
            const shiftSubSection = meta.shift === 'Morning' ? 0.25 : 0.75;
            const drawerOffset = 0.05; // Small offset for visual separation
            return sectionStart + (sectionHeight * shiftSubSection) + (Math.random() * 0.1 - 0.05);
          }

          return sectionStart + (sectionHeight / 2);
        })
      },
      link: {
        source: links.map(l => l.source),
        target: links.map(l => l.target),
        value: links.map(l => l.value),
        color: links.map(l => l.color),
        hoverinfo: 'skip'  // Disable hover tooltips for iPad usability
      }
    }];

    // Layout configuration
    const layout = {
      font: {
        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        size: 13,
        color: '#3D3128'
      },
      paper_bgcolor: 'white',
      plot_bgcolor: 'white',
      margin: { t: 20, r: 20, b: 20, l: 20 },
      hovermode: 'closest',  // Enable hover detection for inspector panel
      hoverlabel: {
        bgcolor: 'white',
        bordercolor: '#E5DDD0',
        font: {
          size: 12,
          family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
      }
    };

    // Config options
    const config = {
      responsive: true,
      displayModeBar: false,  // Hide Plotly toolbar for cleaner look
      scrollZoom: false
    };

    // Store node labels and metadata for click handling
    this.nodeLabels = nodes;
    this.nodeMetadata = nodeMetadata; // NEW: Store metadata mapping

    // Render the Sankey diagram
    try {
      const sankeyElement = document.getElementById('cashFlowSankey');

      Plotly.newPlot(sankeyElement, sankeyData, layout, config).then(() => {
        console.log('[CashFlowModal] Sankey diagram rendered successfully');
        console.log('[CashFlowModal] Node metadata:', nodeMetadata);

        // Initialize inspector panel
        this.initializeInspector();

        // Attach hover event handlers
        this.attachHoverHandlers();
      });

    } catch (error) {
      console.error('[CashFlowModal] Error rendering Sankey:', error);
      document.getElementById('cashFlowSankey').innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #C44536; flex-direction: column;">
          <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
          <div style="font-size: 1rem;">Error rendering visualization</div>
          <div style="font-size: 0.875rem; margin-top: 0.5rem;">${error.message}</div>
        </div>
      `;
    }
  }

  /**
   * Initialize the inspector panel component
   */
  initializeInspector() {
    const inspectorContainer = document.getElementById('cashFlowInspector');
    if (inspectorContainer && typeof CashFlowInspector !== 'undefined') {
      this.inspector = new CashFlowInspector(inspectorContainer, this.currentData);
      console.log('[CashFlowModal] Inspector panel initialized');
    } else {
      console.error('[CashFlowModal] Inspector container or CashFlowInspector class not found');
    }
  }

  /**
   * Attach hover event handlers to Sankey diagram
   */
  attachHoverHandlers() {
    this.plotlyDiv = document.getElementById('cashFlowSankey');
    if (!this.plotlyDiv) {
      console.error('[CashFlowModal] Cannot attach hover handlers - plotlyDiv not found');
      return;
    }

    console.log('[CashFlowModal] Attaching hover handlers to plotlyDiv:', this.plotlyDiv);
    console.log('[CashFlowModal] Inspector instance:', this.inspector);
    console.log('[CashFlowModal] NodeMetadata available:', Object.keys(this.nodeMetadata || {}).length, 'nodes');

    // Handle hover events
    this.plotlyDiv.on('plotly_hover', (eventData) => {
      console.log('[CashFlowModal] plotly_hover event triggered!', eventData);

      // Cancel any pending unhover timeout
      if (this.unhoverTimeout) {
        clearTimeout(this.unhoverTimeout);
        this.unhoverTimeout = null;
        console.log('[CashFlowModal] Canceled pending unhover timeout');
      }

      if (!eventData || !eventData.points || eventData.points.length === 0) {
        console.log('[CashFlowModal] No event data or points');
        return;
      }

      const point = eventData.points[0];
      console.log('[CashFlowModal] Point data:', point);

      let metadata;

      // Check if hovering over a link/flow (links have source/target properties)
      if (point.source !== undefined || point.target !== undefined) {
        console.log('[CashFlowModal] Hovering over link - showing target node data');
        // Show the target node's data when hovering over a link
        const targetNodeIndex = point.target;
        console.log('[CashFlowModal] Link target index:', targetNodeIndex);
        metadata = this.nodeMetadata[targetNodeIndex];
      } else {
        // Hovering over a node directly
        const nodeIndex = point.pointNumber;
        console.log('[CashFlowModal] Node index:', nodeIndex);
        metadata = this.nodeMetadata[nodeIndex];
      }

      console.log('[CashFlowModal] Retrieved metadata:', metadata);

      if (metadata && this.inspector) {
        console.log('[CashFlowModal] Calling inspector.updateNode with:', metadata);
        this.inspector.updateNode(metadata);
      } else {
        console.warn('[CashFlowModal] Cannot update inspector:', {
          hasMetadata: !!metadata,
          hasInspector: !!this.inspector
        });
      }
    });

    // Handle unhover events
    this.plotlyDiv.on('plotly_unhover', () => {
      console.log('[CashFlowModal] plotly_unhover event triggered');

      // Clear any existing timeout
      if (this.unhoverTimeout) {
        clearTimeout(this.unhoverTimeout);
      }

      // Return to default state after a delay (gives time for next hover to cancel)
      this.unhoverTimeout = setTimeout(() => {
        if (this.inspector) {
          console.log('[CashFlowModal] Calling inspector.showDefault');
          this.inspector.showDefault();
        }
        this.unhoverTimeout = null;
      }, 500); // Increased from 300ms to 500ms for better tolerance
    });

    console.log('[CashFlowModal] Hover handlers attached ✅');
  }

  /**
   * Handle click on Sankey node or link
   *
   * @param {Object} eventData - Plotly click event data
   */
  handleNodeClick(eventData) {
    if (!eventData.points || eventData.points.length === 0) {
      console.log('[CashFlowModal] No points in click event');
      return;
    }

    const point = eventData.points[0];
    console.log('[CashFlowModal] Full point data:', point);

    const pointNumber = point.pointNumber;

    // CRITICAL FIX: Detect link clicks by checking for link-specific properties
    // Links have 'source' and 'target' properties, nodes don't
    // This is the most reliable way to distinguish them in Plotly Sankey
    if (point.source !== undefined || point.target !== undefined) {
      console.log('[CashFlowModal] Link/flow path clicked (has source/target) - ignoring');
      this.closeDrillDownPanel();
      return;
    }

    // Check if this is a node click by checking if pointNumber is within our nodes array
    // Nodes are stored in this.nodeLabels array. If pointNumber >= nodeLabels.length, it's a link
    if (pointNumber === undefined || pointNumber >= this.nodeLabels.length) {
      console.log('[CashFlowModal] Link clicked (pointNumber out of range) - ignoring');
      this.closeDrillDownPanel();
      return;
    }

    // This is a node click - look up the label and metadata
    const label = this.nodeLabels[pointNumber];
    const metadata = this.nodeMetadata[pointNumber];
    console.log('[CashFlowModal] Node clicked - pointNumber:', pointNumber, 'label:', label, 'metadata:', metadata);

    if (!label || !metadata) {
      console.warn('[CashFlowModal] No label/metadata found for pointNumber:', pointNumber);
      return;
    }

    // Use metadata to determine node type (more reliable than string parsing)
    if (metadata.type === 'total') {
      // Clicking total cash - close any open drill-down
      console.log('[CashFlowModal] Total Cash clicked - closing panel');
      this.closeDrillDownPanel();
    } else if (metadata.type === 'restaurant') {
      // Restaurant node clicked
      console.log('[CashFlowModal] Restaurant clicked:', metadata.code);
      this.showRestaurantDrillDown(metadata.code);
    } else if (metadata.type === 'shift') {
      // Shift node clicked - use metadata for reliable restaurant code
      console.log('[CashFlowModal] Shift clicked:', metadata.code, metadata.shift);
      this.showShiftDrillDown(`${metadata.code} ${metadata.shift}`);
    } else if (metadata.type === 'drawer') {
      // Drawer node clicked
      console.log('[CashFlowModal] Drawer clicked:', metadata.drawer);
      this.showDrawerDrillDown(metadata.drawer, label);
    } else {
      // Unknown node type - log for debugging
      console.warn('[CashFlowModal] Unknown node type:', metadata.type);
      this.closeDrillDownPanel();
    }
  }

  /**
   * Show restaurant drill-down panel
   *
   * @param {string} restaurantCode - Restaurant code (SDR, T12, TK9)
   */
  showRestaurantDrillDown(restaurantCode) {
    const data = this.currentData;
    const restaurants = data.restaurants || {};
    const restData = restaurants[restaurantCode];

    if (!restData) {
      console.warn('[CashFlowModal] No data for restaurant:', restaurantCode);
      return;
    }

    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();

    // Build restaurant detail HTML
    const restaurantNames = {
      'SDR': "Sandra's Mexican Cuisine",
      'T12': 'Tink-A-Tako #12',
      'TK9': 'Tink-A-Tako #9'
    };

    const shifts = restData.shifts || {};
    const morningData = shifts['Morning'] || { cash: 0, drawers: [] };
    const eveningData = shifts['Evening'] || { cash: 0, drawers: [] };

    let html = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <h3 style="font-size: 1.5rem; font-weight: 600; color: ${THEME_COLORS.text.primary}; margin: 0;">
            ${restaurantCode} - ${restaurantNames[restaurantCode]}
          </h3>
          <p style="font-size: 0.875rem; color: ${THEME_COLORS.text.muted}; margin: 0.25rem 0 0 0;">
            Week Cash Breakdown
          </p>
        </div>
        <button
          onclick="window.cashFlowModal.closeDrillDownPanel()"
          style="
            background: none;
            border: 1px solid ${THEME_COLORS.border};
            color: ${THEME_COLORS.text.secondary};
            font-size: 1.5rem;
            line-height: 1;
            padding: 0.25rem 0.75rem;
            border-radius: 0.375rem;
            cursor: pointer;
            transition: all 0.2s;
          "
          onmouseover="this.style.background='${THEME_COLORS.status.critical.bg}'; this.style.color='${THEME_COLORS.status.critical.text}';"
          onmouseout="this.style.background='none'; this.style.color='${THEME_COLORS.text.secondary}';"
        >×</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
        <!-- Morning Shift -->
        <div style="
          padding: 1.25rem;
          background: linear-gradient(135deg, rgba(255, 193, 7, 0.08) 0%, rgba(250, 246, 240, 0.5) 100%);
          border: 1px solid ${THEME_COLORS.border};
          border-radius: 0.5rem;
        ">
          <div style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.75rem;">
            ☀️ Morning Shift
          </div>
          <div style="font-size: 1.75rem; font-weight: 300; color: #FFA726; margin-bottom: 1rem;">
            ${businessEngine.formatCurrency(morningData.cash)}
          </div>
          <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">DRAWERS</div>
          ${morningData.drawers.map(drawer => `
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
              <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">${drawer.name}</span>
              <span style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.primary};">${businessEngine.formatCurrency(drawer.cash)}</span>
            </div>
          `).join('')}
        </div>

        <!-- Evening Shift -->
        <div style="
          padding: 1.25rem;
          background: linear-gradient(135deg, rgba(63, 81, 181, 0.08) 0%, rgba(250, 246, 240, 0.5) 100%);
          border: 1px solid ${THEME_COLORS.border};
          border-radius: 0.5rem;
        ">
          <div style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.75rem;">
            🌙 Evening Shift
          </div>
          <div style="font-size: 1.75rem; font-weight: 300; color: #3F51B5; margin-bottom: 1rem;">
            ${businessEngine.formatCurrency(eveningData.cash)}
          </div>
          <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">DRAWERS</div>
          ${eveningData.drawers.map(drawer => `
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid ${THEME_COLORS.border};">
              <span style="font-size: 0.875rem; color: ${THEME_COLORS.text.secondary};">${drawer.name}</span>
              <span style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.primary};">${businessEngine.formatCurrency(drawer.cash)}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Summary Stats -->
      <div style="
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        padding: 1rem;
        background: ${THEME_COLORS.status.normal.bg};
        border-radius: 0.5rem;
      ">
        <div style="text-align: center;">
          <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">TOTAL CASH</div>
          <div style="font-size: 1.25rem; font-weight: 600; color: ${THEME_COLORS.status.success.text};">
            ${businessEngine.formatCurrency(restData.total_cash)}
          </div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">TIPS</div>
          <div style="font-size: 1.25rem; font-weight: 600; color: #1976D2;">
            ${businessEngine.formatCurrency(restData.total_tips || 0)}
          </div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.25rem;">NET CASH</div>
          <div style="font-size: 1.25rem; font-weight: 600; color: ${THEME_COLORS.status.success.text};">
            ${businessEngine.formatCurrency(restData.net_cash || 0)}
          </div>
        </div>
      </div>
    `;

    const panel = document.getElementById('cashFlowDrillDown');
    panel.innerHTML = html;
    panel.classList.remove('hidden');

    // Smooth scroll to panel
    setTimeout(() => {
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  /**
   * Show shift drill-down panel
   *
   * @param {string} shiftLabel - Shift label (e.g., "SDR Morning")
   */
  showShiftDrillDown(shiftLabel) {
    console.log('[CashFlowModal] showShiftDrillDown called with:', shiftLabel);

    const parts = shiftLabel.split(' ');
    const restaurantCode = parts[0];
    const shiftName = parts[1];

    console.log('[CashFlowModal] Parsed - restaurantCode:', restaurantCode, 'shiftName:', shiftName);

    const data = this.currentData;
    const restaurants = data.restaurants || {};

    console.log('[CashFlowModal] Available restaurants:', Object.keys(restaurants));
    console.log('[CashFlowModal] Looking up restaurant:', restaurantCode);

    const restData = restaurants[restaurantCode];

    console.log('[CashFlowModal] Restaurant data found:', restData ? 'YES' : 'NO');
    if (restData) {
      console.log('[CashFlowModal] Restaurant data:', {
        total_cash: restData.total_cash,
        shifts: Object.keys(restData.shifts || {})
      });
    }

    if (!restData || !restData.shifts) {
      console.error('[CashFlowModal] No restaurant data or shifts found for:', restaurantCode);
      return;
    }

    const shiftData = restData.shifts[shiftName];
    if (!shiftData) {
      console.error('[CashFlowModal] No shift data found for:', shiftName);
      return;
    }

    console.log('[CashFlowModal] Shift data:', shiftData);

    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();

    const icon = shiftName === 'Morning' ? '☀️' : '🌙';
    const color = shiftName === 'Morning' ? '#FFA726' : '#3F51B5';

    let html = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <h3 style="font-size: 1.5rem; font-weight: 600; color: ${THEME_COLORS.text.primary}; margin: 0;">
            ${icon} ${restaurantCode} - ${shiftName} Shift
          </h3>
          <p style="font-size: 0.875rem; color: ${THEME_COLORS.text.muted}; margin: 0.25rem 0 0 0;">
            Cash Drawer Breakdown
          </p>
        </div>
        <button
          onclick="window.cashFlowModal.closeDrillDownPanel()"
          style="
            background: none;
            border: 1px solid ${THEME_COLORS.border};
            color: ${THEME_COLORS.text.secondary};
            font-size: 1.5rem;
            line-height: 1;
            padding: 0.25rem 0.75rem;
            border-radius: 0.375rem;
            cursor: pointer;
          "
        >×</button>
      </div>

      <div style="font-size: 2rem; font-weight: 300; color: ${color}; margin-bottom: 1.5rem; text-align: center;">
        ${businessEngine.formatCurrency(shiftData.cash)}
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        ${shiftData.drawers.map(drawer => {
          const percentage = ((drawer.cash / shiftData.cash) * 100).toFixed(1);
          return `
            <div style="
              padding: 1.25rem;
              background: white;
              border: 1px solid ${THEME_COLORS.border};
              border-radius: 0.5rem;
              text-align: center;
            ">
              <div style="font-size: 0.875rem; font-weight: 600; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
                ${drawer.name}
              </div>
              <div style="font-size: 1.5rem; font-weight: 600; color: ${THEME_COLORS.status.success.text}; margin-bottom: 0.25rem;">
                ${businessEngine.formatCurrency(drawer.cash)}
              </div>
              <div style="font-size: 0.75rem; color: ${THEME_COLORS.text.muted};">
                ${percentage}% of shift
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;

    const panel = document.getElementById('cashFlowDrillDown');
    panel.innerHTML = html;
    panel.classList.remove('hidden');

    setTimeout(() => {
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  /**
   * Show drawer drill-down panel
   *
   * @param {string} drawerName - Drawer name
   * @param {string} fullLabel - Full label with amount
   */
  showDrawerDrillDown(drawerName, fullLabel) {
    const { businessEngine } = this.engines;
    const THEME_COLORS = this.getColors();

    // Extract amount from label
    const amountStr = fullLabel.split('<br>')[1];

    let html = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <h3 style="font-size: 1.25rem; font-weight: 600; color: ${THEME_COLORS.text.primary}; margin: 0;">
            💵 ${drawerName}
          </h3>
        </div>
        <button
          onclick="window.cashFlowModal.closeDrillDownPanel()"
          style="
            background: none;
            border: 1px solid ${THEME_COLORS.border};
            color: ${THEME_COLORS.text.secondary};
            font-size: 1.5rem;
            line-height: 1;
            padding: 0.25rem 0.75rem;
            border-radius: 0.375rem;
            cursor: pointer;
          "
        >×</button>
      </div>

      <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 0.875rem; color: ${THEME_COLORS.text.muted}; margin-bottom: 0.5rem;">
          Week Total
        </div>
        <div style="font-size: 2.5rem; font-weight: 300; color: ${THEME_COLORS.status.success.text};">
          ${amountStr}
        </div>
      </div>
    `;

    const panel = document.getElementById('cashFlowDrillDown');
    panel.innerHTML = html;
    panel.classList.remove('hidden');

    setTimeout(() => {
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  /**
   * Close drill-down panel
   */
  closeDrillDownPanel() {
    const panel = document.getElementById('cashFlowDrillDown');
    if (panel) {
      panel.classList.add('hidden');
    }
  }
}

// ============================================
// Global Functions (Window Scope)
// ============================================

/**
 * Close cash flow modal
 */
window.closeCashFlowModal = function() {
  const modalContainer = document.getElementById('cash-flow-modal');
  const modal = modalContainer ? modalContainer.querySelector('.modal-overlay') : null;
  if (modal) {
    modal.classList.add('hidden');
    modalContainer.classList.add('hidden');
  }
};

/**
 * Show cash flow details modal
 * Called from OverviewCard onclick
 */
window.showCashDetails = function() {
  const weekData = window.dashboardApp?.getCurrentData();
  const cashFlowData = weekData?.overview?.cashFlow || null;

  if (!cashFlowData || !cashFlowData.total_cash) {
    console.warn('[CashFlowModal] No cash flow data available');
    // Show modal with empty state
    window.cashFlowModal?.open({});
  } else {
    console.log('[CashFlowModal] Opening with data:', cashFlowData);
    window.cashFlowModal?.open(cashFlowData);
  }
};

// ============================================
// Initialization
// ============================================

/**
 * Initialize cash flow modal
 *
 * @param {Object} engines - Dashboard engines (businessEngine, themeEngine, layoutEngine)
 */
export function initializeCashFlowModal(engines) {
  // Load Plotly.js if not already loaded
  if (typeof Plotly === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
    script.onload = () => {
      console.log('[CashFlowModal] Plotly.js loaded successfully');
      initModal();
    };
    script.onerror = () => {
      console.error('[CashFlowModal] Failed to load Plotly.js');
    };
    document.head.appendChild(script);
  } else {
    initModal();
  }

  function initModal() {
    // Create modal instance and attach to window
    window.cashFlowModal = new CashFlowModal(engines);

    // Find or create modal container
    let modalContainer = document.getElementById('cash-flow-modal');
    if (!modalContainer) {
      modalContainer = document.createElement('div');
      modalContainer.id = 'cash-flow-modal';
      document.body.appendChild(modalContainer);
    }

    // Render modal HTML into container
    modalContainer.innerHTML = window.cashFlowModal.render();

    console.log('[CashFlowModal] Initialized successfully with Plotly.js');
  }
}
