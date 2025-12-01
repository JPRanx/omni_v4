/**
 * Dashboard V3 - iPad App Entry Point
 *
 * Initializes all engines and orchestrates components
 * NO hardcoded values - everything comes from engines
 */

// Import configuration and engines
import config from './shared/config/index.js';
import { initializeEngines } from './engines/index.js';

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
import { DataValidator } from './shared/utils/dataValidator.js';

// ============================================
// Data Loading Functions
// ============================================

/**
 * Load data from static v4Data.js file
 */
async function loadFromStatic() {
  console.log('[DataLoader] Loading from static v4Data.js...');
  const module = await import('./data/v4Data.js');
  console.log('[DataLoader] ✅ Static data loaded');
  return module.v4Data;
}

/**
 * Load data from Supabase database
 */
async function loadFromSupabase() {
  console.log('[DataLoader] Loading from Supabase...');

  try {
    // Initialize Supabase client
    const { createClient } = window.supabase;
    const supabaseUrl = 'https://cactkpgueegwkqprgdwe.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNhY3RrcGd1ZWVnd2txcHJnZHdlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4NzM5MTQsImV4cCI6MjA3ODQ0OTkxNH0.TzpPyMg7Bhey4Vos-Ev2OVFEo80hfIkSBBpXTIgHsvg';

    const supabase = createClient(supabaseUrl, supabaseKey);
    console.log('[DataLoader] Supabase client initialized');

    // Query all daily operations (261 rows expected)
    const { data: dailyOps, error: dailyError } = await supabase
      .from('daily_operations')
      .select('*')
      .order('business_date');

    if (dailyError) throw dailyError;

    // Query all shift operations (522 rows expected - 2 shifts per day)
    const { data: shiftOps, error: shiftError } = await supabase
      .from('shift_operations')
      .select('*')
      .order('business_date, shift_name');

    if (shiftError) throw shiftError;

    // Query all vendor payouts (detailed payout records)
    const { data: vendorPayouts, error: vendorError } = await supabase
      .from('vendor_payouts')
      .select('*')
      .order('business_date, shift_name, vendor_name');

    if (vendorError) {
      console.warn('[DataLoader] vendor_payouts query failed (table may not exist yet):', vendorError);
    }

    console.log(`[DataLoader] Fetched ${dailyOps.length} daily operations, ${shiftOps.length} shift operations, ${vendorPayouts?.length || 0} vendor payouts`);

    // Debug: Log sample data
    if (dailyOps.length > 0) {
      console.log('[DataLoader] Sample daily operation:', dailyOps[0]);
      console.log('[DataLoader] Daily ops columns:', Object.keys(dailyOps[0]));
    }
    if (shiftOps.length > 0) {
      console.log('[DataLoader] Sample shift operation:', shiftOps[0]);
      console.log('[DataLoader] Shift ops columns:', Object.keys(shiftOps[0]));
    }

    // Transform Supabase data to v4Data structure
    const transformedData = transformSupabaseToV4Data(dailyOps, shiftOps, vendorPayouts || []);

    console.log('[DataLoader] ✅ Supabase data loaded and transformed');
    return transformedData;

  } catch (error) {
    console.error('[DataLoader] ❌ Failed to load from Supabase:', error);
    console.log('[DataLoader] Falling back to static data...');
    return loadFromStatic();
  }
}

