-- OMNI V4 - Data Verification Queries
-- Purpose: Verify all backfilled data is correct

-- ============================================================================
-- 1. TABLE ROW COUNTS
-- ============================================================================
SELECT 'restaurants' as table_name, COUNT(*) as row_count FROM restaurants
UNION ALL
SELECT 'daily_operations', COUNT(*) FROM daily_operations
UNION ALL
SELECT 'shift_operations', COUNT(*) FROM shift_operations
UNION ALL
SELECT 'vendor_payouts', COUNT(*) FROM vendor_payouts
UNION ALL
SELECT 'timeslot_patterns', COUNT(*) FROM timeslot_patterns
UNION ALL
SELECT 'daily_labor_patterns', COUNT(*) FROM daily_labor_patterns
UNION ALL
SELECT 'timeslot_results', COUNT(*) FROM timeslot_results
UNION ALL
SELECT 'batch_runs', COUNT(*) FROM batch_runs
ORDER BY table_name;

-- ============================================================================
-- 2. RESTAURANT REFERENCE DATA
-- ============================================================================
SELECT
    code,
    name,
    created_at
FROM restaurants
ORDER BY code;

-- ============================================================================
-- 3. DAILY OPERATIONS SUMMARY
-- ============================================================================
SELECT
    restaurant_code,
    COUNT(*) as days_count,
    MIN(business_date) as first_date,
    MAX(business_date) as last_date,
    ROUND(SUM(total_sales)::numeric, 2) as total_sales,
    ROUND(SUM(labor_cost)::numeric, 2) as total_labor,
    ROUND(SUM(food_cost)::numeric, 2) as total_cogs,
    ROUND(AVG(labor_percent)::numeric, 1) as avg_labor_pct,
    ROUND(SUM(net_profit)::numeric, 2) as total_profit
FROM daily_operations
GROUP BY restaurant_code
ORDER BY restaurant_code;

-- ============================================================================
-- 4. SAMPLE DAILY OPERATIONS (Most Recent 5)
-- ============================================================================
SELECT
    business_date,
    restaurant_code,
    total_sales,
    labor_cost,
    labor_percent,
    food_cost,
    net_profit,
    labor_grade,
    labor_status
FROM daily_operations
ORDER BY business_date DESC, restaurant_code
LIMIT 5;

-- ============================================================================
-- 5. SHIFT OPERATIONS BREAKDOWN
-- ============================================================================
SELECT
    restaurant_code,
    shift_name,
    COUNT(*) as shift_count,
    ROUND(SUM(sales)::numeric, 2) as total_sales,
    ROUND(SUM(cash_collected)::numeric, 2) as total_cash,
    ROUND(SUM(tips_distributed)::numeric, 2) as total_tips,
    ROUND(SUM(vendor_payouts)::numeric, 2) as total_payouts
FROM shift_operations
GROUP BY restaurant_code, shift_name
ORDER BY restaurant_code, shift_name;

-- ============================================================================
-- 6. BATCH RUN DETAILS
-- ============================================================================
SELECT
    id,
    start_date,
    end_date,
    restaurants_processed,
    status,
    records_processed,
    errors_count,
    started_at,
    completed_at,
    duration_seconds
FROM batch_runs
ORDER BY started_at DESC
LIMIT 5;

-- ============================================================================
-- 7. LABOR PERFORMANCE DISTRIBUTION
-- ============================================================================
SELECT
    labor_grade,
    COUNT(*) as day_count,
    ROUND(AVG(labor_percent)::numeric, 1) as avg_labor_pct,
    ROUND(AVG(total_sales)::numeric, 2) as avg_sales
FROM daily_operations
WHERE labor_grade IS NOT NULL
GROUP BY labor_grade
ORDER BY labor_grade;

-- ============================================================================
-- 8. CASH FLOW SUMMARY
-- ============================================================================
SELECT
    restaurant_code,
    ROUND(SUM(cash_collected)::numeric, 2) as total_cash,
    ROUND(SUM(tips_distributed)::numeric, 2) as total_tips,
    ROUND(SUM(vendor_payouts_total)::numeric, 2) as total_vendor_payouts,
    ROUND(SUM(net_cash)::numeric, 2) as net_cash
FROM daily_operations
GROUP BY restaurant_code
ORDER BY restaurant_code;

-- ============================================================================
-- 9. DATE RANGE COVERAGE
-- ============================================================================
SELECT
    MIN(business_date) as first_day,
    MAX(business_date) as last_day,
    MAX(business_date) - MIN(business_date) + 1 as day_span,
    COUNT(DISTINCT business_date) as unique_dates,
    COUNT(DISTINCT restaurant_code) as unique_restaurants,
    COUNT(*) as total_records
FROM daily_operations;

-- ============================================================================
-- 10. DATA QUALITY CHECKS
-- ============================================================================
-- Check for nulls in critical fields
SELECT
    'Missing sales' as check_name,
    COUNT(*) as issue_count
FROM daily_operations
WHERE total_sales IS NULL OR total_sales = 0

UNION ALL

SELECT
    'Missing labor cost',
    COUNT(*)
FROM daily_operations
WHERE labor_cost IS NULL

UNION ALL

SELECT
    'Missing labor percent',
    COUNT(*)
FROM daily_operations
WHERE labor_percent IS NULL

UNION ALL

SELECT
    'Negative profit',
    COUNT(*)
FROM daily_operations
WHERE net_profit < 0;
