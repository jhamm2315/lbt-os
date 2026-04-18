-- LBT OS integration layer
-- Run in Supabase SQL Editor after the base schema.

CREATE TABLE IF NOT EXISTS integration_connections (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id                UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider              TEXT NOT NULL,
    label                 TEXT,
    status                TEXT NOT NULL DEFAULT 'connected',
    credentials_encrypted TEXT NOT NULL,
    config                JSONB NOT NULL DEFAULT '{}',
    external_account_id   TEXT,
    external_account_name TEXT,
    last_synced_at        TIMESTAMPTZ,
    last_sync_status      TEXT,
    last_sync_error       TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_sync_runs (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id         UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    connection_id  UUID NOT NULL REFERENCES integration_connections(id) ON DELETE CASCADE,
    provider       TEXT NOT NULL,
    trigger_source TEXT NOT NULL DEFAULT 'manual',
    status         TEXT NOT NULL DEFAULT 'pending',
    stats          JSONB NOT NULL DEFAULT '{}',
    error          TEXT,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS integration_record_links (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id        UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    connection_id UUID NOT NULL REFERENCES integration_connections(id) ON DELETE CASCADE,
    provider      TEXT NOT NULL,
    object_type   TEXT NOT NULL,
    external_id   TEXT NOT NULL,
    local_table   TEXT NOT NULL,
    local_id      UUID NOT NULL,
    fingerprint   TEXT,
    last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(connection_id, object_type, external_id)
);

CREATE INDEX IF NOT EXISTS idx_integration_connections_org ON integration_connections(org_id, provider);
CREATE INDEX IF NOT EXISTS idx_integration_sync_runs_org ON integration_sync_runs(org_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_integration_record_links_lookup ON integration_record_links(connection_id, object_type, external_id);

CREATE TRIGGER trg_integration_connections_updated
    BEFORE UPDATE ON integration_connections
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE TRIGGER trg_integration_record_links_updated
    BEFORE UPDATE ON integration_record_links
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
