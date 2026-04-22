-- LBT OS AI audit report enrichment fields
-- Safe to run repeatedly in Supabase SQL Editor.

ALTER TABLE audit_reports
    ADD COLUMN IF NOT EXISTS biggest_leverage_point TEXT,
    ADD COLUMN IF NOT EXISTS health_rationale TEXT,
    ADD COLUMN IF NOT EXISTS segment_analysis JSONB NOT NULL DEFAULT '{}';
