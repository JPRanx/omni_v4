# Dashboard V3 - Semantic Color Roles Reference

Complete reference guide for all 27 semantic color roles in the Dashboard V3 theme system.

## Overview

The semantic theme system uses **role-based color naming** instead of aesthetic naming. This means colors are named by their **PURPOSE** (e.g., `text_primary`) rather than their **APPEARANCE** (e.g., `darkBrown`).

**Benefits:**
- ✅ Themes are portable - same components work across all themes
- ✅ Consistent UI - every theme uses the same semantic structure
- ✅ Easy maintenance - change colors without touching component code
- ✅ Clear intent - color names describe what they're used for

---

## Color Categories

| Category | Count | Purpose |
|----------|-------|---------|
| [Text](#text-hierarchy) | 4 | All text content and typography |
| [Backgrounds](#backgrounds) | 4 | Page, card, and elevated element backgrounds |
| [Borders](#borders) | 3 | Dividers, card edges, separators |
| [Accents](#accents) | 3 | Brand colors, interactive elements |
| [Dashboard](#dashboard-specific) | 7 | Dashboard-specific components |
| [Status](#status-colors) | 6 types × 3 | Status badges, alerts, notifications |

**Total Required Colors:** 23 base + 18 status (6 types × 3 properties) = **41 total values**

---

## Text Hierarchy

### `text_primary`

**Purpose:** Primary text color for main content and headings

**Where Used:**
- H1, H2 headers and titles
- Card titles and main labels
- Metric values and important numbers
- Primary data in tables
- Main navigation items

**Examples:**
- "Restaurant Performance Dashboard"
- "$45,892.50"
- "Week 42 - November 2025"
- Restaurant names in cards
- Table cell data

**Guidelines:**
- Must have strong contrast against `background_primary` (WCAG AA: 4.5:1 minimum)
- Should be the darkest/most prominent text color
- Used for information that needs immediate attention
- Typically dark on light backgrounds, light on dark backgrounds

**Example Values:**
- Desert theme: `#3D3128` (dark brown)
- Graphite theme: `#1E293B` (slate-800)
- Light theme: `#000000` or `#1A1A1A`
- Dark theme: `#FFFFFF` or `#F5F5F5`

---

### `text_secondary`

**Purpose:** Secondary text for supporting content and descriptions

**Where Used:**
- H3, H4 headers and subheadings
- Card subtitles and descriptions
- Supporting text and explanations
- Secondary labels
- Table headers

**Examples:**
- "Performance over the last 7 days"
- "vs. previous week"
- Date ranges and time periods
- "Category:", "Status:", "Location:"
- Column headers in data tables

**Guidelines:**
- Must contrast against backgrounds (WCAG AA: 4.5:1 for small text)
- Slightly lighter/muted compared to `text_primary`
- Should still be clearly readable
- Creates visual hierarchy from primary text

**Example Values:**
- Desert theme: `#594A3C` (medium brown)
- Graphite theme: `#475569` (slate-600)
- Light theme: `#555555` or `#666666`
- Dark theme: `#D4D4D4` or `#CCCCCC`

---

### `text_muted`

**Purpose:** Muted text for labels, metadata, and tertiary information

**Where Used:**
- Input field labels
- Timestamps and update times
- Metadata and auxiliary information
- Helper text and hints
- Placeholder text
- Small print and footnotes

**Examples:**
- "Updated 5 minutes ago"
- "Last sync: 2:45 PM"
- Form field labels: "Email", "Password"
- Tooltips and help text
- "(Optional)" indicators

**Guidelines:**
- Must still be legible (WCAG AA: 4.5:1, but can approach 3:1 for large text)
- Noticeably lighter than `text_secondary`
- Used for information that's available but not critical
- Should not draw immediate attention

**Example Values:**
- Desert theme: `#6E5D4B` (light brown)
- Graphite theme: `#64748B` (slate-500)
- Light theme: `#888888` or `#999999`
- Dark theme: `#A3A3A3` or `#999999`

---

### `text_disabled`

**Purpose:** Disabled text for inactive or unavailable elements

**Where Used:**
- Disabled buttons and inputs
- Inactive menu items
- Unavailable options
- Grayed-out dates
- Read-only text
- Expired items

**Examples:**
- Disabled "Submit" button text
- Inactive navigation items
- Unavailable date selections in calendar
- Expired promo codes
- Read-only form fields

**Guidelines:**
- Should clearly indicate non-interactive state
- Much lighter than other text colors
- Contrast can be lower (WCAG doesn't apply to disabled elements)
- Should not be confusing with `text_muted` (must be clearly more faded)

**Example Values:**
- Desert theme: `#A0938B` (very light brown)
- Graphite theme: `#94A3B8` (slate-400)
- Light theme: `#CCCCCC` or `#DDDDDD`
- Dark theme: `#666666` or `#555555`

---

## Backgrounds

### `background_primary`

**Purpose:** Main page/canvas background color

**Where Used:**
- Body background
- Main container background
- Base layer behind all content
- Canvas for the entire application

**Examples:**
- The color behind all cards and sections
- Negative space around content
- The "paper" color of the dashboard

**Guidelines:**
- Foundation color for the entire theme
- Must contrast well with `text_primary`
- Light themes: Use white or off-white
- Dark themes: Use dark gray or black
- Should not be distracting - neutral and comfortable

**Example Values:**
- Desert theme: `#FAF6F0` (warm pearl/cream)
- Graphite theme: `#F8FAFC` (cool slate-50)
- Light theme: `#FFFFFF` or `#F5F5F5`
- Dark theme: `#121212` or `#1A1A1A`

---

### `background_card`

**Purpose:** Card and section background color

**Where Used:**
- Restaurant cards
- Metric cards
- Data panels and sections
- Content containers
- Sidebar backgrounds

**Examples:**
- Individual restaurant performance cards
- Week overview card
- P&L summary sections
- Side navigation panel

**Guidelines:**
- Must provide clear separation from `background_primary`
- Often white or slightly different from primary background
- Creates visual hierarchy and grouping
- Should have subtle elevation from primary background

**Example Values:**
- Desert theme: `#FFFFFF` (pure white cards on cream)
- Graphite theme: `#FFFFFF` (white cards on light slate)
- Light theme: `#FFFFFF` (white cards on gray)
- Dark theme: `#1E1E1E` or `#2A2A2A` (dark cards on darker bg)

---

### `background_elevated`

**Purpose:** Elevated element backgrounds (modals, dropdowns, overlays)

**Where Used:**
- Modal dialogs
- Dropdown menus
- Popover tooltips
- Overlays and sheets
- Floating panels

**Examples:**
- Investigation modal overlay
- Date picker dropdown
- Context menu popover
- Settings panel
- Notification toasts

**Guidelines:**
- Must stand out from `background_card` - typically lighter or darker
- Creates sense of elevation/layering
- Often has stronger shadow than cards
- Should be clearly distinguishable as "on top" of other content

**Example Values:**
- Desert theme: `#F5EDE2` (warm elevated cream)
- Graphite theme: `#F1F5F9` (slate-100)
- Light theme: `#FFFFFF` with shadow, or `#FAFAFA`
- Dark theme: `#2A2A2A` or `#333333` (lighter than cards)

---

### `background_hover`

**Purpose:** Hover state background for interactive elements

**Where Used:**
- Button hover states
- Table row hovers
- Card hover effects
- Interactive list item hovers
- Menu item hovers

**Examples:**
- Restaurant card on hover
- Table row when mouse over
- Navigation item hover
- Dropdown option hover
- Button background on hover

**Guidelines:**
- Subtle shift from `background_card`
- Should be noticeable but not jarring
- Indicates interactivity and clickability
- Smooth transition for better UX

**Example Values:**
- Desert theme: `#FEF9F3` (very light warm hover)
- Graphite theme: `#F8FAFC` (slate-50)
- Light theme: `#F9F9F9` or `#F0F0F0`
- Dark theme: `#282828` or `#2E2E2E` (slightly lighter)

---

## Borders

### `border_strong`

**Purpose:** Strong borders for major dividers and emphasis

**Where Used:**
- Selected card borders
- Active tab indicators
- Focused input borders
- Major section dividers
- Emphasized boundaries

**Examples:**
- Currently selected restaurant card
- Active week tab underline
- Focused search input
- Section separator lines
- Active filter border

**Guidelines:**
- Most visible border color
- Draws attention and emphasis
- Often matches `accent_primary`
- Creates clear visual separation

**Example Values:**
- Desert theme: `#B89968` (bronze - matches accent)
- Graphite theme: `#0EA5E9` (sky-500 - matches accent)
- Light theme: Your primary brand color
- Dark theme: Bright version of accent color

---

### `border_default`

**Purpose:** Standard borders for cards, inputs, and dividers

**Where Used:**
- Card edges
- Form input borders
- Table borders
- Default dividers
- Section borders

**Examples:**
- Restaurant card border
- Text input border (unfocused)
- Table cell borders
- Metric card border
- Panel dividers

**Guidelines:**
- Most common border color - neutral and clean
- Subtle but visible
- Should not compete with content
- Creates structure without distraction

**Example Values:**
- Desert theme: `#E5DDD0` (soft beige)
- Graphite theme: `#E2E8F0` (slate-200)
- Light theme: `#DDDDDD` or `#E0E0E0`
- Dark theme: `#404040` or `#3A3A3A`

---

### `border_subtle`

**Purpose:** Subtle borders for light separators and inner dividers

**Where Used:**
- Table row separators
- Inner card dividers
- Subtle section separators
- Light separator lines
- Inner table borders

**Examples:**
- Line between table rows
- Divider between card sections
- Subtle separator in lists
- Inner borders in grids

**Guidelines:**
- Barely visible - creates gentle separation
- Lighter than `border_default`
- Should not be prominent
- Used for internal structure

**Example Values:**
- Desert theme: `#F0E8DC` (very light beige)
- Graphite theme: `#F1F5F9` (slate-100)
- Light theme: `#EEEEEE` or `#F5F5F5`
- Dark theme: `#2A2A2A` or `#2E2E2E`

---

## Accents

### `accent_primary`

**Purpose:** Primary brand color and main call-to-action

**Where Used:**
- Primary action buttons
- Main brand highlights
- Active states
- Important icons
- Progress indicators
- Chart primary colors

**Examples:**
- "View Details" button
- Selected tab indicator
- Active navigation item
- Primary chart bars
- Loading spinners
- Success checkmarks

**Guidelines:**
- Your main brand identity color
- Most prominent accent in the theme
- Should stand out against backgrounds
- Used sparingly for maximum impact
- Must have good contrast for accessibility

**Example Values:**
- Desert theme: `#B89968` (bronze gold)
- Graphite theme: `#0EA5E9` (sky-500 blue)
- Light theme: Your brand color (e.g., `#0066FF`)
- Dark theme: Brighter version of brand color

---

### `accent_secondary`

**Purpose:** Secondary accent for variety and supporting actions

**Where Used:**
- Secondary action buttons
- Alternative highlights
- Supporting chart colors
- Secondary icons
- Complementary accents

**Examples:**
- "Export" button
- Secondary metric highlights
- Alternate chart series
- Supporting badges
- Secondary brand elements

**Guidelines:**
- Complements `accent_primary` without clashing
- Used for variety in data visualization
- Should be distinguishable from primary
- Creates visual interest and depth

**Example Values:**
- Desert theme: `#D4A574` (amber sand)
- Graphite theme: `#6366F1` (indigo-500)
- Light theme: Complementary to primary (e.g., `#FF6600`)
- Dark theme: Complementary bright color

---

### `accent_interactive`

**Purpose:** Interactive elements like links and clickable text

**Where Used:**
- Text links
- Clickable labels
- Interactive icons
- Hyperlinks
- Anchor text

**Examples:**
- "Learn more" links
- Clickable timestamps
- Help links
- External links
- In-text navigation links

**Guidelines:**
- Must be clearly distinguishable as clickable
- Different from regular text colors
- Traditional link color (blue) works well but not required
- Should have hover state

**Example Values:**
- Desert theme: `#6B8E9B` (oasis water blue)
- Graphite theme: `#0EA5E9` (sky-500)
- Light theme: `#0066CC` or `#2563EB`
- Dark theme: `#60A5FA` or lighter blue

---

## Dashboard-Specific

### `dashboard_metric`

**Purpose:** Large metric values, KPIs, and important numbers

**Where Used:**
- Revenue figures
- Sales totals
- Percentage values
- Order counts
- Key performance indicators

**Examples:**
- "$45,892.50"
- "87.5%"
- "142 orders"
- "94 score"
- "$2,450 profit"

**Guidelines:**
- Often same as `text_primary` for consistency
- Can be accent color for emphasis
- Must be highly readable - used for critical data
- Should stand out from labels

**Example Values:**
- Desert theme: `#3D3128` (matches text_primary)
- Graphite theme: `#1E293B` (matches text_primary)
- Can also use: `accent_primary` for emphasis

---

### `dashboard_metricLabel`

**Purpose:** Labels for metrics and KPIs

**Where Used:**
- Labels above/below metrics
- Metric descriptions
- KPI category labels
- Unit labels

**Examples:**
- "Total Revenue"
- "Average Order Value"
- "per day"
- "Sales Growth"
- "Service Score"

**Guidelines:**
- Often same as `text_secondary` or `text_muted`
- Should not compete with metric values
- Lighter than the metrics themselves
- Creates hierarchy between label and value

**Example Values:**
- Desert theme: `#6E5D4B` (camel leather)
- Graphite theme: `#64748B` (slate-500)
- Often: `text_secondary` or `text_muted`

---

### `dashboard_sectionHeader`

**Purpose:** Major section headers and titles

**Where Used:**
- "Week Overview" header
- "Restaurant Performance" title
- "P&L Summary" section
- Major dashboard sections
- Category headers

**Examples:**
- "Weekly Performance Dashboard"
- "Restaurants"
- "Financial Summary"
- "Capacity Analysis"

**Guidelines:**
- Often same as `text_primary`
- Can be `accent_primary` for brand emphasis
- Should be prominent and clear
- Hierarchically above subsection headers

**Example Values:**
- Desert theme: `#3D3128` (matches text_primary)
- Graphite theme: `#1E293B` (matches text_primary)
- Can also use: `accent_primary` for emphasis

---

### `dashboard_tableHeader`

**Purpose:** Table column headers and data grid headers

**Where Used:**
- Column headers in tables
- Data grid headers
- Spreadsheet-style headers
- Table metadata headers

**Examples:**
- "Restaurant" column
- "Sales" column
- "Orders" column
- "Status" column
- "Actions" column

**Guidelines:**
- Should stand out from table data
- Often slightly darker/different from body text
- Can match `text_primary` or `text_secondary`
- May have different background color

**Example Values:**
- Desert theme: `#594A3C` (dune shadow)
- Graphite theme: `#475569` (slate-600)
- Often: `text_primary` or `text_secondary`

---

### `dashboard_tableRow`

**Purpose:** Alternating table row backgrounds (zebra striping)

**Where Used:**
- Alternating rows in data tables
- Zebra-striped tables
- Row hover backgrounds
- List alternating items

**Examples:**
- Every other row in restaurant table
- Alternating order list items
- Striped transaction history

**Guidelines:**
- Very subtle - just enough to distinguish rows
- Improves readability in long tables
- Should not be distracting
- Often very close to `background_card`

**Example Values:**
- Desert theme: `#FAFAFA` (very light gray)
- Graphite theme: `#F8FAFC` (slate-50)
- Light theme: `#F9F9F9` or `#FAFAFA`
- Dark theme: `#1E1E1E` or `#242424`

---

### `dashboard_gradientStart`

**Purpose:** Starting color for gradient backgrounds

**Where Used:**
- Header gradient backgrounds (left side)
- Banner gradients (top)
- Decorative gradient elements (start)
- Hero section gradients

**Examples:**
- Restaurant header gradient (left)
- Week overview banner gradient (top)
- Promotional banner gradients

**Guidelines:**
- Often matches or complements `accent_primary`
- Should transition smoothly to `dashboard_gradientEnd`
- Consider gradient direction (usually left-to-right or top-to-bottom)
- Test gradient on actual content

**Example Values:**
- Desert theme: `#B89968` (bronze - matches accent)
- Graphite theme: `#0EA5E9` (sky-500)
- Often: `accent_primary`

---

### `dashboard_gradientEnd`

**Purpose:** Ending color for gradient backgrounds

**Where Used:**
- Header gradient backgrounds (right side)
- Banner gradients (bottom)
- Decorative gradient elements (end)
- Hero section gradients

**Examples:**
- Restaurant header gradient (right)
- Week overview banner gradient (bottom)
- Promotional banner gradients

**Guidelines:**
- Should complement `dashboard_gradientStart`
- Creates smooth transition
- Often lighter or darker shade of start color
- Can be completely different color for bold effect

**Example Values:**
- Desert theme: `#D4A574` (amber sand)
- Graphite theme: `#6366F1` (indigo-500)
- Often: `accent_secondary` or lighter/darker version of start

---

## Status Colors

Each status type has **3 required properties**: `bg` (background), `text` (text color), `border` (border color)

### `status.success`

**Purpose:** Success feedback, positive indicators, completed states

**Properties:**
- `bg`: Light green background
- `text`: Dark green text
- `border`: Medium green border

**Where Used:**
- "Excellent" performance badges
- Success notifications
- Completed task indicators
- Positive metric changes
- Profit indicators
- Check marks and confirmations

**Examples:**
- ✅ "Excellent Performance"
- 🟢 "+15% sales growth"
- ✓ "Order completed"
- "✓ All checks passed"

**Recommended Colors:**
- `bg`: `#F0FDF4` (green-50), `#ECFDF5`, `#D1FAE5`
- `text`: `#15803D` (green-700), `#166534`, `#065F46`
- `border`: `#16A34A` (green-600), `#22C55E`, `#10B981`

---

### `status.warning`

**Purpose:** Warning feedback, caution indicators, attention needed

**Properties:**
- `bg`: Light yellow/amber background
- `text`: Dark yellow/brown text
- `border`: Medium yellow/amber border

**Where Used:**
- "Needs Attention" badges
- Warning notifications
- Moderate stress indicators
- Approaching thresholds
- Caution messages

**Examples:**
- ⚠️ "Needs Attention"
- 🟡 "Approaching capacity"
- "⚠ Review recommended"
- "Moderate stress level"

**Recommended Colors:**
- `bg`: `#FEFCE8` (yellow-50), `#FEF3C7`, `#FEF08A`
- `text`: `#A16207` (yellow-700), `#92400E`, `#854D0E`
- `border`: `#CA8A04` (yellow-600), `#EAB308`, `#F59E0B`

---

### `status.error`

**Purpose:** Error feedback, critical issues, negative indicators

**Properties:**
- `bg`: Light red background
- `text`: Dark red text
- `border`: Medium red border

**Where Used:**
- Error messages
- Failed operations
- Negative metrics
- Loss indicators
- Validation errors
- Critical issues

**Examples:**
- ❌ "Error occurred"
- 🔴 "-10% sales decline"
- "✗ Operation failed"
- "High stress level"

**Recommended Colors:**
- `bg`: `#FEF2F2` (red-50), `#FEE2E2`, `#FECACA`
- `text`: `#991B1B` (red-700), `#B91C1C`, `#DC2626`
- `border`: `#DC2626` (red-600), `#EF4444`, `#F87171`

---

### `status.critical`

**Purpose:** Critical alerts, urgent issues, severe problems

**Properties:**
- `bg`: Light red background (often same as error)
- `text`: Dark red text (often darker than error)
- `border`: Medium red border (often stronger than error)

**Where Used:**
- System failures
- Severe capacity issues
- Emergency alerts
- Urgent action required
- Critical system messages

**Examples:**
- 🚨 "Critical: Immediate action required"
- "System failure"
- "Emergency maintenance needed"

**Recommended Colors:**
- Often same as `error` or slightly more intense
- `bg`: `#FEF2F2` (red-50), `#FEE2E2`
- `text`: `#991B1B` (red-700), `#7F1D1D` (darker)
- `border`: `#DC2626` (red-600), `#B91C1C` (darker)

---

### `status.info`

**Purpose:** Informational messages, tips, neutral notifications

**Properties:**
- `bg`: Light blue background
- `text`: Dark blue text
- `border`: Medium blue border

**Where Used:**
- Info tooltips
- Help messages
- Tips and hints
- Neutral notifications
- Information panels
- Documentation callouts

**Examples:**
- ℹ️ "Pro tip: Use filters for better insights"
- "📘 Learn more about metrics"
- "ℹ Information updated"
- "Helpful hint"

**Recommended Colors:**
- `bg`: `#EFF6FF` (blue-50), `#DBEAFE`, `#BFDBFE`
- `text`: `#1D4ED8` (blue-700), `#1E40AF`, `#075985`
- `border`: `#3B82F6` (blue-500), `#2563EB`, `#0EA5E9`

---

### `status.normal`

**Purpose:** Normal/neutral states, default indicators

**Properties:**
- `bg`: Light gray background
- `text`: Dark gray text
- `border`: Medium gray border

**Where Used:**
- Default status badges
- Neutral indicators
- Normal operation state
- Standard/average performance
- Inactive states

**Examples:**
- "Normal operation"
- "Average performance"
- "Standard status"
- Default state badges

**Recommended Colors:**
- `bg`: `#F9FAFB` (gray-50), `#F3F4F6`, `#E5E7EB`
- `text`: `#374151` (gray-700), `#4B5563`, `#6B7280`
- `border`: `#D1D5DB` (gray-300), `#9CA3AF`, `#6B7280`

---

## Color Naming Conventions

### ✅ Semantic Naming (Good)
- `text_primary` - Named by purpose
- `accent_interactive` - Describes role
- `background_elevated` - Indicates usage
- `dashboard_metric` - Context-specific

### ❌ Aesthetic Naming (Bad)
- `darkBrown` - Describes appearance
- `lightBlue` - Color-specific
- `sandyBeige` - Visual description
- `skyColor` - Aesthetic name

### Why Semantic?
1. **Theme Independence:** Components work with any theme
2. **Clear Intent:** Immediately understand the purpose
3. **Easy Maintenance:** Change colors without touching code
4. **Consistency:** Every theme uses the same semantic structure

---

## Accessibility Guidelines

### Contrast Ratios (WCAG)

**Level AA (Minimum):**
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (≥ 18pt): 3:1 contrast ratio
- UI components: 3:1 contrast ratio

**Level AAA (Enhanced):**
- Normal text: 7:1 contrast ratio
- Large text: 4.5:1 contrast ratio

### Testing Tools
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)
- Browser DevTools Accessibility panel

### Key Pairings to Test
- `text_primary` on `background_primary`
- `text_secondary` on `background_card`
- `accent_primary` on `background_card`
- Status text on status backgrounds

---

## Quick Reference Cheatsheet

```javascript
// TEXT
text_primary          // Main headings, important content
text_secondary        // Subheadings, descriptions
text_muted            // Labels, metadata
text_disabled         // Inactive elements

// BACKGROUNDS
background_primary    // Page background
background_card       // Card backgrounds
background_elevated   // Modals, dropdowns
background_hover      // Hover states

// BORDERS
border_strong         // Selected, emphasized
border_default        // Standard borders
border_subtle         // Light separators

// ACCENTS
accent_primary        // Main brand color
accent_secondary      // Supporting accent
accent_interactive    // Links, clickable

// DASHBOARD
dashboard_metric              // Metric values
dashboard_metricLabel         // Metric labels
dashboard_sectionHeader       // Section titles
dashboard_tableHeader         // Table headers
dashboard_tableRow            // Alternating rows
dashboard_gradientStart       // Gradient start
dashboard_gradientEnd         // Gradient end

// STATUS (each has: bg, text, border)
status.success        // ✅ Success, positive
status.warning        // ⚠️ Warning, caution
status.error          // ❌ Error, negative
status.critical       // 🚨 Critical, urgent
status.info           // ℹ️ Info, neutral
status.normal         // ⚪ Normal, default
```

---

## Additional Resources

- **Template File:** `_TEMPLATE.js` - Complete theme template
- **Theme Guide:** `README.md` - Step-by-step creation guide
- **Example Themes:** `desert.js`, `graphite.js` - Production examples
- **Validator:** `../colorRoles.js` - Color validation logic

---

*Dashboard V3 Semantic Theme System - Version 3.0.0*
