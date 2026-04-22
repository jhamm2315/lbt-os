-- Revenue Intelligence migration
-- Run this after migration_messages.sql

-- Stage tracking timestamp on leads
ALTER TABLE leads ADD COLUMN IF NOT EXISTS stage_changed_at TIMESTAMPTZ;

-- Lead stage history event log
CREATE TABLE IF NOT EXISTS lead_stage_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    lead_id     UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status   TEXT NOT NULL,
    changed_by  TEXT,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lsh_org_id   ON lead_stage_history(org_id);
CREATE INDEX IF NOT EXISTS idx_lsh_lead_id  ON lead_stage_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_lsh_changed  ON lead_stage_history(changed_at DESC);

-- Plan audit log
CREATE TABLE IF NOT EXISTS plan_audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    changed_by  TEXT NOT NULL,
    from_plan   TEXT,
    to_plan     TEXT NOT NULL,
    reason      TEXT,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pal_org_id ON plan_audit_log(org_id);