/**
 * Transform Supabase query results to match v4Data.js structure
 *
 * DTO MAPPING REFERENCE (3-Way Consistency):
 * ================================================
 *
 * RESTAURANT AGGREGATES (Top-level):
 *   Supabase DB         →  v4Data.js       →  Dashboard Display
 *   -----------            -----------         ------------------
 *   total_sales         →  sales           →  Sales
 *   labor_cost          →  laborCost       →  Labor Cost
 *   food_cost           →  cogs            →  COGS
 *   labor_status (last) →  status          →  Status (excellent/good/warning/critical)
 *   labor_grade (last)  →  grade           →  Grade (A/B/C/D/F)
 *
 * DAILY BREAKDOWN:
 *   Supabase DB         →  v4Data.js       →  Dashboard Display
 *   -----------            -----------         ------------------
 *   business_date       →  date            →  Date
 *   restaurant_code     →  restaurant      →  Restaurant
 *   total_sales         →  sales           →  Sales
 *   labor_cost          →  labor           →  Labor (Note: different from aggregate!)
 *   labor_percent       →  laborPercent    →  Labor %
 *   food_cost           →  cogs            →  COGS
 *   cash_collected      →  cashCollected   →  Cash Collected
 *   tips_distributed    →  tipsDistributed →  Tips Distributed
 *   vendor_payouts_total→  vendorPayouts   →  Vendor Payouts
 *   net_cash            →  netCash         →  Net Cash
 *
 * SHIFT BREAKDOWN:
 *   Supabase DB         →  v4Data.js       →  Dashboard Display
 *   -----------            -----------         ------------------
 *   shift_name          →  [key] (lowercase) → Shift Name
 *   sales               →  sales           →  Sales
 *   labor_cost          →  labor           →  Labor
 *   order_count         →  orderCount      →  Order Count
 *   manager             →  manager         →  Manager (from time entries)
 *   voids               →  voids           →  Voids (currently 0, not extracted)
 *   cash_collected      →  cashCollected   →  Cash Collected
 *   tips_distributed    →  tipsDistributed →  Tips Distributed
 *   vendor_payouts      →  vendorPayouts   →  Vendor Payouts
 *   net_cash            →  netCash         →  Net Cash
 *   category_stats      →  category_stats  →  Category Stats
 *   CALCULATED          →  avgOrderValue   →  Avg Order Value (sales / orderCount)
 *
 * NOTE: After migration 002, manager and voids are now stored in Supabase.
 *       Manager is extracted from time entries. Voids will be 0 until extraction is implemented.
 */
function transformSupabaseToV4Data(dailyOps, shiftOps, vendorPayouts = []) {
  console.log('[Transform] Starting transformation...');

  // Group daily operations by week
  const weekMap = new Map();

  dailyOps.forEach(day => {
    const date = new Date(day.business_date);
    const weekKey = getWeekKey(date);

    if (!weekMap.has(weekKey)) {
      weekMap.set(weekKey, {
        startDate: null,
        endDate: null,
        dailyOps: [],
        shiftOps: [],
        vendorPayouts: []
      });
    }

    const week = weekMap.get(weekKey);
    week.dailyOps.push(day);

    // Update week date range
    if (!week.startDate || date < new Date(week.startDate)) {
      week.startDate = day.business_date;
    }
    if (!week.endDate || date > new Date(week.endDate)) {
      week.endDate = day.business_date;
    }
  });

  // Add shift operations to their respective weeks
  shiftOps.forEach(shift => {
    const date = new Date(shift.business_date);
    const weekKey = getWeekKey(date);

    if (weekMap.has(weekKey)) {
      weekMap.get(weekKey).shiftOps.push(shift);
    }
  });

  // Add vendor payouts to their respective weeks
  vendorPayouts.forEach(payout => {
    const date = new Date(payout.business_date);
    const weekKey = getWeekKey(date);

    if (weekMap.has(weekKey)) {
      weekMap.get(weekKey).vendorPayouts.push(payout);
    }
  });

  // Build v4Data structure
  const v4Data = {};
  let weekNumber = 1;

  // Sort weeks by start date
  const sortedWeeks = Array.from(weekMap.entries())
    .sort((a, b) => new Date(a[1].startDate) - new Date(b[1].startDate));

  sortedWeeks.forEach(([weekKey, weekData]) => {
    v4Data[`week${weekNumber}`] = buildWeekData(weekData, weekNumber);
    weekNumber++;
  });

  console.log(`[Transform] ✅ Transformed into ${Object.keys(v4Data).length} weeks`);

  // Debug: Log sample week structure
  const firstWeek = v4Data[Object.keys(v4Data)[0]];
  if (firstWeek && firstWeek.restaurants && firstWeek.restaurants.length > 0) {
    const sampleRestaurant = firstWeek.restaurants[0];
    console.log('[Transform] Sample restaurant structure:', {
      name: sampleRestaurant.name,
      sales: sampleRestaurant.sales,
      laborCost: sampleRestaurant.laborCost,
      dailyBreakdownCount: sampleRestaurant.dailyBreakdown?.length || 0
    });

    if (sampleRestaurant.dailyBreakdown && sampleRestaurant.dailyBreakdown.length > 0) {
      const sampleDay = sampleRestaurant.dailyBreakdown[0];
      console.log('[Transform] Sample daily breakdown:', {
        date: sampleDay.date,
        restaurant: sampleDay.restaurant,
        sales: sampleDay.sales,
        labor: sampleDay.labor,
        shifts: Object.keys(sampleDay.shifts || {})
      });

      const shiftKeys = Object.keys(sampleDay.shifts || {});
      if (shiftKeys.length > 0) {
        console.log('[Transform] Sample shift:', sampleDay.shifts[shiftKeys[0]]);
      }
    }
  }

  return v4Data;
}

