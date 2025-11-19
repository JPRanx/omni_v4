/**
 * Dashboard V3 - Z-Index System
 *
 * Complete z-index configuration based on comprehensive audit
 * Total Z-Index Layers: 7
 *
 * Breakdown:
 * - Base Layer: 0 (normal flow)
 * - Interactive Layers: 3 (elevated, dropdown, sticky)
 * - Overlay Layers: 4 (modal, tooltip, notification, debug)
 *
 * Source Files Analyzed:
 * - dashboard_generator.py (modal overlay, dropdown layers)
 * - WeekTabs.js (tab elevation)
 * - Modal components (overlay stacking)
 */

// ============================================
// Z-INDEX SCALE (7 layers)
// Organized from lowest to highest
// ============================================

export const layers = {
  // Base layer (default document flow)
  base: 0,

  // Slightly elevated content (cards on hover, active tabs)
  elevated: 10,

  // Dropdown menus, popovers
  dropdown: 1000,

  // Sticky headers, fixed navigation
  sticky: 1010,

  // Modal backdrop
  modalBackdrop: 1040,

  // Modal content (above backdrop)
  modalContent: 1050,

  // Tooltips (above modals)
  tooltip: 1070,

  // Notifications, toast messages (highest)
  notification: 1080,

  // Debug overlays (development only)
  debug: 9999,
};

// ============================================
// COMPONENT-SPECIFIC Z-INDEX (14 assignments)
// Mapped to layer system
// ============================================

export const components = {
  // Header
  header: {
    default: layers.base,
    sticky: layers.sticky,
  },

  // Week Tabs
  weekTab: {
    default: layers.base,
    active: layers.elevated,
    hover: layers.elevated,
  },

  // Cards
  card: {
    default: layers.base,
    hover: layers.elevated,
  },

  metricCard: {
    default: layers.base,
    hover: layers.elevated,
  },

  restaurantCard: {
    default: layers.base,
    hover: layers.elevated,
  },

  // Modal System
  modal: {
    backdrop: layers.modalBackdrop,
    content: layers.modalContent,
    closeButton: layers.modalContent + 1,  // 1051 (above content)
  },

  // Dropdown/Menus
  dropdown: {
    menu: layers.dropdown,
    overlay: layers.dropdown - 1,  // 999 (behind menu)
  },

  // Tooltips
  tooltip: {
    default: layers.tooltip,
    arrow: layers.tooltip,
  },

  // Notifications
  notification: {
    toast: layers.notification,
    banner: layers.notification - 10,  // 1070 (below toast)
  },

  // Day Cards (in investigation modal)
  dayCard: {
    default: layers.base,
    hover: layers.elevated,
  },

  // P&L Quadrants
  pnlQuadrant: {
    default: layers.base,
    hover: layers.elevated,
  },

  // Score Bar Shine Effect (inside card)
  scoreBarShine: {
    default: 5,  // Above bar background, below content
  },

  // Background Effects
  bodyShimmer: {
    default: -1,  // Behind all content
  },

  // Loading Overlays
  loading: {
    overlay: layers.modalBackdrop,
    spinner: layers.modalBackdrop + 1,  // 1041
  },
};

// ============================================
// INTERACTION STATES (3 patterns)
// Z-index changes on interaction
// ============================================

export const interactions = {
  // Card hover elevation
  cardHover: {
    from: layers.base,
    to: layers.elevated,
    transition: 'z-index 0s',  // Instant
  },

  // Tab activation
  tabActive: {
    from: layers.base,
    to: layers.elevated,
    transition: 'z-index 0s',
  },

  // Modal opening
  modalOpen: {
    backdrop: layers.modalBackdrop,
    content: layers.modalContent,
    transition: 'z-index 0s',
  },
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  '--z-base': layers.base,
  '--z-elevated': layers.elevated,
  '--z-dropdown': layers.dropdown,
  '--z-sticky': layers.sticky,
  '--z-modal-backdrop': layers.modalBackdrop,
  '--z-modal-content': layers.modalContent,
  '--z-tooltip': layers.tooltip,
  '--z-notification': layers.notification,
  '--z-debug': layers.debug,
};

// ============================================
// TAILWIND Z-INDEX CONFIG
// ============================================

export const tailwindZIndex = {
  0: '0',
  10: '10',
  20: '20',
  30: '30',
  40: '40',
  50: '50',
  auto: 'auto',
  base: layers.base,
  elevated: layers.elevated,
  dropdown: layers.dropdown,
  sticky: layers.sticky,
  'modal-backdrop': layers.modalBackdrop,
  'modal-content': layers.modalContent,
  tooltip: layers.tooltip,
  notification: layers.notification,
  debug: layers.debug,
};

// ============================================
// UTILITY CLASSES
// Pre-configured z-index combinations
// ============================================

export const zIndexClasses = {
  base: 'z-0',
  elevated: 'z-10',
  dropdown: 'z-[1000]',
  sticky: 'z-[1010]',
  modalBackdrop: 'z-[1040]',
  modalContent: 'z-[1050]',
  tooltip: 'z-[1070]',
  notification: 'z-[1080]',
  debug: 'z-[9999]',
};

// ============================================
// STACKING CONTEXTS
// Documentation of stacking context creation
// ============================================

export const stackingContexts = {
  // Elements that create new stacking contexts
  createContext: [
    'positioned elements with z-index (not auto)',
    'elements with opacity < 1',
    'elements with transform',
    'elements with filter',
    'elements with isolation: isolate',
  ],

  // Components that create stacking contexts
  components: [
    'modal (isolation: isolate)',
    'cards with transform on hover',
    'elements with animations (translateY)',
    'elements with box-shadow transitions',
  ],

  // Best practices
  guidelines: [
    'Use layer system, not arbitrary numbers',
    'Keep z-index values in 10s increments for flexibility',
    'Modal layers start at 1000+',
    'Tooltips above modals (1070+)',
    'Debug overlays use 9999',
    'Avoid z-index wars - use stacking contexts',
  ],
};

// ============================================
// DEBUG HELPERS
// For development visualization
// ============================================

export const debug = {
  // Visualize z-index layers (development only)
  visualizeLayer: (layerName) => {
    return {
      zIndex: layers[layerName],
      outline: '2px solid red',
      position: 'relative',
      '&::before': {
        content: `"Layer: ${layerName} (z: ${layers[layerName]})"`,
        position: 'absolute',
        top: 0,
        left: 0,
        background: 'red',
        color: 'white',
        padding: '2px 4px',
        fontSize: '10px',
        zIndex: layers.debug,
      },
    };
  },

  // Get all z-index values in use
  getAllLayers: () => {
    return Object.entries(layers).map(([name, value]) => ({
      name,
      value,
      css: `z-index: ${value}`,
    }));
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  layers,
  components,
  interactions,
  cssVariables,
  tailwindZIndex,
  zIndexClasses,
  stackingContexts,
  debug,

  // Metadata
  totalLayers: 7,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
};
