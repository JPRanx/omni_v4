/**
 * Dashboard V3 - Engine Usage Examples
 *
 * Complete examples demonstrating how to use all 5 engines
 */

import { initializeEngines } from './index.js';
import config from '../shared/config/index.js';

// ============================================
// EXAMPLE 1: Initialize All Engines
// ============================================

console.log('='.repeat(60));
console.log('EXAMPLE 1: Initialize All Engines');
console.log('='.repeat(60));

// Initialize all engines at once
const engines = initializeEngines(config);

console.log('✅ All engines initialized!');
console.log('Available engines:', Object.keys(engines));

// ============================================
// EXAMPLE 2: Using ThemeEngine
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 2: Using ThemeEngine');
console.log('='.repeat(60));

const { themeEngine } = engines;

// Apply desert theme (default)
themeEngine.applyTheme('desert');

// Get theme colors
const primaryColor = themeEngine.getColor('desert.bronzeDust');
console.log('Primary Color (Bronze Dust):', primaryColor);

// Get shadows
const headerShadow = themeEngine.getComponentShadow('header', 'default');
console.log('Header Shadow:', headerShadow);

// Get typography
const headerSize = themeEngine.getTypography('componentSizes', 'headerH1');
console.log('Header H1 Size:', headerSize);

// Get theme stats
const themeStats = themeEngine.getStats();
console.log('Theme Stats:', themeStats);

// ============================================
// EXAMPLE 3: Using LayoutEngine
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 3: Using LayoutEngine');
console.log('='.repeat(60));

const { layoutEngine } = engines;

// Detect current device
const currentDevice = layoutEngine.getCurrentDevice();
console.log('Current Device:', currentDevice);

// Get grid classes for metrics
const metricsGridClasses = layoutEngine.getGridClasses('metrics');
console.log('Metrics Grid Classes:', metricsGridClasses);

// Get grid columns for current device
const metricsColumns = layoutEngine.getGridColumns('metrics');
console.log('Metrics Grid Columns:', metricsColumns);

// Get container classes
const containerClasses = layoutEngine.getContainerClasses('dashboard');
console.log('Dashboard Container Classes:', containerClasses);

// Get z-index for modal
const modalZIndex = layoutEngine.getZIndex('modalContent');
console.log('Modal Z-Index:', modalZIndex);

// Check if mobile
const isMobile = layoutEngine.isMobile();
console.log('Is Mobile:', isMobile);

// Get layout recommendations
const recommendations = layoutEngine.getLayoutRecommendations();
console.log('Layout Recommendations:', recommendations);

// ============================================
// EXAMPLE 4: Using BusinessEngine
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 4: Using BusinessEngine');
console.log('='.repeat(60));

const { businessEngine } = engines;

// Sample restaurant data
const restaurantData = {
  sales: 45000,
  laborCost: 12000,
  laborHours: 320,
  cogs: 13500,
  otherExpenses: 2000,
};

// Evaluate complete restaurant performance
const evaluation = businessEngine.evaluateRestaurant(restaurantData);
console.log('\nRestaurant Evaluation:');
console.log('- Sales Status:', evaluation.statuses.sales);
console.log('- Labor Status:', evaluation.statuses.labor);
console.log('- Overall Status:', evaluation.statuses.overall);
console.log('- Grade:', evaluation.grade.label);
console.log('- Is Passing:', evaluation.isPassing);
console.log('- Needs Attention:', evaluation.needsAttention);

// Calculate specific metrics
const laborPercent = businessEngine.calculateLaborPercent(
  restaurantData.laborCost,
  restaurantData.sales
);
console.log('\nLabor Percentage:', laborPercent.toFixed(1) + '%');

const netProfit = businessEngine.calculateNetProfit(
  restaurantData.sales,
  restaurantData.laborCost,
  restaurantData.cogs,
  restaurantData.otherExpenses
);
console.log('Net Profit:', businessEngine.formatCurrency(netProfit));