/**
 * Get week key (Monday-Sunday) for a date
 */
function getWeekKey(date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust to Monday
  const monday = new Date(d.setDate(diff));
  return monday.toISOString().split('T')[0];
}

/**
 * Build week data structure from daily/shift operations
 */
function buildWeekData(weekData, weekNumber) {
  const { dailyOps, shiftOps, vendorPayouts = [] } = weekData;

  // Debug: Check what restaurant codes we have in the data
  const uniqueCodes = [...new Set(dailyOps.map(d => d.restaurant_code))];
  console.log(`[BuildWeek] Week ${weekNumber}: Found restaurant codes:`, uniqueCodes);
  console.log(`[BuildWeek] Week ${weekNumber}: ${dailyOps.length} daily ops, ${shiftOps.length} shift ops`);

  // Group by restaurant
  const restaurantMap = new Map();
  const restaurants = ['SDR', 'T12', 'TK9'];

  restaurants.forEach(code => {
    const restaurantDays = dailyOps.filter(d => d.restaurant_code === code);
    const restaurantShifts = shiftOps.filter(s => s.restaurant_code === code);

    console.log(`[BuildWeek] Restaurant ${code}: ${restaurantDays.length} days, ${restaurantShifts.length} shifts`);

    if (restaurantDays.length > 0) {
      restaurantMap.set(code, {
        name: getRestaurantName(code),
        code: code,
        dailyOps: restaurantDays,
        shiftOps: restaurantShifts
      });
    }
  });

  // Build restaurants array with daily breakdown
  const restaurantsArray = Array.from(restaurantMap.values()).map(restaurant => {
    const dailyBreakdown = restaurant.dailyOps.map(day => {
      // Get shifts for this day
      const dayShifts = restaurant.shiftOps.filter(s => s.business_date === day.business_date);

      // Build shifts object (not array) with lowercase keys
      const shifts = {};
      dayShifts.forEach(shift => {
        // Shift key: Supabase: shift_name → v4Data: lowercase key (e.g., "morning", "evening")
        const shiftKey = (shift.shift_name || shift.shift_type || 'unknown').toLowerCase();

        // Map Supabase columns to v4Data structure (Shift Breakdown)
        const shiftSales = shift.sales || 0;              // Supabase: sales → v4Data: sales
        const shiftLabor = shift.labor_cost || 0;         // Supabase: labor_cost → v4Data: labor

        // Calculate average order value from sales and order count
        const orderCount = shift.order_count || 0;
        const avgOrderValue = orderCount > 0 ? shiftSales / orderCount : 0;

        shifts[shiftKey] = {
          sales: shiftSales,
          labor: shiftLabor,
          laborPercent: shiftSales > 0 ? (shiftLabor / shiftSales) * 100 : 0,  // Calculated
          manager: shift.manager || "Not Assigned",       // Supabase: manager → v4Data: manager (from time entries)
          voids: shift.voids || 0,                        // Supabase: voids → v4Data: voids (currently 0)
          orderCount: orderCount,                         // Supabase: order_count → v4Data: orderCount
          avgOrderValue: avgOrderValue,                   // Calculated from sales / order_count
          cashCollected: shift.cash_collected || 0,       // Supabase: cash_collected → v4Data: cashCollected
          tipsDistributed: shift.tips_distributed || 0,   // Supabase: tips_distributed → v4Data: tipsDistributed
          vendorPayouts: shift.vendor_payouts || 0,       // Supabase: vendor_payouts → v4Data: vendorPayouts
          netCash: shift.net_cash || 0,                   // Supabase: net_cash → v4Data: netCash
          category_stats: shift.category_stats || {}      // Supabase: category_stats → v4Data: category_stats
        };
      });

      // Map Supabase columns to v4Data structure (Daily Breakdown)
      const sales = day.total_sales || 0;           // Supabase: total_sales → v4Data: sales
      const labor = day.labor_cost || 0;            // Supabase: labor_cost → v4Data: labor
      const cogs = day.food_cost || 0;              // Supabase: food_cost → v4Data: cogs

      return {
        date: day.business_date,                    // Supabase: business_date → v4Data: date
        restaurant: day.restaurant_code,            // Supabase: restaurant_code → v4Data: restaurant
        sales: sales,
        labor: labor,                               // NOTE: "labor" in daily, "laborCost" in aggregate
        laborPercent: day.labor_percent || 0,       // Supabase: labor_percent → v4Data: laborPercent
        cogs: cogs,
        cogsPercent: sales > 0 ? (cogs / sales) * 100 : 0,
        profit: sales - labor - cogs,               // Calculated field
        profitMargin: sales > 0 ? ((sales - labor - cogs) / sales) * 100 : 0,  // Calculated field
        cashCollected: day.cash_collected || 0,     // Supabase: cash_collected → v4Data: cashCollected
        tipsDistributed: day.tips_distributed || 0, // Supabase: tips_distributed → v4Data: tipsDistributed
        vendorPayouts: day.vendor_payouts_total || 0, // Supabase: vendor_payouts_total → v4Data: vendorPayouts
        netCash: day.net_cash || 0,                 // Supabase: net_cash → v4Data: netCash
        shifts: shifts                              // Object with lowercase shift names as keys
      };
    });

    // Calculate restaurant totals (aggregate from daily operations)
    const totalSales = restaurant.dailyOps.reduce((sum, d) => sum + (d.total_sales || 0), 0);
    const totalLaborCost = restaurant.dailyOps.reduce((sum, d) => sum + (d.labor_cost || 0), 0);
    const totalCogs = restaurant.dailyOps.reduce((sum, d) => sum + (d.food_cost || 0), 0);

    // Get most recent day's status and grade for the restaurant
    const mostRecentDay = restaurant.dailyOps[restaurant.dailyOps.length - 1];
    const status = mostRecentDay?.labor_status || 'good';     // Supabase: labor_status → v4Data: status
    const grade = mostRecentDay?.labor_grade || 'B';          // Supabase: labor_grade → v4Data: grade

    return {
      id: `rest-${restaurant.code.toLowerCase()}`,
      name: restaurant.name,
      code: restaurant.code,
      sales: totalSales,                // Supabase: total_sales → v4Data: sales
      laborCost: totalLaborCost,        // Supabase: labor_cost → v4Data: laborCost
      laborPercent: totalSales > 0 ? (totalLaborCost / totalSales) * 100 : 0,
      cogs: totalCogs,                  // Supabase: food_cost → v4Data: cogs
      cogsPercent: totalSales > 0 ? (totalCogs / totalSales) * 100 : 0,
      netProfit: totalSales - totalLaborCost - totalCogs,
      profitMargin: totalSales > 0 ? ((totalSales - totalLaborCost - totalCogs) / totalSales) * 100 : 0,
      status: status,                   // From most recent day's labor_status
      grade: grade,                     // From most recent day's labor_grade
      dailyBreakdown
    };
  });

  // Calculate overview totals
  const totalSales = dailyOps.reduce((sum, d) => sum + (d.total_sales || 0), 0);
  const totalLaborCost = dailyOps.reduce((sum, d) => sum + (d.labor_cost || 0), 0);
  const totalCash = dailyOps.reduce((sum, d) => sum + (d.cash_collected || 0), 0);
  const totalTips = dailyOps.reduce((sum, d) => sum + (d.tips_distributed || 0), 0);
  const totalVendorPayouts = dailyOps.reduce((sum, d) => sum + (d.vendor_payouts_total || 0), 0);
  const totalNetCash = dailyOps.reduce((sum, d) => sum + (d.net_cash || 0), 0);
  const totalOvertimeHours = dailyOps.reduce((sum, d) => sum + (d.overtime_hours || 0), 0);

  // Build cashFlow structure with per-restaurant breakdown (for RestaurantCards)
  const cashFlowRestaurants = {};
  restaurantsArray.forEach(restaurant => {
    // Get restaurant's daily ops
    const restDailyOps = dailyOps.filter(d => d.restaurant_code === restaurant.code);
    const restCash = restDailyOps.reduce((sum, d) => sum + (d.cash_collected || 0), 0);
    const restTips = restDailyOps.reduce((sum, d) => sum + (d.tips_distributed || 0), 0);
    const restPayouts = restDailyOps.reduce((sum, d) => sum + (d.vendor_payouts_total || 0), 0);
    const restNetCash = restDailyOps.reduce((sum, d) => sum + (d.net_cash || 0), 0);

    // Get shift data for this restaurant
    const restShiftOps = shiftOps.filter(s => s.restaurant_code === restaurant.code);
    const morningShifts = restShiftOps.filter(s => s.shift_name === 'Morning');
    const eveningShifts = restShiftOps.filter(s => s.shift_name === 'Evening');

    // Get vendor payouts for this restaurant (detailed records)
    const restVendorPayouts = vendorPayouts
      .filter(p => p.restaurant_code === restaurant.code)
      .map(p => ({
        vendor_name: p.vendor_name,
        amount: p.amount,
        reason: p.reason,
        comments: p.comments,
        time: p.payout_time,
        manager: p.manager,
        drawer: p.drawer,
        shift: p.shift_name,
        date: p.business_date
      }));

    cashFlowRestaurants[restaurant.code] = {
      total_cash: restCash,
      total_tips: restTips,
      total_vendor_payouts: restPayouts,
      net_cash: restNetCash,
      vendor_payouts: restVendorPayouts,  // Array of detailed payout records
      shifts: {
        Morning: {
          cash: morningShifts.reduce((sum, s) => sum + (s.cash_collected || 0), 0),
          tips: morningShifts.reduce((sum, s) => sum + (s.tips_distributed || 0), 0),
          payouts: morningShifts.reduce((sum, s) => sum + (s.vendor_payouts || 0), 0),
          net: morningShifts.reduce((sum, s) => sum + (s.net_cash || 0), 0),
          drawers: []
        },
        Evening: {
          cash: eveningShifts.reduce((sum, s) => sum + (s.cash_collected || 0), 0),
          tips: eveningShifts.reduce((sum, s) => sum + (s.tips_distributed || 0), 0),
          payouts: eveningShifts.reduce((sum, s) => sum + (s.vendor_payouts || 0), 0),
          net: eveningShifts.reduce((sum, s) => sum + (s.net_cash || 0), 0),
          drawers: []
        }
      }
    };
  });

  // Attach cashFlow to each restaurant object (for Investigation Modal)
  restaurantsArray.forEach(restaurant => {
    restaurant.cashFlow = cashFlowRestaurants[restaurant.code] || {};
  });

  // Build all vendor payouts for the week (for Investigation Modal)
  const allVendorPayouts = vendorPayouts.map(p => ({
    vendor_name: p.vendor_name,
    amount: p.amount,
    reason: p.reason,
    comments: p.comments,
    time: p.payout_time,
    manager: p.manager,
    drawer: p.drawer,
    shift: p.shift_name,
    date: p.business_date,
    restaurant_code: p.restaurant_code
  }));

  const cashFlow = {
    total_cash: totalCash,
    total_tips: totalTips,
    total_vendor_payouts: totalVendorPayouts,
    net_cash: totalNetCash,
    vendor_payouts: allVendorPayouts,  // Array of all detailed payout records
    restaurants: cashFlowRestaurants
  };

  return {
    weekNumber,
    dateRange: {
      start: weekData.startDate,
      end: weekData.endDate
    },
    overview: {
      totalSales,
      totalLaborCost,
      totalLabor: totalLaborCost,             // Alias for data validator compatibility
      avgLaborPercent: totalSales > 0 ? (totalLaborCost / totalSales) * 100 : 0,
      overtimeHours: totalOvertimeHours,      // For OverviewCard
      totalCash,                              // For OverviewCard (camelCase)
      total_cash: totalCash,                  // For CashFlowModal (snake_case)
      total_tips: totalTips,                  // For CashFlowModal
      total_vendor_payouts: totalVendorPayouts, // For CashFlowModal
      net_cash: totalNetCash,                 // For CashFlowModal
      cashFlow                                // For RestaurantCards and CashFlowModal
    },
    metrics: {},
    restaurants: restaurantsArray,
    autoClockoutAlerts: []
  };
}

