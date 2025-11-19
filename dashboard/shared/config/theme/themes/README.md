# Dashboard V3 - Theme Creation Guide

Complete guide for creating custom themes using the semantic theme system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Theme Structure](#theme-structure)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [Color Roles Reference](#color-roles-reference)
5. [Registration Process](#registration-process)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Create a new theme in 5 minutes:**

1. **Copy the template:**
   ```bash
   cp _TEMPLATE.js mytheme.js
   ```

2. **Edit the theme name and colors** (lines 27-240 in `mytheme.js`)

3. **Register in `index.js`:**
   ```javascript
   import { mytheme } from './mytheme.js';

   export const themes = {
     desert: desertTheme,
     graphite: graphiteTheme,
     mytheme: mytheme,  // Add your theme here
   };
   ```

4. **Refresh the dashboard** - Your theme will appear in the theme switcher!

---

## Theme Structure

Every theme consists of **4 main parts:**

### 1. **Theme Name** (Required)
```javascript
createTheme('My Theme Name', { ... })
```
- Display name shown in the theme switcher UI
- Use title case (e.g., "Sunset Blaze", "Ocean Depths")

### 2. **Semantic Colors** (Required)
```javascript
{
  text_primary: '#000000',
  text_secondary: '#555555',
  // ... 21 more required colors
}
```
- **23 semantic colors** are REQUIRED
- Use hex format: `#RRGGBB`
- Named by PURPOSE not appearance (e.g., `text_primary` not `darkGray`)

### 3. **Status Colors** (Required)
```javascript
status: {
  success: { bg: '#F0FDF4', text: '#15803D', border: '#16A34A' },
  warning: { bg: '#FEFCE8', text: '#A16207', border: '#CA8A04' },
  error: { bg: '#FEF2F2', text: '#991B1B', border: '#DC2626' },
  critical: { bg: '#FEF2F2', text: '#991B1B', border: '#DC2626' },
  info: { bg: '#EFF6FF', text: '#1D4ED8', border: '#3B82F6' },
  normal: { bg: '#F9FAFB', text: '#374151', border: '#D1D5DB' }
}
```
- **6 status types**, each with 3 properties: `bg`, `text`, `border`

### 4. **Optional Enhancements**
```javascript
{
  typography: { fontFamily: '...', scale: 1.0 },
  animations: { duration: 'normal', easing: 'ease' },
  effects: { shadow: '...', shadowElevated: '...', borderRadius: '...' }
}
```
- Customize fonts, animations, and visual effects
- If omitted, sensible defaults are used

---

## Step-by-Step Tutorial

### Tutorial: Create a "Sunset Blaze" Theme

**Goal:** Create a warm orange/red sunset-inspired theme

#### Step 1: Copy the Template

```bash
cd DashboardV3/shared/config/theme/themes/
cp _TEMPLATE.js sunset.js
```

#### Step 2: Update the Theme Name

Open `sunset.js` and change line 27:

```javascript
export const sunsetTheme = createTheme(
  'Sunset Blaze',  // Change from 'My Theme Name'
```

Also update the export variable name from `myTheme` to `sunsetTheme`.

#### Step 3: Define Your Color Palette

Choose your sunset colors:

```javascript
// Sunset color palette
const SUNSET_COLORS = {
  // Warm oranges and reds
  deepOrange: '#C2410C',    // Dark orange for text
  burnedOrange: '#EA580C',  // Medium orange
  lightOrange: '#FB923C',   // Light orange
  coral: '#F97316',         // Coral accent
  peach: '#FED7AA',         // Light peach
  cream: '#FFF7ED',         // Cream background

  // Supporting colors
  deepRed: '#991B1B',       // Deep red
  softRed: '#FCA5A5',       // Soft red
  gray: '#78716C',          // Neutral gray
};
```

#### Step 4: Map Colors to Semantic Roles

Fill in the semantic color roles:

```javascript
{
  // TEXT HIERARCHY
  text_primary: '#C2410C',        // Deep orange for main text
  text_secondary: '#EA580C',      // Burned orange for secondary
  text_muted: '#78716C',          // Gray for muted text
  text_disabled: '#D6D3D1',       // Light gray for disabled

  // BACKGROUNDS
  background_primary: '#FFF7ED',   // Cream main background
  background_card: '#FFFFFF',      // White cards
  background_elevated: '#FFEDD5',  // Light peach for modals
  background_hover: '#FED7AA',     // Peach hover state

  // BORDERS
  border_strong: '#EA580C',        // Burned orange strong border
  border_default: '#FED7AA',       // Peach default border
  border_subtle: '#FFEDD5',        // Very light peach subtle

  // ACCENTS
  accent_primary: '#F97316',       // Coral primary accent
  accent_secondary: '#FB923C',     // Light orange secondary
  accent_interactive: '#C2410C',   // Deep orange for links

  // DASHBOARD
  dashboard_metric: '#C2410C',           // Deep orange metrics
  dashboard_metricLabel: '#78716C',      // Gray labels
  dashboard_sectionHeader: '#EA580C',    // Burned orange headers
  dashboard_tableHeader: '#C2410C',      // Deep orange table headers
  dashboard_tableRow: '#FFF7ED',         // Cream alternating rows
  dashboard_gradientStart: '#F97316',    // Coral gradient start
  dashboard_gradientEnd: '#FB923C',      // Light orange gradient end

  // STATUS COLORS (use defaults or customize)
  status: {
    success: {
      bg: '#F0FDF4',
      text: '#15803D',
      border: '#16A34A',
    },
    warning: {
      bg: '#FEFCE8',
      text: '#A16207',
      border: '#CA8A04',
    },
    error: {
      bg: '#FEF2F2',
      text: '#991B1B',
      border: '#DC2626',
    },
    critical: {
      bg: '#FEF2F2',
      text: '#991B1B',
      border: '#DC2626',
    },
    info: {
      bg: '#EFF6FF',
      text: '#1D4ED8',
      border: '#3B82F6',
    },
    normal: {
      bg: '#F9FAFB',
      text: '#374151',
      border: '#D1D5DB',
    }
  }
}
```

#### Step 5: Customize Optional Enhancements (Optional)

```javascript
{
  typography: {
    fontFamily: '"Playfair Display", "Georgia", serif',  // Elegant serif for sunset theme
    scale: 1.05  // Slightly larger text
  },

  animations: {
    duration: 'slow',      // Slower, more relaxed animations
    easing: 'ease-in-out'  // Smooth transitions
  },

  effects: {
    shadow: '0 2px 4px rgba(234, 88, 12, 0.1)',           // Orange-tinted shadow
    shadowElevated: '0 10px 20px rgba(234, 88, 12, 0.15)', // Stronger orange shadow
    borderRadius: '0.75rem'                                // Rounder corners
  }
}
```

#### Step 6: Register the Theme

Open `themes/index.js` and add your theme:

```javascript
// Import themes
import { desertTheme } from './desert.js';
import { graphiteTheme } from './graphite.js';
import { sunsetTheme } from './sunset.js';  // Add this line

// Theme registry
export const themes = {
  desert: desertTheme,
  graphite: graphiteTheme,
  sunset: sunsetTheme,  // Add this line
};

// Theme metadata (optional but recommended)
export const themeMetadata = {
  desert: {
    id: 'desert',
    name: 'Desert Oasis',
    description: 'Warm, luxurious Dubai-inspired theme',
    category: 'warm',
    preview: { primary: '#B89968', background: '#FAF6F0', text: '#3D3128' }
  },
  graphite: {
    id: 'graphite',
    name: 'Graphite Professional',
    description: 'Cool, modern professional theme',
    category: 'cool',
    preview: { primary: '#0EA5E9', background: '#F8FAFC', text: '#1E293B' }
  },
  sunset: {  // Add this block
    id: 'sunset',
    name: 'Sunset Blaze',
    description: 'Warm orange and red sunset-inspired theme',
    category: 'warm',
    preview: { primary: '#F97316', background: '#FFF7ED', text: '#C2410C' }
  }
};
```

#### Step 7: Test Your Theme

1. **Save all files**
2. **Refresh the dashboard** (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
3. **Click the theme switcher** - "Sunset Blaze" should appear
4. **Click your theme** - Dashboard should switch to sunset colors
5. **Test all sections** - Verify colors look good across all components

---

## Color Roles Reference

### Quick Reference Table

| Role | Purpose | Examples |
|------|---------|----------|
| `text_primary` | Main text | Headers, titles, important content |
| `text_secondary` | Supporting text | Descriptions, subtitles |
| `text_muted` | Tertiary text | Labels, timestamps, metadata |
| `text_disabled` | Inactive text | Disabled buttons, unavailable options |
| `background_primary` | Main background | Page background |
| `background_card` | Card background | Cards, panels, sections |
| `background_elevated` | Modal background | Modals, dropdowns, popovers |
| `background_hover` | Hover state | Interactive element hovers |
| `border_strong` | Strong borders | Selected cards, active tabs |
| `border_default` | Normal borders | Card edges, input borders |
| `border_subtle` | Light borders | Table lines, subtle dividers |
| `accent_primary` | Primary brand | Main buttons, brand highlights |
| `accent_secondary` | Secondary brand | Secondary buttons, alternates |
| `accent_interactive` | Interactive | Links, clickable text |
| `dashboard_metric` | Metric values | Numbers, KPIs, data values |
| `dashboard_metricLabel` | Metric labels | Labels for metrics |
| `dashboard_sectionHeader` | Section headers | Major section titles |
| `dashboard_tableHeader` | Table headers | Column headers |
| `dashboard_tableRow` | Table rows | Alternating row colors |
| `dashboard_gradientStart` | Gradient start | Header gradients left |
| `dashboard_gradientEnd` | Gradient end | Header gradients right |

For detailed descriptions of each role, see [COLOR_ROLES.md](./COLOR_ROLES.md)

---

## Registration Process

### How Theme Registration Works

1. **Theme File Structure:**
   ```
   themes/
   ├── index.js           ← Theme registry (register here)
   ├── desert.js          ← Desert theme
   ├── graphite.js        ← Graphite theme
   ├── yourtheme.js       ← Your new theme
   └── _TEMPLATE.js       ← Template (do not register)
   ```

2. **Import Your Theme:**
   ```javascript
   import { yourtheme } from './yourtheme.js';
   ```

3. **Add to Registry:**
   ```javascript
   export const themes = {
     desert: desertTheme,
     graphite: graphiteTheme,
     yourtheme: yourtheme,  // Theme ID: key used in code
   };
   ```

4. **Theme ID Conventions:**
   - Use lowercase
   - Use underscores for multi-word IDs (e.g., `sunset_blaze`)
   - Keep it short and descriptive
   - ID is used in code, name is used in UI

5. **Add Metadata (Optional):**
   ```javascript
   export const themeMetadata = {
     yourtheme: {
       id: 'yourtheme',
       name: 'Your Theme Display Name',
       description: 'Brief description of your theme',
       category: 'warm' | 'cool' | 'neutral' | 'dark',
       preview: {
         primary: '#FF0000',      // Preview color 1
         background: '#FFFFFF',   // Preview color 2
         text: '#000000'          // Preview color 3
       }
     }
   };
   ```

### Automatic Integration

Once registered, your theme:
- ✅ Appears in the theme switcher automatically
- ✅ Can be switched to via UI
- ✅ Generates CSS variables automatically
- ✅ Works with all components
- ✅ Persists across page refreshes (if persistence is enabled)

---

## Best Practices

### Color Selection

1. **Ensure Contrast:**
   - Text on backgrounds: WCAG AA minimum (4.5:1 for normal text, 3:1 for large)
   - Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

2. **Maintain Hierarchy:**
   - `text_primary` should be darkest/most prominent
   - `text_secondary` should be clearly distinguishable from primary
   - `text_muted` should be visibly lighter but still readable
   - `text_disabled` should clearly indicate non-interactive state

3. **Background Harmony:**
   - `background_card` should provide clear separation from `background_primary`
   - `background_elevated` should stand out from `background_card`
   - `background_hover` should be a subtle shift from `background_card`

4. **Accent Balance:**
   - `accent_primary` should be your main brand color
   - `accent_secondary` should complement (not clash with) primary
   - `accent_interactive` should be clearly distinguishable as clickable

### Status Colors

1. **Use Universal Conventions:**
   - ✅ **Green** for success/positive
   - ⚠️ **Yellow/Amber** for warning/caution
   - ❌ **Red** for error/negative
   - ℹ️ **Blue** for info/neutral

2. **Each Status Needs 3 Colors:**
   - `bg`: Light background (e.g., light green for success)
   - `text`: Dark text for contrast (e.g., dark green)
   - `border`: Medium border color (e.g., medium green)

3. **Maintain Accessibility:**
   - Text must contrast against background
   - Test status badges with actual content

### Typography & Effects

1. **Font Selection:**
   - Choose readable fonts for data-heavy dashboards
   - System fonts (`-apple-system`, `BlinkMacSystemFont`) are fast and reliable
   - Web fonts add personality but increase load time

2. **Animation Speed:**
   - `'fast'` (150ms): Quick interactions, dropdowns
   - `'normal'` (300ms): Default, works for most
   - `'slow'` (500ms): Dramatic effects, large transitions

3. **Shadows & Borders:**
   - Subtle shadows create depth without distraction
   - Border radius should match your theme's personality (sharp vs. soft)

### Testing Your Theme

**Test Checklist:**

- [ ] All text is readable against backgrounds
- [ ] Links are clearly distinguishable
- [ ] Hover states are visible
- [ ] Status badges are color-coded correctly
- [ ] Metrics and data are prominent
- [ ] Tables are readable with alternating rows
- [ ] Gradients transition smoothly
- [ ] Borders provide clear separation
- [ ] Theme works on different screen sizes
- [ ] Theme looks good with real data (not just test data)

### Theme Categories

Organize themes by category:

- **Warm:** Desert, Sunset, Autumn, Terracotta
- **Cool:** Graphite, Ocean, Sky, Winter
- **Neutral:** Monochrome, Grayscale, Minimal
- **Dark:** Midnight, Carbon, Shadow

---

## Troubleshooting

### Theme Not Appearing in Switcher

**Problem:** Created theme but it doesn't show in UI

**Solutions:**
1. Check `themes/index.js` - Is your theme imported and registered?
2. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for import errors
4. Verify theme file exports correctly: `export const mytheme = createTheme(...)`

### Colors Not Changing

**Problem:** Theme switches but colors stay the same

**Solutions:**
1. Ensure all 23 semantic colors are defined
2. Check browser console for validation warnings
3. Verify CSS variables are being generated (inspect `:root` in DevTools)
4. Clear browser cache and hard refresh

### Validation Warnings

**Problem:** Console shows "Theme 'X' is missing colors"

**Solutions:**
1. Check the validation message - it lists missing colors
2. Refer to `_TEMPLATE.js` for complete list of required colors
3. Add missing colors to your theme object
4. Validation will show coverage percentage (aim for 100%)

### Status Colors Not Working

**Problem:** Status badges are wrong colors or not displaying

**Solutions:**
1. Ensure status object has all 6 types: `success`, `warning`, `error`, `critical`, `info`, `normal`
2. Each type must have 3 properties: `bg`, `text`, `border`
3. Verify hex color format: `#RRGGBB`

### Theme Looks Different in Components

**Problem:** Some components don't use theme colors

**Solutions:**
1. Check if components use semantic methods:
   - ✅ `themeEngine.getSemanticTextColor('primary')`
   - ❌ `themeEngine.getColor('sandDarkest')` (legacy)
2. Some legacy components may not be fully migrated yet
3. Report issues on GitHub

### Import Errors

**Problem:** "Cannot find module" or import errors

**Solutions:**
1. Verify file path in import statement
2. Check file extension: `.js` required
3. Ensure export matches import:
   ```javascript
   // In sunset.js
   export const sunsetTheme = createTheme(...)

   // In index.js
   import { sunsetTheme } from './sunset.js';  // ✅ Correct
   import sunsetTheme from './sunset.js';      // ❌ Wrong (default import)
   ```

---

## Additional Resources

- **Template File:** `_TEMPLATE.js` - Complete theme template with inline documentation
- **Color Roles:** `COLOR_ROLES.md` - Comprehensive color role reference
- **Example Themes:** `desert.js`, `graphite.js` - Production-ready examples
- **Color Roles Validator:** `../colorRoles.js` - Validation logic

---

## Support

If you encounter issues or have questions:

1. Check this README
2. Review `_TEMPLATE.js` for examples
3. Compare with `desert.js` or `graphite.js`
4. Check browser console for validation messages
5. Open an issue on GitHub

---

**Happy Theming! 🎨**

*Dashboard V3 Semantic Theme System*
*Version 3.0.0*