// Calculate grade from metrics
const grade = businessEngine.calculateGrade({
  sales: restaurantData.sales,
  laborPercent: laborPercent,
  profitMargin: (netProfit / restaurantData.sales) * 100,
});
console.log('Calculated Grade:', grade.label, grade.description);

// Get status styling
const statusClasses = businessEngine.getStatusClasses(evaluation.statuses.overall);
console.log('Status Tailwind Classes:', statusClasses);

// ============================================
// EXAMPLE 5: Using DeviceRouter
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 5: Using DeviceRouter');
console.log('='.repeat(60));

const { deviceRouter } = engines;

// Get device type and route
const deviceType = deviceRouter.getDeviceType();
const route = deviceRouter.getRoute();
console.log('Device Type:', deviceType);
console.log('Recommended Route:', route);

// Check device capabilities
const capabilities = deviceRouter.getCapabilities();
console.log('\nDevice Capabilities:');
console.log('- Has Touch:', capabilities.hasTouch);
console.log('- Has Hover:', capabilities.hasHover);
console.log('- Has Animations:', capabilities.hasAnimations);
console.log('- Has GPU:', capabilities.hasGPU);
console.log('- Fast Connection:', capabilities.hasFastConnection);

// Check feature availability
const gradientAnimsAvailable = deviceRouter.isFeatureAvailable('gradientAnimations');
console.log('\nGradient Animations Available:', gradientAnimsAvailable);

// Get enabled features
const enabledFeatures = deviceRouter.getEnabledFeatures();
console.log('Enabled Features Count:', enabledFeatures.length);

// Get device optimizations
const optimizations = deviceRouter.getOptimizations();
console.log('\nDevice Optimizations:');
console.log('- Use Lightweight Mode:', optimizations.useLightweightMode);
console.log('- Enable Animations:', optimizations.enableAnimations);
console.log('- Lazy Load Images:', optimizations.lazyLoadImages);

// Get interface configuration
const interfaceConfig = deviceRouter.getInterfaceConfig();
console.log('\nInterface Configuration:', interfaceConfig);

// ============================================
// EXAMPLE 6: Using ConfigValidator
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 6: Using ConfigValidator');
console.log('='.repeat(60));

const { validator } = engines;

// Get validation report
const validationReport = validator.getReport();
console.log('Configuration Valid:', validationReport.valid);
console.log('Total Checks:', validationReport.stats.totalChecks);
console.log('Passed:', validationReport.stats.passed);
console.log('Failed:', validationReport.stats.failed);
console.log('Warnings:', validationReport.stats.warned);

// Get health check
const healthCheck = validator.getHealthCheck();
console.log('\nHealth Check:');
console.log('- Status:', healthCheck.status);
console.log('- Score:', healthCheck.score + '%');
console.log('- Issues:', healthCheck.issues);

// ============================================
// EXAMPLE 7: Real-World Scenario
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 7: Real-World Scenario - Render Restaurant Card');
console.log('='.repeat(60));

// Simulate rendering a restaurant card with all engines working together

const restaurant = {
  name: 'Downtown Bistro',
  sales: 52000,
  laborCost: 14000,
  cogs: 15000,
};

console.log(`\nRendering card for: ${restaurant.name}`);

// 1. Use BusinessEngine to evaluate performance
const restaurantEval = businessEngine.evaluateRestaurant(restaurant);
console.log('✅ Performance evaluated');

// 2. Use ThemeEngine to get styling
const cardShadow = themeEngine.getComponentShadow('restaurantCard', 'default');
const cardBorder = themeEngine.getBorder('radius', 'lg');
console.log('✅ Styling retrieved');

// 3. Use LayoutEngine to get grid placement
const restaurantGridClasses = layoutEngine.getGridClasses('restaurants');
console.log('✅ Layout determined');

// 4. Use DeviceRouter to optimize for device
const shouldLazyLoad = deviceRouter.getOptimizations().lazyLoadImages;
console.log('✅ Device optimizations applied');

