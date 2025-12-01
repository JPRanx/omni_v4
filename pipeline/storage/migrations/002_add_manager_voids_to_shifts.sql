-- Migration: Add manager and voids columns to shift_operations table
-- Purpose: Store shift manager assignments and void transaction counts
-- Date: 2025-01-24

-- Add manager column (TEXT, nullable)
ALTER TABLE shift_operations
ADD COLUMN IF NOT EXISTS manager TEXT;

-- Add voids column (INTEGER, default 0)
ALTER TABLE shift_operations
ADD COLUMN IF NOT EXISTS voids INTEGER DEFAULT 0;

-- Add comment to document the columns
COMMENT ON COLUMN shift_operations.manager IS 'Manager assigned to this shift (extracted from time entries)';
COMMENT ON COLUMN shift_operations.voids IS 'Number of void transactions in this shift';