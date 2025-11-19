/**
 * Data Parity Test - Automated comparison of both data sources
 * This will identify the exact point where data diverges
 *
 * Usage:
 * 1. Open dashboard in browser
 * 2. Open console
 * 3. Run: await testDataParity()
 */

async function testDataParity() {
  console.log('🧪 Starting Data Parity Test...');
  console.log('='.repeat(60));

  // Test Case 1: Specific known data point
  const testDate = '2025-10-29';  // Last date in range
  const testRestaurant = 'SDR';
  const testShift = 'morning';

  // Enable debug mode
  window.SUPABASE_DEBUG = true;

  try {
    console.log(`\n📍 Test Case: ${testRestaurant} - ${testDate} - ${testShift} shift`);

    // Fetch from local
    console.log('\n1️⃣ Fetching from LOCAL mode...');
    await window.dashboardApp.setDataSourceMode('local');
    await new Promise(resolve => setTimeout(resolve, 1000));
    const localData = captureDataPoint(testDate, testRestaurant, testShift);

    // Fetch from Supabase
    console.log('\n2️⃣ Fetching from SUPABASE mode...');
    await window.dashboardApp.setDataSourceMode('supabase');
    await new Promise(resolve => setTimeout(resolve, 3000));
    const supabaseData = captureDataPoint(testDate, testRestaurant, testShift);

    // Compare and report
    console.log('\n3️⃣ Comparing results...');
    const differences = compareResults(localData, supabaseData);

    // Save results
    window.parityTestResults = {
      testCase: { date: testDate, restaurant: testRestaurant, shift: testShift },
      local: localData,
      supabase: supabaseData,
      differences: differences,
      timestamp: new Date().toISOString()
    };

    console.log('\n✅ Test complete. Results saved to: window.parityTestResults');

    return window.parityTestResults;

  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  } finally {
    window.SUPABASE_DEBUG = false;
  }
}

function captureDataPoint(date, restaurant, shift) {
  const app = window.dashboardApp;
  if (!app || !app.data) {
    console.error('No data available');
    return null;
  }

  console.log(`  Capturing data for ${date}...`);

  // Find the data point across all weeks
  let foundData = null;
  let foundWeek = null;

  for (const [weekKey, weekData] of Object.entries(app.data)) {
    const restaurantData = weekData.restaurants?.find(r => r.code === restaurant);
    if (restaurantData) {
      const dayData = restaurantData.dailyBreakdown?.find(d => d.date === date);
      if (dayData) {
        foundData = dayData;
        foundWeek = weekKey;
        break;
      }
    }
  }

  if (!foundData) {
    console.warn(`  ⚠️ No data found for ${date}`);
    return null;
  }

  const shiftData = foundData.shifts?.[shift];
  const categoryStats = shiftData?.category_stats;

  const result = {
    week: foundWeek,
    date: foundData.date,
    restaurant: foundData.restaurant,
    shift: shift,
    shiftData: shiftData,
    categoryStats: categoryStats,
    hasValidCategoryStats: categoryStats &&
      Object.keys(categoryStats).length > 0 &&
      (categoryStats.Lobby || categoryStats['Drive-Thru'] || categoryStats.ToGo),
    summary: {
      sales: shiftData?.sales,
      orderCount: shiftData?.orderCount,
      laborPercent: shiftData?.laborPercent,
      manager: shiftData?.manager
    }
  };

  console.log(`  ✓ Found in ${foundWeek}:`);
  console.log(`    - Sales: $${result.summary.sales}`);
  console.log(`    - Orders: ${result.summary.orderCount}`);
  console.log(`    - Category Stats: ${result.hasValidCategoryStats ? 'YES' : 'NO'}`);

  if (categoryStats) {
    console.log('    - Categories:', Object.keys(categoryStats).join(', '));
    if (categoryStats.Lobby) {
      console.log(`      Lobby: ${categoryStats.Lobby.passed}✓ / ${categoryStats.Lobby.failed}✗`);
    }
    if (categoryStats['Drive-Thru']) {
      console.log(`      Drive-Thru: ${categoryStats['Drive-Thru'].passed}✓ / ${categoryStats['Drive-Thru'].failed}✗`);
    }
    if (categoryStats.ToGo) {
      console.log(`      ToGo: ${categoryStats.ToGo.passed}✓ / ${categoryStats.ToGo.failed}✗`);
    }
  }

  return result;
}

