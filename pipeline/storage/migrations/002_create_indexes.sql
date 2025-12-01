-- OMNI V4 Performance Indexes
-- Purpose: Optimize common query patterns

-- ============================================================================
-- DAILY OPERATIONS INDEXES
-- ============================================================================

-- Most common query: Get data for restaurant in date range
CREATE INDEX idx_daily_ops_restaurant_date
    ON daily_operations(restaurant_code, business_date DESC);

-- Filter by date range across all restaurants
CREATE INDEX idx_daily_ops_date
    ON daily_operations(business_date DESC);

-- Filter by performance status
CREATE INDEX idx_daily_ops_status
    ON daily_operations(labor_status)
    WHERE labor_status IN ('CRITICAL', 'SEVERE');

-- Filter by grade
CREATE INDEX idx_daily_ops_grade
    ON daily_operations(labor_grade);

-- ============================================================================
-- SHIFT OPERATIONS INDEXES
-- ============================================================================

CREATE INDEX idx_shift_ops_restaurant_date
    ON shift_operations(restaurant_code, business_date DESC);

CREATE INDEX idx_shift_ops_shift
    ON shift_operations(shift_name);

-- ============================================================================
-- VENDOR PAYOUTS INDEXES
-- ============================================================================

-- Query payouts by restaurant and date range
CREATE INDEX idx_vendor_payouts_restaurant_date
    ON vendor_payouts(restaurant_code, business_date DESC);

-- Query by vendor for vendor analysis
CREATE INDEX idx_vendor_payouts_vendor
    ON vendor_payouts(vendor_name);

-- Filter by shift
CREATE INDEX idx_vendor_payouts_shift
    ON vendor_payouts(shift_name);

-- ============================================================================
-- PATTERN INDEXES
-- ============================================================================

-- Lookup patterns by key (most common operation)
CREATE INDEX idx_timeslot_patterns_key
    ON timeslot_patterns(pattern_key);

-- Filter patterns by restaurant
CREATE INDEX idx_timeslot_patterns_restaurant
    ON timeslot_patterns(restaurant_code);

-- Filter by category for service type analysis
CREATE INDEX idx_timeslot_patterns_category
    ON timeslot_patterns(category);

-- Filter by confidence (for reliable patterns only)
CREATE INDEX idx_timeslot_patterns_confidence
    ON timeslot_patterns(confidence DESC)
    WHERE confidence >= 0.6;

-- Daily labor pattern lookups
CREATE INDEX idx_daily_labor_patterns_restaurant_dow
    ON daily_labor_patterns(restaurant_code, day_of_week);

-- ============================================================================
-- TIMESLOT RESULTS INDEXES
-- ============================================================================

-- Query timeslots by restaurant and date
CREATE INDEX idx_timeslot_results_restaurant_date
    ON timeslot_results(restaurant_code, business_date DESC);

-- Filter failing timeslots
CREATE INDEX idx_timeslot_results_failures
    ON timeslot_results(pass_fail)
    WHERE pass_fail = false;

-- Filter by grade
CREATE INDEX idx_timeslot_results_grade
    ON timeslot_results(grade);

-- ============================================================================
-- BATCH RUNS INDEXES
-- ============================================================================

CREATE INDEX idx_batch_runs_status
    ON batch_runs(status);

CREATE INDEX idx_batch_runs_date
    ON batch_runs(started_at DESC);