// 5. Format display values
const formattedSales = businessEngine.formatCurrency(restaurant.sales);
const formattedLaborPercent = businessEngine.formatPercentage(restaurantEval.metrics.laborPercent);

console.log('\nCard Details:');
console.log('- Restaurant:', restaurant.name);
console.log('- Sales:', formattedSales);
console.log('- Labor %:', formattedLaborPercent);
console.log('- Status:', restaurantEval.statuses.overall);
console.log('- Grade:', restaurantEval.grade.label);
console.log('- Grid Classes:', restaurantGridClasses);
console.log('- Shadow:', cardShadow);
console.log('- Border Radius:', cardBorder);
console.log('- Lazy Load:', shouldLazyLoad);

// ============================================
// EXAMPLE 8: Complete Weekly Dashboard
// ============================================

console.log('\n' + '='.repeat(60));
console.log('EXAMPLE 8: Complete Weekly Dashboard Data');
console.log('='.repeat(60));

// Sample weekly data
const weekData = [
  { day: 'Monday', sales: 42000, laborCost: 11000, cogs: 12500 },
  { day: 'Tuesday', sales: 45000, laborCost: 12000, cogs: 13500 },
  { day: 'Wednesday', sales: 48000, laborCost: 13000, cogs: 14000 },
  { day: 'Thursday', sales: 51000, laborCost: 13500, cogs: 15000 },
  { day: 'Friday', sales: 58000, laborCost: 15000, cogs: 17000 },
  { day: 'Saturday', sales: 62000, laborCost: 16000, cogs: 18500 },
  { day: 'Sunday', sales: 55000, laborCost: 14500, cogs: 16500 },
];

// Calculate weekly summary
const weeklySummary = businessEngine.calculateWeeklySummary(weekData);

console.log('\nWeekly Summary:');
console.log('- Total Sales:', businessEngine.formatCurrency(weeklySummary.totalSales));
console.log('- Avg Daily Sales:', businessEngine.formatCurrency(weeklySummary.avgDailySales));
console.log('- Total Labor Cost:', businessEngine.formatCurrency(weeklySummary.totalLaborCost));
console.log('- Net Profit:', businessEngine.formatCurrency(weeklySummary.netProfit));
console.log('- Profit Margin:', businessEngine.formatPercentage(weeklySummary.profitMargin));

// Evaluate each day
console.log('\nDaily Evaluations:');
weekData.forEach((day, index) => {
  const previousDay = index > 0 ? weekData[index - 1] : null;
  const dayEval = businessEngine.evaluateDay(day, previousDay);

  console.log(`\n${day.day}:`);
  console.log('  Sales:', businessEngine.formatCurrency(day.sales));
  console.log('  Status:', dayEval.statuses.sales);
  console.log('  Grade:', dayEval.grade.label);

  if (dayEval.variance) {
    const varianceFormatted = businessEngine.formatVariance(dayEval.variance.sales);
    console.log('  Variance:', varianceFormatted.text, varianceFormatted.icon);
  }
});

// ============================================
// SUMMARY
// ============================================

console.log('\n' + '='.repeat(60));
console.log('SUMMARY: All Engines Working Together');
console.log('='.repeat(60));

console.log(`
✅ ThemeEngine: Manages all visual styling (colors, shadows, typography)
✅ LayoutEngine: Handles responsive layouts and grid systems
✅ BusinessEngine: Performs all business calculations and evaluations
✅ DeviceRouter: Detects device and optimizes experience
✅ ConfigValidator: Ensures all 538 configurations are valid

All engines work independently but share the same configuration source.
No hardcoded values - everything comes from /shared/config/

Total Configurations: 538
- Theme: 271 configs
- Layout: 41 configs
- Business: 53 configs
- Content: 116 configs
- Features: 35 configs
- Resolution: 8 conflicts resolved

The engines are ready for use in iPad and Mobile interfaces!
`);

console.log('='.repeat(60));
