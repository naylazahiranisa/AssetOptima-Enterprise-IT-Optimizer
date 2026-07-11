-- ============================================================================
-- AssetOptima - Migration 001: Initial Schema
--
-- Description: Initial database setup. Idempotent — safe to re-run.
-- Migration type: Schema creation
-- Dependencies: PostgreSQL 17+
-- ============================================================================

BEGIN;

-- ############################################################################
-- 1. Verify database version
-- ############################################################################
DO $$
BEGIN
    IF current_setting('server_version_num')::INT < 170000 THEN
        RAISE EXCEPTION 'PostgreSQL 17+ required (current: %)', current_setting('server_version');
    END IF;
END $$;

-- ############################################################################
-- 2. Load schema
-- ############################################################################
\i ../schema/schema.sql

-- ############################################################################
-- 3. Verify schema integrity
-- ############################################################################
DO $$
DECLARE
    expected_tables INT := 22;
    actual_tables INT;
BEGIN
    SELECT COUNT(*) INTO actual_tables
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE';

    IF actual_tables < expected_tables THEN
        RAISE WARNING 'Expected % tables, found %. Check schema for errors.',
            expected_tables, actual_tables;
    ELSE
        RAISE NOTICE 'Migration 001 complete: % tables created.', actual_tables;
    END IF;
END $$;

COMMIT;
