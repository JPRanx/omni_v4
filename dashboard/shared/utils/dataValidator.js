/**
 * DataValidator.js
 *
 * Centralized validation utility for dashboard data consistency.
 * Ensures all aggregated totals match their source data.
 *
 * Usage:
 *   import { DataValidator } from './shared/utils/dataValidator.js';
 *   const validator = new DataValidator();
 *   const report = validator.validateAll(weekData);
 *
 * @version 3.0
 */

export class DataValidator {
  constructor() {
    this.tolerance = 0.01; // Floating-point tolerance
  }

  /**
   * Check if two numbers are equal within tolerance
   *
   * @param {number} a - First number
   * @param {number} b - Second number
   * @returns {boolean} True if equal within tolerance
   */
  isEqual(a, b) {
    return Math.abs(a - b) <= this.tolerance;
  }

  /**
   * Validate weekly totals match restaurant sums
   *
   * @param {Object} weekData - Week data object
   * @returns {Object} Validation result
   */
  validateWeeklyTotals(weekData) {
    const restaurants = weekData.restaurants || [];
    const overview = weekData.overview || {};
    const errors = [];

    // Calculate expected totals from restaurants
    const expectedSales = restaurants.reduce((sum, r) => sum + (r.sales || 0), 0);
    const expectedLabor = restaurants.reduce((sum, r) => sum + (r.laborCost || r.payroll || 0), 0);
    const expectedCogs = restaurants.reduce((sum, r) => sum + (r.cogs || 0), 0);

    // Validate totalSales
    if (!this.isEqual(overview.totalSales || 0, expectedSales)) {
      errors.push({
        field: 'totalSales',
        overview: overview.totalSales || 0,
        calculated: expectedSales,
        diff: (overview.totalSales || 0) - expectedSales,
        restaurants: restaurants.map(r => ({ name: r.name, sales: r.sales || 0 }))
      });
    }

    // Validate totalLabor
    if (!this.isEqual(overview.totalLabor || 0, expectedLabor)) {
      errors.push({
        field: 'totalLabor',
        overview: overview.totalLabor || 0,
        calculated: expectedLabor,
        diff: (overview.totalLabor || 0) - expectedLabor,
        restaurants: restaurants.map(r => ({ name: r.name, labor: r.laborCost || r.payroll || 0 }))
      });
    }

    // Validate totalCogs
    if (!this.isEqual(overview.totalCogs || 0, expectedCogs)) {
      errors.push({
        field: 'totalCogs',
        overview: overview.totalCogs || 0,
        calculated: expectedCogs,
        diff: (overview.totalCogs || 0) - expectedCogs,
        restaurants: restaurants.map(r => ({ name: r.name, cogs: r.cogs || 0 }))
      });
    }

    return {
      valid: errors.length === 0,
      errors,
      checked: ['totalSales', 'totalLabor', 'totalCogs']
    };
  }

  /**
   * Validate overtime hours match employee totals
   *
   * @param {Object} weekData - Week data object
   * @returns {Object} Validation result
   */
  validateOvertimeHours(weekData) {
    const employees = weekData.autoClockout || [];
    const overview = weekData.overview || {};

    // Calculate total OT from all employees
    const calculatedOT = employees.reduce((sum, e) => sum + (e.overtime_hours || 0), 0);
    const overviewOT = overview.overtimeHours || 0;

    // Calculate OT by restaurant
    const byRestaurant = {};
    employees.forEach(emp => {
      const restaurant = emp.restaurant || 'Unknown';
      if (!byRestaurant[restaurant]) {
        byRestaurant[restaurant] = 0;
      }
      byRestaurant[restaurant] += (emp.overtime_hours || 0);
    });

    const isValid = this.isEqual(calculatedOT, overviewOT);

    return {
      valid: isValid,
      overview: overviewOT,
      calculated: calculatedOT,
      diff: calculatedOT - overviewOT,
      byRestaurant,
      employeeCount: employees.length,
      error: isValid ? null : {
        field: 'overtimeHours',
        overview: overviewOT,
        calculated: calculatedOT,
        diff: calculatedOT - overviewOT
      }
    };
  }