function compareResults(local, supabase) {
  const differences = [];

  console.log('='.repeat(60));
  console.log('COMPARISON RESULTS:');
  console.log('='.repeat(60));

  if (!local && !supabase) {
    console.log('❌ No data found in either mode!');
    differences.push({ type: 'NO_DATA', severity: 'CRITICAL' });
    return differences;
  }

  if (!local) {
    console.log('❌ No data in LOCAL mode!');
    differences.push({ type: 'MISSING_LOCAL_DATA', severity: 'CRITICAL' });
    return differences;
  }

  if (!supabase) {
    console.log('❌ No data in SUPABASE mode!');
    differences.push({ type: 'MISSING_SUPABASE_DATA', severity: 'CRITICAL' });
    return differences;
  }

  // Compare basic fields
  console.log('\n📊 Basic Fields:');
  const fields = ['sales', 'orderCount', 'laborPercent', 'manager'];

  fields.forEach(field => {
    const localVal = local.summary[field];
    const supabaseVal = supabase.summary[field];
    const match = localVal === supabaseVal;

    console.log(`  ${field}:`);
    console.log(`    Local: ${localVal}`);
    console.log(`    Supabase: ${supabaseVal}`);
    console.log(`    ${match ? '✅ MATCH' : '❌ DIFFER'}`);

    if (!match) {
      differences.push({
        type: 'FIELD_MISMATCH',
        field: field,
        local: localVal,
        supabase: supabaseVal,
        severity: 'HIGH'
      });
    }
  });

  // Compare category_stats
  console.log('\n🎯 Category Stats:');
  const localCS = local.categoryStats;
  const supabaseCS = supabase.categoryStats;

  console.log(`  Local has category_stats: ${local.hasValidCategoryStats ? 'YES' : 'NO'}`);
  console.log(`  Supabase has category_stats: ${supabase.hasValidCategoryStats ? 'YES' : 'NO'}`);

  if (!local.hasValidCategoryStats && !supabase.hasValidCategoryStats) {
    console.log('  ⚠️ Neither has valid category_stats');
    differences.push({
      type: 'NO_CATEGORY_STATS',
      severity: 'CRITICAL'
    });
  } else if (local.hasValidCategoryStats && !supabase.hasValidCategoryStats) {
    console.log('  ❌ Supabase MISSING category_stats!');
    differences.push({
      type: 'SUPABASE_MISSING_CATEGORY_STATS',
      severity: 'CRITICAL'
    });
  } else if (!local.hasValidCategoryStats && supabase.hasValidCategoryStats) {
    console.log('  ❌ Local MISSING category_stats!');
    differences.push({
      type: 'LOCAL_MISSING_CATEGORY_STATS',
      severity: 'CRITICAL'
    });
  } else {
    // Both have category_stats, compare them
    const categories = ['Lobby', 'Drive-Thru', 'ToGo'];

    categories.forEach(cat => {
      const localCat = localCS?.[cat];
      const supabaseCat = supabaseCS?.[cat];

      console.log(`\n  ${cat}:`);

      if (!localCat && !supabaseCat) {
        console.log('    Both missing');
      } else if (!localCat) {
        console.log('    ❌ Missing in Local');
        differences.push({
          type: 'CATEGORY_MISSING_IN_LOCAL',
          category: cat,
          severity: 'HIGH'
        });
      } else if (!supabaseCat) {
        console.log('    ❌ Missing in Supabase');
        differences.push({
          type: 'CATEGORY_MISSING_IN_SUPABASE',
          category: cat,
          severity: 'HIGH'
        });
      } else {
        const fieldsMatch =
          localCat.total === supabaseCat.total &&
          localCat.passed === supabaseCat.passed &&
          localCat.failed === supabaseCat.failed;

        console.log(`    Local: ${localCat.passed}✓ / ${localCat.failed}✗ (${localCat.total} total)`);
        console.log(`    Supabase: ${supabaseCat.passed}✓ / ${supabaseCat.failed}✗ (${supabaseCat.total} total)`);
        console.log(`    ${fieldsMatch ? '✅ MATCH' : '❌ DIFFER'}`);

        if (!fieldsMatch) {
          differences.push({
            type: 'CATEGORY_STATS_MISMATCH',
            category: cat,
            local: localCat,
            supabase: supabaseCat,
            severity: 'CRITICAL'
          });
        }
      }
    });
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY:');
  console.log(`  Total differences found: ${differences.length}`);

  if (differences.length === 0) {
    console.log('  ✅ DATA MATCHES PERFECTLY!');
  } else {
    const critical = differences.filter(d => d.severity === 'CRITICAL').length;
    const high = differences.filter(d => d.severity === 'HIGH').length;

    console.log(`  ❌ Issues: ${critical} CRITICAL, ${high} HIGH`);

    // Root cause analysis
    const supabaseMissingCS = differences.some(d =>
      d.type === 'SUPABASE_MISSING_CATEGORY_STATS'
    );

    if (supabaseMissingCS) {
      console.log('\n🔍 ROOT CAUSE IDENTIFIED:');
      console.log('  Supabase is not returning category_stats from database.');
      console.log('  Check: SupabaseDataService transformation and database query.');
    }
  }

  console.log('='.repeat(60));

  return differences;
}

// Export for use
if (typeof window !== 'undefined') {
  window.testDataParity = testDataParity;
  console.log('✅ Data Parity Test loaded. Run: await testDataParity()');
}