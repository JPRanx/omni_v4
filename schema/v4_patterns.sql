-- OMNI V4 Pattern Storage Schema
-- Database: Supabase (PostgreSQL 15+)
-- Purpose: Store learned traffic and staffing patterns for predictive analytics

-- ============================================================================
-- TABLE: v4_patterns
-- ============================================================================
-- Stores learned patterns for restaurant traffic and staffing predictions
-- Each pattern is uniquely identified by 4 dimensions:
--   - restaurant_code: Which restaurant (SDR, T12, TK9)
--   - service_type: Which service channel (Lobby, Drive-Thru, ToGo)
--   - hour: Which hour of day (0-23)
--   - day_of_week: Which day (0=Monday, 6=Sunday)

CREATE TABLE IF NOT EXISTS v4_patterns (
    -- ========================================================================
    -- PATTERN IDENTITY (4-dimensional composite key)
    -- ========================================================================
    restaurant_code TEXT NOT NULL,
    service_type TEXT NOT NULL CHECK (service_type IN ('Lobby', 'Drive-Thru', 'ToGo')),
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),

    -- ========================================================================
    -- PATTERN PREDICTIONS
    -- ========================================================================
    -- Expected values learned from historical observations
    expected_volume REAL NOT NULL CHECK (expected_volume >= 0),
    expected_staffing REAL NOT NULL CHECK (expected_staffing >= 0),

    -- ========================================================================
    -- LEARNING METADATA
    -- ========================================================================
    -- Confidence: How reliable is this pattern (0.0-1.0)
    -- Grows asymptotically with observations: 1 - 1/(observations + 1)
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Observations: Number of data points used to learn this pattern
    -- Used for dynamic learning rate (early vs mature observations)
    observations INTEGER NOT NULL CHECK (observations >= 0),

    -- ========================================================================
    -- TIMESTAMPS
    -- ========================================================================
    -- When this pattern was last updated (for staleness detection)
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- When this pattern was first created
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- ========================================================================
    -- EXTENSIBILITY
    -- ========================================================================
    -- JSON metadata for future extensions (variance, tags, notes, etc.)
    -- Example: {"is_fallback": true, "days_averaged": 3, "variance": 12.5}
    metadata JSONB DEFAULT '{}',

    -- ========================================================================
    -- CONSTRAINTS
    -- ========================================================================
    PRIMARY KEY (restaurant_code, service_type, hour, day_of_week)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
-- Target: All pattern queries < 100ms

-- Index 1: Filter by restaurant (most common query)
-- Usage: SELECT * FROM v4_patterns WHERE restaurant_code = 'SDR'
CREATE INDEX IF NOT EXISTS idx_patterns_restaurant
    ON v4_patterns(restaurant_code);

-- Index 2: Filter by restaurant + service type
-- Usage: SELECT * FROM v4_patterns WHERE restaurant_code = 'SDR' AND service_type = 'Lobby'
CREATE INDEX IF NOT EXISTS idx_patterns_service
    ON v4_patterns(restaurant_code, service_type);

-- Index 3: Filter by hour (for fallback queries)
-- Usage: SELECT * FROM v4_patterns WHERE hour = 12
CREATE INDEX IF NOT EXISTS idx_patterns_hour
    ON v4_patterns(hour);

-- Index 4: Filter by last_updated (for staleness detection)
-- Usage: SELECT * FROM v4_patterns WHERE last_updated < NOW() - INTERVAL '14 days'
CREATE INDEX IF NOT EXISTS idx_patterns_updated
    ON v4_patterns(last_updated);

-- Index 5: Composite for exact pattern lookup (covered by PRIMARY KEY)
-- Usage: SELECT * FROM v4_patterns WHERE restaurant_code = 'SDR' AND service_type = 'Lobby'
--        AND hour = 12 AND day_of_week = 1
-- (No additional index needed - PRIMARY KEY provides this)

-- ============================================================================
-- COMMENTS (PostgreSQL Documentation)
-- ============================================================================
COMMENT ON TABLE v4_patterns IS
'Learned traffic and staffing patterns for predictive analytics. Each pattern represents expected behavior for a specific restaurant, service type, hour, and day of week.';

