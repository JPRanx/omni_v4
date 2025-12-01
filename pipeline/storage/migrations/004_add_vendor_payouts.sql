-- Migration: Add vendor_payouts table for detailed payout tracking
-- Purpose: Store detailed vendor payout data from cash management CSV
-- Date: 2025-11-26

CREATE TABLE IF NOT EXISTS vendor_payouts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,

    -- Shift context
    shift_name TEXT NOT NULL CHECK (shift_name IN ('Morning', 'Evening')),

    -- Vendor payout details
    vendor_name TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    reason TEXT,
    comments TEXT,
    payout_time TIMESTAMPTZ,
    manager TEXT,
    drawer TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes for common queries
    CONSTRAINT vendor_payouts_unique UNIQUE(business_date, restaurant_code, shift_name, vendor_name, amount, payout_time)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_vendor_payouts_date_restaurant
    ON vendor_payouts(business_date, restaurant_code);

CREATE INDEX IF NOT EXISTS idx_vendor_payouts_shift
    ON vendor_payouts(shift_name);

CREATE INDEX IF NOT EXISTS idx_vendor_payouts_vendor
    ON vendor_payouts(vendor_name);

-- Add comments
COMMENT ON TABLE vendor_payouts IS 'Detailed vendor payout data extracted from Toast POS cash-mgmt CSV';
COMMENT ON COLUMN vendor_payouts.vendor_name IS 'Vendor or category name (e.g., Supplies, Misc)';
COMMENT ON COLUMN vendor_payouts.amount IS 'Payout amount (positive value)';
COMMENT ON COLUMN vendor_payouts.reason IS 'Payout reason/category';
COMMENT ON COLUMN vendor_payouts.comments IS 'Additional notes about the payout';
COMMENT ON COLUMN vendor_payouts.payout_time IS 'When the payout occurred';
COMMENT ON COLUMN vendor_payouts.manager IS 'Manager who approved the payout';
COMMENT ON COLUMN vendor_payouts.drawer IS 'Which cash drawer was used';