/**
 * Get restaurant full name from code
 */
function getRestaurantName(code) {
  const names = {
    'SDR': "Sandra's Mexican Cuisine",
    'T12': 'Tink-A-Tako #12',
    'TK9': 'Tink-A-Tako #9'
  };
  return names[code] || code;
}

/**
 * Load data based on localStorage preference
 */
async function loadData() {
  const dataSource = localStorage.getItem('dataSource') || 'static';
  console.log(`[DataLoader] Data source preference: ${dataSource}`);

  if (dataSource === 'supabase') {
    return await loadFromSupabase();
  } else {
    return await loadFromStatic();
  }
}

/**
 * Main App Class
 */
class DashboardApp {
  constructor() {
    this.engines = null;
    this.currentWeek = null; // Will be set to most recent week
    this.data = null; // Will be loaded based on user preference
    this.components = {};
    this.validationReport = null;
    this.dataSource = localStorage.getItem('dataSource') || 'static';

    console.log(`[App] Dashboard initializing with ${this.dataSource} data source`);
  }

  /**
   * Initialize the application - ASYNC VERSION WITH DATA LOADING
   */
  async initialize() {
    try {
      console.log('[App] Initializing Dashboard V3...');

      // Step 0: Load data first
      this.data = await loadData();
      console.log('[App] ✅ Data loaded');

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

      // Step 5: Data is already loaded
      console.log(`[App] ✅ Data ready from ${this.dataSource} source`);

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
    this.renderDataSourceToggle();

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
   * Render data source toggle button
   */
  renderDataSourceToggle() {
    const container = document.getElementById('data-source-toggle');
    if (!container) {
      console.warn('[App] No data-source-toggle container found');
      return;
    }

    const currentSource = this.dataSource;
    const displayText = currentSource === 'static' ? 'Static (v4Data)' : 'Live (Supabase)';
    const statusColor = currentSource === 'static' ? '#B89968' : '#10B981';

    container.innerHTML = `
      <button
        id="toggle-data-source-btn"
        style="
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: white;
          border: 2px solid ${statusColor};
          border-radius: 8px;
          font-family: var(--font-primary);
          font-size: 14px;
          font-weight: 600;
          color: ${statusColor};
          cursor: pointer;
          transition: all 0.2s ease;
        "
        onmouseover="this.style.background='${statusColor}'; this.style.color='white';"
        onmouseout="this.style.background='white'; this.style.color='${statusColor}';"
      >
        <span style="font-size: 16px;">📊</span>
        <span>Data: ${displayText}</span>
      </button>
    `;

    // Add click handler
    const button = document.getElementById('toggle-data-source-btn');
    button.addEventListener('click', () => this.toggleDataSource());
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
   * Toggle data source between static and Supabase
   */
  toggleDataSource() {
    const currentSource = localStorage.getItem('dataSource') || 'static';
    const newSource = currentSource === 'static' ? 'supabase' : 'static';

    console.log(`[App] Toggling data source from ${currentSource} to ${newSource}`);

    // Save preference
    localStorage.setItem('dataSource', newSource);

    // Reload page to load new data source
    window.location.reload();
  }

  /**
   * Get current data source
   */
  getDataSource() {
    return this.dataSource;
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
