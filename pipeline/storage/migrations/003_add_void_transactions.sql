-- Migration: Add void_transactions table for detailed void tracking
-- Purpose: Store detailed void transaction data including server, approver, reason, and items
-- Date: 2025-01-24

CREATE TABLE IF NOT EXISTS void_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_date DATE NOT NULL,
    restaurant_code TEXT NOT NULL REFERENCES restaurants(code) ON DELETE CASCADE,

    -- Shift context
    shift_name TEXT NOT NULL CHECK (shift_name IN ('Morning', 'Evening')),

    -- Void transaction details
    order_number TEXT NOT NULL,
    void_date TIMESTAMPTZ NOT NULL,
    server TEXT NOT NULL,
    approver TEXT NOT NULL,
    reason TEXT NOT NULL,

    -- Items and amounts
    item_count INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    items_detail JSONB,  -- Array of voided item names

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes for common queries
    CONSTRAINT void_transactions_unique UNIQUE(business_date, restaurant_code, order_number)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_void_transactions_date_restaurant
    ON void_transactions(business_date, restaurant_code);

CREATE INDEX IF NOT EXISTS idx_void_transactions_shift
    ON void_transactions(shift_name);

CREATE INDEX IF NOT EXISTS idx_void_transactions_server
    ON void_transactions(server);

CREATE INDEX IF NOT EXISTS idx_void_transactions_reason
    ON void_transactions(reason);

-- Add comments
COMMENT ON TABLE void_transactions IS 'Detailed void transaction data extracted from Toast POS VoidDetails CSV';
COMMENT ON COLUMN void_transactions.order_number IS 'Order number that was voided';
COMMENT ON COLUMN void_transactions.void_date IS 'When the void occurred';
COMMENT ON COLUMN void_transactions.server IS 'Server who initiated the order';
COMMENT ON COLUMN void_transactions.approver IS 'Manager who approved the void';
COMMENT ON COLUMN void_transactions.reason IS 'Reason for void (e.g., Customer Changed Mind, Server Error)';
COMMENT ON COLUMN void_transactions.items_detail IS 'JSON array of voided item names';