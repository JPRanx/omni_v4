-- OMNI V4 Database Schema
-- Purpose: Store restaurant analytics data from Toast POS processing
-- Design: Based on ACTUAL working features (no phantom fields)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. REFERENCE DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS restaurants (
    code TEXT PRIMARY KEY,  -- 'SDR', 'T12', 'TK9'
    name TEXT NOT NULL,
    address TEXT,
    timezone TEXT DEFAULT 'America/Chicago',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert reference data
INSERT INTO restaurants (code, name) VALUES
    ('SDR', 'Sandras Mexican Cuisine'),
    ('T12', 'Tacos x12'),
    ('TK9', 'Tinks & Tako')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- 2. DAILY OPERATIONS (Core Business Metrics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_operations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,

    -- Sales metrics
    total_sales DECIMAL(10,2) NOT NULL DEFAULT 0,
    order_count INTEGER,

    -- Labor metrics
    labor_cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    labor_hours DECIMAL(10,2),
    labor_percent DECIMAL(5,2),
    employee_count INTEGER,

    -- Overtime tracking
    overtime_hours DECIMAL(10,2) DEFAULT 0,
    overtime_cost DECIMAL(10,2) DEFAULT 0,

    -- COGS (from vendor payouts)
    food_cost DECIMAL(10,2) DEFAULT 0,
    food_cost_percent DECIMAL(5,2),

    -- Profitability
    net_profit DECIMAL(10,2),
    profit_margin DECIMAL(5,2),

    -- Cash flow summary
    cash_collected DECIMAL(10,2) DEFAULT 0,
    tips_distributed DECIMAL(10,2) DEFAULT 0,
    vendor_payouts_total DECIMAL(10,2) DEFAULT 0,
    net_cash DECIMAL(10,2) DEFAULT 0,

    -- Service mix (optional - only if order categorization ran)
    lobby_percent DECIMAL(5,2),
    drivethru_percent DECIMAL(5,2),
    togo_percent DECIMAL(5,2),
    categorized_orders INTEGER,

    -- Performance grading
    labor_status TEXT CHECK (labor_status IN ('EXCELLENT', 'GOOD', 'WARNING', 'CRITICAL', 'SEVERE')),
    labor_grade TEXT CHECK (labor_grade IN ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F')),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(business_date, restaurant_code)
);

-- ============================================================================
-- 3. SHIFT OPERATIONS (Morning/Evening Split)
-- ============================================================================

CREATE TABLE IF NOT EXISTS shift_operations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,
    shift_name TEXT NOT NULL CHECK (shift_name IN ('Morning', 'Evening')),

    -- Sales
    sales DECIMAL(10,2) DEFAULT 0,
    order_count INTEGER,

    -- Labor
    labor_cost DECIMAL(10,2) DEFAULT 0,
    labor_hours DECIMAL(10,2),

    -- Cash flow
    cash_collected DECIMAL(10,2) DEFAULT 0,
    tips_distributed DECIMAL(10,2) DEFAULT 0,
    vendor_payouts DECIMAL(10,2) DEFAULT 0,
    net_cash DECIMAL(10,2) DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(business_date, restaurant_code, shift_name)
);

-- ============================================================================
-- 4. VENDOR PAYOUTS (COGS Detail)
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendor_payouts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,

    -- Payout details
    amount DECIMAL(10,2) NOT NULL,
    reason TEXT,
    comments TEXT,
    vendor_name TEXT,

    -- Context
    shift_name TEXT CHECK (shift_name IN ('Morning', 'Evening')),
    drawer TEXT,
    manager TEXT,
    payout_time TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. TIMESLOT PATTERNS (Machine Learning Storage)
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeslot_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    pattern_key TEXT UNIQUE NOT NULL,  -- Format: SDR_Monday_morning_11:00-11:15_Lobby

    -- Pattern dimensions
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL,  -- 'Monday', 'Tuesday', etc.
    shift TEXT NOT NULL,  -- 'morning', 'evening'
    time_window TEXT NOT NULL,  -- '11:00-11:15'
    category TEXT NOT NULL,  -- 'Lobby', 'Drive-Thru', 'ToGo'

    -- Statistical values (Exponential Moving Average)
    baseline_time DECIMAL(10,2),  -- Average fulfillment time in minutes
    variance DECIMAL(10,2),  -- Acceptable variance in minutes
    confidence DECIMAL(5,2),  -- 0.0 to 1.0
    observations_count INTEGER DEFAULT 0,

    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. DAILY LABOR PATTERNS (Daily-Level Learning)
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_labor_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),  -- 0=Monday, 6=Sunday

    -- Expected patterns
    expected_labor_percent DECIMAL(5,2),
    expected_total_hours DECIMAL(10,2),

    -- Learning metrics
    confidence DECIMAL(5,2),  -- 0.0 to 1.0
    observations INTEGER DEFAULT 0,

    -- Metadata
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(restaurant_code, day_of_week)
);

-- ============================================================================
-- 7. TIMESLOT RESULTS (15-Minute Performance Windows)
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeslot_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,

    -- Timeslot identification
    timeslot_index INTEGER NOT NULL CHECK (timeslot_index BETWEEN 0 AND 63),
    timeslot_label TEXT NOT NULL,  -- '6:00 AM', '6:15 AM', etc.
    shift_name TEXT CHECK (shift_name IN ('Morning', 'Evening')),

    -- Performance metrics
    orders INTEGER DEFAULT 0,
    sales DECIMAL(10,2) DEFAULT 0,
    labor_cost DECIMAL(10,2) DEFAULT 0,
    efficiency_score DECIMAL(5,2),

    -- Grading
    grade TEXT CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),
    pass_fail BOOLEAN,

    -- Service breakdown (if available)
    lobby_orders INTEGER,
    drivethru_orders INTEGER,
    togo_orders INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(business_date, restaurant_code, timeslot_index)
);

-- ============================================================================
-- 8. BATCH PROCESSING METADATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS batch_runs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Run configuration
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    restaurants_processed TEXT[],  -- ['SDR', 'T12', 'TK9']

    -- Status tracking
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    records_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_messages JSONB,

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);
