-- =============================================================
-- Data Portability & Migration Tracking
-- Run after schema.sql and migration_add_integrations.sql
-- =============================================================

-- Track full workspace exports (for audit trail + GDPR compliance)
CREATE TABLE IF NOT EXISTS workspace_exports (
    id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id       UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    triggered_by TEXT        NOT NULL,  -- Clerk user_id
    row_counts   JSONB       NOT NULL DEFAULT '{}',
    file_size_bytes BIGINT,
    exported_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workspace_exports_org
    ON workspace_exports(org_id, exported_at DESC);

-- Migration import runs — tracks large historical data loads
-- (distinct from csv_import_logs which tracks small manual uploads)
CREATE TABLE IF NOT EXISTS migration_runs (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_system   TEXT        NOT NULL,  -- quickbooks | hubspot | csv_bulk | stripe
    status          TEXT        NOT NULL DEFAULT 'pending',
                                           -- pending | running | completed | failed
    total_rows      INT         NOT NULL DEFAULT 0,
    imported_rows   INT         NOT NULL DEFAULT 0,
    skipped_rows    INT         NOT NULL DEFAULT 0,
    error           TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_migration_runs_org
    ON migration_runs(org_id, started_at DESC);