COMMENT ON COLUMN v4_patterns.restaurant_code IS
'Restaurant identifier (SDR, T12, TK9)';

COMMENT ON COLUMN v4_patterns.service_type IS
'Service channel: Lobby (dine-in), Drive-Thru, or ToGo (takeout)';

COMMENT ON COLUMN v4_patterns.hour IS
'Hour of day in 24-hour format (0-23). Example: 12 = noon, 18 = 6 PM';

COMMENT ON COLUMN v4_patterns.day_of_week IS
'Day of week: 0=Monday, 1=Tuesday, ..., 6=Sunday (ISO 8601)';

COMMENT ON COLUMN v4_patterns.expected_volume IS
'Expected transaction volume for this time slot (learned via exponential moving average)';

COMMENT ON COLUMN v4_patterns.expected_staffing IS
'Expected staffing level for this time slot (learned via exponential moving average)';

COMMENT ON COLUMN v4_patterns.confidence IS
'Pattern reliability score (0.0-1.0). Calculated as: 1 - 1/(observations + 1). Higher = more reliable.';

COMMENT ON COLUMN v4_patterns.observations IS
'Number of data points used to learn this pattern. Used for dynamic learning rates.';

COMMENT ON COLUMN v4_patterns.last_updated IS
'Timestamp when pattern was last updated. Used for staleness detection and decay.';

COMMENT ON COLUMN v4_patterns.created_at IS
'Timestamp when pattern was first created (never changes).';

COMMENT ON COLUMN v4_patterns.metadata IS
'JSON metadata for extensions. Example: {"is_fallback": true, "variance": 12.5, "notes": "Holiday adjusted"}';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS for multi-tenant security (if needed in production)
-- ALTER TABLE v4_patterns ENABLE ROW LEVEL SECURITY;

-- Example policy (uncomment for production):
-- CREATE POLICY "Users can only access their restaurant patterns"
--     ON v4_patterns
--     FOR ALL
--     USING (restaurant_code = current_setting('app.current_restaurant')::TEXT);

-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- Get exact pattern (most common operation)
-- Expected performance: < 10ms (uses PRIMARY KEY)
-- SELECT * FROM v4_patterns
-- WHERE restaurant_code = 'SDR'
--   AND service_type = 'Lobby'
--   AND hour = 12
--   AND day_of_week = 1;

-- Get all patterns for a service type (for fallback chain)
-- Expected performance: < 50ms (uses idx_patterns_service)
-- SELECT * FROM v4_patterns
-- WHERE restaurant_code = 'SDR'
--   AND service_type = 'Lobby'
-- ORDER BY hour, day_of_week;

-- Get all patterns for a restaurant (for bulk operations)
-- Expected performance: < 100ms (uses idx_patterns_restaurant)
-- SELECT * FROM v4_patterns
-- WHERE restaurant_code = 'SDR';

-- Find stale patterns (for cleanup/decay)
-- Expected performance: < 200ms (uses idx_patterns_updated)
-- SELECT * FROM v4_patterns
-- WHERE last_updated < NOW() - INTERVAL '14 days';

-- Get reliable patterns only (confidence threshold)
-- SELECT * FROM v4_patterns
-- WHERE restaurant_code = 'SDR'
--   AND confidence >= 0.6
--   AND observations >= 4;

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
-- V3 → V4 Migration:
-- - V3 patterns table (if exists) should be migrated using ETL script
-- - Map V3 fields to V4 schema
-- - Calculate confidence from V3 observations
-- - Set metadata = {} for V3 patterns
-- - Defer migration to Week 9 (not blocking for Week 3 completion)

-- Performance Targets:
-- - Single pattern lookup: < 10ms
-- - Service type scan: < 50ms
-- - Restaurant scan: < 100ms
-- - Bulk operations: < 500ms

-- Maintenance:
-- - Consider VACUUM ANALYZE v4_patterns weekly
-- - Monitor index usage with pg_stat_user_indexes
-- - Set up pattern decay job (reduce confidence for stale patterns)
