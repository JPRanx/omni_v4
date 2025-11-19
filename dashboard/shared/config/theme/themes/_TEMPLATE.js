/**
 * Dashboard V3 - Theme Template
 *
 * USE THIS TEMPLATE TO CREATE NEW THEMES
 *
 * Instructions:
 * 1. Copy this file and rename it (e.g., sunset.js, ocean.js, forest.js)
 * 2. Update the theme name on line 94
 * 3. Replace all color values with your theme colors
 * 4. Customize typography, animations, and effects if desired
 * 5. Register your theme in themes/index.js (see README.md for details)
 * 6. Your theme will automatically appear in the theme switcher
 *
 * Color Guidelines:
 * - Use hex colors (#RRGGBB format)
 * - Ensure sufficient contrast for accessibility (WCAG AA minimum)
 * - Test your theme with actual dashboard content
 * - All 23 semantic colors are REQUIRED for full theme coverage
 *
 * Version: 3.0.0
 * Date: 2025-11-01
 */

import { createTheme } from '../themeTemplate.js';

export const myTheme = createTheme(
  // ============================================
  // THEME NAME (Change this to your theme name)
  // ============================================
  'My Theme Name',  // Display name shown in theme switcher

  // ============================================
  // SEMANTIC COLORS (ALL 23 REQUIRED)
  // ============================================
  {
    // ==========================================
    // TEXT HIERARCHY (4 colors)
    // ==========================================
    // Used for: All text content across the dashboard

    text_primary: '#000000',
    // Primary text color - Main headings, important content, metric values
    // Where used: H1/H2 headers, card titles, primary labels, data values
    // Example: "Restaurant Performance", "$45,892", "Week 42"
    // Contrast: Must contrast well against background_primary

    text_secondary: '#555555',
    // Secondary text color - Subheadings, descriptions, supporting content
    // Where used: H3/H4 headers, card subtitles, descriptions, helper text
    // Example: "Last 7 days performance", "vs. last week", date ranges
    // Contrast: Slightly muted from text_primary but still readable

    text_muted: '#888888',
    // Muted text color - Labels, metadata, tertiary information
    // Where used: Input labels, table column headers, timestamps, metadata
    // Example: "Updated 5 mins ago", "Category:", small print
    // Contrast: Can be lighter but must remain legible

    text_disabled: '#CCCCCC',
    // Disabled text color - Inactive or unavailable elements
    // Where used: Disabled buttons, inactive menu items, unavailable options
    // Example: Grayed-out dates, disabled form fields
    // Contrast: Clearly indicates non-interactive state

    // ==========================================
    // BACKGROUNDS (4 colors)
    // ==========================================
    // Used for: Page backgrounds, cards, elevated elements

    background_primary: '#FFFFFF',
    // Primary background - Main page/canvas background
    // Where used: Body background, main container background
    // Example: The base color behind all content
    // Note: Should be light for dark text or dark for light text

    background_card: '#FFFFFF',
    // Card background - Individual card and section backgrounds
    // Where used: Restaurant cards, metric cards, data panels
    // Example: White cards on light gray background
    // Note: Often same as background_primary or slightly different

    background_elevated: '#F5F5F5',
    // Elevated background - Modals, dropdowns, popovers
    // Where used: Modal dialogs, dropdown menus, tooltips, overlays
    // Example: Investigation modal, date picker dropdown
    // Note: Should stand out from background_card (lighter or darker)

    background_hover: '#F9F9F9',
    // Hover background - Interactive element hover states
    // Where used: Button hovers, row hovers, clickable card hovers
    // Example: Table row on hover, card lift effect background
    // Note: Subtle change from background_card for smooth transitions

    // ==========================================
    // BORDERS (3 colors)
    // ==========================================
    // Used for: Dividing sections, card edges, separators

    border_strong: '#333333',
    // Strong border - Major section dividers, emphasized borders
    // Where used: Main section separators, selected card borders, active tabs
    // Example: Border around selected restaurant card
    // Note: Most visible border, draws attention

    border_default: '#DDDDDD',
    // Default border - Standard card borders, dividers
    // Where used: Card edges, form input borders, table borders
    // Example: Gray border around metric cards
    // Note: Most common border color, neutral and clean

    border_subtle: '#EEEEEE',
    // Subtle border - Light separators, table lines
    // Where used: Table row separators, subtle dividers, inner borders
    // Example: Light line between table rows
    // Note: Barely visible, creates gentle separation

    // ==========================================
    // ACCENTS (3 colors)
    // ==========================================
    // Used for: Brand colors, interactive elements, highlights

    accent_primary: '#0066FF',
    // Primary accent - Main brand color, primary actions
    // Where used: Primary buttons, active states, brand highlights, charts
    // Example: "View Details" button, selected tab indicator
    // Note: Your main brand color, used for important CTAs

    accent_secondary: '#FF6600',
    // Secondary accent - Supporting accent, secondary actions
    // Where used: Secondary buttons, alternative highlights, complementary charts
    // Example: "Export" button, secondary metric highlights
    // Note: Complements accent_primary, used for variety

    accent_interactive: '#0099CC',
    // Interactive accent - Links, clickable elements
    // Where used: Text links, clickable icons, interactive labels
    // Example: "Learn more" link, clickable timestamps
    // Note: Must be distinguishable from text colors

    // ==========================================
    // DASHBOARD-SPECIFIC (7 colors)
    // ==========================================
    // Used for: Dashboard-specific components and data visualization

    dashboard_metric: '#000000',
    // Metric values - Large numbers, KPIs, data values
    // Where used: Revenue numbers, percentages, sales figures
    // Example: "$45,892", "87%", "142 orders"
    // Note: Often same as text_primary for consistency

    dashboard_metricLabel: '#666666',
    // Metric labels - Labels for metrics and KPIs
    // Where used: Labels above/below metric values
    // Example: "Total Revenue", "Average Order Value"
    // Note: Often same as text_secondary or text_muted

    dashboard_sectionHeader: '#000000',
    // Section headers - Major section titles
    // Where used: "Week Overview", "Restaurant Performance", "P&L Summary"
    // Example: Large section divider headers
    // Note: Often same as text_primary, may match accent_primary

    dashboard_tableHeader: '#333333',
    // Table headers - Column headers in data tables
    // Where used: Table column headers, data grid headers
    // Example: "Restaurant", "Sales", "Orders", "Status"
    // Note: Can be text_primary or slightly different for emphasis

    dashboard_tableRow: '#FAFAFA',
    // Table rows - Alternating row backgrounds
    // Where used: Zebra-striping in tables for readability
    // Example: Every other row in restaurant performance table
    // Note: Very subtle, just enough to distinguish rows

    dashboard_gradientStart: '#0066FF',
    // Gradient start - Beginning color for gradient backgrounds
    // Where used: Header gradients, banner backgrounds, decorative gradients
    // Example: Restaurant header gradient left side
    // Note: Often matches accent_primary

    dashboard_gradientEnd: '#00AAFF',
    // Gradient end - Ending color for gradient backgrounds
    // Where used: Header gradients, banner backgrounds, decorative gradients
    // Example: Restaurant header gradient right side
    // Note: Often matches accent_secondary or a lighter shade

    // ==========================================
    // STATUS COLORS (6 status types)
    // ==========================================
    // Each status has 3 properties: bg (background), text, border
    // Used for: Status badges, alerts, notifications, feedback

    status: {
      success: {
        bg: '#F0FDF4',      // Light green background
        text: '#15803D',    // Dark green text
        border: '#16A34A',  // Medium green border
      },
      // Used for: Success messages, positive metrics, completed states
      // Example: "Excellent performance", profit indicators, check marks

      warning: {
        bg: '#FEFCE8',      // Light yellow background
        text: '#A16207',    // Dark yellow/amber text
        border: '#CA8A04',  // Medium yellow border
      },
      // Used for: Warning messages, attention needed, moderate alerts
      // Example: "Needs attention" badge, moderate stress indicators

      error: {
        bg: '#FEF2F2',      // Light red background
        text: '#991B1B',    // Dark red text
        border: '#DC2626',  // Medium red border
      },
      // Used for: Error messages, critical issues, negative indicators
      // Example: "Critical" badge, high stress, loss indicators

      critical: {
        bg: '#FEF2F2',      // Light red background (often same as error)
        text: '#991B1B',    // Dark red text
        border: '#DC2626',  // Medium red border
      },
      // Used for: Critical alerts, urgent issues, severe problems
      // Example: System failures, severe capacity issues
      // Note: Often same as error but can be more intense

      info: {
        bg: '#EFF6FF',      // Light blue background
        text: '#1D4ED8',    // Dark blue text
        border: '#3B82F6',  // Medium blue border
      },
      // Used for: Informational messages, tips, neutral notifications
      // Example: "Pro tip", information tooltips, help text

      normal: {
        bg: '#F9FAFB',      // Light gray background
        text: '#374151',    // Dark gray text
        border: '#D1D5DB',  // Medium gray border
      }
      // Used for: Neutral states, default badges, normal operations
      // Example: "Normal" status, default state indicators
    }
  },

  // ============================================
  // OPTIONAL ENHANCEMENTS
  // ============================================
  // Customize these if you want theme-specific typography, animations, or effects
  // If omitted, sensible defaults will be used
  {
    // ==========================================
    // TYPOGRAPHY (Optional)
    // ==========================================
    typography: {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      // Font stack for the theme (optional, defaults to Inter)

      scale: 1.0
      // Typography scale multiplier (1.0 = default, 1.1 = 10% larger, 0.9 = 10% smaller)
    },

    // ==========================================
    // ANIMATIONS (Optional)
    // ==========================================
    animations: {
      duration: 'normal',
      // Animation speed: 'fast' (150ms), 'normal' (300ms), 'slow' (500ms)

      easing: 'ease'
      // Easing function: 'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear'
    },

    // ==========================================
    // EFFECTS (Optional)
    // ==========================================
    effects: {
      shadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      // Default box shadow for cards and elevated elements

      shadowElevated: '0 10px 15px rgba(0, 0, 0, 0.1)',
      // Elevated shadow for modals and popovers

      borderRadius: '0.5rem'
      // Default border radius (0.5rem = 8px, 0.375rem = 6px, 0.25rem = 4px)
    }
  }
);

// ============================================
// EXPORT
// ============================================
// Export your theme so it can be imported in themes/index.js
export default myTheme;

// ============================================
// NEXT STEPS
// ============================================
// 1. Copy this file and rename it (e.g., sunset.js)
// 2. Change 'myTheme' variable name to match your theme (e.g., sunsetTheme)
// 3. Update theme name on line 27 (e.g., 'Sunset Blaze')
// 4. Fill in all color values with your theme colors
// 5. Customize typography, animations, effects if desired
// 6. Open themes/index.js and add your theme:
//    - Import: import { sunsetTheme } from './sunset.js';
//    - Register: sunset: sunsetTheme, (in the themes object)
// 7. Refresh your dashboard - your theme will appear in the theme switcher!
//
// For detailed instructions, see README.md in this directory
// For color role reference, see COLOR_ROLES.md in this directory
