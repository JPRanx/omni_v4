-- Migration: Add category_stats JSONB column to shift_operations table
-- Purpose: Store shift-level category statistics (Lobby, Drive-Thru, ToGo)
--          with pass/fail counts from unique orders (not aggregated from timeslots)
-- Date: 2025-11-16

-- Add the category_stats column (JSONB allows storing nested JSON data)
ALTER TABLE shift_operations
ADD COLUMN IF NOT EXISTS category_stats JSONB;

-- Example data structure that will be stored:
-- {
--   "Lobby": {"total": 50, "passed": 45, "failed": 5},
--   "Drive-Thru": {"total": 120, "passed": 115, "failed": 5},
--   "ToGo": {"total": 80, "passed": 68, "failed": 12}
-- }

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'shift_operations'
AND column_name = 'category_stats';