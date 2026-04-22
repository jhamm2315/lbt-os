-- Migration: add csv_import_logs table for manual CSV upload history
-- Run in Supabase SQL editor

CREATE TABLE IF NOT EXISTS csv_import_logs (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id        UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_type   TEXT NOT NULL,
    filename      TEXT,
    rows_imported INT  NOT NULL DEFAULT 0,
    row_count     INT  NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'success',
    error         TEXT,
    imported_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_csv_import_logs_org
    ON csv_import_logs(org_id, imported_at DESC);

-- RLS
ALTER TABLE csv_import_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Org members can read their own import logs"
    ON csv_import_logs FOR SELECT
    USING (org_id = auth_org_id());