  /**
   * Validate restaurant daily breakdown sums
   *
   * @param {Object} restaurant - Restaurant object
   * @returns {Object} Validation result
   */
  validateRestaurantDaily(restaurant) {
    if (!restaurant.dailyBreakdown || restaurant.dailyBreakdown.length === 0) {
      return {
        valid: true,
        skipped: true,
        reason: 'No daily breakdown data'
      };
    }

    const expectedSales = restaurant.dailyBreakdown.reduce((sum, day) => sum + (day.sales || 0), 0);
    const expectedLabor = restaurant.dailyBreakdown.reduce((sum, day) => sum + (day.labor || 0), 0);
    const expectedCogs = restaurant.dailyBreakdown.reduce((sum, day) => sum + (day.cogs || 0), 0);

    const errors = [];

    if (!this.isEqual(restaurant.sales || 0, expectedSales)) {
      errors.push({
        field: 'sales',
        restaurant: restaurant.name,
        total: restaurant.sales || 0,
        calculated: expectedSales,
        diff: (restaurant.sales || 0) - expectedSales
      });
    }

    if (!this.isEqual(restaurant.laborCost || restaurant.payroll || 0, expectedLabor)) {
      errors.push({
        field: 'labor',
        restaurant: restaurant.name,
        total: restaurant.laborCost || restaurant.payroll || 0,
        calculated: expectedLabor,
        diff: (restaurant.laborCost || restaurant.payroll || 0) - expectedLabor
      });
    }

    if (!this.isEqual(restaurant.cogs || 0, expectedCogs)) {
      errors.push({
        field: 'cogs',
        restaurant: restaurant.name,
        total: restaurant.cogs || 0,
        calculated: expectedCogs,
        diff: (restaurant.cogs || 0) - expectedCogs
      });
    }

    return {
      valid: errors.length === 0,
      errors,
      restaurant: restaurant.name
    };
  }

  /**
   * Run all validations and return comprehensive report
   *
   * @param {Object} weekData - Complete week data
   * @returns {Object} Validation report
   */
  validateAll(weekData) {
    // Run all validation checks
    const weeklyTotals = this.validateWeeklyTotals(weekData);
    const overtime = this.validateOvertimeHours(weekData);

    // Validate each restaurant's daily breakdown
    const restaurantValidations = (weekData.restaurants || []).map(restaurant =>
      this.validateRestaurantDaily(restaurant)
    );

    // Collect all errors
    const allErrors = [
      ...weeklyTotals.errors,
      ...(overtime.error ? [overtime.error] : []),
      ...restaurantValidations.flatMap(rv => rv.errors || [])
    ];

    // Calculate totals
    const totalChecks = 4 + restaurantValidations.filter(rv => !rv.skipped).length * 3;
    const failed = allErrors.length;
    const passed = totalChecks - failed;

    return {
      valid: allErrors.length === 0,
      errors: allErrors,
      summary: {
        totalChecks,
        passed,
        failed,
        passRate: totalChecks > 0 ? (passed / totalChecks * 100).toFixed(1) : 100
      },
      details: {
        weeklyTotals,
        overtime,
        restaurants: restaurantValidations
      }
    };
  }

  /**
   * Format validation report for console display
   *
   * @param {Object} report - Validation report
   * @returns {string} Formatted report
   */
  formatReport(report) {
    if (report.valid) {
      return '✅ All data consistency checks passed!';
    }

    let output = '❌ Data Consistency Issues Found:\n\n';
    output += `Summary: ${report.summary.passed}/${report.summary.totalChecks} checks passed (${report.summary.passRate}%)\n\n`;

    report.errors.forEach((error, index) => {
      output += `${index + 1}. ${error.field}:\n`;
      output += `   Overview: ${error.overview}\n`;
      output += `   Calculated: ${error.calculated}\n`;
      output += `   Difference: ${error.diff.toFixed(2)}\n\n`;
    });

    return output;
  }

  /**
   * Log validation report to console with color coding
   *
   * @param {Object} report - Validation report
   */
  logReport(report) {
    if (report.valid) {
      console.log('%c✅ All data consistency checks passed!', 'color: #10B981; font-weight: bold;');
      console.log(`${report.summary.totalChecks} checks completed successfully.`);
      return;
    }

    console.group('%c⚠️ Data Consistency Warnings', 'color: #F59E0B; font-weight: bold; font-size: 14px;');
    console.log(`%c${report.summary.passed}/${report.summary.totalChecks} checks passed (${report.summary.passRate}%)`, 'font-weight: bold;');
    console.log('');

    report.errors.forEach((error, index) => {
      console.group(`%c${index + 1}. ${error.field}`, 'font-weight: bold;');
      console.log('Overview value:', error.overview);
      console.log('Calculated sum:', error.calculated);
      console.log('%cDifference:', 'font-weight: bold;', error.diff.toFixed(2));

      if (error.restaurants) {
        console.log('Breakdown by restaurant:', error.restaurants);
      }
      if (error.byRestaurant) {
        console.log('Breakdown by restaurant:', error.byRestaurant);
      }

      console.groupEnd();
    });

    console.groupEnd();
  }
}

// Export convenience function
export function validateWeekData(weekData) {
  const validator = new DataValidator();
  return validator.validateAll(weekData);
}
