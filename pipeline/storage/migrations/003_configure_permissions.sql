-- OMNI V4 - Configure Permissions and Disable RLS
-- Purpose: Allow the Python client to read/write data without authentication issues

-- ============================================================================
-- DISABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- By default, Supabase enables RLS which blocks all access unless policies exist
-- For internal analytics tools, we disable RLS to allow full access

ALTER TABLE restaurants DISABLE ROW LEVEL SECURITY;
ALTER TABLE daily_operations DISABLE ROW LEVEL SECURITY;
ALTER TABLE shift_operations DISABLE ROW LEVEL SECURITY;
ALTER TABLE vendor_payouts DISABLE ROW LEVEL SECURITY;
ALTER TABLE timeslot_patterns DISABLE ROW LEVEL SECURITY;
ALTER TABLE daily_labor_patterns DISABLE ROW LEVEL SECURITY;
ALTER TABLE timeslot_results DISABLE ROW LEVEL SECURITY;
ALTER TABLE batch_runs DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
-- Ensure anon and authenticated roles can access all tables

-- Grant to anon role (used by API key)
GRANT ALL ON restaurants TO anon;
GRANT ALL ON daily_operations TO anon;
GRANT ALL ON shift_operations TO anon;
GRANT ALL ON vendor_payouts TO anon;
GRANT ALL ON timeslot_patterns TO anon;
GRANT ALL ON daily_labor_patterns TO anon;
GRANT ALL ON timeslot_results TO anon;
GRANT ALL ON batch_runs TO anon;

-- Grant to authenticated role
GRANT ALL ON restaurants TO authenticated;
GRANT ALL ON daily_operations TO authenticated;
GRANT ALL ON shift_operations TO authenticated;
GRANT ALL ON vendor_payouts TO authenticated;
GRANT ALL ON timeslot_patterns TO authenticated;
GRANT ALL ON daily_labor_patterns TO authenticated;
GRANT ALL ON timeslot_results TO authenticated;
GRANT ALL ON batch_runs TO authenticated;

-- Grant usage on sequences (for auto-incrementing IDs if needed)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================================================
-- ENABLE REALTIME (Optional - for future live dashboard)
-- ============================================================================
-- Uncomment these if you want real-time updates in the future

-- ALTER PUBLICATION supabase_realtime ADD TABLE daily_operations;
-- ALTER PUBLICATION supabase_realtime ADD TABLE shift_operations;
-- ALTER PUBLICATION supabase_realtime ADD TABLE timeslot_patterns;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- After running this, verify with:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
-- Should show rowsecurity = false for all tables
